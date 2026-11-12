# Signal Catalogue
> Eighteen signal families: what each one is, what it consumes, whether it is a surprise or a level, how fast it decays, how much money it can carry, and which gate stands in its way.

A signal is only listed here if its input is either already in the repository or has a named owner and a route to getting here. "Surprise or level" is the most important column: a *level* (a club is missing its left tackle) is public knowledge within hours and is mostly already in the price; a *surprise* (the club filed a downgrade nobody expected, or failed to file at all) is the only thing a small operation can systematically capture. That is why the availability family dominates this catalogue and why the highest-conviction item on it — SIG-03 — is literally a signal about the *absence of data*.

{{csv data/signals.csv;;cols=id:ID,signal:Signal,family:Family,definition:Definition,inputs_required:Inputs,surprise_or_level:Type,direction_when_positive:Direction if the signal is real,decay_note:Decay,capacity_note:Capacity,blocking_gate:Gate,status:State;;source=S-DESIGN;;caption=State is "specified" where the input exists, "blocked on data" where it does not, and nothing in between: no signal here is measured, because measuring one needs prices or playing time.}}

## What is buildable today, before any decision

Two signals need nothing but data already in this repository, and they are the ones to build first — a working signal pipeline on free inputs is worth more than a perfect design on rented inputs.

| Signal | Input in repo | Test we can run without prices |
| --- | --- | --- |
| SIG-09 rest asymmetry | [schedule](league-data.html) — kickoff timestamps | does the short-week club cover less often than its record implies, using only official results we choose to ingest |
| SIG-10 travel and kickoff hour | schedule venue strings | does an overseas or non-standard-hour game have a wider result distribution than a domestic noon game |
| SIG-03 undisclosed absence | injury hub vs official prose, daily | frequency and duration of "no injuries reported" blocks that contradict same-week reporting — a data-integrity signal with direct pricing consequences |

## Family summary

| Family | Signals | Share blocked on data | Read |
| --- | --- | --- | --- |
| availability | SIG-01, SIG-02, SIG-03, SIG-07 | 0 of 4 | our strongest area, because the league publishes the raw material weekly |
| depth | SIG-04, SIG-05, SIG-06, SIG-08 | 3 of 4 | the requirement that cannot be met without playing-time data; only the ambiguity signal (SIG-06) is close to buildable |
| context | SIG-09, SIG-10 | 0 of 2 | free, verifiable, small, and honest about being small |
| pricing and prop structure | SIG-11, SIG-12, SIG-13, SIG-14 | 2 of 4 | where parlay and prop-combo mispricings live; needs our own scoring process first |
| origination | SIG-15, SIG-16 | 1 of 2 | the actual objective; SIG-16 is a diagnostic on SIG-15, not a separate edge |
| governance | SIG-17, SIG-18 | 0 of 2 | not predictions at all — controls that decide whether a prediction is worth acting on |

## Design rules applied to every row

1. **Direction is stated as a hypothesis with a sign, never a magnitude.** Saying "a depleted nickel package should raise opponent slot targets" is a claim we can test cheaply. Saying "+1.4 yards per route run" before we have fitted one is a fabrication with a decimal point.
2. **Decay is measured against the publication cycle**, not the calendar: an availability surprise is worth hours, a depth deficiency is worth weeks. This is what makes the three filings per week worth engineering for.
3. **Capacity is stated because a signal nobody can bet is not an edge.** The quarterback-chain signal is high-conviction and appears four times a week at best; the totals-surprise signal appears constantly but in a market that reprices in seconds.
4. **Blocking gate is mandatory.** A signal with no named gate is a wish, and every row here has one.
