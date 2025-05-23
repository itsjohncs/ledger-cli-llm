from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LedgerEntry:
    """
    Represents any entry in a ledger file, preserving the original text.
    """
    lines: List[str]
    is_transaction: bool


def parse_ledger(content: str) -> List[LedgerEntry]:
    """
    Parse ledger content and return a list of LedgerEntry objects.
    
    Args:
        content: String containing ledger content
        
    Returns:
        List of LedgerEntry objects, preserving the original text
    """
    entries = []
    
    lines = content.splitlines(keepends=True)
    
    i = 0
    while i < len(lines):
        # Skip empty lines
        if not lines[i].strip():
            i += 1
            continue
        
        # Check if this is a transaction line (starts with a date)
        is_transaction = lines[i].strip() and lines[i].strip()[0].isdigit()
        
        # Collect all lines for this entry
        entry_lines = [lines[i]]
        i += 1
        
        # If it's a transaction, collect all indented lines that follow
        if is_transaction:
            while i < len(lines) and (not lines[i].strip() or lines[i][0].isspace()):
                if lines[i].strip():  # Skip empty lines
                    entry_lines.append(lines[i])
                i += 1
        
        # Create entry object
        entries.append(LedgerEntry(
            lines=entry_lines,
            is_transaction=is_transaction
        ))
    
    return entries
