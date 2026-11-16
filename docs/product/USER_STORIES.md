# PeaOps Cumulative User Stories - v0.7

Each story uses: **As a [role], I want [capability], so that [outcome].** Acceptance criteria are product requirements and test/UAT inputs; they are not claims of production completeness.

## Platform and administration

### US-ADM-001 Company setup
As a system administrator, I want to create a company with code, name and base currency, so that all business data has an organizational boundary.
- Company code is unique.
- Base currency contains three characters.
- Creation writes an audit event.

### US-ADM-002 Number sequences
As a system administrator, I want company-specific document sequences, so that operational records receive controlled numbers.
- Sequence issues padded values and increments once.
- Duplicate company/document-type sequence is rejected.
- Invalid next number or padding is rejected.

### US-ADM-003 Fiscal periods
As a controller, I want fiscal periods with valid start/end dates, so that transactions can be organized by reporting period.
- End cannot precede start.
- Period code is unique within company.

### US-ADM-004 Posting profiles
As a finance administrator, I want business posting roles mapped to GL accounts, so that integrated documents can create balanced journals.
- Accounts belong to the same company.
- Sales and procurement profiles are independently configurable.
- Incomplete profiles appear in data-quality results.

### US-ADM-005 Saved reports
As a manager, I want to save and share report parameters, so that recurring analysis is reproducible.
- Supported report type is required.
- Parameters are stored as JSON.
- Owner-specific listing also returns shared reports.

## Finance

### US-FIN-001 Balanced journals
As an accountant, I want unbalanced journals rejected, so that the general ledger remains controlled.
- Total debit equals total credit and is greater than zero.
- A line cannot contain both debit and credit.
- Only draft journals can post.

### US-FIN-002 Customer invoice
As an AR user, I want to create and post customer invoices, so that receivables are recorded.
- Customer belongs to company.
- Totals derive from line quantity, price and tax.
- Due date cannot precede invoice date.

### US-FIN-003 Supplier invoice
As an AP user, I want supplier invoices, so that obligations can be tracked.
- Supplier party type is enforced.
- Invoice lifecycle exposes outstanding balance.

### US-FIN-004 Payment allocation
As a cash-application user, I want partial payment allocation, so that open balances remain accurate.
- Allocation cannot exceed payment unallocated amount.
- Allocation cannot exceed invoice outstanding amount.
- Invoice becomes partial or paid based on remaining balance.

### US-FIN-005 Ageing
As a credit or AP manager, I want Current/1–30/31–60/61–90/90+ ageing, so that overdue balances can be prioritized.
- Bucket uses due date and explicit as-of date.
- Paid balances do not appear as open ageing.

### US-FIN-006 Financial statements
As a controller, I want income-statement and balance-sheet views, so that financial performance and position can be reviewed.
- Natural balance follows supported account type.
- Balance sheet reports the accounting difference.
- Unsupported account classification is flagged.

## Sales

### US-SAL-001 Price lists
As a sales operations user, I want dated item prices, so that commercial terms can be managed.
- Price list has validity window and currency.
- Each item occurs once per list.

### US-SAL-002 Quotation
As a salesperson, I want quotations with discount and tax, so that I can offer controlled commercial terms.
- Quantity is positive; discounts/taxes are bounded.
- Send action is allowed only from draft.
- Totals are derived, not typed.

### US-SAL-003 Quote conversion
As a salesperson, I want to convert an accepted/sent quotation, so that I do not re-key an order.
- Lines and commercial values are copied.
- Source becomes converted.
- Order receives controlled number.

### US-SAL-004 Credit control
As a credit manager, I want order exposure checked, so that commitments stay within customer limits.
- Exposure includes open AR, confirmed orders and new order.
- Breach blocks confirmation unless override is explicitly requested with reason.

### US-SAL-005 Delivery
As a fulfilment user, I want to deliver confirmed orders, so that inventory and order status stay synchronized.
- Cumulative delivery cannot exceed ordered quantity.
- Warehouse stock cannot go negative unless policy permits.
- Delivery writes inventory issues and trace links.

### US-SAL-006 Integrated sales posting
As a finance user, I want delivered orders invoiced and posted, so that AR, revenue, COGS and inventory are connected.
- Delivery is prerequisite.
- Idempotency prevents duplicate invoices.
- Complete posting profile creates balanced journal.

## Procurement

### US-PRO-001 Purchase request
As a requester, I want to capture demand and required date, so that procurement has an authorized sourcing input.
- Required date cannot precede request date.
- Submit is allowed only from draft.

### US-PRO-002 RFQ
As a buyer, I want to issue RFQs, so that suppliers can compete on the same demand.
- Response due date cannot precede RFQ date.
- Supplier quote requires an issued RFQ.

### US-PRO-003 Quote comparison
As a buyer, I want a transparent supplier comparison, so that the recommendation is explainable.
- Lowest eligible total ranks first.
- Ties use earliest promise then stable identity.

### US-PRO-004 Purchase order
As a buyer, I want to convert a supplier quote to a PO, so that accepted terms are retained.
- Lines copy without re-keying.
- Confirmation recalculates totals.

### US-PRO-005 Goods receipt
As a receiving user, I want partial receipts, so that delivered quantities are tracked accurately.
- Cumulative quantity cannot exceed order.
- Order is partial until all lines complete.

### US-PRO-006 Three-way match
As an AP reviewer, I want PO/receipt/invoice comparison, so that only acceptable supplier invoices auto-post.
- Quantity and price variances are calculated.
- Tolerances are configurable per request.
- Exception prevents automatic journal.

## Inventory

### US-INV-001 Movement ledger
As an inventory controller, I want every movement recorded, so that stock history is traceable.
- Quantity is positive and signed direction is derived.
- Movement stores warehouse, item, cost, value and reference.

