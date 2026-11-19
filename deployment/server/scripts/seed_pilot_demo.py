"""Seed a pilot demo company into the current database. Idempotent."""
from app.core.db import SessionLocal
from app.domain.models import Company, Party, User, Role, RolePermission, UserRole, Item, Warehouse, NumberSequence, SmtpSetting, Account, FiscalPeriod, PostingProfile
from app.security.rules import hash_password
from datetime import date

ADMIN_PASSWORD = "Admin@123456"

ACCOUNTS = [
    ("1000", "Cash & Bank", "asset"),
    ("1100", "Accounts Receivable", "asset"),
    ("1200", "Inventory", "asset"),
    ("1500", "Fixed Assets", "asset"),
    ("2000", "Accounts Payable", "liability"),
    ("2100", "Taxes Payable", "liability"),
    ("3000", "Owner's Equity", "equity"),
    ("4000", "Sales Revenue", "revenue"),
    ("5000", "Cost of Goods Sold", "expense"),
    ("6000", "Operating Expenses", "expense"),
    ("7000", "Depreciation", "expense"),
    ("8000", "Interest & Finance Costs", "expense"),
]

PERIODS = [
    ("FY26-11", "Nov 2026", date(2026, 11, 1), date(2026, 11, 30), "closed"),
    ("FY26-12", "Dec 2026", date(2026, 12, 1), date(2026, 12, 31), "open"),
    ("FY27-01", "Jan 2027", date(2027, 1, 1), date(2027, 1, 31), "open"),
]

with SessionLocal() as db:
    if db.query(Company).first():
        print("already seeded — nothing to do")
    else:
        c = Company(code="ACME", name="Acme Pvt Ltd", base_currency="INR")
        db.add(c); db.flush()
        r = Role(company_id=c.id, code="company_admin", name="Company Administrator", system_role=True)
        db.add(r); db.flush()
        db.add(RolePermission(role_id=r.id, permission="admin:*"))
        u = User(company_id=c.id, username="admin", display_name="Demo Admin", password_hash=hash_password(ADMIN_PASSWORD), must_change_password=False)
        db.add(u); db.flush(); db.add(UserRole(user_id=u.id, role_id=r.id))
        db.add(Party(company_id=c.id, party_type="customer", code="CUST-001", name="Blue Sky Retail Pvt Ltd", credit_limit=500000))
        for sku, name in [("SKU-PSU", "Bench PSU 5V/3A"), ("SKU-RES", "Resistor 10k 1/4W"), ("SKU-CASE", "Enclosure 120x80x40")]:
            db.add(Item(company_id=c.id, sku=sku, name=name, unit="EA"))
        db.add(Warehouse(company_id=c.id, code="MAIN", name="Main warehouse"))
        # Chart of accounts
        account_ids = {}
        for code, name_, atype in ACCOUNTS:
            a = Account(company_id=c.id, code=code, name=name_, account_type=atype)
            db.add(a); db.flush()
            account_ids[code] = a.id
        # Posting profile (sales)
        db.add(PostingProfile(
            company_id=c.id,
            profile_type="sales",
            receivable_account_id=account_ids["1100"],
            revenue_account_id=account_ids["4000"],
            inventory_account_id=account_ids["1200"],
            cogs_account_id=account_ids["5000"],
        ))
        # Posting profile (procurement)
        db.add(PostingProfile(
            company_id=c.id,
            profile_type="procurement",
            payable_account_id=account_ids["2000"],
            inventory_account_id=account_ids["1200"],
            expense_account_id=account_ids["6000"],
        ))
        # Fiscal periods
        for code, name_, start, end, status in PERIODS:
            db.add(FiscalPeriod(company_id=c.id, code=code, name=name_, start_date=start, end_date=end, status=status))
        # SMTP
        if not db.query(SmtpSetting).first():
            db.add(SmtpSetting(host="", port=587, username="", password="", from_address="", use_tls=True, active=False))
        for doc, prefix in [("ar_invoice","INV"),("ap_invoice","PINV"),("sales_quote","SQ"),("sales_order","SO"),("purchase_request","PR"),("rfq","RFQ"),("supplier_quote","SUP"),("purchase_order","PO"),("goods_receipt","GRN"),("stock_transfer","ST"),("receipt","RCT"),("payment","PMT"),("sales_delivery","DN")]:
            db.add(NumberSequence(company_id=c.id, document_type=doc, prefix=prefix, next_number=1, padding=5))
        db.commit()
        print("demo seeded: company 1 / admin / Admin@123456")