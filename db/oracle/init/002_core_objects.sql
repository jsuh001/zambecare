-- Connect as ZC_STAGE before running the staging section.
CREATE TABLE stg_patient (
    batch_id             NUMBER(18) NOT NULL,
    source_record_id     VARCHAR2(100) NOT NULL,
    source_system        VARCHAR2(50) NOT NULL,
    patient_json         CLOB,
    first_name           VARCHAR2(100),
    last_name            VARCHAR2(100),
    date_of_birth        DATE,
    email                VARCHAR2(255),
    load_timestamp       TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    validation_status    VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    validation_message   VARCHAR2(1000),
    CONSTRAINT pk_stg_patient PRIMARY KEY (batch_id, source_record_id),
    CONSTRAINT ck_stg_patient_status CHECK (
        validation_status IN ('PENDING', 'VALID', 'REJECTED', 'LOADED')
    )
);

CREATE TABLE stg_encounter (
    batch_id             NUMBER(18) NOT NULL,
    source_record_id     VARCHAR2(100) NOT NULL,
    source_patient_id    VARCHAR2(100) NOT NULL,
    encounter_type       VARCHAR2(30),
    encounter_status     VARCHAR2(20),
    started_at           TIMESTAMP WITH TIME ZONE,
    ended_at             TIMESTAMP WITH TIME ZONE,
    load_timestamp       TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    validation_status    VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    validation_message   VARCHAR2(1000),
    CONSTRAINT pk_stg_encounter PRIMARY KEY (batch_id, source_record_id)
);

-- Connect as ZC_AUDIT before running the audit section.
CREATE TABLE etl_batch (
    batch_id             NUMBER(18) PRIMARY KEY,
    source_system        VARCHAR2(50) NOT NULL,
    entity_name          VARCHAR2(50) NOT NULL,
    started_at           TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    completed_at         TIMESTAMP WITH TIME ZONE,
    batch_status         VARCHAR2(20) NOT NULL,
    source_count         NUMBER(18),
    accepted_count       NUMBER(18),
    rejected_count       NUMBER(18),
    CONSTRAINT ck_etl_batch_status CHECK (
        batch_status IN ('STARTED', 'VALIDATING', 'TRANSFORMING', 'COMPLETED', 'FAILED')
    )
);

CREATE TABLE rejected_record (
    rejection_id         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id             NUMBER(18) NOT NULL,
    source_entity        VARCHAR2(50) NOT NULL,
    source_record_id     VARCHAR2(100) NOT NULL,
    rule_code            VARCHAR2(50) NOT NULL,
    rejection_reason     VARCHAR2(1000) NOT NULL,
    rejected_at          TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE TABLE reconciliation_result (
    reconciliation_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id             NUMBER(18) NOT NULL,
    entity_name          VARCHAR2(50) NOT NULL,
    source_count         NUMBER(18) NOT NULL,
    target_count         NUMBER(18) NOT NULL,
    rejected_count       NUMBER(18) NOT NULL,
    unexplained_count    NUMBER(18) NOT NULL,
    reconciliation_status VARCHAR2(10) NOT NULL,
    checked_at           TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT ck_recon_status CHECK (reconciliation_status IN ('PASS', 'FAIL'))
);

-- Connect as ZC_DW before running the warehouse section.
CREATE TABLE dim_patient (
    patient_key          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_patient_id    VARCHAR2(100) NOT NULL,
    source_system        VARCHAR2(50) NOT NULL,
    birth_year           NUMBER(4),
    current_flag         CHAR(1) DEFAULT 'Y' NOT NULL,
    effective_from       TIMESTAMP WITH TIME ZONE NOT NULL,
    effective_to         TIMESTAMP WITH TIME ZONE,
    row_hash             VARCHAR2(64),
    CONSTRAINT ck_dim_patient_current CHECK (current_flag IN ('Y', 'N'))
);

CREATE UNIQUE INDEX ux_dim_patient_current
    ON dim_patient (
        CASE WHEN current_flag = 'Y' THEN source_system END,
        CASE WHEN current_flag = 'Y' THEN source_patient_id END
    );

CREATE TABLE fact_encounter (
    encounter_key        NUMBER GENERATED ALWAYS AS IDENTITY,
    patient_key          NUMBER NOT NULL,
    batch_id             NUMBER(18) NOT NULL,
    source_encounter_id  VARCHAR2(100) NOT NULL,
    encounter_type       VARCHAR2(30),
    encounter_status     VARCHAR2(20),
    started_at           TIMESTAMP NOT NULL,
    ended_at             TIMESTAMP,
    load_timestamp       TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_fact_encounter PRIMARY KEY (encounter_key),
    CONSTRAINT fk_fact_encounter_patient FOREIGN KEY (patient_key)
        REFERENCES dim_patient(patient_key)
)
PARTITION BY RANGE (started_at)
INTERVAL (NUMTOYMINTERVAL(1, 'MONTH'))
(
    PARTITION p_initial VALUES LESS THAN (TIMESTAMP '2025-01-01 00:00:00')
);

CREATE INDEX ix_fact_encounter_patient
    ON fact_encounter(patient_key, started_at) LOCAL;
