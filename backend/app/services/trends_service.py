from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from dateutil.relativedelta import relativedelta

def get_lending_trends(db: Session, months: int = 18) -> list:
    """
    Returns monthly cumulative totals of lent vs borrowed principal
    for the last N months, based on date_issued.
    """
    today = date.today()
    start_month = (today.replace(day=1) - relativedelta(months=months - 1))

    rows = db.execute(text("""
        SELECT
            date_trunc('month', date_issued)::date AS month,
            direction,
            SUM(principal) AS total
        FROM loans
        WHERE date_issued >= :start_month
        GROUP BY 1, 2
        ORDER BY 1
    """), {"start_month": start_month}).mappings().all()

    # Build a map: month -> {lent: x, borrowed: y}
    monthly = {}
    cursor = start_month
    for _ in range(months):
        key = cursor.strftime("%Y-%m")
        monthly[key] = {"month": cursor.strftime("%b %Y"), "lent": 0, "borrowed": 0}
        cursor = cursor + relativedelta(months=1)

    for r in rows:
        key = r["month"].strftime("%Y-%m")
        if key in monthly:
            monthly[key][r["direction"]] = float(r["total"])

    # Convert to cumulative totals
    result = []
    cum_lent = 0
    cum_borrowed = 0
    for key in sorted(monthly.keys()):
        m = monthly[key]
        cum_lent     += m["lent"]
        cum_borrowed += m["borrowed"]
        result.append({
            "month":            m["month"],
            "lent":             m["lent"],
            "borrowed":         m["borrowed"],
            "cumulative_lent":     round(cum_lent, 2),
            "cumulative_borrowed": round(cum_borrowed, 2),
        })

    return result
