-- ═══════════════════════════════════════════════════════════════
--  Personal Loan Tracker — Full Database Schema
--  PostgreSQL 16
--  Tables: persons, loans, payments, interest_ledger,
--          attachments, alerts, audit_log
-- ═══════════════════════════════════════════════════════════════

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────────
--  ENUMS
-- ─────────────────────────────────────────────

CREATE TYPE loan_direction    AS ENUM ('lent', 'borrowed');
CREATE TYPE loan_status       AS ENUM ('active', 'partial', 'settled', 'overdue', 'cancelled');
CREATE TYPE interest_type     AS ENUM ('simple', 'compound');
CREATE TYPE interest_period   AS ENUM ('daily', 'weekly', 'monthly', 'yearly');
CREATE TYPE payment_method    AS ENUM ('cash', 'bank_transfer', 'mobile_payment', 'crypto', 'other');
CREATE TYPE alert_type        AS ENUM ('overdue', 'due_soon', 'partial_reminder');
CREATE TYPE attachment_parent AS ENUM ('loan', 'payment');
CREATE TYPE file_type         AS ENUM ('photo', 'pdf', 'screenshot', 'other');
CREATE TYPE relationship_tag  AS ENUM ('friend', 'family', 'colleague', 'acquaintance', 'other');

-- ─────────────────────────────────────────────
--  TABLE: persons
--  Everyone you lend to or borrow from
-- ─────────────────────────────────────────────

