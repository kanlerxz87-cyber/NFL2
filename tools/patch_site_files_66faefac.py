#!/usr/bin/env python3
"""Re-apply session 66faefac's edits to the tracked site files.

Why this exists: the shared workspace has had tracked files reset by another
session's cleanup (tools/build_site.py and content/*.md were reverted mid-build on
13 November, wiping uncommitted page-layer edits). Rather than repeating one-off
seds by hand, every edit is declared here, is idempotent, and refuses to apply to an
unexpected file: each edit names an anchor that must appear exactly once, plus a
marker that proves the edit is already in place.

    python3 tools/patch_site_files_66faefac.py
    python3 tools/build_site.py
    python3 tools/verify.py

Scope: tools/build_site.py, content/data-dictionary.md, content/executive-summary.md,
content/index.md. Nothing else, because nothing else in the tracked tree is ours.
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def p(*parts):
    return os.path.join(ROOT, *parts)


def rows(rel):
    with open(p(rel), encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def patch(rel, edits):
    fp = p(rel)
    s = open(fp, encoding="utf-8").read()
    n = 0
    for needle, marker, repl in edits:
        if marker and marker in s:
            continue
        hits = s.count(needle)
        if hits != 1:
            sys.exit("%s: anchor appears %d times, expected exactly 1: %r" % (rel, hits, needle[:80]))
        s = s.replace(needle, repl, 1)
        n += 1
    with open(fp, "w", encoding="utf-8") as fh:
        fh.write(s)
    print("%s: %d edit(s) applied, %d already present" % (rel, n, len(edits) - n))
    return s


# --------------------------------------------------------------------- build_site.py
NAV_OLD = '''    ("Governance", [("methodology", "Verification Method"), ("price-archive", "Price Archive"),
                   ("sources", "Source Registry")]),
]'''
NAV_NEW = '''    ("Governance", [("methodology", "Verification Method"), ("price-archive", "Price Archive"),
                   ("sources", "Source Registry")]),
    # Availability read through a depth chart, and the first decision this site has
    # locked before the games it predicts happened.
    ("Availability", [("availability-1113", "Week 10 Availability (13 Nov)"),
                      ("preregistration", "Pre-Registration Lock")]),
]'''

PAGES_OLD = "PAGES = [slug for _, items in NAV for slug, _ in items]"
PAGES_NEW = PAGES_OLD + '''
# The two 66faefac pages are registered after the NAV sweep so the group order above
# stays the reading order of the site; both are in PAGE_KIND below, which is what the
# auditor uses to tell a designed page from a measured one.
PAGES = PAGES + ["availability-1113", "preregistration"]'''

KIND_OLD = '    "week10-settled": ("measured", "Computed result"),'
KIND_NEW = KIND_OLD + '''
    "availability-1113": ("measured", "Measured data"),
    "preregistration": ("measured", "Computed result"),'''

METRICS_OLD = "    m.update(gamelog_metrics(st))"
METRICS_NEW = '''    # The 13 November read and the first locked decision, counted from the registers so
    # the landing page never has to remember a number. verify.py does not yet police the
    # hub arithmetic here - that is S-47, the proposal to promote it into the verifier.
    avail = _safe_rows("club_availability_20261113_66faefac.csv")
    m.update({
        "avail_rows": sum(int(r["rows_today"]) for r in avail),
        "avail_clubs": sum(1 for r in avail if r["state"] == "rows published"),
        "avail_none": sum(1 for r in avail if r["state"] == "No Injuries Reported"),
        "avail_designations": sum(int(r["out"]) for r in avail),
        "avail_flagged_rows": _safe_len("hub_flagged_20261113_66faefac.csv"),
        "deficiency_rows": _safe_len("availability_deficiency_66faefac.csv"),
        "deficiency_first_string": sum(1 for r in _safe_rows("availability_deficiency_66faefac.csv")
                                       if r["string_depth"] == "1st string"),
        "prereg_fixtures": _safe_len("prereg_wk10_66faefac.csv"),
        "prereg_called": sum(1 for r in _safe_rows("prereg_wk10_66faefac.csv")
                             if r["call"].startswith("take") and r["locked"] == "yes"),
        "reverification_1113": _safe_len("reverification_66faefac.csv"),
        "rv1113_confirmed": sum(1 for r in _safe_rows("reverification_66faefac.csv") if r["result"] == "MATCH"),
        "rv1113_mismatch": sum(1 for r in _safe_rows("reverification_66faefac.csv") if r["result"] == "MISMATCH"),
        "rv1113_notchecked": sum(1 for r in _safe_rows("reverification_66faefac.csv") if r["result"] == "NOT CHECKED"),
    })
    m.update(gamelog_metrics(st))'''

BUILD_EDITS = [
    (NAV_OLD, '("Availability",', NAV_NEW),
    (KIND_OLD, '"availability-1113":', KIND_NEW),
    (METRICS_OLD, 'avail_rows', METRICS_NEW),
]

# --------------------------------------------------------- content/data-dictionary.md
DICT_ANCHOR = "### Grains introduced by the origination lab"
DICT_BLOCK = """| `data/club_availability_20261113_66faefac.csv` | 28 | club × the 13 November hub read: rows published, D/L/F split, designations, the load the locked rule consumes, and the same club's counts at the 04:45Z and 22:35Z reads with the delta | S-HUB-1113 |
| `data/hub_flagged_20261113_66faefac.csv` | 17 | one named player: the nine game designations plus the non-participants at the four clubs whose chart this build transcribes, with the hub's practice code | S-HUB-1113 |
| `data/hub_club_counts_20261113_66faefac.csv` | 28 | one club block as the page displayed it, before any derivation - the hand-transcription input the tool re-totals against | S-HUB-1113 |
| `data/availability_deficiency_66faefac.csv` | 18 | one unavailable player × the column he holds in the club's own printed order, the next man up, and how many bodies are left in that group | S-HUB-1113, S-DEPTH-KC, S-DEPTH-GB, S-DEPTH-NE, S-DEPTH-DET |
| `data/prereg_wk10_66faefac.csv` | 14 | one Week 10 fixture × the locked decision: load by side, differential, call or no-call, our line, stake zero, with the decision timestamp | S-HUB-1113, S-CALC |
| `data/prereg_sensitivity_66faefac.csv` | 6 | one threshold × how many fixtures the same rule would call; only the 4 row was registered, the rest are context | S-CALC |
| `data/reverification_66faefac.csv` | 23 | one check performed against a live official page on 13 November, with its outcome, including 4 `NOT CHECKED` and 3 `MISMATCH` rows | S-HUB-1113, S-STAND-1113B, S-SCHED10-1113, S-SCHED11-1113B, S-SCORES-1113B |

