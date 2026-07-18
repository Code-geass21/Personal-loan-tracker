import json
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

NOW = datetime.utcnow().isoformat()

def ts(val):
    """Return timestamp or current time if null."""
    return val if val else NOW

@router.post("/from-json")
async def restore_from_json(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        contents = await file.read()
        data = json.loads(contents)
    except Exception as e:
        return JSONResponse({"status": "error", "error": f"Invalid JSON file: {e}"}, status_code=400)

    if "persons" not in data or "loans" not in data:
        return JSONResponse({"status": "error", "error": "Not a valid loan tracker backup file"}, status_code=400)

    results = {}

    try:
        # Clear existing data
        db.execute(text("DELETE FROM audit_log"))
        db.execute(text("DELETE FROM alerts"))
        db.execute(text("DELETE FROM interest_ledger"))
        db.execute(text("DELETE FROM targets"))
        db.execute(text("DELETE FROM attachments"))
        db.execute(text("DELETE FROM loan_fees")) # <-- ADD THIS LINE
        db.execute(text("DELETE FROM payments"))
        db.execute(text("DELETE FROM loans"))
        db.execute(text("DELETE FROM persons"))
        db.commit()

        # Restore persons
        person_count = 0
        for p in data.get("persons", []):
            db.execute(text("""
                INSERT INTO persons (id, full_name, nickname, phone, email, relationship,
                    address, national_id, notes, is_archived, created_at, updated_at)
                VALUES (:id, :full_name, :nickname, :phone, :email, :relationship,
                    :address, :national_id, :notes, :is_archived, :created_at, :updated_at)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id":           p.get("id"),
                "full_name":    p.get("full_name"),
                "nickname":     p.get("nickname"),
                "phone":        p.get("phone"),
                "email":        p.get("email"),
                "relationship": p.get("relationship", "other"),
                "address":      p.get("address"),
                "national_id":  p.get("national_id"),
                "notes":        p.get("notes"),
                "is_archived":  p.get("is_archived", False),
                "created_at":   ts(p.get("created_at")),
                "updated_at":   ts(p.get("updated_at")),
            })
            person_count += 1
        db.commit()
        results["persons"] = {"status": "ok", "count": person_count}

        # Restore loans
        loan_count = 0
        for l in data.get("loans", []):
            db.execute(text("""
                INSERT INTO loans (id, person_id, direction, principal, currency,
                    interest_rate, interest_type, interest_period,
                    institution_type, emi_start_date, tenure_months, emi_amount, day_count_method,
                    date_issued, due_date, status, purpose, notes,
                    total_paid, total_interest, balance_due, created_at, updated_at)
                VALUES (:id, :person_id, :direction, :principal, :currency,
                    :interest_rate, :interest_type, :interest_period,
                    :institution_type, :emi_start_date, :tenure_months, :emi_amount, :day_count_method,
                    :date_issued, :due_date, :status, :purpose, :notes,
                    :total_paid, :total_interest, :balance_due, :created_at, :updated_at)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id":               l.get("id"),
                "person_id":        l.get("person_id"),
                "direction":        l.get("direction"),
                "principal":        l.get("principal"),
                "currency":         l.get("currency", "INR"),
                "interest_rate":    l.get("interest_rate", 0),
                "interest_type":    l.get("interest_type", "simple"),
                "interest_period":  l.get("interest_period", "monthly"),
                "institution_type": l.get("institution_type", "non_institutional"),
                "emi_start_date":   l.get("emi_start_date"),
                "tenure_months":    l.get("tenure_months"),
                "emi_amount":       l.get("emi_amount"),
                "day_count_method": l.get("day_count_method", "actual_365"),
                "date_issued":      l.get("date_issued"),
                "due_date":         l.get("due_date"),
                "status":           l.get("status", "active"),
                "purpose":          l.get("purpose"),
                "notes":            l.get("notes"),
                "total_paid":       l.get("total_paid", 0),
                "total_interest":   l.get("total_interest", 0),
                "balance_due":      l.get("balance_due", 0),
                "created_at":       ts(l.get("created_at")),
                "updated_at":       ts(l.get("updated_at")),
            })
            loan_count += 1
        db.commit()
        results["loans"] = {"status": "ok", "count": loan_count}

        # Restore payments
        payment_count = 0
        for p in data.get("payments", []):
            db.execute(text("""
                INSERT INTO payments (id, loan_id, amount, payment_date, method,
                    reference, notes, created_at, updated_at)
                VALUES (:id, :loan_id, :amount, :payment_date, :method,
                    :reference, :notes, :created_at, :updated_at)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id":           p.get("id"),
                "loan_id":      p.get("loan_id"),
                "amount":       p.get("amount"),
                "payment_date": p.get("payment_date"),
                "method":       p.get("method", "cash"),
                "reference":    p.get("reference"),
                "notes":        p.get("notes"),
                "created_at":   ts(p.get("created_at")),
                "updated_at":   ts(p.get("updated_at")),
            })
            payment_count += 1
        db.commit()
        results["payments"] = {"status": "ok", "count": payment_count}

        # Restore loan_fees
        fee_count = 0
        for f in data.get("loan_fees", []):
            db.execute(text("""
                INSERT INTO loan_fees (id, loan_id, fee_name, amount, tax_rate, tax_amount, status, created_at, updated_at)
                VALUES (:id, :loan_id, :fee_name, :amount, :tax_rate, :tax_amount, :status, :created_at, :updated_at)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id":         f.get("id"),
                "loan_id":    f.get("loan_id"),
                "fee_name":   f.get("fee_name"),
                "amount":     f.get("amount"),
                "tax_rate":   f.get("tax_rate", 0),
                "tax_amount": f.get("tax_amount", 0),
                "status":     f.get("status", "pending"),
                "created_at": ts(f.get("created_at")),
                "updated_at": ts(f.get("updated_at")),
            })
            fee_count += 1
        db.commit()
        results["loan_fees"] = {"status": "ok", "count": fee_count}

        # Restore attachments
        attach_count = 0
        for a in data.get("attachments", []):
            db.execute(text("""
                INSERT INTO attachments (id, parent_id, parent_type, file_type, original_name, file_path, mime_type, file_size_kb, notes, uploaded_at)
                VALUES (:id, :parent_id, :parent_type, :file_type, :original_name, :file_path, :mime_type, :file_size_kb, :notes, :uploaded_at)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id":            a.get("id"),
                "parent_id":     a.get("parent_id"),
                "parent_type":   a.get("parent_type", "loan"),
                "file_type":     a.get("file_type", "other"),
                "original_name": a.get("original_name"),
                "file_path":     a.get("file_path"),
                "mime_type":     a.get("mime_type", "application/pdf"),
                "file_size_kb":  a.get("file_size_kb") if a.get("file_size_kb") else 1, # Prevents > 0 constraint crash
                "notes":         a.get("notes"),
                "uploaded_at":   ts(a.get("uploaded_at")),
            })
            attach_count += 1
        db.commit()
        results["attachments"] = {"status": "ok", "count": attach_count}

        # Restore targets
        target_count = 0
        for t in data.get("targets", []):
            db.execute(text("""
                INSERT INTO targets (id, scope, loan_id, monthly_amount, currency,
                    notes, is_active, created_at, updated_at)
                VALUES (:id, :scope, :loan_id, :monthly_amount, :currency,
                    :notes, :is_active, :created_at, :updated_at)
                ON CONFLICT (id) DO NOTHING
            """), {
                "id":             t.get("id"),
                "scope":          t.get("scope"),
                "loan_id":        t.get("loan_id"),
                "monthly_amount": t.get("monthly_amount"),
                "currency":       t.get("currency", "INR"),
                "notes":          t.get("notes"),
                "is_active":      t.get("is_active", True),
                "created_at":     ts(t.get("created_at")),
                "updated_at":     ts(t.get("updated_at")),
            })
            target_count += 1
        db.commit()
        results["targets"] = {"status": "ok", "count": target_count}

        return JSONResponse({
            "status":      "ok",
            "exported_at": data.get("exported_at", "unknown"),
            "results":     results,
            "summary": {
                "persons":  person_count,
                "loans":    loan_count,
                "payments": payment_count,
                "targets":  target_count,
            }
        })

    except Exception as e:
        db.rollback()
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@router.get("/backups")
def list_backups():
    import os
    from app.config import settings
    backup_root = settings.BACKUP_DIR
    if not os.path.exists(backup_root):
        return []
    backups = []
    for name in sorted(os.listdir(backup_root), reverse=True):
        full = os.path.join(backup_root, name)
        if os.path.isdir(full) and name.startswith("backup_"):
            files = []
            size = 0
            for dp, _, fs in os.walk(full):
                for f in fs:
                    fp = os.path.join(dp, f)
                    sz = os.path.getsize(fp)
                    size += sz
                    files.append({"name": f, "size_kb": round(sz/1024, 1)})
            backups.append({
                "name":    name,
                "created": name.replace("backup_", ""),
                "size_kb": round(size/1024, 1),
                "files":   files,
                "path":    full
            })
    return backups
