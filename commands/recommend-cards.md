---
description: Recommend the best Indian credit cards based on your spend patterns
argument-hint: [path-to-spend-analysis.json]
allowed-tools: [Read, Bash]
---

# Recommend Cards

Compare your spend patterns against the card database and rank the best options for you.

## Arguments
$ARGUMENTS

## Instructions

### Step 1 — Load spend data

Read the spend analysis from:
- The path in `$ARGUMENTS` if provided
- Otherwise `/tmp/spend_analysis.json`

If neither exists, tell the user: "No spend analysis found. Run `/analyze-spend <your-statement>` first."

### Step 2 — Load card database

Read `~/.india-cards/cards.json`.

If `last_updated` is null or more than 14 days ago:
> "Card database is stale or empty. Run `/refresh-cards` to populate it from official bank pages."

If the file has fewer than 5 cards, suggest refreshing anyway.

### Step 3 — Score each card

For every card in the database, calculate:

**Annual reward value (₹):**
```
For each spend category:
  category_annual_spend = spend.categories[cat].monthly_avg × 12
  points_earned = category_annual_spend / 100 × base_reward_points_per_100

  If card has accelerated rate for this category:
    points_earned = points_earned × multiplier

  reward_value += points_earned × (reward_point_value_paise / 100)
```

**Relevant perks value (estimate ₹):**
- Domestic lounge access: ₹800 per visit (if they travel, use estimated 4–8 visits/year)
- International lounge access: ₹2500 per visit
- Dining discount: if dining monthly_avg > ₹3000, estimate 15% of annual dining
- Fuel surcharge waiver: 1% of annual fuel spend
- Welcome benefit: add once (joining year only)
- Movie offers (if entertainment > ₹500/month): ₹300/month

**Net annual benefit:**
```
net = reward_value + perks_value − annual_fee + (fee_waiver_spend_lakhs × 100000 > annual_projected_spend ? 0 : annual_fee)
```
(If the user's annual spend clears the fee waiver threshold, treat annual fee as ₹0.)

### Step 4 — Present top 5

Rank by net annual benefit, highest first. Format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#1  HDFC Regalia Gold (HDFC Bank)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Annual fee   : ₹2,500  (waived at ₹4L spend — you spend ₹X/yr → fee likely waived)
Reward value : ₹4,200/yr
Perks value  : ₹3,600/yr  (4× domestic lounge + dining discount)
Net benefit  : ₹5,300/yr

Why this works for you:
• You spend ₹3,000/mo on dining → 4 pts per ₹150 + 20% off via Swiggy Dineout
• You spend ₹9,000/mo on travel → 5X on select travel brands
• Fee likely waived (annual spend > ₹4L)

Best for: travel + dining
Official page: https://www.hdfcbank.com/...
```

### Step 5 — Show what you're missing

After the top 5, add a short section:
```
━━ Cards not recommended for your profile ━━
• SBI SimplyCLICK — optimised for online shopping; your online spend is too low
• Axis Atlas — best for international travel; you have limited forex spend
```

### Step 6 — Key caveat

End with:
> **Note:** Reward calculations are estimates based on stated earn rates. Actual value depends on which redemption options you use (statement credit is typically lower value than airline miles or gift vouchers). Card terms change — verify current rates at the official page before applying.
