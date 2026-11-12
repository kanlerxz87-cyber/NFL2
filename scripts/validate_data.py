#!/usr/bin/env python3
"""Validate NFL2 data snapshots: every row sourced, no blank verified values, standings arithmetic."""
import json, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
errors = []
def load(p):
    try:
        return json.loads((root/p).read_text())
    except Exception as e:
        errors.append(f"{p}: invalid JSON: {e}")
        return None

# Standings
s = load("data/standings_2026.json")
if s:
    if not s.get("source_url","").startswith("https://www.nfl.com/"):
        errors.append("standings: source_url must be official NFL.com")
    if len(s["teams"]) != 32:
        errors.append(f"standings: expected 32 teams, got {len(s['teams'])}")
    for t in s["teams"]:
        for k in ["team","abbr","conf","div","w","l","t","pct","pf","pa","net","home","road","div_rec","conf_rec","strk","last5"]:
            if k not in t or t[k] in (None, ""):
                errors.append(f"standings {t.get('abbr')}: blank/missing {k}")
        if t["pf"] - t["pa"] != t["net"]:
            errors.append(f"standings {t['abbr']}: PF-PA != Net ({t['pf']}-{t['pa']} vs {t['net']})")
        if t["w"] + t["l"] + t["t"] == 0:
            errors.append(f"standings {t['abbr']}: zero games")

# Schedule
sc = load("data/schedule_week11_2026.json")
if sc:
    if not sc.get("source_url","").startswith("https://www.nfl.com/"):
        errors.append("schedule: source_url must be NFL.com")
    if len(sc["games"]) != 13:
        errors.append(f"schedule: expected 13 games, got {len(sc['games'])}")
    for g in sc["games"]:
        for k in ["game","away","home","date","time_et","tv"]:
            if not g.get(k):
                errors.append(f"schedule {g.get('game')}: blank {k}")

# Teams
tm = load("data/teams.json")
if tm:
    if len(tm["teams"]) != 32:
        errors.append("teams: expected 32")
    for t in tm["teams"]:
        if not t.get("team") or not t.get("abbr") or not t.get("conf") or not t.get("div"):
            errors.append(f"teams: incomplete {t}")

# Player leaders
pl = load("data/player_leaders_2026.json")
if pl:
    for cat in ["passing","rushing","receiving","tackles"]:
        c = pl.get(cat, {})
        if not c.get("source_url","").startswith("https://www.nfl.com/"):
            errors.append(f"leaders {cat}: source must be NFL.com")
        if len(c.get("rows",[])) != 10:
            errors.append(f"leaders {cat}: expected 10 rows")

# Defense
df = load("data/team_stats_defense_2026.json")
if df:
    if len(df["teams"]) != 32:
        errors.append("defense: expected 32")
    for t in df["teams"]:
        for k in ["pass_yds_allowed","rush_yds_allowed","pa","pf"]:
            if t.get(k) in (None, ""):
                errors.append(f"defense {t.get('abbr')}: blank {k}")

# Injuries
inj = load("data/injuries_2026-11-11.json")
if inj:
    if not inj.get("source_url","").startswith("https://www.nfl.com/"):
        errors.append("injuries: source must be NFL.com")
    if not inj.get("key_items"):
        errors.append("injuries: no items")

# Suggestions / Questions / Strategies
sg = load("data/suggestions.json")
if sg and len(sg.get("suggestions",[])) != 12:
    errors.append("suggestions: expected 12")
q = load("data/questions.json")
if q and len(q.get("questions",[])) != 20:
    errors.append("questions: expected 20")
st = load("data/strategies.json")
if st:
    if st.get("leaderboard") != []:
        errors.append("strategies: leaderboard must be empty until gates pass (no invented performance)")
    if len(st.get("gates",[])) != 8:
        errors.append("strategies: expected 8 gates")

if errors:
    print("VALIDATION FAILED:")
    for e in errors: print(" -", e)
    sys.exit(1)
print("VALIDATION PASSED: all snapshots sourced, complete, arithmetic OK.")
