#!/usr/bin/env bash
#
# Fires the Morning Brief workflow at the exact moment this script runs, by
# calling GitHub's workflow_dispatch API. Point a reliable scheduler at this
# (a server crontab, launchd, etc.) so the brief arrives at the same time every
# day instead of whenever GitHub's own cron gets around to it.
#
# For a zero-infrastructure setup (no always-on machine), use a hosted cron
# service to make the same HTTP POST directly. See docs/RELIABLE_TRIGGER.md.
#
# Required environment variables:
#   GH_DISPATCH_TOKEN  Fine-grained GitHub token with this repo's
#                      "Actions" permission set to Read and write.
#   GH_OWNER           The account that holds your fork (where the secrets are
#                      set and Actions runs).
#
# Optional overrides (defaults shown):
#   GH_REPO=My-Morning-Brief
#   GH_WORKFLOW=morning-brief.yml
#   GH_REF=main
#
set -euo pipefail

: "${GH_DISPATCH_TOKEN:?Set GH_DISPATCH_TOKEN to a fine-grained token with Actions: Read and write}"
: "${GH_OWNER:?Set GH_OWNER to the account that holds your fork}"

OWNER="${GH_OWNER}"
REPO="${GH_REPO:-My-Morning-Brief}"
WORKFLOW="${GH_WORKFLOW:-morning-brief.yml}"
REF="${GH_REF:-main}"

curl --fail --silent --show-error -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${GH_DISPATCH_TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW}/dispatches" \
  -d "{\"ref\":\"${REF}\"}"

echo "Dispatched ${WORKFLOW} on ${OWNER}/${REPO}@${REF}"
