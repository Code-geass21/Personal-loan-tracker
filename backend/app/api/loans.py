from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.loan import LoanCreate, LoanUpdate, LoanResponse, LoanSummary
from app.schemas.payment import PaymentResponse
from app.schemas.alert import AlertResponse
from app.schemas.attachment import AttachmentResponse
from app.services import loan_service
from app.services.interest_service import accrue_interest, recalculate_loan
from app.services import attachment_service, payment_service
from app.models.attachment import AttachmentParent
from app.models.alert import Alert
from fastapi.responses import StreamingResponse
import io
import openpyxl
from fpdf import FPDF

router = APIRouter()

@router.get("/", response_model=List[dict])
def list_loans(
    direction:  Optional[str]  = Query(None),
    status:     Optional[str]  = Query(None),
    person_id:  Optional[UUID] = Query(None),
    currency:   Optional[str]  = Query(None),
    db: Session = Depends(get_db)
):
    return loan_service.get_all(db, direction, status, person_id, currency)

@router.get("/overdue", response_model=List[dict])
def list_overdue(db: Session = Depends(get_db)):
    return loan_service.get_overdue(db)

@router.get("/due-soon", response_model=List[dict])
def list_due_soon(
    days: int = Query(7),
    db: Session = Depends(get_db)
):
    return loan_service.get_due_soon(db, days)

