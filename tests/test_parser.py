import pytest
from pathlib import Path
from ledger_cli_llm.parser import parse_ledger


def test_parse_empty_content():
    """Test parsing empty ledger content."""
    entries = parse_ledger("")
    assert len(entries) == 0


def test_parse_simple_transaction():
    """Test parsing a simple transaction."""
    content = """2023/01/01 Payee
    Expenses:Food    $10.00
    Assets:Checking
"""

    entries = parse_ledger(content)

    assert len(entries) == 1
    assert entries[0].is_transaction
    assert len(entries[0].lines) == 3
    assert entries[0].lines[0] == "2023/01/01 Payee\n"
    assert entries[0].lines[1] == "    Expenses:Food    $10.00\n"
    assert entries[0].lines[2] == "    Assets:Checking\n"


def test_parse_multiple_entries():
    """Test parsing multiple entries including transactions and non-transactions."""
    content = """account Assets:Checking
    
2023/01/01 Grocery Store
    Expenses:Food    $50.00
    Assets:Checking

; Comment line
2023/01/02 Restaurant
    Expenses:Food    $25.00
    Assets:Checking
"""

    entries = parse_ledger(content)

    assert len(entries) == 4

    # First entry is an account declaration (non-transaction)
    assert not entries[0].is_transaction
    assert entries[0].lines[0] == "account Assets:Checking\n"

    # Second entry is a transaction
    assert entries[1].is_transaction
    assert entries[1].lines[0] == "2023/01/01 Grocery Store\n"
    assert len(entries[1].lines) == 3

    # Third entry is a comment (non-transaction)
    assert not entries[2].is_transaction
    assert entries[2].lines[0] == "; Comment line\n"

    # Fourth entry is a transaction
    assert entries[3].is_transaction
    assert entries[3].lines[0] == "2023/01/02 Restaurant\n"
    assert len(entries[3].lines) == 3


def test_transaction_with_comments():
    """Test parsing a transaction with inline comments."""
    content = """2023/01/01 Payee  ; Transaction comment
    ; Posting comment
    Expenses:Food    $10.00  ; Amount comment
    Assets:Checking
"""

    entries = parse_ledger(content)

    assert len(entries) == 1
    assert entries[0].is_transaction
    assert len(entries[0].lines) == 4
    assert "; Transaction comment" in entries[0].lines[0]
    assert entries[0].lines[1] == "    ; Posting comment\n"
    assert "; Amount comment" in entries[0].lines[2]
