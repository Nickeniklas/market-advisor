#!/usr/bin/env python3
"""Build portfolio.positions.md from a broker export dropped in portfolio/raw/.

Usage (from anywhere):
    python3 tools/build_portfolio.py
    python3 tools/build_portfolio.py --raw-dir portfolio/raw --output portfolio.positions.md

Reads:   portfolio/raw/*.csv   (Nordnet positions export, unmodified)
Writes:  portfolio.positions.md (repo root — git-ignored, contains your data)

Drop a fresh export in and re-run: every number downstream is recomputed and
dated. Nothing here is hand-maintained except the INSTRUMENTS table below.

This is the cleaning step — all normalization (encoding, delimiters, decimal
commas, ticker lookup, tagging) happens here, once. The generated file is the
curated layer; sessions read it and assume it's clean. If a value looks wrong
downstream, fix it here and rebuild.

Zero dependencies, same as tools/build_dashboard.py.
"""

import argparse
import csv
import io
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Nordnet exports carry no ticker column and no notion of what a holding *is*,
# so both come from portfolio/instruments.csv — a git-ignored file, because the
# list of what you own is personal data and this script is committed.
#
# It is created for you on first run, pre-filled with the names from your export
# and blank ticker/tags columns to fill in. Buy something new and the next build
# appends it and tells you.
INSTRUMENTS_FILE = "instruments.csv"
INSTRUMENTS_HEADER = ["nimi", "ticker", "tags"]

# One-line gloss per tag, so the generated file explains its own groupings
# instead of leaving a bare slug to be interpreted. Generic financial concepts,
# not personal data — tags you coin yourself simply render without a gloss.
TAG_LABELS = {
    "ai-supply":  "AI/semiconductor supply side — sells the compute",
    "ai-demand":  "AI demand side — buys the compute",
    "defence":    "Defence / defence-adjacent industrials",
    "nordic":     "Nordic-listed",
    "energy":     "Energy / utilities",
    "financials": "Banks and insurers",
    "healthcare": "Healthcare / pharma",
    "consumer":   "Consumer-facing",
}

# Canonical field -> header spellings that map to it. Matched after
# normalization (casefold, NBSP -> space, whitespace collapsed), so
# "Tuotto,\xa0EUR" and "tuotto, eur" both land on `return_eur`.
COLUMNS = {
    "name":       ["nimi", "namn", "name", "instrument"],
    "currency":   ["valuutta", "valuta", "currency"],
    "quantity":   ["määrä", "antal", "quantity"],
    "avg_price":  ["keskikurssi", "gav", "genomsnittskurs", "average price"],
    "last_price": ["viimeisin", "senaste", "last"],
    "value_orig": ["arvo", "värde", "marknadsvärde", "value"],
    "value_eur":  ["arvo eur", "värde eur", "market value eur", "value eur"],
    "return_pct": ["tuotto, %", "tuotto %", "avkastning, %", "return %"],
    "return_eur": ["tuotto, eur", "tuotto eur", "avkastning, eur", "return eur"],
}
REQUIRED = ["name", "currency", "quantity", "value_orig", "value_eur"]

# Nordnet's `% tänään` (0 for every row in a snapshot taken outside market
# hours) and `Lainoitusarvo` (collateral value, a margin-lending concept) carry
# nothing for this analysis and are deliberately dropped.


def normalize_header(h: str) -> str:
    h = unicodedata.normalize("NFC", h).replace("\xa0", " ")
    return re.sub(r"\s+", " ", h).strip().casefold()


def decode(path: Path) -> str:
    """Decode a broker export without knowing its encoding up front.

    Nordnet emits UTF-16 LE with a BOM; other exports (and hand-edited files)
    are commonly UTF-8 or Windows-1252. cp1252 decodes any byte sequence, so it
    is the last resort and never raises.
    """
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("cp1252")


def sniff_delimiter(header_line: str) -> str:
    """Pick the delimiter by frequency on the header line.

    csv.Sniffer is skipped on purpose: Nordnet's headers contain literal commas
    ("Tuotto, EUR") inside tab-separated fields, which reliably fools it into
    guessing comma.
    """
    return max(("\t", ";", ","), key=header_line.count)


