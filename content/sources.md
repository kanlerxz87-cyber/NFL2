# Source Registry
> Every source this project is built on, with its tier, the moment it was fetched and precisely what it was used for.

Tier A is the league's own domain. Tier B is research literature. Tier C is our own repository and arithmetic. Tier D is third-party reporting that we looked at and deliberately did **not** use as a system of record — those rows exist so that the decision to exclude them is auditable rather than invisible.

{{csv data/sources.csv;;cols=id:ID,name:Source,org:Publisher,url:URL:urls,kind:Type,tier:Tier,accessed_utc:Fetched,used_for:Used for,verified:Verification state;;source=S-REPO;;show_source=0;;caption=Fetch times are UTC on 12 November 2026. "Used for" is the only place a source's role is stated, so an unused field cannot quietly become a fact.}}

## Deliberate exclusions

| Considered | Why it is not in the system of record | Where it does appear |
| --- | --- | --- |
| Operator injury tables (e.g. DraftKings Network) | accurate-looking, but they publish statuses earlier than the league's own file; using them would import un-declared information into a "verified" table | [FL-02](flagged-for-review.html), exhibit row in the registry above |
| Wire-service and beat-reporter posts | not the league; also, availability claims that later changed within the same week (Puka Nacua is the worked example) | [FL-04](flagged-for-review.html) |
| Third-party roster-rule explainers (IR minimums, return designations, 21-day window) | the mechanics matter to our gates, but only the league's text can be cited as the rule | [FL-05](flagged-for-review.html), [Q-08](questions.html) |
| Any odds screen, sportsbook API or aggregator | none reachable from this environment, and none official — so the site carries no prices at all | [FL-10](flagged-for-review.html) |
| Community stat mirrors | not the source of record for a scoring or standings claim when the league page itself was fetchable | not used |
