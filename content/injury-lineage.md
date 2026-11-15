# Week 10 Injury Read Lineage — what each read holds, and what changed
> Every Week 10 injury file in this repository, the official read it came from, what it reconciles against, and the change between reads. Counts and differences only; nothing is inferred. No file here is a retained raw capture, so none is verified byte-for-byte (see FL-80 on the Flagged for Review page).

## What this page establishes, and what it does not

- **Established:** how many player rows each file holds, how many clubs it covers, how each file compares with the earlier file it refreshes, and whether the 254-row headline was correct ([FL-77](flagged-for-review.html): it was not).
- **Established for four clubs:** a live read on 15 November of the 44 player rows for WAS, NYG, NE and DET matches the 15 November file on all 44 rows and the 13 November file on 31 of 44. The 13 differences are the NE and DET rows already flagged in [FL-73](flagged-for-review.html) and [FL-74](flagged-for-review.html).
- **Not established:** which of the 17 added players and 51 changed values reflect the league's own changes and which reflect transcription. No retained capture exists to separate them ([FL-78](flagged-for-review.html)).
- **Not established:** the 12 November transcripts disagree on 12 values for the same players ([FL-79](flagged-for-review.html)).

## 1. Every Week 10 injury file, reconciled

Each read is compared with the earlier file it refreshes. "Only here" and "only in reference" count players; "value differences" counts players present in both whose injury, practice or game-status value differs. Blank cells mean "not published" in that read, never zero.

{{csv data/injury_lineage_d8372691.csv;;cols=read_id:Read,read:Read label,read_utc:Read time (UTC),scope:Scope,player_rows:Player rows,no_injury_blocks:No-injury blocks,clubs_with_players:Clubs with rows,playing_clubs_without_rows:Playing clubs with no rows,reference_read:Compared with,players_only_here:Only here,players_only_in_reference:Only in reference,field_differences_on_shared:Value differences,claim_check:Claim check;;source_col=source_id;;caption=Source column: the registered source for each read, or the official nfl.com/injuries page where no registered row exists. "Playing clubs with no rows" comes from the Week 10 schedule file. The partial 15 November read is compared only with the clubs it covers.}}

The SHA-256 of each repository copy is in `data/injury_lineage_d8372691.csv`, column `sha256_repo_copy`. It hashes the repository file, not the official response, so it proves only that the file has not changed since this build.

## 2. Change by club, between reads

Read this table as counts, never as levels. "Value changes" counts the players present in both reads whose injury, practice or game-status value differs. The 15 November read covers four clubs only; the other clubs are blank for that read.

{{csv data/injury_club_delta_d8372691.csv;;cols=club:Club,week10_status:Week 10 status,rows_L1_254:12 Nov first read,rows_L2_279:12 Nov 22:35Z,rows_L4_296:13 Nov 12:46Z,delta_L4_minus_L2:Change 12 to 13 Nov,rows_L7_15nov:15 Nov four-club read,delta_L7_minus_L4:Change 13 to 15 Nov,value_changes_L2_to_L4:Value changes 12 to 13 Nov,value_changes_L4_to_L7:Value changes 13 to 15 Nov;;source_col=source;;caption=Club abbreviations are the league's own. A bye club is not in the Week 10 schedule file, so it has no row in any read. Clubs with a zero are in the schedule but have no player row in that file; a zero is not a statement that the club is healthy.}}

## 3. Players added or changed between the 12 Nov refresh and the 13 Nov read

Every row is a player whose value differs between the two reads. Blank cells are fields the read did not publish for that player.

{{csv data/injury_delta_players_d8372691.csv;;cols=change:Change,club:Club,player:Player,pos:Pos,injury_12nov_2235:Injury 12 Nov,practice_12nov_2235:Practice 12 Nov:practice,status_12nov_2235:Status 12 Nov:status,injury_13nov_1246:Injury 13 Nov,practice_13nov_1246:Practice 13 Nov:practice,status_13nov_1246:Status 13 Nov:status;;source_col=source;;caption=The earlier value is from the 22:35Z 12 Nov refresh and the later from the 12:46Z 13 Nov read. These are differences between two transcriptions; they are not confirmed league changes ([FL-78](flagged-for-review.html)).}}

## 4. Live spot-check: 44 rows, four clubs

The rows below are the player rows for WAS, NYG, NE and DET on the official Week 10 page, read on 15 November at about 12:50 UTC and transcribed from the page text. Each is compared field by field (injury, practice, game status) with the 15 November file and the 13 November file.

{{csv data/injury_spotcheck_d8372691.csv;;cols=club:Club,player:Player,live_practice:Live practice:practice,live_status:Live game status:status,L7_matches_live:15 Nov file matches,L4_practice:13 Nov practice:practice,L4_status:13 Nov game status:status,L4_matches_live:13 Nov file matches;;source_col=source;;group=club;;caption=Live values from the official page. "Matches" = injury, practice and game status all equal. 15 Nov file: 44 of 44 match. 13 Nov file: 31 of 44 match; the 13 that differ are NE (10) and DET (3).}}

## How these tables are produced

Computed by `scripts/injury_lineage_d8372691.py`, which reads only repository files and writes the four CSVs behind this page. Run with `--check`, it fails if any output differs from its inputs, and CI runs that check on every push. The live transcription is `data/injury_live_chunk_d8372691.csv`. The Kansas City block was cut off in the page text and is not used. The official page remains the reference for every value: [nfl.com/injuries](https://www.nfl.com/injuries/).

Open items that depend on this page: [FL-77](flagged-for-review.html) (headline corrected), [FL-78](flagged-for-review.html), [FL-79](flagged-for-review.html), [FL-80](flagged-for-review.html) (no retained capture), [FL-81](flagged-for-review.html) (row-count corrections).
