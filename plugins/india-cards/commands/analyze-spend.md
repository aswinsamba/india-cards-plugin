---
description: Analyse a bank statement and extract spend patterns by category
argument-hint: <path-to-statement.csv|pdf|txt>
allowed-tools: [Read, Bash]
---

# Analyse Spend

Read the bank statement and produce a structured spend breakdown that `/recommend-cards` can use.

## Statement File
$ARGUMENTS

## Instructions

1. Read the statement file at the path provided.

2. Parse all debit/spend transactions. The file may be CSV, plain text, or a text export from a PDF. Common column patterns:
   - CSV: Date, Description/Narration, Debit, Credit, Balance
   - Text: lines like "15 Mar 2026  SWIGGY  500.00 Dr"
   - Skip credit/reversal entries (they're refunds, not spend)

3. For each spend transaction, classify into exactly one of these categories:
   - **dining** — restaurants, cafes, Zomato, Swiggy, EazyDiner, food delivery
   - **grocery** — BigBasket, Blinkit, Zepto, DMart, supermarkets, kirana
   - **travel** — flights, hotels, MakeMyTrip, Yatra, Ixigo, IRCTC, Uber, Ola, Rapido, cabs
   - **fuel** — petrol pumps, HPCL, BPCL, Indian Oil
   - **online_shopping** — Amazon, Flipkart, Myntra, Meesho, Nykaa, electronics, apparel
   - **entertainment** — BookMyShow, Netflix, Hotstar, Spotify, cinema, gaming
   - **utilities** — electricity, BESCOM, MSEB, internet, Airtel, Jio, BSNL, mobile recharge, water, piped gas
   - **health** — pharmacy, hospitals, Netmeds, Apollo, 1mg, doctors, diagnostics
   - **insurance** — LIC, health insurance, car insurance premiums
   - **emi** — loan EMIs, credit card EMIs (from another card)
   - **international** — any foreign currency transaction or international merchant
   - **other** — anything that doesn't fit the above

4. Compute totals. If the statement covers multiple months, compute monthly averages.

5. Write this JSON to `/tmp/spend_analysis.json`:
```json
{
  "source_file": "<filename>",
  "period_start": "YYYY-MM",
  "period_end": "YYYY-MM",
  "months_covered": 3,
  "total_spend": 45000,
  "monthly_avg_spend": 15000,
  "categories": {
    "dining":          {"total": 6000,  "monthly_avg": 2000, "pct": 13.3},
    "grocery":         {"total": 4500,  "monthly_avg": 1500, "pct": 10.0},
    "travel":          {"total": 9000,  "monthly_avg": 3000, "pct": 20.0},
    "fuel":            {"total": 3000,  "monthly_avg": 1000, "pct": 6.7},
    "online_shopping": {"total": 7500,  "monthly_avg": 2500, "pct": 16.7},
    "entertainment":   {"total": 1500,  "monthly_avg": 500,  "pct": 3.3},
    "utilities":       {"total": 3000,  "monthly_avg": 1000, "pct": 6.7},
    "health":          {"total": 1500,  "monthly_avg": 500,  "pct": 3.3},
    "insurance":       {"total": 3000,  "monthly_avg": 1000, "pct": 6.7},
    "emi":             {"total": 0,     "monthly_avg": 0,    "pct": 0},
    "international":   {"total": 6000,  "monthly_avg": 2000, "pct": 13.3},
    "other":           {"total": 0,     "monthly_avg": 0,    "pct": 0}
  },
  "top_merchants": [
    "Amazon: ₹4500",
    "Swiggy: ₹3000",
    "MakeMyTrip: ₹9000"
  ],
  "annual_projected_spend": 180000,
  "notes": "3 months of HDFC account statement"
}
```

6. Print a clean readable summary:
   - Total monthly spend
   - Top 4 categories with ₹ amounts and %
   - Any notable patterns (e.g. heavy international spend, high dining)
   - Confirm: "Saved to /tmp/spend_analysis.json — run /recommend-cards to get card suggestions."
