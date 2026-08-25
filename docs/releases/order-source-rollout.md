# Release Plan: `order_source` on `fct_revenue`

## Deploy steps

1. Add `order_source` column to `stg_orders`, nullable, no default writes yet — strategy: expand
   rollback: `ALTER TABLE stg_orders DROP COLUMN order_source`
   guards against: schema lock / migration collision with concurrent writers

2. Deploy loader change that populates `order_source` on newly ingested rows — strategy: rolling
   rollback: revert loader commit, redeploy previous image
   guards against: NULL `order_source` leaking into downstream mart logic

3. Backfill historical `order_source` via one-off batch job — strategy: expand
   rollback: re-run backfill job in "null-restore" mode (sets column back to NULL for the touched rows)
   guards against: mart classifying pre-cutover historical orders as `unknown`/miscategorized

4. Build `fct_revenue_v2` (source-split rewrite) into a parallel `green` schema; existing `fct_revenue` untouched — strategy: blue/green
   rollback: `DROP SCHEMA green CASCADE` (or drop `green.fct_revenue_v2`)
   guards against: the rewritten model producing wrong or drifted totals before anything depends on it

5. Deploy `revenue_by_source` DAG in shadow mode — it refreshes `green.fct_revenue_v2` and reconciles totals against `fct_revenue`, but nothing reads from it — strategy: canary
   rollback: pause DAG in Airflow UI (`airflow dags pause revenue_by_source`)
   guards against: reconciliation mismatches or DAG failures ever reaching a consumer

6. Point BI report #1 (of the two needing the breakdown) at `fct_revenue_v2` — strategy: canary
   rollback: metadata flip — set report's data source back to legacy `fct_revenue`
   guards against: broad blast radius if the new model is subtly wrong under real query patterns

7. Point BI report #2 at `fct_revenue_v2` once report #1 has been stable — strategy: rolling
   rollback: metadata flip — set report #2's data source back to legacy `fct_revenue`
   guards against: cutting over both reports at once, which would mask a report-specific issue

8. Contract: swap the `fct_revenue` alias to point at `fct_revenue_v2`; explicitly pin the legacy report to a frozen `fct_revenue_legacy` alias first — strategy: blue/green
   rollback: swap alias back — `fct_revenue` → old (blue) table
   guards against: legacy report silently inheriting the source-split schema/behavior it must not change

9. Decommission the old (blue) `fct_revenue` table; promote `revenue_by_source` from shadow/reconciliation mode to the sole owner of `fct_revenue` refreshes — strategy: in-place
   rollback: none — restore from last snapshot taken before this step (forward-fix territory)
   guards against: indefinite double-compute cost and drift between the blue and green copies

## Release-level summary

```
trigger to roll back: revenue_by_source reconciliation task fails (totals diverge from legacy fct_revenue beyond tolerance), or either BI report shows a revenue swing outside normal day-over-day range
```

`revert path: pause the revenue_by_source DAG (step 5's rollback) first to stop further bad writes, then metadata-flip any cutover BI report(s) back to legacy fct_revenue (step 6/7's rollback). If already past the alias swap, swap the fct_revenue alias back to the blue table (step 8's rollback) instead.`

`data remediation: rows written into green.fct_revenue_v2 by a bad DAG run are dropped and the table is rebuilt from the last good reconciled state — fct_revenue itself (blue) is untouched until step 8, so no remediation is needed there for any failure caught before the alias swap.`

`time window: any time before step 8 — pure rollback via DAG pause + metadata flip, no data loss. After step 8, revert is the alias swap-back, viable for as long as the blue table is kept (target: 24h bake). Once step 9 drops the blue table, forward-fix only.`

---

**2am playbook:** DAG fails mid-rollout → pause `revenue_by_source`, flip any already-cutover BI report(s) back to legacy `fct_revenue`. No data remediation needed if step 8 hasn't run yet.

**Release is finished:** after step 9 — blue `fct_revenue` table dropped, DAG is sole owner, both BI reports stable on `fct_revenue_v2`, legacy report confirmed unchanged on `fct_revenue_legacy`.