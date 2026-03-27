---
description: Refresh the Indian credit card database from official bank benefit pages
argument-hint: [card-id]
allowed-tools: [Read, Write, WebFetch, Bash]
---

# Refresh Card Database

Fetch official bank benefit pages and extract structured card data.
Uses WebFetch — no API key needed.

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

### Determine scope

If `$ARGUMENTS` contains a card ID, process only that entry from the catalogue above.
Otherwise process all 20 cards.

### For each card:

1. Use the URL from the catalogue above.

2. Fetch the page using WebFetch with this prompt:
   > "Extract ALL credit card benefits, fees, reward rates, lounge access, and perks mentioned on this page. Return raw text — do not summarise."

3. From the returned content, extract this structure:
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

4. After processing all cards, write the updated database to `~/.india-cards/cards.json`.
   First ensure the directory exists: run `mkdir -p ~/.india-cards` via Bash.
   Then use the Write tool to save to `~/.india-cards/cards.json`:
```json
{
  "last_updated": "<ISO timestamp>",
  "cards": {
    "<card-id>": { ...extracted data, "id": "<card-id>", "official_url": "...", "last_fetched": "..." },
    ...
  }
}
```

### Report

After finishing:
- How many cards updated successfully
- Any that returned thin/empty content (likely JS-rendered — note them but continue)
- Confirm: "Database saved to ~/.india-cards/cards.json"
