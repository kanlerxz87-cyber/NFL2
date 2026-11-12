"""Offline CLI: python -m engine.cli lines|correlations|leaderboard."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .models import Game,RidgeBaseline
from .statistics import pearson,joint_metrics,cluster_bootstrap_correlation
from .validation import evaluate_gates,leaderboard,GATES


def load(path): return json.loads(Path(path).read_text())


def lines_report(games_path,schedule_path,as_of):
    base={'as_of':as_of,'status':'blocked','real_money_enabled':False,'lines':[],'gates':[{'id':g[0],'name':g[1]} for g in GATES]}
    if not games_path or not Path(games_path).exists():
        base['reason']='No completed official game-result archive supplied. Aggregate standings are not a point-in-time training set.'; return base
    payload=load(games_path); games=[]
    for g in payload.get('games',[]):
        if g.get('status')!='final' or g.get('home_score') is None or g.get('away_score') is None or not g.get('available_at') or g['available_at']>as_of: continue
        games.append(Game(g['game_id'],g['season'],g['week'],g['home'],g['away'],g['home_score'],g['away_score'],g.get('neutral',False),g.get('source_url',''),g['available_at']))
    teams=sorted({t for g in games for t in (g.home,g.away)})
    model=RidgeBaseline()
    try: model.fit(games,teams)
    except ValueError as e: base['reason']=str(e); return base
    if not schedule_path or not Path(schedule_path).exists(): base['reason']='No official planning schedule supplied.'; return base
    schedule=load(schedule_path)
    for g in schedule.get('games',[]):
        home,away=g.get('home'),g.get('away')
        if home not in teams or away not in teams:
            base['lines'].append({'home':home,'away':away,'status':'blocked','reason':'Team lacks completed-game history.','source_url':g.get('source_url')}); continue
        p=model.predict(home,away,neutral=g.get('neutral',False),decision_at=as_of)
        p.update({'game_id':g.get('game_id'),'source_url':g.get('source_url'),'market_price':None,'edge':None,'clv':None})
        base['lines'].append(p)
    base['status']='research_lines_generated_unvalidated'; base['training_games']=len(games); return base


def correlation_report(path):
    if not path or not Path(path).exists(): return {'status':'blocked','reason':'No point-in-time paired observations supplied.','coefficients':[]}
    payload=load(path); out=[]
    for pair in payload.get('pairs',[]):
        rows=[r for r in pair.get('observations',[]) if r.get('available_at') and r.get('cluster_id')]
        x=[r.get('x') for r in rows]; y=[r.get('y') for r in rows]
        item={'id':pair.get('id'),'source_url':pair.get('source_url'),'n':len(rows),'pearson':None,'joint':None,'bootstrap':None}
        if len(rows)>=3 and all(isinstance(v,(int,float)) for v in x+y):
            item['pearson']=pearson(x,y)
            item['bootstrap']=cluster_bootstrap_correlation(x,y,[r['cluster_id'] for r in rows])
            if all(v in (0,1) for v in x+y): item['joint']=joint_metrics(x,y)
        else: item['status']='unverified_missing_or_nonnumeric_pairs'
        out.append(item)
    return {'status':'computed_from_supplied_observations','coefficients':out,'warning':'Raw association is not a parlay price or causal effect. Intervals resample entire game/week clusters.'}


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('lines'); p.add_argument('--games'); p.add_argument('--schedule'); p.add_argument('--as-of',required=True); p.add_argument('--out')
    p=sub.add_parser('correlations'); p.add_argument('--pairs'); p.add_argument('--out')
    p=sub.add_parser('leaderboard'); p.add_argument('--strategies'); p.add_argument('--out')
    args=ap.parse_args()
    if args.command=='lines': result=lines_report(args.games,args.schedule,args.as_of)
    elif args.command=='correlations': result=correlation_report(args.pairs)
    else:
        strategies=load(args.strategies).get('strategies',[]) if args.strategies and Path(args.strategies).exists() else []
        result=leaderboard(strategies); result['gate_definitions']=[{'id':a,'name':b,'rule':c} for a,b,c in GATES]
    text=json.dumps(result,indent=2)+'\n'
    if args.out: Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(text)
    print(text,end='')
if __name__=='__main__': main()
