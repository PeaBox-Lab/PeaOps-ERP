# Architecture

PeaOps remains a modular monolith with Finance, Sales, Procurement, Inventory and Integration domain areas sharing organization, party, item, warehouse, audit and numbering foundations.

## Integration architecture

- Explicit application commands coordinate cross-module changes.
- `IntegrationEvent` supplies replay protection and operation status.
- `DocumentLink` supplies durable source-to-result traceability.
- `PostingProfile` maps business posting roles to company GL accounts.
- Operational and financial mutations share one database transaction.
- Pure integration rules validate delivery quantities, matching and balanced posting specifications.

## Transaction boundaries

Sales delivery updates inventory, writes movement history and delivery records atomically. Integrated invoicing creates subledger documents, optional GL journals and trace links atomically. Procurement matching creates the supplier invoice and match result together; an exception prevents automatic journal posting.

## Production hardening gap

The current create-all schema approach must be replaced with migrations. Concurrent posting requires row locking or optimistic version checks. Idempotency uniqueness must be enforced and tested on PostgreSQL under parallel requests.
