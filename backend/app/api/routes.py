from datetime import date, datetime, timedelta
import json
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.core.db import get_db
from app.core.config import settings
from app.security.rules import hash_password, verify_password, create_access_token, normalize_permissions, create_refresh_token, hash_refresh_token
from app.security.service import permissions_for_user, require_permission
from app.security.sod import validate_role_permissions, require_distinct_actor, require_version
from app.domain.models import (
    Company, Account, JournalEntry, JournalLine, AuditEvent, Party, FiscalPeriod,
    NumberSequence, BankAccount, Invoice, InvoiceLine, Payment, Item,
    PriceList, PriceListLine, SalesQuote, SalesQuoteLine, SalesOrder, SalesOrderLine,
    PurchaseRequest, PurchaseRequestLine, RequestForQuote, RequestForQuoteLine,
    SupplierQuote, SupplierQuoteLine, PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine, Warehouse, InventoryPolicy, InventoryBalance,
    InventoryMovement, StockTransfer, StockTransferLine, IntegrationEvent, DocumentLink,
    PostingProfile, SalesDelivery, SalesDeliveryLine, SupplierInvoiceMatch,
    SavedReport, ReportRun, DataQualityFinding, User, Role, RolePermission,
    UserRole, SecurityEvent, AuthSession, ApprovalRecord
)
from .schemas import (
    CompanyCreate, AccountCreate, JournalCreate, PartyCreate, FiscalPeriodCreate,
    NumberSequenceCreate, BankAccountCreate, InvoiceCreate, PaymentCreate, AllocationCreate,
    PriceListCreate, SalesQuoteCreate, SalesOrderCreate, QuoteConversion, OrderConfirmation,
    PurchaseRequestCreate, RFQCreate, SupplierQuoteCreate, PurchaseOrderCreate,
    SupplierQuoteConversion, GoodsReceiptCreate, InventoryPolicyCreate,
    InventoryMovementCreate, StockTransferCreate, InventoryReservation, PostingProfileCreate,
    SalesDeliveryCreate, IntegratedSalesInvoiceCreate, SupplierInvoiceIntegratedCreate,
    SavedReportCreate, ReportRunCreate, UserCreate, LoginRequest, RoleCreate,
    UserRoleAssignment, RefreshRequest, LogoutRequest, ApprovalCreate, ApprovalDecision
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
    return {"status": "ok", "product": "PeaOps", "version": "0.8.1"}
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
def sales_view(obj):
    return {"id": obj.id, "number": obj.number, "customer_id": obj.customer_id,
            "status": obj.status, "currency": obj.currency, "subtotal": str(obj.subtotal),
            "discount_amount": str(obj.discount_amount), "tax_amount": str(obj.tax_amount),
            "total_amount": str(obj.total_amount)}
def ensure_customer(db: Session, company_id: int, customer_id: int):
    customer = db.get(Party, customer_id)
    if not customer or customer.company_id != company_id or customer.party_type != "customer":
        raise HTTPException(404, "Customer not found for company")
    return customer
def ensure_items(db: Session, company_id: int, item_ids: list[int]):
    found = db.scalars(select(Item).where(Item.company_id == company_id, Item.id.in_(item_ids))).all()
    if len({x.id for x in found}) != len(set(item_ids)):
        raise HTTPException(404, "One or more items were not found for company")
@router.post("/price-lists")
def create_price_list(data: PriceListCreate, db: Session = Depends(get_db)):
    from app.domain.sales_rules import validate_validity
    try: validate_validity(data.valid_from, data.valid_until)
    except ValueError as exc: raise HTTPException(400, str(exc))
    ensure_items(db, data.company_id, [x.item_id for x in data.lines])
    obj = PriceList(company_id=data.company_id, code=data.code, name=data.name, currency=data.currency,
                    valid_from=data.valid_from, valid_until=data.valid_until)
    obj.lines = [PriceListLine(**x.model_dump()) for x in data.lines]
    db.add(obj); db.flush(); audit(db, "create", "price_list", obj.id, obj.code)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "code": obj.code, "name": obj.name, "currency": obj.currency, "active": obj.active}
@router.get("/price-lists")
def list_price_lists(company_id: int, active_on: date | None = None, db: Session = Depends(get_db)):
    q = select(PriceList).where(PriceList.company_id == company_id)
    if active_on: q = q.where(PriceList.active == True, PriceList.valid_from <= active_on, PriceList.valid_until >= active_on)
    return [{"id": x.id, "code": x.code, "name": x.name, "currency": x.currency,
             "valid_from": x.valid_from, "valid_until": x.valid_until, "active": x.active} for x in db.scalars(q.order_by(PriceList.code)).all()]
@router.post("/sales-quotes")
def create_sales_quote(data: SalesQuoteCreate, db: Session = Depends(get_db)):
    from app.domain.sales_rules import validate_validity
    ensure_customer(db, data.company_id, data.customer_id)
    ensure_items(db, data.company_id, [x.item_id for x in data.lines])
    try: validate_validity(data.quote_date, data.valid_until)
    except ValueError as exc: raise HTTPException(400, str(exc))
    number = data.number or next_number(db, data.company_id, "sales_quote")
    obj = SalesQuote(company_id=data.company_id, customer_id=data.customer_id, number=number,
                     quote_date=data.quote_date, valid_until=data.valid_until, currency=data.currency, notes=data.notes)
    obj.lines = [SalesQuoteLine(**x.model_dump()) for x in data.lines]
    try: obj.recalculate()
    except ValueError as exc: raise HTTPException(400, str(exc))
    db.add(obj); db.flush(); audit(db, "create", "sales_quote", obj.id, obj.number)
    db.commit(); db.refresh(obj); return sales_view(obj)
@router.post("/sales-quotes/{quote_id}/send")
def send_sales_quote(quote_id: int, db: Session = Depends(get_db)):
    obj = db.scalar(select(SalesQuote).options(selectinload(SalesQuote.lines)).where(SalesQuote.id == quote_id))
    if not obj: raise HTTPException(404, "Sales quotation not found")
    try: obj.send()
    except ValueError as exc: raise HTTPException(409, str(exc))
    audit(db, "send", "sales_quote", obj.id, obj.number); db.commit(); return sales_view(obj)
@router.get("/sales-quotes")
def list_sales_quotes(company_id: int, status: str | None = None, db: Session = Depends(get_db)):
    q = select(SalesQuote).where(SalesQuote.company_id == company_id)
    if status: q = q.where(SalesQuote.status == status)
    return [sales_view(x) | {"quote_date": x.quote_date, "valid_until": x.valid_until} for x in db.scalars(q.order_by(SalesQuote.quote_date.desc())).all()]
@router.post("/sales-orders")
def create_sales_order(data: SalesOrderCreate, db: Session = Depends(get_db)):
    from app.domain.sales_rules import validate_delivery_promise
    ensure_customer(db, data.company_id, data.customer_id)
    ensure_items(db, data.company_id, [x.item_id for x in data.lines])
    try: validate_delivery_promise(data.order_date, data.promised_date)
    except ValueError as exc: raise HTTPException(400, str(exc))
    number = data.number or next_number(db, data.company_id, "sales_order")
    obj = SalesOrder(company_id=data.company_id, customer_id=data.customer_id, number=number,
                     order_date=data.order_date, promised_date=data.promised_date, currency=data.currency)
    obj.lines = [SalesOrderLine(**x.model_dump()) for x in data.lines]
    try: obj.recalculate()
    except ValueError as exc: raise HTTPException(400, str(exc))
    db.add(obj); db.flush(); audit(db, "create", "sales_order", obj.id, obj.number)
    db.commit(); db.refresh(obj); return sales_view(obj)
@router.post("/sales-quotes/{quote_id}/convert")
def convert_quote(quote_id: int, data: QuoteConversion, db: Session = Depends(get_db)):
    from app.domain.sales_rules import validate_delivery_promise
    quote = db.scalar(select(SalesQuote).options(selectinload(SalesQuote.lines)).where(SalesQuote.id == quote_id))
    if not quote: raise HTTPException(404, "Sales quotation not found")
    if quote.status not in {"sent", "accepted"}: raise HTTPException(409, "Only sent or accepted quotations may be converted")
    try: validate_delivery_promise(data.order_date, data.promised_date)
    except ValueError as exc: raise HTTPException(400, str(exc))
    number = data.order_number or next_number(db, quote.company_id, "sales_order")
    order = SalesOrder(company_id=quote.company_id, customer_id=quote.customer_id, quote_id=quote.id,
                       number=number, order_date=data.order_date, promised_date=data.promised_date, currency=quote.currency)
    order.lines = [SalesOrderLine(item_id=x.item_id, description=x.description, quantity=x.quantity,
                                  unit_price=x.unit_price, discount_percent=x.discount_percent, tax_rate=x.tax_rate) for x in quote.lines]
    order.recalculate(); quote.status = "converted"; db.add(order); db.flush()
    audit(db, "convert", "sales_quote", quote.id, f"order={order.number}"); db.commit(); db.refresh(order)
    return sales_view(order)
