-- Synthetic care-directory seed data (portfolio demo only; no real people).
-- Idempotent: facilities dedupe on name, providers dedupe on the UNIQUE npi.

INSERT INTO clinical.facility (
    facility_name, facility_type, address_line_1, city, state_code, postal_code, latitude, longitude
)
VALUES
    ('ZambeCare Dallas Clinic',        'CLINIC',       '100 Synthetic Health Way', 'Dallas',  'TX', '75201', 32.776700, -96.797000),
    ('North Texas Community Hospital', 'HOSPITAL',     '250 Demo Medical Drive',   'Plano',   'TX', '75024', 33.019800, -96.698900),
    ('Oak Health Urgent Care',         'URGENT_CARE',  '18 Example Avenue',        'Irving',  'TX', '75039', 32.814000, -96.948900),
    ('Austin Sample Medical Center',   'HOSPITAL',     '900 Placeholder Parkway',  'Austin',  'TX', '78701', 30.267200, -97.743100),
    ('Houston Model Family Clinic',    'CLINIC',       '55 Mock Street',           'Houston', 'TX', '77002', 29.760400, -95.369800)
ON CONFLICT (facility_name) DO NOTHING;

-- Provider rows are attached to a facility by name and carry a distinct NPI so the
-- INSERT can safely run more than once.
INSERT INTO clinical.provider (facility_id, npi, first_name, last_name, specialty_code, is_accepting_patients)
SELECT f.facility_id, v.npi, v.first_name, v.last_name, v.specialty_code, v.is_accepting_patients
FROM (VALUES
    ('ZambeCare Dallas Clinic',        '0000000001', 'Amara',   'Testdoctor',    'PRIMARY_CARE',          TRUE),
    ('Houston Model Family Clinic',     '0000000002', 'Noah',    'Sampleton',     'PRIMARY_CARE',          TRUE),
    ('North Texas Community Hospital',  '0000000003', 'David',   'Example',       'CARDIOLOGY',            TRUE),
    ('Austin Sample Medical Center',    '0000000004', 'Priya',   'Mockford',      'CARDIOLOGY',            FALSE),
    ('ZambeCare Dallas Clinic',         '0000000005', 'Lina',    'Democlinician', 'DERMATOLOGY',           TRUE),
    ('North Texas Community Hospital',  '0000000006', 'Omar',    'Placeholder',   'ORTHOPEDICS',           TRUE),
    ('Houston Model Family Clinic',     '0000000007', 'Grace',   'Testerman',     'PEDIATRICS',            TRUE),
    ('Austin Sample Medical Center',    '0000000008', 'Elena',   'Sampleburg',    'BEHAVIORAL_HEALTH',     TRUE),
    ('North Texas Community Hospital',  '0000000009', 'Maria',   'Exampleton',    'OBSTETRICS_GYNECOLOGY', TRUE),
    ('ZambeCare Dallas Clinic',         '0000000010', 'James',   'Mockler',       'ENDOCRINOLOGY',         TRUE),
    ('Austin Sample Medical Center',    '0000000011', 'Sofia',   'Demova',        'GASTROENTEROLOGY',      TRUE),
    ('Houston Model Family Clinic',     '0000000012', 'Daniel',  'Placeholder',   'OPHTHALMOLOGY',         TRUE),
    ('Oak Health Urgent Care',         '0000000013', 'Ruth',    'Sampleworth',   'PRIMARY_CARE',          TRUE),
    ('North Texas Community Hospital',  '0000000014', 'Kwame',   'Testcroft',     'PEDIATRICS',            TRUE)
) AS v(facility_name, npi, first_name, last_name, specialty_code, is_accepting_patients)
JOIN clinical.facility f ON f.facility_name = v.facility_name
ON CONFLICT DO NOTHING;
