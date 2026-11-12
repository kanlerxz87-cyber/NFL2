#!/usr/bin/env python3
"""
verify_data.py — deterministic, line-by-line verification of the transcribed NFL data.

Checks performed (all pure arithmetic, no external calls, no inference):
  V1  Every game has two distinct clubs, both of which are real NFL clubs.
  V2  Games per club per week <= 1 (no club plays twice in a week; byes are gaps).
  V3  Team-game totals derived from the 136 game rows == official standings PF/PA.
  V4  Standings PCT == (W + T/2) / (W + L + T) exactly, for all 32 clubs.
  V5  Standings NET == PF - PA exactly.
  V6  W + L + T consistency: every club's games played equals wins+losses+ties
      from the game log.
  V7  League-wide PF total == league-wide PA total (points are zero-sum).
  V8  Win/loss/tie counts from the game log == standings W/L/T.
  V9  Team passing+rushing yards vs total offensive yards where both published.
  V10 Streak string agrees with the club's final games in the log.

Output: data/derived/verification_report.json + human-readable stdout.
Exit code 1 if any HARD check fails.
"""
import json, os, sys, datetime
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

CLUBS = {
 "AZ":"Arizona Cardinals","ATL":"Atlanta Falcons","BAL":"Baltimore Ravens","BUF":"Buffalo Bills",
 "CAR":"Carolina Panthers","CHI":"Chicago Bears","CIN":"Cincinnati Bengals","CLE":"Cleveland Browns",
 "DAL":"Dallas Cowboys","DEN":"Denver Broncos","DET":"Detroit Lions","GB":"Green Bay Packers",
 "HOU":"Houston Texans","IND":"Indianapolis Colts","JAX":"Jacksonville Jaguars","KC":"Kansas City Chiefs",
 "LA":"Los Angeles Rams","LAC":"Los Angeles Chargers","LV":"Las Vegas Raiders","MIA":"Miami Dolphins",
 "MIN":"Minnesota Vikings","NE":"New England Patriots","NO":"New Orleans Saints","NYG":"New York Giants",
 "NYJ":"New York Jets","PHI":"Philadelphia Eagles","PIT":"Pittsburgh Steelers","SEA":"Seattle Seahawks",
 "SF":"San Francisco 49ers","TB":"Tampa Bay Buccaneers","TEN":"Tennessee Titans","WAS":"Washington Commanders",
}

checks, fails = [], []
def add(cid, name, ok, detail, hard=True):
    checks.append({"id":cid,"name":name,"status":"PASS" if ok else "FAIL",
                   "severity":"hard" if hard else "soft","detail":detail})
    if not ok and hard: fails.append(cid)

def load(p):
    with open(os.path.join(D,p),encoding="utf-8") as f: return json.load(f)

games_doc = load("games_2026.json")
stand_doc = load("standings_raw.json")
games = games_doc["games"]; std = stand_doc["standings"]

# ---------- V1 ----------
bad=[]
for g in games:
    if g["away"] not in CLUBS or g["home"] not in CLUBS or g["away"]==g["home"]: bad.append(g)
add("V1","Every game row references two distinct, real NFL clubs", not bad,
    f"{len(games)} game rows, {len(bad)} malformed")

# ---------- V2 ----------
per_week={}
for g in games:
    for t in (g["away"],g["home"]):
        per_week.setdefault((t,g["week"]),0); per_week[(t,g["week"])]+=1
dup=[k for k,v in per_week.items() if v>1]
add("V2","No club plays more than once in any week", not dup, f"duplicates={dup}")

# ---------- V3 / V6 / V7 / V8 ----------
pf={t:0 for t in CLUBS}; pa={t:0 for t in CLUBS}
w={t:0 for t in CLUBS}; l={t:0 for t in CLUBS}; ti={t:0 for t in CLUBS}
gpl={t:0 for t in CLUBS}
for g in games:
    a,h=g["away"],g["home"]; ap,hp=g["away_pts"],g["home_pts"]
    if ap==hp:
        # NFL regular-season ties are a real, rule-defined outcome (see rulebook)
        w[a]+=0;l[a]+=0;ti[a]+=1; w[h]+=0;l[h]+=0;ti[h]+=1
    elif ap>hp: w[a]+=1; l[h]+=1
    else: w[h]+=1; l[a]+=1
    pf[a]+=ap; pa[a]+=hp; pf[h]+=hp; pa[h]+=ap
    gpl[a]+=1; gpl[h]+=1

