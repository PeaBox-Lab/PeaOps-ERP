
from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import String, Date, DateTime, ForeignKey, Numeric, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.domain.rules import validate_journal, calculate_invoice, allocate_balance, ageing_bucket as resolve_ageing_bucket, issue_number
MONEY_ZERO = Decimal("0.00")
class EntryStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"
class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    VOID = "void"
class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    base_currency: Mapped[str] = mapped_column(String(3), default="INR")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
class Branch(Base):
    __tablename__ = "branches"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(120))
class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_account_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(160))
    account_type: Mapped[str] = mapped_column(String(30))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    reference: Mapped[str] = mapped_column(String(60), index=True)
    description: Mapped[str] = mapped_column(String(240), default="")
    status: Mapped[str] = mapped_column(String(20), default=EntryStatus.DRAFT.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    lines: Mapped[list[JournalLine]] = relationship(back_populates="entry", cascade="all, delete-orphan")
    def assert_balanced(self):
        validate_journal([(line.debit, line.credit) for line in self.lines])
    def post(self):
        if self.status != EntryStatus.DRAFT.value:
            raise ValueError("Only draft journals may be posted")
        self.assert_balanced()
        self.status = EntryStatus.POSTED.value
        self.posted_at = datetime.utcnow()
class JournalLine(Base):
    __tablename__ = "journal_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("journal_entries.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    memo: Mapped[str] = mapped_column(String(240), default="")
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    entry: Mapped[JournalEntry] = relationship(back_populates="lines")
class Party(Base):
    __tablename__ = "parties"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_party_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    party_type: Mapped[str] = mapped_column(String(20))
    code: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(180))
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    sku: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(180))
    unit: Mapped[str] = mapped_column(String(20), default="EA")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(160))
class FiscalPeriod(Base):
    __tablename__ = "fiscal_periods"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_period_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(80))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="open")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("Fiscal period end date cannot precede start date")
class NumberSequence(Base):
    __tablename__ = "number_sequences"
    __table_args__ = (UniqueConstraint("company_id", "document_type", name="uq_sequence_company_document"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(30))
    prefix: Mapped[str] = mapped_column(String(20), default="")
    next_number: Mapped[int] = mapped_column(default=1)
    padding: Mapped[int] = mapped_column(default=5)
    def issue(self) -> str:
        value, self.next_number = issue_number(self.prefix, self.next_number, self.padding)
        return value
class BankAccount(Base):
    __tablename__ = "bank_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    gl_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (UniqueConstraint("company_id", "invoice_type", "number", name="uq_invoice_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), index=True)
    invoice_type: Mapped[str] = mapped_column(String(10))
    number: Mapped[str] = mapped_column(String(40), index=True)
    invoice_date: Mapped[date] = mapped_column(Date, default=date.today)
    due_date: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    status: Mapped[str] = mapped_column(String(20), default=InvoiceStatus.DRAFT.value)
    description: Mapped[str] = mapped_column(String(240), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lines: Mapped[list[InvoiceLine]] = relationship(back_populates="invoice", cascade="all, delete-orphan")
    allocations: Mapped[list[PaymentAllocation]] = relationship(back_populates="invoice")
    @property
    def outstanding(self) -> Decimal:
        return max(Decimal(self.total_amount or 0) - Decimal(self.paid_amount or 0), MONEY_ZERO)
    def recalculate(self):
        self.subtotal, self.tax_amount, self.total_amount = calculate_invoice(
            [(line.quantity, line.unit_price, line.tax_rate) for line in self.lines]
        )
    def post(self):
        if self.status != InvoiceStatus.DRAFT.value:
            raise ValueError("Only draft invoices may be posted")
        if self.due_date < self.invoice_date:
            raise ValueError("Invoice due date cannot precede invoice date")
        self.recalculate()
        self.status = InvoiceStatus.OPEN.value
    def allocate(self, amount: Decimal):
        amount = Decimal(amount)
        if self.status not in {InvoiceStatus.OPEN.value, InvoiceStatus.PARTIALLY_PAID.value}:
            raise ValueError("Only open invoices accept allocations")
        self.paid_amount, _, self.status = allocate_balance(self.total_amount, self.paid_amount, amount)
    def ageing_bucket(self, as_of: date) -> str:
        return resolve_ageing_bucket(self.due_date, as_of, self.outstanding)
class InvoiceLine(Base):
    __tablename__ = "invoice_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), index=True)
    description: Mapped[str] = mapped_column(String(240))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("1"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    invoice: Mapped[Invoice] = relationship(back_populates="lines")
    @property
    def net_amount(self) -> Decimal:
        return (Decimal(self.quantity) * Decimal(self.unit_price)).quantize(Decimal("0.01"))
    @property
    def tax_amount(self) -> Decimal:
        return (self.net_amount * Decimal(self.tax_rate) / Decimal("100")).quantize(Decimal("0.01"))
class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), index=True)
    bank_account_id: Mapped[int | None] = mapped_column(ForeignKey("bank_accounts.id"), nullable=True)
    payment_type: Mapped[str] = mapped_column(String(10))
    reference: Mapped[str] = mapped_column(String(60), index=True)
    payment_date: Mapped[date] = mapped_column(Date, default=date.today)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    unallocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    status: Mapped[str] = mapped_column(String(20), default="posted")
    allocations: Mapped[list[PaymentAllocation]] = relationship(back_populates="payment", cascade="all, delete-orphan")
    def allocate(self, invoice: Invoice, amount: Decimal):
        amount = Decimal(amount)
        if amount > Decimal(self.unallocated_amount):
            raise ValueError("Allocation exceeds unallocated payment amount")
        invoice.allocate(amount)
        self.unallocated_amount = Decimal(self.unallocated_amount) - amount
        self.allocations.append(PaymentAllocation(invoice=invoice, amount=amount))
