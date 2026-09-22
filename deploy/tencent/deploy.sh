#!/usr/bin/env bash
set -euo pipefail

BRANCH="${BRANCH:-release/v34.152-r15.26-tencent-lighthouse}"
WEB_ROOT="${WEB_ROOT:-/var/www/exoticalloycn}"

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

echo "[1/7] Resolve release source"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git fetch --prune origin "$BRANCH"
  git checkout -B "$BRANCH" "origin/$BRANCH"
  SHA="$(git rev-parse HEAD)"
elif [[ -f RELEASE_PACKAGE_SHA ]]; then
  SHA="$(tr -d '[:space:]' < RELEASE_PACKAGE_SHA)"
  [[ "$SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "ERROR: invalid RELEASE_PACKAGE_SHA"; exit 1; }
else
  echo "ERROR: neither Git metadata nor RELEASE_PACKAGE_SHA is available."
  exit 1
fi
export TONGJUN_RELEASE_COMMIT="$SHA"
echo "Release commit: $SHA"

echo "[2/7] Build and validate production artifact"
npm run build:production

echo "[3/7] Materialize immutable static release"
RELEASE_DIR="$WEB_ROOT/releases/$SHA"
sudo mkdir -p "$RELEASE_DIR"
sudo rsync -a --delete _prod/ "$RELEASE_DIR/"
sudo chown -R root:www-data "$RELEASE_DIR"
sudo find "$RELEASE_DIR" -type d -exec chmod 0755 {} +
sudo find "$RELEASE_DIR" -type f -exec chmod 0644 {} +

echo "[4/7] Atomically switch current static release"
sudo mkdir -p "$WEB_ROOT/releases"
sudo ln -sfn "$RELEASE_DIR" "$WEB_ROOT/current"

echo "[5/7] Restart localhost API"
sudo systemctl restart tongjun-api.service

echo "[6/7] Validate and reload Nginx"
sudo nginx -t
sudo systemctl reload nginx

echo "[7/7] Local readiness probes"
STATUS="$(curl -sS -o /tmp/tongjun-health.json -w '%{http_code}' http://127.0.0.1:8787/api/health || true)"
cat /tmp/tongjun-health.json || true
echo
if [[ "$STATUS" != "200" && "$STATUS" != "503" ]]; then
  echo "ERROR: local API health returned HTTP $STATUS"
  exit 1
fi

curl -fsS --resolve exoticalloycn.com:443:127.0.0.1 https://exoticalloycn.com/ >/dev/null
echo "PASS: R15.26 deployed locally through Nginx. API health HTTP $STATUS."
if [[ "$STATUS" == "503" ]]; then
  echo "WARNING: RFQ route is not production-ready yet. Configure RFQ_WEBHOOK_URL and RFQ_SHARED_SECRET in /etc/tongjun-overseas.env."
fi

if [[ "${RUN_EXTERNAL_CHECK:-0}" == "1" ]]; then
  npm run check:production
fi
