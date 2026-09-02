# Security and HIPAA-Aligned Design

## Important limitation

ZambeCare is an educational portfolio system using synthetic data. Technical controls alone do not establish HIPAA compliance. A real regulated deployment would require a formal risk analysis, organizational policies, workforce training, incident and breach processes, vendor review, appropriate Business Associate Agreements, and legal/compliance oversight.

## Security principles

1. Do not use real PHI.
2. Collect and expose the minimum data needed.
3. Deny access by default.
4. Separate operational identifiers from analytics.
5. Encrypt data in transit and at rest in any hosted environment.
6. Record access metadata without copying clinical data into logs.
7. Treat backups and exports as sensitive as primary data.
8. Test restoration and incident response.

## Planned safeguards

| Safeguard | Design |
|---|---|
| Unique identity | Individual user accounts; no shared clinical accounts |
| Authentication | Strong password hashing; MFA for workforce roles |
| Authorization | Role and relationship-based access; least privilege |
| Session control | Short-lived tokens, refresh rotation, automatic expiration |
| Audit control | Append-only access and change events with request correlation |
| Integrity | Constraints, hashes, reconciliation, controlled migrations |
| Transmission | TLS for APIs and database connections in hosted environments |
| Storage | Encrypted database, object storage, backups, and secrets |
| Secrets | Environment/secret store; never Git or application logs |
| Availability | Health checks, backups, restore tests, runbooks |
| Risk management | Versioned risk register and periodic review |

## Logging rules

Logs may contain:

- Request/correlation ID
- Route template
- Status code
- Duration
- Service and release version
- Internal non-identifying batch ID

Logs must not contain:

- Names, dates of birth, addresses, emails, or phone numbers
- Symptom descriptions, diagnoses, medications, or vital values
- Authentication tokens, cookies, passwords, or database URLs
- Raw FHIR resources

## Threats considered in Phase 1

| Threat | Initial treatment |
|---|---|
| Credentials committed to Git | `.env` ignored; example placeholders; CI pattern check |
| Excessive warehouse access | Separate Oracle schemas and object grants |
| PHI copied into analytics | Direct identifiers omitted from initial dbt staging model |
| Unexplained data loss | Batch reconciliation and rejected-record accounting |
| AI presented as diagnosis | Explicit decision-support boundary and emergency-first rules |
| Resource exhaustion | Optional profiles for large local services |

## Before any public deployment

- Complete a documented risk assessment.
- Add TLS and secure headers.
- Add authenticated role-based access.
- Remove or rotate every development secret.
- Confirm images and dependencies are scanned.
- Confirm backups contain only synthetic data.
- Run authorization and API security tests.
- Verify audit events cannot be modified by application roles.
- Verify no PHI-like values appear in logs.

## Phase 2 implemented controls

- Argon2 password hashing
- Generic invalid-credential responses and dummy unknown-user password verification
- Temporary lockout after repeated password failures
- Short-lived signed access tokens
- Fingerprinted, rotating, revocable refresh sessions
- Patient self-access derived from authenticated identity
- Explicit role checks for directory administration
- Application audit events for registration, login, profile access, and changes
- Explicit CORS origin configuration

The React demonstration currently keeps its session in browser `sessionStorage`. This is acceptable only for the synthetic portfolio environment. A production design requires a dedicated browser-session threat assessment and would normally use secure, HTTP-only, same-site cookies with CSRF defenses.