class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"
    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"), index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    payment: Mapped[Payment] = relationship(back_populates="allocations")
    invoice: Mapped[Invoice] = relationship(back_populates="allocations")
class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    actor: Mapped[str] = mapped_column(String(120), default="system")
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(80))
    details: Mapped[str] = mapped_column(Text, default="")
class PriceList(Base):
    __tablename__ = "price_lists"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_price_list_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    valid_from: Mapped[date] = mapped_column(Date)
    valid_until: Mapped[date] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    lines: Mapped[list[PriceListLine]] = relationship(back_populates="price_list", cascade="all, delete-orphan")
class PriceListLine(Base):
    __tablename__ = "price_list_lines"
    __table_args__ = (UniqueConstraint("price_list_id", "item_id", name="uq_price_list_item"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    price_list_id: Mapped[int] = mapped_column(ForeignKey("price_lists.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    price_list: Mapped[PriceList] = relationship(back_populates="lines")
class SalesQuote(Base):
    __tablename__ = "sales_quotes"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_quote_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    quote_date: Mapped[date] = mapped_column(Date, default=date.today)
    valid_until: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lines: Mapped[list[SalesQuoteLine]] = relationship(back_populates="quote", cascade="all, delete-orphan")
    def recalculate(self):
        from app.domain.sales_rules import total_document
        self.subtotal, self.discount_amount, _, self.tax_amount, self.total_amount = total_document(
            [(x.quantity, x.unit_price, x.discount_percent, x.tax_rate) for x in self.lines]
        )
    def send(self):
        if self.status != "draft": raise ValueError("Only draft quotations may be sent")
        self.recalculate(); self.status = "sent"
class SalesQuoteLine(Base):
    __tablename__ = "sales_quote_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("sales_quotes.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    description: Mapped[str] = mapped_column(String(240))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    quote: Mapped[SalesQuote] = relationship(back_populates="lines")
class SalesOrder(Base):
    __tablename__ = "sales_orders"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_order_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), index=True)
    quote_id: Mapped[int | None] = mapped_column(ForeignKey("sales_quotes.id"), nullable=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    order_date: Mapped[date] = mapped_column(Date, default=date.today)
    promised_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lines: Mapped[list[SalesOrderLine]] = relationship(back_populates="order", cascade="all, delete-orphan")
    def recalculate(self):
        from app.domain.sales_rules import total_document
        self.subtotal, self.discount_amount, _, self.tax_amount, self.total_amount = total_document(
            [(x.quantity, x.unit_price, x.discount_percent, x.tax_rate) for x in self.lines]
        )
class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    description: Mapped[str] = mapped_column(String(240))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    order: Mapped[SalesOrder] = relationship(back_populates="lines")


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_pr_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    request_date: Mapped[date] = mapped_column(Date, default=date.today)
    required_date: Mapped[date] = mapped_column(Date)
    requester: Mapped[str] = mapped_column(String(120), default="system")
    department: Mapped[str] = mapped_column(String(80), default="")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    justification: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lines: Mapped[list[PurchaseRequestLine]] = relationship(back_populates="request", cascade="all, delete-orphan")

    def submit(self):
        if self.status != "draft": raise ValueError("Only draft purchase requests may be submitted")
        if not self.lines: raise ValueError("Purchase request requires at least one line")
        self.status = "submitted"


class PurchaseRequestLine(Base):
    __tablename__ = "purchase_request_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("purchase_requests.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    description: Mapped[str] = mapped_column(String(240))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    estimated_unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    request: Mapped[PurchaseRequest] = relationship(back_populates="lines")


class RequestForQuote(Base):
    __tablename__ = "request_for_quotes"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_rfq_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    purchase_request_id: Mapped[int | None] = mapped_column(ForeignKey("purchase_requests.id"), nullable=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    rfq_date: Mapped[date] = mapped_column(Date, default=date.today)
    response_due: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lines: Mapped[list[RequestForQuoteLine]] = relationship(back_populates="rfq", cascade="all, delete-orphan")
    supplier_quotes: Mapped[list[SupplierQuote]] = relationship(back_populates="rfq")

    def issue(self):
        if self.status != "draft": raise ValueError("Only draft RFQs may be issued")
        if not self.lines: raise ValueError("RFQ requires at least one line")
        self.status = "issued"


class RequestForQuoteLine(Base):
    __tablename__ = "request_for_quote_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    rfq_id: Mapped[int] = mapped_column(ForeignKey("request_for_quotes.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    description: Mapped[str] = mapped_column(String(240))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    rfq: Mapped[RequestForQuote] = relationship(back_populates="lines")


class SupplierQuote(Base):
    __tablename__ = "supplier_quotes"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_supplier_quote_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    rfq_id: Mapped[int] = mapped_column(ForeignKey("request_for_quotes.id"), index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    quote_date: Mapped[date] = mapped_column(Date, default=date.today)
    valid_until: Mapped[date] = mapped_column(Date)
    promised_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(20), default="received")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    rfq: Mapped[RequestForQuote] = relationship(back_populates="supplier_quotes")
    lines: Mapped[list[SupplierQuoteLine]] = relationship(back_populates="quote", cascade="all, delete-orphan")

    def recalculate(self):
        from app.domain.procurement_rules import total_purchase_document
        self.subtotal, self.discount_amount, _, self.tax_amount, self.total_amount = total_purchase_document(
            [(x.quantity, x.unit_price, x.discount_percent, x.tax_rate) for x in self.lines]
        )


class SupplierQuoteLine(Base):
    __tablename__ = "supplier_quote_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("supplier_quotes.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    description: Mapped[str] = mapped_column(String(240))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    quote: Mapped[SupplierQuote] = relationship(back_populates="lines")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_po_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), index=True)
    supplier_quote_id: Mapped[int | None] = mapped_column(ForeignKey("supplier_quotes.id"), nullable=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    order_date: Mapped[date] = mapped_column(Date, default=date.today)
    promised_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(24), default="draft")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lines: Mapped[list[PurchaseOrderLine]] = relationship(back_populates="order", cascade="all, delete-orphan")
    receipts: Mapped[list[GoodsReceipt]] = relationship(back_populates="order")

    def recalculate(self):
        from app.domain.procurement_rules import total_purchase_document
        self.subtotal, self.discount_amount, _, self.tax_amount, self.total_amount = total_purchase_document(
            [(x.quantity, x.unit_price, x.discount_percent, x.tax_rate) for x in self.lines]
        )

    def confirm(self):
        if self.status != "draft": raise ValueError("Only draft purchase orders may be confirmed")
        self.recalculate(); self.status = "confirmed"


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    description: Mapped[str] = mapped_column(String(240))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(7, 4), default=MONEY_ZERO)
    order: Mapped[PurchaseOrder] = relationship(back_populates="lines")


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_receipt_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    receipt_date: Mapped[date] = mapped_column(Date, default=date.today)
    warehouse_id: Mapped[int | None] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="posted")
    notes: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[PurchaseOrder] = relationship(back_populates="receipts")
    lines: Mapped[list[GoodsReceiptLine]] = relationship(back_populates="receipt", cascade="all, delete-orphan")


