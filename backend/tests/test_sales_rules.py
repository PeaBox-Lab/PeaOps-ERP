
from datetime import date
from decimal import Decimal
import pytest
from app.domain.sales_rules import price_line, total_document, validate_validity, validate_delivery_promise, check_credit_limit
def test_line_pricing_with_discount_and_tax():
    result = price_line(Decimal('2'), Decimal('100'), Decimal('10'), Decimal('18'))
    assert result == (Decimal('200.00'), Decimal('20.00'), Decimal('180.00'), Decimal('32.40'), Decimal('212.40'))
def test_document_totals_multiple_lines():
    result = total_document([
        (Decimal('2'), Decimal('100'), Decimal('10'), Decimal('18')),
        (Decimal('1'), Decimal('50'), Decimal('0'), Decimal('0')),
    ])
    assert result == (Decimal('250.00'), Decimal('20.00'), Decimal('230.00'), Decimal('32.40'), Decimal('262.40'))
@pytest.mark.parametrize('discount', [Decimal('-1'), Decimal('101')])
def test_invalid_discount_rejected(discount):
    with pytest.raises(ValueError, match='Discount'):
        price_line(Decimal('1'), Decimal('100'), discount, Decimal('0'))
def test_zero_value_document_rejected():
    with pytest.raises(ValueError, match='greater than zero'):
        total_document([(Decimal('1'), Decimal('0'), Decimal('0'), Decimal('0'))])
def test_invalid_quote_validity_rejected():
    with pytest.raises(ValueError, match='Valid-until'):
        validate_validity(date(2026,11,20), date(2026,11,19))
def test_invalid_delivery_promise_rejected():
    with pytest.raises(ValueError, match='Promised'):
        validate_delivery_promise(date(2026,11,20), date(2026,11,19))
def test_credit_exposure_within_limit():
    exposure = check_credit_limit(Decimal('1000'), Decimal('300'), Decimal('200'), Decimal('400'))
    assert exposure == Decimal('900')
def test_credit_limit_breach_rejected():
    with pytest.raises(ValueError, match='credit limit exceeded'):
        check_credit_limit(Decimal('1000'), Decimal('500'), Decimal('200'), Decimal('400'))
def test_zero_credit_limit_is_unlimited():
    exposure = check_credit_limit(Decimal('0'), Decimal('5000'), Decimal('1000'), Decimal('2000'))
    assert exposure == Decimal('8000')