@router.post("/sales-orders/{order_id}/confirm")
def confirm_sales_order(order_id: int, data: OrderConfirmation, db: Session = Depends(get_db)):
    from app.domain.sales_rules import check_credit_limit
    order = db.scalar(select(SalesOrder).options(selectinload(SalesOrder.lines)).where(SalesOrder.id == order_id))
    if not order: raise HTTPException(404, "Sales order not found")
    if order.status != "draft": raise HTTPException(409, "Only draft sales orders may be confirmed")
    customer = db.get(Party, order.customer_id); order.recalculate()
    receivables = db.scalar(select(func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0)).where(
        Invoice.company_id == order.company_id, Invoice.party_id == order.customer_id,
        Invoice.invoice_type == "ar", Invoice.status.in_(["open", "partially_paid"]))) or Decimal("0")
    pending = db.scalar(select(func.coalesce(func.sum(SalesOrder.total_amount), 0)).where(
        SalesOrder.company_id == order.company_id, SalesOrder.customer_id == order.customer_id,
        SalesOrder.status == "confirmed", SalesOrder.id != order.id)) or Decimal("0")
    try: exposure = check_credit_limit(customer.credit_limit, receivables, pending, order.total_amount)
    except ValueError as exc:
        if not data.override_credit: raise HTTPException(409, str(exc))
        if not data.override_reason.strip(): raise HTTPException(400, "Credit override reason is required")
        exposure = Decimal(receivables) + Decimal(pending) + Decimal(order.total_amount)
        audit(db, "credit_override", "sales_order", order.id, data.override_reason)
    order.status = "confirmed"; audit(db, "confirm", "sales_order", order.id, f"exposure={exposure}")
    db.commit(); return sales_view(order) | {"credit_exposure": str(exposure)}
@router.post("/sales-orders/{order_id}/invoice")
def invoice_sales_order(order_id: int, db: Session = Depends(get_db)):
    order = db.scalar(select(SalesOrder).options(selectinload(SalesOrder.lines)).where(SalesOrder.id == order_id))
    if not order: raise HTTPException(404, "Sales order not found")
    if order.status != "confirmed": raise HTTPException(409, "Only confirmed sales orders may be invoiced")
    number = next_number(db, order.company_id, "ar_invoice")
    invoice = Invoice(company_id=order.company_id, party_id=order.customer_id, invoice_type="ar", number=number,
                      invoice_date=date.today(), due_date=date.today(), currency=order.currency,
                      description=f"Sales order {order.number}")
    invoice.lines = [InvoiceLine(description=x.description, quantity=x.quantity,
                                 unit_price=(Decimal(x.unit_price) * (Decimal('100') - Decimal(x.discount_percent)) / Decimal('100')),
                                 tax_rate=x.tax_rate) for x in order.lines]
    invoice.recalculate(); db.add(invoice); db.flush(); order.status = "invoiced"
    audit(db, "invoice", "sales_order", order.id, f"invoice={invoice.number}"); db.commit(); db.refresh(invoice)
    return invoice_view(invoice)
@router.get("/sales-orders")
def list_sales_orders(company_id: int, status: str | None = None, db: Session = Depends(get_db)):
    q = select(SalesOrder).where(SalesOrder.company_id == company_id)
    if status: q = q.where(SalesOrder.status == status)
    return [sales_view(x) | {"order_date": x.order_date, "promised_date": x.promised_date} for x in db.scalars(q.order_by(SalesOrder.order_date.desc())).all()]



def procurement_view(obj):
    return {"id": obj.id, "number": obj.number, "status": obj.status, "currency": obj.currency,
            "subtotal": str(obj.subtotal), "discount_amount": str(obj.discount_amount),
            "tax_amount": str(obj.tax_amount), "total_amount": str(obj.total_amount)}


def ensure_supplier(db: Session, company_id: int, supplier_id: int):
    supplier = db.get(Party, supplier_id)
    if not supplier or supplier.company_id != company_id or supplier.party_type != "supplier":
        raise HTTPException(404, "Supplier not found for company")
    return supplier


@router.post("/purchase-requests")
def create_purchase_request(data: PurchaseRequestCreate, db: Session = Depends(get_db)):
    from app.domain.procurement_rules import validate_required_date
    ensure_items(db, data.company_id, [x.item_id for x in data.lines])
    try: validate_required_date(data.request_date, data.required_date)
    except ValueError as exc: raise HTTPException(400, str(exc))
    number = data.number or next_number(db, data.company_id, "purchase_request")
    obj = PurchaseRequest(company_id=data.company_id, number=number, request_date=data.request_date,
                          required_date=data.required_date, requester=data.requester,
                          department=data.department, justification=data.justification)
    obj.lines = [PurchaseRequestLine(**x.model_dump()) for x in data.lines]
    db.add(obj); db.flush(); audit(db, "create", "purchase_request", obj.id, obj.number)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "number": obj.number, "status": obj.status, "required_date": obj.required_date}


@router.post("/purchase-requests/{request_id}/submit")
def submit_purchase_request(request_id: int, db: Session = Depends(get_db)):
    obj = db.scalar(select(PurchaseRequest).options(selectinload(PurchaseRequest.lines)).where(PurchaseRequest.id == request_id))
    if not obj: raise HTTPException(404, "Purchase request not found")
    try: obj.submit()
    except ValueError as exc: raise HTTPException(409, str(exc))
    audit(db, "submit", "purchase_request", obj.id, obj.number); db.commit()
    return {"id": obj.id, "number": obj.number, "status": obj.status}


@router.get("/purchase-requests")
def list_purchase_requests(company_id: int, status: str | None = None, db: Session = Depends(get_db)):
    q = select(PurchaseRequest).where(PurchaseRequest.company_id == company_id)
    if status: q = q.where(PurchaseRequest.status == status)
    return [{"id": x.id, "number": x.number, "request_date": x.request_date, "required_date": x.required_date,
             "requester": x.requester, "department": x.department, "status": x.status} for x in db.scalars(q.order_by(PurchaseRequest.request_date.desc())).all()]


@router.post("/rfqs")
def create_rfq(data: RFQCreate, db: Session = Depends(get_db)):
    from app.domain.procurement_rules import validate_quote_window
    ensure_items(db, data.company_id, [x.item_id for x in data.lines])
    if data.purchase_request_id:
        req = db.get(PurchaseRequest, data.purchase_request_id)
        if not req or req.company_id != data.company_id: raise HTTPException(404, "Purchase request not found for company")
    try: validate_quote_window(data.rfq_date, data.response_due)
    except ValueError as exc: raise HTTPException(400, str(exc))
    number = data.number or next_number(db, data.company_id, "rfq")
    obj = RequestForQuote(company_id=data.company_id, purchase_request_id=data.purchase_request_id,
                          number=number, rfq_date=data.rfq_date, response_due=data.response_due,
                          currency=data.currency, notes=data.notes)
    obj.lines = [RequestForQuoteLine(**x.model_dump()) for x in data.lines]
    db.add(obj); db.flush(); audit(db, "create", "rfq", obj.id, obj.number)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "number": obj.number, "status": obj.status, "response_due": obj.response_due}


@router.post("/rfqs/{rfq_id}/issue")
def issue_rfq(rfq_id: int, db: Session = Depends(get_db)):
    obj = db.scalar(select(RequestForQuote).options(selectinload(RequestForQuote.lines)).where(RequestForQuote.id == rfq_id))
    if not obj: raise HTTPException(404, "RFQ not found")
    try: obj.issue()
    except ValueError as exc: raise HTTPException(409, str(exc))
    audit(db, "issue", "rfq", obj.id, obj.number); db.commit()
    return {"id": obj.id, "number": obj.number, "status": obj.status}


@router.get("/rfqs")
def list_rfqs(company_id: int, status: str | None = None, db: Session = Depends(get_db)):
    q = select(RequestForQuote).where(RequestForQuote.company_id == company_id)
    if status: q = q.where(RequestForQuote.status == status)
    return [{"id": x.id, "number": x.number, "rfq_date": x.rfq_date, "response_due": x.response_due,
             "currency": x.currency, "status": x.status} for x in db.scalars(q.order_by(RequestForQuote.rfq_date.desc())).all()]


