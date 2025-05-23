from ledger_cli_llm.parser import parse_ledger


def test_parse_empty_content():
    """Test parsing empty ledger content."""
    entries = parse_ledger("")
    assert len(entries) == 0

    # Test with a single empty line
    entries = parse_ledger("\n")
    assert len(entries) == 1
    assert not entries[0].is_transaction
    assert entries[0].original_lines == ["\n"]


def test_parse_simple_transaction():
    """Test parsing a simple transaction."""
    content = """2023/01/01 Payee
    Expenses:Food    $10.00
    Assets:Checking
"""

    entries = parse_ledger(content)

    assert len(entries) == 1
    assert entries[0].is_transaction
    assert len(entries[0].original_lines) == 3
    assert entries[0].original_lines[0] == "2023/01/01 Payee\n"
    assert entries[0].original_lines[1] == "    Expenses:Food    $10.00\n"
    assert entries[0].original_lines[2] == "    Assets:Checking\n"


def test_parse_empty_lines():
    """Test parsing content with empty lines."""
    content = "\n\n\n"
    entries = parse_ledger(content)

    assert len(entries) == 3
    for entry in entries:
        assert not entry.is_transaction
        assert entry.original_lines == ["\n"]


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

    # First entry is an account declaration (non-transaction)
    assert not entries[0].is_transaction
    assert entries[0].original_lines[0] == "account Assets:Checking\n"

    assert not entries[1].is_transaction
    assert entries[1].original_lines[0] == "\n"

    # Transactions swallow up the empty lines following them
    assert entries[2].is_transaction
    assert entries[2].original_lines[0] == "2023/01/01 Grocery Store\n"
    assert len(entries[2].original_lines) == 4

    assert not entries[3].is_transaction
    assert entries[3].original_lines[0] == "; Comment line\n"

    assert entries[4].is_transaction
    assert entries[4].original_lines[0] == "2023/01/02 Restaurant\n"
    assert len(entries[4].original_lines) == 3

    assert len(entries) == 5


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
    assert len(entries[0].original_lines) == 4
    assert "; Transaction comment" in entries[0].original_lines[0]
    assert entries[0].original_lines[1] == "    ; Posting comment\n"
    assert "; Amount comment" in entries[0].original_lines[2]


def test_transform_unknown_replacements():
    """Test the transform function replaces UnknownPayee and UnknownAccount with ?."""
    content = """2023/01/01 UnknownPayee
    UnknownAccount    $10.00
    Assets:Checking
"""

    entries = parse_ledger(content)
    transformed_lines = entries[0].transform()

    assert transformed_lines[0] == "1\n"  # First line is the entry ID
    assert "2023/01/01 ?" in transformed_lines[1]
    assert "?    $10.00" in transformed_lines[2]

    # Verify the original lines are unchanged
    assert "UnknownPayee" in entries[0].original_lines[0]
    assert "UnknownAccount" in entries[0].original_lines[1]


def test_transform_metadata_handling():
    """Test the transform function handles metadata lines correctly."""
    content = """2023/01/01 Payee
    ; SyncedDescription: Original purchase
    ; Metadata: Should be removed
    Assets:Checking
"""

    entries = parse_ledger(content)
    transformed_lines = entries[0].transform()

    # SyncedDescription should be kept but renamed to Info
    assert len(transformed_lines) == 4  # +1 for the ID line
    assert transformed_lines[0] == "1\n"  # First line is the entry ID
    assert "; Info: Original purchase" in transformed_lines[2]

    # Other metadata should be removed
    assert all("Metadata: Should be removed" not in line for line in transformed_lines)

    # Test with a line that has SyncedDescription as part of another word
    content2 = """2023/01/01 Payee
    ; NotSyncedDescription: Should be removed
    Assets:Checking
"""
    entries2 = parse_ledger(content2)
    transformed_lines2 = entries2[0].transform()

    # The metadata line should be removed
    assert len(transformed_lines2) == 3  # +1 for the ID line
    assert transformed_lines2[0] == "1\n"  # First line is the entry ID
    assert all("NotSyncedDescription" not in line for line in transformed_lines2)
