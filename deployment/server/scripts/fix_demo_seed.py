"""One-off repair: recalc seeded demo invoices so totals/status are consistent."""
from app.core.db import SessionLocal
from app.domain.models import Invoice, PaymentAllocation
from decimal import Decimal

with SessionLocal() as db:
    invs = db.query(Invoice).filter(Invoice.invoice_type == 'ar').order_by(Invoice.id).all()
    for inv in invs:
        inv.recalculate()
        allocs = db.query(PaymentAllocation).filter(PaymentAllocation.invoice_id == inv.id).all()
        paid = sum((a.amount for a in allocs), Decimal('0.00'))
        inv.paid_amount = paid
        if inv.total_amount and inv.paid_amount >= inv.total_amount:
            inv.status = 'paid'
        elif inv.paid_amount > 0:
            inv.status = 'partially_paid'
        elif inv.status not in {'draft', 'open', 'void'}:
            inv.status = 'open'
        print(inv.number, inv.status, 'total=', inv.total_amount, 'paid=', inv.paid_amount)
    db.commit()
    print('done')