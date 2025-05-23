import argparse
from pathlib import Path


def parse_arguments():
    parser = argparse.ArgumentParser(description="Ledger CLI LLM tool")
    parser.add_argument("path", type=Path, help="Path to the ledger file")

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    print(f"Processing ledger file: {args.path}")
