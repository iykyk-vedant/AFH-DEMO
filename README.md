# AFH-DEMO — E-Commerce Core Microservice

A Python FastAPI microservice handling authentication, user sessions, and checkout payment processing.
Used as the target testing repository for the **Amaze on Work** Autonomous SRE & Incident Healing Agent.

## Architecture
- `app/routes/auth.py`: User authentication and JWT session validation
- `app/services/payment_service.py`: Checkout pricing and discount calculations
- `tests/`: Pytest unit test suites
- `incidents/`: Production incident alerts and failure reports

## Running Tests
```bash
pytest tests/ -v
```
