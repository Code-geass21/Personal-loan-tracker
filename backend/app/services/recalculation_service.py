from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date
from app.utils.finance import calculate_pro_rata_interest, calculate_tax

def recalculate_loan_state(db: Session, loan_id: str):
    # 1. Fetch Loan Details
    loan = db.execute(text("SELECT * FROM loans WHERE id = :id"), {"id": str(loan_id)}).mappings().first()
    if not loan:
        return

    # 2. Fetch all Payments
    payments = db.execute(text(
        "SELECT * FROM payments WHERE loan_id = :id ORDER BY payment_date ASC, created_at ASC"
    ), {"id": str(loan_id)}).mappings().all()

    # 3. Fetch all Active Fees
    fees = db.execute(text(
        "SELECT * FROM loan_fees WHERE loan_id = :id AND status != 'waived'"
    ), {"id": str(loan_id)}).mappings().all()

    principal_balance = Decimal(str(loan["principal"]))
    entered_rate = Decimal(str(loan["interest_rate"]))
    interest_period = loan["interest_period"]
    amortization_type = loan.get("amortization_type", "simple") if "amortization_type" in loan else "simple"

    total_interest_accrued = Decimal('0')
    total_paid = Decimal('0')
    unpaid_interest = Decimal('0')

    # Tally Upfront Fees + Tax (GST)
    unpaid_fees = Decimal('0')
    for f in fees:
        fee_amt = Decimal(str(f["amount"]))
        fee_tax_rate = Decimal(str(f.get("tax_rate", 0) if f.get("tax_rate") is not None else 0))
        fee_tax = calculate_tax(fee_amt, fee_tax_rate)
        unpaid_fees += (fee_amt + fee_tax)

    last_event_date = loan["date_issued"]

    if amortization_type in ('simple', 'compound', 'pro_rata'):
        for payment in payments:
            pay_date = payment["payment_date"]
            cash_paid = Decimal(str(payment["amount"]))

            # Step A: Accrue interest to this date
            days_elapsed = max(0, (pay_date - last_event_date).days)
            new_interest = calculate_pro_rata_interest(principal_balance, entered_rate, days_elapsed, interest_period)

            unpaid_interest += new_interest
            total_interest_accrued += new_interest

            is_manual = payment.get("is_manual", False)

            if is_manual:
                # <--- BANK MODE (Manual Overrides) --->
                manual_prin = Decimal(str(payment.get("principal_component") or 0))
                manual_int  = Decimal(str(payment.get("interest_component") or 0))

                principal_balance -= manual_prin
                unpaid_interest -= manual_int
                if unpaid_interest < 0:
                    unpaid_interest = Decimal('0')

                total_paid += cash_paid
            else:
                # <--- FRIEND MODE (Automatic Waterfall) --->
                cash_left = cash_paid
                pay_tax_rate = Decimal(str(payment.get("tax_rate", 0) if payment.get("tax_rate") is not None else 0))

                # 0. Pay off fees
                if cash_left >= unpaid_fees:
                    cash_left -= unpaid_fees
                    unpaid_fees = Decimal('0')
                else:
                    unpaid_fees -= cash_left
                    cash_left = Decimal('0')

                # 1. Pay off interest
                interest_cleared = Decimal('0')
                if cash_left >= unpaid_interest:
                    interest_cleared = unpaid_interest
                    cash_left -= unpaid_interest
                    unpaid_interest = Decimal('0')
                else:
                    interest_cleared = cash_left
                    unpaid_interest -= cash_left
                    cash_left = Decimal('0')

                db.execute(text("UPDATE payments SET interest_component = :int_comp WHERE id = :pid"),
                            {"int_comp": float(interest_cleared), "pid": str(payment["id"])})

                # <--- THE MAGIC FIX: Tax ONLY on the interest cleared! --->
                tax_credit = interest_cleared * (pay_tax_rate / Decimal('100'))

                # The tax credit acts as extra cash going towards the principal
                cash_left += tax_credit
                total_paid += (cash_paid + tax_credit)

                # 2. Pay off principal
                if cash_left > 0:
                    principal_balance -= cash_left
                    db.execute(text("UPDATE payments SET principal_component = :prin_comp WHERE id = :pid"),
                                {"prin_comp": float(cash_left), "pid": str(payment["id"])})

            last_event_date = pay_date

    # Step C: Accrue final interest to TODAY
    days_to_today = max(0, (date.today() - last_event_date).days)
    final_interest = calculate_pro_rata_interest(principal_balance, entered_rate, days_to_today, interest_period)
    unpaid_interest += final_interest
    total_interest_accrued += final_interest

    balance_due = principal_balance + unpaid_interest + unpaid_fees

    new_status = 'active'
    if balance_due <= 0:
        new_status = 'settled'
        balance_due = Decimal('0')
    elif total_paid > 0:
        new_status = 'partial'

    if loan["status"] in ('cancelled',):
        new_status = loan["status"]

    db.execute(text("""
        UPDATE loans
        SET total_paid = :paid,
            total_interest = :interest,
            balance_due = :balance,
            status = :status,
            updated_at = NOW()
        WHERE id = :id
    """), {
        "paid": float(total_paid),
        "interest": float(total_interest_accrued),
        "balance": float(balance_due),
        "status": new_status,
        "id": str(loan_id)
    })
    db.commit()
