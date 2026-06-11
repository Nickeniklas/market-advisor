# market-advisor

A personal macro-financial education tool powered by Claude Code.

Runs regular analysis sessions to help you understand the current market environment,
think through risks, and build better mental models for long-term investing.
Built for a Finnish investor with a 7+ year horizon using Nordnet.

---

## Project Structure

```
market-advisor/
├── CLAUDE.md             ← Core system prompt + persona (don't edit unless upgrading)
├── portfolio.template.md ← Template — copy to portfolio.md and fill in your details
├── portfolio.md          ← YOUR context: holdings, cash, what's on your mind (git-ignored)
├── run.md                ← How to start a session + tips
├── README.md             ← This file
└── sessions/             ← Auto-logged session outputs (your investment journal, git-ignored)
    └── YYYY-MM-DD.md
```

`portfolio.md` and your real session logs are listed in `.gitignore` — they contain
your personal financial data and stay local even if this repo is public.

---

## Quick Start

1. **Copy `portfolio.template.md` to `portfolio.md`** and fill in your actual positions and cash
2. Open the project in Claude Code: `claude` in this directory
3. Paste the prompt from `run.md` (or just say "run a market advisor session")
4. Read the output, push back with follow-up questions, think about the open questions
5. Session is auto-logged to `sessions/`

---

## What Each Session Produces

1. **Macro Snapshot** — current inflation, rates, equity levels, key risks
2. **3 Scenarios** — plausible macro futures with probability estimates + what each means for your portfolio
3. **Key Principles** — timeless concepts made relevant to right now
4. **Open Questions** — hard questions to sit with before next session
5. **Session Log** — saved automatically to `sessions/YYYY-MM-DD.md`

---

## Maintenance

- Update `portfolio.md` before each session (especially "What I'm Thinking About")
- Commit changes to git to track your portfolio evolution over time
- Sessions folder builds into a personal investment journal over months/years
