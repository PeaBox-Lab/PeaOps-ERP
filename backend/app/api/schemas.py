
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
    document_type: Literal["ar_invoice", "ap_invoice", "receipt", "payment", "sales_quote", "sales_order", "purchase_request", "rfq", "purchase_order", "goods_receipt", "stock_transfer", "sales_delivery"]
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
class PriceListLineIn(BaseModel):
    item_id: int
    unit_price: Decimal = Field(ge=0)
class PriceListCreate(BaseModel):
    company_id: int
    code: str
    name: str
    currency: str = Field(default="INR", min_length=3, max_length=3)
    valid_from: date
    valid_until: date
    lines: list[PriceListLineIn] = Field(min_length=1)
class SalesLineIn(BaseModel):
    item_id: int
    description: str = Field(min_length=1, max_length=240)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)
class SalesQuoteCreate(BaseModel):
    company_id: int
    customer_id: int
    number: str | None = None
    quote_date: date
    valid_until: date
    currency: str = Field(default="INR", min_length=3, max_length=3)
    notes: str = ""
    lines: list[SalesLineIn] = Field(min_length=1)
class SalesOrderCreate(BaseModel):
    company_id: int
    customer_id: int
    number: str | None = None
    order_date: date
    promised_date: date | None = None
    currency: str = Field(default="INR", min_length=3, max_length=3)
    lines: list[SalesLineIn] = Field(min_length=1)
class QuoteConversion(BaseModel):
    order_number: str | None = None
    order_date: date
    promised_date: date | None = None
class OrderConfirmation(BaseModel):
    override_credit: bool = False
    approval_id: int | None = Field(default=None, ge=1)
    override_reason: str = Field(default="", max_length=240)


class PurchaseRequestLineIn(BaseModel):
    item_id: int
    description: str = Field(min_length=1, max_length=240)
    quantity: Decimal = Field(gt=0)
    estimated_unit_cost: Decimal = Field(default=Decimal("0"), ge=0)


class PurchaseRequestCreate(BaseModel):
    company_id: int
    number: str | None = None
    request_date: date
    required_date: date
    requester: str = Field(default="system", min_length=1, max_length=120)
    department: str = Field(default="", max_length=80)
    justification: str = ""
    lines: list[PurchaseRequestLineIn] = Field(min_length=1)


class RFQLineIn(BaseModel):
    item_id: int
    description: str = Field(min_length=1, max_length=240)
    quantity: Decimal = Field(gt=0)


class RFQCreate(BaseModel):
    company_id: int
    purchase_request_id: int | None = None
    number: str | None = None
    rfq_date: date
    response_due: date
    currency: str = Field(default="INR", min_length=3, max_length=3)
    notes: str = ""
    lines: list[RFQLineIn] = Field(min_length=1)


class SupplierQuoteLineIn(BaseModel):
    item_id: int
    description: str = Field(min_length=1, max_length=240)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class SupplierQuoteCreate(BaseModel):
    company_id: int
    rfq_id: int
    supplier_id: int
    number: str
    quote_date: date
    valid_until: date
    promised_date: date | None = None
    currency: str = Field(default="INR", min_length=3, max_length=3)
    lines: list[SupplierQuoteLineIn] = Field(min_length=1)


class PurchaseOrderCreate(BaseModel):
    company_id: int
    supplier_id: int
    number: str | None = None
    order_date: date
    promised_date: date | None = None
    currency: str = Field(default="INR", min_length=3, max_length=3)
    lines: list[SupplierQuoteLineIn] = Field(min_length=1)


class SupplierQuoteConversion(BaseModel):
    order_number: str | None = None
    order_date: date
    promised_date: date | None = None


class GoodsReceiptLineIn(BaseModel):
    purchase_order_line_id: int
    quantity: Decimal = Field(gt=0)


class GoodsReceiptCreate(BaseModel):
    number: str | None = None
    receipt_date: date
    warehouse_id: int | None = None
    notes: str = ""
    lines: list[GoodsReceiptLineIn] = Field(min_length=1)


class InventoryPolicyCreate(BaseModel):
    company_id: int
    item_id: int
    warehouse_id: int
    tracking_mode: Literal["none", "lot", "serial"] = "none"
    reorder_point: Decimal = Field(default=Decimal("0"), ge=0)
    reorder_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    allow_negative: bool = False


class InventoryMovementCreate(BaseModel):
    company_id: int
    approval_id: int | None = Field(default=None, ge=1)
    item_id: int
    warehouse_id: int
    movement_type: Literal["opening", "receipt", "issue", "adjustment_in", "adjustment_out"]
    movement_date: date
    quantity: Decimal = Field(gt=0)
    unit_cost: Decimal | None = Field(default=None, ge=0)
    reference_type: str = Field(default="manual", max_length=40)
    reference_id: str = Field(default="", max_length=80)
    lot_number: str | None = None
    serial_number: str | None = None
    notes: str = ""


class StockTransferLineIn(BaseModel):
    item_id: int
    quantity: Decimal = Field(gt=0)
    lot_number: str | None = None
    serial_number: str | None = None


class StockTransferCreate(BaseModel):
    company_id: int
    number: str | None = None
    transfer_date: date
    source_warehouse_id: int
    destination_warehouse_id: int
    notes: str = ""
    lines: list[StockTransferLineIn] = Field(min_length=1)


