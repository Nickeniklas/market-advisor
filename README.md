# market-advisor

A personal macro-financial education tool powered by Claude Code.

Runs regular analysis sessions to help you understand the current market environment,
think through risks, and build better mental models for long-term investing.

See [`demo/dashboard.html`](demo/dashboard.html) for sample output (synthetic
data — no real sessions).

---

## Project Structure

```
market-advisor/
├── CLAUDE.md             ← Core system prompt + workflow (generic, don't edit unless upgrading)
├── persona.template.md   ← Template — copy to persona.md and fill in who you are / where you invest
├── persona.md            ← YOUR context: country, tax wrappers, platforms, horizon (git-ignored)
├── portfolio.template.md ← Template — copy to portfolio.md and fill in your details
├── portfolio.md          ← YOUR context: holdings, cash, what's on your mind (git-ignored)
├── EXAMPLE-SESSION.md    ← Generic sample of session output (no personal data)
├── run.md                ← How to start a session + tips
├── README.md             ← This file
├── CHANGELOG.md          ← History of repo/template setup changes (not your portfolio)
├── tools/
│   ├── build_dashboard.py       ← Builds dashboard.html from sessions/ frontmatter (stdlib only)
│   └── dashboard.template.html  ← Dashboard template (generic — data is injected at build time)
├── obsidian/
│   └── Market Sessions Dashboard.md  ← Ready-made Dataview queries for an Obsidian vault
├── demo/                 ← Committed demo: synthetic sample data only, safe to browse/publish
│   ├── dashboard.html    ← Pre-built dashboard from the synthetic sessions below
│   └── sessions/         ← 7 synthetic session logs (4 deep, 3 pulse) — no real data
├── dashboard.html        ← Generated local dashboard (git-ignored — contains your data)
└── sessions/             ← Auto-logged session outputs (your investment journal, git-ignored)
    └── YYYY-MM-DD.md
```

---

## What Gets Pushed vs. Stays Local

Everything personal lives in git-ignored files. Everything else in this repo is
generic and contains no personal data — safe to push to a public remote.

| File | Pushed to git? | Contains |
|------|-----------------|----------|
| `CLAUDE.md`, `README.md`, `run.md`, `CHANGELOG.md` | ✅ Yes | Generic instructions/docs only |
| `persona.template.md`, `portfolio.template.md` | ✅ Yes | Empty templates with `[placeholder]` examples |
| `EXAMPLE-SESSION.md` | ✅ Yes | Generic sample output, no real numbers |
| `tools/build_dashboard.py`, `tools/dashboard.template.html` | ✅ Yes | Generic build script + template, no data |
| `obsidian/Market Sessions Dashboard.md` | ✅ Yes | Generic Dataview queries, no data |
| `demo/dashboard.html`, `demo/sessions/*.md` | ✅ Yes | Synthetic sample data only — no real sessions, never reads `persona.md`/`portfolio.md`/`sessions/` |
| **`persona.md`** | ❌ No (git-ignored) | Your country, tax wrappers, platforms, horizon, language |
| **`portfolio.md`** | ❌ No (git-ignored) | Your holdings, cash, notes |
| **`sessions/*.md`** | ❌ No (git-ignored) | Your real session logs |
| **`dashboard.html`** | ❌ No (git-ignored) | Built output — embeds your session data |

If you ever see real personal details (your country, holdings, account numbers,
etc.) inside `CLAUDE.md`, `README.md`, or any other file from the "pushed" rows —
that's a bug. It should only ever live in `persona.md`, `portfolio.md`,
`sessions/`, or `dashboard.html`.

---

## Quick Start

1. **Copy `persona.template.md` to `persona.md`** and fill in your country, tax
   wrappers, platform(s), home market index, investment horizon, and experience
   level — this is what makes the persona/teaching style fit you instead of being
   generic
2. **Copy `portfolio.template.md` to `portfolio.md`** and fill in your actual positions and cash
3. Open the project in Claude Code: `claude` in this directory
4. Paste the prompt from `run.md` (or just say "run a market advisor session")
5. Read the output, push back with follow-up questions, think about the open questions
6. Session is auto-logged to `sessions/`

---

## Demo

`demo/` contains a pre-built dashboard (`demo/dashboard.html`) and 7 synthetic
session logs (`demo/sessions/`) so anyone browsing the repo can see the output
without running anything or filling in `persona.md`/`portfolio.md`. All values
are made up — no real session, holding, or personal detail is ever read into
it. Open `demo/dashboard.html` directly in a browser, or serve the `demo/`
folder via GitHub Pages for a shareable live link.

It was built with:

```
python3 tools/build_dashboard.py --sessions-dir demo/sessions --output demo/dashboard.html
```

---

## What Each Session Produces

1. **Macro Snapshot** — current inflation, rates, equity levels, key risks,
   each data point dated to its as-of print or reference period
2. **Scenario Review** — the previous deep session's scenarios scored against
   what actually happened since (supported / contradicted / neutral, with
   evidence), its declared falsifiers checked fired / not fired, and its open
   questions answered. Skipped (with a note) only on the first-ever deep session.
