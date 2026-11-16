"""Create the first company admin after migrations. Run from backend directory."""
import getpass
from sqlalchemy import select
from app.core.db import SessionLocal
from app.domain.models import Company,User,Role,RolePermission,UserRole
from app.security.rules import hash_password

def main():
    company_code=input('Company code: ').strip();username=input('Admin username: ').strip().lower();display=input('Display name: ').strip();password=getpass.getpass('Password: ')
    with SessionLocal() as db:
        company=db.scalar(select(Company).where(Company.code==company_code))
        if not company:raise SystemExit('Company not found; create the company through controlled setup first.')
        if db.scalar(select(User).where(User.company_id==company.id,User.username==username)):raise SystemExit('User already exists.')
        role=db.scalar(select(Role).where(Role.company_id==company.id,Role.code=='company_admin'))
        if not role:
            role=Role(company_id=company.id,code='company_admin',name='Company Administrator',system_role=True);db.add(role);db.flush();db.add(RolePermission(role_id=role.id,permission='admin:*'))
        user=User(company_id=company.id,username=username,display_name=display,password_hash=hash_password(password));db.add(user);db.flush();db.add(UserRole(user_id=user.id,role_id=role.id));db.commit();print(f'Created administrator {username}.')
if __name__=='__main__':main()