"""


def dict_edits():
    return [(DICT_ANCHOR, "`data/club_availability_20261113_66faefac.csv`", DICT_BLOCK + DICT_ANCHOR)]


# ------------------------------------------------------------- content/executive-summary.md
EXEC_SECTION = """## Added in the third verification pass, 13 Nov 2026 12:45Z (session `66faefac`)

The same official hub, read a third time, plus the first prediction this site has locked before a
result existed. Four things moved, and none of them is a correction of the pages below: those snapshots
stay byte-frozen so the drift stays measurable.

| What changed | The measured result | Where |
| --- | --- | --- |
| **The register grew again, and nothing shrank.** A third read of the Week 10 hub 14 hours after the second holds 296 rows instead of 279, across all 28 playing clubs: 26 with names, two publishing `No Injuries Reported`. Ten clubs gained rows, eighteen were unchanged, none lost one. | 254 · 279 · 296 rows | [Week 10 availability](availability-1113.html), [FL-38](flagged-for-review.html) |
| **Availability now joins to a depth chart, for four clubs.** Eighteen unavailable players are read against the column they hold on their club's own published order, and eight of them sit in a 1st-string column: Green Bay lost a running back, a centre, a middle linebacker and a first-string nickel to non-participation in one block, while Detroit's starting centre and starting corner are both ruled out. | 18 joined rows · 8 first-string · 3 exhausted chains | [availability_deficiency_66faefac.csv](https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/availability_deficiency_66faefac.csv) |
| **The first locked decision.** ST-15 takes the healthier club when the availability load differs by four or more, was written at 12:45Z with a SHA-256 committed, and called 2 of the 13 un-played fixtures. Every other fixture is recorded as a no-call rather than dropped, and every stake is zero because gate G-07 is not passed. | 14 fixtures · 2 calls · 0 units staked | [Pre-registration lock](preregistration.html) |
| **One hub row contradicts itself, in the open.** Detroit's Kerby Joseph carries a full practice and an `OUT` designation in the same row, which breaks any feature that reads only one column. It is published as a conflict, not resolved. | 1 of 9 designations | [FL-39](flagged-for-review.html), [Q-43](questions.html) |