@router.get("/{loan_id}", response_model=dict)
def get_loan(loan_id: UUID, db: Session = Depends(get_db)):
    result = loan_service.get_summary_by_id(db, loan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Loan not found")
    return result

@router.post("/", response_model=LoanResponse, status_code=201)
def create_loan(data: LoanCreate, db: Session = Depends(get_db)):
    loan = loan_service.create(db, data)
    # loan_service automatically runs the new math engine, so we just return!
    return loan_service.get_summary_by_id(db, loan.id) or loan

@router.patch("/{loan_id}", response_model=LoanResponse)
def update_loan(loan_id: UUID, data: LoanUpdate, db: Session = Depends(get_db)):
    result = loan_service.update(db, loan_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Loan not found")

    # --- THE FIX: Save the calculated diff into the Audit Log ---
    diff_text = getattr(result, "_audit_diff", None)
    if diff_text:
        from app.models.audit_log import AuditLog

        audit_entry = AuditLog(
            loan_id=loan_id,
            action="Updated Details",
            description=diff_text
        )
        db.add(audit_entry)
        db.commit()
    # ------------------------------------------------------------

    return result

@router.delete("/{loan_id}", status_code=204)
def delete_loan(loan_id: UUID, db: Session = Depends(get_db)):
    success = loan_service.delete(db, loan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Loan not found")

@router.post("/{loan_id}/cancel", response_model=LoanResponse)
def cancel_loan(loan_id: UUID, db: Session = Depends(get_db)):
    result = loan_service.cancel(db, loan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Loan not found")

    # --- THE FIX: Save the cancellation to the Audit Log ---
    from app.models.audit_log import AuditLog
    audit_entry = AuditLog(
        loan_id=loan_id,
        action="Cancelled",
        description="Loan was manually cancelled. Remaining balance wiped to $0."
    )
    db.add(audit_entry)
    db.commit()
    # -------------------------------------------------------

    return result

@router.get("/{loan_id}/payments", response_model=List[PaymentResponse])
def get_loan_payments(loan_id: UUID, db: Session = Depends(get_db)):
    return payment_service.get_by_loan(db, loan_id)

@router.get("/{loan_id}/attachments", response_model=List[AttachmentResponse])
def get_loan_attachments(loan_id: UUID, db: Session = Depends(get_db)):
    return attachment_service.get_by_parent(db, loan_id, AttachmentParent.loan)

@router.get("/{loan_id}/alerts", response_model=List[AlertResponse])
def get_loan_alerts(loan_id: UUID, db: Session = Depends(get_db)):
    loan = loan_service.get_by_id(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return db.query(Alert).filter(
        Alert.loan_id == loan_id,
        Alert.is_dismissed == False
    ).order_by(Alert.trigger_date.desc()).all()

@router.get("/{loan_id}/interest", response_model=List[dict])
def get_loan_interest(loan_id: UUID, db: Session = Depends(get_db)):
    from sqlalchemy import text
    rows = db.execute(text(
        "SELECT period_start, period_end, opening_balance, "
        "interest_accrued, closing_balance, calc_type, rate_applied "
        "FROM interest_ledger WHERE loan_id = :loan_id ORDER BY period_start"
    ), {"loan_id": str(loan_id)}).mappings().all()
    return [
        {
            "period_start":     str(e["period_start"]),
            "period_end":       str(e["period_end"]),
            "opening_balance":  float(e["opening_balance"]),
            "interest_accrued": float(e["interest_accrued"]),
            "closing_balance":  float(e["closing_balance"]),
            "calc_type":        str(e["calc_type"]),
            "rate_applied":     float(e["rate_applied"]),
        }
        for e in rows
    ]

@router.get("/{loan_id}/audit", response_model=List[dict])
def get_loan_audit(loan_id: UUID, db: Session = Depends(get_db)):
    from app.models.audit_log import AuditLog
    logs = db.query(AuditLog).filter(
        AuditLog.loan_id == loan_id
    ).order_by(AuditLog.changed_at.desc()).all()

    clean_logs = []
    for l in logs:
        # THE FIX: Skip the automatic database ghost rows that have no details!
        if (l.action == 'updated' or l.action == 'Updated') and not l.description:
            continue

        clean_logs.append({
            "action":        l.action,
            "changed_field": l.changed_field,
            "old_value":     l.old_value,
            "new_value":     l.new_value,
            "description":   l.description,
            "changed_at":    l.changed_at,
        })

    return clean_logs

@router.get("/{loan_id}/statement/download")
def download_statement(loan_id: UUID, format: str = "txt", db: Session = Depends(get_db)):
    # 1. Fetch Loan & Payments
    loan = loan_service.get_by_id(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    payments = payment_service.get_by_loan(db, loan_id)

    # 2. THE FIX: Log the export directly to the Audit Log!
    from app.models.audit_log import AuditLog
    audit_entry = AuditLog(
        loan_id=loan_id,
        action="Statement Exported",
        description=f"User downloaded the loan statement in {format.upper()} format."
    )
    db.add(audit_entry)
    db.commit()

    # 3. Prepare the Data Rows
    headers = ["Date", "Description", "Amount", "Principal Paid", "Interest Paid"]
    rows = []
    for p in payments:
        rows.append([
            str(p.payment_date),
            "Payment Received",
            f"${p.amount:.2f}",
            f"${p.principal_component or 0:.2f}",
            f"${p.interest_component or 0:.2f}"
        ])

    # 4. Generate the requested file type
    if format == "xlsx":
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Loan Statement"
        ws.append(headers)
        for r in rows:
            ws.append(r)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=loan_statement.xlsx"}
        )

    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Loan Statement", ln=True, align='C')
        pdf.ln(10)

        # Draw Table Headers
        pdf.set_font("Arial", 'B', 10)
        col_widths = [30, 45, 30, 40, 40]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, str(header), border=1)
        pdf.ln()

        # Draw Table Rows
        pdf.set_font("Arial", '', 10)
        for r in rows:
            for i, item in enumerate(r):
                pdf.cell(col_widths[i], 10, str(item), border=1)
            pdf.ln()

        pdf_bytes = pdf.output(dest='S')
        stream = io.BytesIO(pdf_bytes)
        return StreamingResponse(
            stream,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=loan_statement.pdf"}
        )

    else: # Default TXT
        stream = io.StringIO()
        stream.write("LOAN STATEMENT\n")
        stream.write("-" * 65 + "\n")
        stream.write(f"{' | '.join(headers)}\n")
        stream.write("-" * 65 + "\n")
        for r in rows:
            stream.write(f"{' | '.join(r)}\n")

        byte_stream = io.BytesIO(stream.getvalue().encode('utf-8'))
        return StreamingResponse(
            byte_stream,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=loan_statement.txt"}
        )
