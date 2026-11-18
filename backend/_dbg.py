import os
os.environ["PEAOPS_DATABASE_URL"] = "sqlite:///./_dbg.db"
os.environ["PEAOPS_SECRET_KEY"] = "debug-secret-key-that-is-long-enough-1234567890"
os.environ["PEAOPS_ENVIRONMENT"] = "development"
os.environ["PEAOPS_AUTO_CREATE_SCHEMA"] = "true"
import importlib, app.core.config as config, app.core.db as dbmod, app.main as main
from app.core.db import Base
from app.domain.models import Company, Party, User, Role, RolePermission, UserRole, NumberSequence, Item
from app.security.rules import hash_password
import app.core.db as dbmod
dbmod.settings.secret_key = os.environ["PEAOPS_SECRET_KEY"]; dbmod.settings.database_url = os.environ["PEAOPS_DATABASE_URL"]
importlib.reload(dbmod); importlib.reload(main)
session = dbmod.SessionLocal()
company = Company(code="ACME", name="Acme", base_currency="INR"); session.add(company); session.flush()
role = Role(company_id=company.id, code="company_admin", name="Admin", system_role=True); session.add(role); session.flush()
session.add(RolePermission(role_id=role.id, permission="admin:*"))
user = User(company_id=company.id, username="admin", display_name="Admin", password_hash=hash_password("Admin@123456")); session.add(user); session.flush(); session.add(UserRole(user_id=user.id, role_id=role.id)); session.commit(); session.close()
from fastapi.testclient import TestClient
client = TestClient(main.app)
r = client.post("/api/v1/auth/login", json={"company_id": 1, "username": "admin", "password": "Admin@123456"})
print("login", r.status_code); print(r.json())
import json, base64
token = r.json()["access_token"]
payload = token.split(".")[1]
payload += "=" * (-len(payload) % 4)
print("claims", json.loads(base64.urlsafe_b64decode(payload)))
