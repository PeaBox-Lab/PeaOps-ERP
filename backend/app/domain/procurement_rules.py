from datetime import date
from decimal import Decimal, ROUND_HALF_UP

ZERO = Decimal('0.00')
TWOPLACES = Decimal('0.01')


def price_purchase_line(quantity: Decimal, unit_price: Decimal, discount_percent: Decimal = ZERO, tax_rate: Decimal = ZERO):
    quantity = Decimal(quantity); unit_price = Decimal(unit_price)
    discount_percent = Decimal(discount_percent); tax_rate = Decimal(tax_rate)
    if quantity <= 0 or unit_price < 0:
        raise ValueError('Quantity must be positive and unit price cannot be negative')
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError('Discount percent must be between 0 and 100')
    if tax_rate < 0 or tax_rate > 100:
        raise ValueError('Tax rate must be between 0 and 100')
    gross = (quantity * unit_price).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    discount = (gross * discount_percent / Decimal('100')).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    net = gross - discount
    tax = (net * tax_rate / Decimal('100')).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    return gross, discount, net, tax, net + tax


def total_purchase_document(lines: list[tuple[Decimal, Decimal, Decimal, Decimal]]):
    subtotal = discount_total = tax_total = ZERO
    for quantity, unit_price, discount_percent, tax_rate in lines:
        gross, discount, _, tax, _ = price_purchase_line(quantity, unit_price, discount_percent, tax_rate)
        subtotal += gross; discount_total += discount; tax_total += tax
    net_total = subtotal - discount_total
    total = net_total + tax_total
    if total <= 0:
        raise ValueError('Procurement document total must be greater than zero')
    return subtotal, discount_total, net_total, tax_total, total


def validate_required_date(request_date: date, required_date: date):
    if required_date < request_date:
        raise ValueError('Required date cannot precede request date')


def validate_quote_window(rfq_date: date, response_due: date):
    if response_due < rfq_date:
        raise ValueError('RFQ response due date cannot precede RFQ date')


def choose_best_quote(quotes: list[tuple[int, Decimal, date | None]]):
    if not quotes:
        raise ValueError('At least one supplier quotation is required')
    eligible = [(quote_id, Decimal(total), promised) for quote_id, total, promised in quotes if Decimal(total) > 0]
    if not eligible:
        raise ValueError('No eligible supplier quotations')
    return min(eligible, key=lambda x: (x[1], x[2] or date.max, x[0]))


def apply_receipt(ordered: Decimal, received: Decimal, new_receipt: Decimal):
    ordered = Decimal(ordered); received = Decimal(received); new_receipt = Decimal(new_receipt)
    if ordered <= 0 or received < 0 or new_receipt <= 0:
        raise ValueError('Receipt quantities must be positive')
    if received + new_receipt > ordered:
        raise ValueError('Receipt quantity exceeds remaining purchase order quantity')
    updated = received + new_receipt
    status = 'received' if updated == ordered else 'partially_received'
    return updated, ordered - updated, status
