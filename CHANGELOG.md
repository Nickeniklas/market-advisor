# Changelog

Tracks structural/setup changes to this repo (`CLAUDE.md`, templates, docs) — not
your portfolio or market-session history, which live in git-ignored files under
`sessions/`, `portfolio.md`, and `persona.md`.

---

## 2026-08-22 — Sessions now anchor to the real date and fill blank instrument tags

Two silent-failure modes surfaced in the same session, both of which had already
corrupted real output.

**Date inference.** A deep session read the newest files in the repo — a
2026-08-08 pulse log and a 2026-08-08 positions build — and concluded that was
today's date. It was 2026-08-22. The session was logged under the wrong date,
its macro data was two weeks stale, and it told the user the portfolio snapshot
was "same-day fresh" when it was 14 days old. Nothing in the repo asserts the
current date, and `build_portfolio.py` warns only at `age > 14`, so a snapshot at
exactly 14 days passes with no warning at all.

**Blank instrument tags.** `apply_instruments()` appends a row for any holding
the export contains but `instruments.csv` doesn't know — with `ticker` and `tags`
empty — and warns once. Filling them was left to the user. In practice several
holdings sat untagged from the file's creation on 2026-07-27 through three pulses
and one deep session. An untagged holding appears in no thematic bloc, so a
double-digit percentage of the portfolio — including one of its largest
positions — was invisible in every exposure map produced in that window. The task
is classification, which the model does well and a CSV form does badly.

- `CLAUDE.md`: in "Portfolio data (both modes)", the `As of` check now requires
  taking today's date from the environment rather than inferring it from
  `sessions/` or the positions file, and stating the snapshot's age in days
  explicitly; notes that the build's warning fires past 14 days so exactly 14
  passes silently. Added a paragraph making blank `tags` cells in
  `portfolio/instruments.csv` a session responsibility: check at session start,
  propose a tag per blank (reusing existing slugs where they fit), confirm with
  the user, write back before using any bloc figures. Names it explicitly as the
  one generated-adjacent file a session is expected to edit.
- `README.md`: "Maintenance" gained the exactly-14-days caveat, a bullet stating
  thematic tags are now handled by the session rather than by hand, and a bullet
  making explicit that Position Notes are *not* automatic and nothing warns when
  one is missing. The `instruments.csv` line in "Project Structure" now says
  blank tags are filled by the session.

Not changed: `build_portfolio.py`. The auto-append and the warning already work
correctly — the gap was that nothing was responsible for acting on the warning.

---

## 2026-08-08 — Documented pulse mode; standardized the name on "pulse"

Pulse mode was fully specified in `CLAUDE.md` but never mentioned in
`README.md` or `run.md` as something the user could actually trigger — there
was no way to learn it existed short of reading the mode spec directly.
Separately, `CLAUDE.md`'s section header read `MODE: weekly-pulse` while the
`mode:` value every pulse log actually writes to frontmatter is `pulse`, a
naming mismatch.

- `CLAUDE.md`: renamed the `### MODE: weekly-pulse` header to
  `### MODE: pulse`. Step content is unchanged. Clarified in "Session Modes"
  that a routine is a Claude Code scheduled task the user sets up themselves
  locally — nothing is scheduled by default.
- `run.md`: added a "Pulse Session Prompt" block alongside the existing one
  (renamed "Deep Session Prompt" for clarity), noted the pulse prompt can be
  saved as a user-managed local routine, split the tips section by which
  apply to pulse vs. deep, and added a weekly pulse row to the cadence table
  with existing rows marked as deep.
- `README.md`: Quick Start now states it runs a deep session by default and
  points at the pulse prompt. Added a "Session Modes" section ahead of "What
  Each Session Produces" describing both modes and pointing at
  `demo/sessions/*-pulse.md` for real pulse output examples; that section now
  states up front it describes deep only.
- Grepped the repo for `weekly-pulse` after the change — the only remaining
  hits are inside past changelog entries below, which describe history and
  are left as written.

**Net effect:** pulse is now discoverable from the docs a new user actually
reads first, and the mode name is spelled one way everywhere going forward.

---

## 2026-07-26 — Portfolio numbers are built from a broker export, not typed by hand

