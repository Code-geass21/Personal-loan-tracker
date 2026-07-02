from decimal import Decimal, ROUND_HALF_UP
from datetime import date

def smart_annualize_rate(entered_rate: Decimal, period: str) -> Decimal:
    """
    Intelligently converts UI rate inputs into true Annual Rates.
    Fixes the classic '12% per month vs 12% per year' confusion.
    """
    rate = Decimal(str(entered_rate))
    period = period.lower() if period else 'yearly'

    if period == 'monthly':
        # In informal lending: Entering '2' + Monthly means 2% per month (24% Annual)
        # Entering '12' + Monthly usually means 12% Annual (1% per month)
        if rate < Decimal('10'):
            return rate * Decimal('12')
        else:
            return rate # Treat >= 10 as an annual rate already
    elif period == 'daily':
        return rate * Decimal('365')
    elif period == 'weekly':
        return rate * Decimal('52')

    return rate # Fallback for 'yearly'

def calculate_emi(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    """Calculates the fixed Equated Monthly Installment (EMI)."""
    if annual_rate == 0 or months <= 0:
        return (principal / Decimal(max(1, months))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    monthly_rate = (annual_rate / Decimal('100')) / Decimal('12')
    compound_factor = (Decimal('1') + monthly_rate) ** months
    emi = principal * monthly_rate * compound_factor / (compound_factor - Decimal('1'))

    return emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_days_between(start_date: date, end_date: date) -> int:
    """Returns the exact number of days between two dates."""
    return max(0, (end_date - start_date).days)

def calculate_pro_rata_interest(principal: Decimal, entered_rate: Decimal, days: int, period: str = 'yearly') -> Decimal:
    """Calculates exact daily interest using Smart Annualization (Actual/365 method)."""
    if entered_rate == 0 or days == 0 or principal <= 0:
        return Decimal('0.00')

    annual_rate = smart_annualize_rate(entered_rate, period)
    daily_rate = (annual_rate / Decimal('100')) / Decimal('365')
    interest = principal * daily_rate * Decimal(str(days))

    return interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_tax(base_amount: Decimal, tax_rate: Decimal) -> Decimal:
    """Calculates exact tax amount given a base amount and percentage rate."""
    if tax_rate <= 0 or base_amount <= 0:
        return Decimal('0.00')

    tax = base_amount * (Decimal(str(tax_rate)) / Decimal('100'))
    return tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
