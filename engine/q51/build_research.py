#!/usr/bin/env python3
"""Build Q51 research artifacts from already checked-in, source-linked inputs.

This is a CURRENT snapshot model, not a historical backtest. The upstream game
log was retrieved as a batch after the games were final; that batch timestamp is
used as availability. It must not be misrepresented as point-in-time historical
feature availability. No market prices, prop thresholds or settlement contracts
are invented. Outputs are paper-only research, never betting recommendations.
"""
from __future__ import annotations
import csv, json, hashlib
from pathlib import Path
from .models import Game, RidgeBaseline
from .statistics import pearson, cluster_bootstrap_correlation
from .validation import evaluate_gates, leaderboard, GATES
from .cli import lines_report, correlation_report

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'q51'/'data'
RESEARCH=ROOT/'research'/'q51'
SCHEDULE_URL='https://www.nfl.com/news/week-11-schedule-change'
GAMES_URL='https://www.nfl.com/schedules/2026/REG/'
INJURY_URL='https://www.nfl.com/injuries/league/2026/REG10'
ROUNDUP_URL='https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11'


def read_csv(name):
    with (ROOT/'data'/name).open(newline='') as f: return list(csv.DictReader(f,delimiter='|'))

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def main():
    sources={r['id']:r for r in read_csv('sources.csv')}
    retrieved=sources['S-GAMES26']['accessed_utc'].replace('Z',':00+00:00')
    rows=read_csv('games_2026_wk1_9.csv')
    standings=json.loads((ROOT/'data'/'standings-2026.json').read_text())['teams']
    aliases={t['team']:('LAR' if t['abbr']=='LA' else t['abbr']) for t in standings}
    games=[]
    for i,r in enumerate(rows,1):
        home=aliases.get(r['home'],r['home']); away=aliases.get(r['away'],r['away'])
        games.append({'game_id':f"2026-R{int(r['week']):02d}-{away}-{home}",'season':2026,'week':int(r['week']),
                      'home':home,'away':away,'home_score':int(r['home_pts']),'away_score':int(r['away_pts']),
                      'neutral':r['neutral']=='yes','status':'final','source_url':r['source'],'available_at':retrieved,
                      'source_row':i+1})
    dump(OUT/'games.json',{'games':games,'provenance':{'source_id':'S-GAMES26','batch_retrieved_at':retrieved,
        'limitation':'Batch retrieval after completion; not a historical point-in-time archive. Current-snapshot research only.'}})
    schedule=json.loads((ROOT/'data'/'schedule-week11-2026.json').read_text())
    sg=[]
    for i,g in enumerate(schedule['games'],1):
        home=aliases[g['home']]; away=aliases[g['away']]
        sg.append({'game_id':f'2026-R11-{away}-{home}','home':home,'away':away,'date':g['date'],'time_et':g['timeET'],
                   'tv':g['tv'],'neutral':'Mexico City' in g.get('note',''),'source_url':SCHEDULE_URL,'source_row':i+10})
    dump(OUT/'week11.json',{'games':sg,'source_url':SCHEDULE_URL,'as_of':'2026-11-12','planning_week':11})
    lines=lines_report(str(OUT/'games.json'),str(OUT/'week11.json'),'2026-11-12T23:59:59+00:00')
    lines['provenance']={'training_source':GAMES_URL,'schedule_source':SCHEDULE_URL,'batch_retrieved_at':retrieved,
                         'input_sha256':hashlib.sha256((ROOT/'data'/'games_2026_wk1_9.csv').read_bytes()).hexdigest()}
    lines['not_a_backtest']=True
    dump(OUT/'lines.json',lines)
    # Descriptive game-level associations. These are NOT prop-leg correlations.
    hs=[g['home_score'] for g in games]; aws=[g['away_score'] for g in games]
    totals=[h+a for h,a in zip(hs,aws)]; margins=[h-a for h,a in zip(hs,aws)]
    abs_margins=[abs(m) for m in margins]; clusters=[f"2026-W{g['week']}" for g in games]
    specs=[('home_points_away_points','Home points vs away points',hs,aws),
           ('home_points_total','Home points vs game total',hs,totals),
           ('away_points_total','Away points vs game total',aws,totals),
           ('total_absolute_margin','Game total vs absolute margin',totals,abs_margins),
           ('home_margin_total','Home margin vs game total',margins,totals),
           ('home_points_home_win','Home points vs home win indicator',hs,[1 if m>0 else 0 for m in margins])]
    pairs=[]
    for pid,label,x,y in specs:
        pairs.append({'id':pid,'label':label,'source_url':GAMES_URL,'observations':[{'x':a,'y':b,'cluster_id':c,'available_at':retrieved} for a,b,c in zip(x,y,clusters)]})
    dump(OUT/'correlation-inputs.json',{'pairs':pairs})
    corr=correlation_report(str(OUT/'correlation-inputs.json'))
    for item,pair in zip(corr['coefficients'],pairs):
        item['label']=pair['label']; item['ci_status']='withheld_only_9_week_clusters'
        if item.get('bootstrap'): item['bootstrap']['lower']=None; item['bootstrap']['upper']=None
    corr['interpretation']='Descriptive associations among official final scores. Not causal effects, not betting edges, and not same-game player-prop leg correlations.'
    dump(OUT/'correlations.json',corr)
    gates=evaluate_gates({}, {}, market='single')
    dump(OUT/'gates.json',gates)
    dump(OUT/'leaderboard.json',leaderboard([]))
    # Availability summary: counts are derived from the official-source-linked CSV.
    injuries=read_csv('injuries_2026_wk10.csv'); depth=read_csv('depth_changes_2026_wk10.csv')
    teams=sorted(set(r['team'] for r in injuries)|set(r['team'] for r in depth))
    availability=[]
    for t in teams:
        ir=[r for r in injuries if r['team']==t]; dr=[r for r in depth if r['team']==t]
        availability.append({'team':t,'injury_listings':len(ir),'out':sum(r['status']=='OUT' for r in ir),
                             'questionable':sum(r['status']=='Q' for r in ir),'depth_events':len(dr),
                             'confirmed_replacement_impact':None,'source_url':INJURY_URL,'depth_source_url':ROUNDUP_URL})
    dump(OUT/'availability.json',{'as_of':'2026-11-12','week':10,'rows':availability,
        'limitations':['Practice participation is not game status.','Club depth charts are unofficial editorial ordering.','No snaps, routes, targets or replacement performance are inferred.','Week 10 snapshot is stale for Week 11 decisions.']})
    # Preserve the failed live probe rather than silently substituting fetched text.
    probe=Path('/tmp/nfl2-collector/manifest.json')
    if probe.exists(): dump(RESEARCH/'collector-probe.json',json.loads(probe.read_text()))
    print(json.dumps({'games':len(games),'lines':len(lines['lines']),'correlations':len(corr['coefficients']),
                      'availability_teams':len(availability),'eligible_strategies':0},indent=2))

if __name__=='__main__': main()
