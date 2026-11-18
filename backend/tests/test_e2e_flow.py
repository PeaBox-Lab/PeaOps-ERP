from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from app.domain.models import Company, Party, User, Role, RolePermission, UserRole, NumberSequence, Item
from app.security.rules import hash_password

client = TestClient(app)

def _seed():
    with SessionLocal() as session:
        if session.query(Company).first():
            return
        company = Company(code="ACME", name="Acme Pvt Ltd", base_currency="INR")
        session.add(company); session.flush()
        role = Role(company_id=company.id, code="company_admin", name="Company Administrator", system_role=True)
        session.add(role); session.flush()
        session.add(RolePermission(role_id=role.id, permission="admin:*"))
        user = User(company_id=company.id, username="admin", display_name="Admin", password_hash=hash_password("Admin@123456"))
        session.add(user); session.flush(); session.add(UserRole(user_id=user.id, role_id=role.id))
        session.add(Party(company_id=company.id, party_type="customer", code="CUST-001", name="Blue Sky Retail", credit_limit=100000))
        session.add(Item(company_id=company.id, sku="SKU-PSU", name="Bench PSU", unit="EA"))
        session.add(NumberSequence(company_id=company.id, document_type="ar_invoice", prefix="INV", next_number=1, padding=5))
        session.commit()

def test_pilot_login_and_invoice_flow():
    _seed()
    r = client.post("/api/v1/auth/login", json={"company_id": 1, "username": "admin", "password": "Admin@123456"})
    assert r.status_code == 200, r.text
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = client.post("/api/v1/invoices", json={"company_id": 1, "party_id": 1, "invoice_type": "ar", "invoice_date": "2026-11-18", "due_date": "2026-12-18", "lines": [{"description": "Consulting services", "quantity": 10, "unit_price": 25000, "tax_rate": 18}]}, headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["number"] == "INV00001"
    r = client.get("/api/v1/invoices", params={"company_id": 1}, headers=h)
    assert any(i["number"] == "INV00001" for i in r.json())