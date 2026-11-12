boot('parlays', async (el) => {
  const d = await app.load('props.json');
  const cor = await app.load('correlation.json');
  const P = d.prop_correlation || {};
  const vig = d.parlay_vig || [];
  const slate = d.slate || {};
  const pairs = cor.outcomes?.pairs || [];

  el.innerHTML = `
  <section class="hero"><h1>Parlays &amp; player props</h1>
    <p class="lede">What a same-game parlay actually costs, which legs genuinely diversify, and — stated
    plainly — the prop data we do not have.</p></section>

  <h2>What the book keeps</h2>
  <p class="small muted">Exact arithmetic at −110 per leg: the book's implied probability minus a fair
  50/50 price. This is not an estimate.</p>
  ${app.table([
    { label: 'Legs', num: true, key: 'legs' },
    { label: 'Book decimal odds', num: true, render: r => app.num(r.book_decimal_odds, 3) },
    { label: 'Book American', num: true, render: r => app.vblank(r.book_american) },
    { label: 'Book implied prob', num: true, render: r => app.pct(r.book_implied_prob, 3) },
    { label: 'Fair implied prob', num: true, render: r => app.pct(r.fair_implied_prob_50_50, 3) },
    { label: 'Hold', num: true, render: r => {
      const c = r.hold_pct > 15 ? 'bad' : r.hold_pct > 10 ? 'warn' : 'muted';
      return `<span class="${c}">${r.hold_pct.toFixed(2)}%</span>`;
    }},
    { label: 'Fair American', num: true, render: r => app.vblank(r.fair_american) },
  ], vig)}
  <div class="note warn">Every extra leg compounds the hold. That is the structural reason a long
  parlay is a worse bet than the sum of its parts even when each part is break-even.</div>

  <h2>Verified correlated pricing</h2>
  <p class="small muted">From the measured correlations on the Correlations page.</p>
  ${app.table([
    { label: 'Combination', render: r => `${app.esc(r.leg_a)} + ${app.esc(r.leg_b)}` },
    { label: 'φ', num: true, render: r => app.num(r.phi, 4) },
    { label: 'Fair price', num: true, render: r => app.vblank(r.parlay?.fair_american_if_observed) },
    { label: 'Book price', num: true, render: r => app.vblank(r.parlay?.independent_american) },
    { label: 'Error', num: true, render: r => app.sgn(r.parlay?.price_error_pct, 1) + '<span class="dim small">%</span>' },
    { label: 'Action', render: r => Math.abs(r.phi) < 0.15
        ? '<span class="pill pass">acceptable</span>'
        : r.phi > 0 ? '<span class="pill warn">avoid — book understates</span>'
                    : '<span class="pill bad">avoid — book overstates</span>' },
  ], pairs)}

  <h2>Player props — the honest position</h2>
  <div class="note bad">
    <strong>${app.esc(P.status || 'UNVERIFIED')}.</strong> ${app.esc(P.why || '')}
  </div>
  <details open><summary>What would make prop correlation measurable</summary>
    <ul class="small muted">${(P.what_would_fix_it || []).map(x => `<li>${app.esc(x)}</li>`).join('')}</ul>
  </details>

  <h2>Structural relationships — direction only, no magnitudes</h2>
  <p class="small muted">These signs are logical consequences of how football scoring works, not
  measurements. They are published so a parlay builder can avoid the worst combinations while the
  data gap exists.</p>
  ${app.table([
    { label: 'Leg A', render: r => app.esc(r.leg_a) },
    { label: 'Leg B', render: r => app.esc(r.leg_b) },
    { label: 'Direction', render: r => `<span class="pill ${r.sign === '+' ? 'warn' : 'neutral'}">${app.esc(r.sign)}</span>` },
    { label: 'Why', render: r => app.esc(r.reason) },
    { label: 'Verified?', render: () => '<span class="pill unverified">structural</span>' },
  ], P.structural_relationships_only || [])}

  <h2>Team-score correlation (measured)</h2>
  <p class="small">Across ${app.vblank(d.team_score_correlation?.n_games)} games the correlation between
  the home and away scores is <strong>${app.num(d.team_score_correlation?.corr_home_score_away_score, 4)}</strong>.</p>
  <div class="note">${app.esc(d.team_score_correlation?.interpretation || '')}</div>

  <h2>Week 9 2026 priced slate</h2>
  ${slate.available ? `
    <p class="small muted">${app.esc(slate.source)}</p>
    <div class="grid g4">
      ${app.statCard('Players priced', slate.rows, 'main slate')}
      ${app.statCard('Games', (slate.games || []).length, '11-game slate')}
      ${app.statCard('Flagged by book', Object.entries(slate.status_counts || {}).filter(([k]) => k !== 'active').reduce((a, [, v]) => a + v, 0), 'IR / OUT / Q / D')}
      ${app.statCard('Source verified', 'yes', 'book export, mirrored in repo', 'good')}
    </div>
    ${app.table([
      { label: 'Game', mono: true, key: 'game' },
      { label: 'Players', num: true, key: 'players' },
      { label: 'QB', num: true, key: 'qb' },
      { label: 'RB', num: true, key: 'rb' },
      { label: 'WR', num: true, key: 'wr' },
      { label: 'TE', num: true, key: 'te' },
    ], slate.games || [])}
    <div class="note warn small">${app.esc(slate.note_on_status || '')}</div>
  ` : '<p class="muted">Slate data not available in this build.</p>'}

  <h2>Recommendation</h2>
  <div class="note">${app.esc(d.recommendation || '')}</div>
  `;
});
