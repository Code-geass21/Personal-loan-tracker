#!/bin/bash
# ─────────────────────────────────────────────
#  Personal Loan Tracker — Backup Script
#  Run: bash scripts/backup.sh
# ─────────────────────────────────────────────

BACKUP_DIR=~/docker/loan-tracker/backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting backup at $DATE..."

# 1. Database dump
echo "📦 Backing up database..."
docker exec loan_tracker_db pg_dump \
  -U loan_user loan_tracker \
  > "$BACKUP_DIR/db_$DATE.sql"

# 2. Uploads volume
echo "📁 Backing up uploads..."
docker run --rm \
  -v loan_tracker_uploads:/data \
  -v "$BACKUP_DIR":/backup \
  alpine tar czf /backup/uploads_$DATE.tar.gz -C /data . 2>/dev/null

# 3. JSON export via API
echo "📊 Exporting data as JSON..."
curl -s http://localhost:8001/export/full-backup \
  > "$BACKUP_DIR/data_$DATE.json"

echo ""
echo "✅ Backup complete! Files saved to $BACKUP_DIR:"
ls -lh "$BACKUP_DIR" | grep "$DATE"
echo ""
echo "To restore database:"
echo "  docker exec -i loan_tracker_db psql -U loan_user loan_tracker < $BACKUP_DIR/db_$DATE.sql"