**The limitation that decides what this is worth:** the load is a sum of two published counts, so a player in both columns is counted twice. Only Washington, New England and Detroit carry both columns today, and de-duplicating those three changes no locked call. The arithmetic on required sample does not move either: 1,382 games to detect a 1.0-point error difference, 400 settled bets before any leaderboard claim. Two calls is not evidence of anything except that the mechanism runs.
"""


def exec_edits():
    """True when the third-pass section still has to be appended; idempotent by marker."""
    txt = open(p("content", "executive-summary.md"), encoding="utf-8").read()
    if "third verification pass" in txt:
        print("executive-summary: section already present")
        return False
    return True


# ----------------------------------------------------------------------- content/index.md
IDX_EDITS = [
    ("| Injury and availability collection | running — 254 rows snapshotted at 04:45Z, **re-read at 22:35Z: 279 rows across 26 clubs** | `data/injuries_2026_wk10.csv`, `data/injuries_wk10_2026_hubrefresh.csv`, `data/injury_delta_a392.csv` | no stored history, so no availability signal can be backtested (FL-27, Q-36) |",
     "a third read at 12:45Z",
     "| Injury and availability collection | running — 254 rows snapshotted at 04:45Z, re-read at 22:35Z (279 rows, 26 clubs), **a third read 13 Nov 12:45Z: 296 rows across all 28 clubs** | `data/injuries_2026_wk10.csv`, `data/injuries_wk10_2026_hubrefresh.csv`, `data/club_availability_20261113_66faefac.csv`, `data/injury_delta_a392.csv` | no stored history, so no availability signal can be backtested (FL-27, Q-36, S-46) |"),
    ("| Depth deficiency by side of the ball | 26 clubs with two-sided counts off the official filing; verified 1st-to-4th string chains for the 2 clubs whose charts were transcribed | [Depth Deficiencies](deficiencies.html), `data/deficiency_by_club_a392.csv` | 30 club charts not transcribed (Q-37, S-39) |",
     "18 joined rows on the 13 November read",
     "| Depth deficiency by side of the ball | 26 clubs with two-sided counts off the official filing; the 13 November read joins an unavailable name to the column it holds on the club's own chart — **18 joined rows on the 13 November read, 8 of them 1st string**, for the 4 clubs this build transcribes | [Depth Deficiencies](deficiencies.html), [Week 10 availability](availability-1113.html), `data/availability_deficiency_66faefac.csv` | 28 club charts not transcribed (Q-37, S-39, S-48) |"),
    ("| Strategy registry | 14 entries, none tracked | `data/strategies.csv` | pre-registration + tracking ledger |",
     "| Strategy registry | {{metric strategies}} entries",
     "| Strategy registry | {{metric strategies}} entries; **1 locked before its slate (ST-15)**, none ranked | `data/strategies.csv`, `data/prereg_wk10_66faefac.csv` | tracking ledger + settled volume (G-08) |"),
    ("| Competition | [Strategy registry](strategies.html) | 14 entries including two negative controls |",
     "| Availability | [Week 10 availability](availability-1113.html) |",
     """| Availability | [Week 10 availability](availability-1113.html) | the 13 November hub read: 296 rows, 28 clubs, and every unavailable name from a transcribed chart joined to the column it leaves empty |
| Availability | [Pre-registration lock](preregistration.html) | the first prediction pinned before kickoff: one rule, one threshold, fourteen fixtures, a hash, and the grading tool that fails if the file is touched |
| Competition | [Strategy registry](strategies.html) | {{metric strategies}} entries including two negative controls, one of them the locked rule above |"""),
    ("| Data | [Week 10 injury report](injuries.html) | all 254 official rows, per-row source links |",
     "the frozen 04:45Z snapshot",
     "| Data | [Week 10 injury report](injuries.html) | all 254 rows of the frozen 04:45Z snapshot, per-row source links; later reads are published beside it, never over it |"),
]


def main():
    patch("tools/build_site.py", BUILD_EDITS)
    patch("content/data-dictionary.md", dict_edits())
    if exec_edits():
        fp = p("content", "executive-summary.md")
        src = open(fp, encoding="utf-8").read().rstrip()
        with open(fp, "w", encoding="utf-8") as fh:
            fh.write(src + "\n\n" + EXEC_SECTION.strip() + "\n")
        print("executive-summary: third-pass section appended")
    patch("content/index.md", IDX_EDITS)
    print("done. next: python3 tools/build_site.py && python3 tools/verify.py")


if __name__ == "__main__":
    main()
