boot('ratings', async (el) => {
  const d = await app.load('lines.json');
  const R = d.ratings || {};
  const T = R.teams || [];

  el.innerHTML = `
  <section class="hero"><h1>Team ratings</h1>
    <p class="lede">Offence and defence in points, fitted only on games played before the target week.
    Positive offence is points scored above league average; positive "allowed" is a leaky defence.</p></section>

  <div class="note">
    <strong>${app.esc(R.method || '')}</strong> — fitted through ${app.esc(R.through || '')} using
    ${app.vblank(R.games_used)} games from seasons ${(R.window_seasons || []).join('–')}.
    League average ${app.num(R.league_average_points, 2)} points; home-field ${app.num(R.home_field_points, 2)} points.
  </div>

  <div class="grid g4">
    ${app.statCard('League average', app.num(R.league_average_points, 2), 'points per team')}
    ${app.statCard('Home-field advantage', app.num(R.home_field_points, 2), 'points')}
    ${app.statCard('Games in window', R.games_used, 'time-decayed')}
    ${app.statCard('Residual σ', app.num(R.sigma_residual, 2), 'points')}
  </div>

  <h2>Net rating</h2>
  <p class="small muted">Net = offence − points allowed above average. This is the number that drives
  the spread; the two components drive the total.</p>
  ${app.table([
    { label: 'Team', mono: true, key: 'team' },
    { label: 'Offence', num: true, render: r => app.sgn(r.offense, 2) },
    { label: 'Defence (allowed)', num: true, render: r => app.sgn(r.defense_allowed, 2) },
    { label: 'Net', num: true, render: r => `<strong>${app.sgn(r.net, 2)}</strong>` },
    { label: 'Games in window', num: true, key: 'games_in_window' },
    { label: 'Read', render: r => r.net > 3 ? '<span class="pill good">contender</span>'
        : r.net < -3 ? '<span class="pill bad">struggling</span>' : '<span class="pill neutral">average</span>' },
    { label: 'Source', render: () => app.srcLink('https://github.com/leesharpe/nfldata/blob/master/DATASETS.md', 'nfldata') },
  ], T)}

  <h2>How to use these numbers</h2>
  <div class="grid g2">
    <div class="card"><h3>Reading the defence column</h3>
      <p class="small muted">A negative "defence allowed" is <em>good</em>: the team concedes fewer
      points than average. This trips people up, so it is labelled rather than hidden.</p></div>
    <div class="card"><h3>What a rating is not</h3>
      <p class="small muted">It is not a forecast of a single game. The residual σ is
      ${app.num(R.sigma_residual, 2)} points, which is larger than almost every rating gap on this
      table — that is why single-game outcomes are so hard to predict.</p></div>
  </div>
  `;
});
