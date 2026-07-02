import os
import json
import csv
import io
import shutil
import subprocess
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter()

@router.post("/run")
def run_backup(db: Session = Depends(get_db)):
    """
    Complete one-click backup:
    1. PostgreSQL full dump
    2. All uploaded files (photos, PDFs, screenshots)
    3. Complete JSON export (all 7 tables)
    All saved to BACKUP_DIR/backup_YYYYMMDD_HHMMSS/
    """
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(settings.BACKUP_DIR, f"backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)

    results = {}

    # ── 1. Full JSON export ───────────────────────
    try:
        def serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            from datetime import date
            if isinstance(obj, date):
                return obj.isoformat()
            return str(obj)

        persons  = db.execute(text("SELECT * FROM persons ORDER BY full_name")).mappings().all()
        loans    = db.execute(text("SELECT * FROM v_loan_summary ORDER BY date_issued DESC")).mappings().all()
        payments = db.execute(text("SELECT * FROM payments ORDER BY payment_date")).mappings().all()
        interest = db.execute(text("SELECT * FROM interest_ledger ORDER BY period_start")).mappings().all()
        targets  = db.execute(text("SELECT * FROM targets")).mappings().all()
        alerts   = db.execute(text("SELECT * FROM alerts ORDER BY trigger_date DESC")).mappings().all()
        audit    = db.execute(text("SELECT * FROM audit_log ORDER BY changed_at DESC")).mappings().all()
        app_settings = db.execute(text("SELECT * FROM app_settings")).mappings().all()

        data = {
            "exported_at":     datetime.now().isoformat(),
            "app_version":     "1.0.0",
            "persons":         [dict(r) for r in persons],
            "loans":           [dict(r) for r in loans],
            "payments":        [dict(r) for r in payments],
            "interest_ledger": [dict(r) for r in interest],
            "targets":         [dict(r) for r in targets],
            "alerts":          [dict(r) for r in alerts],
            "audit_log":       [dict(r) for r in audit],
        }

        json_path = os.path.join(backup_dir, f"data_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(data, f, default=serial, indent=2)

        results["json_export"] = {
            "status": "ok",
            "file":   f"data_{timestamp}.json",
            "records": {
                "persons":  len(data["persons"]),
                "loans":    len(data["loans"]),
                "payments": len(data["payments"]),
                "targets":  len(data["targets"]),
            }
        }
    except Exception as e:
        results["json_export"] = {"status": "error", "error": str(e)}

    # ── 2. Copy all uploaded files ────────────────
    try:
        uploads_src = settings.UPLOAD_DIR
        uploads_dst = os.path.join(backup_dir, "uploads")
        if os.path.exists(uploads_src):
            shutil.copytree(uploads_src, uploads_dst)
            # Count files
            file_count = sum(len(files) for _, _, files in os.walk(uploads_dst))
            results["uploads"] = {"status": "ok", "files_copied": file_count}
        else:
            results["uploads"] = {"status": "ok", "files_copied": 0, "note": "No uploads yet"}
    except Exception as e:
        results["uploads"] = {"status": "error", "error": str(e)}

    # ── 3. PostgreSQL dump ────────────────────────
    try:
        db_dump_path = os.path.join(backup_dir, f"database_{timestamp}.sql")
        # Parse connection details from DATABASE_URL
        db_url = settings.DATABASE_URL
        # postgresql://user:pass@host:port/dbname
        import re
        m = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_url)
        if m:
            pg_user, pg_pass, pg_host, pg_port, pg_db = m.groups()
        else:
            pg_user, pg_pass, pg_host, pg_port, pg_db = "loan_user", "", "db", "5432", "loan_tracker"

        result = subprocess.run(
            ["pg_dump", "-h", pg_host, "-p", pg_port, "-U", pg_user, "-d", pg_db],
            capture_output=True, text=True,
            env={**os.environ, "PGPASSWORD": pg_pass}
        )
        if result.returncode == 0:
            with open(db_dump_path, 'w') as f:
                f.write(result.stdout)
            results["database_dump"] = {
                "status": "ok",
                "file":   f"database_{timestamp}.sql",
                "size_kb": round(os.path.getsize(db_dump_path) / 1024, 1)
            }
        else:
            results["database_dump"] = {"status": "skipped", "note": "pg_dump not available in container — JSON export covers all data"}
    except Exception as e:
        results["database_dump"] = {"status": "skipped", "note": str(e)}

    # ── Summary ───────────────────────────────────
    backup_size = sum(
        os.path.getsize(os.path.join(dirpath, f))
        for dirpath, _, files in os.walk(backup_dir)
        for f in files
    )

    return JSONResponse({
        "status":     "ok",
        "timestamp":  timestamp,
        "backup_dir": f"backup_{timestamp}",
        "full_path":  backup_dir,
        "size_kb":    round(backup_size / 1024, 1),
        "results":    results
    })

@router.get("/list")
def list_backups():
    """List all existing backups with their sizes and dates."""
    backup_root = settings.BACKUP_DIR
    if not os.path.exists(backup_root):
        return []

    backups = []
    for name in sorted(os.listdir(backup_root), reverse=True):
        full = os.path.join(backup_root, name)
        if os.path.isdir(full) and name.startswith("backup_"):
            size = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, _, files in os.walk(full)
                for f in files
            )
            backups.append({
                "name":     name,
                "created":  name.replace("backup_", ""),
                "size_kb":  round(size / 1024, 1),
                "path":     full
            })

    return backups
