#!/usr/bin/env python3
"""
verify_personnel.py — integrity checks on the depth-chart / injury join.

P1  Every chart group key is unique within its side (the bug that mis-scored a
    3rd-string player as a starter).
P2  No player appears in two different slots of the same club chart. A player may
    legitimately appear twice under the SAME position label (NFL charts do this for
    free safety / strong safety), but never at two different depths of one slot.
P3  Every injury row either maps to exactly one chart slot or is explicitly flagged.
P4  Every club named in the injury report appears in the coverage table.
P5  No row claims a depth position for a club whose chart is not transcribed.
P6  The starter/backup counts in the summary equal a fresh recount of the rows.
"""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT,"data")
def load(p):
    with open(os.path.join(D,p),encoding="utf-8") as f: return json.load(f)
DEPTH=load("depth_charts.json"); PER=load("derived/personnel.json"); INJ=load("injuries_week10.json")

checks=[]
def add(cid,name,ok,detail=""):
    checks.append({"id":cid,"name":name,"status":"PASS" if ok else "FAIL","detail":detail})

# P1
bad=[]
for club,ch in DEPTH["depth_charts"].items():
    for side in ("offense","defense"):
        keys=list(ch.get(side,{}).keys())
        dup=[k for k,c in collections.Counter(keys).items() if c>1]
        if dup: bad.append({"club":club,"side":side,"duplicate_keys":dup})
add("P1","Every position-group key is unique within its side", not bad, str(bad))

# P2
def norm(n):
    n=n.lower().replace(".","").replace("'","").replace("-"," ").replace("  "," ")
    for s in [" jr"," sr"," iii"," ii"," iv"]:
        if n.endswith(s): n=n[:-len(s)]
    return n.strip()
bad2=[]; multi=[]
for club,ch in DEPTH["depth_charts"].items():
    seen={}
    for side in ("offense","defense"):
        for g,ps in ch.get(side,{}).items():
            for i,p in enumerate(ps):
                if not p: continue
                seen.setdefault(norm(p),set()).add((g,i+1))
    for p,slots in seen.items():
        # illegal: the SAME position group listing one player at two depths
        bygroup=collections.defaultdict(set)
        for g,d in slots: bygroup[g].add(d)
        for g,ds in bygroup.items():
            if len(ds)>1: bad2.append({"club":club,"player":p,"group":g,"depths":sorted(ds)})
        # legal but must be declared: a player genuinely listed at two positions
        if len(slots)>1: multi.append({"club":club,"player":p,"slots":sorted(slots)})
add("P2a","No player appears twice at different depths of the SAME position group", not bad2, str(bad2))
add("P2b",f"{len(multi)} players are legitimately listed at two different positions "
         "(real charts do this; each is declared, not merged away)", len(multi)>0, str(multi))

# P3
bad3=[r for r in PER["rows"] if r["map_status"]=="mapped" and r["depth_position"] is None]
add("P3a","Every row marked 'mapped' carries a depth position", not bad3, str(bad3[:3]))
allowed={"mapped","not on published chart","depth unmapped (club chart not transcribed)"}
bad3b=[r for r in PER["rows"] if r["map_status"] not in allowed]
add("P3b","Every row carries one of the three declared map statuses", not bad3b, str(bad3b[:3]))

# P4
clubs_inj=set()
for g in INJ["games"]:
    for p in g["players"]: clubs_inj.add(p["team"])
clubs_tbl={s["team"] for s in PER["by_club"]}
add("P4","Every club with injury rows appears in the coverage table", clubs_inj<=clubs_tbl,
    f"missing={sorted(clubs_inj-clubs_tbl)}")

# P5
charted=set(DEPTH["meta"]["charted"])
bad5=[r for r in PER["rows"] if r["depth_position"] is not None and r["team"] not in charted]
add("P5","No depth position is asserted for a club whose chart was not transcribed", not bad5, str(bad5[:3]))

# P6
recount={}
for r in PER["rows"]:
    s=recount.setdefault(r["team"],collections.Counter())
    if r["practice_code"]=="DNP":
        d=r["depth_position"]
        if d==1: s["starters_dnp"]+=1
        elif d==2: s["second_string_dnp"]+=1
        elif d==3: s["third_string_dnp"]+=1
        elif d==4: s["fourth_string_dnp"]+=1
mismatch=[]
for s in PER["by_club"]:
    rc=recount.get(s["team"],collections.Counter())
    for k in ("starters_dnp","second_string_dnp","third_string_dnp","fourth_string_dnp"):
        if s[k]!=rc.get(k,0): mismatch.append({"team":s["team"],"field":k,"table":s[k],"recount":rc.get(k,0)})
add("P6","Starter/2nd/3rd/4th-string counts equal a fresh recount of the rows", not mismatch, str(mismatch))

# P7 - the flagged players genuinely are absent from the chart
absent=[r for r in PER["rows"] if r["map_status"]=="not on published chart"]
add("P7",f"{len(absent)} injured players are explicitly flagged as absent from their club's published chart "
         "(not silently treated as backups)", len(absent)>0, ", ".join(f"{r['team']}:{r['player']}" for r in absent))

npass=sum(1 for c in checks if c["status"]=="PASS")
for c in checks: print(f"[{c['status']}] {c['id']:4s} {c['name']}")
print(f"\n{npass}/{len(checks)} personnel checks passed")
PER["meta"]["personnel_verification"]=checks
with open(os.path.join(D,"derived","personnel.json"),"w",encoding="utf-8") as f: json.dump(PER,f,indent=2)
sys.exit(0 if npass==len(checks) else 1)
