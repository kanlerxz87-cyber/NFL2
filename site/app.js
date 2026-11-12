/* NFL2 dashboard — vanilla JS, no build step, no external dependencies.
   Every rendered table row carries a source link. A row without a source
   renders a visible "no source" flag rather than being silently accepted. */
'use strict';

const DATA = './data/';
const NAV = [
  ['index.html', 'Overview', 'home'],
  ['lines.html', 'Our Lines', 'lines'],
  ['ratings.html', 'Team Ratings', 'ratings'],
  ['calibration.html', 'Calibration', 'calibration'],
  ['strategies.html', 'Strategies', 'strategies'],
  ['leaderboard.html', 'Leaderboard', 'leaderboard'],
  ['luck.html', 'Luck vs Skill', 'luck'],
  ['correlation.html', 'Correlations', 'correlation'],
  ['parlays.html', 'Parlays & Props', 'parlays'],
  ['injuries.html', 'Injuries & Depth', 'injuries'],
  ['data.html', 'Data & Audit', 'data'],
  ['questions.html', 'Open Questions', 'questions'],
  ['suggestions.html', 'Suggestions', 'suggestions'],
  ['flagged.html', 'Flagged for Review', 'flagged'],
];

const cache = {};
async function load(name) {
  if (cache[name]) return cache[name];
  const r = await fetch(DATA + name, { cache: 'no-store' });
  if (!r.ok) throw new Error(`${name}: HTTP ${r.status}`);
  const j = await r.json();
  cache[name] = j;
  return j;
}

/* ---------- helpers ---------- */
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const isNum = (v) => typeof v === 'number' && isFinite(v);
const num = (v, d = 2) => (isNum(v) ? v.toFixed(d) : '<span class="dim">—</span>');
const pct = (v, d = 1) => (isNum(v) ? (v * 100).toFixed(d) + '%' : '<span class="dim">—</span>');
const sgn = (v, d = 2) => {
  if (!isNum(v)) return '<span class="dim">—</span>';
  const c = v > 0 ? 'good' : v < 0 ? 'bad' : 'muted';
  return `<span class="${c}">${v > 0 ? '+' : ''}${v.toFixed(d)}</span>`;
};
const blank = '<span class="dim" title="not confirmable from a verified source">—</span>';
const vblank = (v) => (v === null || v === undefined || v === '' ? blank : v);

function srcLink(url, label) {
  if (!url) return '<span class="pill warn" title="no official source attached">no source</span>';
  return `<a class="src" href="${esc(url)}" target="_blank" rel="noopener">${esc(label || hostOf(url))}</a>`;
}
function hostOf(u) {
  try { return new URL(u).hostname.replace(/^www\./, ''); } catch { return 'source'; }
}
function pill(status) {
  const s = String(status || '').toLowerCase();
  const map = {
    pass: 'pass', fail: 'fail', warn: 'warn', flag: 'flag', met: 'met', done: 'done',
    open: 'open', verified: 'verified', unverified: 'unverified', partial: 'partial',
    certified: 'certified', rejected: 'rejected', good: 'good', bad: 'bad',
  };
  return `<span class="pill ${map[s] || 'neutral'}">${esc(status ?? '—')}</span>`;
}

function table(cols, rows, opts = {}) {
  if (!rows || !rows.length) return '<p class="muted small">No rows.</p>';
  const head = cols.map(c => `<th class="${c.num ? 'num' : ''}">${esc(c.label)}</th>`).join('');
  const body = rows.map(r => '<tr>' + cols.map(c => {
    const raw = c.render ? c.render(r) : vblank(r[c.key]);
    const cls = c.num ? ' class="num"' : c.mono ? ' class="mono"' : '';
    return `<td${cls}>${raw}</td>`;
  }).join('') + '</tr>').join('');
  return `<div class="tbl-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function statCard(k, v, n, cls = '') {
  return `<div class="card tight"><div class="k">${esc(k)}</div>
    <div class="v ${cls}">${v}</div><div class="n">${n || ''}</div></div>`;
}

function setHeader(active) {
  const nav = NAV.map(([href, label, key]) =>
    `<a href="${href}" class="${key === active ? 'active' : ''}">${esc(label)}</a>`).join('');
  document.getElementById('nav').innerHTML = nav;
}

async function stamp() {
  try {
    const idx = await load('index.json');
    const el = document.getElementById('stamp');
    if (el) el.textContent = 'build ' + idx.generated_utc.replace('T', ' ').replace('Z', 'Z');
  } catch (e) { /* leave blank */ }
}

function boot(active, fn) {
  setHeader(active);
  stamp();
  const el = document.getElementById('app');
  fn(el).catch(err => {
    el.innerHTML = `<div class="note bad"><strong>Could not load data.</strong>
      ${esc(err.message)}<br><span class="small">Run <code>python3 -m pipeline.build</code>
      to regenerate <code>site/data/</code>, then reload.</span></div>`;
  });
}

/* Expose to pages */
window.app = { load, esc, num, pct, sgn, blank, vblank, srcLink, pill, table, statCard, boot, isNum };
/* Page modules call boot() directly, so it must be in global scope too. */
if (typeof window !== 'undefined') window.boot = boot;
