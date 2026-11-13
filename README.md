# NFL2 — collect, organise, analyse, and originate

A data + decision project for the NFL: an injury and availability record built only from official league
sources, a specification for originating our own lines and pricing parlays and prop combos, a strategy
leaderboard that has to clear validation gates, and a published register of questions, suggestions and
flags so that the owner can choose a path before anything is implemented.

**Live site (GitHub Pages):** https://kanlerxz87-cyber.github.io/NFL2/
**Independent Q51 evidence dashboard:** [q51/index.html](q51/index.html) · [Flagged for Review](q51/flagged.html)
**Executive summary (site):** [executive-summary.html](executive-summary.html) · [Q51 executive summary](q51/executive-summary.html) · **owner's brief from the earlier session:** [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
**Coordination board:** [COORDINATION.md](COORDINATION.md)

> Q51 publishes current-snapshot research lines and descriptive correlations from the source-linked game log. They are **unvalidated, paper-only** outputs, not betting advice. No market/prop/settlement archive exists, the leaderboard is empty, and real-money execution is disabled.

## What is in here

| Path | What it is |
| --- | --- |
| `index.html`, `*.html` | the published site — generated, never hand-edited |
| `content/*.md` | the prose and directives for every page |
| `data/*.csv` | the verified datasets and the registers (requirements, questions, suggestions, gates, signals, strategies, correlation, flags, sources) |
| `data/games_2026_wk1_9.csv` | the 136 completed results of weeks 1–9, imported from a parallel session's fetch and re-audited here; each row cites its own official game page |
| `tools/build_site.py` | markdown + CSV → static HTML; refuses to build a row without a source |
| `tools/verify.py` | data audit (37 checks): reconciliations, vocabularies, blank policy, no fabricated results, game-log cross-check |
| `tools/review_build_site.py`, `tools/review_verify.py` | the *other* session's generator and auditor, kept running under renamed paths and checked by `.github/workflows/verify.yml` |
| `tools/check_site.py` | site audit: links, empty cells, template markers, official-source coverage, stale-output and input-digest guards |
| `tools/compute_tables.py` | the analytic tables (vig, parlay coupling, sample sizes) — closed-form, no market data |
| `tools/import_parallel.py` | re-imports the game log from `data/games_2026.json` and prints the standings reconciliation |
| `scripts/**`, `data/*.json`, `data/derived/**` | the parallel session (`arena-009ec582`) and its datasets: 136-game log, standings, team stats, player leaders, depth charts, derived analysis |
| `portal/`, `engine/`, `datasets/e143a7ca/`, `reports/` | session `e143a7ca`'s 10-page quantitative portal, its own build/verify engine, its datasets and its three report documents; linked from the page map rather than merged into these registers |
| `review/`, `review/content/`, `research/**`, `tools/review_*.py`, `.github/workflows/verify.yml` | session `arena-01b698ef`'s register dashboard (16 pages) with its own generator, its own row-level auditor and its own CI gate; the tool names `tools/build_site.py` and `tools/verify.py` were claimed by this root build, so their copies were renamed and left otherwise untouched |
| `archive/session-009ec582/` | that session's 15-page root build, preserved verbatim with its own stylesheet and script so it still renders |
| `docs/` | that session's earlier 18-page build, published at `/NFL2/docs/` |
| `COORDINATION.md` | shared task board for concurrent agent sessions: claims, scopes, log, handoffs, integration record |
| `.github/workflows/validate.yml` | CI: build, both audits, and a drift check that the committed HTML matches a rebuild |
| `q51/`, `engine/q51/`, `collectors/q51/`, `tests/q51/`, `research/q51/` | independent Q51 evidence dashboard, tested paper-only engine, robots-aware collector, mutation tests and source-evidence audit; namespaced to preserve upstream work |
| `.github/workflows/q51.yml` | CI: Q51 unit/mutation tests, deterministic research/site rebuild and strict row-source/link/safety verification |

## Week 11 forward sample — pre-registered (session `0a113a24`, 13 Nov 2026)

