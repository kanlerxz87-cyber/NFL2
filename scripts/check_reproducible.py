#!/usr/bin/env python3
"""Fail if `python3 -m pipeline.build` changes any committed value.

Only `generated_utc` / `as_of` stamps are allowed to differ between builds; every
number, label and source must reproduce byte-for-byte once those are removed.
This is what stops a "verified" dataset drifting silently.
"""
from __future__ import annotations
import glob, json, os, subprocess, sys

IGNORE = ("generated_utc", "as_of")


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in IGNORE}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o


def main() -> int:
    failed = []
    for f in sorted(glob.glob("site/data/*.json")):
        try:
            old = json.loads(subprocess.run(["git", "show", f"HEAD:{f}"],
                                            capture_output=True, text=True, check=True).stdout)
        except subprocess.CalledProcessError:
            print(f"  NEW  {f} (not in HEAD)")
            continue
        new = json.load(open(f, encoding="utf-8"))
        if strip(old) == strip(new):
            print(f"  ok   {f}")
        else:
            failed.append(f)
            print(f"  DIFF {f}")
    if failed:
        print(f"\n{len(failed)} data file(s) do not reproduce: {failed}")
        print("A committed value changed on rebuild - investigate before merging.")
        return 1
    print("\nall data files reproduce exactly (timestamps ignored)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
