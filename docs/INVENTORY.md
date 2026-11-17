
# Inventory Module - v0.5

## Ledger model

Every posted stock event creates an append-only inventory movement. Movement types are opening, receipt, issue, adjustment in/out and transfer in/out. Warehouse balances are updated from the same controlled operation and expose on-hand, reserved, available, average cost and inventory value.

## Quantity controls

Outbound movements cannot create negative stock unless the item/warehouse policy explicitly allows it. Reservations cannot exceed available quantity. Transfers validate the full source side before writing either warehouse, then create equal transfer-out and transfer-in quantities.

## Valuation

Inbound movements use weighted-average costing. Outbound movements carry the current average cost. Warehouse inventory value decreases at issue cost and transfers preserve value between warehouses. This is a valuation foundation; period close, retroactive cost adjustment, landed cost and accounting journals are planned later.

## Tracking

Policies select `none`, `lot` or `serial` tracking. Lot-tracked movements require a lot number. Serial-tracked movements require a serial number and quantity exactly one. Uniqueness, genealogy and expiry controls are future work.

## Replenishment

Reorder checks use available quantity (`on hand − reserved`). When available quantity is at or below the reorder point, the configured reorder quantity is suggested. The alert does not automatically create a purchase request in v0.5.
