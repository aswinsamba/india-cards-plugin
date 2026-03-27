# India Cards — Claude Code Plugin

Analyse your Indian bank statements and get data-driven credit card recommendations based on your actual spend.

Card data is pulled from **official bank benefit pages** — not third-party aggregators.

---

## Commands

| Command | What it does |
|---|---|
| `/analyze-spend <statement>` | Parse a bank statement, classify spend by category, save to `/tmp/spend_analysis.json` |
| `/recommend-cards` | Score all cards against your spend, rank by net annual benefit |
| `/refresh-cards [card-id]` | Re-fetch official bank pages and update the card database |

---

## Quick Start

```bash
# 1. Install the plugin (once it's on GitHub)
/plugin install india-cards@claude-plugins-official

# 2. Populate the card database (fetches 20 official bank pages — ~2 min)
/refresh-cards

# 3. Drop your bank statement in (CSV or text export from your bank portal)
/analyze-spend ~/Downloads/hdfc-statement-jan-mar.csv

# 4. Get recommendations
/recommend-cards
```

No API key needed — refresh runs using Claude's built-in WebFetch.

---

## Card Database

Card URLs are bundled in the plugin (`data/card_urls.json`) — 20 cards across HDFC, Axis, ICICI, SBI, IDFC FIRST, Amex, Kotak, IndusInd.

Generated data is stored in `~/.india-cards/cards.json` (user-writable, outside the plugin).

To add a card: open a PR adding an entry to `data/card_urls.json`, then run `/refresh-cards <new-card-id>`.

---

## How Refresh Works

1. `scripts/refresh.py` fetches each card's official benefits URL
2. Strips scripts/nav/footer, extracts page text
3. Calls `claude-haiku-4-5` to extract structured JSON (fees, reward rates, perks)
4. Writes everything to `data/cards.json`

Most Indian bank pages serve enough static HTML for this to work. For JS-heavy pages that return thin content, a Playwright version (`scripts/refresh_playwright.py`) will be added.

---

## Statement Formats Supported

- **CSV** from bank portal (HDFC NetBanking, Axis Bank, ICICI iMobile, SBI YONO)
- **Plain text** copy-paste from statement PDF
- **Tabular text** — most formats work, the model adapts

---

## Privacy

Your statement never leaves your machine. The refresh script sends bank page text (publicly available) to Claude API. The recommend step runs entirely locally against `cards.json`.