@router.post("/supplier-quotes")
def create_supplier_quote(data: SupplierQuoteCreate, db: Session = Depends(get_db)):
    from app.domain.sales_rules import validate_validity, validate_delivery_promise
    ensure_supplier(db, data.company_id, data.supplier_id)
    ensure_items(db, data.company_id, [x.item_id for x in data.lines])
    rfq = db.get(RequestForQuote, data.rfq_id)
    if not rfq or rfq.company_id != data.company_id: raise HTTPException(404, "RFQ not found for company")
    if rfq.status != "issued": raise HTTPException(409, "Supplier quotations require an issued RFQ")
    try:
        validate_validity(data.quote_date, data.valid_until)
        validate_delivery_promise(data.quote_date, data.promised_date)
    except ValueError as exc: raise HTTPException(400, str(exc))
    obj = SupplierQuote(company_id=data.company_id, rfq_id=data.rfq_id, supplier_id=data.supplier_id,
                        number=data.number, quote_date=data.quote_date, valid_until=data.valid_until,
                        promised_date=data.promised_date, currency=data.currency)
    obj.lines = [SupplierQuoteLine(**x.model_dump()) for x in data.lines]
    try: obj.recalculate()
    except ValueError as exc: raise HTTPException(400, str(exc))
    db.add(obj); db.flush(); audit(db, "receive", "supplier_quote", obj.id, obj.number)
    db.commit(); db.refresh(obj); return procurement_view(obj) | {"supplier_id": obj.supplier_id, "rfq_id": obj.rfq_id}


@router.get("/rfqs/{rfq_id}/comparison")
def compare_supplier_quotes(rfq_id: int, db: Session = Depends(get_db)):
    from app.domain.procurement_rules import choose_best_quote
    rfq = db.get(RequestForQuote, rfq_id)
    if not rfq: raise HTTPException(404, "RFQ not found")
    quotes = db.scalars(select(SupplierQuote).where(SupplierQuote.rfq_id == rfq_id, SupplierQuote.status == "received")).all()
    try: best_id, _, _ = choose_best_quote([(x.id, x.total_amount, x.promised_date) for x in quotes])
    except ValueError as exc: raise HTTPException(409, str(exc))
    return {"rfq_id": rfq_id, "recommended_quote_id": best_id, "basis": "lowest total, then earliest promise",
            "quotes": [{"id": x.id, "number": x.number, "supplier_id": x.supplier_id,
                        "promised_date": x.promised_date, "total_amount": str(x.total_amount),
                        "recommended": x.id == best_id} for x in sorted(quotes, key=lambda q: (q.total_amount, q.promised_date or date.max))]}


@router.post("/purchase-orders")
def create_purchase_order(data: PurchaseOrderCreate, db: Session = Depends(get_db)):
    from app.domain.sales_rules import validate_delivery_promise
    ensure_supplier(db, data.company_id, data.supplier_id)
    ensure_items(db, data.company_id, [x.item_id for x in data.lines])
    try: validate_delivery_promise(data.order_date, data.promised_date)
    except ValueError as exc: raise HTTPException(400, str(exc))
    number = data.number or next_number(db, data.company_id, "purchase_order")
    obj = PurchaseOrder(company_id=data.company_id, supplier_id=data.supplier_id, number=number,
                        order_date=data.order_date, promised_date=data.promised_date, currency=data.currency)
    obj.lines = [PurchaseOrderLine(**x.model_dump()) for x in data.lines]
    try: obj.recalculate()
    except ValueError as exc: raise HTTPException(400, str(exc))
    db.add(obj); db.flush(); audit(db, "create", "purchase_order", obj.id, obj.number)
    db.commit(); db.refresh(obj); return procurement_view(obj)


@router.post("/supplier-quotes/{quote_id}/convert")
def convert_supplier_quote(quote_id: int, data: SupplierQuoteConversion, db: Session = Depends(get_db)):
    from app.domain.sales_rules import validate_delivery_promise
    quote = db.scalar(select(SupplierQuote).options(selectinload(SupplierQuote.lines)).where(SupplierQuote.id == quote_id))
    if not quote: raise HTTPException(404, "Supplier quotation not found")
    if quote.status != "received": raise HTTPException(409, "Only received supplier quotations may be converted")
    promised = data.promised_date or quote.promised_date
    try: validate_delivery_promise(data.order_date, promised)
    except ValueError as exc: raise HTTPException(400, str(exc))
    number = data.order_number or next_number(db, quote.company_id, "purchase_order")
    order = PurchaseOrder(company_id=quote.company_id, supplier_id=quote.supplier_id, supplier_quote_id=quote.id,
                          number=number, order_date=data.order_date, promised_date=promised, currency=quote.currency)
    order.lines = [PurchaseOrderLine(item_id=x.item_id, description=x.description, quantity=x.quantity,
                                     unit_price=x.unit_price, discount_percent=x.discount_percent, tax_rate=x.tax_rate)
                   for x in quote.lines]
    order.recalculate(); quote.status = "converted"; db.add(order); db.flush()
    audit(db, "convert", "supplier_quote", quote.id, f"purchase_order={order.number}")
    db.commit(); db.refresh(order); return procurement_view(order)


@router.post("/purchase-orders/{order_id}/confirm")
def confirm_purchase_order(order_id: int, db: Session = Depends(get_db)):
    obj = db.scalar(select(PurchaseOrder).options(selectinload(PurchaseOrder.lines)).where(PurchaseOrder.id == order_id))
    if not obj: raise HTTPException(404, "Purchase order not found")
    try: obj.confirm()
    except ValueError as exc: raise HTTPException(409, str(exc))
    audit(db, "confirm", "purchase_order", obj.id, obj.number); db.commit(); return procurement_view(obj)


@router.get("/purchase-orders")
def list_purchase_orders(company_id: int, status: str | None = None, db: Session = Depends(get_db)):
    q = select(PurchaseOrder).where(PurchaseOrder.company_id == company_id)
    if status: q = q.where(PurchaseOrder.status == status)
    return [procurement_view(x) | {"supplier_id": x.supplier_id, "order_date": x.order_date,
                                   "promised_date": x.promised_date} for x in db.scalars(q.order_by(PurchaseOrder.order_date.desc())).all()]


@router.post("/purchase-orders/{order_id}/receipts")
def create_goods_receipt(order_id: int, data: GoodsReceiptCreate, db: Session = Depends(get_db)):
    from app.domain.procurement_rules import apply_receipt
    order = db.scalar(select(PurchaseOrder).options(selectinload(PurchaseOrder.lines)).where(PurchaseOrder.id == order_id))
    if not order: raise HTTPException(404, "Purchase order not found")
    if order.status not in {"confirmed", "partially_received"}: raise HTTPException(409, "Purchase order is not open for receipt")
    if data.warehouse_id:
        warehouse = db.get(Warehouse, data.warehouse_id)
        if not warehouse or warehouse.company_id != order.company_id: raise HTTPException(404, "Warehouse not found for company")
    by_id = {x.id: x for x in order.lines}; receipt_lines=[]
    try:
        for incoming in data.lines:
            line = by_id.get(incoming.purchase_order_line_id)
            if not line: raise HTTPException(404, "Purchase order line not found")
            line.received_quantity, _, _ = apply_receipt(line.quantity, line.received_quantity, incoming.quantity)
            receipt_lines.append(GoodsReceiptLine(purchase_order_line_id=line.id, item_id=line.item_id, quantity=incoming.quantity))
    except ValueError as exc: raise HTTPException(409, str(exc))
    all_received = all(Decimal(x.received_quantity) == Decimal(x.quantity) for x in order.lines)
    order.status = "received" if all_received else "partially_received"
    number = data.number or next_number(db, order.company_id, "goods_receipt")
    receipt = GoodsReceipt(company_id=order.company_id, purchase_order_id=order.id, number=number,
                           receipt_date=data.receipt_date, warehouse_id=data.warehouse_id, notes=data.notes,
                           lines=receipt_lines)
    db.add(receipt); db.flush(); audit(db, "receive", "purchase_order", order.id, f"receipt={receipt.number}")
    db.commit(); db.refresh(receipt)
    return {"id": receipt.id, "number": receipt.number, "purchase_order_id": order.id,
            "order_status": order.status, "receipt_date": receipt.receipt_date}



def ensure_inventory_entities(db: Session, company_id: int, item_id: int, warehouse_id: int):
    item = db.get(Item, item_id); warehouse = db.get(Warehouse, warehouse_id)
    if not item or item.company_id != company_id: raise HTTPException(404, "Item not found for company")
    if not warehouse or warehouse.company_id != company_id: raise HTTPException(404, "Warehouse not found for company")
    return item, warehouse


