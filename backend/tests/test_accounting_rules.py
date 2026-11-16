from decimal import Decimal
from app.domain.models import JournalEntry, JournalLine

def line(d="0", c="0"):
    return JournalLine(account_id=1, debit=Decimal(d), credit=Decimal(c))

def test_balanced_journal_posts():
    entry = JournalEntry(company_id=1, reference="T1", lines=[line("100", "0"), line("0", "100")])
    entry.post()
    assert entry.status == "posted"

def test_unbalanced_journal_fails():
    entry = JournalEntry(company_id=1, reference="T2", lines=[line("100", "0"), line("0", "99")])
    try:
        entry.post()
        assert False
    except ValueError:
        assert entry.status == "draft"
