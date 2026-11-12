boot('injuries', async (el) => {
  const d = await app.load('availability.json');
  const por = d.position_out_rates || {};
  const vac = d.depth_vacancies || {};
  const il = d.injury_load || {};
  const bdi = d.backup_deficiency || {};

  const load24 = (il.teams || []).filter(t => t.season === 2024)
    .sort((a, b) => b.weighted_load - a.weighted_load);
  const load25 = (il.teams || []).filter(t => t.season === 2025)
    .sort((a, b) => b.weighted_load - a.weighted_load);

  el.innerHTML = `
  <section class="hero"><h1>Injuries &amp; depth</h1>
    <p class="lede">Who is hurt, how much it costs, and — the part most sites skip — how often a team
    is down to a second or third-string player because a starter is ruled out.</p></section>

  <div class="note">
    <strong>Sources.</strong> Weekly injury reports come from the nflverse
    <code>injuries</code> release, which mirrors the NFL's official injury report fields
    (Out / Doubtful / Questionable, plus practice participation). Cross-checked against
    ${app.srcLink('https://www.nfl.com/injuries/', 'nfl.com/injuries')}. Depth charts come from the
    nflverse <code>depth_charts</code> release.
  </div>

  <h2>Injury burden by position</h2>
  <p class="small muted">"Out rate" is the share of injury-report entries where the game status was
  Out. Wilson 95% intervals are shown because most positions cannot be statistically separated from
  each other at this sample size — and the site says so rather than ranking noise.</p>
  ${app.table([
    { label: 'Position', mono: true, key: 'position' },
    { label: 'Report entries', num: true, key: 'reports' },
    { label: 'Out', num: true, key: 'outs' },
    { label: 'Out rate', num: true, render: r => app.pct(r.out_rate, 1) },
    { label: '95% CI', num: true, render: r => `<span class="mono small">${app.pct(r.ci_low, 1)} – ${app.pct(r.ci_high, 1)}</span>` },
    { label: 'Distinguishably above pooled?', render: r => r.distinguishably_above_pooled
        ? '<span class="pill warn">yes</span>' : '<span class="pill neutral">no</span>' },
    { label: 'Source', render: () => app.srcLink('https://github.com/nflverse/nflverse-data/releases/tag/injuries', 'nflverse') },
  ], por.table || [])}
  <p class="small muted">Pooled Out rate across all positions: <strong>${app.pct(por.pooled_out_rate, 1)}</strong>
  (${(por.seasons || []).join(', ')}). Only rows marked "yes" are demonstrably different.</p>

  <h2>Depth-chart vacancies — starters ruled out</h2>
  <div class="note warn">
    <strong>Coverage: ${vac.season} only.</strong> ${app.esc(vac.method || '')} A full depth chart for
    other seasons is not reachable from this environment, so the index is not extended — it is left
    blank rather than estimated.
  </div>
  ${app.table([
    { label: 'Team', mono: true, key: 'team' },
    { label: 'Starter slots tracked', num: true, key: 'starter_slots' },
    { label: 'Slots ruled out', num: true, key: 'starter_slots_out' },
    { label: 'Vacancy rate', num: true, render: r => {
      const v = r.vacancy_rate;
      const c = v > 0.08 ? 'bad' : v > 0.06 ? 'warn' : 'muted';
      return `<span class="${c}">${app.pct(v, 2)}</span>`;
    }},
    { label: 'Thin position-weeks', num: true, render: r => r.thin_position_weeks,
      title: 'starter Out AND no depth-2 body available' },
    { label: 'Weeks', num: true, key: 'weeks' },
    { label: 'Source', render: () => app.srcLink('https://github.com/nflverse/nflverse-data/releases/tag/depth_charts', 'depth charts') },
  ], vac.teams || [])}

  <h2>What "thin" means, precisely</h2>
  <div class="note">
    <p class="small">A position-week is counted as <strong>thin</strong> when (a) at least one
    depth-1 player at that position group is listed Out on the injury report, and (b) no depth-2
    player at that position group is available. That is the concrete case where a team is down to a
    third-string body.</p>
    <p class="small">Total thin position-weeks across the 2024 season:
    <strong>${(vac.weekly || []).reduce((a, x) => a + (x.thin || 0), 0)}</strong>. This is a floor, not
    a ceiling: a player can be active but limited, and that does not show up in this definition.</p>
  </div>

  <h2>Weekly detail — where starters were out</h2>
  <details><summary>Show ${(vac.weekly || []).length} team-position-weeks with at least one starter out</summary>
    ${app.table([
      { label: 'Team', mono: true, key: 'team' },
      { label: 'Week', num: true, key: 'week' },
      { label: 'Group', mono: true, key: 'pos_group' },
      { label: 'Starters', num: true, key: 'starters' },
      { label: 'Out', num: true, key: 'starters_out' },
      { label: 'Backups available', num: true, key: 'backups_available' },
      { label: 'Ratio', num: true, render: r => app.pct(r.vacancy_ratio, 0) },
      { label: 'Thin?', render: r => r.thin ? '<span class="pill bad">thin</span>' : '<span class="pill neutral">covered</span>' },
    ], vac.weekly || [])}
  </details>

  <h2>Team injury load (weighted)</h2>
  <p class="small muted">Weights: Out 1.0, Doubtful 0.75, Questionable 0.30 — stated so the ranking can
  be audited and argued with.</p>
  <div class="grid g2">
    <div class="card tight"><div class="k">2024 heaviest</div>
      ${app.table([
        { label: 'Team', mono: true, key: 'team' },
        { label: 'Out', num: true, key: 'out' },
        { label: 'Load', num: true, render: r => app.num(r.weighted_load, 1) },
      ], load24.slice(0, 8))}
    </div>
    <div class="card tight"><div class="k">2025 heaviest</div>
      ${app.table([
        { label: 'Team', mono: true, key: 'team' },
        { label: 'Out', num: true, key: 'out' },
        { label: 'Load', num: true, render: r => app.num(r.weighted_load, 1) },
      ], load25.slice(0, 8))}
    </div>
  </div>

  <h2>Offence vs defence — backup deficiency</h2>
  <div class="note warn">
    <strong>Verified seasons: ${(bdi.verified_seasons || []).join('–')}.</strong>
    ${app.esc(bdi.why_unverified || '')}
  </div>
  <p class="small muted">${app.esc(bdi.definition || '')}</p>
  <details><summary>Show the ${(bdi.teams || []).length} verified team-seasons</summary>
    ${app.table([
      { label: 'Season', num: true, key: 'season' },
      { label: 'Team', mono: true, key: 'team' },
      { label: 'Starts', num: true, render: r => app.num(r.starts, 0) },
      { label: 'By inexperienced players', num: true, render: r => app.num(r.starts_inexperienced, 0) },
      { label: 'Share', num: true, render: r => app.pct(r.inexperience_share, 1) },
      { label: 'Source', render: () => app.srcLink('https://github.com/leesharpe/nfldata/blob/master/DATASETS.md#rosters', 'nfldata') },
    ], bdi.teams || [])}
  </details>
  <div class="note bad small">
    Post-2018 rows are deliberately absent. An estimate would be indistinguishable from a made-up
    number once it reached a table, so the cells are blank and the reason is printed instead.
  </div>
  `;
});
