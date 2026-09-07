-- ═══════════════════════════════════════════════════════════════
--  Migration 002 — Payment Targets
--  Adds support for global and per-loan monthly payment targets
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE targets (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    scope           VARCHAR(50)  NOT NULL,  -- Reverted to VARCHAR to match legacy data
    loan_id         UUID         REFERENCES loans(id) ON DELETE CASCADE,
    monthly_amount  NUMERIC(15,2) NOT NULL CHECK (monthly_amount >= 0),
    currency        CHAR(3)      NOT NULL DEFAULT 'INR',
    notes           TEXT,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_target_scope CHECK (
        (scope = 'loan' AND loan_id IS NOT NULL) OR
        (scope = 'global' AND loan_id IS NULL)
    )
);

CREATE UNIQUE INDEX uq_target_global_active
    ON targets (scope) WHERE scope = 'global' AND is_active = TRUE;

CREATE UNIQUE INDEX uq_target_loan_active
    ON targets (loan_id) WHERE scope = 'loan' AND is_active = TRUE;

CREATE TRIGGER trg_targets_updated_at
    BEFORE UPDATE ON targets
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

GRANT SELECT, INSERT, UPDATE, DELETE ON targets TO loan_user;
