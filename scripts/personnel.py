#!/usr/bin/env python3
"""
personnel.py — join the official injury report to club-published depth charts.

The join answers one question the injury report cannot answer on its own:
    "is the club missing a STARTING player, or a 2nd/3rd/4th-string player?"

Rules (no inference):
  * depth_position comes ONLY from the club's published depth chart column index.
  * A player missing from the chart gets depth_position = null and unit_status =
    "unknown" — never "backup", never "starter".
  * A player listed on the chart but absent from the injury report is not a deficiency.
  * Practice status is published verbatim. Game status is published verbatim; where
    NFL.com prints it blank we carry null and say so.
  * Charts exist for 4 clubs only. The other clubs' rows are reported as
    depth-unmapped so the gap is visible rather than silently averaging in.
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data"); OUT = os.path.join(D, "derived")
os.makedirs(OUT, exist_ok=True)
def load(p):
    with open(os.path.join(D,p), encoding="utf-8") as f: return json.load(f)

INJ  = load("injuries_week10.json")
DEPTH= load("depth_charts.json")
CHARTS = DEPTH["depth_charts"]

def normalise(name):
    n = name.lower()
    n = n.replace(".", "").replace("'", "").replace("-", " ").replace("  "," ")
    for suf in [" jr", " sr", " iii", " ii", " iv", " v"]:
        if n.endswith(suf): n = n[: -len(suf)]
    return n.strip()

# index chart: club -> normalised name -> [ {group, slot, depth} ]
CHART_INDEX = {}
for club, chart in CHARTS.items():
    idx = {}
    for side in ("offense","defense"):
        for group, players in chart.get(side, {}).items():
            for i, p in enumerate(players):
                if not p: continue
                idx.setdefault(normalise(p), []).append({"group":group,"side":side,"depth":i+1})
    CHART_INDEX[club] = idx

def unit_of(group):
    g = group.upper()
    if g in ("QB","RB","FB","WR","WR2","WR3","TE","LT","LG","C","RG","RT"):
        return "offense"
    return "defense"

rows = []
for game in INJ["games"]:
    for p in game["players"]:
        club = p["team"]
        key = normalise(p["player"])
        entries = CHART_INDEX.get(club, {}).get(key)
        if club not in CHARTS:
            depth, group, side, status = None, None, None, "depth unmapped (club chart not transcribed)"
        elif entries:
            e = min(entries, key=lambda x: x["depth"])
            depth, group, side = e["depth"], e["group"], unit_of(e["group"])
            status = "mapped"
        else:
            depth, group, side, status = None, None, None, "not on published chart"
        # normalise practice status
        pr = (p["practice"] or "").strip()
        practice_code = {"Did Not Participate In Practice":"DNP",
                         "Limited Participation in Practice":"LP",
                         "Full Participation in Practice":"FP"}.get(pr, pr or None)
        rows.append({
            "game": f'{game["away"]} at {game["home"]}',
            "kickoff_et": game["kickoff_et"],
            "team": club, "player": p["player"], "pos": p["pos"],
            "injury": p["injury"], "practice": pr or None, "practice_code": practice_code,
            "game_status": p["status"],
            "depth_position": depth, "depth_group": group, "unit": side,
            "map_status": status,
            "all_chart_slots": [f'{x["group"]} ({x["depth"]}st/nd/rd/th)' for x in (entries or [])],
            "multi_slot": bool(entries and len(entries) > 1),
        })

# ---- per-club summary -----------------------------------------------------
summary = {}
for r in rows:
    s = summary.setdefault(r["team"], {
        "team": r["team"], "listed": 0, "dnp": 0, "lp": 0, "fp": 0,
        "game_status_out": 0, "game_status_questionable": 0,
        "starters_dnp": 0, "starters_out": 0,
        "second_string_dnp": 0, "third_string_dnp": 0, "fourth_string_dnp": 0,
        "unmapped": 0, "charted": r["team"] in CHARTS})
    s["listed"] += 1
    if r["practice_code"] == "DNP": s["dnp"] += 1
    if r["practice_code"] == "LP":  s["lp"] += 1
    if r["practice_code"] == "FP":  s["fp"] += 1
    if r["game_status"] == "Out": s["game_status_out"] += 1
    if r["game_status"] == "Questionable": s["game_status_questionable"] += 1
    if r["depth_position"] is None: s["unmapped"] += 1
    if r["practice_code"] == "DNP":
        if r["depth_position"] == 1: s["starters_dnp"] += 1
        elif r["depth_position"] == 2: s["second_string_dnp"] += 1
        elif r["depth_position"] == 3: s["third_string_dnp"] += 1
        elif r["depth_position"] == 4: s["fourth_string_dnp"] += 1
    if r["game_status"] == "Out" and r["depth_position"] == 1:
        s["starters_out"] += 1

# deficiency index: an unweighted count. Deliberately NOT a points estimate,
# because no published mapping from depth to points exists.
for t, s in summary.items():
    s["deficiency_index"] = s["starters_dnp"]*3 + s["second_string_dnp"]*2 + \
                            s["third_string_dnp"] + s["fourth_string_dnp"]
    s["index_basis"] = "starters DNP x3 + 2nd string x2 + 3rd x1 + 4th x1 (a transparency weight, NOT an empirical points value)"

out = {
 "meta": {
   "generated_utc": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
   "sources": {"injury":INJ["meta"]["source_injury"],"status":INJ["meta"]["source_status"],
               "depth_charts":DEPTH["meta"]["sources"]},
   "row_count": len(rows),
   "clubs_with_rows": len(summary),
   "clubs_charted": DEPTH["meta"]["charted"],
   "joins_to_published_chart": sum(1 for r in rows if r["map_status"]=="mapped"),
   "joins_failed_not_on_chart": sum(1 for r in rows if r["map_status"]=="not on published chart"),
   "clubs_depth_unmapped": sum(1 for r in rows if r["depth_position"] is None and r["map_status"].startswith("depth unmapped")),
   "method_note": "Depth position is read from the club's own published depth chart. Because only 4 of 32 club charts were transcribed and verified, 2nd/3rd/4th-string detail is only asserted for KC, GB, NE and DET. Everywhere else the field is null and the row is flagged.",
   "why_index_is_not_points": "There is no official source that converts a depth-chart slot into expected points. The index above is a stated, auditable weighting used only to sort clubs. It must not be read as a point-spread adjustment."
 },
 "by_club": sorted(summary.values(), key=lambda s: (-s["deficiency_index"], -s["starters_dnp"], s["team"])),
 "rows": rows,
}
with open(os.path.join(OUT,"personnel.json"),"w",encoding="utf-8") as f:
    json.dump(out,f,indent=2)

print(f"rows={len(rows)} clubs={len(summary)} mapped={out['meta']['joins_to_published_chart']} "
       f"not_on_chart={out['meta']['joins_failed_not_on_chart']} depth_unmapped={out['meta']['clubs_depth_unmapped']}")
print(f"\n{'TEAM':5s} {'listed':>6s} {'DNP':>4s} {'Out':>4s} {'STARTER DNP':>11s} {'2nd':>4s} {'3rd':>4s} {'4th':>4s} {'IDX':>4s} charted")
for s in out["by_club"]:
    print(f"{s['team']:5s} {s['listed']:6d} {s['dnp']:4d} {s['game_status_out']:4d} "
          f"{s['starters_dnp']:11d} {s['second_string_dnp']:4d} {s['third_string_dnp']:4d} "
          f"{s['fourth_string_dnp']:4d} {s['deficiency_index']:4d} {s['charted']}")
mapped=[r for r in rows if r["map_status"]=="mapped" and r["practice_code"]=="DNP"]
print("\nVERIFIED starter-level absences (depth 1, DNP):")
for r in mapped:
    if r["depth_position"]==1:
        print(f"  {r['team']} {r['player']:22s} {r['depth_group']:5s} {r['unit']:8s} {r['injury'] or '(no injury listed)'}")
print("\nplayers on injury report but NOT found on their club's published chart:")
for r in rows:
    if r["map_status"]=="not on published chart":
        print(f"  {r['team']} {r['player']}")
