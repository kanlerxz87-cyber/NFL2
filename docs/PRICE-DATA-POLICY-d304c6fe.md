# NFL2 Price-Data Policy (BL-20)

**Status:** adopted · **Decided:** 2026-11-16 · **Deciding session:** `d304c6fe` · **Registration:** this file's git commit hash
**Authority:** owner brief, "Decide the price-data policy before any backtest is published" (BL-20); supersedes the unlabelled practice of computing against community archive prices (FL-10, FL-21, FL-29, FL-30).

## 1. Why this policy exists

The brief requires a price-snapshot store recording opening and closing numbers for every market we originate (BL-01), and forbids publishing backtests before the price-data policy is decided (BL-20). The repository currently holds community-archive prices (nfldata) whose **vintage is undocumented** — no capture time, no opening/closing definition, no licence (FL-21, FL-29, FL-30). Numbers computed against such prices cannot be called backtests. This policy decides the rules before any further backtest is published, and re-labels what already exists.

## 2. Binding rules

| # | Rule | Enforced by |
|---|---|---|
| P1 | Every price stored anywhere in this project carries: market id, market type, price, capture timestamp (UTC), source id, and a content hash of the captured payload. A row missing any of these is rejected by the build. | data pipeline + `tools/verify.py` row checks |
| P2 | **Opening price** = first price observed after the market opens. **Closing price** = last price observed before kickoff. Both are stored; neither is recomputed or interpolated. | price-snapshot store schema (§3) |
| P3 | Community-archive prices (nfldata et al.) are **comparison anchors only**. Every table, chart or grade computed against them carries an explicit "exploratory — unvintaged price" label. They are never a source of truth and never feed a leaderboard number. | site labelling + G-01 |
| P4 | No ROI, CLV or price-based performance number appears on the leaderboard until the price-snapshot store holds at least one full week of vintaged rows for the markets in question. Until then the cells stay blank and flagged (BL-01 blocked at G-01, G-07). | leaderboard build rules |
| P5 | Any backtest published before this policy is re-labelled exploratory wherever it appears (Fair-Line Lab archive comparisons, settled-page archive columns, pipeline outputs). The re-labelling does not delete the numbers; it removes their claim to be evidence. | integration session edits |
| P6 | If a price source cannot state its capture time, it is admitted only to the archive tier (source register tier C) and can never clear gate G-01. | `data/sources.csv` tiering |
| P7 | The store records every market we originate **from day one**, even while its first rows are being accumulated (BL-18): side, total, moneyline in that origination order. | origination lab |

## 3. Price-snapshot store schema (BL-01) — fixed by this policy

```
market_id        | league game id + market type (spread | total | moneyline)
side             | which outcome the price is quoted against
opening_price    | numeric, as quoted (American or decimal — the unit column records which)
opening_ts_utc   | first observation after market open
closing_price    | numeric, as quoted
closing_ts_utc   | last observation before kickoff
source_id        | registered source in data/sources.csv (tier A or approved B)
captured_by      | capture routine id + version
payload_sha256   | hash of the raw captured payload
```

A market row without both vintages is admitted as `partial` and can never clear G-01.

## 4. What this does not decide

- **Where prices are captured from** (Q-01/Q-02, operator data licensing). The policy governs treatment of whatever is captured; it does not authorize scraping operator content.
- **The definition of "beat the market"** — that is the proper-score/CLV leaderboard work (BL-37, BL-38, BL-60), which depends on this policy but is specified separately.

## 5. Pre-registration

This policy is frozen as of the commit that introduces it. Changing any rule above requires a new dated policy file and a new commit hash before any affected number is published — the same freeze rule the strategies follow (BL-70, DG-04).
