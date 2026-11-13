# Depth Cascades — Re-verified Against the Official Pages
> The brief asks the site to know when a defence or an offence is down to its second, third or fourth string. The earlier depth register (18 cascades, Week 10) made that claim with labels such as *Names and DNP Verified*. On 13 November 2026 each cascade was checked, player by player, against the club's own depth chart and the league's own Week 10 injury report. This page publishes the outcome, including every contradiction.

## What was checked, and against what

Two sources, both read on **13 November 2026**:

1. **The club's depth chart** for each of the 12 clubs named in the cascades. The Seahawks and Patriots charts were read in full (two and three pages); the other ten clubs' charts were read on their first page, and their page counts were not re-checked. All were read on the club's own website. Several clubs label their chart *unofficial*, and the Patriots' page is titled "Unofficial Depth Chart". The label on each page is recorded in [FL-50](flagged-for-review.html); it is not assumed.
2. **The official NFL Week 10 injury report** at [nfl.com/injuries/league/2026/REG10](https://www.nfl.com/injuries/league/2026/REG10), read in all seven pages. Players placed on injured reserve are not on the weekly report; their status is taken from NFL.com news articles and marked `NEWS_ONLY` ([FL-52](flagged-for-review.html)).

Nothing is inferred. A player who does not appear on the report is shown as *not on report*, which is a fact about the report and not a statement that he is healthy.

## Verdicts

| Verdict | Meaning |
| --- | --- |
| **VERIFIED** | Every named player is placed where the cascade says on the club's chart, and every status the cascade gives matches the report. Players the cascade says are absent from the chart are counted as consistent. |
| **PARTLY** | The core string is confirmed, but at least one status is wrong, one injury detail is not on the official injury report table, or a slot is contested because the chart lists one slot per row. |
| **CONTRADICTED** | The chart order or the status of a named starter disagrees with the cascade. The cascade should not be used until it is corrected. |

Counts in the table below are computed from the player rows in the detail table. Match means `MATCH` or `CONSISTENT`; contradicted means `STATUS_MISMATCH`, `STATUS_UNDERSTATED` or `CHART_MISMATCH`; partly or unverified is everything else.

{{csv data/depth_cascade_verdicts_6539b6a0.csv;;cols=cascade:Cascade,club:Club,unit:Unit,verdict:Verdict,claimed_tier_label:Claimed tier label,rows_total:Players checked,rows_match:Match,rows_mismatch:Contradicted,rows_other:Partly or unverified,reason:Why,chart_url:Club chart:urls;;source_col=report_url;;caption=Eighteen cascades, one row each. The verdict follows the rule above and is checked against the player rows below. Source for every row: the official Week 10 injury report, with the club chart shown alongside.}}

## Line-by-line detail

Each row is one named player in one cascade. *Club chart shows* is the column and row the club's own page places him in, in the club's own words. *Official report* is what nfl.com published for him on 13 November, or *not on report*.

**Result codes:** MATCH (chart and report agree) · CONSISTENT (not on report, which fits the claim) · STATUS_MISMATCH (report disagrees with the cascade's status) · STATUS_UNDERSTATED (the cascade states less than the report) · CHART_MISMATCH (the chart's string order disagrees with the cascade) · NOT_ON_CHART (the chart does not list him) · OMITTED_BY_CASCADE (the chart lists a player the cascade does not name, or the cascade omits a starter) · PARTLY_SLOT (status agrees but the chart's slot differs from the cascade's label) · NEWS_ONLY (status or injury detail comes only from an NFL.com news article, not the report table).

{{csv data/depth_cascades_6539b6a0.csv;;cols=cascade:Cascade,club:Club,player:Player,claimed_string:Cascade says (string),claimed_status:Cascade says (status),chart_placement:Club chart shows,official_report:Official report 13 Nov,result:Result,note:Note,chart_url:Club chart:urls;;source_col=report_url;;group=cascade;;caption=139 player rows across the 18 cascades. Club charts are linked on each row; the official report is the source column. Read the result code before the words.}}

## What this changes

- **Do not price, or describe a game, on a cascade tier until its verdict is VERIFIED.** Five are verified, nine are partly confirmed and four are contradicted.
- **Nine statuses are wrong on the official report, and two are understated.** The full list is in [FL-48](flagged-for-review.html).
- **The Ravens cascade (DC-01) is out of date.** It omits Jacoby Brissett, who is listed as the Ravens' starting quarterback and was acquired from Arizona on Nov. 6 ([NFL.com](https://www.nfl.com/news/nfl-trade-deadline-track-every-move-since-start-of-2026-regular-season)). It also treats Austin Reed as a practice-squad player, while NFL.com's Nov. 5 roundup says he was signed to the active roster ([FL-47](flagged-for-review.html)).
- **Four cascades depend on a rule the repository has not chosen.** Several clubs list one slot per row, so column 1 is not always the starter. The owner's decision on the string rule is [Q-49](questions.html); the options are in [S-57](suggestions.html).
- **Coverage is twelve clubs, and the other twenty of the 32 have no re-verified chart in this session.** The registers disagree on how many clubs are verified, which is [FL-45](flagged-for-review.html).

Every irregularity above is on the [Flagged for Review](flagged-for-review.html) page with its source link. Nothing here has been fixed silently.
