boot('data', async (el) => {
  const a = await app.load('audit.json');
  const prov = await app.load('provenance.json');
  const F = a.findings || [];
  const files = prov.files || [];
  const s = a.summary || {};

  el.innerHTML = `
  <section class="hero"><h1>Data &amp; audit</h1>
    <p class="lede">Every source file, its hash, and every integrity check that ran against it.
    If a check failed, it is here.</p></section>

  <div class="grid g4">
    ${app.statCard('Checks run', s.checks, 'schema, identity, range, coverage')}
    ${app.statCard('Passed', s.pass, 'no action needed', 'good')}
    ${app.statCard('Warnings', s.warn, 'known limitation', 'warn')}
    ${app.statCard('Flagged', s.flag + s.fail, 'published for review', (s.flag + s.fail) > 0 ? 'warn' : 'good')}
  </div>

  <h2>Snapshot</h2>
  ${app.table([
    { label: 'Property', key: 'k' }, { label: 'Value', mono: true, render: r => app.esc(r.v) },
    { label: 'Source', render: r => app.srcLink(
        'https://github.com/leesharpe/nfldata/blob/master/DATASETS.md', 'nfldata') },
  ], [
    { k: 'Upstream repository', v: prov.upstream?.repo },
    { k: 'Upstream commit', v: prov.upstream?.commit },
    { k: 'Commit timestamp', v: prov.upstream?.commit_date },
    { k: 'Games in file', v: a.coverage?.games },
    { k: 'Completed games', v: a.coverage?.played_games },
    { k: 'Seasons covered', v: (a.coverage?.seasons || []).join(' – ') },
    { k: 'Regular-season games before 2026', v: a.coverage?.regular_season_games_before_2026 },
    { k: 'Last completed game', v: a.coverage?.last_completed_game_utc },
    { k: 'Player-seasons', v: a.coverage?.roster_player_seasons },
  ])}

  <h2>Integrity checks</h2>
  ${app.table([
    { label: 'ID', mono: true, key: 'id' },
    { label: 'Check', render: r => app.esc(r.check) },
    { label: 'Status', render: r => app.pill(r.status) },
    { label: 'Detail', render: r => app.esc(r.detail) },
    { label: 'Source', render: r => app.srcLink(r.source, 'source') },
  ], F)}

  <h2>Source files and hashes</h2>
  <p class="small muted">SHA-256 lets anyone confirm the build used exactly these bytes.</p>
  ${app.table([
    { label: 'File', mono: true, key: 'file' },
    { label: 'Rows', num: true, key: 'rows' },
    { label: 'Bytes', num: true, render: r => app.isNum(r.bytes) ? r.bytes.toLocaleString() : app.blank },
    { label: 'SHA-256', mono: true, render: r => `<span class="src">${app.esc((r.sha256 || '').slice(0, 16))}…</span>` },
    { label: 'Verified', render: r => app.pill(r.verified === false ? 'unverified' : 'verified') },
    { label: 'Source', render: r => app.srcLink(
        r.url && r.url.startsWith('http') ? r.url
          : 'https://github.com/leesharpe/nfldata', 'nfldata') },
  ], (a.files || []).map(f => ({ ...f, rows: f.rows })))}

  <h2>Vendored files</h2>
  ${app.table([
    { label: 'File', mono: true, key: 'file' },
    { label: 'Bytes', num: true, render: r => app.isNum(r.bytes) ? r.bytes.toLocaleString() : app.blank },
    { label: 'SHA-256', mono: true, render: r => `<span class="src">${app.esc((r.sha256 || '').slice(0, 16))}…</span>` },
    { label: 'Status', render: r => app.pill(r.verified === false ? 'unverified' : 'verified') },
    { label: 'Source', render: r => app.srcLink(
        r.url && r.url.startsWith('http') ? r.url
          : 'https://github.com/nflverse/nflverse-data/releases', 'nflverse') },
    { label: 'Note', render: r => r.note ? `<span class="small muted">${app.esc(r.note)}</span>` : app.blank },
  ], files)}

  <h2>Known-missing datasets</h2>
  <p class="small muted">Named explicitly so nobody assumes the absence was an oversight.</p>
  ${app.table([
    { label: 'Dataset', render: r => app.esc(r.dataset) },
    { label: 'Status', render: r => app.pill('unverified') },
    { label: 'Why', render: r => app.esc(r.why) },
  ], prov.unavailable || [])}

  <h2>Reproduce this build</h2>
  <div class="note small">
    <code>git clone https://github.com/kanlerxz87-cyber/NFL2 &amp;&amp; cd NFL2</code><br>
    <code>pip install numpy pandas scipy pyarrow</code><br>
    <code>python3 -m pipeline.build</code><br>
    Output lands in <code>site/data/*.json</code>. Every artefact carries
    <code>generated_utc</code> and its source list.
  </div>
  `;
});
