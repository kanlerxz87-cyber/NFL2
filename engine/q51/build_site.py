#!/usr/bin/env python3
"""Deterministic Q51 evidence dashboard. No external runtime dependencies."""
from __future__ import annotations
import html, json, re
from pathlib import Path
from .validation import GATES

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'q51'
DATA=OUT/'data'
RESEARCH=ROOT/'research'/'q51'
NFL='https://www.nfl.com/'
RULES='https://media.nfl.com/content/dam/communications/Official%20Playing%20Rules/2026%20Official%20Playing%20Rules.pdf'
STATS='https://www.nfl.com/stats/player-stats/'
SCHEDULE='https://www.nfl.com/news/week-11-schedule-change'
INJ='https://www.nfl.com/injuries/league/2026/REG10'
ROUNDUP='https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11'
REPO='https://github.com/kanlerxz87-cyber/NFL2'
PAGES=[('index','Overview'),('executive-summary','Executive summary'),('lines','Research lines'),('correlations','Correlations'),('availability','Injuries & depth'),('competition','Competition & gates'),('decisions','Questions & suggestions'),('flagged','Flagged for Review'),('methodology','Methodology'),('sources','Sources')]

def load(p): return json.loads(Path(p).read_text())
def e(x): return html.escape(str(x),quote=True)
def link(url,label=None): return f'<a href="{e(url)}" target="_blank" rel="noopener">{e(label or url)}</a>'
def src(*urls): return '<span class="sources">'+' · '.join(link(u) for u in urls if u)+'</span>'
def blank(): return '<td class="blank" aria-label="Unverified — not published"></td>'
def cell(x): return blank() if x is None or x=='' else f'<td>{e(x)}</td>'
def num(x,d=3): return '' if x is None else f'{x:.{d}f}'
def table(headers,rows,caption=''):
    head=''.join(f'<th scope="col">{e(h)}</th>' for h in headers)
    body=''.join('<tr>'+''.join(r)+'</tr>' for r in rows)
    cap=f'<caption>{e(caption)}</caption>' if caption else ''
    return f'<div class="tablewrap"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
def card(title,value,note): return f'<article class="card"><h3>{e(title)}</h3><p class="metric">{e(value)}</p><p>{e(note)}</p></article>'
def callout(text,kind='warn'): return f'<div class="callout {kind}">{text}</div>'

def nav(active):
    parts=[]
    for slug,label in PAGES:
        current=' aria-current="page"' if slug==active else ''
        parts.append(f'<a href="{slug}.html"{current}>{e(label)}</a>')
    items=''.join(parts)
    return f'<header><a class="brand" href="index.html">NFL2 <span>Q51 evidence</span></a><nav aria-label="Q51 sections">{items}</nav><a class="rootlink" href="../index.html">Canonical dashboard</a></header>'

