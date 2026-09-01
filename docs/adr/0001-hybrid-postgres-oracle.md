# ADR 0001: Use PostgreSQL OLTP and Oracle Analytics

- Status: Accepted
- Date: 2026-09-01

## Context

The platform needs a low-cost transactional backend while also demonstrating the Oracle engineering depth required by the target Senior Oracle Data Engineer role.

## Decision

Use PostgreSQL for the patient-facing transactional application and Oracle AI Database Free for staging, PL/SQL processing, reconciliation, dimensional analytics, and performance laboratories.

## Consequences

- Creates a realistic heterogeneous integration problem.
- Preserves the requested Python/PostgreSQL backend.
- Makes Oracle central to the data-engineering portfolio.
- Requires cross-database reconciliation and careful type mapping.
- Oracle runs only when needed to conserve local resources.
