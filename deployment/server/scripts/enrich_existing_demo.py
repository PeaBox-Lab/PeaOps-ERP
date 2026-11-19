"""Idempotent enrichment for the existing demo database.
Adds COA + posting profiles + fiscal periods + a supplier + a few realistic AR invoices/payments.
Safe to run multiple times. Works on whatever company is already seeded (usually ACME).
"""
from datetime import date
from decimal import Decimal
from app.core.db import SessionLocal
from app.domain.models import (
    Company, Account, FiscalPeriod, PostingProfile, Party, Invoice, InvoiceLine, Item,
    NumberSequence, Payment, PaymentAllocation,
)

ACCOUNTS = [
    ("1000", "Cash & Bank", "asset"), ("1100", "Accounts Receivable", "asset"),
    ("1200", "Inventory", "asset"),   ("1500", "Fixed Assets", "asset"),
    ("2000", "Accounts Payable", "liability"), ("2100", "Taxes Payable", "liability"),
    ("3000", "Owner's Equity", "equity"), ("4000", "Sales Revenue", "revenue"),
    ("5000", "Cost of Goods Sold", "expense"), ("6000", "Operating Expenses", "expense"),
    ("7000", "Depreciation", "expense"), ("8000", "Interest & Finance Costs", "expense"),
]

PERIODS = [("FY26-11", "Nov 2026", date(2026, 11, 1), date(2026, 11, 30), "closed"),
           ("FY26-12", "Dec 2026", date(2026, 12, 1), date(2026, 12, 31), "open"),
           ("FY27-01", "Jan 2027", date(2027, 1, 1), date(2027, 1, 31), "open")]

def get_company(db):
    c = db.query(Company).first()
    assert c, "No company found — seed first."
    return c

def ensure_accounts(db, cid):
    created = []
    for code, name, atype in ACCOUNTS:
        existing = db.query(Account).filter(Account.company_id == cid, Account.code == code).first()
        if existing: continue
        db.add(Account(company_id=cid, code=code, name=name, account_type=atype))
        created.append(code)
    if created:
        db.flush()
    return created

def account_id(db, cid, code):
    a = db.query(Account).filter(Account.company_id == cid, Account.code == code).first()
    return a.id if a else None

def ensure_posting_profiles(db, cid):
    created = []
    if not db.query(PostingProfile).filter(PostingProfile.company_id == cid, PostingProfile.profile_type == "sales").first():
        db.add(PostingProfile(company_id=cid, profile_type="sales",
            receivable_account_id=account_id(db, cid, "1100"),
            revenue_account_id=account_id(db, cid, "4000"),
            inventory_account_id=account_id(db, cid, "1200"),
            cogs_account_id=account_id(db, cid, "5000")))
        created.append("sales")
    if not db.query(PostingProfile).filter(PostingProfile.company_id == cid, PostingProfile.profile_type == "procurement").first():
        db.add(PostingProfile(company_id=cid, profile_type="procurement",
            payable_account_id=account_id(db, cid, "2000"),
            inventory_account_id=account_id(db, cid, "1200"),
            expense_account_id=account_id(db, cid, "6000")))
        created.append("procurement")
    if created: db.flush()
    return created

def ensure_periods(db, cid):
    created = []
    for code, name, start, end, status in PERIODS:
        if db.query(FiscalPeriod).filter(FiscalPeriod.company_id == cid, FiscalPeriod.code == code).first():
            continue
        db.add(FiscalPeriod(company_id=cid, code=code, name=name, start_date=start, end_date=end, status=status))
        created.append(code)
    if created: db.flush()
    return created

def ensure_supplier(db, cid):
    existing = db.query(Party).filter(Party.company_id == cid, Party.code == "SUP-001").first()
    if existing: return existing
    s = Party(company_id=cid, party_type="supplier", code="SUP-001", name="ABC Supplies Ltd", credit_limit=0)
    db.add(s); db.flush(); return s

def ensure_sequences(db, cid):
    defaults = [("ar_invoice","INV"),("ap_invoice","PINV"),("sales_quote","SQ"),("sales_order","SO"),("purchase_request","PR"),("rfq","RFQ"),("supplier_quote","SUP"),("purchase_order","PO"),("goods_receipt","GRN"),("stock_transfer","ST"),("receipt","RCT"),("payment","PMT"),("sales_delivery","DN")]
    for doc, prefix in defaults:
        if not db.query(NumberSequence).filter(NumberSequence.company_id == cid, NumberSequence.document_type == doc).first():
            db.add(NumberSequence(company_id=cid, document_type=doc, prefix=prefix, next_number=1, padding=5))
    db.flush()

def ensure_invoices(db, cid):
    existing = db.query(Invoice).filter(Invoice.company_id == cid, Invoice.invoice_type == "ar").all()
    if existing:
        return existing
    customer = db.query(Party).filter(Party.company_id == cid, Party.party_type == "customer").order_by(Party.id).first()
    if not customer:
        return []
    items = db.query(Item).filter(Item.company_id == cid).limit(3).all()
    if not items:
        return []
    out = []
    for idx, (qty, price) in enumerate([(10, 25000), (5, 80000)], start=1):
        item = items[min(idx - 1, len(items) - 1)]
        from app.domain.rules import calculate_invoice
        invoice = Invoice(company_id=cid, party_id=customer.id, invoice_type="ar", number=f"INV0000{idx}", invoice_date=date(2026, 11, 15 + idx - 1), due_date=date(2026, 12, 15 + idx - 1), currency="INR", description=f"Demo invoice {idx}")
        invoice.lines = [InvoiceLine(description=item.name, quantity=qty, unit_price=price, tax_rate=18)]
        db.add(invoice)
        db.flush()
        invoice.recalculate()
        invoice.status = "open"
        out.append(invoice)
    db.flush()
    # partial payment on invoice 1
    if out:
        inv = out[0]
        bank = db.query(Account).filter(Account.company_id == cid, Account.code == "1000").first()
        payment = Payment(company_id=cid, party_id=customer.id, payment_type="receipt", reference="RCT-ENRICH-1", payment_date=date(2026, 11, 20), amount=Decimal(str(inv.total_amount / 2)), unallocated_amount=Decimal(str(inv.total_amount / 2)), status="posted")
        db.add(payment); db.flush()
        db.add(PaymentAllocation(payment_id=payment.id, invoice_id=inv.id, amount=payment.unallocated_amount))
        payment.unallocated_amount = Decimal("0")
        inv.paid_amount = Decimal(str(inv.total_amount / 2)); inv.status = "partially_paid"
        db.flush()
    return out

def main():
    with SessionLocal() as db:
        c = get_company(db)
        print(f"enriching company {c.id}: {c.code}")
        a = ensure_accounts(db, c.id)
        print("accounts added:", a)
        pp = ensure_posting_profiles(db, c.id)
        print("posting profiles:", pp)
        p = ensure_periods(db, c.id)
        print("periods:", p)
        sup = ensure_supplier(db, c.id)
        print("supplier:", sup.code)
        ensure_sequences(db, c.id)
        invs = ensure_invoices(db, c.id)
        print("ar invoices seeded:", [(i.number, str(i.total_amount), i.status) for i in invs])
        db.commit()
        print("enrichment complete")

if __name__ == "__main__":
    main()