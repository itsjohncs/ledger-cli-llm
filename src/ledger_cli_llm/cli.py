import argparse
from pathlib import Path
from .parser import parse_ledger


def parse_arguments():
    parser = argparse.ArgumentParser(description="Ledger CLI LLM tool")
    parser.add_argument("path", type=Path, help="Path to the ledger file")

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    # Read the ledger file
    if not args.path.exists():
        print(f"Error: Ledger file not found: {args.path}")
        return

    with open(args.path, "r") as file:
        content = file.read()

    # Parse the ledger content
    entries = parse_ledger(content)

    # Print summary of parsed entries
    transaction_count = sum(1 for entry in entries if entry.is_transaction)
    print(f"Parsed {len(entries)} entries, including {transaction_count} transactions")

    # Print the first few transactions as an example
    print("\nExample transactions:")
    for entry in entries:
        if entry.is_transaction:
            print("Original:")
            print("".join(entry.original_lines))
            print("\nTransformed:")
            print("".join(entry.transform()))
            break
