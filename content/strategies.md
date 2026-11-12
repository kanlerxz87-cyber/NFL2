# Strategy Registry
> Fourteen registered entries — ten candidate strategies, two negative controls, one measurement-only experiment and one do-nothing baseline — each with its thesis, its signals, its entry rule, its stake rule, its correlation treatment and the gates standing in its way.

An entry is a *specification*, not a claim. Nothing here has been tracked, so nothing here has a record. Registration is the point at which a strategy's inputs, rules and planned sample are frozen; after that, edits inside a measurement window are prohibited by gate G-11, which is the difference between a competition and a group of people adjusting their models until the numbers look good.

{{csv data/strategies.csv;;cols=id:ID,name:Strategy,bet_type:Type,market:Market,thesis:Thesis,signals:Signals,entry_rule:Entry rule,stake_rule:Stake,correlation_treatment:Correlation,n_target:Planned n,gates_blocking:Blocking gates,status:State;;source=S-DESIGN;;caption="Planned n" is the sample required before a claim, from the arithmetic on the removing-luck page. "designed, not tracked" means exactly that; "blocked on prices" means the entry cannot even be evaluated yet.}}

## Why the two controls are entries, not footnotes

| Entry | Role | What it can prove |
| --- | --- | --- |
| ST-12 do-nothing baseline | the zero line | that a strategy's after-vig result is indistinguishable from never betting — the most common way a "winning" model is a losing one |
| ST-13 public-news echo | the latency test | that our signals contain information the market has not already incorporated; if betting the headline direction does as well as our model, we have built a news reader |

A leaderboard without a zero line is a ranking of self-reports. Both controls stay permanently registered, and both are reported next to every candidate.

## Rules for adding an entry

1. Declare every input dataset and every signal id. Overlap above 60% of signals makes two entries one family for reward purposes (gate G-13) — otherwise the leaderboard rewards the same idea five times.
2. State the thesis as something that could turn out to be false, and name the observation that would kill it (S-21).
3. State the correlation treatment even when the answer is "single leg, not applicable". The entries where people skip this field are the parlays and prop combos, which is exactly where the error is expensive.
4. Freeze the stake rule at registration. A stake rule that changes with recent results is a mood, not a rule.
5. Declare a market capacity. A signal worth 3 units a week and a signal worth 300 are different projects and must not be ranked as though they were the same.

## Where the entries came from

Every candidate strategy above is built out of two things the repository actually has: the weekly availability and depth record from the league, and the fixture facts derivable from official kickoff timestamps. That is deliberate. A registry written from intuition would have twenty entries and no data; a registry written from the data we hold has fourteen entries, and each one names the missing input that stands between it and a test.
