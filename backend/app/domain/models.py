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
