# Suggestion review console
> A place to review every suggestion and choose a path **before** anything is implemented. Nothing on this page has been built on your instruction: it orders the {{metric suggestions}} suggestions the register already holds, scores them on the fields the register already publishes, and bundles them into four candidate paths so you can approve a path rather than forty-five separate items.

## How the score is produced — and what it is not

`priority_score = impact_pts / (effort_pts + risk_pts)`, where the register's own codes become
`H=3, M=2, L=1` for impact and `L=1, M=2, H=3` for effort, and the risk text is reduced to its
first word (`Low=1, Medium=2, High=3`).

This is **arithmetic on published fields, not evidence**. It orders the register; it does not
rank the world. Two suggestions scoring 1.50 are tied because their fields are tied, not because
they are worth the same. The point of publishing the arithmetic is that you can change the
weights and see the order move — the inputs are all on the [suggestion register](suggestions.html).

## The four candidate paths

{{csv data/s745_decision_paths.csv;;cols=path:Path,path_name:Name,goal:Goal,suggestions:Items,high_impact:High impact,quick_wins:Quick wins,total_effort_points:Effort pts,suggestion_ids:Contains;;source=S-REGISTER-745;;caption=Each path is a bundle of the register's existing suggestion ids. Membership is this session's proposal, computed from each suggestion's category, and it is printed in full so you can move a row. "Quick wins" are high-impact, low-effort items inside that path.}}

{{csv data/s745_decision_paths.csv;;cols=path:Path,unblocks:What it unblocks,does_not_fix:What it does NOT fix,first_milestone:First milestone;;source=S-REGISTER-745;;caption=The honest half of the argument. Every path on this site is cheap to describe and expensive to finish, and each one leaves something else unsolved — that is the point of choosing a path rather than approving everything.}}

## Every suggestion, scored and ranked

{{csv data/s745_suggestion_scores.csv;;cols=rank:#,id:ID,title:Suggestion,path:Path,impact:Impact,effort:Effort,risk_class:Risk,priority_score:Score,quick_win:Quick win,depends_on:Depends on,decision:Register decision;;source=S-REGISTER-745;;caption=All {{metric suggestions}} suggestions in score order. The decision column is the register's own status, carried through untouched — nine are already "adopted (v1)" in this build and do not need your approval again; the ones marked "recommended", "open - owner decision" or "blocked" are the ones this console exists to settle.}}

## The short list

{{csv data/s745_suggestion_scores.csv;;cols=rank:#,id:ID,title:Suggestion,path:Path,priority_score:Score,decision:Register decision;;source=S-REGISTER-745;;filter=quick_win=yes;;caption=High impact, low effort, {{metric s745_quickwins}} of them. If you approve nothing else on this page, these are the items where the cost of being wrong is close to zero.}}

{{csv data/s745_suggestion_scores.csv;;cols=rank:#,id:ID,title:Suggestion,path:Path,impact:Impact,effort:Effort,risk_class:Risk,priority_score:Score,decision:Register decision;;source=S-REGISTER-745;;filter=decision=open;;caption=Everything the register still holds as an open decision. These are the rows that need a human, not a build.}}

## What to decide, in the order I would take them

1. **Pick a path, not a list.** Path A (prove the data layer) is a prerequisite for any of the others being believable, and it is the cheapest — {{metric s745_pathA_quick}} of its {{metric s745_pathA_n}} items are quick wins. Path B (prices) is the one that unlocks 9 of the 14 validation gates and the only one you have to pay for.
2. **Answer [Q-01](questions.html) — the price feed.** Until that is settled, Path C (the availability signal this session just extended to 31 clubs) cannot be *validated*, only built. That is a defensible reason to do A first and B second.
3. **Decide the refresh cadence** ([Q-40](questions.html), [S-43](suggestions.html)). The standings were one game stale on 13 November and nothing on the site recorded when they were read ([FL-35](flagged-for-review.html)).
4. **Decide whether the week 1–9 game log stays frozen** ([Q-41](questions.html), [S-26](suggestions.html)). It is the pre-registered corpus; appending to it invalidates every grade.

## What this console deliberately does not do

* It does not save your choices. Every published page on this site is generated and has no
  JavaScript, so a triage tick-box would be lost on the next build. The durable place for a
  decision is the `decision` column of `data/suggestions.csv`, and the change is one line.
* It does not weight impact more cleverly than the register does. Any weighting you prefer is a
  change to one dict in `scripts/build_s745_decisions.py`.
* It does not score the {{metric flags}} flagged irregularities. Those are defects and gaps, not
  proposals; they are on [Flagged for Review](flagged-for-review.html).
