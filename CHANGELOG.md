# Changelog

Tracks structural/setup changes to this repo (`CLAUDE.md`, templates, docs) — not
your portfolio or market-session history, which live in git-ignored files under
`sessions/`, `portfolio.md`, and `persona.md`.

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
