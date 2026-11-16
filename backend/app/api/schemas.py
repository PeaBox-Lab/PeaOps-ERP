from decimal import Decimal
from pydantic import BaseModel, Field

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
