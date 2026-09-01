# ZambeCare — Living Project Documentation

## 1. Executive summary

ZambeCare is a personal portfolio platform demonstrating senior-level Oracle data engineering in a healthcare setting. A transactional application captures synthetic patient, provider, encounter, diagnosis, facility, and observation data. Data from the application and standards-based files flows through controlled ingestion into an Oracle analytical environment. PL/SQL performs operational validation and batch control; dbt performs visible, version-controlled analytical transformations and reconciliation.

The project is aligned to the capabilities emphasized by Bitscopic: Oracle SQL and PL/SQL, ETL/ELT, healthcare integration, data modeling, performance tuning, production support, data quality, observability, DevOps, and secure handling of sensitive data.

## 2. Business problem

Healthcare data commonly arrives from multiple systems with inconsistent identifiers, formats, terminology, and timeliness. Analysts and clinical operations teams require trustworthy, traceable data. ZambeCare demonstrates how to:

- Capture patient-care interactions.
- Route a patient toward an appropriate level and location of care.
- Ingest operational and FHIR-shaped clinical information.
- Validate and standardize records.
- Preserve rejected data and explain failures.
- Create analytics-ready facts and dimensions.
- Reconcile every batch from source to target.
- Protect identifying data and audit access.

## 3. Personas

| Persona | Primary capabilities |
|---|---|
| Patient | Register, submit symptoms, locate care, view authorized history |
| Doctor | Review assigned patients, document encounters and diagnoses |
| Nurse | Record vital signs and observations for authorized encounters |
| Facility administrator | Maintain facility/provider availability |
| Data engineer | Operate pipelines, investigate failures, reconcile batches |
| Security auditor | Review access and security events without modifying clinical data |
| Analyst | Query de-identified analytical models |

## 4. System context

The system is separated into operational and analytical responsibilities.

- **Operational application:** FastAPI and PostgreSQL prioritize validated transactions.
- **Integration layer:** Python and Airflow extract synthetic PostgreSQL changes and parse FHIR JSON/CSV.
- **Oracle staging:** Retains source lineage and validation status.
- **PL/SQL control layer:** Validates, rejects, records batch state, and supports safe restart.
- **dbt transformation layer:** Builds analytics models, tests assumptions, documents lineage, and reconciles batches.
- **Presentation layer:** Superset/Grafana dashboards are introduced after reliable models exist.

## 5. Data flow

1. A synthetic transaction is committed in PostgreSQL.
2. An ingestion job assigns a unique batch ID and extracts a bounded dataset.
3. Data is loaded without destructive transformation into Oracle staging.
4. PL/SQL validates required fields, relationships, codes, and temporal rules.
5. Invalid records are placed in `ZC_AUDIT.REJECTED_RECORD` with explainable rule codes.
6. dbt builds incremental facts and dimensions from valid records.
7. dbt reconciliation confirms source = target + rejected.
8. Failed tests stop promotion and create an operational incident.
9. Authorized reporting models expose minimized or de-identified data.

## 6. Data architecture

### PostgreSQL operational model

The normalized OLTP model is the system of engagement for the demonstration application. Direct identifiers remain restricted to the operational boundary.

### Oracle schemas

| Schema | Purpose |
|---|---|
| `ZC_STAGE` | Raw/source-aligned data and validation state |
| `ZC_AUDIT` | Batch controls, exceptions, reconciliation, audit events |
| `ZC_DW` | Curated dimensions, facts, and materialized summaries |
| `ZC_DBT` | dbt-owned views/tables where adapter ownership is appropriate |

### Dimensional model

The target design uses conformed dimensions for patient, provider, facility, diagnosis, and date. Facts include encounters, observations, referrals, and appointments. Patient analytics use a warehouse surrogate key and exclude unnecessary direct identifiers.

## 7. Healthcare interoperability

The first supported FHIR R4-shaped resources will be:

- Patient
- Practitioner
- Organization
- Appointment
- Encounter
- Condition
- Observation

Mappings will retain source identifiers, source system, ingestion timestamp, and raw-resource checksum. Observations will initially cover common vital signs. OMOP-inspired analytical mappings will be added for Person, Care Site, Provider, Visit Occurrence, Condition Occurrence, and Measurement.

## 8. AI safety design

The symptom feature is a routing aid, not a diagnosis engine.

