# AFH-DEMO — E-Commerce Core Microservice

A Python FastAPI microservice handling authentication, user sessions, and checkout payment processing.
Used as the target testing repository for the **Amaze on Work** Autonomous SRE & Incident Healing Agent.

## Architecture & Services
- `app/routes/auth.py`: User authentication, bcrypt hash validation, and JWT sessions (`INC-001`)
- `app/services/payment_service.py`: Checkout pricing and discount calculations (`INC-002`)
- `app/services/shipping_service.py`: Shipping rate computation based on weight and distance (`INC-003`)
- `app/services/inventory_service.py`: Stock reservation and catalog pagination (`INC-004`, `INC-005`)
- `app/services/user_service.py`: Customer profile updates and preference management (`INC-006`)
- `app/services/audit_service.py`: Structured compliance and audit event logging (`INC-007`)
- `app/services/webhook_service.py`: Partner webhook dispatch and endpoint validation (`INC-008`)
- `app/services/analytics_service.py`: Metric ingestion and query parameter parsing (`INC-009`)
- `app/services/rate_limiter.py`: API gateway proxy header parsing and IP rate limiting (`INC-010`)
- `app/services/cart_service.py`: Cart item subtotal IEEE-754 precision integrity validation (`INC-011`)

## Incident Repository
Each incident alert ticket with error logs, stack traces, and expected behavior is stored in `incidents/INC-*.json`.

## Running Tests
```bash
pytest tests/ -v
```
