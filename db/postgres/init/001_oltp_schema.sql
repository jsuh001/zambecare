CREATE SCHEMA IF NOT EXISTS clinical;
CREATE SCHEMA IF NOT EXISTS security;

CREATE TABLE IF NOT EXISTS clinical.patient (
    patient_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_patient_id UUID NOT NULL UNIQUE,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    date_of_birth       DATE NOT NULL,
    sex_at_birth        VARCHAR(20),
    email               VARCHAR(255) NOT NULL UNIQUE,
    phone               VARCHAR(30),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE
);

-- Phase 2 links this table to security.user_account through an Alembic migration.

CREATE TABLE IF NOT EXISTS clinical.facility (
    facility_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    facility_name       VARCHAR(200) NOT NULL CONSTRAINT uq_facility_name UNIQUE,
    facility_type       VARCHAR(50) NOT NULL,
    address_line_1      VARCHAR(200) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    state_code          CHAR(2) NOT NULL,
    postal_code         VARCHAR(10) NOT NULL,
    latitude            NUMERIC(9,6),
    longitude           NUMERIC(9,6),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS clinical.provider (
    provider_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    facility_id         BIGINT REFERENCES clinical.facility(facility_id),
    npi                  VARCHAR(10) UNIQUE,
    first_name           VARCHAR(100) NOT NULL,
    last_name            VARCHAR(100) NOT NULL,
    specialty_code      VARCHAR(50) NOT NULL,
    is_accepting_patients BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS clinical.encounter (
    encounter_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id          BIGINT NOT NULL REFERENCES clinical.patient(patient_id),
    provider_id         BIGINT REFERENCES clinical.provider(provider_id),
    facility_id         BIGINT REFERENCES clinical.facility(facility_id),
    encounter_type      VARCHAR(30) NOT NULL,
    encounter_status    VARCHAR(20) NOT NULL,
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    batch_id            BIGINT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_encounter_status CHECK (
        encounter_status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')
    ),
    CONSTRAINT ck_encounter_dates CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE IF NOT EXISTS clinical.diagnosis (
    diagnosis_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    encounter_id        BIGINT NOT NULL REFERENCES clinical.encounter(encounter_id),
    diagnosis_code      VARCHAR(20) NOT NULL,
    diagnosis_system    VARCHAR(30) NOT NULL DEFAULT 'ICD-10-CM',
    diagnosis_text      VARCHAR(500),
    diagnosis_type      VARCHAR(20) NOT NULL,
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clinical.vital_sign (
    vital_sign_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    encounter_id        BIGINT NOT NULL REFERENCES clinical.encounter(encounter_id),
    observation_code    VARCHAR(30) NOT NULL,
    observation_name    VARCHAR(100) NOT NULL,
    numeric_value       NUMERIC(12,4) NOT NULL,
    unit_code           VARCHAR(30) NOT NULL,
    observed_at         TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS security.phi_access_audit (
    audit_id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_id            VARCHAR(100) NOT NULL,
    actor_role          VARCHAR(50) NOT NULL,
    action_name         VARCHAR(50) NOT NULL,
    resource_type       VARCHAR(50) NOT NULL,
    resource_id         VARCHAR(100) NOT NULL,
    occurred_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id          UUID NOT NULL,
    outcome             VARCHAR(20) NOT NULL,
    source_ip_hash      VARCHAR(128),
    CONSTRAINT ck_audit_outcome CHECK (outcome IN ('SUCCESS', 'DENIED', 'ERROR'))
);

CREATE INDEX IF NOT EXISTS ix_encounter_patient_started
    ON clinical.encounter(patient_id, started_at DESC);
CREATE INDEX IF NOT EXISTS ix_diagnosis_encounter
    ON clinical.diagnosis(encounter_id);
CREATE INDEX IF NOT EXISTS ix_vital_encounter_observed
    ON clinical.vital_sign(encounter_id, observed_at DESC);

COMMENT ON SCHEMA clinical IS 'Synthetic transactional healthcare data for ZambeCare.';
COMMENT ON TABLE security.phi_access_audit IS 'Append-only demonstration audit trail; never log clinical payloads.';
