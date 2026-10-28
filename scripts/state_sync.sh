#!/usr/bin/env bash
# Persist the SQLite state + data files on a separate `state` branch between workflow runs.
#   scripts/state_sync.sh pull   -> copies state/ and data/ from the state branch (if it exists)
#   scripts/state_sync.sh push   -> commits state/ and data/ to the state branch (retries on conflict)
set -euo pipefail
cmd="${1:?pull|push}"
BR=state
git config user.name  "shorts-bot"
git config user.email "shorts-bot@users.noreply.github.com"
if [[ "$cmd" == "pull" ]]; then
  if git ls-remote --exit-code --heads origin "$BR" >/dev/null 2>&1; then
    git fetch -q origin "$BR"
    mkdir -p state data
    for db in live.db dryrun.db; do git show "origin/$BR:state/$db" > "state/$db" 2>/dev/null || rm -f "state/$db"; done
    for f in signals.json insights.json LEARNINGS.md; do git show "origin/$BR:data/$f" > "data/$f" 2>/dev/null || rm -f "data/$f"; done
    echo "state restored"
  else
    echo "no state branch yet - starting fresh"
  fi
elif [[ "$cmd" == "push" ]]; then
  tmp=$(mktemp -d)
  cp -r state data "$tmp"/ 2>/dev/null || true
  for attempt in 1 2 3; do
    rm -rf .state-wt && git worktree prune
    if git ls-remote --exit-code --heads origin "$BR" >/dev/null 2>&1; then
      git fetch -q origin "$BR" && git worktree add -q .state-wt "origin/$BR" && (cd .state-wt && git checkout -q -B "$BR")
    else
      git worktree add -q --detach .state-wt && (cd .state-wt && git checkout -q --orphan "$BR" && git rm -rqf . )
    fi
    mkdir -p .state-wt/state .state-wt/data
    cp "$tmp"/state/*.db .state-wt/state/ 2>/dev/null || true
    cp "$tmp"/data/*.json "$tmp"/data/*.md .state-wt/data/ 2>/dev/null || true
    (cd .state-wt && git add -A && (git diff --cached --quiet || git commit -qm "state: $(date -u +%FT%TZ) ${GITHUB_WORKFLOW:-local}") && git push -q origin "$BR") && break
    echo "push conflict, retrying ($attempt)"; sleep $((attempt * 5))
  done
  rm -rf .state-wt "$tmp"; git worktree prune
fi
