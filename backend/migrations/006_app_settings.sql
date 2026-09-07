-- ═══════════════════════════════════════════════════════════════
--  Migration 006 — App Settings
--  Restores the missing settings table for the UI Theme toggle
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(50) PRIMARY KEY,
    value VARCHAR(255),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Insert the default light theme so the frontend has something to read immediately
INSERT INTO app_settings (key, value) VALUES ('theme', 'light') ON CONFLICT DO NOTHING;

GRANT SELECT, INSERT, UPDATE, DELETE ON app_settings TO loan_user;
