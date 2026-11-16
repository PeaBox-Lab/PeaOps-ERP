# Data Migration Guide

## Load sequence

Companies → branches/warehouses → accounts/periods → parties → items/policies → opening journals → open AR/AP → opening inventory → open sales/procurement documents.

## Controls

Define source ownership, extraction date, mapping, transformation, reject handling and sign-off. Reconcile record counts, control totals, balances, inventory quantities/value and open-document totals. Never invent missing master codes or financial values.

## Evidence

Retain source extracts, mappings, load logs, rejected rows, reconciliation schedules and business-owner approval.
