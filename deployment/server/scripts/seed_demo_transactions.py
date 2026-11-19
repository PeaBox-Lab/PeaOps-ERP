# Demo transaction payload for the fresh seed. Idempotent — skips if the company already has invoices.
from app.domain.models import Invoice, InvoiceLine, SalesOrder, SalesOrderLine, Party, Item, Payment, PaymentAllocation
from datetime import date, timedelta

def seed_transactions(db, company):
    cid = company.id
    if db.query(Invoice).filter(Invoice.company_id == cid).first():
        print("transactions already present — skipping")
        return
    cust = db.query(Party).filter(Party.company_id == cid, Party.code == "CUST-001").first()
    supplier = db.query(Party).filter(Party.company_id == cid, Party.code == "SUP-001").first()
    if not supplier:
        supplier = Party(company_id=cid, party_type="supplier", code="SUP-001", name="Blue Sky Components Ltd", credit_limit=0)
        db.add(supplier); db.flush()
    items = {x.sku: x for x in db.query(Item).filter(Item.company_id == cid).all()}
    psu = items.get("SKU-PSU")
    res = items.get("SKU-RES")
    if not cust or not supplier or not psu:
        print("missing master data — run full seed first")
        return

    # Outstanding AR invoice (₹2.95L)
    inv1 = Invoice(company_id=cid, party_id=cust.id, invoice_type="ar", number="INV00001",
                   invoice_date=date(2026, 11, 10), due_date=date(2026, 12, 10), currency="INR",
                   description="Bench PSU batch — October", status="open")
    inv1.lines = [InvoiceLine(description="Bench PSU 5V/3A", quantity=10, unit_price=25000, tax_rate=18)]
    db.add(inv1); db.flush()

    # Overdue invoice with partial payment (₹11.8k total, ₹5k paid)
    inv2 = Invoice(company_id=cid, party_id=cust.id, invoice_type="ar", number="INV00002",
                   invoice_date=date(2026, 10, 1), due_date=date(2026, 10, 31), currency="INR",
                   description="Resistor kit — September", status="open")
    inv2.lines = [InvoiceLine(description="Resistor 10k 1/4W", quantity=5000, unit_price=2, tax_rate=18)]
    db.add(inv2); db.flush()

    pmt = Payment(company_id=cid, party_id=cust.id, payment_type="receipt", reference="RCT-DEMO-01",
                  payment_date=date(2026, 11, 5), amount=5000, unallocated_amount=5000, status="posted")
    db.add(pmt); db.flush()
    db.add(PaymentAllocation(payment_id=pmt.id, invoice_id=inv2.id, amount=5000))
    pmt.unallocated_amount = 0
    inv2.paid_amount = 5000; inv2.status = "partially_paid"

    # Open purchase order
    from app.domain.models import PurchaseOrder, PurchaseOrderLine
    po = PurchaseOrder(company_id=cid, supplier_id=supplier.id, number="PO00001", order_date=date(2026, 11, 12),
                       promised_date=date(2026, 11, 30), currency="INR", status="confirmed")
    po.lines = [PurchaseOrderLine(item_id=psu.id, description="Bench PSU 5V/3A", quantity=100, unit_price=14000, discount_percent=0, tax_rate=18)]
    db.add(po)

    db.flush()
    print("demo transactions seeded: 2 AR invoices, 1 payment, 1 sales order")

if __name__ == "__main__":
    from app.core.db import SessionLocal
    from app.domain.models import Company
    with SessionLocal() as db:
        c = db.query(Company).first()
        if not c:
            print("no company seeded yet")
        else:
            seed_transactions(db, c)
            db.commit()