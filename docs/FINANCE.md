# Finance Module - v0.2

## Document lifecycle

AR and AP invoices begin in `draft`. Posting recalculates subtotal, tax and total from lines, validates due dates and moves the invoice to `open`. Allocations move it to `partially_paid` or `paid`. Payments cannot be allocated beyond either the payment's unallocated amount or the invoice's outstanding amount.

## Party controls

- AR invoices and receipts require a customer.
- AP invoices and supplier payments require a supplier.
- An allocation must match company, party and document direction.
- GSTIN is reserved as a 15-character optional party field; tax compliance automation remains planned.

## Ageing

Open balances are bucketed as Current, 1–30, 31–60, 61–90 and 90+ days using invoice due date and an explicit report date.

## Numbering

Sequences are company- and document-type-specific. Supported types are `ar_invoice`, `ap_invoice`, `receipt` and `payment`. Invoice creation can issue a configured number automatically or accept an explicit number.

## Not yet automated

Invoice and payment operations do not yet generate general-ledger journals. The v0.6 integration milestone will connect quote-to-cash and procure-to-pay documents to controlled accounting posting.
