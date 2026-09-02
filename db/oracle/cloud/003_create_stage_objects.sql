-- Source-aligned healthcare staging. Run as ADMIN after audit objects.
WHENEVER SQLERROR EXIT SQL.SQLCODE

CREATE TABLE zc_stage.stg_patient (
    batch_id NUMBER NOT NULL,
    source_system VARCHAR2(50) NOT NULL,
    source_record_id VARCHAR2(100) NOT NULL,
    external_patient_id VARCHAR2(100),
    first_name VARCHAR2(100), last_name VARCHAR2(100),
    date_of_birth DATE, sex_at_birth VARCHAR2(20),
    email VARCHAR2(255), phone VARCHAR2(30),
    raw_resource CLOB, record_checksum VARCHAR2(64) NOT NULL,
    validation_status VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    validation_message VARCHAR2(1000),
    loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_stg_patient PRIMARY KEY (batch_id, source_system, source_record_id),
    CONSTRAINT ck_stg_patient_json CHECK (raw_resource IS JSON),
    CONSTRAINT ck_stg_patient_status CHECK (validation_status IN ('PENDING','VALID','REJECTED'))
);

CREATE TABLE zc_stage.stg_practitioner (
    batch_id NUMBER NOT NULL, source_system VARCHAR2(50) NOT NULL,
    source_record_id VARCHAR2(100) NOT NULL, practitioner_identifier VARCHAR2(100),
    first_name VARCHAR2(100), last_name VARCHAR2(100), specialty_code VARCHAR2(50),
    raw_resource CLOB, record_checksum VARCHAR2(64) NOT NULL,
    validation_status VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    validation_message VARCHAR2(1000), loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_stg_practitioner PRIMARY KEY (batch_id, source_system, source_record_id),
    CONSTRAINT ck_stg_practitioner_json CHECK (raw_resource IS JSON),
    CONSTRAINT ck_stg_practitioner_status CHECK (validation_status IN ('PENDING','VALID','REJECTED'))
);

CREATE TABLE zc_stage.stg_facility (
    batch_id NUMBER NOT NULL, source_system VARCHAR2(50) NOT NULL,
    source_record_id VARCHAR2(100) NOT NULL, facility_name VARCHAR2(200),
    facility_type VARCHAR2(50), address_line_1 VARCHAR2(200), city VARCHAR2(100),
    state_code VARCHAR2(10), postal_code VARCHAR2(20), latitude NUMBER(9,6), longitude NUMBER(9,6),
    raw_resource CLOB, record_checksum VARCHAR2(64) NOT NULL,
    validation_status VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    validation_message VARCHAR2(1000), loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_stg_facility PRIMARY KEY (batch_id, source_system, source_record_id),
    CONSTRAINT ck_stg_facility_json CHECK (raw_resource IS JSON),
    CONSTRAINT ck_stg_facility_status CHECK (validation_status IN ('PENDING','VALID','REJECTED'))
);

CREATE TABLE zc_stage.stg_encounter (
    batch_id NUMBER NOT NULL, source_system VARCHAR2(50) NOT NULL,
    source_record_id VARCHAR2(100) NOT NULL, source_patient_id VARCHAR2(100) NOT NULL,
    source_practitioner_id VARCHAR2(100), source_facility_id VARCHAR2(100),
    encounter_type VARCHAR2(30), encounter_status VARCHAR2(20),
    started_at TIMESTAMP WITH TIME ZONE, ended_at TIMESTAMP WITH TIME ZONE,
    raw_resource CLOB, record_checksum VARCHAR2(64) NOT NULL,
    validation_status VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    validation_message VARCHAR2(1000), loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_stg_encounter PRIMARY KEY (batch_id, source_system, source_record_id),
    CONSTRAINT ck_stg_encounter_json CHECK (raw_resource IS JSON),
    CONSTRAINT ck_stg_encounter_dates CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT ck_stg_encounter_status CHECK (validation_status IN ('PENDING','VALID','REJECTED'))
);

CREATE TABLE zc_stage.stg_condition (
    batch_id NUMBER NOT NULL, source_system VARCHAR2(50) NOT NULL,
    source_record_id VARCHAR2(100) NOT NULL, source_patient_id VARCHAR2(100) NOT NULL,
    source_encounter_id VARCHAR2(100), condition_code VARCHAR2(30), code_system VARCHAR2(200),
    clinical_status VARCHAR2(30), recorded_at TIMESTAMP WITH TIME ZONE,
    raw_resource CLOB, record_checksum VARCHAR2(64) NOT NULL,
    validation_status VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    validation_message VARCHAR2(1000), loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_stg_condition PRIMARY KEY (batch_id, source_system, source_record_id),
    CONSTRAINT ck_stg_condition_json CHECK (raw_resource IS JSON),
    CONSTRAINT ck_stg_condition_status CHECK (validation_status IN ('PENDING','VALID','REJECTED'))
);

CREATE TABLE zc_stage.stg_observation (
    batch_id NUMBER NOT NULL, source_system VARCHAR2(50) NOT NULL,
    source_record_id VARCHAR2(100) NOT NULL, source_patient_id VARCHAR2(100) NOT NULL,
    source_encounter_id VARCHAR2(100), observation_code VARCHAR2(30), observation_name VARCHAR2(100),
    numeric_value NUMBER(12,4), unit_code VARCHAR2(30), observed_at TIMESTAMP WITH TIME ZONE,
    raw_resource CLOB, record_checksum VARCHAR2(64) NOT NULL,
    validation_status VARCHAR2(20) DEFAULT 'PENDING' NOT NULL,
    validation_message VARCHAR2(1000), loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_stg_observation PRIMARY KEY (batch_id, source_system, source_record_id),
    CONSTRAINT ck_stg_observation_json CHECK (raw_resource IS JSON),
    CONSTRAINT ck_stg_observation_status CHECK (validation_status IN ('PENDING','VALID','REJECTED'))
);

CREATE INDEX zc_stage.ix_stg_patient_source ON zc_stage.stg_patient(source_system, source_record_id);
CREATE INDEX zc_stage.ix_stg_enc_patient ON zc_stage.stg_encounter(source_patient_id, started_at);
CREATE INDEX zc_stage.ix_stg_condition_patient ON zc_stage.stg_condition(source_patient_id, recorded_at);
CREATE INDEX zc_stage.ix_stg_observation_patient ON zc_stage.stg_observation(source_patient_id, observed_at);

