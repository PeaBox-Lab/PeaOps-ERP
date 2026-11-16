from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.core.db import get_db
from app.domain.models import (
    Company, Account, JournalEntry, JournalLine, AuditEvent, Party, FiscalPeriod,
    NumberSequence, BankAccount, Invoice, InvoiceLine, Payment
)
from .schemas import (
    CompanyCreate, AccountCreate, JournalCreate, PartyCreate, FiscalPeriodCreate,
    NumberSequenceCreate, BankAccountCreate, InvoiceCreate, PaymentCreate, AllocationCreate
)

router = APIRouter(prefix="/api/v1")


def audit(db: Session, action: str, entity_type: str, entity_id: int | str, details: str = ""):
    db.add(AuditEvent(action=action, entity_type=entity_type, entity_id=str(entity_id), details=details))


def invoice_view(obj: Invoice):
    return {
        "id": obj.id, "number": obj.number, "invoice_type": obj.invoice_type,
        "party_id": obj.party_id, "invoice_date": obj.invoice_date, "due_date": obj.due_date,
        "currency": obj.currency, "subtotal": str(obj.subtotal), "tax_amount": str(obj.tax_amount),
        "total_amount": str(obj.total_amount), "paid_amount": str(obj.paid_amount),
        "outstanding": str(obj.outstanding), "status": obj.status,
    }


@router.get("/health")
def health():
    return {"status": "ok", "product": "PeaOps", "version": "0.2.0"}


@router.post("/companies")
def create_company(data: CompanyCreate, db: Session = Depends(get_db)):
    obj = Company(**data.model_dump())
    db.add(obj); db.flush(); audit(db, "create", "company", obj.id, obj.name)
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
    audit(db, "post", "journal_entry", obj.id, obj.reference); db.commit()
    return {"id": obj.id, "status": obj.status, "posted_at": obj.posted_at}


@router.get("/trial-balance")
def trial_balance(company_id: int, db: Session = Depends(get_db)):
    q = (select(Account.code, Account.name, func.coalesce(func.sum(JournalLine.debit), 0), func.coalesce(func.sum(JournalLine.credit), 0))
         .join(JournalLine, JournalLine.account_id == Account.id)
         .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
         .where(Account.company_id == company_id, JournalEntry.status == "posted")
         .group_by(Account.id, Account.code, Account.name).order_by(Account.code))
    return [{"code": c, "account": n, "debit": str(d), "credit": str(cr), "balance": str(Decimal(d)-Decimal(cr))} for c,n,d,cr in db.execute(q).all()]


@router.post("/parties")
def create_party(data: PartyCreate, db: Session = Depends(get_db)):
    obj = Party(**data.model_dump()); db.add(obj); db.flush(); audit(db, "create", data.party_type, obj.id, obj.name)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "code": obj.code, "name": obj.name, "party_type": obj.party_type, "gstin": obj.gstin}


@router.get("/parties")
def list_parties(company_id: int, party_type: str | None = None, db: Session = Depends(get_db)):
    q = select(Party).where(Party.company_id == company_id)
    if party_type: q = q.where(Party.party_type == party_type)
    q = q.order_by(Party.name)
    return [{"id": x.id, "code": x.code, "name": x.name, "party_type": x.party_type, "gstin": x.gstin, "credit_limit": str(x.credit_limit)} for x in db.scalars(q).all()]


@router.post("/fiscal-periods")
def create_fiscal_period(data: FiscalPeriodCreate, db: Session = Depends(get_db)):
    obj = FiscalPeriod(**data.model_dump())
    try: obj.validate_dates()
    except ValueError as exc: raise HTTPException(400, str(exc))
    db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "code": obj.code, "name": obj.name, "status": obj.status}


@router.get("/fiscal-periods")
def list_fiscal_periods(company_id: int, db: Session = Depends(get_db)):
    q = select(FiscalPeriod).where(FiscalPeriod.company_id == company_id).order_by(FiscalPeriod.start_date)
    return [{"id": x.id, "code": x.code, "name": x.name, "start_date": x.start_date, "end_date": x.end_date, "status": x.status} for x in db.scalars(q).all()]


@router.post("/number-sequences")
def create_number_sequence(data: NumberSequenceCreate, db: Session = Depends(get_db)):
    obj = NumberSequence(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "document_type": obj.document_type, "prefix": obj.prefix, "next_number": obj.next_number}


@router.post("/bank-accounts")
def create_bank_account(data: BankAccountCreate, db: Session = Depends(get_db)):
    obj = BankAccount(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj)
    return {"id": obj.id, "code": obj.code, "name": obj.name, "currency": obj.currency}


@router.get("/bank-accounts")
def list_bank_accounts(company_id: int, db: Session = Depends(get_db)):
    q = select(BankAccount).where(BankAccount.company_id == company_id).order_by(BankAccount.code)
    return [{"id": x.id, "code": x.code, "name": x.name, "currency": x.currency, "active": x.active} for x in db.scalars(q).all()]


def next_number(db: Session, company_id: int, document_type: str) -> str:
    seq = db.scalar(select(NumberSequence).where(NumberSequence.company_id == company_id, NumberSequence.document_type == document_type))
    if not seq: raise HTTPException(409, f"Number sequence not configured for {document_type}")
    return seq.issue()


