
from decimal import Decimal
import pytest
from app.domain.reporting_rules import account_nature,natural_balance,income_statement,balance_sheet,percentage,inventory_turnover,days_outstanding,validate_report_parameters,render_csv

def test_account_nature():assert account_nature('asset')=='debit' and account_nature('revenue')=='credit'
def test_unsupported_account_type():
 with pytest.raises(ValueError,match='Unsupported'):account_nature('mystery')
def test_natural_balances():assert natural_balance('asset',Decimal('100'),Decimal('20'))==Decimal('80.00') and natural_balance('liability',Decimal('10'),Decimal('60'))==Decimal('50.00')
def test_income_statement():
 result=income_statement([('revenue',Decimal('0'),Decimal('1000')),('expense',Decimal('600'),Decimal('0'))]);assert result=={'revenue':Decimal('1000.00'),'expenses':Decimal('600.00'),'net_income':Decimal('400.00')}
def test_balanced_balance_sheet():
 result=balance_sheet([('asset',Decimal('1000'),Decimal('0')),('liability',Decimal('0'),Decimal('600')),('equity',Decimal('0'),Decimal('400'))]);assert result['balanced'] is True
def test_unbalanced_balance_sheet():
 result=balance_sheet([('asset',Decimal('1000'),Decimal('0')),('liability',Decimal('0'),Decimal('500')),('equity',Decimal('0'),Decimal('400'))]);assert result['difference']==Decimal('100.00') and result['balanced'] is False
def test_percentage_zero_denominator():assert percentage(Decimal('10'),Decimal('0'))==Decimal('0.00')
def test_percentage():assert percentage(Decimal('2'),Decimal('5'))==Decimal('40.00')
def test_inventory_turnover():assert inventory_turnover(Decimal('600'),Decimal('100'),Decimal('200'))==Decimal('4.00')
def test_days_outstanding():assert days_outstanding(Decimal('100'),Decimal('1000'),365)==Decimal('36.50')
def test_invalid_days():
 with pytest.raises(ValueError,match='positive'):days_outstanding(Decimal('10'),Decimal('100'),0)
def test_report_parameters():assert validate_report_parameters('income_statement',{}) is True
def test_unsupported_report():
 with pytest.raises(ValueError,match='Unsupported'):validate_report_parameters('unknown',{})
def test_csv_rendering_and_escape():
 csv=render_csv(['Name','Value'],[['A, Inc','10'],['Quoted "Name"','20']]);assert '"A, Inc"' in csv and '"Quoted ""Name"""' in csv
def test_csv_width_validation():
 with pytest.raises(ValueError,match='header width'):render_csv(['A','B'],[['one']])
