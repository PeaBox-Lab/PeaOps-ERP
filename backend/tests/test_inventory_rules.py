
from decimal import Decimal
import pytest
from app.domain.inventory_rules import apply_movement,weighted_average,issue_value,transfer_quantities,reorder_status,validate_tracking,signed_quantity

def test_receipt_increases_stock(): assert apply_movement(Decimal('10'),'receipt',Decimal('4'))==Decimal('14.0000')
def test_issue_reduces_stock(): assert apply_movement(Decimal('10'),'issue',Decimal('4'))==Decimal('6.0000')
def test_negative_stock_rejected():
    with pytest.raises(ValueError,match='negative stock'): apply_movement(Decimal('2'),'issue',Decimal('3'))
def test_negative_stock_allowed_by_policy(): assert apply_movement(Decimal('2'),'issue',Decimal('3'),True)==Decimal('-1.0000')
def test_weighted_average_valuation():
    quantity,average,value=weighted_average(Decimal('10'),Decimal('20'),Decimal('5'),Decimal('32'))
    assert (quantity,average,value)==(Decimal('15.0000'),Decimal('24.00'),Decimal('360.00'))
def test_issue_value(): assert issue_value(Decimal('3'),Decimal('24.50'))==Decimal('73.50')
def test_transfer_source_balance():
    source,destination_add=transfer_quantities(Decimal('20'),Decimal('7'))
    assert (source,destination_add)==(Decimal('13.0000'),Decimal('7.0000'))
def test_reorder_trigger_uses_available():
    available,needs,suggested=reorder_status(Decimal('20'),Decimal('8'),Decimal('12'),Decimal('25'))
    assert (available,needs,suggested)==(Decimal('12.0000'),True,Decimal('25.0000'))
def test_no_reorder_above_point():
    available,needs,suggested=reorder_status(Decimal('20'),Decimal('2'),Decimal('12'),Decimal('25'))
    assert (available,needs,suggested)==(Decimal('18.0000'),False,Decimal('0.0000'))
def test_lot_tracking_requires_lot():
    with pytest.raises(ValueError,match='Lot number'): validate_tracking('lot',Decimal('5'),None,None)
def test_serial_tracking_requires_one_unit():
    with pytest.raises(ValueError,match='quantity 1'): validate_tracking('serial',Decimal('2'),None,'SN-1')
def test_serial_tracking_accepts_one(): validate_tracking('serial',Decimal('1'),None,'SN-1')
def test_signed_transfer_entries():
    assert signed_quantity('transfer_out',Decimal('3'))==Decimal('-3')
    assert signed_quantity('transfer_in',Decimal('3'))==Decimal('3')
