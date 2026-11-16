# Changelog

## 0.2.0 - 2026-11-16

### Added
- Accounts Receivable and Accounts Payable invoice foundation.
- Customer and supplier APIs with GSTIN-ready party records.
- Fiscal periods, document numbering and bank-account models and endpoints.
- Receipts, supplier payments and partial invoice allocation.
- Outstanding balance and AR/AP ageing APIs.
- Finance command-centre frontend.
- Finance rule tests for arithmetic, allocation, ageing and numbering.

### Changed
- Product/API/frontend version advanced to 0.2.0.
- Finance audit coverage expanded to parties, invoices, payments and allocations.
- Domain rules separated from persistence models for independently testable accounting controls.

## 0.1.0 - 2026-11-16

### Added
- Shared ERP core and three deployment branches.
- Core organizational, master-data, finance and audit domain models.
- Balanced journal validation and controlled posting.
- FastAPI health, company, account, journal and trial-balance endpoints.
- React/TypeScript dashboard shell with process explorer.
- PostgreSQL-first deployment configuration and local SQLite developer mode.
