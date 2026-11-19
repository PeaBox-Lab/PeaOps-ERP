"""One-off fix: remove the malformed demo AR seed and reseed plausible amounts."""
from app.core.db import SessionLocal
from app.domain.models import Invoice, InvoiceLine, Payment, PaymentAllocation, SalesOrder, PurchaseOrder
from datetime import date

with SessionLocal() as db:
    from app.domain.models import Invoice, InvoiceLine, Payment, PaymentAllocation, SalesOrder, PurchaseOrder, PurchaseOrderLine
    from datetime import date
    for inv in list(db.query(Invoice).filter(Invoice.invoice_type == 'ar', Invoice.number.in_(['INV00001','INV00002']))):
        db.query(PaymentAllocation).filter(PaymentAllocation.invoice_id == inv.id).delete(synchronize_session=False)
        db.delete(inv)
    db.query(Payment).filter(Payment.reference == 'RCT-DEMO-01').delete(synchronize_session=False)
    db.query(PurchaseOrderLine).filter(PurchaseOrderLine.order_id.in_(db.query(PurchaseOrder.id).filter(PurchaseOrder.number == 'PO00001'))).delete(synchronize_session=False)
    db.query(PurchaseOrder).filter(PurchaseOrder.number == 'PO00001').delete(synchronize_session=False)
    db.query(SalesOrder).filter(SalesOrder.number == 'SO00001').delete(synchronize_session=False)
    db.commit()
    print('cleared malformed demo AR/tx rows')