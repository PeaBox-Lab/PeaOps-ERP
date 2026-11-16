# Troubleshooting

| Symptom | Likely cause | Safe action |
|---|---|---|
| Number sequence not configured | Missing document-type sequence | Create the sequence for the company |
| Journal not balanced | Debit and credit mismatch | Correct draft lines; do not force posting |
| Credit limit exceeded | AR + confirmed orders + new order exceeds limit | Review exposure or follow authorized override process |
| Negative stock | Insufficient warehouse balance | Receive/transfer stock or correct the request |
| Over-receipt/over-delivery | Quantity exceeds remaining source line | Reduce quantity or inspect prior transactions |
| Supplier match exception | Quantity or price outside tolerance | Investigate PO, receipt and invoice |
| No automatic journal | Posting profile incomplete | Configure required company accounts |
| Duplicate operation uncertainty | Retried request | Reuse the same idempotency key and inspect event result |
| Statement unsupported account type | Account classification is not recognized | Correct account type through controlled master-data process |
