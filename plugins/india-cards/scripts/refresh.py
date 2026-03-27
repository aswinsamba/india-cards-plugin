#!/usr/bin/env python3
"""
Refresh Indian credit card database from official bank benefit pages.

Usage:
    python3 refresh.py                 # refresh all cards
    python3 refresh.py --card hdfc-regalia-gold  # refresh one card

Requirements:
    pip3 install requests beautifulsoup4 anthropic --break-system-packages
    ANTHROPIC_API_KEY must be set in environment
"""

import json
import sys
import time
from pathlib import Path

import anthropic
import requests
from bs4 import BeautifulSoup

PLUGIN_DIR = Path(__file__).parent.parent
URLS_FILE  = PLUGIN_DIR / "data" / "card_urls.json"
CARDS_FILE = Path.home() / ".india-cards" / "cards.json"
CARDS_FILE.parent.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

EXTRACTION_PROMPT = """\
You are extracting structured credit card benefit data from an Indian bank's official benefits page.

Return ONLY valid JSON with this exact schema — no markdown, no explanation:
{{
  "name": "full card name as shown on page",
  "issuer": "bank name",
  "joining_fee": <number or null>,
  "annual_fee": <number or null>,
  "fee_waiver_spend_lakhs": <number or null, e.g. 4.0 means ₹4 lakh annual spend>,
  "base_reward_points_per_100": <number or null, base earn rate per ₹100 spent>,
  "reward_point_value_paise": <number or null, approx paise per point, e.g. 50 means ₹0.50>,
  "accelerated_categories": [
    {{"category": "dining|travel|online|grocery|fuel|entertainment|all", "multiplier": <number>, "note": "optional context"}}
  ],
  "lounge_domestic_annual": <number or "unlimited" or null>,
  "lounge_international_annual": <number or "unlimited" or null>,
  "forex_markup_pct": <number or null, e.g. 2.0>,
  "fuel_surcharge_waiver": <true or false>,
  "welcome_benefit_value": <number or null, approx ₹ value of welcome gift>,
  "milestone_benefits": ["short description each"],
  "insurance_covers": ["short description each"],
  "other_perks": ["short description each, max 6 items"],
  "card_type": "cashback|rewards|travel|lifestyle|premium",
  "best_for": ["category1", "category2"]
}}

If a field is genuinely not mentioned on the page, use null.
Do not guess or extrapolate beyond what the page says.

Page content:
{content}"""


def fetch_page(url: str) -> str | None:
    """Fetch page and return cleaned text, or None on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"    [WARN] HTTP error: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # Deduplicate blank lines
    lines = [l for l in text.splitlines() if l.strip()]
    text = "\n".join(lines)

    # Limit to ~8000 chars — enough for benefits content, fits in Haiku context
    if len(text) > 8000:
        text = text[:8000]

    # Sanity check: if content is too thin, the page is probably JS-rendered
    if len(text) < 300:
        print(f"    [WARN] Very thin content ({len(text)} chars) — page may be JS-rendered")
        print(f"           Try opening in a browser and check if benefits are visible")

    return text


def extract_benefits(client: anthropic.Anthropic, card_id: str, url: str) -> dict | None:
    """Fetch page and use Claude Haiku to extract structured benefits."""
    content = fetch_page(url)
    if not content:
        return None

    print(f"    Parsing with Claude ({len(content)} chars)...")
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": EXTRACTION_PROMPT.format(content=content),
        }],
    )

    raw = msg.content[0].text.strip()

    # Strip markdown fences if model adds them anyway
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"    [WARN] JSON parse failed: {e}")
        print(f"    Raw output: {raw[:300]}")
        return None


def main():
    if not URLS_FILE.exists():
        print(f"[ERROR] card_urls.json not found at {URLS_FILE}")
        sys.exit(1)

    urls_data: dict = json.loads(URLS_FILE.read_text())

    # Load or initialise the database
    if CARDS_FILE.exists():
        db = json.loads(CARDS_FILE.read_text())
    else:
        db = {"last_updated": None, "cards": {}}

    # Determine scope
    if len(sys.argv) == 3 and sys.argv[1] == "--card":
        target_id = sys.argv[2]
        if target_id not in urls_data:
            print(f"[ERROR] Unknown card id: {target_id}")
            print(f"Known ids: {', '.join(urls_data.keys())}")
            sys.exit(1)
        to_refresh = {target_id: urls_data[target_id]}
    else:
        to_refresh = urls_data

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    ok, failed = 0, []
    print(f"Refreshing {len(to_refresh)} card(s)...\n")

    for card_id, meta in to_refresh.items():
        print(f"[{card_id}]  {meta['name']}")
        print(f"    {meta['url']}")

        data = extract_benefits(client, card_id, meta["url"])

        if data:
            data["id"]            = card_id
            data["official_url"]  = meta["url"]
            data["last_fetched"]  = time.strftime("%Y-%m-%dT%H:%M:%S")
            db["cards"][card_id]  = data
            print(f"    OK")
            ok += 1
        else:
            failed.append(card_id)
            print(f"    SKIPPED (kept previous data if any)")

        time.sleep(1.2)  # polite rate limiting

    db["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    CARDS_FILE.write_text(json.dumps(db, indent=2, ensure_ascii=False))

    print(f"\n{'='*50}")
    print(f"Done. {ok} updated, {len(failed)} failed.")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        print(f"Tip: JS-rendered pages need Playwright. Run:")
        print(f"  pip3 install playwright && playwright install chromium")
        print(f"  Then use scripts/refresh_playwright.py for those cards.")
    print(f"Database: {CARDS_FILE}")


if __name__ == "__main__":
    main()
