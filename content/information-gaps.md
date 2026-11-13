# What we know, what we don't, and how to find out
> The brief asks for a clear list of questions, the information we have, the information we do not, and suggestions for discovering what is missing — before any decision is made. This page is that list: the question register restated as an information inventory, so a reader can see at a glance which decisions are blocked by *missing facts* and which are blocked by *missing entitlements*.

## The shape of the gap

| Measure | Value |
| --- | --- |
| Decision-blocking questions | **{{metric questions}}** |
| Priority 0 — blocks a gate outright | **{{metric s745_p0}}** |
| Questions where we currently hold **nothing** | **{{metric s745_have_empty}}** |
| Questions with a plausible official route to an answer | **{{metric s745_official_route}}** |
| Questions still open | **{{metric s745_open}}** |

Those two middle numbers are the ones that matter. A question where we hold nothing is not
"early" — it is unanswerable until someone goes and gets something.

## The whole register

{{csv data/s745_information_gaps.csv;;cols=id:ID,priority:Pri,question:Question,information_we_have:What we have,information_we_lack:What we lack,discovery_action:How to close it,official_route_exists:Official route,status:Status;;source=S-REGISTER-745;;group=priority;;caption=All {{metric questions}} questions, grouped by priority, in the register's own words. "What we have" and "what we lack" are the register's existing fields; nothing has been re-worded to look better.}}

## The ones where we hold nothing at all

{{csv data/s745_information_gaps.csv;;cols=id:ID,priority:Pri,question:Question,blocks:Blocks,information_we_lack:What we lack,discovery_action:How to close it;;source=S-REGISTER-745;;filter=have_is_empty=yes;;caption={{metric s745_have_empty}} questions where the register's own "what we have" field begins with nothing. These are the genuine unknowns: no amount of analysis inside this repository closes them, because there is no input to analyse.}}

## Blocked on a decision, not on data

{{csv data/s745_information_gaps.csv;;cols=id:ID,priority:Pri,question:Question,blocks:Blocks,information_we_have:What we have,discovery_action:How to close it,status:Status;;source=S-REGISTER-745;;filter=priority=P0;;caption=Every priority-0 question. Most of these are not research problems. Q-01 is a purchasing decision, Q-03 is a policy decision, Q-26 is a money decision — the information exists, the authorisation does not.}}

## Discovery suggestions — how to close the gaps

These are the concrete actions that would convert a blank into a fact. Each is written against
the question it closes.

| Gap | Why it is still open | Discovery suggestion | What it would unlock |
| --- | --- | --- | --- |
| Prices and capture times (Q-01) | no price source is reachable from this sandbox | decide the vendor tier (exchange, book or aggregator) and license one season of closing spreads and totals with timestamps | vig stripping, fair-value deviation, CLV, and 9 of 14 gates |
| Player-level data (Q-02) | public box-score facts only | compare the league's Next Gen Stats terms against open alternatives; pick one and version it | prop models, and any replacement-cost estimate for a backup |
| Injury history (Q-36, FL-35) | three filings a week, none stored point-in-time | snapshot the hub on a fixed schedule and store each filing as a dated event; start with the Week 10 file, which now has a second dated read | every availability feature and any backtest of one |
| Club depth charts (this session) | the league publishes none; clubs publish them as HTML | re-run `scripts/build_s745_depth.py` weekly. It fetched 31 of 32 on 2026-11-13; Houston's is an image (FL-60) | the replacement chain behind the deficiency register |
| Joint bet settlement (Q-12) | no parlay or SGP settlement archive | record, per leg, the settlement outcome of every tracked bet; do not estimate a correlation before then | every rho in the correlation table that is currently blank |
| Whether the served site is the audited one (FL-23) | egress from this sandbox excludes github.io | have a session with egress fetch the live URL and compare digests | closes the last open flag from the 12 November audit |
| Backtest-versus-forward policy (Q-03) | no written rule | adopt S-04 as policy and record the decision in the register | makes the leaderboard mean anything |

## Rules this page follows

* **No answer is filled in.** Where the register says we lack something, this page says we lack it.
  A blank is rendered `not published`, never as "unknown but probably fine".
* **No inference from another tree.** Five other session trees publish analytics in this
  repository. Their derived numbers are not restated here as this project's own findings; see
  [Q-29](questions.html) and the [verification method](methodology.html).
* **"Official route exists" is a computed guess and is labelled one.** It is a keyword match over
  the register's own "how to close" text, not a verified claim that the page is fetchable. Where
  the match fails the cell reads `not established`, which means *no keyword matched* — not *no route exists*.