def page(slug,title,subtitle,body):
    doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — NFL2 Q51</title><link rel="stylesheet" href="assets/style.css"></head><body>{nav(slug)}<main><h1>{e(title)}</h1><p class="subtitle">{subtitle}</p>{body}</main><footer>Paper-only research · snapshot 2026-11-12 · no wager placement · <a href="{REPO}">canonical repository</a></footer><script src="assets/app.js"></script></body></html>'''
    (OUT/f'{slug}.html').write_text(doc)

def strip_status(s):
    if not s: return ''
    return re.sub(r'\s*\([^)]*\)','',s).strip()

def main():
    OUT.mkdir(exist_ok=True); (OUT/'assets').mkdir(exist_ok=True)
    lines=load(DATA/'lines.json'); corr=load(DATA/'correlations.json'); avail=load(DATA/'availability.json')
    gates=load(DATA/'gates.json'); board=load(DATA/'leaderboard.json'); review=load(RESEARCH/'current-review.json')
    ledger=load(RESEARCH/'source-evidence.json'); sources={s['id']:s for s in ledger['sources']}
    depth=load(ROOT/'data'/'s53126614_depth_deficiencies_2026.json')['deficiencies']
    probe=load(RESEARCH/'collector-probe.json') if (RESEARCH/'collector-probe.json').exists() else {'successful':0,'failed':0}
    # Overview
    body=callout('<strong>Decision status:</strong> research lines are generated but <strong>not validated</strong>. No market prices, prop thresholds, settlement archive or eligible strategy results exist. Luck is controlled, not eliminated.')
    body+='<section class="cards">'+card('Official game log',str(lines['training_games']),'Weeks 1–9; batch retrieval, not a historical point-in-time archive.')+card('Research lines',str(len(lines['lines'])),'Week 11 planning slate; neutral-site handling explicit.')+card('Descriptive correlations',str(len(corr['coefficients'])),'Game-score associations only; 9 week clusters, intervals withheld.')+card('Eligible strategies','0','All gates fail closed; leaderboard empty by design.')+'</section>'
    rows=[['Collection','Partial','254 injury listings and 227 depth events inherited; live collector probe failed in sandbox.',src(INJ,ROUNDUP)],
          ['Line origination','Unvalidated research','13 current-snapshot ridge lines; no market comparison or edge.',src(SCHEDULE,NFL+'schedules/2026/REG/')],
          ['Correlation','Descriptive only','6 game-score pairs; not prop-leg correlations.',src(NFL+'schedules/2026/REG/')],
          ['Competition','Blocked','Singles, parlays and prop combos covered by gates; no eligible entries.',src(RULES,REPO+'/blob/main/engine/q51/validation.py')],
          ['Review','Published','Questions, suggestions and flagged items are visible before optional changes.',src(NFL,REPO+'/blob/main/research/q51/current-review.json')]]
    body+='<h2>Workstream status</h2>'+table(['Workstream','Status','Analysis','Official / canonical evidence'],[[cell(a),cell(b),cell(c),d] for a,b,c,d in rows])
    body+='<h2>Start here</h2><ul><li><a href="executive-summary.html">Executive summary</a></li><li><a href="flagged.html">Flagged for Review</a></li><li><a href="decisions.html">Questions & suggestions</a></li><li><a href="methodology.html">Methodology and limitations</a></li></ul>'
    page('index','Q51 evidence dashboard','Independent audit, reproducible research engine and fail-closed competition policy.',body)
    # Executive summary
    body=callout('<strong>Bottom line:</strong> the project now has a source-linked dashboard, a tested paper-only engine and an explicit review queue. It does <strong>not</strong> have a validated betting edge. The next decision is data access and pre-registration, not staking.')
    body+='<h2>What is verified</h2><p>Standings, schedule, injury listings and player/team statistics are inherited from official NFL.com transcriptions and reconciled by the repository verifiers. Q51 re-audited the original 48-file baseline line by line, recorded 18 findings, and rechecked the affected current files after upstream repairs. Two game-center pages were independently re-read as spot checks; the full 136-game log is reconciled to standings, not claimed as a fresh per-page re-transcription here.</p>'
    body+='<h2>What is computed</h2><p>Thirteen Week 11 research lines use a predeclared ridge margin/total baseline on 136 completed games. Six descriptive Pearson correlations use official final scores. Intervals are withheld because only nine week clusters exist. These outputs are not calibrated probabilities, market edges or same-game prop correlations.</p>'
    body+='<h2>What remains blocked</h2><p>Licensed opening/closing prices, prop thresholds, book-specific settlement contracts, play-by-play/snaps/routes, confirmed game-day lineups, weather and a locked out-of-sample holdout are missing. The collector is implemented and unit-tested but the live sandbox probe failed at the TLS boundary. No scheduled ingestion is claimed.</p>'
    body+='<h2>Competition and rewards</h2><p>Separate boards are defined for singles, parlays and player-prop combos. Only gate-eligible paper strategies can rank; rewards are virtual badges. Monetary rewards, betting credits and real-money execution are disabled pending legal, funding and operational review.</p>'
    body+='<h2>Luck policy</h2><p>Luck cannot be removed. The engine controls it with point-in-time guards, chronological validation, cluster bootstrap uncertainty, Holm multiplicity correction, calibration, executable CLV/net ROI lower bounds, stability checks and paper drawdown caps. A fixed bet count never proves skill.</p>'
    body+='<h2>Recommended next decision</h2><p>Review the <a href="decisions.html">suggestions and questions</a>. Choose a data-access path and pre-register one hypothesis family before collecting outcomes. Do not enable real-money execution.</p>'
    page('executive-summary','Executive summary','A decision-ready summary of verified facts, computed research and unresolved gaps.',body)
    # Lines
    body=callout('<strong>Not betting advice.</strong> Current-snapshot research only. Training data was retrieved as a batch after completion; this is not a historical backtest. Market price, edge and CLV are blank.')
    rows=[]
    for g in lines['lines']:
        rows.append([cell(g['away']+' @ '+g['home']),cell('Neutral' if g.get('neutral_site') else 'Home/away'),cell(num(g.get('expected_home_margin'),2)),cell(num(g.get('fair_home_spread'),2)),cell(num(g.get('fair_total'),2)),cell(num(g.get('home_win_probability'),3)),blank(),blank(),blank(),src(g['source_url'],NFL+'schedules/2026/REG/')])
    body+=table(['Fixture','Venue mode','Expected home margin','Fair home spread','Fair total','Empirical home win share','Market price','Edge','CLV','Official inputs'],rows,'Week 11 planning slate · ridge=20 · 136 training games')
    body+='<h2>Adjustments</h2><p>Injury, lineup, weather and rest/travel adjustments are exactly zero because the inputs are unavailable. Zero means <em>unavailable</em>, not <em>no effect</em>. Probabilities are in-sample residual shares, not out-of-sample calibration.</p>'
    page('lines','Originated research lines','Deterministic ridge baseline; unvalidated, paper-only, no market comparison.',body)
    # Correlations
    body=callout('<strong>Scope:</strong> descriptive associations among official final scores. These are not causal effects, betting edges or player-prop leg correlations. Only nine week clusters exist; publication intervals are withheld.')
    rows=[]
    for c in corr['coefficients']:
        rows.append([cell(c['label']),cell(c['n']),cell(num(c['pearson'],4)),blank(),blank(),cell('9 week clusters; interval withheld'),src(c['source_url'])])
    body+=table(['Pair','n','Pearson r','95% lower','95% upper','Uncertainty status','Official input'],rows)
    body+='<h2>Parlay and prop-combo policy</h2><p>Same-game legs require a trained joint distribution and book-specific settlement. Naive multiplication is prohibited. Cross-game independence must be tested by game/week clusters, not assumed. No prop thresholds or paired prop outcomes are present, so prop-leg coefficients remain blank.</p>'
    page('correlations','Correlation register','Measured game-score associations and explicitly blocked prop-leg estimates.',body)
    # Availability
    body=callout('<strong>Week 10 snapshot.</strong> Practice participation is not game status. Club depth charts are unofficial editorial ordering. Confirmed replacement impact is blank until official gamebook lineups and playing-time data are joined.')
    rows=[]
    for r in avail['rows']:
        rows.append([cell(r['team']),cell(r['injury_listings']),cell(r['out']),cell(r['questionable']),cell(r['depth_events']),blank(),src(r['source_url'],r['depth_source_url'])])
    body+='<h2>Club availability summary</h2>'+table(['Team','Injury listings','OUT','Questionable','Depth events','Confirmed replacement impact','Official sources'],rows)
    rows=[]
    for d in depth:
        rows.append([cell(d['team']),cell(d['side']),cell(d['unit']),cell(strip_status(d['starter_1st'])),cell(strip_status(d['backup_2nd'])),cell(strip_status(d['backup_3rd'])),cell(strip_status(d['backup_4th'])),blank(),src(d['depth_source'],d['injury_source'])])
    body+='<h2>1st–4th string ordering (unofficial club charts)</h2><p>Status annotations from the inherited snapshot are removed here; only ordering is shown. Confirm actual replacements with official gamebooks. Missing strings stay blank.</p>'+table(['Team','Side','Unit','1st','2nd','3rd','4th','Confirmed impact','Club + league sources'],rows)
    page('availability','Injuries and depth deficiencies','Official injury listings plus unofficial club ordering; no inferred replacement performance.',body)
    # Competition
    body=callout('<strong>Leaderboard empty.</strong> No strategy has supplied eligible historical market evidence. Rewards are virtual badges only; real-money execution is disabled.')
    rows=[]
    for g in gates['gates']:
        rows.append([cell(g['id']),cell(next(x[1] for x in GATES if x[0]==g['id'])),cell('PASS' if g['passed'] else 'BLOCKED'),cell(g['detail']),src(RULES,REPO+'/blob/main/engine/q51/validation.py')])
    body+='<h2>Validation gates</h2>'+table(['Gate','Name','Current status','Rule','Policy / official context'],rows)
    specs=[('Single: rating vs market','Beat no-vig market on proper scores and executable CLV','Blocked: no price archive'),('Single: availability shock','Point-in-time injury/lineup shock vs baseline','Blocked: no historical lineup archive'),('Parlay: cross-game joint','Cluster-tested joint model, not naive independence','Blocked: no ticket/settlement archive'),('Parlay: price dispersion','Compare executable joint prices after fees/limits','Blocked: no price archive'),('Prop combo: QB–WR joint','Same-game joint distribution with settlement adapter','Blocked: no prop thresholds/outcomes'),('Prop combo: usage replacement','Snaps/routes/targets after confirmed starter replacement','Blocked: no entitlement or gamebook join')]
    rows=[[cell(a),cell(b),cell(c),blank(),src(STATS,RULES,REPO+'/blob/main/engine/q51/grading.py')] for a,b,c in specs]
    body+='<h2>Strategy families (proposed, not results)</h2>'+table(['Market','Hypothesis','Current blocker','Performance','Official / canonical context'],rows)
    body+='<h2>Reward rules</h2><p>Gold/Silver/Bronze virtual badges for gate-eligible paper strategies only. No cash, betting credits, deposits, wager placement or guaranteed profit. Monetary rewards require a separate legal/funding/operational decision and are not implemented.</p>'
    page('competition','Competition, gates and rewards','Singles, parlays and player-prop combos; fail-closed eligibility and virtual badges only.',body)
    # Decisions
    suggestions=[('SQ51-01','License an opening/closing odds archive','High','High','Blocks CLV, devig and market baseline','Proposed',STATS),('SQ51-02','Acquire play-by-play/snaps/routes entitlement','High','High','Needed for EPA and replacement usage','Proposed',STATS),('SQ51-03','Schedule the robots-aware collector outside the sandbox','High','Medium','Live probe failed; need immutable hashes and drift alerts','Proposed',INJ),('SQ51-04','Join official gamebook lineups to depth charts','High','Medium','Confirms actual starter replacements','Proposed',NFL+'schedules/2026/REG/'),('SQ51-05','Pre-register one hypothesis family and locked holdout','High','Low','Controls multiplicity and selection bias','Proposed',RULES),('SQ51-06','Build same-game joint prop model after data access','High','High','No naive multiplication','Proposed',STATS),('SQ51-07','Add weather and rest/travel features','Medium','Medium','Only after point-in-time storage','Proposed','https://www.weather.gov/'),('SQ51-08','Review monetary rewards and jurisdiction separately','High','High','Paper-only until legal/funding approval','Proposed','https://www.ncpgambling.org/help-treatment/')]
    rows=[]
    for sid,name,impact,effort,why,status,url in suggestions:
        rows.append([cell(sid),cell(name),cell(impact),cell(effort),cell(why),cell(status),f'<td><label class="review"><input type="checkbox" data-suggestion="{sid}"> Select for review</label></td>',src(url,REPO+'/blob/main/engine/q51/build_site.py')])
    body=callout('<strong>Review before implementation.</strong> Selections are stored only in this browser and do not change the repository or enable any strategy.','info')
    body+='<h2>Suggestions</h2>'+table(['ID','Suggestion','Impact','Effort','Reason','Status','Review','Context source'],rows)
    questions=[('QQ51-01','Which licensed market archive is authorized?','No odds archive','Contract/API scope, timestamps, markets, settlement','Ask data owner; test a signed sample against book terms',''), ('QQ51-02','Which player-level data entitlement is available?','No snaps/routes/targets','Play-by-play and participation license','Inspect provider schema; join to official gamebooks',''), ('QQ51-03','What is the canonical team key?','LA/LAR aliases','Stable internal ID with source-native aliases','Adopt LAR internally; preserve aliases','LAR'), ('QQ51-04','Which book settlement rules apply?','No settlement contracts','Push/void/OT/dead-heat rules per market','Obtain terms; encode adapters and tests',''), ('QQ51-05','What is the pre-registered trial family?','No frozen family','Hypotheses, code hash, thresholds, staking','Freeze before outcomes; include all tuning trials',''), ('QQ51-06','Where will immutable raw responses live?','Collector probe failed','Object storage or Git LFS policy with hashes','Run collector outside sandbox; verify robots and retention',''), ('QQ51-07','Which official gamebooks confirm replacements?','Depth charts unofficial','Gamebook participation/lineup PDFs','Download per game; join player IDs and snaps',''), ('QQ51-08','Is the competition legal in the operator jurisdiction?','US helpline only','Local legal review, age/KYC, funding','Counsel review; keep paper-only until resolved',''), ('QQ51-09','What reward budget is approved?','No funding','Virtual badges now; monetary later','Owner decision; no betting credits by default','Virtual badges only'), ('QQ51-10','Which season is the locked holdout?','No holdout','Chronological split and cluster plan','Pre-register season; do not tune on it','')]
    rows=[[cell(a),cell(b),cell(c),cell(d),cell(f),cell(g if g else None),src(STATS if i in (1,2,6,7) else RULES if i in (4,5,10) else INJ if i==3 else REPO)] for i,(a,b,c,d,f,g) in enumerate(questions,1)]
    body+='<h2>Questions / information needed</h2>'+table(['ID','Question','Known','Missing','Discovery plan','Answer','Context source'],rows)
    page('decisions','Questions and suggestions','Dedicated review section. Optional changes remain proposed until selected and approved.',body)
    # Flagged
    rows=[]
    status={r['id']:r for r in review['findings']}
    for f in ledger['findings']:
        urls=[sources[s]['url'] for s in f['source_ids'] if s in sources]
        st=status.get(f['id'],{}).get('status','needs review'); action=status.get(f['id'],{}).get('action',f['resolution'])
        rows.append([cell(f['id']),cell(f['severity']),cell(f['title']),cell(st),cell(action),src(*urls,REPO+'/blob/main/research/q51/source-evidence.json')])
    extra=[('Q51-F19','medium','Missing team anchors and archive cross-build links','resolved','Added anchor targets and repaired archive links.',REPO+'/blob/main/scripts/audit_q51_current.py',NFL),('Q51-F20','high','Live collector probe failed at sandbox TLS boundary','open_environment','0/7 successful retrievals; manual page-fetch evidence kept separate.',REPO+'/blob/main/research/q51/collector-probe.json',INJ),('Q51-F21','high','Game log is batch-retrieved, not historical point-in-time','open_method_limit','Current-snapshot research only; no backtest claim.',REPO+'/blob/main/q51/data/games.json',NFL+'schedules/2026/REG/'),('Q51-F22','medium','Inherited design/proposal pages lack NFL/club row links','open_legacy_design_rows','Flagged as internal design; Q51 pages enforce row-level links.',REPO+'/blob/main/research/q51/current-audit.json',NFL),('Q51-F23','medium','Legacy root Pages and docs-only Actions workflow coexist','open_deployment_topology','Confirm root legacy deployment after merge; do not assume Actions artifact is live.',REPO+'/blob/main/.github/workflows/pages.yml',NFL)]
    for fid,sev,title,st,action,url,official in extra:
        rows.append([cell(fid),cell(sev),cell(title),cell(st),cell(action),src(official,url)])
    body=callout('<strong>Flagged items do not block publication.</strong> They are visible here with evidence and an explicit status. Unverified values remain blank; nothing is inferred.')
    body+=table(['ID','Severity','Finding','Status','Action / resolution','Evidence'],rows,'A-01–A-18 baseline findings plus Q51 current-tree findings')
    page('flagged','Flagged for Review','Every irregularity and unresolved data gap, with source links and explicit status.',body)
    # Methodology
    body='<h2>Verification layers</h2><ol><li><strong>Structural:</strong> syntax, hashes, line counts, internal links, table shape and row-source coverage.</li><li><strong>Factual:</strong> official source actually read; stored value compared cell by cell; conflicts flagged.</li><li><strong>Derived:</strong> deterministic code over source-linked inputs; labelled as model output, not an NFL fact.</li><li><strong>Policy:</strong> gates and rewards are project decisions, not league rules or guarantees.</li></ol>'
    body+='<h2>Never infer</h2><p>Unconfirmable values are blank and flagged. Practice participation is not game status. Club depth ordering is not a confirmed lineup. Neutral-site games do not receive standard home-field adjustment. A source URL prefix is not proof of factual agreement.</p>'
    body+='<h2>Luck and validation</h2><p>Luck cannot be eliminated. Controls include point-in-time availability, chronological walk-forward validation, locked holdout, cluster bootstrap intervals, Holm correction over the complete trial family, calibration, executable CLV/net ROI lower bounds, stability and paper drawdown caps. Minimum counts are necessary but never sufficient.</p>'
    body+='<h2>Settlement</h2><p>Singles and parlays require explicit book-specific settlement. The engine tests pushes, voids and tie conventions; a void leg reduces the parlay price under the declared paper convention. Official NFL scoring rules do not establish sportsbook settlement.</p>'
    rows=[[cell('Structural audit'),cell('Every tracked file hashed; JSON/CSV/Python/JS parsed; HTML rows and links inventoried'),src(REPO+'/blob/main/scripts/audit_q51_current.py',NFL)],[cell('Engine tests'),cell('34 tests: odds, devig, grading, leakage, bootstrap, gates and collector parsers'),src(REPO+'/blob/main/tests/q51',RULES)],[cell('Collector'),cell('Allowlisted, robots-aware, rate-limited, SHA-256 manifest; live probe failed in sandbox'),src(REPO+'/blob/main/collectors/q51/collect.py',INJ)]]
    body+=table(['Layer','Implementation','Evidence'],rows)
    page('methodology','Methodology and limitations','What is verified, what is computed, and what the project refuses to infer.',body)
    # Sources
    rows=[]
    for s in ledger['sources']:
        rows.append([cell(s['id']),cell(s['authority']),cell(s['used_for']),cell(s.get('evidence','')),link(s['url'])])
    body=table(['ID','Authority','Used for','Evidence actually read','Source'],rows,'Source ledger recorded during the Q51 audit; retrieval method is disclosed in the ledger.')
    body+='<h2>Current review</h2><p>'+link(REPO+'/blob/main/research/q51/current-review.json','current-review.json')+' records resolved, mitigated and open findings after upstream repairs. '+link(REPO+'/blob/main/research/q51/current-audit.json','current-audit.json')+' records the structural current-tree inventory.</p>'
    page('sources','Source ledger','Official and canonical sources actually read, with the evidence used from each.',body)
    # Assets
    (OUT/'assets'/'style.css').write_text('''
