#!/bin/bash
set -euo pipefail

HOSTNAME="db.qrurnpxrtfeuktkvtmki.supabase.co" # Replace if yours is different
echo "--- Startup Script Initiated ---"
echo "Attempting to resolve IPv4 address for: ${HOSTNAME}"
PG_IPV4=$(dig +short A "${HOSTNAME}" | head -n1 || true)

if [[ -n "${PG_IPV4}" ]]; then
    echo "Resolved ${HOSTNAME} -> ${PG_IPV4} (IPv4)."
    export PGHOSTADDR="${PG_IPV4}"
    echo "Exported PGHOSTADDR=${PG_IPV4} to force IPv4 connection."
else
    echo "Warning: Could not resolve IPv4 address for ${HOSTNAME}."
fi

echo "Setting PYTHONPATH to include the project source directory..."
export PYTHONPATH="${PYTHONPATH:-}:/opt/render/project/src"
echo "PYTHONPATH set to: $PYTHONPATH"

# Render sets PORT environment variable (default: 10000)
# Must bind to 0.0.0.0 to receive traffic from Render's load balancer
PORT=${PORT:-10000}
echo "Starting Uvicorn server on 0.0.0.0:${PORT}..."
exec uvicorn packages.api.main:app --host 0.0.0.0 --port "${PORT}"