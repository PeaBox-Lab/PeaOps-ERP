from datetime import date
from decimal import Decimal
import pytest
from app.domain.integration_rules import require_idempotency_key,validate_delivery_quantities,three_way_match,journal_totals,sales_journal,purchase_journal

def test_valid_idempotency_key(): assert require_idempotency_key('sales-001-abc')=='sales-001-abc'
def test_short_idempotency_key_rejected():
    with pytest.raises(ValueError,match='8 to 120'): require_idempotency_key('short')
def test_partial_delivery():
    updated,remaining,status=validate_delivery_quantities(Decimal('10'),Decimal('2'),Decimal('3'))
    assert (updated,remaining,status)==(Decimal('5'),Decimal('5'),'partially_delivered')
def test_final_delivery():
    updated,remaining,status=validate_delivery_quantities(Decimal('10'),Decimal('4'),Decimal('6'))
    assert (updated,remaining,status)==(Decimal('10'),Decimal('0'),'delivered')
def test_over_delivery_rejected():
    with pytest.raises(ValueError,match='exceeds remaining'): validate_delivery_quantities(Decimal('10'),Decimal('8'),Decimal('3'))
def test_three_way_exact_match():
    result=three_way_match(Decimal('10'),Decimal('10'),Decimal('10'),Decimal('100'),Decimal('100'))
    assert result['matched'] is True
def test_three_way_quantity_exception():
    result=three_way_match(Decimal('10'),Decimal('8'),Decimal('10'),Decimal('100'),Decimal('100'))
    assert result['matched'] is False and result['quantity_variance']==Decimal('2')
def test_three_way_tolerance_accepts_small_variance():
    result=three_way_match(Decimal('10'),Decimal('9.5'),Decimal('10'),Decimal('100'),Decimal('101'),Decimal('0.5'),Decimal('1'))
    assert result['matched'] is True
def test_three_way_price_exception():
    result=three_way_match(Decimal('10'),Decimal('10'),Decimal('10'),Decimal('100'),Decimal('103'),Decimal('0'),Decimal('1'))
    assert result['matched'] is False and result['price_ok'] is False
def test_balanced_journal_totals(): assert journal_totals([(Decimal('100'),Decimal('0')),(Decimal('0'),Decimal('100'))])==(Decimal('100'),Decimal('100'))
def test_unbalanced_integrated_journal_rejected():
    with pytest.raises(ValueError,match='not balanced'): journal_totals([(Decimal('100'),Decimal('0')),(Decimal('0'),Decimal('99'))])
def test_sales_journal_with_cost_is_balanced():
    lines=sales_journal(Decimal('236'),Decimal('120'));assert sum(x[1] for x in lines)==sum(x[2] for x in lines)==Decimal('356.00')
def test_purchase_journal_is_balanced():
    lines=purchase_journal(Decimal('500'));assert sum(x[1] for x in lines)==sum(x[2] for x in lines)==Decimal('500.00')