@router.post("/invoices")
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db)):
    party = db.get(Party, data.party_id)
    expected_type = "customer" if data.invoice_type == "ar" else "supplier"
    if not party or party.company_id != data.company_id: raise HTTPException(404, "Party not found for company")
    if party.party_type != expected_type: raise HTTPException(409, f"{data.invoice_type.upper()} invoice requires a {expected_type}")
    number = data.number or next_number(db, data.company_id, f"{data.invoice_type}_invoice")
    obj = Invoice(company_id=data.company_id, party_id=data.party_id, invoice_type=data.invoice_type,
                  number=number, invoice_date=data.invoice_date, due_date=data.due_date,
                  currency=data.currency, description=data.description)
    obj.lines = [InvoiceLine(**line.model_dump()) for line in data.lines]
    try: obj.recalculate()
    except ValueError as exc: raise HTTPException(400, str(exc))
    db.add(obj); db.flush(); audit(db, "create", f"{data.invoice_type}_invoice", obj.id, obj.number)
    db.commit(); db.refresh(obj)
    return invoice_view(obj)


@router.post("/invoices/{invoice_id}/post")
def post_invoice(invoice_id: int, db: Session = Depends(get_db)):
    obj = db.scalar(select(Invoice).options(selectinload(Invoice.lines)).where(Invoice.id == invoice_id))
    if not obj: raise HTTPException(404, "Invoice not found")
    try: obj.post()
    except ValueError as exc: raise HTTPException(409, str(exc))
    audit(db, "post", f"{obj.invoice_type}_invoice", obj.id, obj.number); db.commit(); db.refresh(obj)
    return invoice_view(obj)


@router.get("/invoices")
def list_invoices(company_id: int, invoice_type: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    q = select(Invoice).where(Invoice.company_id == company_id)
    if invoice_type: q = q.where(Invoice.invoice_type == invoice_type)
    if status: q = q.where(Invoice.status == status)
    q = q.order_by(Invoice.due_date, Invoice.number)
    return [invoice_view(x) for x in db.scalars(q).all()]


@router.post("/payments")
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    party = db.get(Party, data.party_id)
    expected_type = "customer" if data.payment_type == "receipt" else "supplier"
    if not party or party.company_id != data.company_id: raise HTTPException(404, "Party not found for company")
    if party.party_type != expected_type: raise HTTPException(409, f"{data.payment_type.title()} requires a {expected_type}")
    obj = Payment(**data.model_dump(), unallocated_amount=data.amount)
    db.add(obj); db.flush(); audit(db, "post", data.payment_type, obj.id, obj.reference)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "reference": obj.reference, "amount": str(obj.amount), "unallocated_amount": str(obj.unallocated_amount), "status": obj.status}


@router.post("/payments/{payment_id}/allocate")
def allocate_payment(payment_id: int, data: AllocationCreate, db: Session = Depends(get_db)):
    payment = db.scalar(select(Payment).options(selectinload(Payment.allocations)).where(Payment.id == payment_id))
    invoice = db.get(Invoice, data.invoice_id)
    if not payment: raise HTTPException(404, "Payment not found")
    if not invoice: raise HTTPException(404, "Invoice not found")
    if payment.company_id != invoice.company_id or payment.party_id != invoice.party_id:
        raise HTTPException(409, "Payment and invoice must belong to the same company and party")
    expected_invoice = "ar" if payment.payment_type == "receipt" else "ap"
    if invoice.invoice_type != expected_invoice: raise HTTPException(409, "Payment type does not match invoice type")
    try: payment.allocate(invoice, data.amount)
    except ValueError as exc: raise HTTPException(409, str(exc))
    audit(db, "allocate", "payment", payment.id, f"invoice={invoice.number}; amount={data.amount}")
    db.commit(); db.refresh(payment); db.refresh(invoice)
    return {"payment_id": payment.id, "invoice_id": invoice.id, "allocated": str(data.amount), "payment_unallocated": str(payment.unallocated_amount), "invoice_outstanding": str(invoice.outstanding), "invoice_status": invoice.status}


@router.get("/ageing")
def ageing(company_id: int, invoice_type: str = Query(pattern="^(ar|ap)$"), as_of: date = Query(default_factory=date.today), db: Session = Depends(get_db)):
    q = select(Invoice).where(Invoice.company_id == company_id, Invoice.invoice_type == invoice_type, Invoice.status.in_(["open", "partially_paid"]))
    buckets = {"current": Decimal("0"), "1-30": Decimal("0"), "31-60": Decimal("0"), "61-90": Decimal("0"), "90+": Decimal("0")}
    items = []
    for obj in db.scalars(q).all():
        bucket = obj.ageing_bucket(as_of); buckets[bucket] += obj.outstanding
        items.append({"invoice_id": obj.id, "number": obj.number, "party_id": obj.party_id, "due_date": obj.due_date, "outstanding": str(obj.outstanding), "bucket": bucket})
    return {"company_id": company_id, "invoice_type": invoice_type, "as_of": as_of, "buckets": {k: str(v) for k,v in buckets.items()}, "items": items}
