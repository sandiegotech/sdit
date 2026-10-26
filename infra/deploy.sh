#!/usr/bin/env bash
# Deploy learn.sandiegotech.org — stack, then site, then cache invalidation.
#
# This IS the deploy: since 2026-10-26 the Cloudflare record for the domain
# points at this distribution (DNS only), and GitHub Pages is out of the path.
# Pushing to main runs the checks but publishes nothing. The sync walks the
# working tree, not git, so anything uncommitted in the folder goes live too.
#
#   ./deploy.sh            # stack + site
#   ./deploy.sh --site     # site only (skip the CloudFormation step)
set -euo pipefail

STACK=sdit-learn-web
REGION=us-west-2
DOMAIN=learn.sandiegotech.org
CERT_ARN=arn:aws:acm:us-east-1:681432799403:certificate/59fb1783-88f3-4e97-a036-a48abcf4679b

cd "$(dirname "$0")"
SITE_ROOT="$(cd .. && pwd)"

# The account API is a separate stack; read its endpoint rather than hardcoding
# it, so a redeploy of that stack can't leave this one pointing at a dead host.
API_URL=$(aws cloudformation describe-stacks \
  --stack-name sdit-account --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
API_DOMAIN=${API_URL#https://}
API_DOMAIN=${API_DOMAIN%/}
WORK_DOMAIN=$(aws cloudformation describe-stacks \
  --stack-name sdit-account --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='WorkBucketDomain'].OutputValue" --output text)

if [ "${1:-}" != "--site" ]; then
  echo "→ Deploying stack $STACK (API origin: $API_DOMAIN)"
  aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name "$STACK" \
    --region "$REGION" \
    --no-fail-on-empty-changeset \
    --parameter-overrides \
      DomainName="$DOMAIN" \
      CertificateArn="$CERT_ARN" \
      ApiDomain="$API_DOMAIN" \
      WorkBucketDomain="$WORK_DOMAIN"
fi

# Look each output up by name. A single multi-key query returns them in
# CloudFormation's order, not the order they were asked for, so positional
# reads silently assign the wrong value to the wrong variable.
stack_output() {
  aws cloudformation describe-stacks \
    --stack-name "$STACK" --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text
}

BUCKET=$(stack_output BucketName)
DIST_ID=$(stack_output DistributionId)
DIST_DOMAIN=$(stack_output DistributionDomain)

for v in BUCKET DIST_ID DIST_DOMAIN; do
  if [ -z "${!v}" ]; then echo "error: stack output for $v is empty" >&2; exit 1; fi
done

# The edge function decides directory-vs-page from a fixed list plus a
# course-code pattern (see template.yaml). A directory it does not recognise
# gets served as <name>.html and 404s — silently, and only for the extensionless
# form, which is exactly the form nobody tests. Catch it at deploy time.
UNKNOWN=$(cd "$SITE_ROOT" && find . -name index.html \
    -not -path './.git/*' -not -path './account/*' -not -path './infra/*' \
    -not -path './node_modules/*' -not -path './dist/*' \
  | sed 's|^\./||; s|/index\.html$||' \
  | grep -v '^index\.html$' \
  | grep -vE '^(courses|curriculum|begin|portfolio|notebook|programs/Bachelor-Liberal-Arts)$' \
  | grep -vE '^courses/[A-Z]+-[0-9]+$' \
  | grep -vE '^gates/semester-[1-8]$' || true)

if [ -n "$UNKNOWN" ]; then
  echo "error: directories unknown to the edge function in template.yaml:" >&2
  echo "$UNKNOWN" | sed 's/^/  /' >&2
  echo "Add them to DIRS in template.yaml, then redeploy." >&2
  exit 1
fi

# The release gate: day pages written ahead of knowledge/calendar.yaml's
# released_through stay on this machine until their Monday. They are listed
# by the calendar, not by date, so the site changes by decision.
UNRELEASED=()
while IFS= read -r rel; do
  [ -n "$rel" ] && UNRELEASED+=(--exclude "$rel")
done < <(cd "$SITE_ROOT" && python3 scripts/publishing.py --unreleased-paths)
echo "→ Holding back ${#UNRELEASED[@]} unreleased path exclusion(s)"

echo "→ Syncing site to s3://$BUCKET"
# --delete keeps the bucket an exact mirror of the repo, so a file removed here
# disappears from the site. Everything excluded below is source, not site:
# account/ and infra/ are deploy code, scripts/ is the Python build tooling.
aws s3 sync "$SITE_ROOT" "s3://$BUCKET" \
  --delete \
  --exclude ".git/*" \
  --exclude ".github/*" \
  --exclude ".vscode/*" \
  --exclude ".DS_Store" \
  --exclude "account/*" \
  --exclude "infra/*" \
  --exclude "scripts/*" \
  --exclude "dist/*" \
  --exclude "knowledge/*" \
  --exclude "PLAN.md" \
  --exclude "AUTHORING.md" \
  --exclude "my-work/*" \
  --exclude "serve.py" \
  --exclude "CNAME" \
  --exclude ".nojekyll" \
  --exclude "wrangler.toml" \
  --exclude "*.md" \
  "${UNRELEASED[@]}"

# HTML is cached at the edge under the CachingOptimized policy, so a sync alone
# would leave stale pages served for hours. "/*" counts as ONE path against the
# 1,000-per-month free allowance, not one per file.
echo "→ Invalidating CloudFront cache"
aws cloudfront create-invalidation \
  --distribution-id "$DIST_ID" --paths "/*" \
  --query 'Invalidation.Id' --output text

echo
echo "Done. Live at https://$DOMAIN (DNS cut over 2026-10-26); the distribution itself answers at https://$DIST_DOMAIN."