- [week11-originated.html](week11-originated.html): thirteen Week 11 lines published and SHA-256 pre-registered before kickoff (decision timestamp `2026-11-13T12:39Z`), with the empty forward grade beside them.
- `tools/originate_week11.py` re-derives all 14 published Week 10 lines before it writes anything; `tools/grade_forward.py` refuses to grade if any pre-registered artefact has changed (tested: a one-cell edit reports `BROKEN` and exits 1).
- Inputs: `data/schedule_week11_2026.csv`, `data/originated_lines_wk11_0a113a24.csv`, `data/prereg_week11_0a113a24.json` (+ `.csv` mirror), `data/games_week11_played.csv` (append-only, empty until games are final).
- Re-verification: `tools/reverify_0a113a24.py` → `data/reverification_0a113a24.csv` (102 rows: 95 match, 2 mismatch explained under FL-36, 5 not checked) and `data/week11_broadcaster_change_0a113a24.csv`.
- Checks: `tools/verify.py` `forward_sample_holds()` re-runs the hash, reproduction and slate checks on every run.

## Rules this project does not bend

1. Every table row that asserts a fact links an **official league page** (`nfl.com`, `operations.nfl.com`), or the build fails.
2. An unconfirmable value stays **blank** and is rendered as `not published` — never zero, never a guess, never a third party's number.
3. Anything arithmetic is **recomputed** from the inputs on every build (league points reconcile to the unit; 6,246 for = 6,246 against).
4. **No performance claim without a forward sample.** Backtests never appear on the leaderboard.
5. Irregularities are **published**, not silently fixed: see *Flagged for Review*.
6. **Another session's file is an input, not a source.** Importing it means re-deriving its per-row sources and reconciling it against data transcribed from a different official page; what cannot be re-derived stays labelled as that session's output.

## Repository layout

```
*.html                      the published dashboard (generated)
content/<slug>.md           page prose + {{csv ...}} directives
data/<name>.csv             pipe-delimited, fixed field count
data/build_manifest.json     inputs digest + measured counts (generated)
tools/build_site.py          generator
tools/verify.py              data auditor
tools/check_site.py          site auditor
tools/compute_tables.py      analytic exhibits
tools/import_parallel.py     cross-session import + reconciliation
scripts/ · data/*.json       parallel session's pipeline and datasets
review/ · research/**        session arena-01b698ef's register dashboard and its notes
docs/ · archive/**           session arena-009ec582's published builds
tools/review_*.py            arena-01b698ef generator + auditor (renamed, logic unchanged)
```

## Work with it

```
python tools/build_site.py     # regenerate every page from data/ + content/
python tools/verify.py         # audit the data       (exit 1 on any failure)
python tools/check_site.py     # audit the site links (exit 1 on any failure)
python -m engine.q51.build_research  # Q51 current-snapshot research artifacts
python -m engine.q51.build_site      # Q51 evidence dashboard
python -m unittest discover -s tests/q51 -v
python scripts/verify_q51.py         # strict Q51 row-source, blank, link and safety gate
```

No dependencies, no build tooling, no JavaScript. Editing a page means editing its markdown or its CSV,
then running the builder; CI fails if you forget. **Do not hand-edit a root `*.html` file** — it is
overwritten by the builder, and the CI drift check fails the commit.

## Five published trees, one audited at the root

| Tree | Owner | Audited by | Status |
| --- | --- | --- | --- |
| `/` (repository root) | `bc4b47cf` | `tools/verify.py` + `tools/check_site.py` + drift check, in `.github/workflows/validate.yml` | **canonical** — this is what https://kanlerxz87-cyber.github.io/NFL2/ serves |
| `review/` | `arena-01b698ef` | their own `tools/review_verify.py` (row-level, 423 rows) in `.github/workflows/verify.yml` | live, labelled, not merged into the root registers |
| `archive/session-009ec582/` | `arena-009ec582` | their 12 build checks at the time they wrote it | archived; carries a banner pointing at the root |
| `docs/` | `arena-009ec582` | as above | live at `/NFL2/docs/`, unchanged |
| `portal/` | `e143a7ca` | their own `engine/verify_repo_and_site.py`, which also runs a whole-repository link check over root, `docs/`, `review/` and `portal/` | live, labelled, five trees and counting |

## Where the earlier session's pages went

That session's root build moved intact to `archive/session-009ec582/`, so its tables are still readable
at `https://kanlerxz87-cyber.github.io/NFL2/archive/session-009ec582/index.html` (results, standings,
team stats, injuries & depth, analysis, strategies, method, data sources, questions, suggestions,
flagged for review), and its previous build remains at `/NFL2/docs/`. Two of its numbers were adopted
here after re-derivation — the 136-game log and the reconciliation against the standings table — and the
rest of its derived analysis is deliberately **not** restated as this project's own; see `Q-29` and
`S-26` in the registers, and §8 of `COORDINATION.md` for the full integration record.

## Line-origination lab (`/site/`) — session `arena-63ac21e9`

