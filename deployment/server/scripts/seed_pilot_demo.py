"""Seed a holding-company demo (two subsidiaries under one group). Idempotent."""
import os
from app.core.db import SessionLocal
from app.domain.models import Company, Party, User, Role, RolePermission, UserRole, Item, Warehouse, NumberSequence, SmtpSetting, Account, FiscalPeriod, PostingProfile, Group, GroupCompany, GroupMember
from app.security.rules import hash_password
from datetime import date

ADMIN_PASSWORD = "Admin@123456"
SUPERADMIN_USERNAME = os.getenv("PEAOPS_SUPERADMIN_USERNAME", "").strip().lower()
SUPERADMIN_PASSWORD = os.getenv("PEAOPS_SUPERADMIN_PASSWORD", "")

ACCOUNTS = [
    ("1000", "Cash & Bank", "asset"), ("1100", "Accounts Receivable", "asset"),
    ("1200", "Inventory", "asset"),   ("1500", "Fixed Assets", "asset"),
    ("2000", "Accounts Payable", "liability"), ("2100", "Taxes Payable", "liability"),
    ("3000", "Owner's Equity", "equity"), ("4000", "Sales Revenue", "revenue"),
    ("5000", "Cost of Goods Sold", "expense"), ("6000", "Operating Expenses", "expense"),
    ("7000", "Depreciation", "expense"), ("8000", "Interest & Finance Costs", "expense"),
]

PERIODS = [
    ("FY26-11", "Nov 2026", date(2026, 11, 1), date(2026, 11, 30), "closed"),
    ("FY26-12", "Dec 2026", date(2026, 12, 1), date(2026, 12, 31), "open"),
    ("FY27-01", "Jan 2027", date(2027, 1, 1), date(2027, 1, 31), "open"),
]

SEQUENCES = [("ar_invoice","INV"),("ap_invoice","PINV"),("sales_quote","SQ"),("sales_order","SO"),("purchase_request","PR"),("rfq","RFQ"),("supplier_quote","SUP"),("purchase_order","PO"),("goods_receipt","GRN"),("stock_transfer","ST"),("receipt","RCT"),("payment","PMT"),("sales_delivery","DN")]


def _ensure_coa_and_profile(db, company_id: int):
    account_ids = {}
    for code, name_, atype in ACCOUNTS:
        existing = db.query(Account).filter(Account.company_id == company_id, Account.code == code).first()
        if existing:
            account_ids[code] = existing.id
        else:
            a = Account(company_id=company_id, code=code, name=name_, account_type=atype)
            db.add(a); db.flush(); account_ids[code] = a.id
    if not db.query(PostingProfile).filter(PostingProfile.company_id == company_id, PostingProfile.profile_type == "sales").first():
        db.add(PostingProfile(company_id=company_id, profile_type="sales",
            receivable_account_id=account_ids["1100"], revenue_account_id=account_ids["4000"],
            inventory_account_id=account_ids["1200"], cogs_account_id=account_ids["5000"]))
    if not db.query(PostingProfile).filter(PostingProfile.company_id == company_id, PostingProfile.profile_type == "procurement").first():
        db.add(PostingProfile(company_id=company_id, profile_type="procurement",
            payable_account_id=account_ids["2000"], inventory_account_id=account_ids["1200"],
            expense_account_id=account_ids["6000"]))
    for code, name_, start, end, status in PERIODS:
        if not db.query(FiscalPeriod).filter(FiscalPeriod.company_id == company_id, FiscalPeriod.code == code).first():
            db.add(FiscalPeriod(company_id=company_id, code=code, name=name_, start_date=start, end_date=end, status=status))
    for doc, prefix in SEQUENCES:
        if not db.query(NumberSequence).filter(NumberSequence.company_id == company_id, NumberSequence.document_type == doc).first():
            db.add(NumberSequence(company_id=company_id, document_type=doc, prefix=prefix, next_number=1, padding=5))

