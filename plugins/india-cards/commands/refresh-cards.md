---
description: Refresh the Indian credit card database from official bank benefit pages
argument-hint: [card-id]
allowed-tools: [Read, Write, Bash]
---

# Refresh Card Database

Fetch official bank benefit pages and extract structured card data.
Uses local Python (runs on the user's machine, bypasses network proxy).

## Arguments
`$ARGUMENTS`

---

## Card catalogue

```json
{
  "hdfc-regalia-gold":    { "name": "HDFC Regalia Gold",                   "issuer": "HDFC Bank",         "url": "https://www.hdfcbank.com/personal/pay/cards/credit-cards/regalia-gold-credit-card" },
  "hdfc-infinia":         { "name": "HDFC Infinia",                        "issuer": "HDFC Bank",         "url": "https://www.hdfcbank.com/personal/pay/cards/credit-cards/infinia-credit-card" },
  "hdfc-millennia":       { "name": "HDFC Millennia",                      "issuer": "HDFC Bank",         "url": "https://www.hdfcbank.com/personal/pay/cards/credit-cards/millennia-credit-card" },
  "hdfc-moneyback-plus":  { "name": "HDFC MoneyBack+",                     "issuer": "HDFC Bank",         "url": "https://www.hdfcbank.com/personal/pay/cards/credit-cards/moneyback-plus-credit-card" },
  "axis-magnus":          { "name": "Axis Bank Magnus",                    "issuer": "Axis Bank",         "url": "https://www.axisbank.com/retail/cards/credit-card/axis-bank-magnus-card/more-benefits" },
  "axis-atlas":           { "name": "Axis Bank Atlas",                     "issuer": "Axis Bank",         "url": "https://www.axisbank.com/retail/cards/credit-card/axis-bank-atlas-credit-card" },
  "axis-ace":             { "name": "Axis Bank ACE",                       "issuer": "Axis Bank",         "url": "https://www.axisbank.com/retail/cards/credit-card/ace-credit-card" },
  "icici-sapphiro":       { "name": "ICICI Sapphiro",                      "issuer": "ICICI Bank",        "url": "https://www.icicibank.com/personal-banking/cards/credit-card/sapphiro-credit-card/key-privileges" },
  "icici-amazon-pay":     { "name": "ICICI Amazon Pay",                    "issuer": "ICICI Bank",        "url": "https://www.icicibank.com/personal-banking/cards/credit-card/amazon-pay-icici-credit-card/key-privileges" },
  "icici-emeralde":       { "name": "ICICI Emeralde",                      "issuer": "ICICI Bank",        "url": "https://www.icicibank.com/personal-banking/cards/credit-card/emeralde-private-metal-credit-card/key-privileges" },
  "sbi-simplyclick":      { "name": "SBI SimplyCLICK",                     "issuer": "SBI Card",          "url": "https://www.sbicard.com/en/personal/credit-cards/shopping/simplyclick-sbi-card.page" },
  "sbi-elite":            { "name": "SBI Card ELITE",                      "issuer": "SBI Card",          "url": "https://www.sbicard.com/en/personal/credit-cards/travel-and-entertainment/sbi-card-elite.page" },
  "sbi-cashback":         { "name": "SBI Cashback Card",                   "issuer": "SBI Card",          "url": "https://www.sbicard.com/en/personal/credit-cards/cashback/cashback-sbi-card.page" },
  "idfc-first-wealth":    { "name": "IDFC FIRST Wealth",                   "issuer": "IDFC FIRST Bank",   "url": "https://www.idfcfirstbank.com/credit-card/wealth/amp" },
  "idfc-first-select":    { "name": "IDFC FIRST Select",                   "issuer": "IDFC FIRST Bank",   "url": "https://www.idfcfirstbank.com/credit-card/select/amp" },
  "amex-platinum-travel": { "name": "Amex Platinum Travel",                "issuer": "American Express",  "url": "https://www.americanexpress.com/in/benefits/platinum-travel-credit-card/" },
  "amex-mrcc":            { "name": "Amex Membership Rewards Credit Card", "issuer": "American Express",  "url": "https://www.americanexpress.com/in/benefits/membership-rewards-credit-card/" },
  "amex-platinum-reserve":{ "name": "Amex Platinum Reserve",               "issuer": "American Express",  "url": "https://www.americanexpress.com/in/benefits/platinum-reserve-card/" },
  "kotak-league-platinum":{ "name": "Kotak League Platinum",               "issuer": "Kotak Mahindra Bank","url": "https://www.kotak.com/en/personal-banking/cards/credit-cards/league-platinum-credit-card.html" },
  "indusind-celesta":     { "name": "IndusInd Bank Celesta",                "issuer": "IndusInd Bank",     "url": "https://www.indusind.com/in/en/personal/cards/credit-card/celesta-credit-card.html" }
}
```

---

## Instructions

### Step 1 — Ensure dependencies

```bash
python3 -c "import requests, bs4" 2>/dev/null || pip3 install requests beautifulsoup4 --quiet --break-system-packages
mkdir -p ~/.india-cards
```

### Step 2 — Determine scope

If `$ARGUMENTS` contains a card ID, process only that entry.
Otherwise process all 20 cards.

### Step 3 — For each card, fetch locally via Bash

Use this Python one-liner to fetch each page on the user's machine (avoids network proxy):

```bash
python3 - <<'PYEOF'
import requests, sys
from bs4 import BeautifulSoup
url = "CARD_URL_HERE"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36", "Accept-Language": "en-IN,en;q=0.9"}
try:
    r = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script","style","nav","footer","header","iframe"]): t.decompose()
    lines = [l for l in soup.get_text(separator="\n", strip=True).splitlines() if l.strip()]
    print("\n".join(lines)[:8000])
except Exception as e:
    print(f"FETCH_ERROR: {e}", file=sys.stderr)
PYEOF
```

Replace `CARD_URL_HERE` with the card's URL from the catalogue.

### Step 4 — Extract structured data

From the Bash output, extract this JSON structure for each card:

```json
{
  "name": "full card name",
  "issuer": "bank name",
  "joining_fee": <number or null>,
  "annual_fee": <number or null>,
  "fee_waiver_spend_lakhs": <number or null>,
  "base_reward_points_per_100": <number or null>,
  "reward_point_value_paise": <number or null>,
  "accelerated_categories": [
    {"category": "dining|travel|online|grocery|fuel|entertainment|all", "multiplier": <number>, "note": "context"}
  ],
  "lounge_domestic_annual": <number or "unlimited" or null>,
  "lounge_international_annual": <number or "unlimited" or null>,
  "forex_markup_pct": <number or null>,
  "fuel_surcharge_waiver": <true or false>,
  "welcome_benefit_value": <number or null>,
  "milestone_benefits": ["..."],
  "other_perks": ["..."],
  "card_type": "cashback|rewards|travel|lifestyle|premium",
  "best_for": ["category1", "category2"]
}
```

If a fetch fails, use training knowledge for that card and mark it `"source": "training"`. Otherwise mark it `"source": "live"`.

### Step 5 — Write database

Use the Write tool to save to `~/.india-cards/cards.json`:

```json
{
  "last_updated": "<ISO timestamp>",
  "cards": {
    "<card-id>": { ...data, "id": "<card-id>", "official_url": "...", "last_fetched": "...", "source": "live|training" }
  }
}
```

### Report

- How many cards fetched live vs from training knowledge
- Confirm: "Database saved to ~/.india-cards/cards.json"
