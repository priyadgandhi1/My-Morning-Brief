# Morning Brief

A daily news briefing that fetches headlines from RSS feeds, has Claude
organize them into four categories, and sends the result to you on Telegram.
Runs free on GitHub Actions every morning.

Categories: Markets & Macro, Headlines & Politics, Consumer & Retail, PE/VC/M&A.

---

## One-time setup

### 1. Telegram
1. Install Telegram on your iPhone.
2. Message @BotFather, send `/newbot`, follow the prompts. Save the **bot token**.
3. Message @userinfobot to get your numeric **chat ID**. Save it.
4. Open your new bot and send it any message (a bot cannot message you first).

### 2. Anthropic API
1. Go to console.anthropic.com, sign up, add ~$5 credit under Billing.
2. Create an API key under API Keys. Save it (starts with `sk-ant-`).

### 3. GitHub
1. Create a free account at github.com if you don't have one.
2. Create a new repository (name it anything, e.g. `morning-brief`). Private is fine.
3. Upload these files into it (drag and drop in the web UI works):
   - `brief.py`
   - `requirements.txt`
   - `.github/workflows/morning-brief.yml`  (keep this exact folder path)

### 4. Add your secrets
In your repo: **Settings > Secrets and variables > Actions > New repository secret.**
Add three, named exactly:
   - `ANTHROPIC_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### 5. Test it
Go to the **Actions** tab in your repo, pick "Morning Brief", click
**Run workflow**. Within a minute you should get a Telegram message.

---

## Customizing

- **News sources:** edit the `FEEDS` list near the top of `brief.py`.
- **Send time:** edit the `cron` line in `morning-brief.yml`. It uses UTC.
  `0 11 * * *` is 11:00 UTC = roughly 7am US Eastern. For 7am Eastern during
  standard time (winter) use `0 12 * * *`. GitHub does not adjust for DST,
  so you may nudge it by an hour twice a year.
- **Style/length:** edit the `prompt` text inside `summarize_with_claude`.

## Cost
- Telegram: free. GitHub Actions: free for this. Anthropic API: a few cents/day.
