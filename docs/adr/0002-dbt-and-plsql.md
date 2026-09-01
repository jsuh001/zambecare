# ADR 0002: Combine PL/SQL and dbt

- Status: Accepted
- Date: 2026-09-01

## Context

dbt makes transformations, tests, lineage, documentation, and reconciliation accessible, while the target role expects strong production PL/SQL.

## Decision

Use PL/SQL for operational validation, bulk loading, batch state, exceptions, and recovery. Use dbt for analytical transformations, incremental models, dimensional models, tests, lineage, and reconciliation views.

## Consequences

- Demonstrates traditional Oracle and modern analytics engineering.
- Avoids hiding all transformation logic inside procedures.
- Requires clear ownership so the same transformation is not implemented twice.
