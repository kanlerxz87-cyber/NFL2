# NFL2 — collect, organise, analyse, and originate

A data + decision project for the NFL: an injury and availability record built only from official league
sources, a specification for originating our own lines and pricing parlays and prop combos, a strategy
leaderboard that has to clear validation gates, and a published register of questions, suggestions and
flags so that the owner can choose a path before anything is implemented.

**Live site (GitHub Pages):** https://kanlerxz87-cyber.github.io/NFL2/

## What is in here

| Path | What it is |
| --- | --- |
| `index.html`, `*.html` | the published site — generated, never hand-edited |
| `content/*.md` | the prose and directives for every page |
| `data/*.csv` | the verified datasets and the registers (requirements, questions, suggestions, gates, signals, strategies, correlation, flags, sources) |
| `tools/build_site.py` | markdown + CSV → static HTML; refuses to build a row without a source |
| `tools/verify.py` | data audit: reconciliations, vocabularies, blank policy, no fabricated results |
| `tools/check_site.py` | site audit: links, empty cells, template markers, official-source coverage |
| `tools/compute_tables.py` | the analytic tables (vig, parlay coupling, sample sizes) — closed-form, no market data |
| `COORDINATION.md` | shared task board for concurrent agent sessions: claims, scopes, log, handoffs |
| `.github/workflows/validate.yml` | CI: build, both audits, and a drift check that the committed HTML matches a rebuild |

## Rules this project does not bend

1. Every table row that asserts a fact links an **official league page** (`nfl.com`, `operations.nfl.com`), or the build fails.
2. An unconfirmable value stays **blank** and is rendered as `not published` — never zero, never a guess, never a third party's number.
3. Anything arithmetic is **recomputed** from the inputs on every build (league points reconcile to the unit; 6,246 for = 6,246 against).
4. **No performance claim without a forward sample.** Backtests never appear on the leaderboard.
5. Irregularities are **published**, not silently fixed: see *Flagged for Review*.

## Work with it

```
python tools/build_site.py     # regenerate every page from data/ + content/
python tools/verify.py         # audit the data      (exit 1 on any failure)
python tools/check_site.py     # audit the site links (exit 1 on any failure)
```

No dependencies, no build tooling, no JavaScript. Editing a page means editing its markdown or its CSV,
then running the builder; CI fails if you forget.
