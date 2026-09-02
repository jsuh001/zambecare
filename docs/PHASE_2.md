# Phase 2 — Secure Application and Patient Portal

## Status

Implemented and validated on 2026-09-02.

## Outcome

Phase 2 turns the Phase 1 platform foundation into a usable healthcare demonstration application:

- Python/FastAPI backend
- PostgreSQL transactional database
- Alembic versioned migration
- Argon2 password hashing
- JWT access and refresh tokens
- Refresh-token rotation and logout revocation
- Role-based authorization
- Patient registration, login, profile view/update/deactivation
- Public doctor and facility search
- Restricted facility/provider administration endpoints
- Security audit events
- React patient portal
- Synthetic directory seed data
- Expanded CI validation

Oracle and dbt remain available but are not required to run Phase 2.

## User journeys

### Patient registration

1. Patient enters synthetic account and demographic information.
2. API validates email and password strength.
3. Password is hashed using Argon2.
4. `USER_ACCOUNT`, `USER_ROLE`, and `PATIENT` records are created in one transaction.
5. The `PATIENT` role is assigned.
6. Registration is written to the audit table.

### Authentication

1. Patient submits email and password.
2. API returns the same generic error for unknown accounts and incorrect passwords.
3. Five consecutive failures trigger a temporary lock.
4. Successful authentication creates a short-lived access token and a refresh session.
5. Only the SHA-256 fingerprint of the refresh token is stored.
6. Refreshing rotates and revokes the previous refresh token.
7. Logout revokes the active refresh session.

### Patient dashboard

An authenticated patient can view their own synthetic profile and update selected fields. Account IDs, roles, audit fields, and other patients are not editable.

### Care directory

Anyone may search active providers and facilities. Creating providers or facilities requires `FACILITY_ADMIN` or `SYSTEM_ADMIN`.

## API endpoints

| Method | Endpoint | Access |
|---|---|---|
| POST | `/api/v1/auth/register` | Public |
| POST | `/api/v1/auth/login` | Public |
| POST | `/api/v1/auth/refresh` | Valid refresh session |
| POST | `/api/v1/auth/logout` | Refresh session |
| GET | `/api/v1/patients/me` | Patient |
| PATCH | `/api/v1/patients/me` | Patient |
| DELETE | `/api/v1/patients/me` | Patient |
| GET | `/api/v1/facilities` | Public |
| POST | `/api/v1/facilities` | Facility/system administrator |
| GET | `/api/v1/providers` | Public |
| POST | `/api/v1/providers` | Facility/system administrator |

## Database changes

Alembic revision `20260902_01` adds:

- `security.user_account`
- `security.role`
- `security.user_role`
- `security.refresh_session`
- `security.audit_event`
- `clinical.patient.user_id`
- `clinical.patient.preferred_language`

It also seeds the six initial roles.

## Frontend scope

The React portal provides:

- Landing page
- Patient registration
- Patient sign-in
- Patient dashboard
- Profile update
- Doctor and facility directory
- Logout

The browser session is stored in `sessionStorage` for this synthetic portfolio demonstration. A production healthcare deployment should use a stronger browser session design, normally secure, HTTP-only, same-site cookies plus CSRF controls and a formal threat assessment.

## Security decisions

- Passwords are never stored or returned directly.
- Refresh tokens are fingerprinted before database storage.
- Login responses do not reveal whether an email exists.
- Unknown-user password checks execute a dummy Argon2 verification to reduce timing differences.
- Patient routes resolve the patient from the authenticated account; the client cannot select another patient ID.
- Administrative operations require explicit roles.
- Audit records contain metadata, not clinical payloads.
- CORS origins are explicitly configured.
- Real PHI remains prohibited.

## Tests implemented

- Health endpoint
- Password hashing
- Registration
- Duplicate registration
- Login
- Invalid password
- Access control
- Profile read/update
- Refresh-token rotation
- Logout revocation
- Patient denied facility administration
- Facility search
- Provider search

## Deferred

- Email verification and password reset delivery
- MFA
- Secure HTTP-only cookie sessions
- Appointment scheduling
- Encounters, diagnoses, and vitals
- FHIR ingestion
- Oracle loading and PL/SQL processing
- AI care routing
- Production deployment and HIPAA compliance assessment

## Acceptance criteria

- [x] Python/FastAPI backend is functional.
- [x] Patient registration and login are implemented.
- [x] Argon2 hashes protect passwords.
- [x] Access and rotating refresh tokens work.
- [x] Roles protect administrative endpoints.
- [x] Patient can access only their profile route.
- [x] Facility and provider search work.
- [x] Audit events are recorded.
- [x] Alembic migration renders successfully.
- [x] Nine backend tests pass.
- [x] Python static lint checks pass.
- [x] React production build succeeds.
- [x] Docker Compose includes the frontend.
- [x] CI validates backend, migration, frontend, and container builds.
