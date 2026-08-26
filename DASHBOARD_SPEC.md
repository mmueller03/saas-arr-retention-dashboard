# Dashboard build spec

Sheet-by-sheet instructions for building the workbook in **Tableau Desktop Public
Edition** (free, no expiry, saves `.twb`/`.twbx` locally, 15M row cap — this data is
8,259 rows).

Connect to all three CSVs in `data/` as separate data sources. They do not need to be
joined; each view below names the source it uses.

---

## The story the dashboard has to tell

Three beats, in this order. Every sheet exists to serve one of them.

1. **ARR grew fast, peaked at $11.4M in January 2022, then fell to $2.1M by 2024.**
2. **The fall is not a retention failure alone, it is an acquisition collapse.**
   New contract starts went 3,578 in 2021, to 491 in 2022, to 138 in 2023.
   New ARR went from $2.1M in 2021 to $12K in 2022.
3. **Churn amplified it.** 2022 lost $6.46M of a $11.44M opening base.
   Gross retention fell to 31%.

---

## Sheet 1 — ARR trend

**Source:** `arr_waterfall_by_year.csv`

- Columns: `year` (continuous, or discrete for clean labels)
- Rows: `beginning_arr`
- Mark: line, with circle markers
- Annotate the 2022 peak point with the value
- Format the axis as currency, no decimals, thousands separator

This is the establishing shot. Keep it uncluttered.

## Sheet 2 — ARR waterfall

**Source:** `arr_waterfall_by_year.csv`

The classic SaaS bridge. Tableau does not have a native waterfall, so:

- Pivot `new_arr`, `expansion_arr`, `contraction_arr`, `churn_arr` into a single
  measure using **Data > Pivot** on the CSV, giving `component` and `amount`
- Columns: `year`
- Rows: `SUM(amount)` set to **Running Total** via a table calculation
- Mark: Gantt Bar
- Size: `-SUM(amount)`
- Color: `component`, with green for new and expansion, red for contraction and churn

If the running-total waterfall fights you, a stacked bar of the four components per
year carries the same message and takes five minutes instead of thirty. Ship that
first, upgrade later.

## Sheet 3 — Retention rates

**Source:** `arr_waterfall_by_year.csv`

- Columns: `year`
- Rows: `gross_retention_rate` and `net_retention_rate` as a dual axis, synchronized
- Format both as percentages
- Add a reference line at 100% on net retention, because crossing below it is the
  moment expansion stopped covering churn

Note in a caption that 2018 and 2019 rates sit on a tiny base (under $1.2M) and are
volatile for that reason. Saying so is better than letting a reader trip over it.

## Sheet 4 — New contracts per year

**Source:** `subscription_transactions.csv`

- Columns: `YEAR(start_date)`
- Rows: `COUNT(transaction_id)`
- Mark: bar
- Color: `product_family`

This is the sheet that proves beat 2. It is the most important chart in the workbook
and it is also the simplest, which is usually how it goes.

## Sheet 5 — ARR by product family and region

**Source:** `subscription_transactions.csv`

- Columns: `YEAR(start_date)`
- Rows: `SUM(arr)`
- Color: `product_family`
- Detail or small multiples: `region`

Elite Plus and Classic are the only two families in this extract. Four regions:
North America, Europe, Latin America, Asia.

## Sheet 6 — Account owner performance

**Source:** `subscription_transactions.csv`

- Rows: `account_owner`, sorted descending by `SUM(arr)`
- Columns: `SUM(arr)`
- Mark: bar, with a `COUNTD(customer_name)` label
- Filter to the top 15 so it stays readable

Optional and the first thing to cut if the dashboard feels crowded.

---

## Assembly

One dashboard, 1200 x 900 or larger, laid out top to bottom:

- **Row 1:** four BAN tiles (big number, small label) — peak ARR $11.4M, current ARR
  $2.1M, 2022 gross retention 31%, new contracts 2023 (138)
- **Row 2:** Sheet 1 (ARR trend) full width
- **Row 3:** Sheet 2 (waterfall) beside Sheet 3 (retention)
- **Row 4:** Sheet 4 (new contracts) beside Sheet 5 (product and region)

Add `region` and `product_family` as dashboard filters applied to all sheets using
that source.

Give it a title that states the finding, not the subject. "ARR fell 82% from peak as
new business stopped" beats "ARR Dashboard".

---

## Publishing

Save locally as `.twbx` into `workbook/` in this repo, and publish to your Tableau
Public profile. Put the Tableau Public URL at the top of the README and on your
resume — for Tableau work the live interactive link is the portfolio piece, the file
is just the backup.

Export a PNG of the finished dashboard to `assets/dashboard.png` so the README shows
something without requiring a click.