CREATE TABLE persons (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(200) NOT NULL,
    nickname        VARCHAR(100),
    phone           VARCHAR(50),
    email           VARCHAR(200),
    relationship    relationship_tag NOT NULL DEFAULT 'other',
    address         TEXT,
    national_id     VARCHAR(100),           -- ID card / passport number (optional)
    notes           TEXT,
    is_archived     BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_persons_full_name   ON persons (full_name);
CREATE INDEX idx_persons_archived    ON persons (is_archived);
CREATE INDEX idx_persons_relationship ON persons (relationship);

-- ─────────────────────────────────────────────
--  TABLE: loans
--  Core loan record — lent or borrowed
-- ─────────────────────────────────────────────

CREATE TABLE loans (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id       UUID         NOT NULL REFERENCES persons(id) ON DELETE RESTRICT,

    -- Direction & amount
    direction       loan_direction NOT NULL,
    principal       NUMERIC(15,2)  NOT NULL CHECK (principal > 0),
    currency        CHAR(3)        NOT NULL DEFAULT 'EUR',  -- ISO 4217

    -- Interest
    interest_rate   NUMERIC(8,4)   NOT NULL DEFAULT 0        CHECK (interest_rate >= 0),
    interest_type   interest_type  NOT NULL DEFAULT 'simple',
    interest_period interest_period NOT NULL DEFAULT 'monthly',

    -- Dates
    date_issued     DATE           NOT NULL DEFAULT CURRENT_DATE,
    due_date        DATE,                                    -- NULL = open-ended

    -- Status & metadata
    status          loan_status    NOT NULL DEFAULT 'active',
    purpose         VARCHAR(500),                            -- what the money was for
    notes           TEXT,

    -- Computed cache (updated by trigger)
    total_paid      NUMERIC(15,2)  NOT NULL DEFAULT 0        CHECK (total_paid >= 0),
    total_interest  NUMERIC(15,2)  NOT NULL DEFAULT 0        CHECK (total_interest >= 0),
    balance_due     NUMERIC(15,2)  NOT NULL DEFAULT 0,       -- principal + interest - paid

    created_at      TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_loans_person_id  ON loans (person_id);
CREATE INDEX idx_loans_status     ON loans (status);
CREATE INDEX idx_loans_direction  ON loans (direction);
CREATE INDEX idx_loans_due_date   ON loans (due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_loans_currency   ON loans (currency);

-- ─────────────────────────────────────────────
--  TABLE: payments
--  Every payment logged against a loan
-- ─────────────────────────────────────────────

CREATE TABLE payments (
    id              UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id         UUID          NOT NULL REFERENCES loans(id) ON DELETE CASCADE,

    amount          NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    payment_date    DATE          NOT NULL DEFAULT CURRENT_DATE,
    method          payment_method NOT NULL DEFAULT 'cash',
    reference       VARCHAR(200),                 -- transaction ID, cheque no., etc.
    notes           TEXT,

    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_loan_id      ON payments (loan_id);
CREATE INDEX idx_payments_payment_date ON payments (payment_date);

-- ─────────────────────────────────────────────
--  TABLE: interest_ledger
--  One row per interest calculation period
--  Written by the background worker daily/monthly
-- ─────────────────────────────────────────────

CREATE TABLE interest_ledger (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id             UUID          NOT NULL REFERENCES loans(id) ON DELETE CASCADE,

    period_start        DATE          NOT NULL,
    period_end          DATE          NOT NULL,
    opening_balance     NUMERIC(15,2) NOT NULL,   -- balance at start of period
    interest_accrued    NUMERIC(15,2) NOT NULL CHECK (interest_accrued >= 0),
    closing_balance     NUMERIC(15,2) NOT NULL,   -- opening + interest_accrued
    calc_type           interest_type NOT NULL,   -- simple or compound (snapshot)
    rate_applied        NUMERIC(8,4)  NOT NULL,   -- rate used (snapshot)

    calculated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    UNIQUE (loan_id, period_start)               -- one entry per loan per period
);

CREATE INDEX idx_interest_loan_id  ON interest_ledger (loan_id);
CREATE INDEX idx_interest_period   ON interest_ledger (period_start, period_end);

-- ─────────────────────────────────────────────
--  TABLE: attachments
--  Files attached to a loan or a payment
--  Polymorphic via parent_type + parent_id
-- ─────────────────────────────────────────────

CREATE TABLE attachments (
    id              UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id       UUID          NOT NULL,
    parent_type     attachment_parent NOT NULL,

    file_type       file_type     NOT NULL DEFAULT 'other',
    original_name   VARCHAR(500)  NOT NULL,
    file_path       TEXT          NOT NULL,       -- path inside /app/uploads volume
    mime_type       VARCHAR(100)  NOT NULL,
    file_size_kb    INTEGER       NOT NULL CHECK (file_size_kb > 0),
    notes           TEXT,

    uploaded_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_attachments_parent ON attachments (parent_id, parent_type);

-- ─────────────────────────────────────────────
--  TABLE: alerts
--  Alert events per loan, checked daily by worker
-- ─────────────────────────────────────────────

CREATE TABLE alerts (
    id              UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id         UUID       NOT NULL REFERENCES loans(id) ON DELETE CASCADE,

    alert_type      alert_type NOT NULL,
    trigger_date    DATE       NOT NULL,          -- date this alert fires
    message         TEXT       NOT NULL,

    is_sent         BOOLEAN    NOT NULL DEFAULT FALSE,
    is_dismissed    BOOLEAN    NOT NULL DEFAULT FALSE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at         TIMESTAMPTZ,
    dismissed_at    TIMESTAMPTZ,

    UNIQUE (loan_id, alert_type, trigger_date)    -- no duplicate alerts for same event
);

CREATE INDEX idx_alerts_loan_id      ON alerts (loan_id);
CREATE INDEX idx_alerts_unsent       ON alerts (is_sent, is_dismissed) WHERE NOT is_sent AND NOT is_dismissed;
CREATE INDEX idx_alerts_trigger_date ON alerts (trigger_date);

-- ─────────────────────────────────────────────
--  TABLE: audit_log
--  Immutable record of every change to a loan
-- ─────────────────────────────────────────────

CREATE TABLE audit_log (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id         UUID        NOT NULL REFERENCES loans(id) ON DELETE CASCADE,

    action          VARCHAR(50) NOT NULL,         -- 'created', 'updated', 'payment_added', etc.
    changed_field   VARCHAR(100),                 -- NULL for whole-record events
    old_value       TEXT,
    new_value       TEXT,
    description     TEXT,                         -- human-readable summary

    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_loan_id    ON audit_log (loan_id);
CREATE INDEX idx_audit_changed_at ON audit_log (changed_at DESC);

-- ─────────────────────────────────────────────
--  TRIGGER FUNCTION: updated_at auto-stamp
-- ─────────────────────────────────────────────

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_persons_updated_at
    BEFORE UPDATE ON persons
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_loans_updated_at
    BEFORE UPDATE ON loans
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─────────────────────────────────────────────
--  TRIGGER FUNCTION: recalculate loan totals
--  Fires after INSERT/UPDATE/DELETE on payments
--  Updates loans.total_paid and loans.balance_due
-- ─────────────────────────────────────────────

CREATE OR REPLACE FUNCTION recalculate_loan_totals()
RETURNS TRIGGER AS $$
DECLARE
    v_loan_id        UUID;
    v_principal      NUMERIC(15,2);
    v_total_paid     NUMERIC(15,2);
    v_total_interest NUMERIC(15,2);
    v_new_status     loan_status;
    v_due_date       DATE;
    v_current_status loan_status;
BEGIN
    -- Determine which loan to update
    IF TG_OP = 'DELETE' THEN
        v_loan_id := OLD.loan_id;
    ELSE
        v_loan_id := NEW.loan_id;
    END IF;

    -- Sum all payments for this loan
    SELECT COALESCE(SUM(amount), 0)
    INTO v_total_paid
    FROM payments
    WHERE loan_id = v_loan_id;

    -- Sum all accrued interest
    SELECT COALESCE(SUM(interest_accrued), 0)
    INTO v_total_interest
    FROM interest_ledger
    WHERE loan_id = v_loan_id;

    -- Get loan details
    SELECT principal, due_date, status
    INTO v_principal, v_due_date, v_current_status
    FROM loans
    WHERE id = v_loan_id;

    -- Do not auto-change cancelled loans
    IF v_current_status = 'cancelled' THEN
        RETURN COALESCE(NEW, OLD);
    END IF;

    -- Determine new status
    IF v_total_paid >= (v_principal + v_total_interest) THEN
        v_new_status := 'settled';
    ELSIF v_total_paid > 0 THEN
        IF v_due_date IS NOT NULL AND v_due_date < CURRENT_DATE THEN
            v_new_status := 'overdue';
        ELSE
            v_new_status := 'partial';
        END IF;
    ELSE
        IF v_due_date IS NOT NULL AND v_due_date < CURRENT_DATE THEN
            v_new_status := 'overdue';
        ELSE
            v_new_status := 'active';
        END IF;
    END IF;

    -- Update the loan row
    UPDATE loans
    SET
        total_paid     = v_total_paid,
        total_interest = v_total_interest,
        balance_due    = GREATEST(0, (v_principal + v_total_interest) - v_total_paid),
        status         = v_new_status
    WHERE id = v_loan_id;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_recalc_on_payment_insert
    AFTER INSERT ON payments
    FOR EACH ROW EXECUTE FUNCTION recalculate_loan_totals();

CREATE TRIGGER trg_recalc_on_payment_update
    AFTER UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION recalculate_loan_totals();

CREATE TRIGGER trg_recalc_on_payment_delete
    AFTER DELETE ON payments
    FOR EACH ROW EXECUTE FUNCTION recalculate_loan_totals();

-- ─────────────────────────────────────────────
--  TRIGGER FUNCTION: auto audit log on loan changes
-- ─────────────────────────────────────────────

CREATE OR REPLACE FUNCTION audit_loan_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (loan_id, action, description)
        VALUES (NEW.id, 'created', 'Loan created — ' || NEW.direction || ' ' || NEW.principal || ' ' || NEW.currency);

    ELSIF TG_OP = 'UPDATE' THEN
        -- Log status changes
        IF OLD.status IS DISTINCT FROM NEW.status THEN
            INSERT INTO audit_log (loan_id, action, changed_field, old_value, new_value)
            VALUES (NEW.id, 'updated', 'status', OLD.status::TEXT, NEW.status::TEXT);
        END IF;

        -- Log due date changes
        IF OLD.due_date IS DISTINCT FROM NEW.due_date THEN
            INSERT INTO audit_log (loan_id, action, changed_field, old_value, new_value)
            VALUES (NEW.id, 'updated', 'due_date', OLD.due_date::TEXT, NEW.due_date::TEXT);
        END IF;

        -- Log amount changes
        IF OLD.principal IS DISTINCT FROM NEW.principal THEN
            INSERT INTO audit_log (loan_id, action, changed_field, old_value, new_value)
            VALUES (NEW.id, 'updated', 'principal', OLD.principal::TEXT, NEW.principal::TEXT);
        END IF;

        -- Log interest rate changes
        IF OLD.interest_rate IS DISTINCT FROM NEW.interest_rate THEN
            INSERT INTO audit_log (loan_id, action, changed_field, old_value, new_value)
            VALUES (NEW.id, 'updated', 'interest_rate', OLD.interest_rate::TEXT, NEW.interest_rate::TEXT);
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_loans
    AFTER INSERT OR UPDATE ON loans
    FOR EACH ROW EXECUTE FUNCTION audit_loan_changes();

-- ─────────────────────────────────────────────
--  TRIGGER FUNCTION: audit log on payment events
-- ─────────────────────────────────────────────

CREATE OR REPLACE FUNCTION audit_payment_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (loan_id, action, description)
        VALUES (NEW.loan_id, 'payment_added',
            'Payment of ' || NEW.amount || ' recorded via ' || NEW.method || ' on ' || NEW.payment_date);
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (loan_id, action, description)
        VALUES (NEW.loan_id, 'payment_updated',
            'Payment updated: ' || OLD.amount || ' → ' || NEW.amount);
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (loan_id, action, description)
        VALUES (OLD.loan_id, 'payment_deleted',
            'Payment of ' || OLD.amount || ' on ' || OLD.payment_date || ' deleted');
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_payments
    AFTER INSERT OR UPDATE OR DELETE ON payments
    FOR EACH ROW EXECUTE FUNCTION audit_payment_changes();

-- ─────────────────────────────────────────────
--  VIEWS
-- ─────────────────────────────────────────────

-- Loan summary with person name and payment info
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
    l.total_paid,
    l.total_interest,
    l.balance_due,
    l.date_issued,
    l.due_date,
    l.purpose,
    p.id           AS person_id,
    p.full_name    AS person_name,
    p.nickname     AS person_nickname,
    p.phone        AS person_phone,
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

-- Dashboard summary
CREATE VIEW v_dashboard_summary AS
SELECT
    COUNT(*) FILTER (WHERE direction = 'lent'     AND status NOT IN ('settled','cancelled')) AS active_lent_count,
    COUNT(*) FILTER (WHERE direction = 'borrowed' AND status NOT IN ('settled','cancelled')) AS active_borrowed_count,
    COUNT(*) FILTER (WHERE status = 'overdue')                                               AS overdue_count,
    COUNT(*) FILTER (WHERE status = 'settled')                                               AS settled_count,
    COALESCE(SUM(balance_due) FILTER (WHERE direction = 'lent'     AND status NOT IN ('settled','cancelled')), 0) AS total_receivable,
    COALESCE(SUM(balance_due) FILTER (WHERE direction = 'borrowed' AND status NOT IN ('settled','cancelled')), 0) AS total_payable
FROM loans;

-- ─────────────────────────────────────────────
--  GRANT permissions (app user)
-- ─────────────────────────────────────────────

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO loan_user;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO loan_user;
