# Integration Module - v0.6

## Design principles

Integrated operations are explicit API commands, not hidden model hooks. Every operation requires an idempotency key. The first successful execution stores its result; a replay returns that result rather than writing duplicate inventory, invoice or journal records.

## Quote to cash

`Sales Order → Sales Delivery → Inventory Issue → AR Invoice → Sales Journal`

Delivery validates cumulative quantity against each order line, checks warehouse stock, writes inventory issues and records cost. Invoice creation requires a posted delivery. With a complete Sales posting profile, PeaOps creates balanced AR/revenue and COGS/inventory journal lines.

## Procure to pay

`Purchase Order → Goods Receipt → Supplier Invoice → Three-Way Match → AP Journal`

A supplier invoice requires a partially or fully received order. Each line compares invoice quantity to received quantity and invoice price to PO price. Configurable tolerances determine `matched` or `exception`. Only matched invoices are eligible for automatic procurement journals.

## Traceability

Document links preserve relationships between source and result records. Integration events record process, source, result, status, timestamps and posting details. The trace endpoint follows direct outgoing links for a selected document.

## Controls still required for production

Database migrations, row-level concurrency locks, retry queues, dead-letter handling, role-based posting permissions, approval workflow, reversal orchestration and period-close enforcement remain later milestones.
