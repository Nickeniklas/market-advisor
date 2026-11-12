# Audit — 2026-11-11

Audited at commit `4ad7991` (master, clean tree). Read-only: nothing in the repo
was changed apart from adding this file.

**Method.** Read every tracked file and the git-ignored inputs the scripts
consume. Ran both scripts with all paths redirected to a temp directory, against
synthetic fixtures and against copies of the real data. "Verified" below means
reproduced that way; anything else is labelled.

**Baseline.** The main paths work today. A fresh build from the real exports
matches the current `portfolio.positions.md` number for number, all 27 real
session logs and all 7 demo logs parse with zero warnings, and the committed
`demo/dashboard.html` is identical to a fresh rebuild. Every finding below is a
way the tools go wrong on input they are likely to meet, not something currently
producing wrong numbers.

---

## 1. Top 5 findings (impact vs effort)

### 1. `instruments.csv` is read and appended with no format checks — verified

`tools/build_portfolio.py:229-239` (read), `tools/build_portfolio.py:267-275` (append)

This is the one build input that people and sessions edit, and three ordinary
ways of saving it break tagging:

- **No trailing newline, then a new holding appears.** The append at line 270
  glues the new row onto the last one: `Beta Inc,BETA,ai-supply` becomes
  `Beta Inc,BETA,ai-supplyGamma AB,,`. The build that does it looks fine; the
  *next* build moves Beta out of `ai-supply` into a bloc called
  `ai-supplyGamma AB`, with no warning. Notepad and whole-file rewrites both
  leave files without a final newline.
- **Saved from Excel** (UTF-8 BOM, or `;` as delimiter, which a Finnish-locale
  Excel uses). The header no longer equals `nimi`, so every row is skipped: all
  holdings are reported untagged, and a blank duplicate row per holding is
  appended on *every* build (2 holdings: 5 lines after one build, 7 after two).
- **Saved as Windows-1252 with an `ä`.** Raw `UnicodeDecodeError` traceback.

Why it matters: bloc shares are the figures sessions quote and reason from, and
the first case fails silently.

Fix: open with `utf-8-sig`, and exit with a clear message if the header is not
exactly `nimi,ticker,tags`. Before appending, check that the file ends in a
newline and write one if it doesn't. About ten lines.

### 2. Same-date exports are concatenated, never merged or de-duplicated — verified

`tools/build_portfolio.py:305-307`, `tools/build_portfolio.py:474-476`

- Downloading the same export twice in a day (the browser names the second one
  `… (1).csv`) doubles everything: €1 900 became €3 800, 2 positions became 4,
  exit code 0, no warning. Weights are unchanged, so nothing looks wrong except
  the euro figures.
- The same holding in two same-date files (two accounts, or the "second broker"
  case the docstring invites) stays as two rows. A holding that is 69% of the
  book showed as two rows of 34.5%, and "Largest position" reported 34.5%.

Why it matters: total invested value and concentration are the two numbers the
session is told never to get wrong, and both failures are silent.

Fix: after reading, merge positions by name (sum quantity, values and
`return_eur`; recompute average price and return %). Skip, with a warning, any
same-date file whose bytes are identical to one already read.

### 3. The filename date is trusted with no sanity check — verified

`tools/build_portfolio.py:123-136`, `:306`, `:344-345`

A file named `export 1.11.2027.csv` beat a genuine `10.11.2026` export. The
output said `As of: 2027-11-01`, the age was negative so no staleness banner was
written, and the exit code was 0. It keeps winning until someone deletes it.

A typo in the other direction makes the new export lose, and the only signal is
one more `ignoring older export` line among the seven the real build already
prints every run.

Why it matters: this disables the staleness guard that `CLAUDE.md` leans on, and
every weight goes quietly stale. The dates look hand-typed (the existing
filenames have inconsistent spacing — that part is a guess).

Fix: treat an as-of date later than today as an error. Collapse the routine
"ignoring older export" lines into a single count, and warn separately when an
ignored file has a newer modification time than the file that won.

### 4. The dashboard build accepts malformed frontmatter silently — verified

`tools/build_dashboard.py:76`, `:102-118`, `:176-191`

Each of these built with exit code 0 and no warning unless noted:

| Input | Result |
|---|---|
| `falsifiers:` items at the key's own indent (valid YAML) | Falsifier strings become extra entries in `scenarios` |
| A falsifier wrapped onto a second line (valid YAML) | The second line becomes a key on the scenario, the text is cut |
| `#` inside a name or falsifier | Everything after it is dropped (line 76) |
| `sp500: 5,650`, `ust_10y: ~4.6`, `backfilled: False` | Stored as strings, so the point vanishes from its chart |
| `probability: 70%` | Stored as a string, and the 85–115 sum check is skipped |
| Frontmatter `date` copied from the previous log | Accepted; sorting uses it, so the session lands in the wrong place |
| `mode: deep` with `scenarios: null` | `TypeError` at line 184 aborts the whole build |

Why it matters: `CLAUDE.md` calls the frontmatter rules "strict — dashboards
depend on these", but `validate()` checks only key presence, mode, the
probability sum and the date's shape. These are exactly the slips a model makes
when writing a log, and a missing chart point is easy to read as a `null`.

Fix: in `validate()`, warn when a numeric key holds a non-number, when a boolean
key holds a non-boolean, when `date` differs from the filename prefix, and when a
scenario entry is not a mapping with a `name`, an integer `probability` and no
keys beyond `family` and `falsifiers`. Guard `scenarios` with an `isinstance`
check so a bad log is reported instead of crashing.

