boot('questions', async (el) => {
  const Q = [
    { g: 'A · Model and market', rows: [
      ['A1', 'Is our line better than the closing line?', 'answered',
       'No. Spread MAE 10.25 vs 9.94; total 10.87 vs 10.50 across 3,404 games.',
       'calibration.json', 'https://github.com/leesharpe/nfldata/blob/master/DATASETS.md'],
      ['A2', 'Is our line at least unbiased?', 'answered',
       'Yes. Spread bias −0.19 pts, total bias −0.02 pts. A 1-pt silent bias would erase every edge we hunt for, so this is a permanent gate.',
       'calibration.json', 'https://github.com/leesharpe/nfldata/blob/master/DATASETS.md'],
      ['A3', 'Are our probabilities calibrated?', 'answered',
       'Mostly. Worst bucket is 0.80–1.00 (predicted 83.7%, observed 91.9%, n=136); the 0.35–0.50 bucket is off by −4.5 pts (n=894).',
       'calibration.json', ''],
      ['A4', 'Would a second model family help?', 'answered',
       'Not this one. A net-points-differential model correlates 0.976 with the ridge ratings and improves MAE by only 0.01 at a 3:1 blend.',
       'luck.json', ''],
      ['A5', 'Does the market already price injuries?', 'open',
       'Cannot be measured. Only closing lines exist for most seasons, so there is no pre/post price to compare. Needs opening-line history.',
       '', ''],
      ['A6', 'Do backup QBs move the line measurably?', 'open',
       'We detect the switch (12.5% of games) but fading it loses 8.2% on the holdout. Separating "already priced" from "no effect" needs opening lines.',
       'strategies.json', ''],
    ]},
    { g: 'B · Injuries and depth', rows: [
      ['B1', 'Which positions are hurt most?', 'answered',
       'By report volume: LB 14.3%, WR 13.9%, CB 13.9%. By Out rate only TE is distinguishably above the 45.3% pooled rate (52.8%, CI 47.6–57.9%).',
       'availability.json', 'https://www.nfl.com/injuries/'],
      ['B2', 'How often is a depth-1 starter ruled out?', 'answered',
       '2024 only: team vacancy rates run 1.9%–10.9% of starter slots (SF 10.85%, CLE 10.46% highest).',
       'availability.json', 'https://github.com/nflverse/nflverse-data/releases/tag/depth_charts'],
      ['B3', 'How often is a team down to a 3rd-stringer?', 'answered',
       '45 position-weeks in 2024 where a starter was Out AND no depth-2 body was available. That is the operational definition and it is a floor.',
       'availability.json', 'https://github.com/nflverse/nflverse-data/releases/tag/depth_charts'],
      ['B4', 'Can snap counts confirm who actually played?', 'open',
       'Not from this environment — the release assets are above the API size limit. Needs a mirror under 1 MB or direct asset access.',
       '', 'https://github.com/nflverse/nflverse-data/releases/tag/snap_counts'],
      ['B5', 'Can depth-chart coverage extend past 2024?', 'open',
       'Needs the 2025–2026 depth_charts release, currently unreachable.', '', ''],
      ['B6', 'Does a starter being out move the line?', 'open',
       'Gated on A5. Without a pre/post price any claim would be a story, not a measurement.', '', ''],
    ]},
    { g: 'C · Strategies and validation', rows: [
      ['C1', 'Did any strategy pass?', 'answered',
       'No — 0 of 22. Closest is S22 (wind 10–15 mph under): +10.4% holdout ROI on 180 legs, failing sample, multiplicity and skill gates.',
       'strategies.json', ''],
      ['C2', 'Are the gates too strict?', 'answered',
       'Not for real money. Bonferroni at 60 tests needs p<0.00083; 180 legs cannot realistically clear that. The gates are calibrated for capital allocation and labelled as such.',
       'strategies.json', ''],
      ['C3', 'How many legs to certify a 55% hit rate?', 'answered',
       'Between 1,200 and 1,600 legs. At 1,200 the Wilson lower bound is 0.5217 (below the 0.5238 break-even); at 1,600 it is 0.5255 (clears). Budget ~1,600 per candidate.',
       '', ''],
      ['C4', 'Are we burning the holdout by looking at it?', 'open',
       'Yes — every look costs a little. Mitigation: declare 2026 wk10–18 plus 2027 the new holdout and re-label 2021–2025 as development. Decision required, it is free today.',
       '', ''],
      ['C5', 'What is the correct reward currency?', 'open',
       'Points are defined; cash raises compliance questions. See the compliance note in the executive summary.',
       '', 'https://www.nfl.com/news/nfl-reminds-players-of-league-gambling-policy-in-light-of-federal-indictments'],
    ]},
    { g: 'D · Parlays and props', rows: [
      ['D1', 'Are spread and total legs independent?', 'answered',
       'Yes — φ = +0.019 across 3,289 games. Combining them genuinely diversifies.',
       'correlation.json', ''],
      ['D2', 'What does a same-game parlay cost?', 'answered',
       'At −110/leg the hold is 8.9% on 2 legs, 13.0% on 3, 17.0% on 4, compounding upward. Exact table on the Parlays page.',
       'props.json', ''],
      ['D3', 'Which prop pairs are correlated?', 'open',
       'Structural signs are known, magnitudes are not. Published as UNVERIFIED rather than estimated — needs prop-line history.',
       'props.json', ''],
      ['D4', 'Do team scores correlate within a game?', 'answered',
       'Barely — r = −0.030 across 3,404 games. Opposing team-total overs are closer to independent than the shared-pace story implies.',
       'props.json', ''],
      ['D5', 'Any legal or ToS constraint on automation?', 'open',
       'Most books prohibit bot-placed wagers; the NFL bars its personnel from betting on NFL games and treats prediction-market sports contracts as betting. Needs a written position.',
       '', 'https://www.nfl.com/news/nfl-reminds-players-of-league-gambling-policy-in-light-of-federal-indictments'],
    ]},
    { g: 'E · Operations', rows: [
      ['E1', 'Is the pipeline reproducible?', 'answered',
       'Yes — python3 -m pipeline.build, pinned upstream commit, SHA-256 per file in provenance.json.',
       'provenance.json', 'https://github.com/kanlerxz87-cyber/NFL2'],
      ['E2', 'How stale can the site be before it misleads?', 'answered',
       'Lines and injuries are volatile. Every page stamps generated_utc; anything over a week old is historical.',
       'index.json', ''],
      ['E3', 'What breaks if the upstream mirror moves?', 'answered',
       'The build fails loudly on hash mismatch rather than silently producing numbers from a different dataset.',
       '', ''],
      ['E4', 'Is a redistribution licence in place?', 'open',
       'nfldata publishes no LICENSE file; data originates with Pro Football Reference and nflverse. Attribution given; formal licence review needed before commercial use.',
       '', 'https://github.com/leesharpe/nfldata'],
    ]},
  ];
  const all = Q.flatMap(g => g.rows);
  const open = all.filter(r => r[2] === 'open').length;

  el.innerHTML = `
  <section class="hero"><h1>Open questions</h1>
    <p class="lede">Everything that must be answered before a decision, split into what we already know
    and what we are missing. Nothing on this page is a guess: an open question names the exact data
    that would close it.</p></section>

  <div class="grid g4">
    ${app.statCard('Questions tracked', all.length, 'across five domains')}
    ${app.statCard('Answered here', all.length - open, 'with evidence attached', 'good')}
    ${app.statCard('Still open', open, 'each names the missing data', 'warn')}
    ${app.statCard('Blocking a decision', '4', 'see the decision path')}
  </div>

  <div class="note">
    <strong>How to use this page.</strong> An <span class="pill open">open</span> row is not a gap in
    the work — it is a finding. It tells you that any conclusion drawn without that data would be
    unsupported, and it names the cheapest way to fix it.
  </div>

  ${Q.map(g => `
    <h2>${app.esc(g.g)}</h2>
    ${app.table([
      { label: '#', mono: true, render: r => app.esc(r[0]) },
      { label: 'Question', render: r => `<strong>${app.esc(r[1])}</strong>` },
      { label: 'Status', render: r => app.pill(r[2]) },
      { label: 'Answer / what is missing', render: r => app.esc(r[3]) },
      { label: 'Evidence', render: r => r[4]
          ? `<a class="src" href="data/${app.esc(r[4])}" target="_blank" rel="noopener">${app.esc(r[4])}</a>`
          : app.blank },
      { label: 'Source', render: r => r[5] ? app.srcLink(r[5]) : app.blank },
    ], g.rows)}`).join('')}

  <h2>Discovery backlog — cheapest ways to close the open items</h2>
  <p class="small muted">Ordered by how much each unlocks, not by how easy it looks.</p>
  ${app.table([
    { label: 'Priority', num: true, render: r => r[0] },
    { label: 'Action', render: r => r[1] },
    { label: 'Closes', render: r => r[2].map(x => `<span class="pill neutral">${app.esc(x)}</span>`).join(' ') },
    { label: 'Why it matters', render: r => app.esc(r[3]) },
  ], [
    [1, 'Acquire opening-line history (2015–2026, one book is enough)', ['A5', 'A6', 'B6'],
     'Turns the injury research from descriptive into measurable. Four open questions close at once.'],
    [2, 'Acquire three seasons of prop-line history', ['D3'],
     'The only way to publish a real prop-to-prop correlation instead of a structural guess.'],
    [3, 'Acquire snap counts', ['B4'],
     'Turns "listed Out" into "actually did not play", which is the version that matters.'],
    [4, 'Extend depth charts to 2025–2026', ['B5', 'B2', 'B3'],
     'Makes the vacancy index current rather than a 2024 archive.'],
    [5, 'Ingest play-by-play / EPA', ['A4'],
     'The only realistic route to closing the 0.31-pt market gap, because it is a genuinely different input.'],
    [6, 'Reserve a fresh holdout (free)', ['C4'],
     'Protects the only clean evidence we have. Costs nothing today and cannot be done retroactively.'],
  ])}
  `;
});
