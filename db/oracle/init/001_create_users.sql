-- Run as a privileged local development account in FREEPDB1.
-- Passwords are placeholders for Phase 1 and must be supplied securely before execution.
WHENEVER SQLERROR EXIT SQL.SQLCODE;
SET VERIFY OFF;

ALTER SESSION SET CONTAINER = FREEPDB1;

ACCEPT stage_password CHAR PROMPT 'Password for ZC_STAGE: ' HIDE
ACCEPT dw_password CHAR PROMPT 'Password for ZC_DW: ' HIDE
ACCEPT audit_password CHAR PROMPT 'Password for ZC_AUDIT: ' HIDE
ACCEPT dbt_password CHAR PROMPT 'Password for ZC_DBT: ' HIDE

CREATE USER zc_stage IDENTIFIED BY "&stage_password" QUOTA UNLIMITED ON users;
CREATE USER zc_dw IDENTIFIED BY "&dw_password" QUOTA UNLIMITED ON users;
CREATE USER zc_audit IDENTIFIED BY "&audit_password" QUOTA UNLIMITED ON users;
CREATE USER zc_dbt IDENTIFIED BY "&dbt_password" QUOTA UNLIMITED ON users;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE SEQUENCE TO zc_stage;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE MATERIALIZED VIEW, CREATE SEQUENCE TO zc_dw;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE SEQUENCE TO zc_audit;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE MATERIALIZED VIEW TO zc_dbt;

-- Apply object-level grants only after 002_core_objects.sql creates the tables.

UNDEFINE stage_password
UNDEFINE dw_password
UNDEFINE audit_password
UNDEFINE dbt_password
SET VERIFY ON;
