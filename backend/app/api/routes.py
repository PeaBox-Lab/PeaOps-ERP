from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.core.db import get_db
from app.domain.models import (
    Company, Account, JournalEntry, JournalLine, AuditEvent, Party, FiscalPeriod,
    NumberSequence, BankAccount, Invoice, InvoiceLine, Payment, Item,
    PriceList, PriceListLine, SalesQuote, SalesQuoteLine, SalesOrder, SalesOrderLine,
    PurchaseRequest, PurchaseRequestLine, RequestForQuote, RequestForQuoteLine,
    SupplierQuote, SupplierQuoteLine, PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine, Warehouse
)
from .schemas import (
    CompanyCreate, AccountCreate, JournalCreate, PartyCreate, FiscalPeriodCreate,
    NumberSequenceCreate, BankAccountCreate, InvoiceCreate, PaymentCreate, AllocationCreate,
    PriceListCreate, SalesQuoteCreate, SalesOrderCreate, QuoteConversion, OrderConfirmation,
    PurchaseRequestCreate, RFQCreate, SupplierQuoteCreate, PurchaseOrderCreate,
    SupplierQuoteConversion, GoodsReceiptCreate
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
    return {"status": "ok", "product": "PeaOps", "version": "0.4.0"}
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