_DATE_PATTERNS = [
    (re.compile(r"(\d{4})-(\d{2})-(\d{2})"), lambda m: (int(m[1]), int(m[2]), int(m[3]))),
    (re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})"), lambda m: (int(m[3]), int(m[2]), int(m[1]))),
]


def as_of_date(path: Path, warnings: list) -> date:
    """The export's as-of date, taken from the filename.

    Nordnet puts no date column in the file, so the filename is the only record
    of when the snapshot was taken. Both `nordnet-26.7.2026.csv` (what Nordnet's
    own UI suggests) and ISO naming work.
    """
    for pattern, extract in _DATE_PATTERNS:
        m = pattern.search(path.name)
        if m:
            try:
                return date(*extract(m))
            except ValueError:
                continue
    fallback = date.fromtimestamp(path.stat().st_mtime)
    warnings.append(
        f"{path.name}: no date in filename — falling back to file mtime ({fallback}). "
        f"Rename it like 'nordnet-26.7.2026.csv' so the as-of date is explicit."
    )
    return fallback


def parse_number(raw: str):
    """Parse a Finnish-locale number: decimal comma, spaces as thousands sep."""
    s = (raw or "").replace("\xa0", "").replace(" ", "").replace("%", "").strip()
    if not s:
        return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def read_export(path: Path, warnings: list) -> list:
    text = decode(path)
    lines = text.splitlines()
    if not lines:
        sys.exit(f"error: {path.name} is empty")

    delimiter = sniff_delimiter(lines[0])
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        sys.exit(f"error: {path.name}: no header row found")

    # header -> canonical field
    lookup = {}
    for field, aliases in COLUMNS.items():
        for raw_header in reader.fieldnames:
            if normalize_header(raw_header) in aliases:
                lookup[field] = raw_header
                break

    missing = [f for f in REQUIRED if f not in lookup]
    if missing:
        sys.exit(
            f"error: {path.name}: missing required column(s): {', '.join(missing)}\n"
            f"  columns found: {reader.fieldnames}\n"
            f"  If Nordnet renamed a column, add the new spelling to COLUMNS in this script."
        )

    positions = []
    for row in reader:
        name = (row.get(lookup["name"]) or "").strip()
        if not name:
            continue  # trailing blank line
        value_eur = parse_number(row.get(lookup["value_eur"]))
        if value_eur is None:
            warnings.append(f"{path.name}: {name!r} has no parseable EUR value — skipped")
            continue

        def field(key):
            return parse_number(row.get(lookup[key])) if key in lookup else None

        positions.append({
            "name": name,
            "ticker": "",
            "tags": [],
            "currency": (row.get(lookup["currency"]) or "").strip(),
            "quantity": field("quantity"),
            "avg_price": field("avg_price"),
            "last_price": field("last_price"),
            "value_orig": field("value_orig"),
            "value_eur": value_eur,
            "return_pct": field("return_pct"),
            "return_eur": field("return_eur"),
            "source": path.name,
        })
    return positions


def apply_instruments(positions: list, path: Path, warnings: list):
    """Attach ticker and tags to each position from portfolio/instruments.csv.

    The file is created on first run and appended to whenever the export
    contains a name it doesn't know, so a new holding is a fill-in-the-blank
    rather than a setup step. A blank ticker or tags cell is legitimate — plenty
    of holdings need no tags — so only *absent rows* are reported.
    """
    known = {}
    if path.is_file():
        with path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                nimi = (row.get("nimi") or "").strip()
                if not nimi:
                    continue
                tags = [t.strip() for t in (row.get("tags") or "").split(";") if t.strip()]
                known[nimi] = ((row.get("ticker") or "").strip(), tags)

    missing = [p["name"] for p in positions if p["name"] not in known]
    for p in positions:
        p["ticker"], p["tags"] = known.get(p["name"], ("", []))

    if not missing:
        return

    new_file = not path.is_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        if new_file:
            writer.writerow(INSTRUMENTS_HEADER)
        for name in missing:
            writer.writerow([name, "", ""])

    rel = path.name if new_file else path.name
    if new_file:
        warnings.append(
            f"created {rel} with {len(missing)} holdings — fill in the ticker and "
            f"tags columns, then re-run. Separate multiple tags with ';' "
            f"(e.g. nordic;financials)."
        )
    else:
        warnings.append(
            f"{len(missing)} new holding(s) appended to {rel} "
            f"({', '.join(missing)}) — fill in ticker/tags and re-run"
        )


