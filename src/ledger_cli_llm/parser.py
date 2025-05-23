import re
from dataclasses import dataclass
from typing import List


@dataclass
class LedgerEntry:
    id: int
    original_lines: List[str]
    is_transaction: bool

    def transform(self) -> List[str]:
        transformed_lines = [f"{self.id}\n"]  # Add the entry ID as the first line

        for line in self.original_lines:
            line = line.replace("UnknownPayee", "?")
            line = line.replace("UnknownAccount", "?")

            if line.startswith(" ") and line.strip().startswith(";"):
                synced_desc_match = re.search(
                    r"^\s*; SyncedDescription:\s+(.*?)$", line
                )
                if synced_desc_match:
                    transformed_line = re.sub(r"; SyncedDescription:", "; Info:", line)
                    transformed_lines.append(transformed_line)

                continue

            transformed_lines.append(line)

        return transformed_lines


def parse_ledger(content: str) -> List[LedgerEntry]:
    entries = []

    lines = content.splitlines(keepends=True)

    next_entry_id = 1

    i = 0
    while i < len(lines):
        # Check if this is a transaction line (starts with a date)
        is_transaction = bool(lines[i].strip() and lines[i].strip()[0].isdigit())

        # Collect all lines for this entry
        entry_lines = [lines[i]]
        i += 1

        # If it's a transaction, collect all indented lines that follow
        if is_transaction:
            while i < len(lines) and (not lines[i].strip() or lines[i][0].isspace()):
                entry_lines.append(lines[i])
                i += 1

        # Create entry object
        entries.append(
            LedgerEntry(
                id=next_entry_id,
                original_lines=entry_lines,
                is_transaction=is_transaction,
            )
        )
        next_entry_id += 1

    return entries
