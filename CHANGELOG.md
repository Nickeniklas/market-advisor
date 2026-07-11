# Changelog

Tracks structural/setup changes to this repo (`CLAUDE.md`, templates, docs) — not
your portfolio or market-session history, which live in git-ignored files under
`sessions/`, `portfolio.md`, and `persona.md`.

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
