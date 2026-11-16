# Procurement Module - v0.4

## Process

`Purchase Request → Submit → RFQ → Issue → Supplier Quotes → Compare → Purchase Order → Confirm → Goods Receipt`

## Purchase requests

Requests capture internal demand before a supplier commitment exists. Each request includes an owner, department, required date, justification and one or more item lines. Submission locks the request into the sourcing lifecycle foundation; approval workflow is planned for v0.8.

## RFQs and supplier quotations

An RFQ has a response deadline and may reference a purchase request. Only an issued RFQ accepts supplier quotations. Supplier quotation totals are derived from quantity, unit price, discount and tax. Validity and promised-delivery dates are validated.

The comparison endpoint recommends the lowest total. Equal totals are ranked by earlier promised date and then stable quote identity. This is a transparent commercial comparison, not an automated award decision.

## Purchase orders

A received supplier quotation can be converted into a purchase order without re-keying commercial lines, or an order can be created directly. Confirmation recalculates the document and changes it from `draft` to `confirmed`.

## Goods receipts

Confirmed orders accept one or more partial receipts. Each receipt references order lines and quantities. Cumulative received quantity cannot exceed ordered quantity. An order becomes `partially_received` until every line is complete, then `received`.

Receipts are quantity-control records only in v0.4. Inventory valuation, landed cost, quality inspection, three-way match and supplier invoice posting remain later milestones.