class GoodsReceiptLine(Base):
    __tablename__ = "goods_receipt_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("goods_receipts.id"), index=True)
    purchase_order_line_id: Mapped[int] = mapped_column(ForeignKey("purchase_order_lines.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    receipt: Mapped[GoodsReceipt] = relationship(back_populates="lines")


class InventoryPolicy(Base):
    __tablename__ = "inventory_policies"
    __table_args__ = (UniqueConstraint("company_id", "item_id", "warehouse_id", name="uq_inventory_policy"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), index=True)
    tracking_mode: Mapped[str] = mapped_column(String(20), default="none")
    reorder_point: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"))
    reorder_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"))
    allow_negative: Mapped[bool] = mapped_column(Boolean, default=False)


class InventoryBalance(Base):
    __tablename__ = "inventory_balances"
    __table_args__ = (UniqueConstraint("company_id", "item_id", "warehouse_id", name="uq_inventory_balance"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), index=True)
    on_hand_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"))
    reserved_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"))
    average_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    inventory_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def available_quantity(self):
        return Decimal(self.on_hand_quantity) - Decimal(self.reserved_quantity)


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), index=True)
    movement_type: Mapped[str] = mapped_column(String(30), index=True)
    movement_date: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    signed_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    movement_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    reference_type: Mapped[str] = mapped_column(String(40), default="manual")
    reference_id: Mapped[str] = mapped_column(String(80), default="")
    lot_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StockTransfer(Base):
    __tablename__ = "stock_transfers"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_transfer_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    transfer_date: Mapped[date] = mapped_column(Date, default=date.today)
    source_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), index=True)
    destination_warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    notes: Mapped[str] = mapped_column(Text, default="")
    lines: Mapped[list[StockTransferLine]] = relationship(back_populates="transfer", cascade="all, delete-orphan")