### 5. `</script>` in a frontmatter string breaks out of the data block — verified in the output file

`tools/build_dashboard.py:240-245`, `tools/dashboard.template.html:143`

`json.dumps` does not escape `</`, so a scenario name containing `</script>`
ends the script element and the rest is parsed as HTML. Confirmed by building
it and finding the literal tag inside the `const DATA = …` line. I did not open
the result in a browser.

Why it matters: scenario names and falsifiers are model-written text derived
from web search. This is the only place outside text reaches an HTML file that
is opened locally and embeds personal data. Likelihood is low.

Fix: `data_json = data_json.replace("</", "<\\/")` before the template
substitution. One line.

### Below the cut

- **Piped stdout on Windows is cp1252** (`tools/build_portfolio.py:493-495`,
  `tools/build_dashboard.py:251-256`) — verified. A holding name outside cp1252
  raises `UnicodeEncodeError` after the output file is written, so the run exits
  1 and the remaining warnings are lost. `€` and `—` also arrive garbled for
  whoever reads the pipe, which includes a session reading the build's stdout.
  Fix: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at the top
  of both `main()` functions.

### Secrets and history

No secrets or personal data found in any committed content.

- 18 commits on `master` / `origin/master`. No personal file was ever committed;
  the only path that no longer exists is `2026-04-09-example.md`, a synthetic
  sample.
- Searched every revision for all 52 holding names and tickers in the local
  `instruments.csv`, plus API-key formats, private keys, password/token
  assignments, e-mail addresses, IBANs and ISINs. Zero hits. The search was
  checked against a term known to be present.
- Commits before `bea2783` hard-code country, broker and account type in
  `CLAUDE.md`. The same details still appear as `[e.g. …]` examples in the
  templates, so this exposes nothing new.
- **Commit metadata:** 17 of 18 commits carry a personal Gmail address as
  author; one uses the GitHub noreply address. If the remote is public, so is
  the address. Setting `user.email` to the noreply address fixes future
  commits; rewriting published history is a judgment call.
- **Local `.git` only:** the object store holds unreachable blobs containing a
  raw broker export, a built positions file and a zip-format file. They are not
  reachable from any ref, so `git push` does not send them; they matter only if
  the folder is copied or zipped with `.git` inside. `git gc --prune=now`
  removes them. How they got there is a guess: staged once, never committed.
- No auth or network surface exists to audit. Both scripts are local CLIs with
  no network calls, `eval`, subprocess or deserialisation. The dashboard's only
  request is Google Fonts (`tools/dashboard.template.html:7-9`), which the
  README discloses.

---

## 2. Tests that would catch real breakage

All stdlib (`unittest` + `tempfile`), no new dependencies.

1. **Golden build from a synthetic Nordnet fixture.** A UTF-16-LE, tab-separated
   file with decimal commas, an NBSP in a header and a negative return. Assert
   total, per-position weights, currency split, bloc shares and the as-of date.
   This covers `decode`, `sniff_delimiter`, the header aliases and
   `parse_number`, which is where a Nordnet format change would land.
2. **`instruments.csv` round trip.** No trailing newline plus a new holding:
   existing rows unchanged, new row on its own line. BOM and `;` variants: read
   correctly or fail loudly, never "everything untagged". A second build
   appends nothing.
3. **Export selection.** Newest date wins; same-date files combine; a
   byte-identical duplicate does not change the total; a future-dated filename
   is rejected; a file with no date warns. Add the 14-day versus 15-day banner
   boundary, which needs `render()` to take `today` as a parameter instead of
   calling `date.today()`.
4. **Frontmatter parser against the documented schema.** Parse the YAML example
   in `CLAUDE.md` and every `demo/sessions/*.md` and compare with the expected
   structure. Then feed the variants from finding 4 and assert each one either
   parses correctly or produces a warning or `ValueError` — never silent
   garbage.
5. **Demo freshness.** Rebuild `demo/sessions` and assert the output equals the
   committed `demo/dashboard.html` apart from the generated date, with zero
   warnings. It is the cheapest end-to-end check of parser plus template, and it
   catches a template change that was not followed by a demo rebuild. It passes
   today.

---

## 3. Not verified

- **Browser behaviour.** No dashboard was opened in a browser. Finding 5 is
  confirmed in the HTML text only. That string values render as `NaN` in the
  session table is inferred from `tools/dashboard.template.html:180` and `:390`.
- **The remote.** Only the local clone was examined, without fetching. Whether
  the GitHub repo is public, and whether it has branches, forks or pull-request
  refs beyond `origin/master`, was not checked.
- **Other Nordnet formats.** Only Finnish-language exports were available. The
  Swedish and English header aliases in `COLUMNS` (`tools/build_portfolio.py:66-76`)
  are untested. The newest export fills the ISIN column for 12 of 23 rows; why
  it is partial is unknown, so whether ISIN could replace name matching is open.
- **Cost-basis line** (`tools/build_portfolio.py:341-342`). It silently leaves
  out positions with no `return_eur`. Whether a real export ever lacks that
  value was not established, so this is a guess, not a finding.
- **Encoding behaviour on other machines.** The cp1252 result was observed here
  (Windows 11, Python 3.12.2) only.
- **Obsidian page.** The Dataview queries in `obsidian/` were read, not run.
- **Session behaviour.** Most of this project is the prompt in `CLAUDE.md`.
  Whether sessions follow it (word budgets, falsifier checks, the Step 7
  reconcile) cannot be audited by reading code and was not tested.
