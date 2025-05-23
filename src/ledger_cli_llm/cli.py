import argparse
from pathlib import Path
from .parser import parse_ledger
import sys


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

    for entry in entries:
        sys.stdout.write("".join(entry.transform()))
