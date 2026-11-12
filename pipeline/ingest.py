"""Step 1 - ingest + integrity audit.

Loads the vendored raw CSVs, checks them against their documented schema, records
SHA-256 hashes for reproducibility and emits `site/data/audit.json` with a
row-by-row-passable list of findings (irregularities included).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from pipeline.common import RAW, SOURCES, UPSTREAM, sha256, utc_now, write_json

FILES = {
    "games.csv": {"rows_min": 7000, "required": [
        "game_id", "season", "game_type", "week", "gameday", "away_team", "home_team",
        "away_score", "home_score", "result", "total", "spread_line", "total_line",
        "away_moneyline", "home_moneyline", "roof", "surface", "temp", "wind",
        "div_game", "away_rest", "home_rest"]},
    "rosters.csv": {"rows_min": 20000, "required": [
        "season", "team", "playerid", "full_name", "position", "games", "starts", "years", "av"]},
    "teams.csv": {"rows_min": 700, "required": ["season", "team", "full", "conf", "division"]},
    "officials.csv": {"rows_min": 40000, "required": ["game_id", "off_pos", "official_id", "name"]},
    "win_totals.csv": {"rows_min": 500, "required": ["season", "team", "line", "over_odds", "under_odds"]},
    "closing_lines.csv": {"rows_min": 15000, "required": ["game_id", "type", "side", "line", "odds", "outcome"]},
    "initial_lines.csv": {"rows_min": 9000, "required": ["season", "sportsbook", "type", "about", "side", "line"]},
    "sc_lines.csv": {"rows_min": 3000, "required": ["season", "week", "away_team", "home_team", "side", "line"]},
    "standings.csv": {"rows_min": 700, "required": ["season", "team", "wins", "losses", "ties", "pct"]},
    "positions.csv": {"rows_min": 15, "required": ["position"]},
}


def load_raw() -> dict[str, pd.DataFrame]:
    out = {}
    for name in FILES:
        path = os.path.join(RAW, name)
        out[name] = pd.read_csv(path, low_memory=False)
    return out


def audit() -> dict:
    df = load_raw()
    findings: list[dict] = []
    file_meta = []

    for name, spec in FILES.items():
        path = os.path.join(RAW, name)
        d = df[name]
        file_meta.append({
            "file": name,
            "rows": int(len(d)),
            "columns": int(d.shape[1]),
            "sha256": sha256(path),
            "bytes": os.path.getsize(path),
            "source": "https://github.com/leesharpe/nfldata",
        })
        missing = [c for c in spec["required"] if c not in d.columns]
        findings.append({
            "id": f"schema:{name}",
            "check": "documented columns present",
            "status": "pass" if not missing else "fail",
            "detail": ("all required columns present" if not missing else f"missing: {missing}"),
            "source": SOURCES["nfldata_games"]["url"],
        })
        if len(d) < spec["rows_min"]:
            findings.append({
                "id": f"rows:{name}", "check": "row count >= expected",
                "status": "warn", "detail": f"{len(d)} rows < expected {spec['rows_min']}",
                "source": "https://github.com/leesharpe/nfldata",
            })

    g = df["games.csv"]

    # --- Deterministic identity checks -------------------------------------
    dup_games = int(g.game_id.duplicated().sum())
    findings.append({
        "id": "games:unique-id", "check": "game_id unique",
        "status": "pass" if dup_games == 0 else "fail",
        "detail": f"{dup_games} duplicate game_id values",
        "source": SOURCES["nfldata_games"]["url"],
    })

    played = g[g.result.notna()].copy()
    recomputed = played.home_score - played.away_score
    diff = (recomputed - played.result).abs()
    findings.append({
        "id": "games:result-identity", "check": "result == home_score - away_score",
        "status": "pass" if diff.max() == 0 else "fail",
        "detail": f"max abs deviation {diff.max():.0f} across {len(played)} played games",
        "source": SOURCES["nfldata_games"]["url"],
    })
    tdiff = ((played.home_score + played.away_score) - played.total).abs()
    findings.append({
        "id": "games:total-identity", "check": "total == home_score + away_score",
        "status": "pass" if tdiff.max() == 0 else "fail",
        "detail": f"max abs deviation {tdiff.max():.0f}",
        "source": SOURCES["nfldata_games"]["url"],
    })

    # --- Range / domain checks -------------------------------------------
    bad_total = played[(played.total < 0) | (played.total > 120)]
    findings.append({
        "id": "games:score-range", "check": "game totals within plausible range 0-120",
        "status": "pass" if len(bad_total) == 0 else "warn",
        "detail": f"{len(bad_total)} games outside range",
        "source": SOURCES["nfl_scoring"]["url"],
    })

    # Score never odd -> every NFL score is achievable with 2,3,6,7,8 point plays,
    # which makes 1 point impossible for a single team.
    odd_scores = played[(((played.home_score % 2) == 1) | ((played.away_score % 2) == 1))]
    findings.append({
        "id": "games:odd-score-impossible", "check": "no team score ends in 1 (impossible under Rule 11)",
        "status": "pass" if len(odd_scores) == 0 else "flag",
        "detail": f"{len(odd_scores)} games with a score ≡ 1 (mod 2) -> impossible total",
        "source": SOURCES["nfl_scoring"]["url"],
    })

    tie_games = played[played.result == 0]
    findings.append({
        "id": "games:ties", "check": "ties present (allowed by Rule 16)",
        "status": "pass",
        "detail": f"{len(tie_games)} tied games",
        "source": SOURCES["nfl_rules_2025"]["url"],
    })

    neg_total = played[(played.total_line <= 0)]
    findings.append({
        "id": "odds:total-positive", "check": "posted total line > 0",
        "status": "pass" if len(neg_total) == 0 else "fail",
        "detail": f"{len(neg_total)} non-positive totals",
        "source": SOURCES["nfldata_games"]["url"],
    })

    # --- Odds completeness (drives the "unverified" policy) --------------
    reg = g[(g.game_type == "REG") & (g.season <= 2025) & g.result.notna()]
    missing_totals = int(reg.total_line.isna().sum())
    findings.append({
        "id": "odds:total-coverage", "check": "closing total present for completed regular-season games",
        "status": "pass" if missing_totals == 0 else "warn",
        "detail": f"{missing_totals} of {len(reg)} completed games lack a total_line",
        "source": SOURCES["nfldata_games"]["url"],
    })
    missing_ml = int(reg.home_moneyline.isna().sum())
    findings.append({
        "id": "odds:ml-coverage", "check": "moneyline present (1999-2006 not covered upstream)",
        "status": "warn" if missing_ml else "pass",
        "detail": f"{missing_ml} of {len(reg)} completed games lack a moneyline",
        "source": SOURCES["nfldata_games"]["url"],
    })

    # --- Season completeness ---------------------------------------------
    seasons = reg.groupby("season").size()
    expected = {s: (272 if s >= 2021 else 256) for s in seasons.index}
    short = {int(s): int(seasons[s]) for s in seasons.index if seasons[s] != expected[int(s)]}
    findings.append({
        "id": "season:game-counts", "check": "regular-season game counts match 256 (<=2020) / 272 (>=2021)",
        "status": "pass" if not short else "flag",
        "detail": ("all seasons complete" if not short else f"deviations: {short}"),
        "source": SOURCES["nfl_rules_2025"]["url"],
    })

    # --- Environment / weather integrity ----------------------------------
    outdoor_missing = int(((g.roof.isin(["outdoors", "open"])) & g.temp.isna() & g.result.notna()).sum())
    findings.append({
        "id": "weather:coverage", "check": "temperature recorded for outdoor games",
        "status": "warn" if outdoor_missing else "pass",
        "detail": f"{outdoor_missing} played outdoor games have no temperature",
        "source": SOURCES["nfldata_games"]["url"],
    })

    # --- Roster integrity -------------------------------------------------
    r = df["rosters.csv"]
    findings.append({
        "id": "rosters:starts-le-games", "check": "starts <= games for every player-season",
        "status": "pass" if int((r.starts > r.games).sum()) == 0 else "flag",
        "detail": f"{int((r.starts > r.games).sum())} rows where starts > games",
        "source": SOURCES["nfldata_rosters"]["url"],
    })
    findings.append({
        "id": "rosters:years-defined", "check": "years of experience >= 0",
        "status": "pass" if int((r.years < 0).sum()) == 0 else "fail",
        "detail": f"{int((r.years < 0).sum())} negative",
        "source": SOURCES["nfldata_rosters"]["url"],
    })

    # --- Teams table integrity -------------------------------------------
    t = df["teams.csv"]
    if "conf" in t.columns:
        findings.append({
            "id": "teams:conf-domain", "check": "conference in {AFC, NFC}",
            "status": "pass" if set(t.conf.dropna().unique()) <= {"AFC", "NFC"} else "fail",
            "detail": f"values: {sorted(t.conf.dropna().unique().tolist())}",
            "source": SOURCES["nfldata_games"]["url"],
        })
    else:
        findings.append({
            "id": "teams:conf-domain", "check": "conference column present",
            "status": "flag", "detail": "teams.csv has no conf column; conference taken from standings.csv",
            "source": "https://github.com/leesharpe/nfldata",
        })

    flagged = [f for f in findings if f["status"] in ("fail", "flag")]
    return {
        "generated_utc": utc_now(),
        "upstream": UPSTREAM,
        "files": file_meta,
        "findings": findings,
        "summary": {
            "checks": len(findings),
            "pass": sum(1 for f in findings if f["status"] == "pass"),
            "warn": sum(1 for f in findings if f["status"] == "warn"),
            "fail": sum(1 for f in findings if f["status"] == "fail"),
            "flag": len(flagged),
            "irregularities": flagged,
        },
        "coverage": {
            "games": int(len(g)),
            "played_games": int(g.result.notna().sum()),
            "seasons": [int(g.season.min()), int(g.season.max())],
            "regular_season_games_before_2026": int(len(reg)),
            "last_completed_game_utc": str(g[g.result.notna()].gameday.max()),
            "roster_player_seasons": int(len(r)),
        },
    }


if __name__ == "__main__":
    import json
    res = audit()
    write_json("audit.json", res)
    print(json.dumps(res["summary"], indent=1))
    print(json.dumps(res["coverage"], indent=1))
