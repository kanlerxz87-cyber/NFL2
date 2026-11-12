boot('leaderboard', async (el) => {
  const d = await app.load('strategies.json');
  const S = d.strategies || [];
  const R = d.reward_rules || {};
  const ranked = [...S].sort((a, b) => (b.holdout?.roi ?? -9) - (a.holdout?.roi ?? -9))
    .map((s, i) => ({ rank: i + 1, ...s }));
  const tier = (s) => {
    if (s.verdict === 'CERTIFIED') return 'Tier 1';
    const fails = s.failed_gates || [];
    const onlyLate = fails.every(f => ['G4_stability', 'G5_multiplicity', 'G6_skill'].includes(f));
    return onlyLate && fails.length ? 'Tier 2' : 'Tier 3';
  };

  el.innerHTML = `
  <section class="hero"><h1>Leaderboard</h1>
    <p class="lede">A competition, scored on the locked holdout only. Rewards are denominated in
    <strong>points and paper allocation</strong>, and a tier-2 or tier-3 result cannot be funded no
    matter how good its ROI looks.</p></section>

  <div class="note bad">
    <strong>${d.summary.certified} of ${d.summary.total} strategies are certified.</strong>
    Every one of them fails at least one gate on the holdout. That is the result, and publishing it
    is the point of the exercise. A leaderboard that always produces a winner is a leaderboard that
    is not testing anything.
  </div>

  <div class="grid g4">
    ${app.statCard('Strategies tested', d.summary.total, 'each fully specified in advance')}
    ${app.statCard('Certified', d.summary.certified, 'all seven gates', 'bad')}
    ${app.statCard('Development window', `${d.windows.development[0]}–${d.windows.development[1]}`, 'parameters discovered here')}
    ${app.statCard('Holdout window', `${d.windows.holdout[0]}–${d.windows.holdout[1]}`, 'scored once', 'warn')}
  </div>

  <h2>Standings</h2>
  ${app.table([
    { label: '#', num: true, key: 'rank' },
    { label: 'Strategy', render: r => `${app.esc(r.name)}<div class="src">${app.esc(r.id)} · ${app.esc(r.family)}</div>` },
    { label: 'Market', render: r => app.esc(r.market) },
    { label: 'Holdout legs', num: true, render: r => app.vblank(r.holdout?.legs) },
    { label: 'Hit', num: true, render: r => app.pct(r.holdout?.hit_rate, 1) },
    { label: 'Break-even', num: true, render: r => app.pct(r.holdout?.break_even, 1) },
    { label: 'ROI', num: true, render: r => app.sgn((r.holdout?.roi ?? 0) * 100, 2) + '<span class="dim small">%</span>' },
    { label: 'Units', num: true, render: r => app.sgn(r.holdout?.profit_units, 1) },
    { label: 'p-value', num: true, render: r => app.isNum(r.holdout?.p_value) ? r.holdout.p_value.toExponential(1) : app.blank },
    { label: 'Tier', render: r => `<span class="pill ${tier(r) === 'Tier 1' ? 'certified' : tier(r) === 'Tier 2' ? 'warn' : 'rejected'}">${tier(r)}</span>` },
    { label: 'Verdict', render: r => app.pill(r.verdict) },
  ], ranked)}

  <h2>Reward rules</h2>
  <div class="grid g2">
    <div class="card">
      <div class="k">Points formula</div>
      <p class="mono small" style="margin:.4rem 0">${app.esc(R.points_formula)}</p>
      <div class="k" style="margin-top:.8rem">Stability factor</div>
      <p class="small" style="margin:.4rem 0">${app.esc(R.stability_factor)}</p>
      <div class="k" style="margin-top:.8rem">Drawdown penalty</div>
      <p class="small" style="margin:.4rem 0">${app.esc(R.drawdown_penalty)}</p>
    </div>
    <div class="card">
      <div class="k">Why the formula looks like this</div>
      <p class="small muted">Multiplying by √legs punishes tiny samples; multiplying by the stability
      factor punishes a single good season; the drawdown penalty punishes a strategy that wins small
      and loses big. A flashy ROI on 40 legs scores near zero by construction — which is the behaviour
      we want.</p>
    </div>
  </div>

  <h2>Payout tiers</h2>
  ${app.table([
    { label: 'Tier', render: r => app.esc(r.tier) },
    { label: 'Reward', render: r => app.esc(r.reward) },
    { label: 'Requirement', render: r => app.esc(r.requires) },
  ], R.payout_tiers || [])}

  <div class="note warn">
    <strong>${app.esc(R.note || '')}</strong>
  </div>

  <div class="note">
    <strong>Compliance constraint on rewards.</strong> The NFL Gambling Policy for Players prohibits
    personnel from betting on NFL games, and the league has stated that prediction-market sports
    contracts count as betting. Any real payout design must sit with legal review first. This is why
    the reward currency above is points and paper allocation.
    ${app.srcLink('https://www.nfl.com/news/nfl-reminds-players-of-league-gambling-policy-in-light-of-federal-indictments', 'nfl.com')}
  </div>

  <h2>Gate definitions</h2>
  ${app.table([
    { label: 'Gate', mono: true, key: 'g' },
    { label: 'Requirement', key: 'v' },
  ], Object.entries(d.gate_definitions || {}).map(([g, v]) => ({ g, v })))}
  `;
});
