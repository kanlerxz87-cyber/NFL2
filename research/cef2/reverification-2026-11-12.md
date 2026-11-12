# Re-verification record — session `cef2b11f` (2026-11-12, ~22:40 UTC)

Independent re-verification of the combined tree at `main` = `25d88a9` (merge of PR #24).
This session publishes **no new analytical opinion**; it re-runs, re-checks, and re-fetches.

## 1. Local suites (all re-run on this branch's tree, all green)

| Suite (owner) | Result |
|---|---|
| `tools/build_site.py` → `tools/verify.py` (root) | 39 passed · 0 warnings · 0 failures; rebuild byte-identical (empty `git diff`) |
| `tools/check_site.py` (root) | 10 passed · 1 expected warning (non-league hosts on the source registry by design) · 0 failures |
| `tools/review_verify.py` (01b698ef) | `OK: all rows, sources, blank cells and links verified. No broken links.` |
| `engine/verify_repo_and_site.py` (e143a7ca) | PASS — 64 HTML repo pages, 1,619 internal links, 0 broken; 100% portal rows sourced |
| `scripts/verify_q51.py` (51ce8d8e) | 10 pages, 0 errors, 130 explicit blank cells |
| `python3 -m unittest discover -s tests/q51` (51ce8d8e) | OK (36 tests) |
| `scripts/verify_s53126614.py` (53126614) | PASS — 9 JSON + 10 HTML pages, 262 rows 100% official-sourced, 0 broken links across 116 repo pages / 3,287 links |
| `scripts/audit_all_pages.py` (eaba7863) | PASS — 96 HTML pages, 222 tables, 3,423 rows, 0 broken links, 0 column mismatches |
| `node scripts/render_test.js` + `scripts/check_links.py` + `scripts/check_reproducible.py` (63ac21e9) | 13/13 pages · 128 refs 0 broken · all artefacts reproduce |

## 2. GitHub Pages status (API-verified, 2026-11-12)

- Pages API: `status: built`, `build_type: legacy`, source `main` `/`, latest build on commit `25d88a9` (created 2026-11-12T08:10:44Z, `error: null`).
- CI on `main`: `build-and-audit`, `Verify site data and links`, `Q51 evidence and engine verification`, `pages build and deployment` — all success at the merge of PR #24.
- Live fetches through the page reader (sandbox `curl` egress to github.io is allowlist-blocked — recorded before as Q-24):
  - `/NFL2/` (root dashboard) — 200; card values (254 rows · 6 designations · 227 depth events · 32 standings · 29 suggestions · 29 questions · 21 flags · 18 signals) match `data/build_manifest.json` metrics exactly.
  - `/NFL2/portal/index.html` — 200; zero-sum table renders (135=135 W/L, 6,246=6,246 PF=PA, 136 games).
  - `/NFL2/q51/index.html` — 200; inherits the same 254/227/136 counts; 0 eligible strategies (gates fail closed by design).
- Open PRs: none. Remote branches: `origin/main` only (plus this session's).

## 3. Official-source row re-checks (fetched 2026-11-12T22:3x–22:4x UTC)

| Object | Method | Result |
|---|---|---|
| 2026 standings — all 32 rows | Transcribed https://www.nfl.com/standings/ (both chunks); compared W-L-T, PF, PA, pct, streak, net vs `data/standings_2026.csv` | **32/32 exact** after the documented LA-vs-LAR key mapping (FL-17); recomputed pct and net agree; zero-sum identities W=L=135, ties=2, PF=PA, 136 games |
| Week-10 injury register | `research/cef2/check_injuries_official.py` against https://www.nfl.com/injuries/ | **254/254 register rows located on the official page, 0 missing**; six game designations identical (5 Out + 1 Questionable: Patrick, Yankoff, Harrison-Q, Brown, Davis, Henderson) |
| Hub movement | Same fetch | The hub now shows **25 rows more** than the register (SEA +15, CIN +4, IND +2, SF +2, JAX +1, AZ +1) — the official page rolled to the next practice filing after the register's capture. Verdict: capture-time fidelity intact; freshness drift quantified (see `freshness-2026-11-12.md`) |

## 4. Irregularities found by this sweep (flagged, not fixed — they are not defects in the data)

1. **CE-01 — `full-injuries-week10-2026.json` totals 253** (D93/L88/F72) where the root CSV and `s53126614_injuries_reg10_2026.json` both carry 254 (D92/L89/F73): one player is unaccounted between the two captures. Settling it needs the dated mirror (owner decision S-26). Published on the brief; no file edited.
2. **CE-02 — pass-vs-rush yards correlation diverges across trees**: `s53` C-14 r = −0.263 (season totals) vs `portal` CORR-12 r = −0.314 (yards/game). Both internally consistent; neither file states its denominator, so a reader sees an unexplained contradiction. Argument for a units field on every correlation record.
3. **CE-03 — "28 clubs" vs 24**: the register's own page says 254 rows span the 28-club Week-10 slate; 24 clubs actually filed rows (BAL, CIN, LAC, SEA showed "No Injuries Reported"). Consistent, but the phrasing reads as a row-count claim. Logged as a change request to the root-build owner (see COORDINATION.md), not edited here.

Machine-readable version: `research/cef2/reverification-2026-11-12.json`.