3. **3 Scenarios** — plausible macro futures, each with a probability expressed
   as a delta from the last session where the same `family` recurs (with the
   reason for the change), 1–2 concrete falsifiers to watch, and an exposure
   map naming the actual `portfolio.md` positions it affects
4. **Key Principles** — timeless concepts made relevant to right now
5. **Open Questions** — hard questions to sit with before next session
6. **Session Log** — saved automatically to `sessions/YYYY-MM-DD.md`, starting
   with a machine-readable YAML frontmatter block (see below)

---

## Machine-Readable Session Logs

Every session log starts with a YAML frontmatter block (schema defined in
`CLAUDE.md`, sample at the top of `EXAMPLE-SESSION.md`) capturing the session's
key numbers: date, mode, policy rates, CPI prints, index levels, yields, FX, and
scenario probabilities. The prose body is for reading; the frontmatter is for
tools. This keeps the `sessions/` folder consumable by anything, locally, without
hosting your data anywhere. Three frontends exist or are planned:

Each deep-session scenario may also carry an optional `family` slug — a short,
free-form identifier for the underlying concept (e.g. `stagflation`,
`soft-landing`) so tooling can tell a re-weighting of the same idea across
sessions apart from a genuinely new one. Scenarios are generated fresh each
session and are never assumed to be the same concept just because the name
matches — continuity is only ever declared explicitly via a shared `family`.
See "Scenario families" in `CLAUDE.md` for the rules on reusing vs. coining slugs.

Each scenario may also carry an optional `falsifiers` list — 1–2 short,
concrete observables that would move that scenario's probability before the
next session (see Step 3 in `CLAUDE.md`). Pulse sessions read the latest deep
log directly and check each one off as fired / not fired; a fired falsifier
is automatically material and normally recommends a deep session. The
dashboard doesn't render this key yet, but it parses cleanly — the frontmatter
schema now has one level of nesting (a scalar list inside a scenario mapping),
and `parse_frontmatter` in `tools/build_dashboard.py` was extended minimally
to support exactly that, still with zero dependencies.

### 1. Local HTML dashboard (built, primary)

```
python3 tools/build_dashboard.py
```

Parses the frontmatter from every log in `sessions/`, injects it into
`tools/dashboard.template.html`, and writes a single self-contained
`dashboard.html` in the repo root. Open it directly in any browser — it works
over `file://`, needs no server and no dependencies (charts are hand-rolled
SVG; the only network use is optional font loading, and it degrades to system
fonts offline).

What it shows:
- **Scenario drift** — one stacked column per deep session; thin ribbons connect
  segments across adjacent deep sessions only when they share a declared
  `family` — no shared family means no ribbon, so the chart never fabricates
  continuity a session didn't actually declare
- **Session cadence** — deep/pulse ticks on a real-time axis
- **Macro small-multiples** — every numeric series as latest value + delta + sparkline
- **Session table** — newest first, with flags and links to the raw logs

Conventions the dashboard respects: `null` values render as gaps, never guesses;
`backfilled: true` sessions get hollow markers everywhere so reconstructed
numbers are visually distinct from live ones; series that were never recorded
(all `null`) are hidden; scenarios without a `family` (including every log
predating that key) still render fine, just standalone, with no ribbon claiming
a continuity that wasn't declared. Rebuild after each session — it takes under
a second; it also warns if two `family` slugs look like probable drift (one a
prefix or suffix-variant of the other) so slug fragmentation gets caught early.
To show your local names (e.g. rename "Home index" to your actual index), edit
the `LABELS` object at the top of the template's script.

`dashboard.html` embeds your data, so it's git-ignored like the logs themselves.

### 2. Obsidian (Dataview)

Point a vault at this repo folder and the frontmatter shows up as Properties.
`obsidian/Market Sessions Dashboard.md` is a ready-made dashboard note with
Dataview queries: all sessions, scenario probabilities per deep session, pulses
that flagged something, backfilled logs, and the latest reading. Requires the
Dataview community plugin.

### 3. Streamlit (later)

The same frontmatter parses in a few lines of Python (`python-frontmatter` or
`pyyaml`), so upgrading to an interactive app needs no changes to the logs —
and `tools/build_dashboard.py` already contains a reusable parser
(`parse_frontmatter`) a Streamlit app can import directly.

The schema is append-only: keys may be added over time but never renamed or
removed, so old logs stay queryable next to new ones.

---

## Maintenance

- `persona.md` is mostly a one-time setup — revisit it only if you move countries,
  switch brokers, or your tax situation changes
- Update `portfolio.md` before each session (especially "What I'm Thinking About")
- Re-run `python3 tools/build_dashboard.py` after each session to refresh the dashboard
- `persona.md`, `portfolio.md`, `sessions/*.md`, and `dashboard.html` are
  git-ignored — they hold your personal details and financial data and won't be
  committed to this repo. If you want version history for these over time, keep
  a separate private repo or local backups for these files.
- Sessions folder builds into a personal investment journal over months/years (locally)
