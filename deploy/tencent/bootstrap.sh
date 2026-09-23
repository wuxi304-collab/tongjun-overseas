#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/tongjun-overseas/app}"
WEB_ROOT="${WEB_ROOT:-/var/www/exoticalloycn}"
SSL_CERT="${SSL_CERT:-/etc/letsencrypt/live/exoticalloycn.com/fullchain.pem}"
SSL_KEY="${SSL_KEY:-/etc/letsencrypt/live/exoticalloycn.com/privkey.pem}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo APP_DIR=... SSL_CERT=... SSL_KEY=... bash deploy/tencent/bootstrap.sh"
  exit 1
fi

for bin in nginx node git rsync curl python3; do
  command -v "$bin" >/dev/null || { echo "Missing prerequisite: $bin"; exit 1; }
done
[[ -f "$SSL_CERT" ]] || { echo "SSL certificate not found: $SSL_CERT"; exit 1; }
[[ -f "$SSL_KEY" ]] || { echo "SSL private key not found: $SSL_KEY"; exit 1; }

mkdir -p "$WEB_ROOT/releases"
chown root:www-data "$WEB_ROOT" "$WEB_ROOT/releases"
chmod 0755 "$WEB_ROOT" "$WEB_ROOT/releases"

# Delivery ledger directory. Owned by the API user so `ProtectSystem=full` still allows
# appends, and mode 0750 so the inquiry metadata is not world readable.
LEDGER_DIR="${LEDGER_DIR:-/var/lib/tongjun-rfq}"
mkdir -p "$LEDGER_DIR"
chown www-data:www-data "$LEDGER_DIR"
chmod 0750 "$LEDGER_DIR"

if [[ ! -f /etc/tongjun-overseas.env ]]; then
  install -m 0600 "$ROOT/deploy/tencent/tongjun-overseas.env.example" /etc/tongjun-overseas.env
  echo "Created /etc/tongjun-overseas.env. Fill RFQ_MAIL_TRANSPORT, RFQ_MAIL_TO, RFQ_MAIL_FROM and the transport credentials before launch."
else
  chmod 0600 /etc/tongjun-overseas.env
fi

sed   -e "s|__APP_DIR__|$APP_DIR|g"   "$ROOT/deploy/tencent/tongjun-api.service.template"   > /etc/systemd/system/tongjun-api.service

sed   -e "s|__WEB_ROOT__|$WEB_ROOT|g"   -e "s|__SSL_CERT__|$SSL_CERT|g"   -e "s|__SSL_KEY__|$SSL_KEY|g"   "$ROOT/deploy/tencent/nginx-exoticalloycn.conf.template"   > /etc/nginx/sites-available/exoticalloycn.conf

ln -sfn /etc/nginx/sites-available/exoticalloycn.conf /etc/nginx/sites-enabled/exoticalloycn.conf
rm -f /etc/nginx/sites-enabled/default

systemctl daemon-reload
systemctl enable tongjun-api.service
nginx -t
systemctl reload nginx

echo "PASS: Tencent Lighthouse service templates installed."
echo "Next: edit /etc/tongjun-overseas.env, then run deploy/tencent/deploy.sh from $APP_DIR."
