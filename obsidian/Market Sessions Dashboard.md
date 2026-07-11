# Market Sessions — Dataview Dashboard

> Drop this note into an Obsidian vault whose root is this repo (or move it into
> the vault and adjust the `FROM "sessions"` path). Requires the **Dataview**
> community plugin. Everything reads the YAML frontmatter of `sessions/*.md` —
> nothing is hosted anywhere.

---

## All sessions (newest first)

```dataview
TABLE mode, sp500, stoxx600, home_index, us_cpi_yoy, eu_cpi_yoy, backfilled
FROM "sessions"
WHERE date
SORT date DESC
```

## Deep sessions — scenario probabilities

```dataview
TABLE scenarios, fed_rate_upper, ust_10y, eurusd
FROM "sessions"
WHERE mode = "deep"
SORT date DESC
```

## Pulses that flagged something

```dataview
TABLE material_change, deep_session_recommended
FROM "sessions"
WHERE mode = "pulse" AND (material_change = true OR deep_session_recommended = true)
SORT date DESC
```

## Backfilled logs (values inferred from prose — read with care)

```dataview
LIST
FROM "sessions"
WHERE backfilled = true
SORT date DESC
```

## Latest reading

```dataview
TABLE WITHOUT ID date, mode, fed_rate_upper, ecb_deposit_rate, us_cpi_yoy, sp500, home_index, ust_10y, eurusd
FROM "sessions"
SORT date DESC
LIMIT 1
```
