# My Portfolio Context

> Copy this file to `portfolio.md` and fill it in.
> `portfolio.md` is git-ignored so your data stays local.
>
> **Positions don't go in this file.** They're built from your broker export by
> `python tools/build_portfolio.py`, which writes `portfolio.positions.md`. Drop an
> export in `portfolio/raw/` and run the build — see README.md for setup.
>
> This file is for what a broker export can't know: why you hold things, cash held
> outside the brokerage, and what's on your mind. Claude reads both at session start.

---

## Profile

> Country, platform, tax wrapper, and investment horizon now live in `persona.md`
> (one-time setup). This section is for things that change with your portfolio.

- **Risk tolerance:** [e.g. Medium-high — I can handle 30–40% drawdowns without panic selling]
- **Monthly savings capacity:** [e.g. €200/month, or "Currently none"]

---

## Position Notes

> Why a position exists, in your words — the reasoning a broker export has no idea
> about. Weights, returns, and currency splits are computed in
> `portfolio.positions.md`; don't restate them here, they'll only go stale.
> Thematic groupings are assigned in `portfolio/instruments.csv`.

- **[Ticker]** — [e.g. Indirect exposure to a supply chain I'm already long]
- **[Ticker]** — [e.g. Small speculative position, sized to be written off]

---

## Cash Position

> Broker exports don't include cash, so this stays hand-maintained.

- **Total uninvested cash:** ~€[fill in]
- **Breakdown:** [e.g. €X in brokerage cash, €Y in bank savings]
- **Interest rate on cash (if any):** [...]

---

## What I'm Thinking About

> Update this before each session. What's on your mind right now?

[Your current thoughts, concerns, or questions go here.]

---

## Constraints & Context

- [e.g. employment status, income, monthly contribution capacity]
- [e.g. other savings/buffers earmarked for living expenses]
- [e.g. familiarity with ETFs, options, etc.]
