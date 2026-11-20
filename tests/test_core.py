from decimal import Decimal

import pytest

from pharmastock.core import CountRow, StockRow, load_counts, load_erp, reconcile


def stock(quantity=10):
    return StockRow("A", "S", "Example", "B", "2028-01", quantity, Decimal(2500))


@pytest.mark.parametrize("actual,status,variance", [
    (10, "MATCH", 0), (7, "SHORTAGE", -3), (12, "EXCESS", 2),
])
def test_reconcile_status(actual, status, variance):
    row = reconcile([stock()], [CountRow("A", "S", "B", actual)])[0]
    assert row["status"] == status
    assert row["variance_quantity"] == variance
    assert row["variance_value_iqd"] == Decimal(variance * 2500)


def test_uncounted_not_assumed_zero():
    row = reconcile([stock()], [])[0]
    assert row["status"] == "UNCOUNTED"
    assert row["variance_quantity"] is None


def test_unexpected_count():
    row = reconcile([], [CountRow("A", "S", "B", 2)])[0]
    assert row["status"] == "UNEXPECTED"


def test_reject_duplicate_erp(tmp_path):
    p = tmp_path / "erp.csv"
    p.write_text("branch,sku,product,batch,expiry,quantity,unit_cost_iqd\n"
                 "A,S,Example,B,2028-01,10,1\nA,S,Example,B,2028-01,20,1\n")
    with pytest.raises(ValueError, match="duplicate"):
        load_erp(p)


def test_reject_negative_counts(tmp_path):
    p = tmp_path / "counts.csv"
    p.write_text("branch,sku,batch,quantity\nA,S,B,-1\n")
    with pytest.raises(ValueError, match="non-negative"):
        load_counts(p)


def test_reject_invalid_cost(tmp_path):
    p = tmp_path / "erp.csv"
    p.write_text("branch,sku,product,batch,expiry,quantity,unit_cost_iqd\n"
                 "A,S,Example,B,2028-01,10,NaN\n")
    with pytest.raises(ValueError, match="unit_cost_iqd"):
        load_erp(p)
