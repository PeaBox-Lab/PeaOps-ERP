
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
ZERO = Decimal('0.00')
TWOPLACES = Decimal('0.01')
def price_line(quantity: Decimal, unit_price: Decimal, discount_percent: Decimal = ZERO, tax_rate: Decimal = ZERO):
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
def total_document(lines: list[tuple[Decimal, Decimal, Decimal, Decimal]]):
    subtotal = discount_total = tax_total = ZERO
    for quantity, unit_price, discount_percent, tax_rate in lines:
        gross, discount, net, tax, _ = price_line(quantity, unit_price, discount_percent, tax_rate)
        subtotal += gross; discount_total += discount; tax_total += tax
    net_total = subtotal - discount_total
    grand_total = net_total + tax_total
    if grand_total <= 0:
        raise ValueError('Sales document total must be greater than zero')
    return subtotal, discount_total, net_total, tax_total, grand_total
def validate_validity(valid_from: date, valid_until: date):
    if valid_until < valid_from:
        raise ValueError('Valid-until date cannot precede valid-from date')
def validate_delivery_promise(order_date: date, promised_date: date | None):
    if promised_date is not None and promised_date < order_date:
        raise ValueError('Promised delivery date cannot precede order date')
def check_credit_limit(credit_limit: Decimal, open_receivables: Decimal, pending_orders: Decimal, new_order: Decimal):
    limit = Decimal(credit_limit); exposure = Decimal(open_receivables) + Decimal(pending_orders) + Decimal(new_order)
    if limit < 0:
        raise ValueError('Credit limit cannot be negative')
    if limit > 0 and exposure > limit:
        raise ValueError(f'Customer credit limit exceeded: exposure={exposure}, limit={limit}')
    return exposure
