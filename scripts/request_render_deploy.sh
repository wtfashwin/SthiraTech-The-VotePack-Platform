#!/usr/bin/env bash
# Request a deploy only after validating local configuration. Never log the hook.
set -euo pipefail

hook_url=${RENDER_DEPLOY_HOOK_URL:-}
if [[ -z "${hook_url//[[:space:]]/}" ]]; then
  echo "::error::Set the RENDER_DEPLOY_HOOK_URL Actions secret to the service's Render deploy hook before running this workflow." >&2
  exit 1
fi

if [[ "$hook_url" != https://api.render.com/deploy/* || "$hook_url" =~ [[:space:]] ]]; then
  echo "::error::RENDER_DEPLOY_HOOK_URL must be an HTTPS Render deploy hook copied from the service settings." >&2
  exit 1
fi

http_code=$(curl --silent --show-error --fail \
  --connect-timeout 10 --max-time 60 \
  --output /dev/null --write-out '%{http_code}' \
  --request POST --url "$hook_url")

case "$http_code" in
  200|202)
    echo "Render accepted the deployment request (HTTP $http_code). Check the service's Render deploy status; this does not confirm a completed deployment."
    ;;
  *)
    echo "::error::Render returned an unexpected HTTP status ($http_code); deployment was not confirmed." >&2
    exit 1
    ;;
esac
