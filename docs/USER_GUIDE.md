# User Guide - v0.4

## Procurement setup

1. Create company, supplier, item and optional warehouse masters.
2. Configure `purchase_request`, `rfq`, `purchase_order` and `goods_receipt` number sequences.
3. Confirm required Finance and Sales setup remains available where needed.

## Request-to-receipt

1. Create a purchase request with required date and demand lines.
2. Submit the request for sourcing.
3. Create and issue an RFQ, optionally linked to the request.
4. Record quotations from supplier masters.
5. Review the RFQ comparison; the recommendation uses lowest total then earliest promise.
6. Convert the chosen supplier quote into a purchase order, or create an order directly.
7. Confirm the purchase order.
8. Record partial or complete goods receipts against individual order lines.
9. Continue receiving until every line is complete and the order status becomes `received`.

## Existing modules retained

- Sales: price lists, quotations, sales orders, credit checks and AR invoice handoff.
- Finance: AR/AP invoices, payments, allocations, ageing, periods, banking foundation, journals and trial balance.
