-- ═══════════════════════════════════════════════════════════════
--  Seed Data — Development / Testing Only
--  Run only in dev; production starts with empty tables
-- ═══════════════════════════════════════════════════════════════

DO $$
DECLARE
    v_person1 UUID;
    v_person2 UUID;
    v_person3 UUID;
    v_loan1   UUID;
    v_loan2   UUID;
    v_loan3   UUID;
BEGIN

-- ── Persons ──────────────────────────────────
INSERT INTO persons (id, full_name, nickname, phone, email, relationship, notes)
VALUES
    (gen_random_uuid(), 'Jan de Vries',    'Jan',    '+31 6 12345678', 'jan@example.nl',    'friend',    'Old school friend')
RETURNING id INTO v_person1;

INSERT INTO persons (id, full_name, nickname, phone, email, relationship, notes)
VALUES
    (gen_random_uuid(), 'Maria Santos',   'Maria',  '+31 6 87654321', 'maria@example.nl',  'colleague', 'Works at the office')
RETURNING id INTO v_person2;

INSERT INTO persons (id, full_name, nickname, phone, email, relationship, notes)
VALUES
    (gen_random_uuid(), 'Ahmed Al-Rashid','Ahmed',  '+31 6 11223344', 'ahmed@example.nl',  'family',    'Brother-in-law')
RETURNING id INTO v_person3;

-- ── Loans ─────────────────────────────────────
INSERT INTO loans (id, person_id, direction, principal, currency, interest_rate, interest_type, interest_period, date_issued, due_date, purpose, notes)
VALUES (
    gen_random_uuid(), v_person1, 'lent', 500.00, 'EUR',
    0, 'simple', 'monthly',
    CURRENT_DATE - INTERVAL '30 days',
    CURRENT_DATE + INTERVAL '60 days',
    'Help with rent',
    'Jan needed help with last month rent'
) RETURNING id INTO v_loan1;

INSERT INTO loans (id, person_id, direction, principal, currency, interest_rate, interest_type, interest_period, date_issued, due_date, purpose)
VALUES (
    gen_random_uuid(), v_person2, 'lent', 1200.00, 'EUR',
    5.0, 'simple', 'yearly',
    CURRENT_DATE - INTERVAL '90 days',
    CURRENT_DATE - INTERVAL '10 days',   -- already overdue
    'Laptop purchase'
) RETURNING id INTO v_loan2;

INSERT INTO loans (id, person_id, direction, principal, currency, interest_rate, interest_type, interest_period, date_issued, due_date, purpose)
VALUES (
    gen_random_uuid(), v_person3, 'borrowed', 800.00, 'EUR',
    0, 'simple', 'monthly',
    CURRENT_DATE - INTERVAL '15 days',
    CURRENT_DATE + INTERVAL '45 days',
    'Car repair emergency'
) RETURNING id INTO v_loan3;

-- ── Payments ──────────────────────────────────
INSERT INTO payments (loan_id, amount, payment_date, method, notes)
VALUES (v_loan1, 200.00, CURRENT_DATE - INTERVAL '10 days', 'bank_transfer', 'First instalment');

INSERT INTO payments (loan_id, amount, payment_date, method, notes)
VALUES (v_loan2, 300.00, CURRENT_DATE - INTERVAL '5 days', 'cash', 'Partial repayment');

END $$;
