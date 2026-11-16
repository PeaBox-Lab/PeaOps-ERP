from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class CompanyCreate(BaseModel):
    code: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=2, max_length=160)
    base_currency: str = Field(default="INR", min_length=3, max_length=3)


class AccountCreate(BaseModel):
    company_id: int
    code: str
    name: str
    account_type: str


class JournalLineIn(BaseModel):
    account_id: int
    memo: str = ""
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")


class JournalCreate(BaseModel):
    company_id: int
    reference: str
    description: str = ""
    lines: list[JournalLineIn] = Field(min_length=2)


class PartyCreate(BaseModel):
    company_id: int
    party_type: Literal["customer", "supplier"]
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=2, max_length=180)
    gstin: str | None = Field(default=None, min_length=15, max_length=15)
    credit_limit: Decimal = Field(default=Decimal("0"), ge=0)


class FiscalPeriodCreate(BaseModel):
    company_id: int
    code: str
    name: str
    start_date: date
    end_date: date


class NumberSequenceCreate(BaseModel):
    company_id: int
    document_type: Literal["ar_invoice", "ap_invoice", "receipt", "payment"]
    prefix: str = ""
    next_number: int = Field(default=1, ge=1)
    padding: int = Field(default=5, ge=1, le=12)


class BankAccountCreate(BaseModel):
    company_id: int
    code: str
    name: str
    currency: str = Field(default="INR", min_length=3, max_length=3)
    gl_account_id: int | None = None


class InvoiceLineIn(BaseModel):
    description: str = Field(min_length=1, max_length=240)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class InvoiceCreate(BaseModel):
    company_id: int
    party_id: int
    invoice_type: Literal["ar", "ap"]
    number: str | None = None
    invoice_date: date
    due_date: date
    currency: str = Field(default="INR", min_length=3, max_length=3)
    description: str = ""
    lines: list[InvoiceLineIn] = Field(min_length=1)

    @model_validator(mode="after")
    def dates_are_valid(self):
        if self.due_date < self.invoice_date:
            raise ValueError("Invoice due date cannot precede invoice date")
        return self


class PaymentCreate(BaseModel):
    company_id: int
    party_id: int
    bank_account_id: int | None = None
    payment_type: Literal["receipt", "payment"]
    reference: str
    payment_date: date
    amount: Decimal = Field(gt=0)


class AllocationCreate(BaseModel):
    invoice_id: int
    amount: Decimal = Field(gt=0)
