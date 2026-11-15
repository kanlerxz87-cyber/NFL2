# Strategy falsification review (session `f05c00f2`)

This is a **standalone review companion**, not a replacement for the canonical strategy register. It covers all 15 IDs currently in `data/strategies.csv` and gives each a two-sided test proposal: what future evidence would support the thesis, and what would make us retire or re-scope it. The page is published as [`index.html`](index.html) under the repository's static-site root.

## Rebuild and verify

```sh
python3 audits/f05c00f2/build.py          # validate IDs and render the page
python3 audits/f05c00f2/build.py --check  # verify without writing
```

The builder checks exact one-to-one coverage and order against `data/strategies.csv`, verifies strategy name/type/market fields, requires both sides of each test, rejects non-official URLs in the official-input column, flags absent links, copies registered blocking gates without remapping them, and emits deterministic HTML. The input strategy-register SHA-256 is visible in the page.

## Source class and limits

- The strategy names and hypotheses are **project design**, sourced from `data/strategies.csv`; they are not official NFL facts.
- NFL URLs are only pointers to possible input evidence. A page link does not show that the relevant historical series was retained, that an input is complete, or that a strategy works.
- This task did not re-fetch NFL pages or make new NFL factual claims. Use `data/sources.csv`, the dated verification artifacts, and `data/flags.csv` to review what the repository actually captured.
- Empty official-input URLs remain empty and carry an `UNVERIFIED` or `NOT APPLICABLE` label. This is deliberate for price and ticket/settlement sources not recorded in the project.
- No backtest values, forecast results, probability outputs, win rates, ROI, CLV, stakes, ranks, or rewards are included. Nothing here validates or authorizes staking.
- The criteria are proposals, not new numeric gates. They do not replace the current registered gate definitions or the requirement to pre-register the comparator, sample window, scoring rule, uncertainty procedure, and multiplicity family before evaluation.

## Open integration request

Suggestion S-21 already asks for a two-sided “what would change our mind” field, but the canonical `data/strategies.csv` schema and `strategies.html` do not yet render a per-entry falsifier. Change request **CR-F05-01** asks the final integrator to add the positive-evidence and falsifier fields to the canonical register and page, then enforce strategy-ID coverage in CI. This session does not edit shared root data, navigation, or generated root pages while another integration PR is active.

## Manual-review links

- [Canonical strategy register](../../data/strategies.csv) — project design.
- [Validation gates](../../data/gates.csv) — project design; no gate status is changed here.
- [Suggestion S-21 and review queue](../../suggestions.html) — project decision context.
- [Official NFL injury hub](https://www.nfl.com/injuries/) — potential availability input; not a retained history by itself.
- [Official NFL game centre](https://www.nfl.com/games/) — entry point for per-game results/gamebooks; not a complete snap-count or prop-price source.
- [Official NFL schedule](https://www.nfl.com/schedules/2026/by-week/week-10) — published fixture facts; this URL is an example week, not a multi-season corpus.
- [Official NFL news index](https://www.nfl.com/news/) — entry point only; each announcement must be dated and captured before use.
