# Injury Hub, 15 November against 13 November — the delta

> A dated, row-level read of the official Week 10 injury hub taken on **15 November 2026 at 12:51Z**, set against the **13 November 2026 12:46Z** file. The rule on this page is the one the brief asks for: the **change** between two reads is published, never the level of either one (S-47 on the suggestion register). Source for every row: nfl.com/injuries, registered as S-INJ-8DEE.

Source for every row: [nfl.com/injuries](https://www.nfl.com/injuries/).

## What the official page shows now

- **Slate:** the 14 Week 10 games involve 28 clubs, and this read covers every one of the 28 clubs on the slate. It is still titled "Week 10" on 15 November. Its Sunday block is dated 15 November and its Monday block 16 November.
- **Los Angeles Chargers and Baltimore Ravens have player rows now.** On 12 November the hub answered both with "No Injuries Reported" ([FL-01](flagged-for-review.html)). On 15 November it lists 19 Chargers rows and 10 Ravens rows, including 12 game-status designations between them. The 13 November file has no rows for either club, so this is a change in the source, not a gap in our file ([FL-81](flagged-for-review.html)).
- **Game-status designations went from 9 to 171** across the slate, with no player removed from the record. The 13 November file has blank injury and designation cells for players whom the 15 November page shows with an injury; FL-73 lists the New England rows ([FL-73](flagged-for-review.html)). Read the 13 November count as a collection gap, not as a level of injury ([FL-83](flagged-for-review.html)).
- **Practice codes changed for 102 of the 296 players** on both reads. A move toward full practice is the signal the brief asks for; a move away from it is the other half. Both are shown in the per-club table below, as counts. The player-level movement is in the data file.

## Per-club delta (28 clubs on the slate)

{{csv data/hub_delta_8dee7df7.csv;;cols=club:Club,rows_13nov:Rows 13 Nov,rows_15nov:Rows 15 Nov,rows_added_15nov:Added,designated_13nov:Designated 13 Nov,designated_15nov:Designated 15 Nov,out_15nov:Out 15 Nov,questionable_15nov:Questionable 15 Nov,doubtful_15nov:Doubtful 15 Nov,practice_changed_shared:Practice changed,state_15nov_vs_13nov:State;;source_col=source;;caption=Counted by tools/hub_delta_8dee7df7.py from the two dated files on every build. Blank counts mean the club had no rows on that read. "Practice changed" counts players on both reads whose practice code moved. No player was removed from the record between the two reads.}}

## Players who are on the 15 November read but not the 13 November read

These 51 rows are new to the record. Every one of them is on the official page as read on 15 November; none was added by us. Practice codes: D = did not practise, L = limited, F = full ([hub read](https://www.nfl.com/injuries/)).

{{csv data/hub_new_rows_8dee7df7.csv;;cols=club:Club,player:Player,pos:Pos,injury:Injury,practice:Practice,game_status:Game status;;source_col=source;;caption=Row-level read in data/hub_read_8dee7df7.csv (347 rows). Blank injury or game-status cells are blank on the official page, not zero.}}

## What this page does not establish

- **It is not a replacement analysis.** The hub gives who is listed and their designation. It does not say who started, because the official inactive list and the snap counts come after the kickoff. The depth question is still open ([FL-06](flagged-for-review.html), [Q-44](questions.html)).
- **It is not a level of health.** A blank cell is a blank cell. Clubs the hub answers with "No Injuries Reported" are a stated state, and no club is read as healthy because it is absent.
- **It is not yet machine-verified.** The 15 November rows were transcribed by hand from the rendered page. A second read of the Monday block (Chargers and Ravens) on the same day matched the transcription name for name, but a raw capture with a stored hash does not exist yet ([FL-82](flagged-for-review.html)). The planned fingerprint monitor is in open pull request #71, owned by another session, and is not part of this page.
- **Week 10 is still the title of the official page.** The data here is a Week 10 read on 15 November, not a Week 11 read.

## Method

1. Each of the 347 rows was copied from the rendered official page on 15 November 2026. The file's read time is 12:51Z, the time it was written; the page fetches were made in the minutes before that. The file keeps the official injury text, practice status and game status, and the practice codes are mapped to D, L and F.
2. `tools/hub_delta_8dee7df7.py` compares the two dated files by club and by player. It fails the build if the 15 November read does not cover the 28 clubs on the slate, if any row lacks an nfl.com source, or if any player on the 13 November read is missing from the 15 November read. All three checks pass.
3. Reproduce with `python3 tools/hub_delta_8dee7df7.py`. The outputs are `data/hub_delta_8dee7df7.csv` and `data/hub_new_rows_8dee7df7.csv`.

Flags for this page: [FL-81](flagged-for-review.html) (Chargers and Ravens), [FL-82](flagged-for-review.html) (hand transcription), [FL-83](flagged-for-review.html) (designation and practice changes). Earlier reads are on the [Availability Watch](availability-watch.html) and the [Week 10 injury report](injuries.html) pages, which still describe the 13 November state.
