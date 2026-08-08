# Run Prompt – Market Advisor Session

> Paste one of these into Claude Code to start a new session.
> Or just type: "run a market advisor session" — Claude Code will read CLAUDE.md
> automatically and default to a deep session.

---

## Deep Session Prompt

```
Run a full market advisor session following the CLAUDE.md instructions.

Start with Step 1 (fetch current macro data via web search), then read persona.md,
portfolio.positions.md, and portfolio.md, then proceed through all steps in order.
Log the session when done.

Any additional context for this session:
[Optional: e.g. "I'm specifically thinking about whether to deploy my cash now or wait"
 or "I read about inverted yield curves this week, can you work that into the analysis?"]
```

---

## Pulse Session Prompt

```
Run a MODE: pulse market advisor session following the CLAUDE.md instructions.

Read portfolio.positions.md and portfolio.md, then the most recent file in
sessions/ plus the latest deep-mode log for the scenario baseline. Fetch current
macro data via web search and compare against last session. Log the result to
sessions/YYYY-MM-DD-pulse.md — flag clearly if nothing material changed.
```

This prompt can be saved as a Claude Code routine — a scheduled task you set up
yourself, locally, on a cadence such as weekly. The repo itself ships no
schedule; running a pulse, on any cadence, is always something you set up.

---

## Tips for Getting the Most Out of Each Session

- **Refresh your positions first** — export from your broker into `portfolio/raw/`
  and run `python3 tools/build_portfolio.py`. Takes a minute and keeps every weight
  and concentration figure honest; a stale snapshot quietly understates whatever
  has moved since. Applies to both deep and pulse sessions.

- **Then update `portfolio.md`** — especially the "What I'm Thinking About" section.
  This is what makes the analysis personal rather than generic. Positions don't go
  in this file anymore; they come from the build above. Deep-session tip only —
  pulse sessions read this file but don't produce teaching content from it.

- **Add a specific question** in the optional context field. Broad sessions are good
  for regular check-ins; focused questions ("explain duration risk to me using my
  bond ETF") produce deeper teaching moments. Deep-session tip only — pulse sessions
  deliberately produce no teaching content, so there's no context field to fill in.

- **Read the session log after** — the `sessions/` folder is your investment journal.
  Re-reading past sessions before starting a new one builds continuity. Applies to
  both.

- **Push back on Claude** — if a scenario or explanation doesn't make sense, ask
  follow-up questions in the same Claude Code session. The CLAUDE.md persona is
  designed to go deeper, not to give you a polished but shallow answer. Deep-session
  tip only — there's no scenario analysis in a pulse to push back on.

---

## Suggested Session Cadence

| Frequency | Mode | Trigger |
|-----------|------|---------|
| Weekly | Pulse | Routine check-in — usually concludes nothing material changed |
| Monthly | Deep | Routine check-in, refresh the export and update portfolio.md |
| After major macro events | Deep | Fed/ECB rate decisions, CPI prints, geopolitical shocks |
| Before deploying significant cash | Deep | Any time you're considering a move > €1,000 |
| When you feel anxious about markets | Deep | Reground in long-term principles |
| A pulse flags something material | Deep | The pulse's `deep_session_recommended` came back true |
