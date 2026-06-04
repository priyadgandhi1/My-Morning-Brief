# My Morning Brief

A daily news briefing, written by Claude and delivered to your Telegram every morning. It pulls fresh stories from a handful of RSS feeds, asks Claude to distill them into a tight, scannable summary, and sends the result to you as a Telegram message. The whole thing runs for free on GitHub Actions; no server required.

## How it works

1. A scheduled GitHub Actions workflow runs `brief.py` once a day (11:00 UTC by default).
2. The script fetches recent items (last 24 hours) from RSS feeds across four categories: Markets & Macro, Headlines & Politics, Consumer & Retail, and PE / VC / M&A.
3. Claude turns the raw headlines into a briefing under 400 words, organized by category.
4. The briefing is sent to you via your Telegram bot.

## Setup

### 1. Fork or clone this repo

Click **Fork** on GitHub, or clone it and push to your own repository.

### 2. Get your three secrets

| Secret | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | Create an API key at [console.anthropic.com](https://console.anthropic.com/) |
| `TELEGRAM_BOT_TOKEN` | Message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`, and follow the prompts |
| `TELEGRAM_CHAT_ID` | Message your new bot first (send it anything), then visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` and copy the `chat.id` value from the response |

### 3. Add the secrets to GitHub

In your repo, go to **Settings → Secrets and variables → Actions → New repository secret** and add all three.

### 4. Test it

Go to the **Actions** tab, select **Morning Brief**, and click **Run workflow**. Within a minute or two you should get a briefing on Telegram.

That's it. The workflow will now run automatically every day.

## Running locally

```bash
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...
export TELEGRAM_BOT_TOKEN=123456:ABC...
export TELEGRAM_CHAT_ID=123456789

python brief.py
```

## Customizing

### Change the news sources

Edit the `FEEDS` list at the top of `brief.py`. Each entry is a `(Category, RSS URL)` pair; add or remove feeds freely. If you add a new category, also mention it in the prompt inside `summarize_with_claude` so Claude knows the section order.

### Change the delivery time

Edit the cron expression in `.github/workflows/morning-brief.yml`. The schedule is in UTC, so for example:

```yaml
- cron: "0 11 * * *"   # 11:00 UTC = 7:00 AM ET (winter) / 6:00 AM ET (summer)
```

Note that GitHub Actions cron schedules can start a few minutes late during busy periods.

### Tune the briefing

A few knobs near the top of `brief.py`:

- `LOOKBACK_HOURS`: how far back to look for news (default 24).
- `MAX_ITEMS_PER_FEED`: cap on items per feed to keep the prompt lean (default 8).
- The prompt in `summarize_with_claude` controls the tone, length, and structure of the briefing itself.

## Cost

One short Claude request per day. With the default settings this typically costs a few cents per day or less. GitHub Actions and Telegram are free.
