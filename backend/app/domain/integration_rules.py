
from decimal import Decimal

ZERO = Decimal('0.00')


def require_idempotency_key(value: str):
    key=(value or '').strip()
    if len(key)<8 or len(key)>120: raise ValueError('Idempotency key must contain 8 to 120 characters')
    return key


def validate_delivery_quantities(ordered: Decimal, previously_delivered: Decimal, delivery: Decimal):
    ordered=Decimal(ordered);previously_delivered=Decimal(previously_delivered);delivery=Decimal(delivery)
    if ordered<=0 or previously_delivered<0 or delivery<=0: raise ValueError('Delivery quantities must be positive')
    if previously_delivered+delivery>ordered: raise ValueError('Delivery quantity exceeds remaining sales order quantity')
    updated=previously_delivered+delivery
    return updated,ordered-updated,'delivered' if updated==ordered else 'partially_delivered'


def three_way_match(po_quantity: Decimal,received_quantity: Decimal,invoiced_quantity: Decimal,po_unit_price: Decimal,invoice_unit_price: Decimal,quantity_tolerance: Decimal=Decimal('0'),price_tolerance_percent: Decimal=Decimal('0')):
    po_quantity=Decimal(po_quantity);received_quantity=Decimal(received_quantity);invoiced_quantity=Decimal(invoiced_quantity)
    po_unit_price=Decimal(po_unit_price);invoice_unit_price=Decimal(invoice_unit_price)
    quantity_tolerance=Decimal(quantity_tolerance);price_tolerance_percent=Decimal(price_tolerance_percent)
    if min(po_quantity,received_quantity,invoiced_quantity,po_unit_price,invoice_unit_price,quantity_tolerance,price_tolerance_percent)<0: raise ValueError('Match inputs cannot be negative')
    quantity_variance=invoiced_quantity-received_quantity
    price_variance=invoice_unit_price-po_unit_price
    allowed_price=po_unit_price*price_tolerance_percent/Decimal('100')
    quantity_ok=quantity_variance<=quantity_tolerance
    price_ok=abs(price_variance)<=allowed_price
    return {'quantity_variance':quantity_variance,'price_variance':price_variance,'quantity_ok':quantity_ok,'price_ok':price_ok,'matched':quantity_ok and price_ok}


def journal_totals(lines: list[tuple[Decimal,Decimal]]):
    debit=sum((Decimal(d) for d,_ in lines),ZERO);credit=sum((Decimal(c) for _,c in lines),ZERO)
    if debit<=0 or debit!=credit: raise ValueError(f'Integrated journal is not balanced: debit={debit}, credit={credit}')
    return debit,credit


def sales_journal(amount: Decimal,cost: Decimal):
    amount=Decimal(amount);cost=Decimal(cost)
    if amount<=0 or cost<0: raise ValueError('Invalid sales posting amounts')
    lines=[('accounts_receivable',amount,ZERO),('revenue',ZERO,amount)]
    if cost>0: lines += [('cost_of_goods_sold',cost,ZERO),('inventory',ZERO,cost)]
    journal_totals([(d,c) for _,d,c in lines]);return lines


def purchase_journal(amount: Decimal):
    amount=Decimal(amount)
    if amount<=0: raise ValueError('Supplier invoice amount must be greater than zero')
    lines=[('inventory_or_expense',amount,ZERO),('accounts_payable',ZERO,amount)]
    journal_totals([(d,c) for _,d,c in lines]);return lines
