
# API Workflow Examples

Use `/docs` for exact request schemas.

## Quote to cash

1. Create customer and items.
2. Configure `sales_quote`, `sales_order`, `sales_delivery`, `ar_invoice` sequences.
3. Create/send quotation; convert to order; confirm order.
4. Deliver order with one stable idempotency key.
5. Create integrated invoice with another stable key.
6. Fetch integration trace and reports.

## Procure to pay

1. Create supplier, items and warehouse.
2. Create request; issue RFQ; record and compare quotes.
3. Convert quote; confirm PO; receive goods.
4. Submit integrated supplier invoice with match tolerances.
5. Inspect match result, event and journal link.
