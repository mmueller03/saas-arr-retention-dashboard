"""Build the Tableau-ready CSVs from the source subscription workbook.

Reads the transaction-level data, computes annual recurring revenue per row,
snapshots each customer's ARR at January 1 of each year, and derives the ARR
waterfall (new / expansion / contraction / churn) from those snapshots.

Verifies the derived snapshots against the published summary table before writing,
so the numbers behind the dashboard are reproducible rather than asserted.

    python scripts/prep_arr_data.py --source "path/to/subscription data.xlsx"
"""

import argparse
import collections
import csv
import datetime
import io
import pathlib

import openpyxl

OUT = pathlib.Path(__file__).resolve().parent.parent / "data"

# Published "Beginning ARR" row from the course summary workbook
# ("customer ARR trend - Summary table with retention rates - completed.xlsx"),
# used as an independent check on the snapshot logic below.
PUBLISHED = {
    2018: 4930.5,
    2019: 1191245.7,
    2020: 2109183.8,
    2021: 8344391.6,
    2022: 11435764.0,
    2023: 4244741.0,
    2024: 2097610.4,
}
YEARS = list(range(2018, 2025))


def load_transactions(src):
    """One dict per transaction, with ARR computed from bookings and term length."""
    wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
    rows = list(wb["data"].iter_rows(values_only=True))
    header = [str(h).strip() for h in rows[0]]
    out = []
    for raw in rows[1:]:
        rec = dict(zip(header, raw))
        start, end = rec["Start Date"], rec["End Date"]
        if not isinstance(start, datetime.datetime) or not isinstance(end, datetime.datetime):
            continue
        days = (end - start).days
        bookings = rec["Bookings"] or 0
        # A zero-day term is a same-day cancellation and carries no recurring revenue.
        arr = bookings * 365 / days if days else 0.0
        out.append(
            {
                "transaction_id": rec["Transaction ID"],
                "customer_name": rec["Customer Name"],
                "start_date": start.date(),
                "end_date": end.date(),
                "product_family": rec["Product Family"],
                "region": rec["Location"],
                "account_owner": rec["Account Owner"],
                "bookings": round(bookings, 2),
                "term_days": days,
                "arr": round(arr, 2),
            }
        )
    return out


def snapshot(transactions, asof):
    """{customer: ARR} for contracts active on `asof`."""
    totals = collections.defaultdict(float)
    for t in transactions:
        if t["term_days"] and t["start_date"] <= asof <= t["end_date"]:
            totals[t["customer_name"]] += t["arr"]
    return totals


def waterfall(prev, cur):
    """New / expansion / contraction / churn between two customer ARR snapshots."""
    new = expansion = contraction = churn = 0.0
    for cust in set(prev) | set(cur):
        before, after = prev.get(cust, 0.0), cur.get(cust, 0.0)
        if before == 0:
            new += after
        elif after == 0:
            churn -= before
        elif after > before:
            expansion += after - before
        elif after < before:
            contraction -= before - after
    return new, expansion, contraction, churn


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        required=True,
        help="path to the source subscription workbook (.xlsx)",
    )
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    tx = load_transactions(args.source)
    print(f"transactions: {len(tx)}")

    snapshots = {y: snapshot(tx, datetime.date(y, 1, 1)) for y in YEARS}

    print("\nBeginning ARR check (derived vs published)")
    worst = 0.0
    for y in YEARS:
        derived = sum(snapshots[y].values())
        pub = PUBLISHED[y]
        diff = abs(derived - pub) / pub * 100 if pub else 0.0
        worst = max(worst, diff)
        print(f"  {y}  derived {derived:>14,.1f}   published {pub:>14,.1f}   diff {diff:5.2f}%")
    print(f"  worst difference: {worst:.2f}%")

    with io.open(OUT / "subscription_transactions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tx[0].keys()))
        w.writeheader()
        w.writerows(tx)

    with io.open(OUT / "customer_arr_by_year.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["customer_name", "year", "asof_date", "arr"])
        for y in YEARS:
            for cust, arr in sorted(snapshots[y].items()):
                w.writerow([cust, y, f"{y}-01-01", round(arr, 2)])

    with io.open(OUT / "arr_waterfall_by_year.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["year", "beginning_arr", "new_arr", "expansion_arr",
             "contraction_arr", "churn_arr", "ending_arr",
             "gross_retention_rate", "net_retention_rate"]
        )
        for y in YEARS[:-1]:
            prev, cur = snapshots[y], snapshots[y + 1]
            begin = sum(prev.values())
            end = sum(cur.values())
            new, exp, con, chn = waterfall(prev, cur)
            grr = (begin + con + chn) / begin if begin else 0.0
            nrr = (begin + exp + con + chn) / begin if begin else 0.0
            w.writerow(
                [y, round(begin, 2), round(new, 2), round(exp, 2), round(con, 2),
                 round(chn, 2), round(end, 2), round(grr, 4), round(nrr, 4)]
            )

    for name in ("subscription_transactions.csv", "customer_arr_by_year.csv",
                 "arr_waterfall_by_year.csv"):
        path = OUT / name
        lines = sum(1 for _ in io.open(path, encoding="utf-8")) - 1
        print(f"wrote {name}: {lines} rows")


if __name__ == "__main__":
    main()
