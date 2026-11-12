# s92 — evidence and decision dashboard

Session `8b4bdcb3` · branch `arena/8b4bdcb3-nfl2` · additive to the repository, owns nothing outside `s92/`.

**Live:** https://kanlerxz87-cyber.github.io/NFL2/s92/ (after merge)

## What it is

Fourteen generated pages that answer three questions: what the repository actually knows, what is missing
before a decision can be made, and what would be built first. It re-derives numbers where it can and links
to other trees where it cannot, instead of restating them.

## Build

```sh
python3 s92/build.py        # regenerates all 14 pages from s92/data/
python3 tools/verify_s92.py # row-level source, link, blank and arithmetic gate
```

CI: `.github/workflows/s92.yml` rebuilds, fails on drift, runs the gate, and re-runs the root audits.

## Files

| Path | What it holds |
| --- | --- |
| `s92/data/repo_audit.csv` | 21 line-by-line findings against official pages, each with a source URL |
| `s92/data/questions.csv` | 15 questions with what we have, what we lack, how it closes |
| `s92/data/suggestions.csv` | 20 scored suggestions with a state column |
| `s92/data/assumptions.csv` | 10 published numbers with their evidence, limits and publication rule |
| `s92/data/gates.csv`, `strategies.csv`, `signals.csv` | the competition specification |
| `s92/data/depth_charts_official.csv` | 152 depth slots from 3 official club charts, labelled unofficial where the club says so |
| `s92/data/depth_deficiency.csv` | starter-to-backup chains computed from the injury filing |
| `s92/data/injuries_official.json` | 277 practice rows parsed from the official hub |
| `s92/data/standings_official.csv` | 32 clubs transcribed from the official standings table |
| `s92/data/week11_lines.csv` | 13 originated Week 11 lines; market columns blank by rule |
| `s92/data/luck.json`, `backtest.json`, `week11_model.json` | the computed statistics |
| `s92/raw/**` | the verbatim official extracts the audit was performed against |

## Rules the build enforces

1. A table row with no `https` source fails the build.
2. A blank value renders as **not published** with the reason attached; it is never 0, never an estimate.
3. No market price is asserted anywhere, because no price source exists.
4. Prose numbers are checked against the data files on every CI run.
5. Anything verified only in part says so on the same line as the number.

## What is not here

No price data, no participation data, no player-prop model, no funded reward schedule. Those are the
open questions on `questions.html`, not gaps this dashboard can close by itself.
