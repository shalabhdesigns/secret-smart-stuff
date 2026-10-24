#!/usr/bin/env bash
# Publish the review bundle for a job: a pre-release holding the MP4 + files, and an issue.
set -euo pipefail
JOB="${1:?job id}"
D="build/$JOB"
TAG="review-$JOB"
gh label create review --color 1D76DB 2>/dev/null || true
files=("$D/final.mp4" "$D/metadata.json" "$D/script.json" "$D/review.md")
if gh release view "$TAG" >/dev/null 2>&1; then
  gh release upload "$TAG" "${files[@]}" --clobber
else
  gh release create "$TAG" "${files[@]}" --prerelease --title "Review: $JOB" --notes "Review bundle for $JOB (not published)."
fi
url=$(gh release view "$TAG" --json assets -q '.assets[] | select(.name=="final.mp4") | .url')
{
  echo "<!-- job:$JOB -->"
  echo "🎬 **Watch the Short:** $url"
  echo
  cat "$D/review.md"
} > issue.md
existing=$(gh issue list --label review --state open --limit 100 --json number,body \
  -q ".[] | select(.body | contains(\"<!-- job:$JOB -->\")) | .number" | head -1)
if [ -n "$existing" ]; then
  gh issue comment "$existing" --body-file issue.md
else
  title=$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["title"][:80])' "$D/metadata.json")
  gh issue create --label review --title "Review: $title" --body-file issue.md
fi