Positions lived as a hand-typed markdown table in `portfolio.md`, with manually
converted EUR values and hand-arithmetic totals, currency splits, and
concentration percentages. Nothing recomputed them, so they rotted silently —
the last two pulse logs each opened by flagging that the table was still marked
to a date six weeks old. Checking the first real broker export against it showed
the drift was worse than stale prices: two positions had been bought that the
file didn't list at all, and it still described that purchase as a pending
decision. Every derived percentage described a portfolio that no longer existed.

- Added **`tools/build_portfolio.py`** (stdlib only, like `build_dashboard.py`).
  Reads broker CSV exports from `portfolio/raw/` and writes
  `portfolio.positions.md`: the holdings table plus computed weights, currency
  exposure, thematic blocs, concentration, and cost basis / unrealized return.
  Updating your numbers is now "drop in a new export, re-run" — nothing is
  retyped.
- Handles the Nordnet export as it actually ships: UTF-16 with a BOM,
  tab-delimited, Finnish decimal commas, and a non-breaking space inside one
  header name. Encoding and delimiter are detected rather than assumed, and
  column headers are matched through an alias table so a broker renaming a
  column fails loudly instead of silently producing wrong numbers.
- The export carries no date column, so the **as-of date comes from the
  filename** (`nordnet-26.7.2026.csv` and ISO naming both work). The generated
  file states its own as-of date and, past 14 days, carries a staleness banner —
  turning the complaint the pulses had been raising by hand into an automatic
  check. `CLAUDE.md` now requires sessions to check that date.
- Several exports can sit in `portfolio/raw/` at once: the newest date wins and
  files sharing that date are combined, so old exports can be kept as history
  without being double-counted, and a second broker can be added without a
  rewrite.
- Ticker symbols and thematic tags come from **`portfolio/instruments.csv`**,
  auto-created on first build and appended to whenever a new holding appears.
  It is git-ignored deliberately: the list of names you own is personal data,
  and the build script is committed. Tags may overlap, so the generated file
  states that blocs don't sum to 100%.
- **`portfolio.md` no longer holds positions.** It keeps what a broker export
  can't know: why each position is held, cash outside the brokerage,
  constraints, and "What I'm Thinking About". `portfolio.template.md` mirrors
  the new split.
- `CLAUDE.md` gains a **"Portfolio data (both modes)"** section stating which
  file owns what; deep Step 2, pulse Step 1, the Step 3 exposure map, the Step 6
  log template, and the pulse boundaries all now point at the generated file for
  numbers and `portfolio.md` for narrative. Exposure maps must cite real weights
  and may name a whole bloc with its share.

## 2026-07-21 — Deep sessions now review the previous one: scenario scoring, falsifiers, exposure maps

Deep sessions previously started from a blank slate each time — new scenarios
were generated with no reference to what the last session predicted, so
nothing ever got scored against reality, probability moves were unexplained,
and open questions were asked once and forgotten. This closes that loop.

- Added **Step 2.5 — Review the Previous Deep Session** to `CLAUDE.md`,
  running right after personal context is read and before new scenarios are
  drafted. It scores every scenario from the most recent deep-mode log
  (supported / contradicted / neutral, with evidence from Step 1), checks any
  declared falsifiers off as fired / not fired, and answers that session's
  open questions. Pulse logs are skipped for this step since they carry no
  scenarios. The first-ever deep session states there's nothing to review and
  proceeds with standalone probabilities.
- **Step 3** now requires: probabilities expressed as a delta from the
  previous session where the scenario's `family` recurs, with the reason for
  the move stated (not just the new number); a **falsifiers** subsection per
  scenario — 1–2 concrete, mechanically checkable observables, not vague
  ones; and an **exposure map** replacing the old generic "connect it to the
  portfolio" line — a table naming actual `portfolio.md` positions and their
  direction of exposure, not general diversification statements.
- **Step 1** now requires every macro data point to carry its as-of date or
  reference period, and to flag when the latest available print is older
  than the normal release cadence would suggest.
- **Step 6** log template gets a new `## Scenario Review (vs YYYY-MM-DD)`
  section between the Macro Snapshot and Scenarios Covered, capturing Step
  2.5's output; the Scenarios Covered section now shows `previous → current`
  probabilities where a family recurs.
