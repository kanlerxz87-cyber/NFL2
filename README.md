# NFL2 — collect, organise, analyse, and originate

A data + decision project for the NFL: an injury and availability record built only from official league
sources, a specification for originating our own lines and pricing parlays and prop combos, a strategy
leaderboard that has to clear validation gates, and a published register of questions, suggestions and
flags so that the owner can choose a path before anything is implemented.

**Live site (GitHub Pages):** https://kanlerxz87-cyber.github.io/NFL2/
**Executive summary (site):** [executive-summary.html](executive-summary.html) · **owner's brief from the earlier session:** [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
**Coordination board:** [COORDINATION.md](COORDINATION.md)

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
| `review/`, `review/content/`, `research/**`, `tools/review_*.py`, `.github/workflows/verify.yml` | session `arena-01b698ef`'s register dashboard (16 pages) with its own generator, its own row-level auditor and its own CI gate; the tool names `tools/build_site.py` and `tools/verify.py` were claimed by this root build, so their copies were renamed and left otherwise untouched |
| `archive/session-009ec582/` | that session's 15-page root build, preserved verbatim with its own stylesheet and script so it still renders |
| `docs/` | that session's earlier 18-page build, published at `/NFL2/docs/` |
| `COORDINATION.md` | shared task board for concurrent agent sessions: claims, scopes, log, handoffs, integration record |
| `.github/workflows/validate.yml` | CI: build, both audits, and a drift check that the committed HTML matches a rebuild |

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
```

No dependencies, no build tooling, no JavaScript. Editing a page means editing its markdown or its CSV,
then running the builder; CI fails if you forget. **Do not hand-edit a root `*.html` file** — it is
overwritten by the builder, and the CI drift check fails the commit.

## Four published trees, one audited

| Tree | Owner | Audited by | Status |
| --- | --- | --- | --- |
| `/` (repository root) | `bc4b47cf` | `tools/verify.py` + `tools/check_site.py` + drift check, in `.github/workflows/validate.yml` | **canonical** — this is what https://kanlerxz87-cyber.github.io/NFL2/ serves |
| `review/` | `arena-01b698ef` | their own `tools/review_verify.py` (row-level, 423 rows) in `.github/workflows/verify.yml` | live, labelled, not merged into the root registers |
| `archive/session-009ec582/` | `arena-009ec582` | their 12 build checks at the time they wrote it | archived; carries a banner pointing at the root |
| `docs/` | `arena-009ec582` | as above | live at `/NFL2/docs/`, unchanged |

## Where the earlier session's pages went

That session's root build moved intact to `archive/session-009ec582/`, so its tables are still readable
at `https://kanlerxz87-cyber.github.io/NFL2/archive/session-009ec582/index.html` (results, standings,
team stats, injuries & depth, analysis, strategies, method, data sources, questions, suggestions,
flagged for review), and its previous build remains at `/NFL2/docs/`. Two of its numbers were adopted
here after re-derivation — the 136-game log and the reconciliation against the standings table — and the
rest of its derived analysis is deliberately **not** restated as this project's own; see `Q-29` and
`S-26` in the registers, and §8 of `COORDINATION.md` for the full integration record.
