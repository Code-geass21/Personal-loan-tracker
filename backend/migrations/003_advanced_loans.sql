-- ═══════════════════════════════════════════════════════════════
-- Migration 003 — Advanced Loan Features
-- Adds support for EMI, Pro-Rata, Fees, and Payment Splitting
-- ═══════════════════════════════════════════════════════════════

-- 1. New ENUMS for advanced tracking
CREATE TYPE amortization_type AS ENUM ('simple', 'emi', 'pro_rata');
CREATE TYPE fee_status AS ENUM ('pending', 'paid', 'waived');

-- 2. Update Loans Table
ALTER TABLE loans
ADD COLUMN amortization_type amortization_type NOT NULL DEFAULT 'simple',
ADD COLUMN term_months INTEGER;

-- 3. Update Payments Table
ALTER TABLE payments
ADD COLUMN principal_component NUMERIC(15,2) NOT NULL DEFAULT 0,
ADD COLUMN interest_component NUMERIC(15,2) NOT NULL DEFAULT 0;

-- 4. Create Loan Fees Table
CREATE TABLE loan_fees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id UUID NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
    fee_name VARCHAR(100) NOT NULL,
    amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    status fee_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_loan_fees_loan_id ON loan_fees (loan_id);

CREATE TRIGGER trg_loan_fees_updated_at
BEFORE UPDATE ON loan_fees
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

GRANT SELECT, INSERT, UPDATE, DELETE ON loan_fees TO loan_user;

-- 5. Update Views to prevent breakage
DROP VIEW IF EXISTS v_loan_summary CASCADE;

CREATE VIEW v_loan_summary AS
SELECT
    l.id,
    l.direction,
    l.status,
    l.currency,
    l.principal,
    l.interest_rate,
    l.interest_type,
    l.interest_period,
    l.amortization_type,
    l.term_months,
    l.total_paid,
    l.total_interest,
    l.balance_due,
    l.date_issued,
    l.due_date,
    l.purpose,
    p.id AS person_id,
    p.full_name AS person_name,
    p.nickname AS person_nickname,
    p.phone AS person_phone,
    p.relationship AS person_relationship,
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
