#!/bin/bash
# ─────────────────────────────────────────────
#  Shadow-Debt — Backup Script
#  Run: bash scripts/backup.sh
# ─────────────────────────────────────────────

# Updated to use the relative path matching our new portable setup
BACKUP_DIR=./backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting backup at $DATE..."

# 1. Database dump
echo "📦 Backing up database..."
docker exec shadow_debt_db pg_dump \
  -U shadow_user shadow_debt \
  > "$BACKUP_DIR/db_$DATE.sql"

# 2. Uploads volume (Fixed to tar the local bind mount directory directly)
echo "📁 Backing up uploads..."
tar czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C ./backend/uploads . 2>/dev/null || echo "No uploads found to backup."

# 3. JSON export via API
echo "📊 Exporting data as JSON..."
curl -s -X POST http://localhost:54317/api/backup/run \
  > "$BACKUP_DIR/data_$DATE.json"

echo ""
echo "✅ Backup complete! Files saved to $BACKUP_DIR:"
ls -lh "$BACKUP_DIR" | grep "$DATE"
echo ""
echo "To restore database:"
echo "  docker exec -i shadow_debt_db psql -U shadow_user shadow_debt < $BACKUP_DIR/db_$DATE.sql"
