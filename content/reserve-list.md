# Reserve List & Roster Events — dated capture (16 Nov 2026)
> Measured capture of the league's official transaction wire: who is on Reserve/Injured, who was traded, and which depth rows the wire proves stale. **"Not listed" on the weekly injury report never means "available"** (BL-65) — this page is the dataset that makes that rule enforceable.

Every row on this page was transcribed on 2026-11-16 from the league's own transactions pages and carries the month page it came from. The capture is a **dated window, not a full-season sweep**: the coverage register below states exactly which dates are in and which are still out, and no row outside the window is guessed.

## November 2026 reserve list (11/03–11/14 captured)

{{csv data/reserve_list_20261116_d304c6fe.csv;;cols=date:Date,club:Club,player:Player,transaction:Transaction,note:Note;;filter=month=2026-11;;source_col=source;;caption=35 rows read from the official November reserve-list page on 2026-11-16. The page was read twice and its tail once; the three reads agree row for row. Malik Willis (MIA, 11/10) is the case the brief names: he is absent from the weekly report because he is on reserve, not because he is healthy.}}

## October 2026 reserve list (10/24–10/31 captured)

{{csv data/reserve_list_20261116_d304c6fe.csv;;cols=date:Date,club:Club,player:Player,transaction:Transaction,note:Note;;filter=month=2026-10;;source_col=source;;caption=25 rows from the official October reserve-list page. The extraction returned rows down to 10/24; rows dated 10/01–10/23 were not returned and are **not captured** (FL-109). C.J. Gardner-Johnson's row is a commissioner suspension placement, not an injury placement — it is kept so the ledger is complete.}}

## November 2026 trades (complete month)

{{csv data/trades_20261116_d304c6fe.csv;;cols=date:Date,from_club:From,to_club:To,player:Player,note:Note;;source_col=source;;caption=All 12 rows the official November trades page published at read time. Two of them are the Colts starting-receiver moves the brief names (Keenan Allen to SF, Josh Downs to KC, both 11/10), and one is the replacement quarterback Baltimore traded in two days after its two quarterbacks went to reserve (Jacoby Brissett, AZ to BAL, 11/06).}}

## Capture coverage — what this dataset is and is not

{{csv data/reserve_coverage_d304c6fe.csv;;cols=month:Month,window_captured:Window captured,rows_captured:Rows,not_captured:Not captured,capture_method:Method,note:Note;;source_col=source;;caption=The honest boundary of the capture. The 32-team roster/IR sweep (BL-13) is **not** complete: August and September are uncaptured and October is partial. A team-level model must not be trusted against this file until the sweep is widened month by month on the same page.}}

## Depth rows the wire proves stale (BL-47, BL-34)

{{csv data/stale_depth_d304c6fe.csv;;cols=id:ID,club:Club,claim:Claim in the repository,official_evidence:Official evidence,evidence_date:Date,verdict:Verdict,action:Action;;source_col=source;;caption=Each verdict dates the staleness from the published transaction, not from a read of a club chart. The rule this table enforces: depth, availability and lineup evidence must be versioned against the last official roster event (BL-34), and a replacement is recorded only when the league announces it (BL-42) — never inferred from jersey order, experience or salary.}}

## Dated hub re-read — named-row deltas (16 Nov 2026)

{{csv data/hub_delta_d304c6fe.csv;;cols=id:ID,club:Club,player:Player,field:Field,value_2026_11_16:Value on 2026-11-16,prior_value:Prior value,prior_read_utc:Prior read,delta:Delta;;source_col=source;;caption=The rule of this project is to publish the delta, never the level (BL-21). Three findings from one dated read: the Lions designations BL-49 tracked as missing are now published by the league as Out, which closes BL-49 with official values; the TreVeyon Henderson conflict (FL-96) is **live-confirmed, not resolved** — two official states exist in one week and both are kept; and the hub still shows Week 10 on 16 November, so no Week 11 participation data exists on any official page yet.}}

## What this unlocks, and what it does not

- **Unlocked:** any availability read can now be joined against the reserve list first, so "absent from the report" is never again transcribed as "available" (BL-65).
- **Unlocked:** the stale-depth verdicts above are dated, sourced and reproducible (BL-47).
- **Not unlocked:** the full-season IR sweep (BL-13), the immutable multi-day snapshot pipeline (BL-29, BL-30) and inactive-list capture (BL-31) — those need scheduled capture, which a one-day session cannot produce. The gate they block is unchanged.
