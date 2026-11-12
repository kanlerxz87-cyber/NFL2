# Price Archive — what the repository actually holds
> The register used to say there were no prices in this project. There are. This page states exactly what they are, what they prove, and what they still cannot be used for.

The brief's central ask — *originate our own lines* — needs a benchmark, so the availability of price data is the single most decision-relevant fact in the project. The canonical flag on this used to read "no price data of any kind". That is no longer true and this page is the correction: `pipeline/data/raw/` (vendored and SHA-256 pinned by a parallel session) carries market prices, and a second tree in this repository has already run a calibration against them.

{{csv data/price_archive_a392.csv;;cols=asset:Asset,rows_2026:2026 rows,seasons:Seasons covered,what_it_proves:What it proves,what_it_does_not_prove:What it does not prove,official:Official?;;source_col=source;;caption=Inventory produced by reading the files themselves, not their names. The file called closing_lines.csv stops at 2018; the file called games.csv is the only one carrying a 2026 price, and it holds 163 of them.}}

## The three things a reader must not conclude

1. **"Closing line" is a file name, not a verified property.** The upstream schema document for `games.csv` defines `spread_line` and `total_line` — and has not been updated since **13 May 2020** — but it never says whether those numbers are the open or the close, and it does not document the moneyline and spread-odds columns at all. So a CLV statistic computed against this column is measuring *something*, and we cannot yet say what. Published as [FL-30](flagged-for-review.html); the decision it forces is [Q-35](questions.html).
2. **No official source for prices exists, and never will.** The league publishes standings, schedules, participation and designations; it does not publish betting lines. Any price on this site is therefore tier-B-or-worse by construction, and the build marks every non-official link inline so a reader can never mistake a community number for a league one.
3. **Prices are historical, not live.** Nothing in this repository is a feed. The `data_fetched` timestamp on every page is the whole of our freshness story, and the archive is a snapshot of a snapshot: a pinned commit of a third-party redistribution of publicly aggregated data.

## What the archive does unlock

A **walk-forward benchmark**. The [origination lab](model-lab.html) scores our line and the archived line on the *same games*, which is the only comparison that survives the missing-price problem: 88 of 136 games carry an archived price, so the paired difference is reported instead of two unpaired means.

It also unlocks a second, cheaper verification that matters more than it looks: the archive transcribed the same 136 results independently of the nfl.com game pages, and after the club-code alias is applied, **136 of 136 scores agree cell for cell, zero disagree**. Two transcriptions that never met each other agreeing on every final score is the strongest evidence in this repository that the game log everything else joins to is clean.

And it exposes a defect that would have been invisible: joining the two sources by team code without an alias table **silently drops all nine Arizona Cardinals games** (`ARI` vs `AZ`), and mis-keys the Rams (`LA` vs `LAR`). Any model trained that way loses a club and still prints an error rate. The fix and the check are in [FL-28](flagged-for-review.html) and [S-36](suggestions.html).

## What is still missing to originate properly

| Need | Why this archive is not enough | Where it is tracked |
| --- | --- | --- |
| Point-in-time open *and* close, with a capture timestamp | a single undocumented column cannot separate "the market moved" from "the vendor's snapshot date" | [Q-01](questions.html), gate G-01 |
| Player-prop prices | no prop line exists in any file here, so the prop-combo and SGP correlations stay blank | [Q-12](questions.html), [Correlation](correlation.html) |
| A licence and an owner decision on tier | the legal and cost question precedes the technical one | [Q-01](questions.html) |
| Historical injuries and participation, to test availability signals | our injury register begins at week 10 of 2026; there is no history to join a price to | [S-35](suggestions.html), gate G-03 |

Until the first two are answered, the site publishes model output as **a diagnostic with an error bar**, never as a line to bet, and the leaderboard stays at zero settled bets for every entry ([Leaderboard & rewards](leaderboard.html)).
