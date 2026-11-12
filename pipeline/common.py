"""Shared configuration, provenance registry and IO helpers for the NFL2 pipeline.

Every number that appears on the site is produced by this pipeline. Nothing is
hand-typed. Run `python3 -m pipeline.build` from the repository root.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "pipeline", "data", "raw")
OUT = os.path.join(ROOT, "site", "data")
DOCS_OUT = os.path.join(ROOT, "pipeline", "out")

# Snapshot of the upstream data commit this build was generated from.
# Verified with `git -C <clone> rev-parse HEAD`.
UPSTREAM = {
    "repo": "leesharpe/nfldata",
    "url": "https://github.com/leesharpe/nfldata",
    "commit": "692e5f9f8ac9f4e2ee751c630817a7c290a04390",
    "commit_date": "2026-11-12T03:45:18+00:00",
    "license_note": "Repository publishes no LICENSE file; data is aggregated from "
                    "Pro Football Reference and nflverse and redistributed publicly by the author. "
                    "Treated as third-party, attribution given; see pipeline/data/SOURCES.md.",
}

# Official-source references used for verification (see docs/verification/).
SOURCES = {
    "nfl_rules_2025": {
        "title": "2025 NFL Rulebook (official)",
        "url": "https://operations.nfl.com/the-rules/2025-nfl-rulebook/",
        "publisher": "NFL Football Operations",
    },
    "nfl_rules_changes_2025": {
        "title": "2025 Rules Changes (official)",
        "url": "https://operations.nfl.com/the-rules/rules-changes/2025-rules-changes/",
        "publisher": "NFL Football Operations",
    },
    "nfl_injury_report": {
        "title": "NFL Injury Report / Game Status policy (official)",
        "url": "https://operations.nfl.com/player-health-safety/injury-report/",
        "publisher": "NFL Football Operations",
    },
    "nfl_cba": {
        "title": "Collective Bargaining Agreement (official PDF)",
        "url": "https://operations.nfl.com/media/aitjth4b/2020-nfl-nflpa-cba.pdf",
        "publisher": "NFL Football Operations",
    },
    "nfl_ir_rules": {
        "title": "Injured Reserve rules (NFL Football Operations)",
        "url": "https://operations.nfl.com/player-health-safety/nfl-injured-reserve/",
        "publisher": "NFL Football Operations",
    },
    "nfl_roster_rules": {
        "title": "Roster and practice-squad rules (NFL Football Operations)",
        "url": "https://operations.nfl.com/player-health-safety/roster-and-practice-squad-rules/",
        "publisher": "NFL Football Operations",
    },
    "nfl_scoring": {
        "title": "NFL official statistics / scoring rules (Rule 11)",
        "url": "https://operations.nfl.com/the-rules/2025-nfl-rulebook/",
        "publisher": "NFL Football Operations",
    },
    "nfldata_games": {
        "title": "nfldata games.csv (schema + column definitions)",
        "url": "https://github.com/leesharpe/nfldata/blob/master/DATASETS.md",
        "publisher": "Lee Sharpe (nfldata), upstream of Pro Football Reference / nflverse",
    },
    "nfldata_rosters": {
        "title": "nfldata rosters.csv (schema, games/starts/years/AV)",
        "url": "https://github.com/leesharpe/nfldata/blob/master/DATASETS.md#rosters",
        "publisher": "Lee Sharpe (nfldata), sourced from Pro Football Reference",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(name: str, obj, out_dir: str | None = None) -> str:
    out_dir = out_dir or OUT
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False, allow_nan=False, default=_json_default)
        fh.write("\n")
    return path


def _json_default(o):
    try:
        import numpy as np
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            v = float(o)
            return None if (v != v) else round(v, 6)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
    except Exception:
        pass
    raise TypeError(f"not JSON serialisable: {type(o)}")


def clean(obj):
    """Recursively convert numpy types and NaN -> None so JSON stays strict."""
    import math
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else round(obj, 6)
    try:
        import numpy as np
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            v = float(obj)
            return None if (math.isnan(v) or math.isinf(v)) else round(v, 6)
        if isinstance(obj, np.bool_):
            return bool(obj)
    except Exception:
        pass
    return obj
