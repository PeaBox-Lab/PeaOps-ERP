
from datetime import date
from decimal import Decimal
import pytest
from app.domain.procurement_rules import (
    price_purchase_line, total_purchase_document, validate_required_date,
    validate_quote_window, choose_best_quote, apply_receipt
)


def test_purchase_line_discount_and_tax():
    result = price_purchase_line(Decimal('10'), Decimal('25'), Decimal('4'), Decimal('18'))
    assert result == (Decimal('250.00'), Decimal('10.00'), Decimal('240.00'), Decimal('43.20'), Decimal('283.20'))


def test_purchase_document_totals():
    result = total_purchase_document([
        (Decimal('10'), Decimal('25'), Decimal('4'), Decimal('18')),
        (Decimal('2'), Decimal('100'), Decimal('0'), Decimal('0')),
    ])
    assert result == (Decimal('450.00'), Decimal('10.00'), Decimal('440.00'), Decimal('43.20'), Decimal('483.20'))


@pytest.mark.parametrize('discount', [Decimal('-0.1'), Decimal('100.1')])
def test_invalid_purchase_discount_rejected(discount):
    with pytest.raises(ValueError, match='Discount'):
        price_purchase_line(Decimal('1'), Decimal('100'), discount, Decimal('0'))


def test_zero_purchase_document_rejected():
    with pytest.raises(ValueError, match='greater than zero'):
        total_purchase_document([(Decimal('1'), Decimal('0'), Decimal('0'), Decimal('0'))])


def test_required_date_cannot_precede_request():
    with pytest.raises(ValueError, match='Required date'):
        validate_required_date(date(2026,11,20), date(2026,11,19))


def test_rfq_due_date_cannot_precede_issue():
    with pytest.raises(ValueError, match='response due'):
        validate_quote_window(date(2026,11,20), date(2026,11,19))


def test_best_quote_uses_price_then_promise():
    chosen = choose_best_quote([
        (1, Decimal('1000'), date(2026,11,25)),
        (2, Decimal('900'), date(2026,11,28)),
        (3, Decimal('900'), date(2026,11,24)),
    ])
    assert chosen[0] == 3


def test_partial_receipt_tracks_remaining():
    updated, remaining, status = apply_receipt(Decimal('10'), Decimal('0'), Decimal('4'))
    assert (updated, remaining, status) == (Decimal('4'), Decimal('6'), 'partially_received')


def test_final_receipt_closes_line():
    updated, remaining, status = apply_receipt(Decimal('10'), Decimal('4'), Decimal('6'))
    assert (updated, remaining, status) == (Decimal('10'), Decimal('0'), 'received')


def test_over_receipt_is_rejected():
    with pytest.raises(ValueError, match='exceeds remaining'):
        apply_receipt(Decimal('10'), Decimal('8'), Decimal('3'))
