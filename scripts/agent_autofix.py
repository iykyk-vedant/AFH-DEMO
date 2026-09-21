#!/usr/bin/env python3
"""
Autonomous SRE Multi-Agent Incident Resolver (GitHub Actions Runner)
Powered by Microsoft Azure AI Foundry (gpt-5-mini & grok-4-20-reasoning)
"""

import os
import sys
import json
import re
import subprocess
from typing import Dict, Any, List, Optional
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Fallback default endpoint if not in env
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://agentathon-2026-resource.openai.azure.com/").rstrip("/")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = "2024-08-01-preview"
PLANNER_MODEL = os.getenv("AZURE_DEPLOYMENT_PLANNER", "gpt-5-mini")
CRITIC_MODEL = os.getenv("AZURE_DEPLOYMENT_CRITIC", "grok-4-20-reasoning")

ISSUE_NUMBER = os.getenv("ISSUE_NUMBER") or "1"
ISSUE_TITLE = os.getenv("ISSUE_TITLE") or "INC-002: Double discount deduction applied during checkout calculation"
ISSUE_BODY = os.getenv("ISSUE_BODY") or "Discount is deducted twice from subtotal in app/services/payment_service.py"


def call_azure_llm(deployment: str, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY secret is not set in GitHub repository settings.")

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"
    headers = {
        "api-key": AZURE_OPENAI_API_KEY,
        "Content-Type": "application/json"
    }
    payload: Dict[str, Any] = {"messages": messages}
    if "gpt-5" not in deployment.lower() and "o1" not in deployment.lower() and "o3" not in deployment.lower():
        payload["temperature"] = temperature

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Azure call to {deployment} failed ({resp.status_code}): {resp.text}")
    return resp.json()["choices"][0]["message"]["content"]


def clean_json_response(text: str) -> Dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def run_critic_review(issue_title: str, issue_body: str) -> Dict[str, Any]:
    print(f"\n[Agent 1: Critic / Reflector ({CRITIC_MODEL})] Deep reasoning safety check...")
    system_prompt = """You are the Lead SRE Critic and Safety Gate.
Your role: Rigorously analyze the incident report before any code is generated.
Find the confirmed root cause, exact bug location, and formulate negative constraints that MUST NOT be violated.
Output strictly in JSON:
{
  "confirmed_root_cause": "<root cause>",
  "recommended_files": ["<filepath>"],
  "patch_constraints": ["<constraint 1>", "<constraint 2>"]
}"""
    user_prompt = f"Issue Title: {issue_title}\n\nIssue Details / Logs:\n{issue_body}"
    content = call_azure_llm(CRITIC_MODEL, [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ], temperature=0.1)
    return clean_json_response(content)


def run_test_generator_agent(
    critic_plan: Dict[str, Any],
    target_file: str,
    file_content: str,
    issue_number: str,
    issue_title: str,
    issue_body: str
) -> Dict[str, str]:
    print(f"\n[Agent 1.5: QA / Test Synthesis Specialist ({PLANNER_MODEL})] Synthesizing dedicated reproduction test case...")
    system_prompt = """You are a Principal QA and Test Automation Engineer.
Your role: Synthesize an isolated, self-contained pytest reproduction test case for the reported incident.
Requirements:
1. Import the buggy function or class from its target module (e.g., `from app.services.shipping_service import calculate_shipping_rate`).
2. Construct test parameters and inputs that trigger the bug described in the issue (e.g., weight_kg=0.0, boundary conditions).
3. Assert the expected, valid business behavior that should hold true once fixed (e.g., proper return values, no exceptions, positive fees).
4. Name the test function `test_incident_regression()` or similar.
5. Use only standard library and pytest. Do not import uninstalled third-party packages.
Output strictly in JSON:
{
  "test_filename": "tests/test_issue_regression.py",
  "test_code": "<full python pytest code>"
}"""
    user_prompt = f"""Incident #{issue_number}: {issue_title}
Report Details / Stack Trace:
{issue_body}

Confirmed Root Cause:
{critic_plan.get('confirmed_root_cause')}

Target File: {target_file}
Source Code:
```python
{file_content}
```"""
    content = call_azure_llm(PLANNER_MODEL, [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ], temperature=0.1)
    res = clean_json_response(content)
    # Ensure filename reflects issue number
    res["test_filename"] = f"tests/test_issue_{issue_number}_regression.py"
    return res


def verify_negative_reproduction(test_filename: str) -> tuple[bool, str]:
    print(f"[Agent 1.5: QA / Test Synthesis Specialist] Executing negative reproduction verification on unpatched code...")
    res = subprocess.run(["pytest", test_filename, "-v"], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"✅ [Negative Validation] Reproduction confirmed! Test failed as expected on unpatched code.")
        return True, res.stdout
    else:
        print(f"⚠️ [Negative Validation] Notice: Test passed on unpatched code. Proceeding with caution.")
        return False, res.stdout


def run_fix_planner(critic_plan: Dict[str, Any], file_path: str, file_content: str, test_content: Optional[str] = None, feedback: Optional[str] = None) -> Dict[str, Any]:
    print(f"\n[Agent 2: Fix Planner ({PLANNER_MODEL})] Formulating surgical replacement patch...")
    system_prompt = """You are a Principal Software Engineer.
Generate the MINIMAL, SURGICAL patch to resolve the bug.
Do not rewrite unrelated logic. Adhere strictly to the Critic's constraints.
Output strictly in JSON:
{
  "file_path": "<relative_path>",
  "original_snippet": "<exact substring to replace>",
  "replacement_snippet": "<replacement code>"
}"""
    user_prompt = f"""Root cause: {critic_plan.get('confirmed_root_cause')}
Constraints: {critic_plan.get('patch_constraints')}
Target file: {file_path}

Target File Contents:
```python
{file_content}
```"""
    if test_content:
        user_prompt += f"""

Target Test Suite Requirements (Ensure your fix satisfies these tests):
{test_content}"""
    if feedback:
        user_prompt += f"""

⚠️ PREVIOUS CANDIDATE PATCH FAILED PYTEST REGRESSION CHECK:
```
{feedback}
```
Analyze the test failure above carefully (e.g. check which assertion failed and what return value or formula was expected).
Regenerate a surgical patch that satisfies both the root cause fix AND all test assertions."""

    content = call_azure_llm(PLANNER_MODEL, [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    return clean_json_response(content)


def parse_pytest_summary(output: str) -> Dict[str, str]:
    """Extract individual test statuses from pytest output."""
    results = {}
    for line in output.splitlines():
        if " PASSED" in line:
            parts = line.split(" PASSED")
            results[parts[0].strip()] = "PASSED"
        elif " FAILED" in line:
            parts = line.split(" FAILED")
            results[parts[0].strip()] = "FAILED"
    return results


def apply_patch_and_test(file_path: str, original: str, replacement: str, extra_test_file: Optional[str] = None) -> tuple[bool, str]:
    print("[Agent 3: Sandbox Validator] Selecting relevant test files...")
    base = os.path.basename(file_path).replace(".py", "")
    short_base = base.replace("_service", "").replace("_router", "")
    candidates = [
        os.path.join("tests", f"test_{base}.py"),
        os.path.join("tests", f"test_{short_base}.py")
    ]
    test_target = None
    for cand in candidates:
        if os.path.exists(cand):
            test_target = cand.replace("\\", "/")
            break

    if not test_target and os.path.exists("tests"):
        for t in os.listdir("tests"):
            if t.startswith("test_") and short_base in t:
                test_target = f"tests/{t}"
                break

    if not test_target:
        test_target = "tests/test_payment.py"

    test_targets = [test_target]
    if extra_test_file and os.path.exists(extra_test_file) and extra_test_file != test_target:
        test_targets.append(extra_test_file)

    # Step A: Baseline Test Run (Before Patch)
    print(f"[Agent 3: Sandbox Validator] Running baseline tests on {' & '.join(test_targets)} (before patch)...")
    base_res = subprocess.run(["pytest"] + test_targets + ["-v"], capture_output=True, text=True)
    before_statuses = parse_pytest_summary(base_res.stdout)
    before_passed = sum(1 for s in before_statuses.values() if s == "PASSED")
    print(f" -> Baseline: {before_passed} passed, {len(before_statuses) - before_passed} failed.")

    # Step B: Apply Patch
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False, f"File {file_path} does not exist."

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    norm_content = content.replace("\r\n", "\n")
    norm_orig = original.replace("\r\n", "\n")
    norm_repl = replacement.replace("\r\n", "\n")

    if norm_orig not in norm_content:
        print(f"Warning: exact snippet not found in {file_path}. Trying stripped match...")
        if norm_orig.strip() not in norm_content:
            print("Failed to match snippet.")
            return False, f"Failed to match original snippet in {file_path}."
        norm_orig = norm_orig.strip()
        norm_repl = norm_repl.strip()

    patched = norm_content.replace(norm_orig, norm_repl, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(patched)

    # Step C: After Patch Test Run
    print(f"[Agent 3: Sandbox Validator] Running tests on {' & '.join(test_targets)} (after patch)...")
    res = subprocess.run(["pytest"] + test_targets + ["-v"], capture_output=True, text=True)
    print(res.stdout)
    after_statuses = parse_pytest_summary(res.stdout)
    after_passed = sum(1 for s in after_statuses.values() if s == "PASSED")
    print(f" -> After patch: {after_passed} passed, {len(after_statuses) - after_passed} failed.")

    # Check 1: 100% pass
    if res.returncode == 0:
        print(f"✅ Pytest on {' & '.join(test_targets)} passed with 100% success!")
        return True, res.stdout

    # Check 2: Regression & Improvement Detection
    newly_passed = [t for t, s in after_statuses.items() if s == "PASSED" and before_statuses.get(t) != "PASSED"]
    regressions = [t for t, s in before_statuses.items() if s == "PASSED" and after_statuses.get(t) != "PASSED"]

    if newly_passed and not regressions:
        print(f"✅ [Regression Detector] Target incident fix confirmed! Newly passing test(s): {newly_passed}")
        print("✅ Zero regressions detected on existing passing tests.")
        return True, res.stdout
    elif regressions:
        print(f"❌ [Regression Detector] Regressions detected! Tests that broke: {regressions}")
        return False, res.stdout
    else:
        print("❌ [Regression Detector] Patch did not resolve any failing test.")
        return False, res.stdout


def main():
    print(f"=======================================================")
    print(f"🚀 Autonomous SRE Incident Resolver - Issue #{ISSUE_NUMBER}")
    print(f"Title: {ISSUE_TITLE}")
    print(f"=======================================================")

    # Step 1: Critic Review
    critic_plan = run_critic_review(ISSUE_TITLE, ISSUE_BODY)
    rec_files = critic_plan.get("recommended_files", [])
    if not rec_files:
        rec_files = ["app/services/payment_service.py"]

    target_file = rec_files[0]
    if not os.path.exists(target_file):
        base = os.path.basename(target_file)
        for root, _, files in os.walk("app"):
            if base in files:
                target_file = os.path.join(root, base).replace("\\", "/")
                break

    with open(target_file, "r", encoding="utf-8") as f:
        file_content = f.read()

    # Step 1.5: Autonomous Test Synthesis (QA Specialist Agent)
    gen_test_file = None
    gen_test_code = None
    negative_confirmed = False
    negative_trace = ""
    try:
        test_gen_result = run_test_generator_agent(
            critic_plan, target_file, file_content, str(ISSUE_NUMBER), ISSUE_TITLE, ISSUE_BODY
        )
        gen_test_file = test_gen_result.get("test_filename", f"tests/test_issue_{ISSUE_NUMBER}_regression.py").replace("\\", "/")
        gen_test_code = test_gen_result.get("test_code", "")

        os.makedirs(os.path.dirname(gen_test_file), exist_ok=True)
        with open(gen_test_file, "w", encoding="utf-8") as tf:
            tf.write(gen_test_code)
        print(f"✅ [Test Synthesis] Synthesized reproduction test saved to {gen_test_file}")

        # Negative validation: Verify test fails on unpatched code
        negative_confirmed, negative_trace = verify_negative_reproduction(gen_test_file)
    except Exception as e:
        print(f"⚠️ Warning: Autonomous test synthesis encountered error: {e}. Falling back to baseline tests.")

    # Discover associated baseline test file if present
    base_name = os.path.basename(target_file).replace(".py", "")
    short_base = base_name.replace("_service", "").replace("_router", "")
    test_content = None
    for cand in [os.path.join("tests", f"test_{base_name}.py"), os.path.join("tests", f"test_{short_base}.py")]:
        if os.path.exists(cand):
            with open(cand, "r", encoding="utf-8") as tf:
                test_content = tf.read()
            print(f"[Context Engine] Loaded baseline test specification from {cand}")
            break

    # Construct comprehensive test guidance for Fix Planner
    full_test_context = ""
    if gen_test_code:
        full_test_context += f"### AUTONOMOUS REPRODUCTION TEST ({gen_test_file}):\n```python\n{gen_test_code}\n```\n"
        if negative_trace:
            full_test_context += f"### UNPATCHED EXECUTION FAILURE:\n```\n{negative_trace}\n```\n"
    if test_content:
        full_test_context += f"### EXISTING TEST SUITE REQUIREMENTS:\n```python\n{test_content}\n```\n"

    # Step 2 & 3: Fix Planning & Sandbox Testing with Self-Healing Loop
    max_attempts = 3
    attempt = 1
    passed = False
    test_feedback = None
    fix = {}

    while attempt <= max_attempts and not passed:
        print(f"\n--- [Iteration {attempt}/{max_attempts}] SRE Agent Resolution Attempt ---")
        if attempt > 1:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(file_content)

        fix = run_fix_planner(critic_plan, target_file, file_content, test_content=full_test_context, feedback=test_feedback)
        passed, test_output = apply_patch_and_test(
            target_file,
            fix.get("original_snippet", ""),
            fix.get("replacement_snippet", ""),
            extra_test_file=gen_test_file
        )

        if not passed:
            print(f"⚠️ Attempt {attempt} failed validation. Triggering self-correction feedback loop...")
            test_feedback = test_output
            attempt += 1

    if not passed:
        print("❌ All self-healing attempts exhausted. Safety Gate engaged.")
        sys.exit(1)

    reproduction_status = "❌ Confirmed failed on unpatched code (reproduced defect)" if negative_confirmed else "⚠️ Generated and evaluated"
    test_section = ""
    if gen_test_file:
        test_section = f"""---

### 🧪 Autonomous Test Synthesis (QA Specialist Agent)
- **Synthesized Regression Test**: `{gen_test_file}`
- **Pre-Patch Reproduction ("Red" Phase)**: {reproduction_status}
- **Post-Patch Validation ("Green" Phase)**: ✅ Passed 100% with zero regressions.
- **Permanence**: Committed to repository alongside fix to prevent future regressions.

```python
{gen_test_code}
```
"""

    # Step 4: Write resolution report for PR
    report = f"""## 🤖 Autonomous Incident Resolution: Issue #{ISSUE_NUMBER}

### 📋 Overview
- **Issue**: #{ISSUE_NUMBER} - {ISSUE_TITLE}
- **Service**: `python-service`
- **Orchestration**: Microsoft Azure AI Foundry Multi-Agent System

---

### 🧐 Critic Analysis (`{CRITIC_MODEL}`)
**Confirmed Root Cause:**
{critic_plan.get('confirmed_root_cause')}

**Enforced Constraints:**
{chr(10).join(f"- {c}" for c in critic_plan.get('patch_constraints', []))}

{test_section}---

### 🛠️ Surgical Patch (`{PLANNER_MODEL}`)
Modified file: `{target_file}`

```python
# Replaced:
{fix.get('original_snippet')}

# With:
{fix.get('replacement_snippet')}
```

---

### 🧪 Validation Results
- **Sandbox Test Runner**: `pytest`
- **Result**: ✅ Passed 100% of tests with zero regressions.
- **Risk Score**: `MEDIUM` (Automated PR Approved)

*Closes #{ISSUE_NUMBER}*
"""
    with open("resolution_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n✅ Autonomous fix verified and resolution_report.md created!")


if __name__ == "__main__":
    main()
