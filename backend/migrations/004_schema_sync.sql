-- 1. Drop the old view to modify tables safely
DROP VIEW IF EXISTS v_loan_summary CASCADE;

-- 2. Fix the loans table
ALTER TABLE loans RENAME COLUMN term_months TO tenure_months;
ALTER TABLE loans ADD COLUMN IF NOT EXISTS institution_type VARCHAR(20) DEFAULT 'non_institutional';
ALTER TABLE loans ADD COLUMN IF NOT EXISTS emi_amount NUMERIC(15,2);
CREATE TYPE day_count_method AS ENUM ('actual_365', 'bank_30_360');
ALTER TABLE loans ADD COLUMN IF NOT EXISTS day_count_method day_count_method NOT NULL DEFAULT 'actual_365';
ALTER TABLE loans ADD COLUMN IF NOT EXISTS emi_start_date DATE;

-- 3. Fix the payments table
ALTER TABLE payments ADD COLUMN IF NOT EXISTS tax_rate NUMERIC(5,2) DEFAULT 0;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS tax_amount NUMERIC(15,2) DEFAULT 0;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS is_manual BOOLEAN DEFAULT FALSE;

-- 4. Fix the loan_fees table
ALTER TABLE loan_fees ADD COLUMN IF NOT EXISTS tax_rate NUMERIC(5,2) DEFAULT 0;
ALTER TABLE loan_fees ADD COLUMN IF NOT EXISTS tax_amount NUMERIC(15,2) DEFAULT 0;

-- 5. Recreate the dashboard view with the new columns
CREATE VIEW v_loan_summary AS
SELECT
    l.id, l.direction, l.status, l.currency, l.principal,
    l.interest_rate, l.interest_type, l.interest_period,
    l.tenure_months, l.emi_amount, l.day_count_method, l.institution_type,
    l.total_paid, l.total_interest, l.balance_due,
    l.date_issued, l.emi_start_date, l.due_date, l.purpose,
    p.id AS person_id, p.full_name AS person_name, p.nickname AS person_nickname,
    p.phone AS person_phone, p.relationship AS person_relationship,
    CASE
        WHEN l.due_date IS NOT NULL AND l.due_date < CURRENT_DATE AND l.status NOT IN ('settled','cancelled')
        THEN (CURRENT_DATE - l.due_date)
        ELSE NULL
    END AS days_overdue,
    CASE
        WHEN l.due_date IS NOT NULL AND l.due_date >= CURRENT_DATE AND l.status NOT IN ('settled','cancelled')
        THEN (l.due_date - CURRENT_DATE)
        ELSE NULL
    END AS days_until_due
FROM loans l
JOIN persons p ON l.person_id = p.id;