def get_inventory_policy(db: Session, company_id: int, item_id: int, warehouse_id: int):
    return db.scalar(select(InventoryPolicy).where(InventoryPolicy.company_id == company_id,
        InventoryPolicy.item_id == item_id, InventoryPolicy.warehouse_id == warehouse_id))


def get_inventory_balance(db: Session, company_id: int, item_id: int, warehouse_id: int):
    balance = db.scalar(select(InventoryBalance).where(InventoryBalance.company_id == company_id,
        InventoryBalance.item_id == item_id, InventoryBalance.warehouse_id == warehouse_id))
    if not balance:
        balance = InventoryBalance(company_id=company_id, item_id=item_id, warehouse_id=warehouse_id)
        db.add(balance); db.flush()
    return balance


@router.post("/inventory/policies")
def create_inventory_policy(data: InventoryPolicyCreate, db: Session = Depends(get_db)):
    ensure_inventory_entities(db, data.company_id, data.item_id, data.warehouse_id)
    existing = get_inventory_policy(db, data.company_id, data.item_id, data.warehouse_id)
    if existing: raise HTTPException(409, "Inventory policy already exists for item and warehouse")
    obj = InventoryPolicy(**data.model_dump()); db.add(obj); db.flush()
    audit(db, "create", "inventory_policy", obj.id, f"item={obj.item_id}; warehouse={obj.warehouse_id}")
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "item_id": obj.item_id, "warehouse_id": obj.warehouse_id,
            "tracking_mode": obj.tracking_mode, "reorder_point": str(obj.reorder_point),
            "reorder_quantity": str(obj.reorder_quantity), "allow_negative": obj.allow_negative}


@router.post("/inventory/movements")
def create_inventory_movement(data: InventoryMovementCreate, db: Session = Depends(get_db)):
    from app.domain.inventory_rules import apply_movement, signed_quantity, weighted_average, issue_value, validate_tracking
    ensure_inventory_entities(db, data.company_id, data.item_id, data.warehouse_id)
    policy = get_inventory_policy(db, data.company_id, data.item_id, data.warehouse_id)
    tracking = policy.tracking_mode if policy else "none"; allow_negative = policy.allow_negative if policy else False
    balance = get_inventory_balance(db, data.company_id, data.item_id, data.warehouse_id)
    try:
        validate_tracking(tracking, data.quantity, data.lot_number, data.serial_number)
        new_on_hand = apply_movement(balance.on_hand_quantity, data.movement_type, data.quantity, allow_negative)
        if data.movement_type in {"opening", "receipt", "adjustment_in"}:
            cost = data.unit_cost if data.unit_cost is not None else balance.average_cost
            _, new_average, new_value = weighted_average(balance.on_hand_quantity, balance.average_cost, data.quantity, cost)
            movement_value = Decimal(data.quantity) * Decimal(cost); balance.average_cost = new_average; balance.inventory_value = new_value
        else:
            movement_value = issue_value(data.quantity, balance.average_cost)
            balance.inventory_value = max(Decimal(balance.inventory_value) - movement_value, Decimal("0"))
        balance.on_hand_quantity = new_on_hand
    except ValueError as exc: raise HTTPException(409, str(exc))
    obj = InventoryMovement(**data.model_dump(), signed_quantity=signed_quantity(data.movement_type, data.quantity),
                            unit_cost=data.unit_cost if data.unit_cost is not None else balance.average_cost,
                            movement_value=movement_value)
    db.add(obj); db.flush(); audit(db, "post", "inventory_movement", obj.id, f"type={obj.movement_type}; qty={obj.quantity}")
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "movement_type": obj.movement_type, "quantity": str(obj.quantity),
            "on_hand": str(balance.on_hand_quantity), "average_cost": str(balance.average_cost),
            "inventory_value": str(balance.inventory_value)}


@router.get("/inventory/balances")
def list_inventory_balances(company_id: int, warehouse_id: int | None = None, item_id: int | None = None, db: Session = Depends(get_db)):
    from app.domain.inventory_rules import reorder_status
    q = select(InventoryBalance).where(InventoryBalance.company_id == company_id)
    if warehouse_id: q = q.where(InventoryBalance.warehouse_id == warehouse_id)
    if item_id: q = q.where(InventoryBalance.item_id == item_id)
    result=[]
    for x in db.scalars(q.order_by(InventoryBalance.warehouse_id, InventoryBalance.item_id)).all():
        policy = get_inventory_policy(db, company_id, x.item_id, x.warehouse_id)
        point = policy.reorder_point if policy else Decimal("0"); qty = policy.reorder_quantity if policy else Decimal("0")
        available, needs, suggested = reorder_status(x.on_hand_quantity, x.reserved_quantity, point, qty)
        result.append({"item_id": x.item_id, "warehouse_id": x.warehouse_id, "on_hand": str(x.on_hand_quantity),
                       "reserved": str(x.reserved_quantity), "available": str(available),
                       "average_cost": str(x.average_cost), "inventory_value": str(x.inventory_value),
                       "needs_reorder": needs, "suggested_reorder": str(suggested)})
    return result


@router.get("/inventory/ledger")
def inventory_ledger(company_id: int, item_id: int | None = None, warehouse_id: int | None = None, db: Session = Depends(get_db)):
    q = select(InventoryMovement).where(InventoryMovement.company_id == company_id)
    if item_id: q = q.where(InventoryMovement.item_id == item_id)
    if warehouse_id: q = q.where(InventoryMovement.warehouse_id == warehouse_id)
    return [{"id": x.id, "movement_date": x.movement_date, "item_id": x.item_id,
             "warehouse_id": x.warehouse_id, "movement_type": x.movement_type,
             "quantity": str(x.quantity), "signed_quantity": str(x.signed_quantity),
             "unit_cost": str(x.unit_cost), "movement_value": str(x.movement_value),
             "reference_type": x.reference_type, "reference_id": x.reference_id,
             "lot_number": x.lot_number, "serial_number": x.serial_number}
            for x in db.scalars(q.order_by(InventoryMovement.movement_date, InventoryMovement.id)).all()]


@router.post("/inventory/reservations")
def reserve_inventory(data: InventoryReservation, db: Session = Depends(get_db)):
    ensure_inventory_entities(db, data.company_id, data.item_id, data.warehouse_id)
    balance = get_inventory_balance(db, data.company_id, data.item_id, data.warehouse_id)
    available = Decimal(balance.on_hand_quantity) - Decimal(balance.reserved_quantity)
    if data.quantity > available: raise HTTPException(409, "Reservation exceeds available stock")
    balance.reserved_quantity = Decimal(balance.reserved_quantity) + data.quantity
    audit(db, "reserve", "inventory_balance", balance.id, f"quantity={data.quantity}")
    db.commit()
    return {"item_id": data.item_id, "warehouse_id": data.warehouse_id,
            "reserved": str(balance.reserved_quantity), "available": str(Decimal(balance.on_hand_quantity)-Decimal(balance.reserved_quantity))}


@router.post("/stock-transfers")
def create_stock_transfer(data: StockTransferCreate, db: Session = Depends(get_db)):
    if data.source_warehouse_id == data.destination_warehouse_id: raise HTTPException(400, "Transfer warehouses must differ")
    for item_id in {x.item_id for x in data.lines}:
        ensure_inventory_entities(db, data.company_id, item_id, data.source_warehouse_id)
        ensure_inventory_entities(db, data.company_id, item_id, data.destination_warehouse_id)
    number = data.number or next_number(db, data.company_id, "stock_transfer")
    obj = StockTransfer(company_id=data.company_id, number=number, transfer_date=data.transfer_date,
                        source_warehouse_id=data.source_warehouse_id, destination_warehouse_id=data.destination_warehouse_id,
                        notes=data.notes, lines=[StockTransferLine(**x.model_dump()) for x in data.lines])
    db.add(obj); db.flush(); audit(db, "create", "stock_transfer", obj.id, obj.number)
    db.commit(); db.refresh(obj)
    return {"id": obj.id, "number": obj.number, "status": obj.status}