1. Deterministic emergency rules run first.
2. Emergency indicators produce clear instructions to seek emergency help.
3. Non-emergency inputs may be categorized by specialty and urgency.
4. Explanations identify the symptoms that influenced routing.
5. Model output cannot write a confirmed diagnosis.
6. The portfolio will use synthetic prompts and preferably a local model.
7. External AI services will not receive real PHI.

## 9. Data quality framework

Data quality is implemented at several boundaries:

- API validation prevents structurally invalid input.
- Database constraints protect local integrity.
- PL/SQL rules apply clinical and batch validations.
- dbt tests verify analytical assumptions and relationships.
- Reconciliation accounts for every extracted record.

Initial quality dimensions are completeness, validity, uniqueness, consistency, integrity, timeliness, and reconciliation accuracy.

## 10. Batch processing standard

Every ingestion batch records:

- Batch ID
- Source system and entity
- Extraction watermark
- Start/end timestamps
- Source, accepted, rejected, and target counts
- Current state
- Error message and retry count
- Code/release version

Loads will be idempotent through stable business keys and batch-aware merge logic. A rerun must not duplicate accepted records. Failed batches restart from a defined checkpoint or are safely replayed.

## 11. Reconciliation standard

The minimum record-count equation is:

`source_count = target_count + rejected_count`

Later reconciliation adds domain-specific totals, null distributions, distinct business keys, and hash comparisons. dbt reconciliation models are tagged and runnable with:

```bash
dbt build --select tag:reconciliation
```

Any unexplained difference fails the pipeline.

## 12. Performance engineering plan

The project will include documented laboratories for:

- Full scans versus indexed access
- Composite and function-based indexes
- Partition pruning
- Local versus global indexes
- Materialized views and query rewrite
- Statistics and cardinality estimation
- Join order and access paths
- PL/SQL row processing versus bulk operations
- Incremental versus full refresh

Each laboratory stores SQL, execution plan, runtime, logical I/O where available, diagnosis, change, and measured result.

## 13. DevOps strategy

### GitHub Actions

Pull-request CI runs unit tests, static validation, container builds, and later security and SQL tests. It never receives production secrets.

### Jenkins

Jenkins demonstrates controlled promotion: validate, test, build immutable images, apply versioned database changes, execute dbt, verify reconciliation, require approval, deploy, and support rollback.

### Containers

The lightweight core profile runs daily development services. Resource-intensive Oracle, Airflow, Jenkins, SonarQube, and observability services are activated only when needed.

## 14. Security architecture

Security is based on least privilege, separation of duties, minimum necessary data, encryption, immutable evidence, tested recovery, and explicit risk assessment. Detailed controls are in `SECURITY_AND_HIPAA.md`.

## 15. Testing strategy

| Layer | Test type |
|---|---|
| API | Unit, schema, authentication, authorization, integration |
| PostgreSQL | Constraints, migrations, transactional integration |
| PL/SQL | utPLSQL packages, invalid records, restart scenarios |
| dbt | Source, generic, singular, unit, reconciliation tests |
| Pipelines | Idempotency, retry, late data, partial failure |
| Security | SAST, secrets, dependencies, containers, API DAST |
| Performance | Repeatable execution-plan laboratories |
| Recovery | Backup restoration and batch replay drills |

## 16. Observability plan

Metrics will include batch duration, throughput, rejection rate, reconciliation failures, API latency, database connection utilization, freshness, and retry count. Logs must use correlation IDs and must not contain direct identifiers, symptoms, diagnoses, tokens, or credentials.

## 17. Cost strategy

- Run locally using free/open-source tools.
- Use Oracle AI Database Free only when practicing Oracle tasks.
- Use synthetic data so paid HIPAA-eligible hosting is unnecessary.
- Avoid always-on cloud services during development.
- Publish a restricted synthetic-data demo only after core engineering is stable.

## 18. Interview evidence produced

The repository will ultimately contain:

- Architecture decision records
- Data model and dictionary
- FHIR-to-Oracle mappings
- PL/SQL packages and utPLSQL tests
- dbt lineage and reconciliation
- Before/after execution plans
- Pipeline incident runbooks
- CI/CD pipeline history
- Security risk register
- Demo script and concise presentation

## 19. Definition of done

A phase is complete only when code, tests, documentation, security considerations, operational instructions, and interview talking points agree with one another.
