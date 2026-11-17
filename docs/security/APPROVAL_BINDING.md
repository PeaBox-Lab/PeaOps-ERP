# Approval Binding - v0.8.2
High-risk actions use a maker-checker record and must match five facts before execution: approved status, company, entity type, entity ID and action. The approver must already be distinct from the requester by the v0.8.1 decision rule.

## Bound controls
| Business action | Approval action | Entity |
|---|---|---|
| Post journal | `journal_post` | `journal_entry` |
| Override sales credit limit | `credit_override` | `sales_order` |
| Manual inventory adjustment | `inventory_adjustment` | `inventory_balance` |
| Assign user role | `role_assignment` | `user` |

## Operator sequence
1. Maker creates the target draft record.
2. Maker requests approval using `/api/v1/approvals` with the exact entity/action.
3. A different checker approves it using the expected approval version.
4. Operator supplies the resulting `approval_id` to the high-risk command.
5. PeaOps rejects missing, pending, cross-company, wrong-entity or wrong-action approvals.

Approval is an authorization prerequisite, not evidence that a business policy is correct. Organizations must define approval limits, emergency access and periodic review outside the codebase.