### US-INV-002 Negative-stock control
As a warehouse manager, I want insufficient issues blocked, so that balances remain credible.
- Default policy blocks negative stock.
- Explicit policy may allow it.

### US-INV-003 Weighted-average valuation
As a controller, I want receipt cost blended into average cost, so that inventory value is maintained.
- New average uses prior quantity/value and receipt cost.
- Issue value uses current average cost.

### US-INV-004 Stock transfer
As a warehouse user, I want transfers between warehouses, so that location balances remain synchronized.
- Source/destination differ.
- Source validates before either side posts.
- Equal out/in quantities and trace reference are written.

### US-INV-005 Tracking
As a quality or warehouse user, I want lot/serial rules, so that controlled items have identifiers.
- Lot mode requires lot.
- Serial mode requires serial and quantity one.

### US-INV-006 Reorder alerts
As a planner, I want reorder alerts based on available stock, so that replenishment is timely.
- Available equals on hand minus reserved.
- Alert occurs at or below reorder point.

## Integration and reliability

### US-INT-001 Idempotent command
As an integration engineer, I want replay-safe posting, so that network retries do not duplicate effects.
- Key length is validated.
- Completed replay returns original result.
- Same key is unique within company.

### US-INT-002 Document trace
As a support user or auditor, I want document relationships, so that I can follow source to result.
- Links identify types, IDs and relationship.
- Integration event identifies source and result.

### US-INT-003 Exception visibility
As an operations manager, I want failed/incomplete integration events visible, so that they can be resolved.
- Event status is filterable.
- Detail is included without secrets.

## Insight and reporting

### US-RPT-001 Trial balance export
As an accountant, I want CSV export, so that I can reconcile and retain evidence.
- Header and row widths match.
- CSV escaping protects commas, quotes and newlines.

### US-RPT-002 KPI dashboard
As an executive, I want sales, purchases, working-capital and integration KPIs, so that I can identify priorities.
- Zero denominators return zero rather than error.
- Values derive from company data.

### US-RPT-003 Operational performance
As a manager, I want customer, supplier and warehouse summaries, so that performance can be compared.
- Results are grouped within company.
- Amounts and counts are explicit.

### US-RPT-004 Data quality
As an administrator, I want actionable findings, so that reporting and posting gaps are visible.
- Incomplete posting profiles are warnings.
- Integration exceptions are errors.
- Accounts without activity are informational.

### US-RPT-005 Report history
As an auditor, I want report-run records, so that generation context is traceable.
- Run stores type, parameters, user and timestamp.

## Security and production operations

### US-SEC-001 User authentication
As a user, I want individual credentials and expiring access tokens, so that access is attributable and time bounded.
- Password policy is validated before hashing.
- Invalid login records a denied security event.
- Five failed attempts temporarily lock the account.

### US-SEC-002 Role administration
As a security administrator, I want reusable roles and permissions, so that access follows job responsibilities.
- Role and user belong to the same company.
- Duplicate permission and assignment are rejected.
- Administrative actions require administrative permissions.

### US-SEC-003 Secure runtime
As a technical administrator, I want unsafe production configuration rejected, so that known development defaults cannot start in production.
- Production requires PostgreSQL.
- Secret contains at least 32 non-default characters.
- Browser origins are explicit HTTPS URLs.

### US-OPS-001 Database migration
As a database administrator, I want versioned schema migrations, so that upgrades are controlled and repeatable.
- Migration runs before API startup.
- CI performs a PostgreSQL migration smoke test.
- Auto-create schema is disabled in production.

### US-OPS-002 Service health
As an operator, I want liveness and readiness probes, so that failed application or database state is detected.
- Liveness does not depend on database.
- Readiness verifies database access.

### US-OPS-003 Backup and restore
As an operator, I want checksummed PostgreSQL backups and a tested restore procedure, so that data can be recovered.
- Backup uses custom format and writes SHA-256.
- Restore validates checksum before changing database.
- Restore drills reconcile critical business totals.

### US-OSS-001 Community contribution
As a contributor, I want licensing, contribution rules, issue templates and CI, so that I can participate safely.
- Repository contains Apache-2.0 license and notice.
- Pull requests require validation and documentation checks.
- Security reports use private disclosure.

### US-OSS-002 Reproducible release
As a maintainer, I want tagged release packaging and checksums, so that users can verify a release.
- Release workflow builds from a tag.
- Generated package excludes secrets and caches.
- Release notes identify limitations and migrations.

## Pilot hardening

### US-SEC-004 Revocable session
As a security administrator, I want refresh sessions that can be revoked, so that logout and account response can prevent future token renewal.
- Refresh token is random and stored only as a hash.
- Expired or revoked session cannot refresh.
- Logout is idempotent.

### US-SEC-005 Deny-by-default route policy
As a security owner, I want API routes protected centrally, so that a newly added endpoint is not accidentally public.
- Public endpoints are explicitly listed.
- Unknown reads require `data:view`.
- Unknown writes require `data:write`.

### US-SOD-001 Maker-checker approval
As a controller, I want a different user to approve high-risk actions, so that one person cannot initiate and approve the same action.
- Requester and approver differ.
- Only pending records can be approved.
- Decision stores approver and time.

### US-SOD-002 Role conflict validation
As a security administrator, I want incompatible permissions rejected, so that selected duties cannot coexist in one role.
- Finance create/approve conflict is detected.
- User administration/security review conflict is detected.

### US-CON-001 Optimistic approval decision
As an approver, I want stale decisions rejected, so that concurrent reviewers do not overwrite one another.
- Client supplies expected version.
- Matching version increments.
- Mismatch returns conflict.
