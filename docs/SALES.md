# Sales Module - v0.3

## Process

`Price List → Quotation → Send → Convert → Sales Order → Credit Check → Confirm → Draft AR Invoice`

## Pricing

Price lists belong to a company, currency and validity window. Each item may occur once in a price list. Quotation and order lines retain their chosen unit price, discount percentage and tax rate so later price-list changes do not silently alter historical commercial documents.

## Quotations

Quotations start in `draft`. Sending recalculates the full document and changes status to `sent`. A sent or accepted quotation can be converted to one sales order; conversion copies all lines and changes the quotation to `converted`.

## Sales orders

Orders start in `draft`. A promised-delivery date cannot precede the order date. Confirmation calculates exposure as open AR + previously confirmed orders + the new order. A positive customer credit limit blocks excess exposure. Credit-limit value zero is treated as unlimited until configurable credit-policy semantics are introduced.

An override requires an explicit reason and creates an audit event. This is a control foundation, not a substitute for role-based authorization or approval workflow.

## Invoice handoff

Only confirmed sales orders can be handed to AR. Handoff creates a draft AR invoice using the order's customer, currency, discounted line prices and tax rates, and marks the order `invoiced`. Inventory shipment and GL posting remain later integration milestones.
