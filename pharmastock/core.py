"""Validation and reconciliation of ERP stock against physical counts."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


@dataclass(frozen=True)
class StockRow:
    branch: str
    sku: str
    product: str
    batch: str
    expiry: str
    quantity: int
    unit_cost_iqd: Decimal


@dataclass(frozen=True)
class CountRow:
    branch: str
    sku: str
    batch: str
    quantity: int


def _read(path: str | Path, required: set[str]) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"CSV must contain columns: {', '.join(sorted(required))}")
        return list(reader)


def _quantity(raw: str, line: int) -> int:
    try:
        value = int(raw)
        if value < 0:
            raise ValueError
        return value
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Row {line}: quantity must be a non-negative integer") from exc


def _text(raw: str | None, line: int, name: str) -> str:
    value = (raw or "").strip()
    if not value:
        raise ValueError(f"Row {line}: {name} is required")
    return value


def load_erp(path: str | Path) -> list[StockRow]:
    required = {"branch", "sku", "product", "batch", "expiry", "quantity", "unit_cost_iqd"}
    result = []
    seen = set()
    for line, row in enumerate(_read(path, required), 2):
        branch, sku, batch = (_text(row[k], line, k) for k in ("branch", "sku", "batch"))
        key = (branch, sku, batch)
        if key in seen:
            raise ValueError(f"Row {line}: duplicate ERP key {key}")
        seen.add(key)
        try:
            cost = Decimal(_text(row["unit_cost_iqd"], line, "unit_cost_iqd"))
            if not cost.is_finite() or cost < 0:
                raise ValueError
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Row {line}: unit_cost_iqd must be non-negative") from exc
        result.append(StockRow(branch, sku, _text(row["product"], line, "product"),
                               batch, _text(row["expiry"], line, "expiry"),
                               _quantity(row["quantity"], line), cost))
    return result


def load_counts(path: str | Path) -> list[CountRow]:
    required = {"branch", "sku", "batch", "quantity"}
    result = []
    seen = set()
    for line, row in enumerate(_read(path, required), 2):
        branch, sku, batch = (_text(row[k], line, k) for k in ("branch", "sku", "batch"))
        key = (branch, sku, batch)
        if key in seen:
            raise ValueError(f"Row {line}: duplicate count key {key}")
        seen.add(key)
        result.append(CountRow(branch, sku, batch, _quantity(row["quantity"], line)))
    return result


def reconcile(erp: list[StockRow], counts: list[CountRow]) -> list[dict]:
    """Compare by branch+SKU+batch; absent counts are UNCOUNTED, never zero."""
    erp_by_key = {(r.branch, r.sku, r.batch): r for r in erp}
    count_by_key = {(r.branch, r.sku, r.batch): r for r in counts}
    rows = []
    for key in sorted(erp_by_key.keys() | count_by_key.keys()):
        expected = erp_by_key.get(key)
        counted = count_by_key.get(key)
        if expected is None:
            status, variance, value = "UNEXPECTED", None, None
        elif counted is None:
            status, variance, value = "UNCOUNTED", None, None
        else:
            variance = counted.quantity - expected.quantity
            status = "MATCH" if variance == 0 else ("EXCESS" if variance > 0 else "SHORTAGE")
            value = Decimal(variance) * expected.unit_cost_iqd
        rows.append({
            "branch": key[0], "sku": key[1], "batch": key[2],
            "product": expected.product if expected else "UNKNOWN",
            "expiry": expected.expiry if expected else "",
            "erp_quantity": expected.quantity if expected else None,
            "counted_quantity": counted.quantity if counted else None,
            "variance_quantity": variance, "variance_value_iqd": value,
            "status": status,
        })
    return rows