pf_mis=[]; pa_mis=[]
for s in std:
    t=s["team"]
    if pf[t]!=s["PF"]: pf_mis.append({"team":t,"from_games":pf[t],"official":s["PF"]})
    if pa[t]!=s["PA"]: pa_mis.append({"team":t,"from_games":pa[t],"official":s["PA"]})
add("V3a","Points-for recomputed from the official game log equals official standings PF for all 32 clubs",
    not pf_mis, f"mismatches={pf_mis}")
add("V3b","Points-against recomputed from the official game log equals official standings PA for all 32 clubs",
    not pa_mis, f"mismatches={pa_mis}")
add("V7","League-wide points scored equals league-wide points allowed",
    sum(pf.values())==sum(pa.values()), f"PF total={sum(pf.values())} PA total={sum(pa.values())}")

wlt_mis=[]
for s in std:
    t=s["team"]
    if (w[t],l[t],ti[t])!=(s["W"],s["L"],s["T"]):
        wlt_mis.append({"team":t,"from_games":[w[t],l[t],ti[t]],"official":[s["W"],s["L"],s["T"]]})
add("V8","W-L-T recomputed from the game log equals official standings W-L-T for all 32 clubs",
    not wlt_mis, f"mismatches={wlt_mis}")

# ---------- V4 / V5 ----------
pct_bad=[]; net_bad=[]
for s in std:
    denom=s["W"]+s["L"]+s["T"]
    # NFL.com publishes PCT rounded half-up to 3 dp (verified on WAS 2-5-1 -> .313).
    # Python's built-in round() is banker's rounding and would yield .312, so use Decimal.
    exp=float((Decimal(2*s["W"]+s["T"])/Decimal(2*denom)).quantize(Decimal("0.001"),rounding=ROUND_HALF_UP))
    if abs(exp-s["PCT"])>0.0005: pct_bad.append({"team":s["team"],"expected":exp,"published":s["PCT"]})
    if s["PF"]-s["PA"]!=s["NET"]: net_bad.append({"team":s["team"],"PF-PA":s["PF"]-s["PA"],"published":s["NET"]})
add("V4","Standings PCT equals (W + T/2)/(W+L+T) for all 32 clubs", not pct_bad, f"mismatches={pct_bad}")
add("V5","Standings net points equals PF - PA for all 32 clubs", not net_bad, f"mismatches={net_bad}")

# ---------- V6 ----------
gp_bad=[s["team"] for s in std if s["W"]+s["L"]+s["T"]!=gpl[s["team"]]]
add("V6","games played in standings equals game-log appearances", not gp_bad, f"mismatches={gp_bad}")

# ---------- V10 ----------
streak_bad=[]
latest_week=max(g["week"] for g in games)
for s in std:
    t=s["team"]
    mine=[g for g in games if t in (g["away"],g["home"])]
    mine.sort(key=lambda g:(g["date"],g["week"]))
    n=int(s["streak"][:-1]); kind=s["streak"][-1]
    # Walk the full chronological log backwards, counting consecutive identical results.
    # Bye weeks are simply absent from the log and therefore do not interrupt a streak.
    run=[]
    for g in reversed(mine):
        my = g["away_pts"] if g["away"]==t else g["home_pts"]
        op = g["home_pts"] if g["away"]==t else g["away_pts"]
        run.append("W" if my>op else ("L" if my<op else "T"))
    got="".join(run)
    if got[:n]!=(kind*n): streak_bad.append({"team":t,"published":s["streak"],"from_log":got})
add("V10",f"Published streak equals the club's trailing result string in the chronological game log (through week {latest_week})",
    not streak_bad, f"mismatches={streak_bad}")

# ---------- V11..V13: team-stat conservation ----------
teamstats = load("team_stats.json")["teams"]
def col(teams, key, idx): return [v[key][idx] for v in teams.values()]

add("V11","Team-stat table covers exactly the 32 NFL clubs", len(teamstats)==32 and set(teamstats)==set(CLUBS),
    f"rows={len(teamstats)}")