- Added an optional `falsifiers` key to the scenario frontmatter schema (a
  plain-string list per scenario, append-only like all keys). This is a
  genuinely nested structure — a list inside a mapping inside a list — which
  `tools/build_dashboard.py`'s hand-rolled `parse_frontmatter` did not
  support; feeding it a `falsifiers:` block would have silently corrupted
  the parsed `scenarios` list (each falsifier string landing as a bogus
  top-level scenario entry) rather than erroring. **Judgment call:** the
  parser's own docstring says to switch to `pyyaml` if the schema ever grows
  genuinely nested structures, but that would add the project's first
  runtime dependency for one small, optional key. Instead extended
  `parse_frontmatter` minimally — one additional nested-list branch, still
  zero-dependency — to correctly capture `falsifiers` as a list on its
  scenario and leave everything else unaffected. Verified against a
  synthetic multi-scenario log with a nested `falsifiers` list plus the
  existing `tags` scalar list and scenario dedent-back cases; also confirmed
  `python3 tools/build_dashboard.py --sessions-dir demo/sessions --output
  demo/dashboard.html` still builds clean with no new warnings. The
  dashboard itself doesn't render `falsifiers` yet — pulse sessions read the
  latest deep log's source file directly for that, not through the
  dashboard build.
- **MODE: weekly-pulse**: step 2 now explicitly reads the latest deep-mode
  log directly for the scenario baseline (probabilities, families,
  falsifiers) rather than relying on a pulse's prose recollection of it, and
  a fired falsifier from that log is added to the "material" checklist —
  it's automatically material and normally sets
  `deep_session_recommended: true`.
- `run.md`: removed the manual `Today's date: [YYYY-MM-DD] ← update this
  before running` line from the session-start prompt — Claude Code already
  knows the current date, and the manual step was a stale-date footgun.
- Added a `falsifiers` entry to the `demo/sessions/2026-07-10.md` Stagflation
  scenario and rebuilt `demo/dashboard.html`, so the demo exercises the new
  key end-to-end (parse → build → still-clean dashboard).
- Updated `README.md`: "What Each Session Produces" now lists the Scenario
  Review step and the delta/falsifiers/exposure-map scenario format; the
  "Machine-Readable Session Logs" section documents the `falsifiers` key and
  the minimal parser extension that supports it.
- Updated `EXAMPLE-SESSION.md` to match: added scenario-consistent
  `falsifiers` (2 per scenario, in both frontmatter and prose) and an honest
  placeholder line in place of a real exposure map (the example's
  `portfolio.md` was never filled in, so no real holdings exist to map).
  Deliberately did **not** add a Scenario Review section — the example
  depicts a first-ever deep session with no prior log to review against —
  and added a blockquote note explaining that absence so it doesn't read as
  a forgotten section. Confirmed the updated frontmatter still parses via
  `parse_frontmatter`.
- Verified the `falsifiers` parser extension end-to-end rather than trusting
  a clean exit code: (1) parsed a temporary synthetic log (not committed)
  with a `falsifiers`-bearing scenario followed by a second scenario, and
  confirmed the printed dict had falsifiers nested only inside the first
  scenario, with the second scenario intact and no stray top-level items in
  `scenarios`; (2) grepped the rebuilt `demo/dashboard.html` for the literal
  falsifier strings added to `demo/sessions/2026-07-10.md` and confirmed
  both are present in the embedded JSON, proving the key survives the real
  build and isn't silently dropped by the (by-design) dashboard-side
  ignoring of the key.

**Net effect:** deep sessions now hold themselves accountable to their own
prior predictions instead of restarting cold each time, scenario
probabilities carry an explained trajectory instead of appearing from
nowhere, and pulses can mechanically detect when a named risk has actually
fired — all without adding a dependency to the build script.

---

## 2026-07-17 — Backfilled `family` slugs into real session logs

Retroactively added the `family` key (introduced same-day, see entry below) to
every scenario in the six pre-existing deep-mode logs in `sessions/`
(2026-04-10, 2026-04-13, 2026-04-13b, 2026-06-11, 2026-06-18, 2026-07-16) —
including logs marked `backfilled: false`. Those logs' numeric frontmatter was
captured live; only the new `family` keys are inferred after the fact from the
prose. Pulse logs have no `scenarios` key and needed no changes.

