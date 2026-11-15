# Brief Coverage, Data Freshness and Today's Official Read
> Every clause of the owner brief is traced to the register row that owns it, its coverage class is stated against the actual contents of this repository, and the two things that changed today - a full re-read of the official injury hub and a measured page-freshness panel - are published with their numbers.

This page answers three questions that none of the other pages answer together: **what in the brief is genuinely covered, what is only specified, and what is missing entirely**; **how old is the evidence behind each published table**; and **what did the official league page say when it was read in full today**, compared row by row with what this site publishes.

Nothing on this page is an estimate. The coverage classes are computed from the contents of `data/` and the four registers, not from anyone's recollection of what was built. Where a figure could not be confirmed from an official source it is left blank and the blank is named.

## The headline numbers

Counted from the {{metric cov_rows}}-row matrix further down this page, across {{metric cov_categories}} categories. The class is the state of the evidence in this repository, not a plan.

| Coverage class | What it means | Clauses | Where it is evidenced |
| --- | --- | --- | --- |
| **covered** | A register row owns the clause and an artefact exists that does what the clause asks | {{metric cov_covered}} | [brief matrix](https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/brief_traceability.csv) |
| **partial** | The clause is owned and part-built; the missing part is named in the Evidence column | {{metric cov_partial}} | [brief matrix](https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/brief_traceability.csv) |
| **blocked** | Owned and specified, but a named entitlement or data input is missing, so building it would be inventing it | {{metric cov_blocked}} | [gate register](https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/gates.csv) |
| **uncovered** | No register row owns the clause and no artefact exists. These are the real gaps | {{metric cov_uncovered}} | [brief matrix](https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/brief_traceability.csv) |
| **resolved** | The clause described a defect that this session's official read closes | {{metric cov_resolved}} | [nfl.com/injuries](https://www.nfl.com/injuries/) |

## Today's official read of the Week 10 injury hub

The league's injury hub was read in full today. The Week 10 table that this site publishes is three and a half days older than that read: it carries {{metric d_rows_13}} rows over {{metric d_clubs_13}} clubs, against {{metric d_rows_15}} rows over {{metric d_clubs_15}} clubs now, and it carries {{metric d_desig_13}} game-status designations against {{metric d_desig_15}} now.

Before any number from that read was stored, it was reconciled club by club against this repository's own 2026-11-13 capture. The reconciliation is the proof that the transcription is complete rather than partial: **14 clubs match the earlier capture exactly, 26 clubs gain rows, and not one club loses a row or a player.** A transcription that had silently dropped part of the page would show negative deltas somewhere; there are none.