class InventoryReservation(BaseModel):
    company_id: int
    item_id: int
    warehouse_id: int
    quantity: Decimal = Field(gt=0)


class PostingProfileCreate(BaseModel):
    company_id: int
    profile_type: Literal["sales", "procurement"]
    receivable_account_id: int | None = None
    payable_account_id: int | None = None
    revenue_account_id: int | None = None
    inventory_account_id: int | None = None
    cogs_account_id: int | None = None
    expense_account_id: int | None = None


class SalesDeliveryLineIn(BaseModel):
    sales_order_line_id: int
    quantity: Decimal = Field(gt=0)


class SalesDeliveryCreate(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=120)
    number: str | None = None
    delivery_date: date
    warehouse_id: int
    notes: str = ""
    lines: list[SalesDeliveryLineIn] = Field(min_length=1)


class IntegratedSalesInvoiceCreate(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=120)
    invoice_date: date
    due_date: date


class SupplierInvoiceLineMatch(BaseModel):
    purchase_order_line_id: int
    invoiced_quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class SupplierInvoiceIntegratedCreate(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=120)
    number: str | None = None
    invoice_date: date
    due_date: date
    quantity_tolerance: Decimal = Field(default=Decimal("0"), ge=0)
    price_tolerance_percent: Decimal = Field(default=Decimal("0"), ge=0)
    lines: list[SupplierInvoiceLineMatch] = Field(min_length=1)


class SavedReportCreate(BaseModel):
    company_id: int
    name: str = Field(min_length=2, max_length=120)
    report_type: Literal["income_statement","balance_sheet","trial_balance","ar_ageing","ap_ageing","sales_performance","procurement_performance","inventory_summary","integration_health"]
    parameters: dict = Field(default_factory=dict)
    owner: str = Field(default="system", min_length=1, max_length=120)
    shared: bool = False


class ReportRunCreate(BaseModel):
    company_id: int
    report_type: Literal["income_statement","balance_sheet","trial_balance","ar_ageing","ap_ageing","sales_performance","procurement_performance","inventory_summary","integration_health"]
    parameters: dict = Field(default_factory=dict)
    generated_by: str = Field(default="system", min_length=1, max_length=120)


class UserCreate(BaseModel):
    company_id: int
    username: str = Field(min_length=3, max_length=120)
    display_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=12, max_length=200)


class LoginRequest(BaseModel):
    company_id: int
    username: str
    password: str
    mfa_code: str | None = None


class RoleCreate(BaseModel):
    company_id: int
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=120)
    permissions: list[str] = Field(min_length=1)


class UserRoleAssignment(BaseModel):
    role_id: int
    approval_id: int = Field(ge=1)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=300)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=300)


class ApprovalCreate(BaseModel):
    company_id: int
    entity_type: str = Field(min_length=2, max_length=50)
    entity_id: str = Field(min_length=1, max_length=80)
    action: Literal["journal_post","credit_override","inventory_adjustment","supplier_match_override","role_assignment"]
    reason: str = Field(min_length=5, max_length=500)


class ApprovalDecision(BaseModel):
    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=500)


# Manufacturing / MRP schemas
class BillOfMaterialCreate(BaseModel):
    company_id: int
    item_id: int
    revision: int = 1
    description: str = ""

class BillOfMaterialLineCreate(BaseModel):
    bom_id: int
    component_id: int
    quantity: Decimal = Field(default=Decimal("1"), ge=0)

class WorkOrderCreate(BaseModel):
    company_id: int
    number: str
    bom_id: int | None = None
    status: str = "draft"
    planned_date: date
    scheduled_date: date | None = None
    quantity: Decimal = Field(default=Decimal("1"), ge=0)

# Project schemas
class ProjectCreate(BaseModel):
    company_id: int
    code: str
    name: str
    description: str = ""
    start_date: date
    end_date: date | None = None
    status: str = "planning"
    budget: Decimal = Field(default=Decimal("0"), ge=0)

class ProjectTaskCreate(BaseModel):
    project_id: int
    name: str
    description: str = ""
    order: int = 0
    status: str = "pending"
    assigned_to: str = ""
    due_date: date | None = None
    estimated_hours: Decimal = Field(default=Decimal("0"), ge=0)
    actual_hours: Decimal = Field(default=Decimal("0"), ge=0)

# Maintenance / Assets schemas
class MaintenanceAssetCreate(BaseModel):
    company_id: int
    code: str
    name: str
    category: str = ""
    purchase_date: date
    warranty_expiry: date | None = None
    location: str = ""
    status: str = "active"

class MaintenanceWorkOrderCreate(BaseModel):
    company_id: int
    number: str
    asset_id: int
    requested_by: str = ""
    work_description: str = ""
    status: str = "open"
    priority: str = "medium"
    requested_date: date = Field(default_factory=date.today)

# Finance / consolidation schemas
class LedgerConsolidationCreate(BaseModel):
    company_id: int
    period_start: date
    period_end: date
    status: str = "draft"
    notes: str = ""

class TreasuryAccountCreate(BaseModel):
    company_id: int
    code: str
    name: str
    currency: str = "INR"
    balance: Decimal = Field(default=Decimal("0"), ge=0)
    account_type: str = "bank"
    bank_account_id: int | None = None
    active: bool = True
