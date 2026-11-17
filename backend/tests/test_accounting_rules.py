
from decimal import Decimal
import pytest
from app.domain.rules import validate_journal
def test_balanced_journal_passes():
    validate_journal([(Decimal('100'), Decimal('0')), (Decimal('0'), Decimal('100'))])
def test_unbalanced_journal_fails():
    with pytest.raises(ValueError, match='not balanced'):
        validate_journal([(Decimal('100'), Decimal('0')), (Decimal('0'), Decimal('99'))])
def test_mixed_debit_credit_line_fails():
    with pytest.raises(ValueError, match='debit OR credit'):
        validate_journal([(Decimal('100'), Decimal('10')), (Decimal('0'), Decimal('90'))])
