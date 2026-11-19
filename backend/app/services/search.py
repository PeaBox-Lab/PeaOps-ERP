"""Global cross-document search for a company. Returns lightweight hits grouped by type."""
import re
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.domain.models import Invoice, SalesOrder, PurchaseOrder, SalesQuote, Party, Item


def _like(col, pattern):
    return col.ilike(f"%{pattern}%")


def global_search(db: Session, company_id: int, q: str, limit: int = 20):
    q_norm = (q or "").strip()
    if len(q_norm) < 2:
        return {"query": q_norm, "hits": []}
    pat = q_norm.lower()
    lim = max(1, min(int(limit), 50))

    hits = []

    # Invoices
    inv_rows = db.scalars(
        select(Invoice).where(Invoice.company_id == company_id)
        .where(Invoice.number.ilike(f"%{q_norm}%") | Invoice.description.ilike(f"%{q_norm}%") | Invoice.status.ilike(f"%{q_norm}%"))
        .order_by(Invoice.invoice_date.desc()).limit(lim)
    ).all()
    for x in inv_rows:
        hits.append({"type": "invoice", "id": x.id, "label": f"{x.number} • {x.status}", "sub": f"AR/AP • {x.total_amount}"})

    # Sales Orders
    so_rows = db.scalars(
        select(SalesOrder).where(SalesOrder.company_id == company_id)
        .where(SalesOrder.number.ilike(f"%{q_norm}%") | SalesOrder.status.ilike(f"%{q_norm}%"))
        .order_by(SalesOrder.order_date.desc()).limit(lim)
    ).all()
    for x in so_rows:
        hits.append({"type": "sales_order", "id": x.id, "label": f"{x.number} • {x.status}", "sub": f"SO • {x.total_amount}"})

    # Purchase Orders
    po_rows = db.scalars(
        select(PurchaseOrder).where(PurchaseOrder.company_id == company_id)
        .where(PurchaseOrder.number.ilike(f"%{q_norm}%") | PurchaseOrder.status.ilike(f"%{q_norm}%"))
        .order_by(PurchaseOrder.order_date.desc()).limit(lim)
    ).all()
    for x in po_rows:
        hits.append({"type": "purchase_order", "id": x.id, "label": f"{x.number} • {x.status}", "sub": f"PO • {x.total_amount}"})

    # Sales Quotes
    sq_rows = db.scalars(
        select(SalesQuote).where(SalesQuote.company_id == company_id)
        .where(SalesQuote.number.ilike(f"%{q_norm}%") | SalesQuote.status.ilike(f"%{q_norm}%"))
        .order_by(SalesQuote.quote_date.desc()).limit(lim)
    ).all()
    for x in sq_rows:
        hits.append({"type": "sales_quote", "id": x.id, "label": f"{x.number} • {x.status}", "sub": f"SQ • {x.total_amount}"})

    # Parties
    p_rows = db.scalars(
        select(Party).where(Party.company_id == company_id)
        .where(Party.code.ilike(f"%{q_norm}%") | Party.name.ilike(f"%{q_norm}%") | Party.party_type.ilike(f"%{q_norm}%"))
        .order_by(Party.name).limit(lim)
    ).all()
    for x in p_rows:
        hits.append({"type": "party", "id": x.id, "label": f"{x.name} ({x.code})", "sub": x.party_type})

    # Items
    i_rows = db.scalars(
        select(Item).where(Item.company_id == company_id)
        .where(Item.sku.ilike(f"%{q_norm}%") | Item.name.ilike(f"%{q_norm}%") | Item.unit.ilike(f"%{q_norm}%"))
        .order_by(Item.name).limit(lim)
    ).all()
    for x in i_rows:
        hits.append({"type": "item", "id": x.id, "label": f"{x.name} ({x.sku})", "sub": f"Unit: {x.unit}"})

    return {"query": q_norm, "hits": hits}