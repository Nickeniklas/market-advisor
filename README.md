# market-advisor

A personal macro-financial education tool powered by Claude Code.

Runs regular analysis sessions to help you understand the current market environment,
think through risks, and build better mental models for long-term investing.

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
└── sessions/             ← Auto-logged session outputs (your investment journal, git-ignored)
    └── YYYY-MM-DD.md
```

---

## What Gets Pushed vs. Stays Local

Everything personal lives in two files, both listed in `.gitignore`. Everything
else in this repo is generic and contains no personal data — safe to push to a
public remote.

| File | Pushed to git? | Contains |
|------|-----------------|----------|
| `CLAUDE.md`, `README.md`, `run.md`, `CHANGELOG.md` | ✅ Yes | Generic instructions/docs only |
| `persona.template.md`, `portfolio.template.md` | ✅ Yes | Empty templates with `[placeholder]` examples |
| `EXAMPLE-SESSION.md` | ✅ Yes | Generic sample output, no real numbers |
| **`persona.md`** | ❌ No (git-ignored) | Your country, tax wrappers, platforms, horizon, language |
| **`portfolio.md`** | ❌ No (git-ignored) | Your holdings, cash, notes |
| **`sessions/*.md`** | ❌ No (git-ignored) | Your real session logs |

If you ever see real personal details (your country, holdings, account numbers,
etc.) inside `CLAUDE.md`, `README.md`, or any other file from the left column —
that's a bug. It should only ever live in `persona.md`, `portfolio.md`, or
`sessions/`.

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

## What Each Session Produces

1. **Macro Snapshot** — current inflation, rates, equity levels, key risks
2. **3 Scenarios** — plausible macro futures with probability estimates + what each means for your portfolio
3. **Key Principles** — timeless concepts made relevant to right now
4. **Open Questions** — hard questions to sit with before next session
5. **Session Log** — saved automatically to `sessions/YYYY-MM-DD.md`, starting
   with a machine-readable YAML frontmatter block (see below)

---

## Machine-Readable Session Logs

Every session log starts with a YAML frontmatter block (schema defined in
`CLAUDE.md`, sample at the top of `EXAMPLE-SESSION.md`) capturing the session's
key numbers: date, mode, policy rates, CPI prints, index levels, yields, FX, and
scenario probabilities. The prose body is for reading; the frontmatter is for
tools. This keeps the `sessions/` folder consumable by anything, locally, without
hosting your data anywhere:

- **Obsidian** — point a vault at this folder (or the `sessions/` subfolder) and
  the frontmatter shows up as Properties. With the Dataview plugin you can build
  query-based dashboards, e.g. a table of scenario probabilities over time:

  ```dataview
  TABLE mode, sp500, home_index, us_cpi_yoy, scenarios
  FROM "sessions"
  SORT date DESC
  ```

- **Static HTML dashboard** — a small script (or a Claude Code task) can parse
  the frontmatter from all logs into a `data.json` and render charts in a single
  local HTML file. No server, nothing leaves your machine.

- **Streamlit (later)** — the same frontmatter parses in a few lines of Python
  (`python-frontmatter` or `pyyaml`), so upgrading to an interactive app needs
  no changes to the logs themselves.

The schema is append-only: keys may be added over time but never renamed or
removed, so old logs stay queryable next to new ones.

---

## Maintenance

- `persona.md` is mostly a one-time setup — revisit it only if you move countries,
  switch brokers, or your tax situation changes
- Update `portfolio.md` before each session (especially "What I'm Thinking About")
- `persona.md`, `portfolio.md`, and `sessions/*.md` are git-ignored — they hold
  your personal details and financial data and won't be committed to this repo.
  If you want version history for these over time, keep a separate private repo
  or local backups for these files.
- Sessions folder builds into a personal investment journal over months/years (locally)