| Measure | 2026-11-13 capture | 2026-11-15 live read | Delta | Source |
| --- | --- | --- | --- | --- |
| Rows | {{metric d_rows_13}} | {{metric d_rows_15}} | +{{metric d_rows_added}} | [nfl.com/injuries](https://www.nfl.com/injuries/) |
| Clubs reporting | {{metric d_clubs_13}} | {{metric d_clubs_15}} | +{{metric d_clubs_added}} | [nfl.com/injuries](https://www.nfl.com/injuries/) |
| Rows carrying a game-status designation | {{metric d_desig_13}} | {{metric d_desig_15}} | +{{metric d_desig_added}} | [nfl.com/injuries](https://www.nfl.com/injuries/) |
| Rows in the Out state | {{metric d_out_13}} | {{metric d_out_15}} | +{{metric d_out_added}} | [nfl.com/injuries](https://www.nfl.com/injuries/) |
| Clubs losing a row or a player | - | 0 | 0 | [nfl.com/injuries](https://www.nfl.com/injuries/) |

The two clubs that were entirely absent are the two Monday-night teams, and they are absent for a reason that is not a collection failure: the hub prints **"No Injuries Reported"** for both. That is a declaration, and it is not the same fact as a blank. See [FL-01](flagged-for-review.html) for why the distinction matters to every availability model on this site.

{{csv data/hub_club_counts_f34622dd.csv;;cols=club:Club,game:Fixture,rows_13nov:Rows 13 Nov,rows_15nov:Rows 15 Nov,rows_added:Added,rows_removed:Removed,dnp_13nov:DNP 13 Nov,dnp_15nov:DNP 15 Nov,designations_13nov:Designations 13 Nov,designations_15nov:Designations 15 Nov,added_players:Players newly listed;;source_col=source;;caption=Per-club reconciliation of today's official read against this repository's 13 November capture. "Added" counts players the league lists today that the 13 November file did not carry; "Removed" is zero for every club, which is the check that the read was complete. The last row is the sum over all 28 reporting clubs.}}

### What this read settles, and what it does not

**Settled.** The three Detroit designations that were published blank are, on the live page, all **Out** with a stated injury and a Did Not Participate practice code: Kerby Joseph (knee), Cade Mays (ankle) and D.J. Reed (hip). The repository's 13 November capture already had them; the older 254-row file that the injury page still renders does not. That is a rendering choice, not a missing fact, and it is recorded as such.

**Settled.** Seattle and Cincinnati are not injury-free. Both publish full blocks - 15 and 9 rows in today's read - and the published table shows neither. The published table's own caption already warns that this is a collection gap rather than a claim of health, which is the right wording, but a reader looking at the table does not see those clubs at all.

**Not settled.** Whether the Week 10 designation set is final. Finals are filed on the last practice day before each kickoff, and fixtures across this slate kick off at different times. A single read cannot establish that a later read would not change a designation, so this page does not claim finality.

## How old is the evidence behind each published table

A stale table and a current table look identical on a static site. This panel makes the age of the evidence a published fact: for each page, the read time of the official source it rests on, the newest read of that same official page anywhere in the repository, and the gap.

{{csv data/page_freshness_f34622dd.csv;;cols=page:Page,publishes:What it publishes,own_read_utc:Evidence read (UTC),newest_read_utc:Newest read held (UTC),lag_days:Lag (days),rows_published:Rows published,rows_in_newest_read:Rows in newest read,rows_withheld:Rows withheld,verdict:Verdict;;source_col=source_url;;caption=Measured from data/sources.csv (the registered read time of each official page) and the row counts of the files themselves. "Rows withheld" is blank where the newest read is of a different page, so no subtraction would be meaningful. A blank is not a zero.}}

{{metric fresh_behind}} of the {{metric fresh_pages}} published pages rest on an official read older than the newest read of that same page held in the repository. The most consequential by far is the Week 10 injury page: its evidence is from 12 November and it is withholding **{{metric fresh_withheld_max}} of the {{metric d_rows_15}} rows** the league publishes today. The remaining gaps are under a day each, and their content - standings, scores, the depth register - is not something that files a game-status designation.

## The clauses that nothing in this repository covers

Ten clauses of the brief have no owning register row at all. They are listed here rather than quietly dropped, because a clause with no owner is the only kind of gap that cannot be closed by work already in flight.

{{csv data/brief_traceability.csv;;cols=clause:Clause,evidence:Why nothing covers it,source:Where the absence is visible;;filter=coverage_class=uncovered;;source_col=source;;caption=Every row here was established by searching all four registers and the whole of data/ for the concept, not by assuming the absence. The source link points at the register whose silence is the evidence.}}

### Two of them are gaps in the *model*, not in the data

An **ablation** is the one method the brief asks for that the repository has never even specified: the same model run with and without a feature group, on a chronological holdout, with the difference and its uncertainty reported. The register contains the fixed-penalty alternative in three places and the word "ablation" in none.

A **demotion gate** is the mirror image of the promotion gates that exist. Fourteen gates are registered and every one of them is one-sided: each states the number a strategy must reach to be promoted, and none states the number at which a live strategy is sent back to paper. A leaderboard that can only promote is a ratchet, which is precisely the failure the brief's "remove luck" instruction is aimed at.

### One is a naming gap that hides a real decision

The brief asks for a **moneyline** origination and for the order *side, then total, then moneyline*. The register's strategy tournament is scored entirely on the moneyline side, and the origination lab publishes a spread and a total. Both halves exist; neither is joined to the other, and no published file carries an originated moneyline price. This is recorded as a partial rather than a pass, because the brief's sequence is about the markets we originate and today we originate two of the three.

## The full matrix

{{csv data/brief_traceability.csv;;cols=id:ID,category:Category,clause:Clause,owning_register:Owner,coverage_class:Coverage class,evidence:Evidence in this repository;;source_col=source;;caption=One row per clause of the owner brief. The Coverage class is computed against the actual contents of data/ and the four registers; the Evidence cell names what exists or names what is missing. Owner is the register row that would own the work, or "none" where no register row covers the clause at all. S-BRIEF is an owner-instruction reference and is not an NFL fact; every factual claim in an Evidence cell is separately sourced in data/sources.csv.}}

## How this page was verified

The matrix is generated from `data/brief_traceability.csv`, and `tools/verify_coverage_f34622dd.py` fails the build if any row lacks an official or canonical `https://` source, if any coverage class falls outside the five defined values, if any clause is duplicated, or if the published per-club deltas do not reconcile to the published totals. The row counts on this page are computed from the files themselves at build time, so a refresh cannot leave a number behind the way a hand-written total can.