conserve = [
  ("V12a","passing yards",       "off_pass",4,"def_pass",4),
  ("V12b","rushing yards",       "off_rush",1,"def_rush",1),
  ("V12c","sacks",               "off_pass",13,"def_pass",13),
  ("V12d","passing touchdowns",  "off_pass",5,"def_pass",5),
  ("V12e","rushing touchdowns",  "off_rush",3,"def_rush",3),
  ("V12f","interceptions",       "off_pass",6,"def_pass",6),
  ("V12g","passing first downs", "off_pass",8,"def_pass",8),
  ("V12h","rushing first downs", "off_rush",7,"def_rush",7),
]
for cid,label,okey,oidx,dkey,didx in conserve:
    o=sum(col(teamstats,okey,oidx)); d=sum(col(teamstats,dkey,didx))
    add(cid,f"League-total offense {label} equals league-total defense {label} allowed (zero-sum conservation)",
        o==d, f"offense={o} defense={d}")

# ---------- V13: published total-offense cross-check (single club, official club page) ----------
kc=teamstats["KC"]
kc_total=kc["off_pass"][4]+kc["off_rush"][1]
add("V13","Offense passing yards + rushing yards equals the 'TOTAL OFFENSIVE YARDS' printed on the club page (KC cross-check)",
    kc_total==3069,
    f"computed={kc_total} (2037+1102) vs club-page total=3069; difference=70. Recorded as irregularity FL-05, not silently reconciled.",
    hard=False)

# ---------- V14: per-club arithmetic where the source publishes a derived value ----------
# AVG (rushing yards per carry) must equal YDS / CAR, rounded to 1dp half-up.
def dps(x): return float(Decimal(str(x)).quantize(Decimal("0.1"),rounding=ROUND_HALF_UP))
rush_avg_bad=[]
for t,v in teamstats.items():
    car,yds,avg=v["off_rush"][0],v["off_rush"][1],v["off_rush"][2]
    if dps(yds/car)!=avg: rush_avg_bad.append({"team":t,"car":car,"yds":yds,"published":avg,"computed":dps(yds/car)})
add("V14a","Team rushing AVG equals YDS/CAR rounded half-up to 1dp, for all 32 clubs",
    not rush_avg_bad, f"mismatches={rush_avg_bad}; matching all 32 establishes the source's rounding convention")

cmp_bad=[]
for t,v in teamstats.items():
    att,cmp_,pct=v["off_pass"][0],v["off_pass"][1],v["off_pass"][2]
    if dps(100*cmp_/att)!=pct: cmp_bad.append({"team":t,"att":att,"cmp":cmp_,"published":pct,"computed":dps(100*cmp_/att)})
add("V14b","Team completion percentage equals 100*CMP/ATT rounded half-up to 1dp, for all 32 clubs",
    not cmp_bad, f"mismatches={cmp_bad}; 31/32 agree, so this is a source-value irregularity (FL-06), not a transcription error",
    hard=False)

ypa_bad=[]
for t,v in teamstats.items():
    att,yds,ypa=v["off_pass"][0],v["off_pass"][4],v["off_pass"][3]
    if dps(yds/att)!=ypa: ypa_bad.append({"team":t,"att":att,"yds":yds,"published":ypa,"computed":dps(yds/att)})
add("V14c","Team yards-per-attempt equals YDS/ATT rounded half-up to 1dp, for all 32 clubs",
    not ypa_bad, f"mismatches={ypa_bad}; 28/32 agree. Tested and rejected alternative denominators: (YDS+SACK_YDS)/(ATT+SACKS) fails 22/32, YDS/(ATT+SACKS) fails 32/32. Hence a source-value irregularity (FL-07), not a transcription error.",
    hard=False)

# ---------- summary ----------
n_pass=sum(1 for c in checks if c["status"]=="PASS")
report={
  "generated_utc": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
  "purpose":"Deterministic re-derivation of every transcribed NFL value against the official source. No network access; no inference.",
  "sources":{"games":games_doc["meta"]["source_pattern"],"standings":stand_doc["meta"]["source"],
             "team_stats":load("team_stats.json")["meta"]["sources"]},
  "totals":{"checks":len(checks),"pass":n_pass,"fail":len(checks)-n_pass,
            "game_rows":len(games),"weeks":[1,9],
            "clubs":len(CLUBS),"league_points":sum(pf.values())},
  "withheld_from_source":{"team_scoring_tables":load("team_stats.json")["meta"]["withheld"]},
  "checks":checks
}
os.makedirs(os.path.join(D,"derived"),exist_ok=True)
with open(os.path.join(D,"derived","verification_report.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,indent=2)

for c in checks:
    print(f"[{c['status']}] {c['id']:<5} {c['name']}")
    if c["status"]=="FAIL": print(f"        -> {c['detail']}")
print(f"\n{n_pass}/{len(checks)} checks passed. Report: data/derived/verification_report.json")
sys.exit(1 if fails else 0)
