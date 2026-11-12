# Data Dictionary
> Every file, every column, the transform applied to it, and the source id it inherits — so a reader can re-derive any cell on this site from the official page.

All files are pipe-delimited CSV with a header row. The generator enforces the field count per row: a row that does not match the header width fails the build. That check found six shifted rows in this dataset while the site was being assembled, which is the only reason to trust it.

## Files

| File | Rows | Grain | Source of record |
| --- | --- | --- | --- |
| `data/injuries_2026_wk10.csv` | 254 | one player × game × filing | S-INJ |
| `data/depth_changes_2026_wk10.csv` | 227 | one roster or availability event per club | S-ROUNDUP, S-DARNOLD, S-WILLIS, S-JACKSON, S-NOV5, S-NOV6, S-HUNTLEY |
| `data/standings_2026.csv` | 32 | club × season-to-date | S-STAND |
| `data/schedule_2026_wk10.csv` | 14 | game | S-WK10REP |
| `data/sources.csv` | 26 | source | — |
| `data/requirements.csv` / `questions.csv` / `suggestions.csv` / `flags.csv` | 40 / {{metric questions}} / {{metric suggestions}} / {{metric flags}} | register rows | S-BRIEF, S-DESIGN, S-REPO |
| `data/games_2026_wk1_9.csv` | {{metric games_log}} | completed results, weeks 1–9, imported from the parallel session and re-audited here | S-GAMES26 |
| `data/gates.csv` / `signals.csv` / `strategies.csv` / `correlation.csv` / `leaderboard.csv` | 14 / 18 / 14 / 12 / 14 | design rows | S-DESIGN |
| `data/build_manifest.json` | — | build output, counts, allowlist | generated |

## Column meanings — injury snapshot

| Column | Type | Definition and rule |
| --- | --- | --- |
| `game` | id | fixture key, joins to `schedule_2026_wk10.csv.game_id`; assigned in the order the official page lists games |
| `team` | abbr | league club abbreviation as published (LAR not LA) |
| `player` | text | display name exactly as published, including suffixes ("Gervon Dexter Sr.", "Carlton Davis III", "Deebo Samuel Sr.") |
| `slug` | key | the league's player URL slug, taken from the published href. Not a stable id — collisions carry opaque suffixes ([FL-15](flagged-for-review.html)) |
| `pos` | code | league position string; used only for the offence/defence split below |
| `injury` | text | populated for 9 of 254 rows because that is what the hub published; never backfilled from prose |
| `practice` | enum | `F` = Full Participation in Practice, `L` = Limited Participation in Practice, `D` = Did Not Participate In Practice |
| `status` | enum | `OUT` = Out, `Q` = Questionable, `D` = Doubtful; empty means no designation had been filed |

## Controlled vocabularies

**Position → side of ball** (a project convention used only to split counts; it is our mapping, not the league's):

| Side | Positions |
| --- | --- |
| Offence | QB, RB, FB, WR, TE, T, G, C, OT, OG |
| Defence | DE, DT, LB, OLB, Edge, CB, S, FS, SS, DB, DL |
| Special teams (excluded from both) | K, P, LS |

**Depth-event types** — RULED-OUT, RULED-OUT-WK9, OUT-SEASON, IR, IR-ACTIVATED, IR-RETURN-DESIG, IR-DECISION, DEPTH-CHART, PRACTICE, DNP, NO-DESIGNATION, SIGNING, ROSTER-CUT, TIMELINE, SEASON-IMPACT. A row's `change` value must be one of these; `verify.py` fails on anything else, because an uncategorised event silently disappears from every count.

## Blank policy

An empty field means the official source did not publish it. It renders as `not published`, is excluded from every count and statistic, and never becomes 0, "no" or a plausible default. Cells deliberately filled with the string `not published` (in the correlation and leaderboard tables) mean the same thing, written explicitly because the column is one where a reader would otherwise expect a number.

## Blank census — where the site is honestly empty

{{blank_census}}

<p class="caption">This is not a defect list; it is the shape of what can be claimed. A table with no blanks in a domain like this would be a table someone filled in.</p>
