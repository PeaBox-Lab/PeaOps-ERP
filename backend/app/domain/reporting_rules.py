
from decimal import Decimal, ROUND_HALF_UP
ZERO=Decimal('0.00');TWOPLACES=Decimal('0.01')

def account_nature(account_type:str):
    value=(account_type or '').strip().lower().replace(' ','_')
    mapping={'asset':'debit','expense':'debit','cost_of_goods_sold':'debit','cogs':'debit','liability':'credit','equity':'credit','revenue':'credit','income':'credit'}
    if value not in mapping:raise ValueError(f'Unsupported account type for reporting: {account_type}')
    return mapping[value]

def natural_balance(account_type:str,debit:Decimal,credit:Decimal):
    debit=Decimal(debit);credit=Decimal(credit)
    return (debit-credit if account_nature(account_type)=='debit' else credit-debit).quantize(TWOPLACES)

def income_statement(rows:list[tuple[str,Decimal,Decimal]]):
    revenue=expenses=ZERO
    for account_type,debit,credit in rows:
        nature=account_nature(account_type);balance=natural_balance(account_type,debit,credit)
        if account_type.lower() in {'revenue','income'}:revenue+=balance
        elif nature=='debit':expenses+=balance
    return {'revenue':revenue,'expenses':expenses,'net_income':(revenue-expenses).quantize(TWOPLACES)}

def balance_sheet(rows:list[tuple[str,Decimal,Decimal]]):
    assets=liabilities=equity=ZERO
    for account_type,debit,credit in rows:
        value=natural_balance(account_type,debit,credit);kind=account_type.lower()
        if kind=='asset':assets+=value
        elif kind=='liability':liabilities+=value
        elif kind=='equity':equity+=value
    difference=(assets-liabilities-equity).quantize(TWOPLACES)
    return {'assets':assets,'liabilities':liabilities,'equity':equity,'difference':difference,'balanced':difference==ZERO}

def percentage(numerator:Decimal,denominator:Decimal):
    numerator=Decimal(numerator);denominator=Decimal(denominator)
    return ZERO if denominator==0 else (numerator/denominator*Decimal('100')).quantize(TWOPLACES,rounding=ROUND_HALF_UP)

def inventory_turnover(cogs:Decimal,opening_inventory:Decimal,closing_inventory:Decimal):
    average=(Decimal(opening_inventory)+Decimal(closing_inventory))/Decimal('2')
    return ZERO if average==0 else (Decimal(cogs)/average).quantize(TWOPLACES,rounding=ROUND_HALF_UP)

def days_outstanding(balance:Decimal,period_activity:Decimal,days:int):
    if days<=0:raise ValueError('Days must be positive')
    activity=Decimal(period_activity)
    return ZERO if activity==0 else (Decimal(balance)/activity*Decimal(days)).quantize(TWOPLACES,rounding=ROUND_HALF_UP)

def validate_report_parameters(report_type:str,parameters:dict):
    allowed={'income_statement','balance_sheet','trial_balance','ar_ageing','ap_ageing','sales_performance','procurement_performance','inventory_summary','integration_health'}
    if report_type not in allowed:raise ValueError('Unsupported report type')
    if not isinstance(parameters,dict):raise ValueError('Report parameters must be an object')
    return True

def csv_escape(value):
    text='' if value is None else str(value)
    return '"'+text.replace('"','""')+'"' if any(x in text for x in [',','"','\n']) else text

def render_csv(headers:list[str],rows:list[list]):
    widths=len(headers)
    if any(len(row)!=widths for row in rows):raise ValueError('CSV rows must match header width')
    return '\n'.join([','.join(csv_escape(x) for x in headers)]+[','.join(csv_escape(x) for x in row) for row in rows])+'\n'
