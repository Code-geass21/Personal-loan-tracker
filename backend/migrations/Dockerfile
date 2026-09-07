FROM postgres:16-alpine

# Bake the migration scripts directly into the database image.
# Postgres automatically runs anything in this directory in alphabetical order.
COPY init.sql /docker-entrypoint-initdb.d/01_init.sql
COPY 002_targets.sql /docker-entrypoint-initdb.d/02_targets.sql
COPY 003_advanced_loans.sql /docker-entrypoint-initdb.d/03_advanced_loans.sql
COPY 004_schema_sync.sql /docker-entrypoint-initdb.d/04_schema_sync.sql
COPY 006_app_settings.sql /docker-entrypoint-initdb.d/05_app_settings.sql
COPY seed.sql /docker-entrypoint-initdb.d/99_seed.sql
