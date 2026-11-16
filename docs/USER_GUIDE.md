# User Guide - v0.6

## Configure posting

1. Complete company, accounts, customer/supplier, item and warehouse setup.
2. Configure document number sequences, including `sales_delivery`.
3. Create a Sales posting profile with receivable, revenue, inventory and COGS accounts.
4. Create a Procurement posting profile with payable and inventory or expense accounts.

## Quote to cash

1. Confirm a sales order.
2. Post one or more deliveries using a unique idempotency key.
3. PeaOps issues delivered quantities from the selected warehouse.
4. Create the integrated AR invoice using a new idempotency key.
5. Review the linked journal when a complete Sales posting profile exists.

## Procure to pay

1. Confirm and receive a purchase order.
2. Submit the supplier invoice with PO-line quantities and prices.
3. Set allowed quantity and price tolerances.
4. Review the match result.
5. A matched invoice can create an AP journal; an exception remains visible for resolution.

## Monitoring

Use Integration Events to review completed or failed operations and Trace Explorer to view document relationships. Reusing a completed idempotency key returns the original result.
