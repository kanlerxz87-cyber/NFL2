"""Small, auditable statistical primitives; no empirical NFL values supplied."""
from __future__ import annotations
import math, random
from collections import defaultdict


def mean(xs):
    xs=list(xs)
    if not xs: raise ValueError('Empty sample')
    return sum(xs)/len(xs)


def pearson(x, y):
    x,y=list(x),list(y)
    if len(x)!=len(y) or len(x)<3: raise ValueError('Need at least three paired observations')
    mx,my=mean(x),mean(y)
    dx=[a-mx for a in x]; dy=[b-my for b in y]
    sx=sum(a*a for a in dx); sy=sum(b*b for b in dy)
    if sx==0 or sy==0: return None
    return max(-1.0,min(1.0,sum(a*b for a,b in zip(dx,dy))/math.sqrt(sx*sy)))


def phi_binary(x,y):
    x,y=list(x),list(y)
    if len(x)!=len(y) or not x or any(v not in (0,1,False,True) for v in x+y): raise ValueError('Binary paired samples required')
    return pearson([int(v) for v in x],[int(v) for v in y])


def joint_metrics(a,b):
    a,b=list(a),list(b)
    if len(a)!=len(b) or not a or any(v not in (0,1,False,True) for v in a+b): raise ValueError('Binary paired samples required')
    n=len(a); pa=mean(a); pb=mean(b); pab=sum(int(x) and int(y) for x,y in zip(a,b))/n
    return {'n':n,'p_a':pa,'p_b':pb,'p_joint':pab,'p_b_given_a':pab/pa if pa else None,
            'independence_product':pa*pb,'joint_lift':pab/(pa*pb) if pa and pb else None,'phi':phi_binary(a,b),
            'warning':'Association is not causation or a tradable edge; estimate on training data only.'}


def cluster_bootstrap_mean(values, clusters, *, iterations=2000, seed=20261112, confidence=0.95):
    """Resample entire games/weeks, not correlated individual legs."""
    values,clusters=list(values),list(clusters)
    if len(values)!=len(clusters) or not values: raise ValueError('Paired values and cluster IDs required')
    if iterations<100 or not 0<confidence<1: raise ValueError('Invalid bootstrap settings')
    groups=defaultdict(list)
    for v,c in zip(values,clusters): groups[str(c)].append(float(v))
    keys=sorted(groups)
    if len(keys)<3: return {'estimate':mean(values),'lower':None,'upper':None,'clusters':len(keys),'iterations':iterations,'seed':seed,'warning':'Fewer than three clusters: interval withheld'}
    rng=random.Random(seed); sums=[(sum(groups[k]),len(groups[k])) for k in keys]; estimates=[]
    for _ in range(iterations):
        total=n=0
        for _ in keys:
            s,m=sums[rng.randrange(len(keys))]; total+=s; n+=m
        estimates.append(total/n)
    estimates.sort(); alpha=(1-confidence)/2
    def quantile(p):
        pos=(len(estimates)-1)*p; lo=int(pos); hi=min(lo+1,len(estimates)-1)
        return estimates[lo]+(estimates[hi]-estimates[lo])*(pos-lo)
    return {'estimate':mean(values),'lower':quantile(alpha),'upper':quantile(1-alpha),'clusters':len(keys),'iterations':iterations,'seed':seed,'confidence':confidence}


def cluster_bootstrap_correlation(x,y,clusters,*,iterations=2000,seed=20261112,confidence=0.95):
    """Percentile interval for Pearson r, resampling whole game/week clusters."""
    x,y,clusters=list(x),list(y),list(clusters)
    if not x or len(x)!=len(y) or len(x)!=len(clusters): raise ValueError('Paired observations and clusters required')
    estimate=pearson(x,y); groups=defaultdict(list)
    for a,b,c in zip(x,y,clusters): groups[str(c)].append((float(a),float(b)))
    keys=sorted(groups)
    if len(keys)<3 or estimate is None: return {'estimate':estimate,'lower':None,'upper':None,'clusters':len(keys),'iterations':iterations,'seed':seed,'warning':'Interval withheld: insufficient clusters or zero variance'}
    rng=random.Random(seed); estimates=[]
    for _ in range(iterations):
        sx=[]; sy=[]
        for _ in keys:
            for a,b in groups[keys[rng.randrange(len(keys))]]: sx.append(a); sy.append(b)
        r=pearson(sx,sy)
        if r is not None: estimates.append(r)
    if len(estimates)<iterations*.95: return {'estimate':estimate,'lower':None,'upper':None,'clusters':len(keys),'iterations':iterations,'seed':seed,'warning':'Too many degenerate resamples'}
    estimates.sort(); alpha=(1-confidence)/2
    def q(p):
        pos=(len(estimates)-1)*p; lo=int(pos); hi=min(lo+1,len(estimates)-1)
        return estimates[lo]+(estimates[hi]-estimates[lo])*(pos-lo)
    return {'estimate':estimate,'lower':q(alpha),'upper':q(1-alpha),'clusters':len(keys),'iterations':iterations,'seed':seed,'confidence':confidence}


def holm_adjust(pvalues):
    """Family-wise error correction over the COMPLETE pre-registered family."""
    ps=list(pvalues)
    if any(not math.isfinite(p) or not 0<=p<=1 for p in ps): raise ValueError('Invalid p-value')
    order=sorted(range(len(ps)),key=lambda i:ps[i]); out=[0.0]*len(ps); running=0.0
    for rank,i in enumerate(order):
        running=max(running,(len(ps)-rank)*ps[i]); out[i]=min(1.0,running)
    return out


def log_loss(probs,outcomes):
    probs,outcomes=list(probs),list(outcomes)
    if len(probs)!=len(outcomes) or not probs or any(not 0<p<1 for p in probs) or any(o not in (0,1) for o in outcomes): raise ValueError('Invalid binary scores')
    return -mean(o*math.log(p)+(1-o)*math.log(1-p) for p,o in zip(probs,outcomes))


def brier(probs,outcomes):
    probs,outcomes=list(probs),list(outcomes)
    if len(probs)!=len(outcomes) or not probs or any(not 0<=p<=1 for p in probs) or any(o not in (0,1) for o in outcomes): raise ValueError('Invalid binary scores')
    return mean((p-o)**2 for p,o in zip(probs,outcomes))


def max_drawdown(returns):
    equity=peak=drawdown=0.0
    for r in returns:
        equity+=r; peak=max(peak,equity); drawdown=max(drawdown,peak-equity)
    return drawdown