- Five families emerged across the six logs: `stagflation`, `soft-landing`,
  and `hard-landing` (spellings matched to the existing `demo/sessions/*.md`
  convention), plus `ai-correction` (matched to the example slug named in
  CLAUDE.md's own "Scenario families" section) and one standalone one-off,
  `higher-for-longer`.
- Notable judgment calls: `hard-landing` (April sessions) was not force-matched
  to the later AI-valuation-correction scenarios (`ai-correction`, first seen
  2026-06-11) — different mechanism (broad oil/tariff-driven recession vs. a
  positioning/valuation unwind concentrated in AI/semiconductor names).
  "Higher-for-Longer Soft Landing" (2026-06-18) was kept standalone rather than
  folded into `soft-landing` despite the name, since that session presents it
  as a distinct third scenario from "Relief Rally / Disinflation Resumes" with
  different rate and portfolio implications.
- Rebuilt the local `dashboard.html`; confirmed `python3 tools/build_dashboard.py`
  runs clean with no slug-drift warning, and the scenario-drift chart now
  renders 12 continuity ribbons across the five deep-session gaps.

---

## 2026-07-17 — Scenario families: fix fabricated continuity in the scenario-drift chart

Scenarios are generated fresh each deep session and may be entirely new
concepts, but the scenario-drift chart stacked-area rendering assumed name
continuity across sessions — "Stagflation" in one session was silently
treated as the same thing as "Stagflation" in the next, producing a
misleading wedge chart with a growing legend as scenario names drifted over
time.

- Added an optional `family` key to each scenario entry in the frontmatter
  schema (`CLAUDE.md`) — a short, free-form, kebab-case slug identifying the
  underlying concept, distinct from the human-readable `name`. Not an enum;
  new concepts get new slugs. Documented the session-time rule: check recent
  deep sessions' families before writing new scenarios, reuse a slug for a
  re-weighting of the same concept, coin a new one for a genuinely new idea,
  and never force a new concept into an old family. `family` is fully
  optional and append-only — logs written before this key existed still
  parse and render, just without continuity ribbons for their scenarios.
- Replaced the stacked-area scenario chart in `tools/dashboard.template.html`
  with per-deep-session stacked columns (segments = that session's
  scenarios) connected by thin continuity ribbons — drawn **only** between
  adjacent deep sessions whose segments share an explicit `family`. No
  shared family means no ribbon, so the chart can no longer claim a
  continuity the log didn't declare. Colors are assigned per family from the
  existing palette in first-appearance order; unfamilied scenarios fall back
  to the prior substring heuristic (soft/stagfl/hard) with their own
  independent color cursor offset past the family slots, so the two don't
  coincidentally collide on a shared chart. The legend lists families plus
  standalone names for unfamilied scenarios; raw scenario name and
  probability remain in tooltips. Also fixed x-axis label collisions:
  MM-DD labels escalate to the full date if two deep sessions share a
  month/day, and to the log's filename if they also share the full date
  (e.g. two deep sessions logged the same day). The hollow-marker convention
  for `backfilled` sessions is unchanged.
- `tools/build_dashboard.py`: confirmed the existing frontmatter parser
  already passes arbitrary extra keys through scenario mappings unchanged
  (no parser change needed for `family` itself). Added a build-time warning
  that flags pairs of `family` slugs that look like probable drift — one a
  prefix of the other, or differing only by a suffix like `-2` or `-trap` —
  so slug fragmentation surfaces immediately instead of silently splitting
  a concept's continuity across two colors.
- Added `family` slugs to `demo/sessions/*.md`'s scenarios (three recurring
  families: `soft-landing`, `stagflation`, `hard-landing`), with one
  deliberately unfamilied one-off scenario ("Liquidity shock" in the
  2026-06-08 log, replacing that session's "Hard landing") so the demo
  exercises both the continuity ribbons and the standalone fallback
  rendering. Rebuilt `demo/dashboard.html`.
- Verified against a synthetic sessions directory (not committed) covering:
  recurring families re-weighted across sessions, a one-off unfamilied
  scenario, two deep sessions logged on the same date, an old-schema log
  with no `family` key at all, and a probable-drift slug pair — confirmed
  correct ribbon placement (including that a family gap and a drift-suffix
  mismatch both correctly produce *no* ribbon rather than a fabricated one),
  correct label de-duplication, and that the build-time drift warning fires.

**Net effect:** the scenario-drift chart only ever shows continuity that was
explicitly declared in the logs, not continuity fabricated from a name
match — old logs keep rendering unchanged, and slug drift gets caught at
build time instead of silently fragmenting the chart.

---

## 2026-07-11 — Committed demo dashboard (synthetic data)

There was no way to see the dashboard's output without setting up
`persona.md`/`portfolio.md` and running real sessions first. A committed demo
closes that gap without ever touching personal data.

- Added `demo/sessions/` — 7 synthetic session logs (4 deep, 3 pulse) dated
  across April–July 2026, following the exact frontmatter schema from
  `CLAUDE.md`. One log is `backfilled: true` and `home_policy_rate` /
  one `home_cpi_yoy` entry are `null`, so the demo also shows how the
  dashboard renders those cases. All values are generic sample numbers in the
  same range as `EXAMPLE-SESSION.md`; none of it is derived from any real
  `persona.md`, `portfolio.md`, or `sessions/` content.
- Added `demo/dashboard.html` — built from those logs via
  `tools/build_dashboard.py`, committed so it's browsable directly from the
  repo (or servable via GitHub Pages) without running anything locally.
- Added `--sessions-dir` and `--output` CLI args to
  `tools/build_dashboard.py` (both optional, defaults unchanged) so the same
  script builds either the real local dashboard or the demo one.
- Fixed `.gitignore`: the `dashboard.html` rule was unrooted and was
  incidentally also matching `demo/dashboard.html`; anchored it to
  `/dashboard.html` so only the real, git-ignored root file is excluded.
- Updated `README.md`: project structure tree, pushed-vs-local table, and a
  new "Demo" section pointing at `demo/dashboard.html`.

**Net effect:** `demo/dashboard.html` gives anyone browsing the repo a working
sample of the dashboard with zero setup, built from entirely synthetic data.

---

## 2026-07-11 — Local dashboard frontends (HTML build + Obsidian note)

With all session logs now carrying machine-readable frontmatter (see entry
below), the first consumers were added. Everything stays local; no data is
hosted anywhere.

- Added `tools/build_dashboard.py` — a stdlib-only Python script that parses
  the frontmatter of every log in `sessions/`, validates it against the schema
  (warns on missing keys and improbable scenario sums, skips malformed files
  loudly rather than silently), and writes a single self-contained
  `dashboard.html` to the repo root.
- Added `tools/dashboard.template.html` — the dashboard itself: hand-rolled
  SVG charts, no JS dependencies, works over `file://` with no server. Shows
  scenario-probability drift across deep sessions (stacked bands), a
  real-time session-cadence strip (deep vs pulse ticks), small-multiple
  sparklines for every numeric series with latest value + delta, and a
  session table linking to the raw logs. Respects the schema's conventions:
  `null` renders as a gap, `backfilled: true` sessions get hollow markers,
  never-recorded series are hidden. A `LABELS` object at the top of the
  template lets local names (home index etc.) be renamed without touching
  anything else — the tracked template stays generic.
- Added `obsidian/Market Sessions Dashboard.md` — a ready-made Dataview
  dashboard note (all sessions, scenarios per deep session, flagged pulses,
  backfilled logs, latest reading) for anyone pointing an Obsidian vault at
  the repo.
- Git-ignored `dashboard.html` — it embeds real session data, so it follows
  the same tracked/local split as the logs it's built from.
- Updated `README.md`: project structure, pushed-vs-local table, and a
  rewritten "Machine-Readable Session Logs" section documenting the three
  frontends (HTML now, Obsidian now, Streamlit later — the build script's
  `parse_frontmatter` is importable by a future Streamlit app as-is).

**Net effect:** `python3 tools/build_dashboard.py` after any session produces
an up-to-date local dashboard in one file; Obsidian users get the same data
via Dataview; the Streamlit upgrade path needs no changes to the logs.

---

## 2026-07-11 — Machine-readable session logs (YAML frontmatter)

Session logs were prose-only, which made them fine to read but awkward to feed
into any tooling. The plan is to consume the journal through local, non-hosted
UIs — Obsidian (Dataview) now, possibly a static HTML dashboard, and maybe
Streamlit later once activity picks up. Rather than committing to one UI, the
logs themselves were made machine-readable so any of these can be layered on
top without touching the data again.

- Added a "Session Log Frontmatter" section to `CLAUDE.md` defining a YAML
  frontmatter schema every session log must start with: date, mode, policy
  rates (Fed/ECB/home), CPI prints (US/EU/home), index levels (S&P 500,
  STOXX 600, home index), 10Y yields (UST/Bund), EUR/USD, scenario
  probabilities (deep mode), and `material_change` /
  `deep_session_recommended` booleans (pulse mode).
- Schema rules: plain numbers only (no %, separators, or ~), `null` for
  unfetched values instead of guesses or omissions, and **append-only keys** —
  keys may be added later but never renamed or removed, so old logs stay
  queryable alongside new ones as tooling evolves.
- Updated both mode specs in `CLAUDE.md` (pulse log format and deep Step 6) to
  require the frontmatter block at the top of every log file.
- Added the frontmatter block to `EXAMPLE-SESSION.md` (generic sample values,
  no personal data — consistent with the existing tracked/local split).
- Added a "Machine-Readable Session Logs" section to `README.md` explaining the
  design and the intended consumers (Obsidian/Dataview with a sample query,
  static HTML, Streamlit later).
- Backfilled the frontmatter schema into the eight pre-existing session logs
  (prose-only, predating this feature), using `null` for anything not stated
  in the prose. Added a `backfilled` key to the schema (required, `false` on
  every live session, `true` only on these reconstructed logs) so any
  consumer can distinguish numbers captured live from values inferred after
  the fact from prose.

**Net effect:** the `sessions/` folder doubles as a queryable local dataset.
The prose stays the journal; the frontmatter feeds whatever UI sits on top,
all locally, with no change needed to logs when upgrading the UI.

---

## 2026-06-11 — Persona extraction

`CLAUDE.md` previously hardcoded the user's personal context directly into the
persona/instructions (location, tax wrappers, brokerage platform(s), local market
index, investment horizon, experience level) — all committed and visible in a
public repo.

- Added `persona.template.md` (tracked) — generic placeholders for: country/tax
  residency, currency, home central bank, tax wrappers & rates, brokerage
  platform(s), fund domicile constraints, local market index/indicators, regional
  CPI, investment horizon, experience level, preferred language.
- Added `persona.md` (git-ignored) — the actual filled-in values, moved out of
  `CLAUDE.md`.
- Rewrote `CLAUDE.md` to be generic: it now reads `persona.md` at session start
  and references it wherever local context is needed. If `persona.md` is
  missing, Claude prompts the user to set it up from the template.
- Removed duplicated location/platform/tax-wrapper/horizon fields from
  `portfolio.template.md` and `portfolio.md` (now live only in `persona.md`).
- Updated `README.md` (Quick Start, project structure, Maintenance) and `run.md`
  to reflect the new `persona.md` setup step.

**Net effect:** `CLAUDE.md`, `README.md`, `run.md`, and the templates are now
fully generic and safe to keep in a public repo. All personal data lives in
`persona.md` and `portfolio.md`, both git-ignored.

---

## 2026-06-11 — Genericize example output, clarify what's pushed

The example session log still contained location/platform/account-specific terms
left over from before the persona extraction, and it shared the `YYYY-MM-DD.md`
naming pattern used by real (git-ignored) session logs — both made it ambiguous
what was generic vs. personal, and what's tracked vs. local.

- Renamed the example session log to `EXAMPLE-SESSION.md` (no date) so it can't
  be confused with real dated logs in `sessions/`, and rewrote its content to be
  fully generic — references local context via `persona.md` instead of naming
  any specific country, platform, or account type.
- Added a "What Gets Pushed vs. Stays Local" table to `README.md` listing every
  file and whether it's tracked, so it's unambiguous at a glance where personal
  data can and can't end up.
