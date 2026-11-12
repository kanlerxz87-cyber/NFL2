# Requirements Register

Each requirement from the brief is itemised, mapped to what was built, and marked with
an honest status. Status values: **met**, **partial** (built, but limited by data
availability — the limit is named), **not met** (and why).

| ID | Requirement (from the brief) | Where it lives | Status |
|----|------------------------------|----------------|--------|
| R1 | Collect, organise and analyse a full list of requirements | this file | met |
| R2 | Suggestions to improve decision making | `docs/SUGGESTIONS.md`, site page *Suggestions* | met |
| R3 | A dedicated suggestions section so someone can review before implementing | site page *Suggestions & Decision Paths* | met |
| R4 | A clear list of questions, information and answers needed before a decision | `docs/OPEN-QUESTIONS.md`, site page *Open Questions* | met |
| R5 | Suggestions to discover missing information | `docs/OPEN-QUESTIONS.md` §Discovery backlog | met |
| R6 | Originate our own NFL lines | `pipeline/engine/lines.py` → `site/data/lines.json`, site page *Our Lines* | met |
| R7 | Research and develop strategies for generating useful signals | `pipeline/engine/strategies.py`, 22 strategies | met |
| R8 | Leaderboard competition with rewards for top strategies | `strategies.json` → `reward_rules`, site page *Leaderboard* | met |
| R9 | Single bets | strategy families model-spread / model-total / model-ml | met |
| R10 | Parlays | `pipeline/engine/correlation.py` + parlay pricing incl. vig scaling | met |
| R11 | Player prop bet combos | `pipeline/engine/props.py` | **partial** — no prop-line history exists in this environment, so correlations are published as UNVERIFIED with the structural sign map only |
| R12 | Every strategy passes validation gates | 7 gates + development/holdout split | met |
| R13 | Determine correlation values | `site/data/correlation.json` — measured φ for 4 leg pairs | **partial** — game markets only verified; player props unverified |
| R14 | Remove luck from the equation | `pipeline/engine/luck.py` — variance, split-half, persistence | met |
| R15 | Build strategies that are selectively skill-based | certification requires G6 + persistence | met (result: none certified — see summary) |
| R16 | Track injuries | weekly injury reports 2024-2026, site page *Injuries & Depth* | met |
| R17 | Know deficiencies where 2nd/3rd/4th string replace starters | `availability.py` `depth_vacancies` | **partial** — full depth charts exist only for 2024 |
| R18 | Same for offence and defence | position groups split OL/DL/LB/DB/QB/RB/WR/TE | met |
| R19 | Executive summary | `docs/EXECUTIVE-SUMMARY.md`, site landing page | met |
| R20 | No manual input from the owner | `python3 -m pipeline.build` regenerates everything | met |
| R21 | Verify line by line from official/trusted sources | `docs/VERIFICATION.md`, every table row carries a source link | met |
| R22 | Flag irregularities for review | site page *Flagged for Review*, `audit.json` | met |
| R23 | Clean landing page + category subpages, dashboard style | `site/` | met |
| R24 | All entries and findings in readable tables | every page is table-first | met |
| R25 | Every table row has a source link to an official site | enforced in `site/app.js` renderer + `scripts/check-site.py` | met |
| R26 | Unconfirmable values left blank and flagged | `verified: false` / blank cells, never imputed | met |
| R27 | Never infer or fill in values | no imputation anywhere in the pipeline | met |
| R28 | Parallel-session coordination | `COORDINATION.md` | met |
| R29 | PR from integration branch, merged, Pages live | `COORDINATION.md` log + PR link | met |
| R30 | Flagged items published, not blocking | site page *Flagged for Review* | met |

## Requirements that changed shape during the work

* **R11 / R13 (player props).** The brief asks for prop-combo correlations. The honest
  position: without a licensed prop-line archive, any published number would be
  invented. The pipeline therefore publishes the *structural* sign of each
  relationship, the *exact* arithmetic of parlay hold, and a named list of the data
  that would make measurement possible. This is recorded as **partial**, not met.
* **R17 (2nd/3rd/4th string).** Depth-chart data exists for 2024 only in reachable
  sources. The metric is computed exactly for 2024 and refuses to publish for other
  seasons instead of extrapolating.
* **R8 (rewards).** Implemented as points and paper allocation, not cash. The NFL's
  gambling policy constrains who may be paid for picks; see the compliance note in the
  executive summary. Cash payouts are flagged as an open question, not decided here.