@router.post("/stock-transfers/{transfer_id}/post")
def post_stock_transfer(transfer_id: int, db: Session = Depends(get_db)):
    from app.domain.inventory_rules import apply_movement, issue_value, validate_tracking
    obj = db.scalar(select(StockTransfer).options(selectinload(StockTransfer.lines)).where(StockTransfer.id == transfer_id))
    if not obj: raise HTTPException(404, "Stock transfer not found")
    if obj.status != "draft": raise HTTPException(409, "Only draft transfers may be posted")
    prepared=[]
    try:
        for line in obj.lines:
            source = get_inventory_balance(db, obj.company_id, line.item_id, obj.source_warehouse_id)
            destination = get_inventory_balance(db, obj.company_id, line.item_id, obj.destination_warehouse_id)
            source_policy = get_inventory_policy(db, obj.company_id, line.item_id, obj.source_warehouse_id)
            dest_policy = get_inventory_policy(db, obj.company_id, line.item_id, obj.destination_warehouse_id)
            validate_tracking(source_policy.tracking_mode if source_policy else "none", line.quantity, line.lot_number, line.serial_number)
            validate_tracking(dest_policy.tracking_mode if dest_policy else "none", line.quantity, line.lot_number, line.serial_number)
            source_after = apply_movement(source.on_hand_quantity, "transfer_out", line.quantity, source_policy.allow_negative if source_policy else False)
            destination_after = apply_movement(destination.on_hand_quantity, "transfer_in", line.quantity, True)
            value = issue_value(line.quantity, source.average_cost)
            prepared.append((line, source, destination, source_after, destination_after, value))
        for line, source, destination, source_after, destination_after, value in prepared:
            source.on_hand_quantity=source_after; source.inventory_value=max(Decimal(source.inventory_value)-value,Decimal("0"))
            old_dest_qty=Decimal(destination.on_hand_quantity); old_dest_val=Decimal(destination.inventory_value)
            destination.on_hand_quantity=destination_after; destination.inventory_value=old_dest_val+value
            destination.average_cost=((destination.inventory_value/destination.on_hand_quantity).quantize(Decimal("0.01")) if destination.on_hand_quantity else Decimal("0"))
            for movement_type, warehouse_id, signed in [("transfer_out",obj.source_warehouse_id,-Decimal(line.quantity)),("transfer_in",obj.destination_warehouse_id,Decimal(line.quantity))]:
                db.add(InventoryMovement(company_id=obj.company_id,item_id=line.item_id,warehouse_id=warehouse_id,
                    movement_type=movement_type,movement_date=obj.transfer_date,quantity=line.quantity,signed_quantity=signed,
                    unit_cost=source.average_cost,movement_value=value,reference_type="stock_transfer",reference_id=str(obj.id),
                    lot_number=line.lot_number,serial_number=line.serial_number,notes=obj.notes))
        obj.status="posted"; audit(db,"post","stock_transfer",obj.id,obj.number); db.commit()
    except ValueError as exc: raise HTTPException(409, str(exc))
    return {"id": obj.id, "number": obj.number, "status": obj.status}


@router.get("/inventory/reorder-alerts")
def reorder_alerts(company_id: int, db: Session = Depends(get_db)):
    from app.domain.inventory_rules import reorder_status
    policies = db.scalars(select(InventoryPolicy).where(InventoryPolicy.company_id == company_id, InventoryPolicy.reorder_quantity > 0)).all()
    alerts=[]
    for policy in policies:
        balance=get_inventory_balance(db, company_id, policy.item_id, policy.warehouse_id)
        available, needs, suggested=reorder_status(balance.on_hand_quantity,balance.reserved_quantity,policy.reorder_point,policy.reorder_quantity)
        if needs: alerts.append({"item_id":policy.item_id,"warehouse_id":policy.warehouse_id,"available":str(available),
                                 "reorder_point":str(policy.reorder_point),"suggested_quantity":str(suggested)})
    return alerts



def integration_event(db: Session, company_id: int, key: str, process: str, source_type: str, source_id: int):
    from app.domain.integration_rules import require_idempotency_key
    key=require_idempotency_key(key)
    existing=db.scalar(select(IntegrationEvent).where(IntegrationEvent.company_id==company_id,IntegrationEvent.idempotency_key==key))
    if existing:
        if existing.status=="completed": return existing, True
        raise HTTPException(409,"Integration operation is already processing or failed")
    event=IntegrationEvent(company_id=company_id,idempotency_key=key,process_type=process,source_type=source_type,source_id=str(source_id))
    db.add(event);db.flush();return event,False


def link_documents(db: Session, company_id: int, source_type: str, source_id: int, target_type: str, target_id: int, relationship: str):
    db.add(DocumentLink(company_id=company_id,source_type=source_type,source_id=str(source_id),target_type=target_type,target_id=str(target_id),relationship=relationship))


def complete_event(event: IntegrationEvent, result_type: str, result_id: int, details: str=""):
    event.status="completed";event.result_type=result_type;event.result_id=str(result_id);event.details=details;event.completed_at=datetime.utcnow()


@router.post("/integration/posting-profiles")
def create_posting_profile(data: PostingProfileCreate, db: Session = Depends(get_db)):
    account_ids=[x for x in [data.receivable_account_id,data.payable_account_id,data.revenue_account_id,data.inventory_account_id,data.cogs_account_id,data.expense_account_id] if x]
    accounts=db.scalars(select(Account).where(Account.company_id==data.company_id,Account.id.in_(account_ids))).all() if account_ids else []
    if len(accounts)!=len(set(account_ids)): raise HTTPException(404,"One or more posting accounts were not found for company")
    obj=PostingProfile(**data.model_dump());db.add(obj);db.commit();db.refresh(obj)
    return {"id":obj.id,"profile_type":obj.profile_type}


@router.post("/sales-orders/{order_id}/deliver")
def deliver_sales_order(order_id: int, data: SalesDeliveryCreate, db: Session = Depends(get_db)):
    from app.domain.integration_rules import validate_delivery_quantities
    from app.domain.inventory_rules import apply_movement,issue_value
    order=db.scalar(select(SalesOrder).options(selectinload(SalesOrder.lines)).where(SalesOrder.id==order_id))
    if not order: raise HTTPException(404,"Sales order not found")
    if order.status not in {"confirmed","partially_delivered"}: raise HTTPException(409,"Sales order is not open for delivery")
    warehouse=db.get(Warehouse,data.warehouse_id)
    if not warehouse or warehouse.company_id!=order.company_id: raise HTTPException(404,"Warehouse not found for company")
    event,replayed=integration_event(db,order.company_id,data.idempotency_key,"sales_delivery","sales_order",order.id)
    if replayed: return {"replayed":True,"event_id":event.id,"result_type":event.result_type,"result_id":event.result_id}
    order_lines={x.id:x for x in order.lines};prepared=[];delivery_lines=[]
    try:
        for incoming in data.lines:
            line=order_lines.get(incoming.sales_order_line_id)
            if not line: raise HTTPException(404,"Sales order line not found")
            delivered=db.scalar(select(func.coalesce(func.sum(SalesDeliveryLine.quantity),0)).join(SalesDelivery,SalesDelivery.id==SalesDeliveryLine.delivery_id).where(SalesDelivery.sales_order_id==order.id,SalesDelivery.status=="posted",SalesDeliveryLine.sales_order_line_id==line.id)) or Decimal("0")
            updated,remaining,_=validate_delivery_quantities(line.quantity,delivered,incoming.quantity)
            balance=get_inventory_balance(db,order.company_id,line.item_id,data.warehouse_id)
            policy=get_inventory_policy(db,order.company_id,line.item_id,data.warehouse_id)
            new_on_hand=apply_movement(balance.on_hand_quantity,"issue",incoming.quantity,policy.allow_negative if policy else False)
            value=issue_value(incoming.quantity,balance.average_cost)
            prepared.append((line,balance,new_on_hand,value,incoming.quantity));delivery_lines.append(SalesDeliveryLine(sales_order_line_id=line.id,item_id=line.item_id,quantity=incoming.quantity,unit_cost=balance.average_cost))
        number=data.number or next_number(db,order.company_id,"sales_delivery")
        delivery=SalesDelivery(company_id=order.company_id,sales_order_id=order.id,number=number,delivery_date=data.delivery_date,warehouse_id=data.warehouse_id,status="posted",notes=data.notes,lines=delivery_lines)
        db.add(delivery);db.flush()
        total_cost=Decimal("0")
        for line,balance,new_on_hand,value,quantity in prepared:
            balance.on_hand_quantity=new_on_hand;balance.inventory_value=max(Decimal(balance.inventory_value)-value,Decimal("0"));total_cost+=value
            db.add(InventoryMovement(company_id=order.company_id,item_id=line.item_id,warehouse_id=data.warehouse_id,movement_type="issue",movement_date=data.delivery_date,quantity=quantity,signed_quantity=-Decimal(quantity),unit_cost=balance.average_cost,movement_value=value,reference_type="sales_delivery",reference_id=str(delivery.id),notes=data.notes))
        all_delivered=True
        for line in order.lines:
            total=db.scalar(select(func.coalesce(func.sum(SalesDeliveryLine.quantity),0)).join(SalesDelivery,SalesDelivery.id==SalesDeliveryLine.delivery_id).where(SalesDelivery.sales_order_id==order.id,SalesDelivery.status=="posted",SalesDeliveryLine.sales_order_line_id==line.id)) or Decimal("0")
            if Decimal(total)<Decimal(line.quantity): all_delivered=False
        order.status="delivered" if all_delivered else "partially_delivered"
        link_documents(db,order.company_id,"sales_order",order.id,"sales_delivery",delivery.id,"fulfilled_by")
        complete_event(event,"sales_delivery",delivery.id,f"cost={total_cost}");audit(db,"deliver","sales_order",order.id,f"delivery={delivery.number}");db.commit()
    except ValueError as exc:
        db.rollback();raise HTTPException(409,str(exc))
    return {"id":delivery.id,"number":delivery.number,"order_status":order.status,"inventory_cost":str(total_cost),"replayed":False}