with SessionLocal() as db:
    group = db.query(Group).first()
    if group:
        print("group already exists — skipping demo seed")
    else:
        group = Group(name="PeaOps Holdco", description="Holding company for demo subsidiaries")
        db.add(group); db.flush()
        for code, name, currency in [("ACME", "Acme Pvt Ltd", "INR"), ("BETA", "Beta Exports Ltd", "INR")]:
            c = db.query(Company).filter(Company.code == code).first()
            if not c:
                c = Company(code=code, name=name, base_currency=currency)
                db.add(c); db.flush()
            db.add(GroupCompany(group_id=group.id, company_id=c.id))
        db.flush()
        # Seed master data per company
        companies = db.query(Company).join(GroupCompany, GroupCompany.company_id == Company.id).filter(GroupCompany.group_id == group.id).all()
        for c in companies:
            role = db.query(Role).filter(Role.company_id == c.id, Role.code == "company_admin").first()
            if not role:
                role = Role(company_id=c.id, code="company_admin", name="Company Administrator", system_role=True)
                db.add(role); db.flush()
                db.add(RolePermission(role_id=role.id, permission="admin:*"))
            user = db.query(User).filter(User.company_id == c.id, User.username == "admin").first()
            if not user:
                user = User(company_id=c.id, username="admin", display_name="Demo Admin", password_hash=hash_password(ADMIN_PASSWORD), must_change_password=False)
                db.add(user); db.flush()
                db.add(UserRole(user_id=user.id, role_id=role.id))
            if not db.query(GroupMember).filter(GroupMember.group_id == group.id, GroupMember.user_id == user.id).first():
                db.add(GroupMember(group_id=group.id, user_id=user.id))
            if not db.query(Party).filter(Party.company_id == c.id).first():
                db.add(Party(company_id=c.id, party_type="customer", code="CUST-001", name="Blue Sky Retail Pvt Ltd", credit_limit=500000))
                db.add(Party(company_id=c.id, party_type="supplier", code="SUP-001", name="Blue Sky Components Ltd", credit_limit=0))
            if not db.query(Item).filter(Item.company_id == c.id).first():
                for sku, name in [("SKU-PSU", "Bench PSU 5V/3A"), ("SKU-RES", "Resistor 10k 1/4W"), ("SKU-CASE", "Enclosure 120x80x40")]:
                    db.add(Item(company_id=c.id, sku=sku, name=name, unit="EA"))
            if not db.query(Warehouse).filter(Warehouse.company_id == c.id).first():
                db.add(Warehouse(company_id=c.id, code="MAIN", name="Main warehouse"))
            _ensure_coa_and_profile(db, c.id)
        if not db.query(SmtpSetting).first():
            db.add(SmtpSetting(host="", port=587, username="", password="", from_address="", use_tls=True, active=False))
        db.commit()
        # Seed a SuperAdmin via env var if requested
        if SUPERADMIN_USERNAME and SUPERADMIN_PASSWORD:
            all_users = db.query(User).join(Company, Company.id == User.company_id).filter(User.username == SUPERADMIN_USERNAME).all()
            if not all_users:
                for c in companies:
                    sa_role = db.query(Role).filter(Role.company_id == c.id, Role.code == "super_admin").first()
                    if not sa_role:
                        sa_role = Role(company_id=c.id, code="super_admin", name="Super Administrator", system_role=True)
                        db.add(sa_role); db.flush()
                        db.add(RolePermission(role_id=sa_role.id, permission="super_admin:*"))
                    sa_user = User(company_id=c.id, username=SUPERADMIN_USERNAME, display_name="Super Administrator", password_hash=hash_password(SUPERADMIN_PASSWORD), must_change_password=False)
                    db.add(sa_user); db.flush()
                    db.add(UserRole(user_id=sa_user.id, role_id=sa_role.id))
                # ensure membership for switching
                for sa_user in db.query(User).filter(User.username == SUPERADMIN_USERNAME).all():
                    if not db.query(GroupMember).filter(GroupMember.group_id == group.id, GroupMember.user_id == sa_user.id).first():
                        db.add(GroupMember(group_id=group.id, user_id=sa_user.id))
                print("seed: superadmin created in ACME and BETA")
        for c in companies:
            print(f"seed: company {c.id} {c.code} {c.name}")
        print("seed: group →", group.name)
