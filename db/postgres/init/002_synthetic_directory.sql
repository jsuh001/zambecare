INSERT INTO clinical.facility (
    facility_name, facility_type, address_line_1, city, state_code, postal_code, latitude, longitude
)
VALUES
    ('ZambeCare Dallas Clinic', 'CLINIC', '100 Synthetic Health Way', 'Dallas', 'TX', '75201', 32.776700, -96.797000),
    ('North Texas Community Hospital', 'HOSPITAL', '250 Demo Medical Drive', 'Plano', 'TX', '75024', 33.019800, -96.698900),
    ('Oak Health Urgent Care', 'URGENT_CARE', '18 Example Avenue', 'Irving', 'TX', '75039', 32.814000, -96.948900)
ON CONFLICT DO NOTHING;

INSERT INTO clinical.provider (
    facility_id, npi, first_name, last_name, specialty_code, is_accepting_patients
)
SELECT facility_id, '0000000001', 'Amara', 'Testdoctor', 'PRIMARY_CARE', TRUE
FROM clinical.facility WHERE facility_name = 'ZambeCare Dallas Clinic'
ON CONFLICT DO NOTHING;

INSERT INTO clinical.provider (
    facility_id, npi, first_name, last_name, specialty_code, is_accepting_patients
)
SELECT facility_id, '0000000002', 'David', 'Example', 'CARDIOLOGY', TRUE
FROM clinical.facility WHERE facility_name = 'North Texas Community Hospital'
ON CONFLICT DO NOTHING;

INSERT INTO clinical.provider (
    facility_id, npi, first_name, last_name, specialty_code, is_accepting_patients
)
SELECT facility_id, '0000000003', 'Lina', 'Democlinician', 'DERMATOLOGY', TRUE
FROM clinical.facility WHERE facility_name = 'ZambeCare Dallas Clinic'
ON CONFLICT DO NOTHING;
