"""Command-line entry point for PharmaStock OSS."""
import argparse
import csv
import sys
from pathlib import Path

from .core import load_counts, load_erp, reconcile


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compare pharmacy ERP stock with physical counts")
    parser.add_argument("--erp", required=True, help="ERP CSV path")
    parser.add_argument("--counts", required=True, help="Physical count CSV path")
    parser.add_argument("--output", default="reconciliation.csv", help="Output CSV path")
    args = parser.parse_args(argv)
    try:
        results = reconcile(load_erp(args.erp), load_counts(args.counts))
        output = Path(args.output)
        if output.resolve() in {Path(args.erp).resolve(), Path(args.counts).resolve()}:
            raise ValueError("Output must not overwrite either input file")
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "branch", "sku", "batch", "product", "expiry", "erp_quantity",
                "counted_quantity", "variance_quantity", "variance_value_iqd", "status",
            ])
            writer.writeheader()
            writer.writerows(results)
        print(f"Wrote {len(results)} reconciliation rows to {output}")
        return 0
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
