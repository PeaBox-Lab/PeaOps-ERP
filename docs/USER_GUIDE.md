# User Guide - v0.3

## Sales setup

1. Create the company, customer and item masters.
2. Configure `sales_quote`, `sales_order` and `ar_invoice` number sequences.
3. Create dated price lists for the selling currency.
4. Set customer credit limits where control is required; zero currently means unlimited.

## Quote-to-order

1. Create a quotation with item, quantity, unit price, discount and tax.
2. Send the quotation after commercial review.
3. Convert a sent quotation to a sales order, or create an order directly.
4. Set an optional promised-delivery date.
5. Confirm the order. PeaOps checks open receivables, other confirmed orders and the new order against the customer limit.
6. If authorized outside the current system, record a credit override with a reason.
7. Hand a confirmed order to Finance to create a draft AR invoice.

## Finance lifecycle retained

- Invoice: Draft → Open → Partially Paid → Paid.
- Payment: Posted → controlled allocations.
- Journal: Draft → balanced validation → Posted.