@router.post("/sales-orders/{order_id}/integrated-invoice")
def integrated_sales_invoice(order_id: int, data: IntegratedSalesInvoiceCreate, db: Session = Depends(get_db)):
    from app.domain.integration_rules import sales_journal
    order=db.scalar(select(SalesOrder).options(selectinload(SalesOrder.lines)).where(SalesOrder.id==order_id))
    if not order: raise HTTPException(404,"Sales order not found")
    if order.status not in {"delivered","partially_delivered"}: raise HTTPException(409,"Sales order must have posted delivery before invoicing")
    event,replayed=integration_event(db,order.company_id,data.idempotency_key,"sales_invoice","sales_order",order.id)
    if replayed:return {"replayed":True,"event_id":event.id,"result_type":event.result_type,"result_id":event.result_id}
    number=next_number(db,order.company_id,"ar_invoice")
    invoice=Invoice(company_id=order.company_id,party_id=order.customer_id,invoice_type="ar",number=number,invoice_date=data.invoice_date,due_date=data.due_date,currency=order.currency,description=f"Sales order {order.number}")
    invoice.lines=[InvoiceLine(description=x.description,quantity=x.quantity,unit_price=(Decimal(x.unit_price)*(Decimal("100")-Decimal(x.discount_percent))/Decimal("100")),tax_rate=x.tax_rate) for x in order.lines]
    invoice.recalculate();db.add(invoice);db.flush()
    cost=db.scalar(select(func.coalesce(func.sum(InventoryMovement.movement_value),0)).where(InventoryMovement.company_id==order.company_id,InventoryMovement.reference_type=="sales_delivery",InventoryMovement.reference_id.in_(select(func.cast(SalesDelivery.id,String)).where(SalesDelivery.sales_order_id==order.id)))) or Decimal("0")
    profile=db.scalar(select(PostingProfile).where(PostingProfile.company_id==order.company_id,PostingProfile.profile_type=="sales"))
    journal_id=None
    if profile and all([profile.receivable_account_id,profile.revenue_account_id,profile.inventory_account_id,profile.cogs_account_id]):
        specs=sales_journal(invoice.total_amount,cost);mapping={"accounts_receivable":profile.receivable_account_id,"revenue":profile.revenue_account_id,"inventory":profile.inventory_account_id,"cost_of_goods_sold":profile.cogs_account_id}
        journal=JournalEntry(company_id=order.company_id,reference=f"AR-{invoice.number}",description=f"Integrated sales posting {order.number}",lines=[JournalLine(account_id=mapping[name],memo=invoice.number,debit=debit,credit=credit) for name,debit,credit in specs]);journal.post();db.add(journal);db.flush();journal_id=journal.id;link_documents(db,order.company_id,"invoice",invoice.id,"journal_entry",journal.id,"posted_by")
    order.status="invoiced";link_documents(db,order.company_id,"sales_order",order.id,"invoice",invoice.id,"billed_by");complete_event(event,"invoice",invoice.id,f"journal_id={journal_id or ''}");db.commit()
    return invoice_view(invoice)|{"journal_id":journal_id,"replayed":False}


@router.post("/purchase-orders/{order_id}/integrated-supplier-invoice")
def integrated_supplier_invoice(order_id: int,data: SupplierInvoiceIntegratedCreate,db: Session=Depends(get_db)):
    from app.domain.integration_rules import three_way_match,purchase_journal
    order=db.scalar(select(PurchaseOrder).options(selectinload(PurchaseOrder.lines)).where(PurchaseOrder.id==order_id))
    if not order:raise HTTPException(404,"Purchase order not found")
    if order.status not in {"partially_received","received"}:raise HTTPException(409,"Purchase order requires a posted receipt before supplier invoicing")
    event,replayed=integration_event(db,order.company_id,data.idempotency_key,"supplier_invoice","purchase_order",order.id)
    if replayed:return {"replayed":True,"event_id":event.id,"result_type":event.result_type,"result_id":event.result_id}
    lines_by_id={x.id:x for x in order.lines};invoice_lines=[];matches=[];matched=True;qty_var=Decimal("0");price_var=Decimal("0")
    for incoming in data.lines:
        line=lines_by_id.get(incoming.purchase_order_line_id)
        if not line:raise HTTPException(404,"Purchase order line not found")
        outcome=three_way_match(line.quantity,line.received_quantity,incoming.invoiced_quantity,line.unit_price,incoming.unit_price,data.quantity_tolerance,data.price_tolerance_percent)
        matches.append((line,outcome));matched=matched and outcome['matched'];qty_var+=outcome['quantity_variance'];price_var+=outcome['price_variance']
        invoice_lines.append(InvoiceLine(description=line.description,quantity=incoming.invoiced_quantity,unit_price=incoming.unit_price,tax_rate=incoming.tax_rate))
    number=data.number or next_number(db,order.company_id,"ap_invoice")
    invoice=Invoice(company_id=order.company_id,party_id=order.supplier_id,invoice_type="ap",number=number,invoice_date=data.invoice_date,due_date=data.due_date,currency=order.currency,description=f"Purchase order {order.number}",lines=invoice_lines)
    invoice.recalculate();db.add(invoice);db.flush()
    match=SupplierInvoiceMatch(company_id=order.company_id,purchase_order_id=order.id,invoice_id=invoice.id,status="matched" if matched else "exception",quantity_variance=qty_var,price_variance=price_var,details="three-way match",matched_at=datetime.utcnow() if matched else None);db.add(match);db.flush()
    journal_id=None
    if matched:
        profile=db.scalar(select(PostingProfile).where(PostingProfile.company_id==order.company_id,PostingProfile.profile_type=="procurement"))
        debit_account=profile.inventory_account_id or profile.expense_account_id if profile else None
        if profile and debit_account and profile.payable_account_id:
            specs=purchase_journal(invoice.total_amount);mapping={"inventory_or_expense":debit_account,"accounts_payable":profile.payable_account_id}
            journal=JournalEntry(company_id=order.company_id,reference=f"AP-{invoice.number}",description=f"Integrated procurement posting {order.number}",lines=[JournalLine(account_id=mapping[name],memo=invoice.number,debit=debit,credit=credit) for name,debit,credit in specs]);journal.post();db.add(journal);db.flush();journal_id=journal.id;link_documents(db,order.company_id,"invoice",invoice.id,"journal_entry",journal.id,"posted_by")
    link_documents(db,order.company_id,"purchase_order",order.id,"invoice",invoice.id,"matched_to");complete_event(event,"invoice",invoice.id,f"match_status={match.status};journal_id={journal_id or ''}");db.commit()
    return invoice_view(invoice)|{"match_status":match.status,"quantity_variance":str(qty_var),"price_variance":str(price_var),"journal_id":journal_id,"replayed":False}


@router.get("/integration/trace")
def integration_trace(company_id:int,source_type:str,source_id:str,db:Session=Depends(get_db)):
    links=db.scalars(select(DocumentLink).where(DocumentLink.company_id==company_id,DocumentLink.source_type==source_type,DocumentLink.source_id==source_id)).all()
    return [{"source_type":x.source_type,"source_id":x.source_id,"target_type":x.target_type,"target_id":x.target_id,"relationship":x.relationship} for x in links]


@router.get("/integration/events")
def list_integration_events(company_id:int,status:str|None=None,db:Session=Depends(get_db)):
    q=select(IntegrationEvent).where(IntegrationEvent.company_id==company_id)
    if status:q=q.where(IntegrationEvent.status==status)
    return [{"id":x.id,"process_type":x.process_type,"source_type":x.source_type,"source_id":x.source_id,"status":x.status,"result_type":x.result_type,"result_id":x.result_id,"details":x.details,"created_at":x.created_at,"completed_at":x.completed_at} for x in db.scalars(q.order_by(IntegrationEvent.created_at.desc())).all()]



