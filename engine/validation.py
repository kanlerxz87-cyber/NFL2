"""Fail-closed competition gates. Missing evidence is never a pass.

Thresholds are project policy, not empirical guarantees. Luck cannot be
eliminated; uncertainty, bias, selection effects and dependence are controlled.
"""
from __future__ import annotations
from .statistics import holm_adjust

GATES = [
    ('G00','Official provenance','Every input has an official source, retrieval time and response hash; critical conflicts resolved.'),
    ('G01','Point-in-time integrity','Feature availability <= decision time; no postgame revisions or future outcomes.'),
    ('G02','Pre-registration','Hypothesis, code hash, complete trial family, market, staking and thresholds frozen before outcomes.'),
    ('G03','Chronological validation','Walk-forward tuning plus untouched season holdout; entire games/weeks kept together.'),
    ('G04','Baseline improvement','Beat both a simple rating and the authorized no-vig market baseline on proper scores.'),
    ('G05','Effective sample','At least 500 settled paper tickets AND 100 independent game/week clusters; neither alone proves skill.'),
    ('G06','Uncertainty','Predeclared 95% cluster-bootstrap lower bounds exceed zero for CLV and proper-score improvement.'),
    ('G07','Multiplicity','Holm-adjusted p-values <= .05 across every registered strategy and tuning trial.'),
    ('G08','Calibration','Out-of-sample calibration slope in [.9,1.1], reliability bins disclosed, no material subgroup miscalibration.'),
    ('G09','CLV and execution','Positive de-vig CLV at executable prices, with limits, latency, voids, pushes and fees modeled.'),
    ('G10','Joint probability','Parlays/prop combos use trained joint distributions and book-specific settlement; no naive same-game multiplication.'),
    ('G11','Stability','Positive held-out performance across seasons, team clusters and price regimes; no single-cluster domination.'),
    ('G12','Risk and safety','Paper drawdown/exposure within frozen caps; real-money execution remains disabled.'),
]


def evaluate_gates(evidence, metrics, *, family_pvalues=None, family_index=None, market='single'):
    results=[]
    def add(gid,passed,detail): results.append({'id':gid,'passed':bool(passed) if passed is not None else False,'detail':detail})
    for i in range(5):
        key=f'g{i:02d}'; add(f'G{i:02d}',evidence.get(key) is True,'Explicit true evidence required; missing/unknown fails.')
    n=metrics.get('settled_tickets'); clusters=metrics.get('independent_clusters')
    add('G05',isinstance(n,(int,float)) and n>=500 and isinstance(clusters,(int,float)) and clusters>=100,'Minimum policy counts; not a guarantee of skill.')
    clv=metrics.get('clv_lower_95'); skill=metrics.get('proper_score_improvement_lower_95')
    add('G06',clv is not None and clv>0 and skill is not None and skill>0,'Both cluster-bootstrap lower bounds must be positive.')
    if family_pvalues is None or family_index is None or not 0<=family_index<len(family_pvalues):
        add('G07',False,'Complete trial family and registered index required.')
    else:
        try: add('G07',holm_adjust(family_pvalues)[family_index]<=.05,'Holm correction over the complete family.')
        except ValueError: add('G07',False,'Invalid p-values.')
    slope=metrics.get('calibration_slope'); add('G08',slope is not None and .9<=slope<=1.1 and evidence.get('reliability_reviewed') is True,'Slope plus reviewed reliability evidence required.')
    add('G09',evidence.get('g09') is True and clv is not None and clv>0 and metrics.get('net_roi_lower_95') is not None and metrics['net_roi_lower_95']>0,'Executable CLV and net paper ROI lower bounds required.')
    add('G10',market=='single' or evidence.get('g10') is True,'Combo joint-model/settlement evidence required.')
    add('G11',evidence.get('g11') is True,'Stability review must be explicitly passed.')
    dd=metrics.get('max_drawdown_units'); cap=metrics.get('drawdown_cap_units')
    add('G12',evidence.get('paper_only') is True and dd is not None and cap is not None and 0<=dd<=cap,'Paper-only and frozen drawdown cap required.')
    return {'market':market,'eligible':all(g['passed'] for g in results),'status':'eligible_paper_only' if all(g['passed'] for g in results) else 'not_eligible','gates':results,'real_money_enabled':False}


def leaderboard(strategies):
    boards={m:[] for m in ('single','parlay','player_prop_combo')}
    for s in strategies:
        market=s.get('market'); result=s.get('validation',{})
        if market not in boards or not result.get('eligible') or not result.get('real_money_enabled') is False: continue
        m=s.get('metrics',{}); required=['clv_mean','proper_score_improvement_mean','net_roi_mean']
        if any(m.get(k) is None for k in required): continue
        boards[market].append({'id':s.get('id'),'name':s.get('name'),'metrics':m,'reward':'virtual_badge_only','score':m['clv_mean']+m['proper_score_improvement_mean']})
    for market,rows in boards.items():
        rows.sort(key=lambda r:(-r['score'],r['id']))
        for i,r in enumerate(rows,1): r['rank']=i; r['badge']={1:'Gold',2:'Silver',3:'Bronze'}.get(i,'Finalist')
    return {'boards':boards,'policy':'Only gate-eligible paper strategies rank. Rewards are virtual; no money or betting credits.','empty_reason':'No eligible historical market/strategy evidence has been supplied.' if not any(boards.values()) else None}
