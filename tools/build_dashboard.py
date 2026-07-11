#!/usr/bin/env python3
"""Build a local, single-file HTML dashboard from sessions/*.md frontmatter.

Usage (from anywhere):
    python3 tools/build_dashboard.py
    python3 tools/build_dashboard.py --sessions-dir demo/sessions --output demo/dashboard.html

Reads:   sessions/*.md   (YAML frontmatter per the schema in CLAUDE.md)
Writes:  dashboard.html  (repo root — git-ignored, contains your data)

Zero dependencies: the frontmatter schema is flat-with-two-known-lists, so a
small dedicated parser is used instead of pyyaml. If the schema ever grows
genuinely nested structures, swap `parse_frontmatter` for pyyaml.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = Path(__file__).resolve().parent / "dashboard.template.html"
MARKER = "__SESSION_DATA__"

# Keys expected on every session (shared schema). Anything missing is warned
# about and set to null so the dashboard renders a gap instead of crashing.
SHARED_KEYS = [
    "date", "mode", "fed_rate_upper", "ecb_deposit_rate", "home_policy_rate",
    "us_cpi_yoy", "eu_cpi_yoy", "home_cpi_yoy", "sp500", "stoxx600",
    "home_index", "ust_10y", "bund_10y", "eurusd", "backfilled",
]


def coerce_scalar(raw: str):
    """Turn a YAML scalar string into None/bool/int/float/str."""
    s = raw.strip().strip('"').strip("'")
    if s in ("null", "~", ""):
        return None
    if s == "true":
        return True
    if s == "false":
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def parse_frontmatter(text: str, source: str):
    """Parse the leading YAML frontmatter block of a session log.

    Handles: flat `key: value` pairs, a `tags:` list of scalars, and a
    `scenarios:` list of {name, probability} mappings. That is the entire
    schema; anything else raises so bad logs are caught, not silently skipped.
    """
    m = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.DOTALL)
    if not m:
        raise ValueError(f"{source}: no frontmatter block found")

    data: dict = {}
    current_list_key = None       # 'tags' or 'scenarios' while inside a list
    lines = m.group(1).splitlines()

    for ln in lines:
        stripped = ln.split("#", 1)[0].rstrip() if not ln.lstrip().startswith("#") else ""
        # keep '#' inside quoted strings? schema has none — comment-stripping is safe
        if not stripped.strip():
            continue

        indent = len(stripped) - len(stripped.lstrip())

        if indent == 0:
            current_list_key = None
            key, _, rest = stripped.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest == "":
                # start of a list (tags: / scenarios:)
                data[key] = []
                current_list_key = key
            else:
                data[key] = coerce_scalar(rest)
        else:
            if current_list_key is None:
                raise ValueError(f"{source}: unexpected indented line: {ln!r}")
            item = stripped.strip()
            if not item.startswith("-"):
                # continuation of a list-item mapping: `  probability: 35`
                key, _, rest = item.partition(":")
                if not data[current_list_key] or not isinstance(data[current_list_key][-1], dict):
                    raise ValueError(f"{source}: stray mapping line: {ln!r}")
                data[current_list_key][-1][key.strip()] = coerce_scalar(rest)
            else:
                item = item[1:].strip()
                if ":" in item:
                    key, _, rest = item.partition(":")
                    data[current_list_key].append({key.strip(): coerce_scalar(rest)})
                else:
                    data[current_list_key].append(coerce_scalar(item))

    return data


def validate(session: dict, source: str, warnings: list):
    for key in SHARED_KEYS:
        if key not in session:
            warnings.append(f"{source}: missing key '{key}' -> set to null")
            session[key] = None
    if session.get("mode") not in ("deep", "pulse"):
        warnings.append(f"{source}: mode is {session.get('mode')!r}, expected deep/pulse")
    if session.get("mode") == "deep":
        probs = [s.get("probability") for s in session.get("scenarios", [])
                 if isinstance(s, dict) and isinstance(s.get("probability"), (int, float))]
        if probs and not (85 <= sum(probs) <= 115):
            warnings.append(f"{source}: scenario probabilities sum to {sum(probs)}")
    d = str(session.get("date", ""))
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
        warnings.append(f"{source}: date {d!r} not in YYYY-MM-DD form")
    return session


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sessions-dir", type=Path, default=REPO_ROOT / "sessions",
        help="directory of session .md logs to read (default: sessions/)",
    )
    parser.add_argument(
        "--output", type=Path, default=REPO_ROOT / "dashboard.html",
        help="path to write the built dashboard to (default: dashboard.html)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    sessions_dir = args.sessions_dir
    output = args.output

    if not sessions_dir.is_dir():
        sys.exit(f"error: {sessions_dir} not found — run from inside the repo")
    if not TEMPLATE.is_file():
        sys.exit(f"error: template missing at {TEMPLATE}")

    files = sorted(p for p in sessions_dir.glob("*.md"))
    if not files:
        sys.exit("error: no session logs found in sessions/ — nothing to build")

    sessions, warnings, skipped = [], [], []
    for p in files:
        try:
            fm = parse_frontmatter(p.read_text(encoding="utf-8"), p.name)
        except ValueError as e:
            skipped.append(str(e))
            continue
        fm["_file"] = p.name
        # normalize date to string for stable JSON + sorting
        fm["date"] = str(fm.get("date", ""))
        sessions.append(validate(fm, p.name, warnings))

    sessions.sort(key=lambda s: (s["date"], s["_file"]))

    payload = {
        "generated": date.today().isoformat(),
        "sessions": sessions,
    }
    data_json = json.dumps(payload, ensure_ascii=False)

    template = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in template:
        sys.exit(f"error: marker {MARKER} not found in template")
    output.write_text(template.replace(MARKER, data_json), encoding="utf-8")

    try:
        output_label = output.relative_to(REPO_ROOT)
    except ValueError:
        output_label = output
    print(f"built {output_label}  ({len(sessions)} sessions)")
    for w in warnings:
        print(f"  warn: {w}")
    for s in skipped:
        print(f"  skipped: {s}")
    print("open it directly in a browser — no server needed.")


if __name__ == "__main__":
    main()