class StockTransferLine(Base):
    __tablename__ = "stock_transfer_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    transfer_id: Mapped[int] = mapped_column(ForeignKey("stock_transfers.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    lot_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    transfer: Mapped[StockTransfer] = relationship(back_populates="lines")


class IntegrationEvent(Base):
    __tablename__ = "integration_events"
    __table_args__ = (UniqueConstraint("company_id", "idempotency_key", name="uq_integration_idempotency"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(120), index=True)
    process_type: Mapped[str] = mapped_column(String(40), index=True)
    source_type: Mapped[str] = mapped_column(String(50))
    source_id: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="processing")
    result_type: Mapped[str] = mapped_column(String(50), default="")
    result_id: Mapped[str] = mapped_column(String(80), default="")
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DocumentLink(Base):
    __tablename__ = "document_links"
    __table_args__ = (UniqueConstraint("company_id", "source_type", "source_id", "target_type", "target_id", name="uq_document_link"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(50), index=True)
    source_id: Mapped[str] = mapped_column(String(80), index=True)
    target_type: Mapped[str] = mapped_column(String(50), index=True)
    target_id: Mapped[str] = mapped_column(String(80), index=True)
    relationship: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PostingProfile(Base):
    __tablename__ = "posting_profiles"
    __table_args__ = (UniqueConstraint("company_id", "profile_type", name="uq_posting_profile"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    profile_type: Mapped[str] = mapped_column(String(30))
    receivable_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    payable_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    revenue_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    inventory_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    cogs_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    expense_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)


class SalesDelivery(Base):
    __tablename__ = "sales_deliveries"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_delivery_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    sales_order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    delivery_date: Mapped[date] = mapped_column(Date, default=date.today)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    notes: Mapped[str] = mapped_column(Text, default="")
    lines: Mapped[list[SalesDeliveryLine]] = relationship(back_populates="delivery", cascade="all, delete-orphan")


class SalesDeliveryLine(Base):
    __tablename__ = "sales_delivery_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    delivery_id: Mapped[int] = mapped_column(ForeignKey("sales_deliveries.id"), index=True)
    sales_order_line_id: Mapped[int] = mapped_column(ForeignKey("sales_order_lines.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    delivery: Mapped[SalesDelivery] = relationship(back_populates="lines")


class SupplierInvoiceMatch(Base):
    __tablename__ = "supplier_invoice_matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    quantity_variance: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"))
    price_variance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    details: Mapped[str] = mapped_column(Text, default="")
    matched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SavedReport(Base):
    __tablename__ = "saved_reports"
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_saved_report_company_name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    report_type: Mapped[str] = mapped_column(String(40), index=True)
    parameters_json: Mapped[str] = mapped_column(Text, default="{}")
    owner: Mapped[str] = mapped_column(String(120), default="system")
    shared: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReportRun(Base):
    __tablename__ = "report_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    saved_report_id: Mapped[int | None] = mapped_column(ForeignKey("saved_reports.id"), nullable=True)
    report_type: Mapped[str] = mapped_column(String(40), index=True)
    parameters_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(20), default="completed")
    row_count: Mapped[int] = mapped_column(default=0)
    generated_by: Mapped[str] = mapped_column(String(120), default="system")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DataQualityFinding(Base):
    __tablename__ = "data_quality_findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    finding_type: Mapped[str] = mapped_column(String(50), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("company_id", "username", name="uq_user_company_username"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    username: Mapped[str] = mapped_column(String(120), index=True)
    display_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(300))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_count: Mapped[int] = mapped_column(default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    mfa_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_role_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(120))
    system_role: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission", name="uq_role_permission"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    permission: Mapped[str] = mapped_column(String(120), index=True)


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)


