# Price-data admission policy

**Policy ID:** P-PRICE-01  
**Version:** 1.0  
**Adopted:** 2026-11-16  
**Owner decision recorded by:** session `a095be15`  
**Status:** adopted for new admissions; existing archive is quarantined from validated performance claims

## Decision

A price may enter the **validated evaluation system of record** only when its source, meaning, timing, provenance, and permitted use are documented and reviewed before it is used to fit or score a strategy. If any of those facts are unknown, the price is retained only in a clearly identified research/quarantine area; it must not support a published backtest, CLV, ROI, EV, leaderboard rank, or strategy promotion.

The repository's currently inventoried community price archive is **research-only and not approved for validated evaluation**. The checked-in inventory records that the 2026 `spread_line`, `total_line`, moneyline, and odds fields have no documented open/close vintage, and that the schema does not define the moneyline/odds columns. Historical files named `closing_lines.csv`, `initial_lines.csv`, and `sc_lines.csv` do not provide a documented 2026 opening/closing pair. Their file names alone are not sufficient evidence of price timing. Keep these data and any calculations derived from them labeled exploratory; do not present them as validation or leaderboard evidence. See the [price archive inventory](../data/price_archive_a392.csv), the [upstream schema reference](https://github.com/nflverse/nfldata/blob/master/DATASETS.md), and source records [S-NFLDATA-ARCHIVE](../data/sources.csv) / [S-NFLDATA-SCHEMA](../data/sources.csv).

No price source is presumed eligible because it is public, popular, or used elsewhere. No operator page may be scraped into the system of record. A non-league source may be admitted only after its source-specific terms and the project's storage, analysis, and display permissions are explicitly reviewed and recorded. This is a governance rule, not a claim that any particular vendor grants those permissions or legal advice.

## Required evidence before admission

Each feed or historical archive must have a reviewed source record with all of the following:

1. Provider, product/feed, exact URL or contract reference, source tier, and review date.
2. Evidence of permitted collection, local retention, model use, derived-result publication, and any restrictions on raw-price display; unresolved terms mean **reject/quarantine**.
3. Market and selection definitions, including spread orientation, total, moneyline, player-prop identity/period/statistic, and settlement treatment where applicable.
4. Explicit price timestamp semantics and timezone. A provider-declared `open` is not interchangeable with first-observed; a provider-declared `close` is not interchangeable with last-observed.
5. Stable event and market identifiers, operator/provider identity, quote value, odds format, capture time in UTC, event start time, and source response or file hash. Missing values stay missing; do not impute timestamps, prices, market labels, or provider identity.
6. Documented coverage, known gaps, corrections/revisions, and an immutable provenance trail sufficient to reproduce the admitted dataset.
7. A versioned admission decision and a passing schema/drift check before any strategy consumes the feed.

## Opening, closing, and consensus conventions

- Preserve each eligible provider/operator quote as its own observation; never overwrite history with the latest quote.
- Record an **opening** number only when the source explicitly identifies an opening quote and provides the quote's timestamp or documented opening-time semantics. Otherwise `opening` remains blank.
- Record a **closing** number only when the source explicitly identifies the closing quote, or when an approved capture system records a final pre-kickoff observation under a pre-registered cutoff rule. Never use an after-kickoff observation as a close.
- Do not call a single operator quote a market consensus. A consensus requires a pre-registered provider set, common market/selection definition, and a documented as-of window; publish component count and dispersion with it. Do not combine quotes whose time or market definitions are incompatible.
- Keep line value, offered odds, vig-free probability (if derived), our fair line/probability, and residual in separate fields. Do not backfill one from another.
- A missing or stale quote is a data gap, not zero, no movement, or evidence of availability.

## Evaluation and publication boundary

- All admitted price data must be tagged as **training**, **validation**, **final holdout**, or **prospective paper/live** before use. The 136-game log remains a pre-registered outcome corpus; its existence does not make an unqualified price series eligible.
- **Never place backtest results on the live leaderboard.** The leaderboard may show only eligible prospective results after registered source, chronology, sample, price, settlement, and statistical gates pass.
- New price-dependent backtests, CLV, ROI, EV, and benchmark-relative skill claims may be published only after the source passes this policy and the evaluation is pre-registered. Existing archive-dependent diagnostics already present in the repository are a documented legacy exception for transparency only: they must be labeled **exploratory / unvalidated / excluded from the leaderboard**, must not be used for strategy selection or promotion, and must state why the price source is quarantined. They are not admitted backtests or evidence of a betting edge. Remove or relabel those legacy outputs rather than presenting them as current performance if this warning cannot be kept with them.
- Price-independent model research based only on officially sourced outcomes is not market-price evidence; it still requires pre-registration, chronological separation, and prominent research-only labeling until the project's validation gates pass.
- Prospective CLV requires an admitted, correctly timed close. ROI/EV requires the actual executable price, applicable settlement rules, and verified result. If any element is absent, publish no numeric score for that measure and flag the gap.
- Every published price-derived row must identify its source and capture/as-of time. Public pages should publish permitted derived analysis and links, not raw provider rows unless the reviewed terms explicitly allow that display.
- A source-term change, schema drift, timestamp anomaly, provenance break, or provider correction suspends new use until reviewed. Existing outputs are flagged and recalculated only from versioned inputs; do not silently replace historical observations.

## Current application

The decision is effective immediately. The repository inventory identifies the nflverse/nfldata archive as community-sourced rather than league-official and documents unresolved vintage/schema questions. Therefore it remains quarantined from **validated backtest, CLV, ROI, EV, leaderboard, and promotion claims** until a source-specific review and complete admission record are added. This does not delete it or prevent clearly labeled exploratory diagnostics. The official NFL/Football Operations URLs checked in the source inventory did not provide an eligible price feed; an official NFL source is not required if a non-league source passes the documented permission and data-quality review.

**This policy does not assert that a specific provider has approved storage or republication.** No such approval is recorded here. The next clearing evidence is an approved source record plus an immutable sample that passes the requirements above.
