"""Tenant isolation proof: company A cannot see or modify company B data."""
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.domain.models import Company, Item, User, Role, RolePermission, UserRole
from app.security.rules import hash_password

client = TestClient(app)


def _auth(company_id: int, username: str, password: str):
    r = client.post("/api/v1/auth/login", json={"company_id": company_id, "username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _seed_company_with_admin(db, code: str, username: str = "admin", perms=("admin:*",)):
    suffix = uuid.uuid4().hex[:6]
    company = Company(code=f"{code}-{suffix}", name=code.title(), base_currency="INR")
    db.add(company); db.flush()
    role = Role(company_id=company.id, code="company_admin", name="Company Administrator", system_role=True)
    db.add(role); db.flush()
    for p in perms:
        db.add(RolePermission(role_id=role.id, permission=p))
    user = User(company_id=company.id, username=username, display_name="Admin", password_hash=hash_password("Admin@123456"))
    db.add(user); db.flush()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()
    return company


def test_company_cannot_read_other_company_items():
    suffix = uuid.uuid4().hex[:8]
    with SessionLocal() as db:
        a = Company(code=f"ISO-A-{suffix}", name="Isolation A", base_currency="INR")
        b = Company(code=f"ISO-B-{suffix}", name="Isolation B", base_currency="INR")
        db.add_all([a, b]); db.flush()
        role_a = Role(company_id=a.id, code="company_admin", name="Company Admin A", system_role=True)
        role_b = Role(company_id=b.id, code="company_admin", name="Company Admin B", system_role=True)
        db.add_all([role_a, role_b]); db.flush()
        db.add(RolePermission(role_id=role_a.id, permission="admin:*"))
        db.add(RolePermission(role_id=role_b.id, permission="data:view"))
        db.flush()
        user_a = User(company_id=a.id, username="admin", display_name="Admin A", password_hash=hash_password("Admin@123456"))
        user_b = User(company_id=b.id, username="admin", display_name="Admin B", password_hash=hash_password("Admin@123456"))
        db.add_all([user_a, user_b]); db.flush()
        db.add(UserRole(user_id=user_a.id, role_id=role_a.id))
        db.add(UserRole(user_id=user_b.id, role_id=role_b.id))
        db.add(Item(company_id=a.id, sku=f"ISO-{suffix}", name="Isolated item A"))
        db.commit()
        a_id, b_id = a.id, b.id

    ha = _auth(a_id, "admin", "Admin@123456")
    hb = _auth(b_id, "admin", "Admin@123456")

    # B lists own company
    r = client.get(f"/api/v1/items?company_id={b_id}", headers=hb)
    assert r.status_code == 200
    assert not any(x["sku"] == f"ISO-{suffix}" for x in r.json())

    # B queries A's company -> 403
    r = client.get(f"/api/v1/items?company_id={a_id}", headers=hb)
    assert r.status_code == 403, r.text

    # B posts to A's company -> 403
    r = client.post("/api/v1/items", json={"company_id": a_id, "sku": f"BRESP-{suffix}", "name": "B sneak"}, headers=hb)
    assert r.status_code == 403
    with SessionLocal() as db:
        assert not db.query(Item).filter(Item.sku == f"BRESP-{suffix}").first()