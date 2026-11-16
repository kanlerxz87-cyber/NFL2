# Roster Events — official transactions, coverage, and depth versioning (16 Nov 2026)
> Row-level official roster events for 2026 (reserve placements and trades), the coverage verdict for each month, the Week 10 availability join (BL-65), and every depth-chart row that a later roster event may have superseded (BL-34, BL-47). **Not listed never means available** — a player absent from the injury hub is not marked healthy here.

Every row is transcribed by a parser from the league's own transaction pages, retained as raw bytes with a SHA-256 and checked on every run by `tools/drift_alarm_6eeab460.py`. The capture is **not a full season sweep**: the coverage table says which months are complete. Where a month is incomplete, its counts are lower bounds.

## Coverage — which months are complete (FL-121)

{{csv data/roster_coverage_6eeab460.csv;;cols=kind:Kind,month:Month,chain_pages_fetched:Pages fetched,distinct_rows:Distinct rows,last_page_rows:Last-page rows,coverage_status:Status,note:Note;;source_col=source_url;;caption=A month is complete only when its last fetched page is short (fewer than 25 rows, the table's page size) with no Next link. August to November are incomplete: the Next Page cursor returns repeated pages, and on August and September some later pages add rows. No chain is treated as complete (FL-121).}}

## November 2026 — reserve placements joined to the Week 10 injury hub (BL-65)

{{csv data/availability_join_6eeab460.csv;;cols=date_iso:Date,club:Club,player:Player,transaction:Transaction,hub_listed:On hub read (14:44Z),hub_game:Hub game,hub_status:Hub status,availability_mark:Delta and rule;;source_col=source;;caption=Each November reserve placement, joined against the Week 10 hub read of 16 Nov 2026 (14:44Z, transcribed by session 4e475b8b). The join is checked against both raw official captures of the hub (14:39Z and 14:44Z): the player's hub row link is present in both captures for every row, and the join agrees with the transcription on all 25 rows. A placement with no hub row is marked not available for the purpose of this page, and is never recorded as healthy. Placements and hub rows that both exist are a disagreement between two official reads, to be resolved from the next dated read, not a level.}}

## November 2026 — reserve list (official rows)

{{csv data/reserve_list_2026_6eeab460.csv;;cols=date_iso:Date,from_club:Club,player:Player,position:Pos,transaction:Transaction;;filter=month=2026-11;;source_col=source;;caption=Every November 2026 Reserve/Injured row on the official reserve-list pages, with the capture hash that holds it. Count: 25 distinct rows, identical to the rows in the retained runner bytes (FL-122 records a second transcription with 35 rows that the retained bytes do not reproduce).}}

## November 2026 — trades (official rows)

{{csv data/trades_2026_6eeab460.csv;;cols=date_iso:Date,from_club:From,to_club:To,player:Player,position:Pos,transaction:Transaction;;filter=month=2026-11;;source_col=source;;caption=Every November 2026 trade row on the official trades page. Two rows dated 11/10 move Colts receivers: Keenan Allen to San Francisco and Josh Downs to Kansas City (BL-34).}}

## Depth rows a roster event may have superseded (BL-34, BL-47)

{{csv data/depth_versioning_6eeab460.csv;;cols=club:Club,position_label:Position,depth:Depth,player:Player,chart_as_published:Chart as published,versioning_status:Versioning status;;filter=versioning_status=!no_departure;;source_col=chart_source;;caption=Only the rows that need a decision, and never a settled verdict. "Undated chart" means the club's chart prints no date, so the row cannot be versioned against a roster event (FL-124). "Candidate" means a reserve placement falls after a dated chart; reserve placements are not reversed in the wire, so the row is a candidate until an activation or a newer dated chart supersedes it (FL-125). Depth order comes from the club's published chart only, never from jersey number, experience or salary.}}

## Method and limits

- **Source of each row:** the official month page of the league's transactions tabs, retained as raw bytes and checked against its SHA-256 in `data/roster_capture_manifest_6eeab460.csv`. Each row's capture hash is in the table.
- **Pagination:** the official tables show 25 rows per page and link the rest through a cursor. The capture follows that cursor to its end, or to a cap of 12 pages, and records an open chain as incomplete.
- **Depth:** the depth register holds 1,558 rows across 31 club charts. Houston has no chart in this register; the backlog records that the club publishes its chart as an image with no HTML table (BL-32). 810 rows carry no printed chart date.
- **Not claimed here:** a full-season roster sweep (BL-13), a team-level availability model, or any player's current health. Those need the complete months and a dated injury read for each week.
- **Open items:** the chain-cursor behaviour for August to November (FL-121); the second November transcription that disagrees with the retained bytes (FL-122); the Colts depth chart, which the register does not date (FL-126).
