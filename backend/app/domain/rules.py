from datetime import date
from decimal import Decimal

ZERO = Decimal('0.00')


def validate_journal(lines: list[tuple[Decimal, Decimal]]) -> None:
    debit = sum((Decimal(d) for d, _ in lines), ZERO)
    credit = sum((Decimal(c) for _, c in lines), ZERO)
    if any(Decimal(d) < 0 or Decimal(c) < 0 or (Decimal(d) and Decimal(c)) for d, c in lines):
        raise ValueError('Each line must contain a non-negative debit OR credit')
    if debit <= 0 or debit != credit:
        raise ValueError(f'Journal is not balanced: debit={debit}, credit={credit}')


def calculate_invoice(lines: list[tuple[Decimal, Decimal, Decimal]]) -> tuple[Decimal, Decimal, Decimal]:
    subtotal = ZERO
    tax = ZERO
    for quantity, unit_price, tax_rate in lines:
        quantity, unit_price, tax_rate = Decimal(quantity), Decimal(unit_price), Decimal(tax_rate)
        if quantity <= 0 or unit_price < 0 or tax_rate < 0 or tax_rate > 100:
            raise ValueError('Invalid invoice line values')
        net = (quantity * unit_price).quantize(Decimal('0.01'))
        subtotal += net
        tax += (net * tax_rate / Decimal('100')).quantize(Decimal('0.01'))
    total = subtotal + tax
    if total <= 0:
        raise ValueError('Invoice total must be greater than zero')
    return subtotal, tax, total


def allocate_balance(total: Decimal, paid: Decimal, amount: Decimal) -> tuple[Decimal, Decimal, str]:
    total, paid, amount = Decimal(total), Decimal(paid), Decimal(amount)
    outstanding = max(total - paid, ZERO)
    if amount <= 0:
        raise ValueError('Allocation amount must be greater than zero')
    if amount > outstanding:
        raise ValueError('Allocation exceeds invoice outstanding balance')
    new_paid = paid + amount
    new_outstanding = total - new_paid
    return new_paid, new_outstanding, 'paid' if new_outstanding == 0 else 'partially_paid'


def ageing_bucket(due_date: date, as_of: date, outstanding: Decimal) -> str:
    if Decimal(outstanding) <= 0:
        return 'paid'
    days = (as_of - due_date).days
    if days <= 0: return 'current'
    if days <= 30: return '1-30'
    if days <= 60: return '31-60'
    if days <= 90: return '61-90'
    return '90+'


def issue_number(prefix: str, next_number: int, padding: int) -> tuple[str, int]:
    if next_number < 1 or padding < 1:
        raise ValueError('Invalid numbering sequence configuration')
    return f'{prefix}{next_number:0{padding}d}', next_number + 1
