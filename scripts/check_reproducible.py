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
        except subprocess.CalledProcessError as e:
            print(f"  NEW  {f} (not in HEAD: {e.stderr.strip()[:120]})")
            continue
        except json.JSONDecodeError as e:
            failed.append(f)
            print(f"  BAD  {f}: committed copy is not valid JSON ({e})")
            continue
        new = json.load(open(f, encoding="utf-8"))
        if strip(old) == strip(new):
            print(f"  ok   {f}")
        else:
            failed.append(f)
            print(f"  DIFF {f}")
            # report the first differing path so the CI log is actionable
            def first_diff(a, b, path=""):
                if type(a) is not type(b):
                    return f"{path}: type {type(a).__name__} -> {type(b).__name__}"
                if isinstance(a, dict):
                    for k in sorted(set(a) | set(b)):
                        if k not in a:
                            return f"{path}.{k}: new key"
                        if k not in b:
                            return f"{path}.{k}: key removed"
                        d = first_diff(a[k], b[k], f"{path}.{k}")
                        if d:
                            return d
                    return None
                if isinstance(a, list):
                    if len(a) != len(b):
                        return f"{path}: length {len(a)} -> {len(b)}"
                    for i, (x, y) in enumerate(zip(a, b)):
                        d = first_diff(x, y, f"{path}[{i}]")
                        if d:
                            return d
                    return None
                if a != b:
                    return f"{path}: {a!r} -> {b!r}"
                return None
            print(f"       first difference {first_diff(strip(old), strip(new)) or '(none)'}")
    if failed:
        print(f"\n{len(failed)} data file(s) do not reproduce: {failed}")
        print("A committed value changed on rebuild - investigate before merging.")
        return 1
    print("\nall data files reproduce exactly (timestamps ignored)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
