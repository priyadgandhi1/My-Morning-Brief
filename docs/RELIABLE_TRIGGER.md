# Reliable delivery time

The brief used to run on GitHub's built-in `schedule:` cron. That cron is
best-effort. During busy periods GitHub queues scheduled runs behind everything
else, so a job set for 11:00 can land at 14:00 one day and 17:00 the next. The
delay is always late, never early, and never the same twice. That is why the
brief was arriving at random times.

The fix is to stop asking GitHub to keep time and to fire the run ourselves from
a scheduler that is punctual. The workflow now exposes only `workflow_dispatch`,
which a scheduler triggers through the GitHub API at the exact minute we choose.
Same minute, every day.

You have two ways to set this up. The hosted path needs no server. The
self-hosted path uses a machine you already keep running.

## What you need either way

A GitHub token that is allowed to start the workflow.

1. Open GitHub, then Settings, then Developer settings, then Fine-grained
   tokens, then Generate new token.
2. Limit the token to this repository only.
3. Under Repository permissions, set **Actions** to **Read and write**. Leave
   everything else as No access.
4. Give it a long expiry and copy the token somewhere safe. You will paste it
   into the scheduler below.

## Path A, hosted scheduler (recommended, no server)

A free cron service makes the API call for you. cron-job.org is a good fit
because it lets you set the timezone directly, so it handles daylight saving
without any math.

1. Create a free account at cron-job.org and add a new cron job.
2. Set the URL to the one below, replacing `OWNER` with the account that holds
   your fork (the one where the secrets are set and Actions runs):
   `https://api.github.com/repos/OWNER/My-Morning-Brief/actions/workflows/morning-brief.yml/dispatches`
3. Set the request method to **POST**.
4. Add the request body: `{"ref":"main"}`
5. Add three request headers:
   - `Accept: application/vnd.github+json`
   - `Authorization: Bearer YOUR_TOKEN_HERE`
   - `X-GitHub-Api-Version: 2022-11-28`
6. Set the schedule to your delivery time and pick your timezone (for the
   morning brief, something like 7:00 in your local zone).
7. Save, then use the service's Run now button once to confirm the brief fires.

A successful dispatch returns an empty response with status 204. If you get 401
the token is wrong or lacks the Actions permission. If you get 404 the workflow
file name, owner, or repo in the URL does not match.

## Path B, self-hosted cron

If you keep a machine running, point its scheduler at `trigger.sh` in the repo
root. The script wraps the same API call and reads the token from an
environment variable.

1. Store the token as `GH_DISPATCH_TOKEN` and your fork's account as `GH_OWNER`.
2. Test it once by hand: `GH_DISPATCH_TOKEN=... GH_OWNER=your-username ./trigger.sh`
3. Add a crontab entry for your delivery time. Remember that crontab uses the
   machine's local time, so set the hour accordingly. For 7:00 every day:

   ```
   0 7 * * * GH_DISPATCH_TOKEN=your_token GH_OWNER=your-username /path/to/My-Morning-Brief/trigger.sh
   ```

## Why there is no GitHub-only fix

GitHub does not promise on-time scheduled runs, and the top of the hour is the
most contested slot of all because it is where most people schedule. Moving the
cron a few minutes past the hour reduces the jitter but never removes it, and
runs can still be dropped under heavy load. An external trigger is the only way
to get a delivery time you can set your morning around.
