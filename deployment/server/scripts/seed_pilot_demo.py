"""Seed a pilot demo company into the current database. Idempotent.
Run inside the api container or locally with the app importable:
  docker compose -f docker-compose.production.yml exec -T -e PYTHONPATH=/app api python /tmp/seed.py
"""
from app.core.db import SessionLocal
from app.domain.models import Company, Party, User, Role, RolePermission, UserRole, Item, Warehouse, NumberSequence
from app.security.rules import hash_password

ADMIN_PASSWORD = "Admin@123456"

with SessionLocal() as db:
    if db.query(Company).first():
        print("already seeded — nothing to do")
    else:
        c = Company(code="ACME", name="Acme Pvt Ltd", base_currency="INR")
        db.add(c); db.flush()
        r = Role(company_id=c.id, code="company_admin", name="Company Administrator", system_role=True)
        db.add(r); db.flush()
        db.add(RolePermission(role_id=r.id, permission="admin:*"))
        u = User(company_id=c.id, username="admin", display_name="Demo Admin", password_hash=hash_password(ADMIN_PASSWORD))
        db.add(u); db.flush(); db.add(UserRole(user_id=u.id, role_id=r.id))
        db.add(Party(company_id=c.id, party_type="customer", code="CUST-001", name="Blue Sky Retail Pvt Ltd", credit_limit=500000))
        for sku, name in [("SKU-PSU", "Bench PSU 5V/3A"), ("SKU-RES", "Resistor 10k 1/4W"), ("SKU-CASE", "Enclosure 120x80x40")]:
            db.add(Item(company_id=c.id, sku=sku, name=name, unit="EA"))
        db.add(Warehouse(company_id=c.id, code="MAIN", name="Main warehouse"))
        for doc, prefix in [("ar_invoice","INV"),("ap_invoice","PINV"),("sales_quote","SQ"),("sales_order","SO"),("purchase_request","PR"),("rfq","RFQ"),("supplier_quote","SUP"),("purchase_order","PO"),("goods_receipt","GRN"),("stock_transfer","ST"),("receipt","RCT"),("payment","PMT"),("sales_delivery","DN")]:
            db.add(NumberSequence(company_id=c.id, document_type=doc, prefix=prefix, next_number=1, padding=5))
        db.commit()
        print("demo seeded: company 1 / admin / Admin@123456 (CHANGE IT)")