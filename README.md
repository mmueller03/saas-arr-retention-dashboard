# SaaS ARR & Retention Dashboard

A Tableau dashboard over seven years of subscription contracts for a health and
wellness SaaS business, tracking annual recurring revenue, the ARR waterfall, and
gross and net retention.

> **Status:** data and analysis complete and verified. The Tableau workbook is in
> progress; this README will carry the Tableau Public link once it is published.

---

## The finding

ARR grew from under $5K to a peak of **$11.4M in January 2022**, then fell to
**$2.1M by January 2024**, an 82% decline from peak.

The decline reads as a churn problem and it is not, or not only. It is an
acquisition collapse:

| Year | New contracts signed | New ARR | Gross retention |
|---:|---:|---:|---:|
| 2020 | 2,356 | $6.11M | 30.8% |
| 2021 | 3,578 | $2.13M | 67.5% |
| 2022 | 491 | $0.01M | 31.4% |
| 2023 | 138 | $0.00M | 44.3% |

New business essentially stopped after 2021. New contract starts fell 86% in a
single year, and new ARR went from $2.13M to $12K. Churn then did the rest: 2022
lost **$6.46M off an opening base of $11.44M**.

Net revenue retention tells the same story from the other side. It held above 100%
in 2020 and 2021, meaning expansion within existing customers more than covered
what churned. In 2022 it fell to 37%, and there was no new business coming in
behind it to compensate.

This lines up with the diagnosis in the
[Optima Life capstone](https://github.com/mmueller03/optima-life-presentation):
the growth problem was acquisition, not retention. This extract covers two of the
five product families, so its retention rates run lower than the portfolio-level
figures in that deck.

---

## Reproducing the numbers

`scripts/prep_arr_data.py` computes ARR per contract, snapshots each customer's ARR
at January 1 of each year, and derives the waterfall from consecutive snapshots.

It checks itself against the published summary table before writing anything:

```bash
python scripts/prep_arr_data.py --source "path/to/subscription data with customer ARR.xlsx"
```

```
Beginning ARR check (derived vs published)
  2018  derived        4,930.5   published        4,930.5   diff  0.00%
  2019  derived    1,191,245.7   published    1,191,245.7   diff  0.00%
  2020  derived    2,109,183.9   published    2,109,183.8   diff  0.00%
  2021  derived    8,344,391.8   published    8,344,391.6   diff  0.00%
  2022  derived   11,435,763.9   published   11,435,764.0   diff  0.00%
  2023  derived    4,244,741.0   published    4,244,741.0   diff  0.00%
  2024  derived    2,097,610.4   published    2,097,610.4   diff  0.00%
  worst difference: 0.00%
```

All seven years reproduce the published totals exactly, so the dashboard is built on
checked numbers rather than a spreadsheet nobody re-derived. Requires `openpyxl`.

### A check worth mentioning

A drop that steep is usually a truncated extract rather than a real decline, so that
was tested before writing any of it up. The data is not truncated: contract end dates
run through 2026 and start dates through August 2024. The collapse in new business is
in the data, not an artifact of where the export stopped.

---

## What's here

```
data/
  subscription_transactions.csv   8,259 contracts: customer, dates, product, region,
                                  account owner, bookings, term length, computed ARR
  customer_arr_by_year.csv        3,028 customer-year ARR snapshots at Jan 1
  arr_waterfall_by_year.csv       6 years: beginning, new, expansion, contraction,
                                  churn, ending ARR, plus gross and net retention

scripts/prep_arr_data.py          builds and verifies all three CSVs
DASHBOARD_SPEC.md                 sheet-by-sheet Tableau build instructions
```

## Definitions

- **ARR** — contract bookings annualized over the term: `bookings x 365 / term_days`.
  Zero-day terms are same-day cancellations and carry no recurring revenue.
- **Snapshot** — a customer's ARR on a date is the sum of ARR across their contracts
  active on that date.
- **Gross retention** — `(beginning + contraction + churn) / beginning`. Cannot
  exceed 100%.
- **Net retention** — `(beginning + expansion + contraction + churn) / beginning`.
  Above 100% means growth from existing customers alone.

Data is synthetic coursework data from GB895 (M.S. Business Analytics, UW-Madison);
customer and account owner names are generated, not real.

**Michael Mueller** — [github.com/mmueller03](https://github.com/mmueller03)
