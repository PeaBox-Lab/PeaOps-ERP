from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.domain.models import (
    Company, Party, User, Role, RolePermission, UserRole,
    FiscalPeriod, NumberSequence, Item, JournalEntry, JournalLine, Account,
)
from app.security.rules import hash_password

client = TestClient(app)

def _seed_test_company():
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
        session.add(FiscalPeriod(company_id=company.id, code="FY26-Nov", name="November 2026",
                                 start_date=date(2026, 11, 1), end_date=date(2026, 11, 30),
                                 status="open"))
        session.commit()

def _seed_period():
    _seed_test_company()
    with SessionLocal() as session:
        if session.query(FiscalPeriod).filter(FiscalPeriod.company_id == 1).first():
            return
        session.add(FiscalPeriod(
            company_id=1, code="FY26-Nov", name="November 2026",
            start_date=date(2026, 11, 1), end_date=date(2026, 11, 30),
            status="closed",
        ))
        session.commit()

def test_closed_period_blocks_journal_post():
    _seed_test_company()
    _seed_period()
    r = client.post("/api/v1/auth/login", json={"company_id": 1, "username": "admin", "password": "Admin@123456"})
    assert r.status_code == 200
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # Create a simple journal
    r = client.post("/api/v1/journal-entries", json={
        "company_id": 1, "reference": "JV-TEST-PERIOD", "description": "Period lock test",
        "lines": [{"account_id": 1, "debit": 1000, "credit": 0}, {"account_id": 2, "credit": 1000}],
    }, headers=h)
    assert r.status_code == 200, r.text
    entry_id = r.json()["id"]

    # Attempt to post into a closed period -> 409
    r = client.post(f"/api/v1/journal-entries/{entry_id}/post?approval_id=1", json={}, headers=h)
    assert r.status_code == 409, r.text

def test_change_password_and_flag():
    _seed_test_company()
    r = client.post("/api/v1/auth/login", json={"company_id": 1, "username": "admin", "password": "Admin@123456"})
    assert r.status_code == 200
    assert "must_change_password" in r.json()

def test_password_change_endpoint():
    _seed_test_company()
    r = client.post("/api/v1/auth/login", json={"company_id": 1, "username": "admin", "password": "Admin@123456"})
    assert r.status_code == 200
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r2 = client.post("/api/v1/auth/change-password", json={
        "company_id": 1,
        "username": "admin",
        "current_password": "Admin@123456",
        "new_password": "Admin@123457",
    }, headers=h)
    assert r2.status_code == 200, r2.text
    assert r2.json()["changed"] is True