def select_exports(raw_dir: Path, warnings: list):
    """Return (as-of date, files) for the most recent snapshot in raw_dir.

    Newest date wins, and every file sharing that date is combined — so a second
    broker can be dropped alongside the first, while older exports can be kept
    as history without being double-counted.
    """
    files = sorted(p for p in raw_dir.glob("*.csv"))
    if not files:
        sys.exit(
            f"error: no .csv exports found in {raw_dir} — "
            f"drop a Nordnet positions export in there and re-run"
        )

    dated = [(as_of_date(p, warnings), p) for p in files]
    latest = max(d for d, _ in dated)
    current = [p for d, p in dated if d == latest]
    for d, p in dated:
        if d != latest:
            warnings.append(f"ignoring older export {p.name} (as of {d}; using {latest})")
    return latest, current


def pct(part, whole):
    return 100.0 * part / whole if whole else 0.0


def fmt_num(v, dp=0):
    """Space-separated thousands, the Finnish convention — used for every
    number in the output so columns are visually consistent."""
    return f"{v:,.{dp}f}".replace(",", " ")


def fmt_eur(v):
    return fmt_num(v, 0)


def render(positions, as_of, sources, output_path) -> str:
    total = sum(p["value_eur"] for p in positions)
    positions = sorted(positions, key=lambda p: -p["value_eur"])

    by_currency = defaultdict(float)
    for p in positions:
        by_currency[p["currency"]] += p["value_eur"]

    by_tag = defaultdict(list)
    for p in positions:
        for tag in p["tags"]:
            by_tag[tag].append(p)

    cost = sum(p["value_eur"] - p["return_eur"] for p in positions if p["return_eur"] is not None)
    gain = sum(p["return_eur"] for p in positions if p["return_eur"] is not None)

    age = (date.today() - as_of).days
    stale = "" if age <= 14 else (
        f"> **This snapshot is {age} days old.** Export a fresh one from Nordnet, "
        f"drop it in `portfolio/raw/`, and re-run the build before relying on these numbers."
    )

    out = []
    out.append("# Portfolio Positions")
    out.append("")
    out.append(f"> **Generated file — do not edit by hand.** Rebuild with `python tools/build_portfolio.py`.")
    out.append(f"> Edits here are overwritten; notes and cash live in `portfolio.md`.")
    out.append("")
    out.append(f"- **As of:** {as_of.isoformat()}")
    out.append(f"- **Source:** {', '.join(sources)}")
    out.append(f"- **Built:** {date.today().isoformat()}")
    if stale:
        out.append("")
        out.append(stale)
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Positions")
    out.append("")
    out.append("| # | Name | Ticker | Cur | Qty | Avg price | Last | Value (orig) | Value (€) | Weight | Return |")
    out.append("|---|------|--------|-----|-----|-----------|------|--------------|-----------|--------|--------|")
    for i, p in enumerate(positions, 1):
        qty = f"{p['quantity']:g}" if p["quantity"] is not None else "—"
        avg = fmt_num(p["avg_price"], 2) if p["avg_price"] is not None else "—"
        last = fmt_num(p["last_price"], 2) if p["last_price"] is not None else "—"
        orig = fmt_num(p["value_orig"]) if p["value_orig"] is not None else "—"
        ret = f"{p['return_pct']:+.1f}%" if p["return_pct"] is not None else "—"
        out.append(
            f"| {i} | {p['name']} | {p['ticker'] or '—'} | {p['currency']} | {qty} | {avg} | {last} | "
            f"{orig} | €{fmt_eur(p['value_eur'])} | {pct(p['value_eur'], total):.1f}% | {ret} |"
        )
    out.append("")
    out.append(f"**Total invested value: €{fmt_eur(total)}** across {len(positions)} positions "
               f"(excludes cash — see `portfolio.md`).")
    if cost:
        out.append("")
        out.append(f"**Cost basis: €{fmt_eur(cost)} → unrealized gain €{fmt_eur(gain)} "
                   f"({pct(gain, cost):+.1f}%).**")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Currency Exposure")
    out.append("")
    out.append("| Currency | Value (€) | Share |")
    out.append("|----------|-----------|-------|")
    for cur, val in sorted(by_currency.items(), key=lambda kv: -kv[1]):
        out.append(f"| {cur} | €{fmt_eur(val)} | {pct(val, total):.1f}% |")
    out.append("")
    out.append("> Currency of listing, not of underlying revenue — a USD-listed company "
               "earning globally is not fully a dollar bet.")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Thematic Blocs")
    out.append("")
    out.append("> **Blocs overlap and do not sum to 100%** — a holding can carry several tags, "
               "and untagged holdings appear in none. Tags are assigned in "
               "`portfolio/instruments.csv`.")
    out.append("")
    out.append("| Bloc | Value (€) | Share | Holdings |")
    out.append("|------|-----------|-------|----------|")
    for tag, members in sorted(by_tag.items(), key=lambda kv: -sum(p["value_eur"] for p in kv[1])):
        val = sum(p["value_eur"] for p in members)
        names = ", ".join(p["ticker"] or p["name"] for p in sorted(members, key=lambda p: -p["value_eur"]))
        out.append(f"| **{tag}** | €{fmt_eur(val)} | {pct(val, total):.1f}% | {names} |")
    out.append("")
    for tag in sorted(by_tag):
        if tag in TAG_LABELS:
            out.append(f"- `{tag}` — {TAG_LABELS[tag]}")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Concentration")
    out.append("")
    top = positions[:5]
    out.append(f"- **Largest position:** {top[0]['ticker'] or top[0]['name']} at "
               f"{pct(top[0]['value_eur'], total):.1f}%")
    for n in (2, 3, 5, 10):
        if n <= len(positions):
            share = sum(p["value_eur"] for p in positions[:n])
            names = ", ".join(p["ticker"] or p["name"] for p in positions[:n])
            label = f"**Top {n}:** {pct(share, total):.1f}%"
            out.append(f"- {label} ({names})" if n <= 3 else f"- {label}")
    tail = [p for p in positions if pct(p["value_eur"], total) < 1.0]
    if tail:
        tail_val = sum(p["value_eur"] for p in tail)
        out.append(f"- **Sub-1% positions:** {len(tail)} holdings totalling "
                   f"€{fmt_eur(tail_val)} ({pct(tail_val, total):.1f}%)")
    out.append("")
    return "\n".join(out) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-dir", type=Path, default=REPO_ROOT / "portfolio" / "raw",
        help="directory of broker .csv exports to read (default: portfolio/raw/)",
    )
    parser.add_argument(
        "--output", type=Path, default=REPO_ROOT / "portfolio.positions.md",
        help="path to write the positions file to (default: portfolio.positions.md)",
    )
    parser.add_argument(
        "--instruments", type=Path, default=None,
        help=f"ticker/tag lookup (default: {INSTRUMENTS_FILE} beside the raw dir)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.raw_dir.is_dir():
        sys.exit(f"error: {args.raw_dir} not found — create it and drop a broker export in")

    warnings = []
    as_of, files = select_exports(args.raw_dir, warnings)

    positions = []
    for path in files:
        positions.extend(read_export(path, warnings))
    if not positions:
        sys.exit("error: no positions parsed — check the export isn't a transaction log")

    instruments = args.instruments or args.raw_dir.parent / INSTRUMENTS_FILE
    apply_instruments(positions, instruments, warnings)

    args.output.write_text(
        render(positions, as_of, [p.name for p in files], args.output), encoding="utf-8"
    )

    try:
        label = args.output.relative_to(REPO_ROOT)
    except ValueError:
        label = args.output
    total = sum(p["value_eur"] for p in positions)
    print(f"built {label}  ({len(positions)} positions, €{fmt_eur(total)}, as of {as_of})")
    for w in warnings:
        print(f"  warn: {w}")


if __name__ == "__main__":
    main()
