
# Sales User and Sales Operations Guide

## Workflow

1. Maintain customers, credit limits and price lists.
2. Create a quotation with validity, discount and tax.
3. Send and convert the quotation to an order.
4. Confirm the order after credit validation.
5. Deliver from a warehouse using a unique idempotency key.
6. Create the integrated AR invoice after delivery.
7. Monitor receivables and customer performance.

## Exceptions

Credit-limit override requires a reason but still needs organizational authorization. Delivery fails when quantity exceeds remaining order quantity or stock would become negative. Do not generate new replay keys to bypass an uncertain prior response.

## v0.8.2 credit override
When confirmation exceeds the credit limit, the override reason must be accompanied by an approved `credit_override` record bound to that sales order.
