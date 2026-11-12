"""Point-in-time ridge baseline for originating research lines.

Only completed, officially sourced games may enter fit(). The target game is
never included. Coefficients are original model outputs, not NFL facts. No
injury, weather or lineup adjustment is invented: unavailable adjustments are
exactly zero and disclosed. This is not a validated betting model.
"""
from __future__ import annotations
from dataclasses import dataclass
from .statistics import mean


def _solve(a,b):
    n=len(b); m=[row[:]+[b[i]] for i,row in enumerate(a)]
    for col in range(n):
        pivot=max(range(col,n),key=lambda r:abs(m[r][col]))
        if abs(m[pivot][col])<1e-10: raise ValueError('Singular model matrix')
        m[col],m[pivot]=m[pivot],m[col]
        div=m[col][col]; m[col]=[v/div for v in m[col]]
        for r in range(n):
            if r==col: continue
            factor=m[r][col]; m[r]=[x-factor*y for x,y in zip(m[r],m[col])]
    return [m[i][-1] for i in range(n)]


def _quantile(xs,p):
    xs=sorted(xs); pos=(len(xs)-1)*p; lo=int(pos); hi=min(lo+1,len(xs)-1)
    return xs[lo]+(xs[hi]-xs[lo])*(pos-lo)


@dataclass(frozen=True)
class Game:
    game_id: str
    season: int
    week: int
    home: str
    away: str
    home_score: int
    away_score: int
    neutral: bool = False
    source_url: str = ''
    available_at: str = ''


class RidgeBaseline:
    def __init__(self, ridge=20.0, min_games=80):
        if ridge<=0 or min_games<1: raise ValueError('Invalid regularization/sample settings')
        self.ridge=ridge; self.min_games=min_games; self.teams=[]; self.margin=None; self.total=None; self.games=[]

    def fit(self,games,teams):
        games=list(games); self.teams=sorted(set(teams))
        if len(games)<self.min_games: raise ValueError(f'Need at least {self.min_games} completed source-backed games')
        if len({g.game_id for g in games})!=len(games): raise ValueError('Duplicate game IDs')
        idx={t:i+1 for i,t in enumerate(self.teams)}; n=len(self.teams)+1
        xm=[]; xt=[]; ym=[]; yt=[]
        for g in games:
            if g.home not in idx or g.away not in idx or g.home==g.away: raise ValueError('Invalid team identities')
            if not g.source_url.startswith('https://www.nfl.com/'): raise ValueError('Official NFL game source required')
            if min(g.home_score,g.away_score)<0: raise ValueError('Invalid score')
            rm=[0.0]*n; rt=[0.0]*n; rm[0]=0.0 if g.neutral else 1.0
            rm[idx[g.home]]=1; rm[idx[g.away]]=-1
            rt[0]=1; rt[idx[g.home]]=1; rt[idx[g.away]]=1
            xm.append(rm); xt.append(rt); ym.append(g.home_score-g.away_score); yt.append(g.home_score+g.away_score)
        def fit_matrix(x,y,penalize_intercept):
            k=len(x[0]); a=[[sum(r[i]*r[j] for r in x) for j in range(k)] for i in range(k)]
            b=[sum(r[i]*v for r,v in zip(x,y)) for i in range(k)]
            for i in range(k):
                if i or penalize_intercept: a[i][i]+=self.ridge
            return _solve(a,b)
        self.margin=fit_matrix(xm,ym,False); self.total=fit_matrix(xt,yt,True); self.games=games
        return self

    def predict(self,home,away,*,neutral=False,decision_at=None):
        if self.margin is None: raise ValueError('Model has not been fitted')
        if decision_at and any(g.available_at and g.available_at>decision_at for g in self.games): raise ValueError('Future information leakage detected')
        i=self.teams.index(home)+1; j=self.teams.index(away)+1
        margin=self.margin[0]*(0 if neutral else 1)+self.margin[i]-self.margin[j]
        total=self.total[0]+self.total[i]+self.total[j]
        mr=[g.home_score-g.away_score-(self.margin[0]*(0 if g.neutral else 1)+self.margin[self.teams.index(g.home)+1]-self.margin[self.teams.index(g.away)+1]) for g in self.games]
        tr=[g.home_score+g.away_score-(self.total[0]+self.total[self.teams.index(g.home)+1]+self.total[self.teams.index(g.away)+1]) for g in self.games]
        margins=[margin+r for r in mr]; totals=[total+r for r in tr]
        pwin=sum(m>0 for m in margins)/len(margins); ppush=sum(m==0 for m in margins)/len(margins)
        return {'model':'ridge-margin-total-v0','status':'RESEARCH ONLY — NOT VALIDATED','home':home,'away':away,
                'expected_home_margin':margin,'expected_total':total,'fair_home_spread':-_quantile(margins,.5),
                'fair_total':_quantile(totals,.5),'home_win_probability':pwin,'home_loss_probability':sum(m<0 for m in margins)/len(margins),'tie_probability':ppush,
                'training_games':len(self.games),'ridge_penalty':self.ridge,'neutral_site':neutral,
                'adjustments':{'injuries':0,'lineups':0,'weather':0,'rest_travel':0},'adjustments_note':'Zero means unavailable, not no effect.',
                'limitations':['In-sample residual distribution; not out-of-sample calibration.','No market odds or execution feasibility.','No player-prop distribution or same-game joint model.','Regularization is a predeclared research setting, not an optimized profit claim.']}
