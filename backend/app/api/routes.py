from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.domain.models import Company, Account, JournalEntry, JournalLine, AuditEvent
from .schemas import CompanyCreate, AccountCreate, JournalCreate

router = APIRouter(prefix="/api/v1")

@router.get("/health")
def health():
    return {"status": "ok", "product": "PeaOps", "version": "0.1.0"}

@router.post("/companies")
def create_company(data: CompanyCreate, db: Session = Depends(get_db)):
    obj = Company(**data.model_dump())
    db.add(obj); db.flush()
    db.add(AuditEvent(action="create", entity_type="company", entity_id=str(obj.id), details=obj.name))
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "code": obj.code, "name": obj.name, "base_currency": obj.base_currency}

@router.get("/companies")
def list_companies(db: Session = Depends(get_db)):
    return [{"id": x.id, "code": x.code, "name": x.name, "base_currency": x.base_currency} for x in db.scalars(select(Company)).all()]

@router.post("/accounts")
def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    obj = Account(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "code": obj.code, "name": obj.name, "account_type": obj.account_type}

@router.get("/accounts")
def list_accounts(company_id: int, db: Session = Depends(get_db)):
    q = select(Account).where(Account.company_id == company_id).order_by(Account.code)
    return [{"id": x.id, "code": x.code, "name": x.name, "account_type": x.account_type} for x in db.scalars(q).all()]

@router.post("/journal-entries")
def create_journal(data: JournalCreate, db: Session = Depends(get_db)):
    obj = JournalEntry(company_id=data.company_id, reference=data.reference, description=data.description)
    for line in data.lines:
        if line.debit < 0 or line.credit < 0 or (line.debit and line.credit):
            raise HTTPException(400, "Each line must contain a non-negative debit OR credit")
        obj.lines.append(JournalLine(**line.model_dump()))
    try: obj.assert_balanced()
    except ValueError as exc: raise HTTPException(400, str(exc))
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "reference": obj.reference, "status": obj.status}

@router.post("/journal-entries/{entry_id}/post")
def post_journal(entry_id: int, db: Session = Depends(get_db)):
    obj = db.get(JournalEntry, entry_id)
    if not obj: raise HTTPException(404, "Journal entry not found")
    try: obj.post()
    except ValueError as exc: raise HTTPException(409, str(exc))
    db.add(AuditEvent(action="post", entity_type="journal_entry", entity_id=str(obj.id), details=obj.reference))
    db.commit()
    return {"id": obj.id, "status": obj.status, "posted_at": obj.posted_at}

@router.get("/trial-balance")
def trial_balance(company_id: int, db: Session = Depends(get_db)):
    q = (select(Account.code, Account.name, func.coalesce(func.sum(JournalLine.debit), 0), func.coalesce(func.sum(JournalLine.credit), 0))
         .join(JournalLine, JournalLine.account_id == Account.id)
         .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
         .where(Account.company_id == company_id, JournalEntry.status == "posted")
         .group_by(Account.id, Account.code, Account.name).order_by(Account.code))
    return [{"code": c, "account": n, "debit": str(d), "credit": str(cr), "balance": str(Decimal(d)-Decimal(cr))} for c,n,d,cr in db.execute(q).all()]
