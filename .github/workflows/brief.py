"""
Morning Brief: fetches news from RSS feeds, has Claude organize it into a categorized briefing, and sends it to you on Telegram.

Reads three secrets from environment variables (set in GitHub):
  ANTHROPIC_API_KEY
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""

import os
import sys
from datetime import datetime, timezone, timedelta

import feedparser
import requests

# ---------------------------------------------------------------------------
# 1. NEWS SOURCES
#    Add or remove feeds freely. Each entry is (Category, RSS URL).
#    These four categories match what you asked for.
# ---------------------------------------------------------------------------
FEEDS = [
    # Markets & macro
    ("Markets & Macro", "https://feeds.content.dowjones.io/public/rss/mw_marketpulse"),
    ("Markets & Macro", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),  # CNBC markets
    # Top headlines & politics
    ("Headlines & Politics", "https://feeds.npr.org/1001/rss.xml"),  # NPR top news
    ("Headlines & Politics", "https://rss.politico.com/politics-news.xml"),
    # Consumer & retail
    ("Consumer & Retail", "https://www.retaildive.com/feeds/news/"),
    # PE / VC / M&A
    ("PE / VC / M&A", "https://www.pehub.com/feed/"),
    ("PE / VC / M&A", "https://news.crunchbase.com/feed/"),
]

# How far back to look for "today's" news.
LOOKBACK_HOURS = 24
# Cap items per feed so the prompt stays lean (and cheap).
MAX_ITEMS_PER_FEED = 8


def fetch_recent_items():
    """Pull recent entries from every feed, grouped by category."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    by_category = {}

    for category, url in FEEDS:
        try:
            parsed = feedparser.parse(url)
        except Exception as e:
            print(f"  ! could not read {url}: {e}", file=sys.stderr)
            continue

        count = 0
        for entry in parsed.entries:
            if count >= MAX_ITEMS_PER_FEED:
                break

            # Figure out the publish time; skip items older than cutoff.
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                if pub_dt < cutoff:
                    continue

            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()
            # Trim long summaries to keep the prompt tight.
            if len(summary) > 300:
                summary = summary[:300] + "..."

            if title:
                by_category.setdefault(category, []).append(
                    {"title": title, "summary": summary}
                )
                count += 1

    return by_category


def build_news_blob(by_category):
    """Turn the collected items into plain text to hand to Claude."""
    lines = []
    for category, items in by_category.items():
        lines.append(f"## {category}")
        for item in items:
            lines.append(f"- {item['title']}")
            if item["summary"]:
                lines.append(f"  {item['summary']}")
        lines.append("")
    return "\n".join(lines)


def summarize_with_claude(news_blob):
    """Ask Claude to write the briefing."""
    api_key = os.environ["ANTHROPIC_API_KEY"]
    today = datetime.now().strftime("%A, %B %d, %Y")

    prompt = f"""You are writing a concise morning news briefing for a busy
professional in strategy and finance. Today is {today}.

Below are raw news items grouped by category, pulled from RSS feeds in the
last {LOOKBACK_HOURS} hours. Write a tight, scannable briefing.

Rules:
- Keep it under 400 words total.
- Use these four sections, in this order, only if there is real news for them:
  Markets & Macro, Headlines & Politics, Consumer & Retail, PE / VC / M&A.
- Under each section, give 2 to 4 bullet points. Each bullet is one crisp
  sentence. Lead with what happened, then why it matters if relevant.
- Skip fluff, duplicates, and anything that is just an opinion column.
- Do not use em dashes anywhere.
- Start with a one line greeting that includes today's date. No sign-off.

Here are the raw items:

{news_blob}"""

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    # Concatenate any text blocks in the response.
    return "".join(
        block["text"] for block in data["content"] if block["type"] == "text"
    ).strip()


def send_telegram(text):
    """Send the briefing to yourself via your Telegram bot."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    # Telegram caps messages at 4096 chars; split if needed.
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)] or ["(no news today)"]
    for chunk in chunks:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": chunk},
            timeout=30,
        )
        resp.raise_for_status()


def main():
    print("Fetching news...")
    by_category = fetch_recent_items()
    total = sum(len(v) for v in by_category.values())
    print(f"  collected {total} items across {len(by_category)} categories")

    if total == 0:
        send_telegram("Morning brief: no fresh news found in the feeds today.")
        return

    news_blob = build_news_blob(by_category)
    print("Asking Claude to write the briefing...")
    briefing = summarize_with_claude(news_blob)

    print("Sending to Telegram...")
    send_telegram(briefing)
    print("Done.")


if __name__ == "__main__":
    main()
