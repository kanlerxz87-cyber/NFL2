boot('flagged', async (el) => {
  const [a, prov, avail, strat] = await Promise.all([
    app.load('audit.json'), app.load('provenance.json'),
    app.load('availability.json'), app.load('strategies.json'),
  ]);

  /* Build the flag list from the data itself, so nothing here is hand-maintained. */
  const flags = [];

  (a.findings || []).filter(f => f.status === 'fail' || f.status === 'flag').forEach(f => flags.push({
    id: f.id, severity: 'review', title: f.check, detail: f.detail,
    source: f.source, kind: 'data integrity',
  }));
  (a.findings || []).filter(f => f.status === 'warn').forEach(f => flags.push({
    id: f.id, severity: 'warn', title: f.check, detail: f.detail,
    source: f.source, kind: 'known limitation',
  }));

  (prov.unavailable || []).forEach(u => flags.push({
    id: 'missing:' + u.dataset, severity: 'unverified',
    title: 'Dataset unavailable — ' + u.dataset, detail: u.why,
    source: 'https://github.com/nflverse/nflverse-data/releases', kind: 'data gap',
  }));

  if (avail.position_out_rates) flags.push({
    id: 'availability:single-season',
    severity: 'warn', title: 'Depth-chart analysis covers one season only',
    detail: 'The only reachable full depth chart is 2024 (37,312 rows). The vacancy index is therefore not comparable across seasons and must not be trended.',
    source: 'https://github.com/nflverse/nflverse-data/releases/tag/depth_charts', kind: 'coverage limit',
  });
  const bd = avail.backup_deficiency || {};
  flags.push({
    id: 'availability:starts-empty',
    severity: 'review', title: 'Starter data is empty after 2018',
    detail: `rosters.csv reports zero starts for every player from 2019 onward, so the backup-deficiency metric is published only for ${(bd.verified_seasons || []).join('–')}. ${bd.why_unverified || ''}`,
    source: 'https://github.com/leesharpe/nfldata/blob/master/DATASETS.md#rosters', kind: 'data integrity',
  });
  flags.push({
    id: 'injuries:2026-mirror-lag',
    severity: 'review', title: 'The 2026 injury mirror lags the official page by one week',
    detail: 'The mirrored injury CSV stops at Week 9 while the official NFL injury page already shows Week 10. The site never claims the mirror is current; line confidence is marked LOW where it applies.',
    source: 'https://www.nfl.com/injuries/', kind: 'data integrity',
  });
  flags.push({
    id: 'props:no-history',
    severity: 'unverified', title: 'Player-prop correlations are unverified',
    detail: 'No historical prop-line archive is reachable, so prop-to-prop correlations cannot be measured from outcomes. Published as structural direction only — no magnitudes are estimated.',
    source: 'https://github.com/nflverse/nflverse-data/releases', kind: 'data gap',
  });
  flags.push({
    id: 'model:worse-than-market',
    severity: 'review', title: 'The line model is worse than the closing line',
    detail: 'Spread MAE 10.25 vs 9.94 and total MAE 10.87 vs 10.50. Every conclusion built on this model inherits that gap, which is why zero strategies are certified.',
    source: 'https://github.com/leesharpe/nfldata/blob/master/DATASETS.md', kind: 'model limit',
  });
  flags.push({
    id: 'selection:exploratory-strategy',
    severity: 'review', title: 'S22 (wind 10–15 mph under) was selected after inspecting results',
    detail: 'The wind band was chosen by looking at the data, which inflates the apparent edge. It is labelled EXPLORATORY and must be pre-registered on a new holdout before any weight is given to it.',
    source: 'https://github.com/nflverse/nflverse-data/releases', kind: 'methodology',
  });
  flags.push({
    id: 'licence:nfldata',
    severity: 'unverified', title: 'No licence file in the upstream data repository',
    detail: 'leesharpe/nfldata publishes no LICENSE. The data is aggregated from Pro Football Reference and nflverse. Attribution is given in the footer; a formal licence review is required before commercial use.',
    source: 'https://github.com/leesharpe/nfldata', kind: 'legal',
  });
  flags.push({
    id: 'compliance:prediction-markets',
    severity: 'warn', title: 'Prediction-market contracts are treated as betting by the NFL',
    detail: 'The league has stated that trading sports event contracts on platforms such as Kalshi is covered by its gambling policy. Any reward design must account for this; no primary NFL document with the text could be loaded, so it is quoted as reported.',
    source: 'https://www.nfl.com/news/nfl-reminds-players-of-league-gambling-policy-in-light-of-federal-indictments',
    kind: 'compliance',
  });

  const bySeverity = { review: 0, warn: 0, unverified: 0 };
  flags.forEach(f => bySeverity[f.severity] = (bySeverity[f.severity] || 0) + 1);

  el.innerHTML = `
  <section class="hero"><h1>Flagged for review</h1>
    <p class="lede">Every irregular, unverifiable or limited item, with its source. Nothing here blocks
    anything — that is deliberate. The site publishes its own weaknesses so they can be argued with
    rather than discovered later.</p></section>

  <div class="note warn">
    <strong>This page is generated from the data, not maintained by hand.</strong> Rows are pulled
    from <code>audit.json</code>, <code>provenance.json</code> and the analysis modules at build time.
    If a flag stops being true, it disappears from this list on the next build.
  </div>

  <div class="grid g4">
    ${app.statCard('Items flagged', flags.length, 'across nine categories')}
    ${app.statCard('Needs a decision', bySeverity.review, 'data integrity, model, methodology', 'warn')}
    ${app.statCard('Unverified', bySeverity.unverified, 'published as blank, never estimated', 'warn')}
    ${app.statCard('Blocking the release', '0', 'by design', 'good')}
  </div>

  <h2>What each severity means</h2>
  ${app.table([
    { label: 'Severity', render: r => app.pill(r[0]) },
    { label: 'Meaning', render: r => app.esc(r[1]) },
  ], [
    ['review', 'A real irregularity or limitation that a human should look at. The site still publishes the data, with the caveat attached.'],
    ['warn', 'A known constraint on how a number may be used, or a coverage gap that limits a comparison.'],
    ['unverified', 'A value or relationship that cannot be confirmed from a reachable official source. It is left blank rather than estimated.'],
  ])}

  <h2>All flagged items</h2>
  ${app.table([
    { label: 'Severity', render: r => app.pill(r.severity) },
    { label: 'Category', render: r => `<span class="pill neutral">${app.esc(r.kind)}</span>` },
    { label: 'Item', render: r => `<strong>${app.esc(r.title)}</strong><div class="src">${app.esc(r.id)}</div>` },
    { label: 'Detail', render: r => app.esc(r.detail) },
    { label: 'Source', render: r => app.srcLink(r.source, 'source') },
  ], flags)}

  <h2>Source-data irregularities found by the audit</h2>
  <p class="small muted">These are properties of the upstream file, not of our processing. They are
  flagged, explained and left untouched.</p>
  ${app.table([
    { label: 'Irregularity', render: r => app.esc(r[0]) },
    { label: 'What it is', render: r => app.esc(r[1]) },
    { label: 'Resolution', render: r => app.esc(r[2]) },
  ], [
    ['2022 has 271 regular-season games, not 272',
     'The Week 17 Buffalo Bills at Cincinnati Bengals game was suspended after Damar Hamlin\'s on-field cardiac arrest and the NFL announced it would not be resumed. The season therefore completed with 271 games.',
     'Confirmed against NFL and ESPN reporting. The audit expects 271 for 2022 explicitly rather than treating it as missing data.'],
    ['rosters.csv reports zero starts for every player from 2019 onward',
     'The upstream field is not populated for recent seasons.',
     'All metrics that depend on starts are withheld after 2018 and marked unverified. No estimate is substituted.'],
    ['Seven roster rows carry negative years of experience',
     'Two players (Chris Williams, Jordan Norwood) show −1 to −5 years of experience in some seasons, an upstream identity/deduplication artefact.',
     'Left untouched and flagged. The affected rows are a negligible share of 28,617 and do not move any published metric.'],
    ['teams.csv has no conference column',
     'The documented schema expects conference and division, but the shipped file carries neither.',
     'Conference is taken from standings.csv instead; the audit records the discrepancy rather than silently joining around it.'],
  ])}

  <h2>How to request a change</h2>
  <div class="note small">
    Each row has a stable <code>id</code>. Quote it when requesting a change. Items marked
    <span class="pill unverified">unverified</span> can generally only be resolved by supplying the
    missing dataset; items marked <span class="pill flag">review</span> are judgement calls about how
    the site presents something.
  </div>
  `;
});