class SecurityEvent(Base):
    __tablename__ = "security_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    username: Mapped[str] = mapped_column(String(120), default="")
    outcome: Mapped[str] = mapped_column(String(20))
    details: Mapped[str] = mapped_column(Text, default="")
    event_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApprovalRecord(Base):
    __tablename__ = "approval_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[str] = mapped_column(String(80), index=True)
    action: Mapped[str] = mapped_column(String(50))
    requested_by: Mapped[str] = mapped_column(String(80))
    approved_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reason: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Attachment(Base):
    __tablename__ = "attachments"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[str] = mapped_column(String(80), index=True)
    filename: Mapped[str] = mapped_column(String(240))
    file_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    uploaded_by: Mapped[str] = mapped_column(String(120), default="system")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"
    __table_args__ = (UniqueConstraint("company_id", "bank_account_id", "statement_date", name="uq_bank_recon"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    bank_account_id: Mapped[int] = mapped_column(ForeignKey("bank_accounts.id"), index=True)
    statement_date: Mapped[date] = mapped_column(Date)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FixedAsset(Base):
    __tablename__ = "fixed_assets"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_fixed_asset_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(60), default="")
    purchase_date: Mapped[date] = mapped_column(Date)
    cost: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    salvage_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    useful_life_months: Mapped[int] = mapped_column(default=60)
    depreciation_method: Mapped[str] = mapped_column(String(20), default="straight_line")
    accumulated_depreciation: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    source: Mapped[str] = mapped_column(String(60), default="")
    status: Mapped[str] = mapped_column(String(20), default="new")
    owner: Mapped[str] = mapped_column(String(120), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Opportunity(Base):
    __tablename__ = "opportunities"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("parties.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(160))
    stage: Mapped[str] = mapped_column(String(30), default="prospecting")
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    probability: Mapped[int] = mapped_column(default=10)
    expected_close: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(20), default="in_app")
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="unread")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class BillOfMaterial(Base):
    __tablename__ = "bill_of_materials"
    __table_args__ = (UniqueConstraint("company_id", "item_id", "revision", name="uq_bom_company_item_revision"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    revision: Mapped[int] = mapped_column(default=1)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lines: Mapped[list[BillOfMaterialLine]] = relationship(back_populates="bom", cascade="all, delete-orphan")


class BillOfMaterialLine(Base):
    __tablename__ = "bill_of_material_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    bom_id: Mapped[int] = mapped_column(ForeignKey("bill_of_materials.id"), index=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("1"))
    bom: Mapped[BillOfMaterial] = relationship(back_populates="lines")


class WorkOrder(Base):
    __tablename__ = "work_orders"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_work_order_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    bom_id: Mapped[int] = mapped_column(ForeignKey("bill_of_materials.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    planned_date: Mapped[date] = mapped_column(Date)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("1"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_project_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planning")
    budget: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tasks: Mapped[list[ProjectTask]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectTask(Base):
    __tablename__ = "project_tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    order: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    assigned_to: Mapped[str] = mapped_column(String(120), default="")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_hours: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    actual_hours: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    project: Mapped[Project] = relationship(back_populates="tasks")


class MaintenanceAsset(Base):
    __tablename__ = "maintenance_assets"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_asset_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(60), default="")
    purchase_date: Mapped[date] = mapped_column(Date)
    warranty_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MaintenanceWorkOrder(Base):
    __tablename__ = "maintenance_work_orders"
    __table_args__ = (UniqueConstraint("company_id", "number", name="uq_mwo_company_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    number: Mapped[str] = mapped_column(String(40), index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("maintenance_assets.id"), index=True)
    requested_by: Mapped[str] = mapped_column(String(120), default="")
    work_description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="open")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    requested_date: Mapped[date] = mapped_column(Date, default=date.today)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LedgerConsolidation(Base):
    __tablename__ = "ledger_consolidations"
    __table_args__ = (UniqueConstraint("company_id", "period_start", "period_end", name="uq_consolidation_company_period"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    consolidated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TreasuryAccount(Base):
    __tablename__ = "treasury_accounts"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_treasury_account_company_code"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(30), index=True)
    name: Mapped[str] = mapped_column(String(160))
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=MONEY_ZERO)
    account_type: Mapped[str] = mapped_column(String(30), default="bank")
    bank_account_id: Mapped[int | None] = mapped_column(ForeignKey("bank_accounts.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
