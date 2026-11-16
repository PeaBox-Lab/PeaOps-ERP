from datetime import date, timedelta
from decimal import Decimal
import pytest
from app.domain.rules import calculate_invoice, allocate_balance, ageing_bucket, issue_number


def test_invoice_calculation():
    subtotal, tax, total = calculate_invoice([(Decimal('2'), Decimal('100'), Decimal('18'))])
    assert (subtotal, tax, total) == (Decimal('200.00'), Decimal('36.00'), Decimal('236.00'))


def test_partial_and_full_allocation():
    paid, outstanding, status = allocate_balance(Decimal('236'), Decimal('0'), Decimal('100'))
    assert (paid, outstanding, status) == (Decimal('100'), Decimal('136'), 'partially_paid')
    paid, outstanding, status = allocate_balance(Decimal('236'), paid, Decimal('136'))
    assert (paid, outstanding, status) == (Decimal('236'), Decimal('0'), 'paid')


def test_overpayment_is_rejected():
    with pytest.raises(ValueError, match='outstanding'):
        allocate_balance(Decimal('236'), Decimal('0'), Decimal('237'))


@pytest.mark.parametrize('days,bucket', [(0,'current'),(1,'1-30'),(30,'1-30'),(31,'31-60'),(61,'61-90'),(91,'90+')])
def test_ageing_boundaries(days, bucket):
    today = date(2026, 11, 16)
    assert ageing_bucket(today - timedelta(days=days), today, Decimal('10')) == bucket


def test_number_sequence_increments():
    value, next_number = issue_number('AR-', 9, 4)
    assert value == 'AR-0009' and next_number == 10