:root{--bg:#f6f8fb;--panel:#fff;--ink:#172033;--muted:#5b6475;--line:#dfe5ee;--accent:#174ea6;--warn:#fff4d6;--info:#e8f1ff;--blank:#f0f2f6}*{box-sizing:border-box}body{margin:0;font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}header{background:#101827;color:#fff;padding:14px 20px;display:flex;gap:18px;align-items:center;flex-wrap:wrap;position:sticky;top:0;z-index:5}.brand{font-weight:800;color:#fff;text-decoration:none;font-size:18px}.brand span{font-weight:500;color:#b9c6dd}.rootlink{margin-left:auto;color:#cfe0ff}nav{display:flex;gap:4px;flex-wrap:wrap}nav a{color:#dbe5f5;text-decoration:none;padding:6px 9px;border-radius:7px;font-size:13px}nav a:hover,nav a[aria-current]{background:#26364f;color:#fff}main{max-width:1280px;margin:0 auto;padding:28px 20px 60px}h1{font-size:30px;margin:0 0 6px}h2{margin-top:32px;font-size:21px}.subtitle{color:var(--muted);margin-top:0}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:22px 0}.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}.card h3{margin:0 0 8px;font-size:14px;color:var(--muted)}.metric{font-size:30px;font-weight:800;margin:0 0 8px;color:var(--accent)}.callout{padding:14px 16px;border-radius:10px;margin:18px 0;border:1px solid #e6cf82;background:var(--warn)}.callout.info{background:var(--info);border-color:#b9d2f5}.tablewrap{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:12px 0 22px}table{border-collapse:collapse;width:100%;font-size:13px}caption{text-align:left;padding:12px;font-weight:700;color:var(--muted)}th,td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}th{background:#eef2f8;position:sticky;top:0;font-size:12px;text-transform:uppercase;letter-spacing:.03em}tr:last-child td{border-bottom:0}td.blank{background:var(--blank);min-width:70px}td.blank:after{content:"—";color:#9aa3b2}.sources a{color:var(--accent);overflow-wrap:anywhere}a{color:var(--accent)}.review{white-space:nowrap}footer{padding:20px;text-align:center;color:var(--muted);border-top:1px solid var(--line)}@media(max-width:700px){header{position:static}main{padding:20px 12px}h1{font-size:25px}th,td{padding:8px}}
''')
    (OUT/'assets'/'app.js').write_text('''
document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('[data-suggestion]').forEach(el=>{const k='nfl2-q51-review-'+el.dataset.suggestion;el.checked=localStorage.getItem(k)==='1';el.addEventListener('change',()=>localStorage.setItem(k,el.checked?'1':'0'));});});
''')
    print(f'built {len(PAGES)} Q51 pages')

if __name__=='__main__': main()
