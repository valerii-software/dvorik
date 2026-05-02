#!/usr/bin/env bash
# In-place deploy on the EC2 host.
#
# Usage (from /opt/dvorik):
#   ./scripts/deploy.sh
#
# Pulls the latest main, rebuilds containers, runs migrations on
# startup (Dockerfile CMD already does collectstatic + migrate),
# then prints the new HEAD and verifies /healthz/.

set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> git fetch + fast-forward to origin/main"
git fetch origin
git checkout main
git pull --ff-only

echo
echo "==> rebuild & restart"
sudo docker compose up -d --build

echo
echo "==> wait for /healthz/"
for i in $(seq 1 30); do
    code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 3 http://localhost/healthz/ || true)
    if [ "$code" = "200" ]; then
        echo "    healthz OK"
        break
    fi
    sleep 2
done

echo
echo "==> deployed:"
git log --oneline -1
sudo docker compose ps
