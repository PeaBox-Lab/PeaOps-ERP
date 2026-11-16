# End User Quick Start

## Before you begin

Confirm your company, role, operating period and relevant master records are available. Use API documentation at `/docs` until fully interactive forms are implemented.

## Universal workflow

1. Create a draft document.
2. Validate dates, party, item, quantities, price, tax and currency.
3. Move the document through its allowed action: submit, send, confirm, post, receive, deliver or allocate.
4. Read the returned status and identifiers.
5. Use reports or trace links to verify downstream effects.

## Safety rules

- Never repeat an integration command with a different idempotency key merely because the response was slow.
- Never bypass a credit, stock, over-receipt or matching exception without an authorized process.
- Never treat dashboard sample values as live business data until connected to your database.
- Report validation messages with document number, action, timestamp and non-sensitive request context.
