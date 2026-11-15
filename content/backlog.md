# Brief Backlog — the 71 line-items the register never tracked
> The owner's brief is longer than the requirement register. This page is the missing part, written down line by line, each with the official page that would have to be read and the state it is actually in.

## What this page is, and what it is not

`data/requirements.csv` holds {{metric requirements}} requirements. They were reconstructed from the *summary* of the brief. The brief itself also contains a line-item backlog of specific directives — a price-snapshot store, a verified results feed, side-then-total-then-moneyline ordering, depth-of-replacement rather than fact-of-replacement, injury as a surprise rather than a level, a 32-team roster and IR sweep, a point-in-time snapshot ledger, a stadium weather overlay, a two-stage skill leaderboard, three explicit **Reject:** decisions, and twenty-eight items tagged with `VR-` and `VQ-` codes.

None of those 71 lines are tracked anywhere else in the repository. `grep -rl "VR-24" .` and `grep -rl "price-snapshot" .` both return no hits outside `.git`. They are transcribed here so that "collect, organize and analyze utilizing a full list of requirements" has a list to be checked against.

Each row carries the **gate that blocks it** and the **number that would clear it**, using the same fourteen gates as the [validation gate register](validation-gates.html).

> **Source class.** The directives, the gate mappings and the clearing numbers are owner instruction and project design. They are **not official NFL facts** and are not verified by an NFL source. The `Source` column on each row links the **official page that would have to be read** to satisfy the directive — that link is an official source, and it is the dependency, not evidence that the work is done. Statuses, gate mappings and clearing numbers are project design. `re-read 2026-11-15` means an agent fetched that page on that date and recorded what it showed; `not re-read today` is a real value and is not a claim; `no official source exists` means the league does not publish the thing the directive needs.

> **Two registers, one brief — read them together.** While this page was being built, a parallel session merged a [Brief Coverage & Freshness](brief-coverage.html) page with an {{metric cov_matrix_rows}}-clause matrix over the same brief. They answer different questions and neither is a superset: that page classes each clause as covered, partial, blocked, uncovered or resolved; this page names **the gate that blocks it, the number that would clear it, and the official page that would have to be read**. The `Coverage clause` column on every row below is the id of the nearest clause in that matrix, matched by string similarity at a 0.72 cutoff by `tools/build_backlog_58e9c708.py` — it is a navigation aid computed by a script, not an official fact and not a claim that the two rows mean exactly the same thing. {{metric backlog_unmapped}} of the {{metric backlog_directives}} rows have no clause near enough to link, and are shown as not published rather than linked to something wrong.

## Verification performed on 15 November 2026

Eight official pages were fetched and read. What each one showed is recorded below, and nothing on this page asserts more than that.

{{csv data/backlog_reads_58e9c708.csv;;cols=page:Official page,url:URL:urls,what_the_official_page_shows:What the official page shows,unblocks:Directives this unblocks,flag:Flag;;source=S-REPO;;caption=Read by this session on 2026-11-15. The injury hub is still labelled Week 10 on that date, which is why the hub rows and the Week 11 schedule rows describe different weeks.}}

## Findings published from those reads

Five irregularities, published rather than edited. The three that change what is possible are also raised on the [Flagged for Review](flagged-for-review.html) page as FL-96, FL-95 and FL-96.

{{csv data/backlog_findings_58e9c708.csv;;cols=id:ID,type:Type,severity:Severity,finding:What we found,evidence:Sources:urls,decision_impact:Effect on decisions,directives:Directives;;source=S-REPO;;caption=Evidence links are the official pages, or the repository file, that each claim rests on. Nothing here was corrected in place.}}

## Summary of the register

Counts are computed from the register on every build, so this table cannot drift from it.

{{csv data/backlog_summary_58e9c708.csv;;cols=grouping:Grouping,bucket:Bucket,count:Count,share_pct:Share pct;;source=S-BRIEF;;group=grouping;;caption=Theme counts and status counts over the same {{metric backlog_directives}} directives.}}

## Directives the brief tagged with a code

Twenty-eight brief lines carry `VR-`, `VQ-` or `SG-` codes. These are the ones where the code is printed in the brief itself; the rest of the register leaves the code blank rather than inventing one.

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,brief_code:Code,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked;;source_col=dependency;;filter=brief_code=*;;caption=The Source column links the official page each directive depends on.}}

# The register, by theme

## Prices

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Prices;;caption=Two of the three are blocked at the source: the league publishes no betting prices, so a price store and a vig decomposition have nothing official to hold.}}

## Results

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Results;;caption=The results feed is the spine every backtest needs. One Week 10 game has settled; the official scores page publishes the rest as kickoff times.}}

## Origination

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Origination;;caption=Spread and total are originated; the moneyline, the probability column and the opponent adjustment are not.}}

## Modelling

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Modelling;;caption=Ablations, opponent-aware ratings and a frozen three-way split. None has been run on the canonical corpus.}}

## Availability

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Availability;;caption=The largest theme, and the one where the official sources turned out to be richer than the repository assumed. The reserve-list and transactions items were carried as blocked and are not.}}

## Depth

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Depth;;caption=Thirty-one of thirty-two club charts are transcribed; Houston publishes an image. The Packers chart re-read today prints jersey numbers, empty slots and a fourth running back in a row with a blank position cell.}}

## Leaderboard

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Leaderboard;;caption=Proper scores, divisions, a demotion gate and controls. The canonical leaderboard ranks nothing, so none of these can be exercised yet.}}

## Luck

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Luck;;caption=Two luck files exist and are published on the skill-vs-luck page. The brief asks for the panel on the dashboard itself.}}

## Correlation

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Correlation;;caption=No gate is mapped here: the register defines no correlation-estimation threshold, and inventing one would be a new gate rather than an existing one.}}

## Venue

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Venue;;caption=Week 10 carries a venue for all fourteen fixtures. Week 11 does not, although the official page names every stadium.}}

## Governance

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Governance;;caption=Pre-registration, drift alarms, durable storage and the public-private split. Two of the nine are already partly done.}}

## Reporting

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why it is in this state;;source_col=dependency;;filter=theme=Reporting;;caption=One directive: a weekly diff on a schedule, rather than a snapshot that silently replaces the last one.}}

## Rejected by the brief

Two directives are recorded because the brief rejects them. They are kept here, marked `rejected`, so they cannot be re-proposed later as though they were open questions.

{{csv data/brief_backlog_58e9c708.csv;;cols=id:ID,brief_code:Proposal,directive:Directive,coverage_matrix_id:Coverage clause,status:Status,blocks:Gate that blocks it,clears_with:Number that clears it,verified_2026_11_15:Checked,note:Why the brief rejects it;;source_col=dependency;;filter=kind=rejected;;caption=Declared, not open. The Packers chart re-read today is the reason the jersey-number shortcut is dangerous: the club prints jersey numbers ahead of every name, so a shortcut would read a printing convention as a depth order.}}