A second, self-contained dashboard lives at **[`site/index.html`](site/index.html)**, published at
**https://kanlerxz87-cyber.github.io/NFL2/site/**. It is additive: it does not modify the pages above,
their data, or their tooling, and it has its own data directory and build command.

| | |
|---|---|
| Spread MAE (3,404 games, 2013–2025) | **10.25 pts** vs the market's **9.94** (+0.31 worse) |
| Total MAE | **10.87 pts** vs **10.50** (+0.37 worse) |
| Strategies certified | **0 of 22** |

The lab originates its own spread/total/moneyline from time-decayed offence and defence ratings,
then holds 22 candidate strategies to seven gates on a locked holdout (2021–2025) after a
development window (2013–2020). It stops at the same wall every honest build does: the closing
line is a better forecast than the model, and the site says so on the landing page.

What it adds beyond a benchmark:

* **Developer/holdout discipline with Bonferroni correction** across 60 tests, plus Wilson bounds,
  chronological split-half and season-to-season persistence tests — four independent luck filters.
* **Measured correlation values.** Spread vs total φ = +0.019 (genuinely independent) against
  spread vs home moneyline φ = +0.669 (one bet counted twice). The book prices both as if
  independent, which understates the correlated parlay by 58.5%.
* **Depth-chart vacancy index.** For 2024, 45 position-weeks where a depth-1 starter was ruled Out
  with no depth-2 body available — the concrete "down to a third-stringer" case.
* **Every unverifiable value left blank**, with the reason printed on
  [`site/flagged.html`](site/flagged.html).

```sh
pip install numpy pandas scipy pyarrow
python3 -m pipeline.build      # regenerates site/data/*.json from vendored, hashed sources
node scripts/render_test.js    # executes every page module against the real JSON
python3 scripts/check_links.py # internal links + data references
```

The two builds do not share a build system and must not be confused with each other: `tools/build_site.py`
builds the root site from `data/`, while `pipeline.build` builds `/site/` from `pipeline/data/raw/`.
Both are verified independently in CI.


---

## Verified 12-Club Depth Cascades, 32-Club Correlations & Repo Audit Suite (Session `eaba7863`)