def posted_account_rows(company_id:int,db:Session):
    q=(select(Account.id,Account.code,Account.name,Account.account_type,func.coalesce(func.sum(JournalLine.debit),0),func.coalesce(func.sum(JournalLine.credit),0))
       .join(JournalLine,JournalLine.account_id==Account.id).join(JournalEntry,JournalEntry.id==JournalLine.entry_id)
       .where(Account.company_id==company_id,JournalEntry.status=="posted")
       .group_by(Account.id,Account.code,Account.name,Account.account_type).order_by(Account.code))
    return db.execute(q).all()


@router.get("/reports/income-statement")
def report_income_statement(company_id:int,db:Session=Depends(get_db)):
    from app.domain.reporting_rules import income_statement,natural_balance
    rows=posted_account_rows(company_id,db);summary=income_statement([(x.account_type,x[4],x[5]) for x in rows])
    detail=[{"code":x.code,"account":x.name,"account_type":x.account_type,"balance":str(natural_balance(x.account_type,x[4],x[5]))} for x in rows if x.account_type.lower() in {"revenue","income","expense","cost_of_goods_sold","cogs"}]
    return {k:str(v) for k,v in summary.items()}|{"detail":detail}


@router.get("/reports/balance-sheet")
def report_balance_sheet(company_id:int,db:Session=Depends(get_db)):
    from app.domain.reporting_rules import balance_sheet,natural_balance
    rows=posted_account_rows(company_id,db);summary=balance_sheet([(x.account_type,x[4],x[5]) for x in rows])
    detail=[{"code":x.code,"account":x.name,"account_type":x.account_type,"balance":str(natural_balance(x.account_type,x[4],x[5]))} for x in rows if x.account_type.lower() in {"asset","liability","equity"}]
    return {k:(str(v) if isinstance(v,Decimal) else v) for k,v in summary.items()}|{"detail":detail}


@router.get("/reports/kpis")
def report_kpis(company_id:int,db:Session=Depends(get_db)):
    from app.domain.reporting_rules import percentage,days_outstanding
    sales=db.scalar(select(func.coalesce(func.sum(Invoice.total_amount),0)).where(Invoice.company_id==company_id,Invoice.invoice_type=="ar",Invoice.status!="void")) or Decimal("0")
    receivables=db.scalar(select(func.coalesce(func.sum(Invoice.total_amount-Invoice.paid_amount),0)).where(Invoice.company_id==company_id,Invoice.invoice_type=="ar",Invoice.status.in_(["open","partially_paid"]))) or Decimal("0")
    purchases=db.scalar(select(func.coalesce(func.sum(Invoice.total_amount),0)).where(Invoice.company_id==company_id,Invoice.invoice_type=="ap",Invoice.status!="void")) or Decimal("0")
    payables=db.scalar(select(func.coalesce(func.sum(Invoice.total_amount-Invoice.paid_amount),0)).where(Invoice.company_id==company_id,Invoice.invoice_type=="ap",Invoice.status.in_(["open","partially_paid"]))) or Decimal("0")
    inventory_value=db.scalar(select(func.coalesce(func.sum(InventoryBalance.inventory_value),0)).where(InventoryBalance.company_id==company_id)) or Decimal("0")
    quotes=db.scalar(select(func.count(SalesQuote.id)).where(SalesQuote.company_id==company_id)) or 0
    converted=db.scalar(select(func.count(SalesQuote.id)).where(SalesQuote.company_id==company_id,SalesQuote.status=="converted")) or 0
    events=db.scalar(select(func.count(IntegrationEvent.id)).where(IntegrationEvent.company_id==company_id)) or 0
    completed=db.scalar(select(func.count(IntegrationEvent.id)).where(IntegrationEvent.company_id==company_id,IntegrationEvent.status=="completed")) or 0
    return {"sales":str(sales),"purchases":str(purchases),"receivables":str(receivables),"payables":str(payables),"inventory_value":str(inventory_value),"quote_conversion_percent":str(percentage(converted,quotes)),"integration_success_percent":str(percentage(completed,events)),"receivable_days":str(days_outstanding(receivables,sales,365)),"payable_days":str(days_outstanding(payables,purchases,365))}


@router.get("/reports/sales-performance")
def sales_performance(company_id:int,db:Session=Depends(get_db)):
    q=(select(Party.id,Party.name,func.count(Invoice.id),func.coalesce(func.sum(Invoice.total_amount),0),func.coalesce(func.sum(Invoice.total_amount-Invoice.paid_amount),0))
       .join(Invoice,Invoice.party_id==Party.id).where(Invoice.company_id==company_id,Invoice.invoice_type=="ar",Invoice.status!="void")
       .group_by(Party.id,Party.name).order_by(func.sum(Invoice.total_amount).desc()))
    return [{"customer_id":x[0],"customer":x[1],"invoice_count":x[2],"sales":str(x[3]),"outstanding":str(x[4])} for x in db.execute(q).all()]


@router.get("/reports/procurement-performance")
def procurement_performance(company_id:int,db:Session=Depends(get_db)):
    q=(select(Party.id,Party.name,func.count(PurchaseOrder.id),func.coalesce(func.sum(PurchaseOrder.total_amount),0))
       .join(PurchaseOrder,PurchaseOrder.supplier_id==Party.id).where(PurchaseOrder.company_id==company_id)
       .group_by(Party.id,Party.name).order_by(func.sum(PurchaseOrder.total_amount).desc()))
    return [{"supplier_id":x[0],"supplier":x[1],"order_count":x[2],"commitment":str(x[3])} for x in db.execute(q).all()]


@router.get("/reports/inventory-summary")
def inventory_summary(company_id:int,db:Session=Depends(get_db)):
    q=(select(Warehouse.id,Warehouse.name,func.count(InventoryBalance.item_id),func.coalesce(func.sum(InventoryBalance.on_hand_quantity),0),func.coalesce(func.sum(InventoryBalance.inventory_value),0))
       .join(InventoryBalance,InventoryBalance.warehouse_id==Warehouse.id).where(InventoryBalance.company_id==company_id)
       .group_by(Warehouse.id,Warehouse.name).order_by(Warehouse.name))
    return [{"warehouse_id":x[0],"warehouse":x[1],"item_count":x[2],"on_hand":str(x[3]),"inventory_value":str(x[4])} for x in db.execute(q).all()]


@router.get("/reports/integration-health")
def integration_health(company_id:int,db:Session=Depends(get_db)):
    q=(select(IntegrationEvent.process_type,IntegrationEvent.status,func.count(IntegrationEvent.id)).where(IntegrationEvent.company_id==company_id).group_by(IntegrationEvent.process_type,IntegrationEvent.status))
    return [{"process_type":x[0],"status":x[1],"count":x[2]} for x in db.execute(q).all()]


@router.post("/reports/saved")
def create_saved_report(data:SavedReportCreate,db:Session=Depends(get_db)):
    from app.domain.reporting_rules import validate_report_parameters
    try:validate_report_parameters(data.report_type,data.parameters)
    except ValueError as exc:raise HTTPException(400,str(exc))
    obj=SavedReport(company_id=data.company_id,name=data.name,report_type=data.report_type,parameters_json=json.dumps(data.parameters,sort_keys=True),owner=data.owner,shared=data.shared)
    db.add(obj);db.commit();db.refresh(obj);return {"id":obj.id,"name":obj.name,"report_type":obj.report_type,"parameters":json.loads(obj.parameters_json),"owner":obj.owner,"shared":obj.shared}


@router.get("/reports/saved")
def list_saved_reports(company_id:int,owner:str|None=None,db:Session=Depends(get_db)):
    q=select(SavedReport).where(SavedReport.company_id==company_id,SavedReport.active==True)
    if owner:q=q.where((SavedReport.owner==owner)|(SavedReport.shared==True))
    return [{"id":x.id,"name":x.name,"report_type":x.report_type,"parameters":json.loads(x.parameters_json),"owner":x.owner,"shared":x.shared} for x in db.scalars(q.order_by(SavedReport.name)).all()]


@router.post("/reports/run")
def record_report_run(data:ReportRunCreate,db:Session=Depends(get_db)):
    from app.domain.reporting_rules import validate_report_parameters
    try:validate_report_parameters(data.report_type,data.parameters)
    except ValueError as exc:raise HTTPException(400,str(exc))
    obj=ReportRun(company_id=data.company_id,report_type=data.report_type,parameters_json=json.dumps(data.parameters,sort_keys=True),generated_by=data.generated_by)
    db.add(obj);db.commit();db.refresh(obj);return {"id":obj.id,"report_type":obj.report_type,"status":obj.status,"generated_at":obj.generated_at}


