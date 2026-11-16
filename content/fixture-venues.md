# Week 11 venues, read from the official game centres
> Thirteen fixtures, 19 to 23 November 2026. Each venue is the stadium and location printed in the Game Info block of that game's own nfl.com game centre, read on 16 November 2026 between 18:02 and 18:06 UTC. Nothing is inferred. A game whose page printed no stadium would be left blank.

{{csv data/venues_wk11_3e77121b.csv;;cols=game_id:Game,date:Date,kickoff_et:Kickoff (ET),away:Away,home:Home,location_as_printed:Location (as printed),stadium_as_printed:Stadium (as printed),network_as_printed:Broadcaster,fl112_cross_check:Cross-check against FL-112,source:Official game centre:urls;;source_col=source;;show_source=0;;caption=Source for every row is that game's own nfl.com game centre. The FL-112 column compares this reading with the venue names session f3ec0ff8 transcribed from the schedule page's hotel-link parameters. Where they disagree the game centre is shown and the difference is flagged (FL-115), not resolved.}}

## What this page settles, and what it does not

**Nine of thirteen venues agree** with the names transcribed in FL-112. For these games the game centre and the parameter values give the same stadium.

**Three disagree.** W11-01 Indianapolis at Houston is printed as **Reliant Stadium** on its game centre; the parameter reads "NRG Stadium". W11-07 Arizona at Kansas City is printed as **Arrowhead Stadium**; the parameter reads "GEHA Field at Arrowhead Stadium". W11-13 Cincinnati at Washington is printed as **Northwest Stadium**; the parameter reads "FedEx Field". The game centre prints the stadium in its own Game Info block for that game, so it is the reading shown here. The parameter is a hotel-link value and is not a stadium field. Which reading the public schedule should carry is a decision for the owner, logged as FL-115.

**W11-12 Minnesota at San Francisco** is played in **Mexico City**, at Estadio Banorte. It is a neutral-site game, and the game centre prints it that way. FL-112 does not list it.

**Not changed here.** The `site` column of `data/schedule_week11_2026.csv` is left as "not published" on purpose. That column belongs to the schedule work, and FL-112 leaves its publication to the owner.

**Not a model input.** A venue is recorded as a fact about a game. It is not a feature yet. Venue effects are signal SIG-10, which is not built.