- **Live Analytics Suite (18 unified pages):** [`https://kanlerxz87-cyber.github.io/NFL2/analytics/index.html`](https://kanlerxz87-cyber.github.io/NFL2/analytics/index.html)
  - [`analytics/depth-deficiencies.html`](analytics/depth-deficiencies.html): 12 official NFL club depth charts joined to Week 10 `REG10` & IR news across **18 verified 1st → 2nd → 3rd → 4th-string offense & defense cascades** + 2026 NFL roster/elevation/ATC spotter rules.
  - [`analytics/correlations.html`](analytics/correlations.html): **14 reproducible 2026 NFL team correlations** across `n = 32` clubs, Fisher-*z* 95% CIs, Same-Game Parlay / prop copula blank register, and 32-club luck-vs.-skill residuals.
  - [`analytics/repo-audit.html`](analytics/repo-audit.html): Line-by-line commit & upstream official-source audit (`RA-05` `REG10` IR blindspots, `RA-06` club depth-chart lag).
  - [`analytics/lines-lab.html`](analytics/lines-lab.html) & [`analytics/schedule.html`](analytics/schedule.html): Interactive fair-line & correlation calculators + Week 11 MODEL v1 originated lines.
- **Reproducible Build & Verification (`eaba7863`):**
  ```sh
  python3 scripts/build_site.py && python3 scripts/build_new_pages.py && python3 scripts/verify_site.py
  python3 scripts/audit_all_pages.py
  ```

---

## Week 11 Fair-Line Origination, 13-Club Depth Deficiency, Signal Competition & Decision Suite (Session `arena-53126614`)

- **Live S53 Suite (10 unified pages):** [`https://kanlerxz87-cyber.github.io/NFL2/s53/index.html`](https://kanlerxz87-cyber.github.io/NFL2/s53/index.html)
  - [`s53/originated-lines.html`](s53/originated-lines.html): Originated Week 11 fair spreads, totals & win probabilities (`v0` PF/PA, `v1` 136-game SRS, `v2` 60% SRS + 40% Pass/Downs Skill; separate `g_away`/`g_home` for 8-vs-9 game pairings; `HFA=0` for neutral Mexico City `MIN vs SF`), with unverified sportsbook market lines strictly blank.
  - [`s53/depth-deficiencies.html`](s53/depth-deficiencies.html): 13 official NFL club depth charts joined with Week 10 `REG10` + IR wire across 18 multi-string replacement chains (`BAL` QB3 Joe Fagnano, `SEA` QB2 Drew Lock, `MIA` QB Kyle McCord, `NE`/`SF`/`DAL` starter clusters); 19 unmapped clubs left blank & flagged.
  - [`s53/correlations.html`](s53/correlations.html), [`s53/leaderboard-competition.html`](s53/leaderboard-competition.html) & [`s53/decision-center.html`](s53/decision-center.html): 15 empirical 2026 correlations (`n=32`), interactive SGP Gaussian-copula tool, 12 pre-registered single/parlay/prop-combo strategies (`0.00u`–`1.00u` reward tiers, gates `G0`–`G8`), interactive Path A–D reviewer & QIA prerequisite register.
  - [`s53/repo-audit.html`](s53/repo-audit.html) & [`s53/flagged.html`](s53/flagged.html): Line-by-line audit correcting 4 NFL.com player-leader column shifts (`Bijan Robinson` TD `9->5`, `Jaylen Warren` TD `7->2`, `Trey McBride` Lng `41->27`, `Ja'Marr Chase` TD `8->7`).
- **Deterministic Row-Source & Whole-Repo Link Verification (`arena-53126614`):**
  ```sh
  python3 scripts/verify_s53126614.py
  ```

---

## Live refresh, NE/DET depth cascade & the first scored competition (Session `arena-2268bfb2`)

- **Live suite (11 pages):** [`https://kanlerxz87-cyber.github.io/NFL2/s2268/index.html`](https://kanlerxz87-cyber.github.io/NFL2/s2268/index.html)
  - [`s2268/refresh.html`](s2268/refresh.html): the official injury hub re-read at **2026-11-13T12:40Z** — 295 rows across 26 clubs — and every one of the 154 differences against the two Week 10 registers already in this repository. Six Week 10 game ids disagree between `data/injuries_2026_wk10.csv` and `data/schedule_2026_wk10.csv`; three of them name a completely different fixture ([FL-64](flagged-for-review.html)).
  - [`s2268/depth.html`](s2268/depth.html): New England and Detroit's own published depth charts joined to the league's injury filing — a 1st-to-4th string cascade for every unavailable player, including the case the register exists for (Stevenson limited behind him, Henderson **out**, so the next man up is the **3rd** string and then the **4th**).
  - [`s2268/competition.html`](s2268/competition.html), [`s2268/forecast.html`](s2268/forecast.html), [`s2268/correlations.html`](s2268/correlations.html), [`s2268/parlays.html`](s2268/parlays.html), [`s2268/luck.html`](s2268/luck.html), [`s2268/gates.html`](s2268/gates.html): ten pre-registered strategies scored on **596 decisions across 72 holdout games** (weeks 5–9), with exact binomial tests, a Benjamini–Hochberg correction, a seeded Monte Carlo, a measured 15-pair same-game correlation matrix, disjoint-parlay arithmetic, ten validation gates and five reward tiers.
  - [`s2268/flagged.html`](s2268/flagged.html) and [`s2268/sources.html`](s2268/sources.html): nine flagged items (one of them a defect this session found in its own harness) and every source read, with its access time.

| Result | Value |
| --- | --- |
| Rows on the live injury hub at 12:40Z | **295** across 26 clubs (LAC and BAL print *No Injuries Reported*) |
| Rows the published Injuries page shows | **254** — 41 rows behind |
| Differences against the two published registers | **154** and **68** |
| Strategies scored out of sample | **10** (8 signals + 2 negative controls) |
| Decisions settled | **596** on 72 holdout games |
| Candidates surviving a 10% false-discovery rate | **4** |
| Our originated spread vs a prediction of zero | MAE **11.03** vs **10.92** — no improvement |
| Our originated total vs the league mean | MAE **11.21** vs **11.18** — no improvement |
| Strongest same-game correlation measured | φ = **0.945** (home wins × home beats our spread) |
| Reward tiers carrying a stake | **0 of 5** — all blocked on a price feed |

**The honest headline:** on this holdout our own lines do not beat knowing nothing, and the best hit rate on
the site (79.2%) sits on the smallest sample (24 decisions) and is deliberately not promoted. Both facts are
published rather than tuned away.

- **Build and verify (`arena-2268bfb2`):**
  ```sh
  python3 tools/s2268_competition.py    # scores the competition; refuses to run on a changed hash
  python3 tools/s2268_refresh.py        # diffs the dated register against the two published ones
  python3 tools/s2268_build_site.py     # renders s2268/
  python3 tools/s2268_verify.py         # row-source, link, determinism and scope gate + every other suite
  ```
