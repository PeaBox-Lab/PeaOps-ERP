"""Period-close guard: rejects postings into closed or locked fiscal periods."""
from sqlalchemy.orm import Session
from app.domain.models import FiscalPeriod

CLOSED_STATUSES = {"closed", "locked"}

def find_blocked_period(db: Session, company_id: int, at_date) -> FiscalPeriod | None:
    """Return the fiscal period containing at_date whose status blocks posting, or None."""
    if at_date is None:
        return None
    period = db.query(FiscalPeriod).filter(
        FiscalPeriod.company_id == company_id,
        FiscalPeriod.start_date <= at_date,
        FiscalPeriod.end_date >= at_date,
    ).first()
    if period and period.status in CLOSED_STATUSES:
        return period
    return None

class PeriodClosed(Exception):
    def __init__(self, period):
        self.period = period
        super().__init__(f"Period {period.code} is {period.status} and does not accept postings")