@router.get("/reports/export/trial-balance.csv")
def export_trial_balance(company_id:int,db:Session=Depends(get_db)):
    from app.domain.reporting_rules import render_csv
    data=trial_balance(company_id,db);csv=render_csv(["Code","Account","Debit","Credit","Balance"],[[x["code"],x["account"],x["debit"],x["credit"],x["balance"]] for x in data])
    return {"filename":f"trial-balance-{company_id}.csv","content_type":"text/csv","content":csv}


@router.get("/reports/data-quality")
def data_quality(company_id:int,db:Session=Depends(get_db)):
    findings=[]
    accounts_without_activity=db.scalars(select(Account).where(Account.company_id==company_id,~Account.id.in_(select(JournalLine.account_id)))).all()
    for x in accounts_without_activity:findings.append({"severity":"info","finding_type":"inactive_account","entity_type":"account","entity_id":str(x.id),"description":f"Account {x.code} has no journal activity"})
    incomplete_profiles=db.scalars(select(PostingProfile).where(PostingProfile.company_id==company_id)).all()
    for x in incomplete_profiles:
        required=[x.receivable_account_id,x.revenue_account_id,x.inventory_account_id,x.cogs_account_id] if x.profile_type=="sales" else [x.payable_account_id,x.inventory_account_id or x.expense_account_id]
        if not all(required):findings.append({"severity":"warning","finding_type":"incomplete_posting_profile","entity_type":"posting_profile","entity_id":str(x.id),"description":f"{x.profile_type.title()} posting profile is incomplete"})
    exceptions=db.scalars(select(IntegrationEvent).where(IntegrationEvent.company_id==company_id,IntegrationEvent.status!="completed")).all()
    for x in exceptions:findings.append({"severity":"error","finding_type":"integration_exception","entity_type":"integration_event","entity_id":str(x.id),"description":f"{x.process_type} event is {x.status}"})
    return findings


@router.get("/health/live")
def live_health():
    return {"status":"alive","product":"PeaOps","version":"0.8.1"}


@router.get("/health/ready")
def ready_health(db:Session=Depends(get_db)):
    try:
        db.execute(select(func.count(Company.id))).scalar()
        return {"status":"ready","database":"ok","version":"0.8.1"}
    except Exception:
        raise HTTPException(503,"Database readiness check failed")


@router.post("/auth/login")
def login(data:LoginRequest,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.company_id==data.company_id,User.username==data.username))
    now=datetime.utcnow()
    if not user or not user.active or (user.locked_until and user.locked_until>now) or not verify_password(data.password,user.password_hash):
        if user:
            user.failed_login_count+=1
            if user.failed_login_count>=5:user.locked_until=now+timedelta(minutes=15)
        db.add(SecurityEvent(company_id=data.company_id,event_type="login",username=data.username,outcome="denied",details="invalid credentials or locked account"));db.commit()
        raise HTTPException(401,"Invalid credentials or account unavailable")
    user.failed_login_count=0;user.locked_until=None;user.last_login_at=now
    permissions=permissions_for_user(db,user.id)
    token=create_access_token(str(user.id),user.company_id,permissions,settings.secret_key,settings.access_token_minutes*60)
    refresh=create_refresh_token();payload=decode_access_token(token,settings.secret_key)
    db.add(AuthSession(user_id=user.id,token_id=payload["jti"],refresh_token_hash=hash_refresh_token(refresh),expires_at=now+timedelta(days=7)))
    db.add(SecurityEvent(company_id=user.company_id,event_type="login",username=user.username,outcome="success"));db.commit()
    return {"access_token":token,"refresh_token":refresh,"token_type":"bearer","expires_in":settings.access_token_minutes*60,"permissions":permissions}


@router.post("/admin/users")
def create_user(data:UserCreate,db:Session=Depends(get_db),principal=Depends(require_permission("admin:users"))):
    if int(principal['company_id'])!=data.company_id:raise HTTPException(403,"Cross-company administration denied")
    obj=User(company_id=data.company_id,username=data.username.strip().lower(),display_name=data.display_name,password_hash=hash_password(data.password))
    db.add(obj);db.flush();db.add(SecurityEvent(company_id=data.company_id,event_type="user_create",username=obj.username,outcome="success",details=f"actor={principal['sub']}"));db.commit();db.refresh(obj)
    return {"id":obj.id,"username":obj.username,"display_name":obj.display_name,"active":obj.active}


@router.post("/admin/roles")
def create_role(data:RoleCreate,db:Session=Depends(get_db),principal=Depends(require_permission("admin:roles"))):
    if int(principal['company_id'])!=data.company_id:raise HTTPException(403,"Cross-company administration denied")
    obj=Role(company_id=data.company_id,code=data.code.strip().lower(),name=data.name);db.add(obj);db.flush()
    obj_permissions=normalize_permissions(data.permissions)
    try: validate_role_permissions(obj_permissions)
    except ValueError as exc: raise HTTPException(409,str(exc))
    db.add_all([RolePermission(role_id=obj.id,permission=x) for x in obj_permissions]);db.add(SecurityEvent(company_id=data.company_id,event_type="role_create",username=str(principal['sub']),outcome="success",details=obj.code));db.commit();db.refresh(obj)
    return {"id":obj.id,"code":obj.code,"name":obj.name,"permissions":obj_permissions}


@router.post("/admin/users/{user_id}/roles")
def assign_user_role(user_id:int,data:UserRoleAssignment,db:Session=Depends(get_db),principal=Depends(require_permission("admin:roles"))):
    user=db.get(User,user_id);role=db.get(Role,data.role_id)
    if not user or not role:raise HTTPException(404,"User or role not found")
    if user.company_id!=role.company_id or user.company_id!=int(principal['company_id']):raise HTTPException(403,"Cross-company role assignment denied")
    db.add(UserRole(user_id=user.id,role_id=role.id));db.add(SecurityEvent(company_id=user.company_id,event_type="role_assign",username=user.username,outcome="success",details=role.code));db.commit()
    return {"user_id":user.id,"role_id":role.id,"assigned":True}


@router.post("/auth/refresh")
def refresh_access(data:RefreshRequest,db:Session=Depends(get_db)):
    session=db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash==hash_refresh_token(data.refresh_token)))
    now=datetime.utcnow()
    if not session or session.revoked_at or session.expires_at<=now:raise HTTPException(401,"Refresh session unavailable")
    user=db.get(User,session.user_id)
    if not user or not user.active:raise HTTPException(401,"User unavailable")
    permissions=permissions_for_user(db,user.id);token=create_access_token(str(user.id),user.company_id,permissions,settings.secret_key,settings.access_token_minutes*60)
    return {"access_token":token,"token_type":"bearer","expires_in":settings.access_token_minutes*60,"permissions":permissions}


@router.post("/auth/logout")
def logout(data:LogoutRequest,db:Session=Depends(get_db)):
    session=db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash==hash_refresh_token(data.refresh_token)))
    if session and not session.revoked_at:session.revoked_at=datetime.utcnow();db.commit()
    return {"revoked":bool(session)}


@router.post("/approvals")
def request_approval(data:ApprovalCreate,db:Session=Depends(get_db),principal=Depends(require_permission("data:write"))):
    if int(principal['company_id'])!=data.company_id:raise HTTPException(403,"Cross-company approval denied")
    obj=ApprovalRecord(company_id=data.company_id,entity_type=data.entity_type,entity_id=data.entity_id,action=data.action,requested_by=str(principal['sub']),reason=data.reason)
    db.add(obj);db.commit();db.refresh(obj);return {"id":obj.id,"status":obj.status,"version":obj.version}


@router.post("/approvals/{approval_id}/approve")
def approve_action(approval_id:int,data:ApprovalDecision,db:Session=Depends(get_db),principal=Depends(require_permission("data:approve"))):
    obj=db.get(ApprovalRecord,approval_id)
    if not obj:raise HTTPException(404,"Approval not found")
    if obj.company_id!=int(principal['company_id']):raise HTTPException(403,"Cross-company approval denied")
    if obj.status!="pending":raise HTTPException(409,"Approval is no longer pending")
    try:
        require_distinct_actor(obj.requested_by,str(principal['sub']),obj.action);obj.version=require_version(data.expected_version,obj.version)
    except (PermissionError,ValueError) as exc:raise HTTPException(409,str(exc))
    obj.status="approved";obj.approved_by=str(principal['sub']);obj.reason=data.reason;obj.decided_at=datetime.utcnow();db.commit()
    return {"id":obj.id,"status":obj.status,"version":obj.version,"approved_by":obj.approved_by}
