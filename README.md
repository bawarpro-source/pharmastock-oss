# PharmaStock OSS

**A privacy-conscious, open-source pharmacy inventory reconciliation CLI.**

PharmaStock OSS compares an ERP inventory snapshot against physical counts by **branch + SKU + batch**, and reports quantity differences and their monetary value in Iraqi dinars (IQD). It is an early-stage **MVP**, not a production pharmacy system.

> [!IMPORTANT]
> Use **fictional data** in public issues and examples. Do not upload real patient information, confidential supplier prices, or private pharmacy stock files to GitHub.

## Features (v0.1.0)

- CSV-based ERP and physical count import
- Batch-level matching across multiple branches
- `MATCH`, `SHORTAGE`, `EXCESS`, `UNCOUNTED`, and `UNEXPECTED` statuses
- IQD variance values calculated using Python `Decimal`
- Validation of required columns, duplicate keys, quantities and costs
- No third-party runtime dependencies, accounts, or external data transfers

## Quick start

Requires Python 3.10+.

```bash
python -m pip install -e .
python -m pharmastock --erp sample_data/erp.csv --counts sample_data/counts.csv --output reconciliation.csv
```

Or use the installed `pharmastock` command instead of `python -m pharmastock`.

## Input CSV schemas

**ERP:** `branch,sku,product,batch,expiry,quantity,unit_cost_iqd`

**Counts:** `branch,sku,batch,quantity`

- Quantities are **non-negative integers** in a single, consistent counting unit (e.g. packets). Do not mix packets and sheets.
- `unit_cost_iqd` is the cost per same counting unit, not a selling price.
- Branch, SKU and batch are case-sensitive identifiers.
- `expiry` is carried through as a label; date validity is not yet checked.
- Missing counts are marked `UNCOUNTED` and **must not** be interpreted as zero stock.
- Counted items absent from the ERP snapshot are marked `UNEXPECTED`; their value cannot be calculated.
- Changes due to sales, purchases or transfers between ERP export and physical count are **not** adjusted in this MVP.

## Test

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
ruff check .
```

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md). Contributions welcome: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Scope and safety

This tool is for **inventory review**, not clinical decision-making, dispensing, medication substitution, or patient care. Independently verify stock discrepancies before operational changes. Do not use for regulated production workflows without appropriate security review, validation, audit trails and access controls.

## Licence

MIT — see [LICENSE](LICENSE).
