# Tencent Lighthouse Deployment — exoticalloycn.com

Release: **V34.152 R15.26**
Branch: `release/v34.152-r15.26-tencent-lighthouse`

## Final topology

```
Internet
  |
  | 80 / 443
  v
Nginx
  |-- /, /assets/*, clean HTML routes -> /var/www/exoticalloycn/current
  |
  `-- /api/* -> 127.0.0.1:8787
                    |
                    `-- Node server/tongjun-api.js
                         |-- /api/health
                         `-- /api/rfq
```

The Node process is intentionally bound to localhost only. Do not expose port 8787 in the Tencent Lighthouse firewall.

## 0. Preconditions

Recommended host baseline:

- Ubuntu 22.04/24.04 LTS
- Nginx
- Node.js 20+ (22 LTS is preferred)
- Git
- Python 3
- rsync
- curl
- valid TLS certificate covering both `exoticalloycn.com` and `www.exoticalloycn.com`

Tencent Lighthouse firewall should expose only the ports required for administration and web traffic, normally 22, 80 and 443. Port 8787 remains private on `127.0.0.1`.

If the Lighthouse instance is located in mainland China, complete the required ICP filing/access filing before opening the domain to public traffic.

## 1. DNS

Point both names to the Lighthouse public IPv4:

- `@` -> server public IPv4
- `www` -> server public IPv4

Final canonical origin is the apex:

`https://exoticalloycn.com`

Nginx permanently redirects `www` to the apex.

## 2. Obtain release source

Two supported paths:

**A. ZIP package (recommended for handoff to another AI/operator)**

Extract the supplied project ZIP to `/opt/tongjun-overseas/app`. The package contains `RELEASE_PACKAGE_SHA`, so no Git metadata is required for release identity or deployment.

**B. Git clone**

Clone the release branch as below.

Recommended path:

```bash
sudo mkdir -p /opt/tongjun-overseas
sudo chown "$USER":"$USER" /opt/tongjun-overseas
git clone https://github.com/wuxi304-collab/tongjun-overseas.git /opt/tongjun-overseas/app
cd /opt/tongjun-overseas/app
git checkout release/v34.152-r15.26-tencent-lighthouse
```

## 3. Configure RFQ secrets

The bootstrap script creates `/etc/tongjun-overseas.env` from the safe example if the file does not exist.

Required for full production readiness:

```
RFQ_WEBHOOK_URL=https://your-secure-receiver.example/path
RFQ_SHARED_SECRET=<strong-random-secret>
RFQ_ALLOWED_ORIGINS=https://exoticalloycn.com,https://www.exoticalloycn.com
```

Keep the file mode at 0600. Never commit the real values.

If the secure RFQ route is not configured, the website still has its client-side email fallback, but `/api/health` deliberately returns 503 and the release is not considered fully production-ready.

## 4. Install Nginx + systemd configuration

Assuming the TLS files are already present:

```bash
cd /opt/tongjun-overseas/app

sudo \
  APP_DIR=/opt/tongjun-overseas/app \
  WEB_ROOT=/var/www/exoticalloycn \
  SSL_CERT=/path/to/fullchain.pem \
  SSL_KEY=/path/to/private.key \
  bash deploy/tencent/bootstrap.sh
```

For Let's Encrypt defaults, the template expects:

```
/etc/letsencrypt/live/exoticalloycn.com/fullchain.pem
/etc/letsencrypt/live/exoticalloycn.com/privkey.pem
```

If using a Tencent Cloud SSL certificate, pass its actual certificate and private-key paths explicitly.

The certificate should cover both the apex and `www` because HTTPS requests to `www` must complete TLS before Nginx can redirect them.

## 5. Deploy R15.26

```bash
cd /opt/tongjun-overseas/app
bash deploy/tencent/deploy.sh
```

The deploy script:

1. fetches and checks out the exact R15.26 release branch;
2. runs the full `npm run build:production` gate;
3. writes the immutable static artifact to `/var/www/exoticalloycn/releases/<git-sha>`;
4. atomically points `/var/www/exoticalloycn/current` to that release;
5. restarts the localhost Node API;
6. validates and reloads Nginx;
7. probes the local health endpoint and HTTPS homepage.

No source, build scripts, secrets or Node server files are copied into the public web root.

## 6. Validate service state

```bash
sudo systemctl status tongjun-api --no-pager
sudo nginx -t
curl -i http://127.0.0.1:8787/api/health
```

For logs:

```bash
sudo journalctl -u tongjun-api -n 100 --no-pager
sudo tail -n 100 /var/log/nginx/error.log
```

A fully ready health response is HTTP 200 with:

- `site_release: V34.152 R15.26`
- `hero_release: V34.152 R15.24`
- `deployment_environment: production`
- `rfq_route_https_valid: true`
- `rfq_signature_configured: true`

## 7. External launch gate

After DNS has propagated and HTTPS is live:

```bash
cd /opt/tongjun-overseas/app
npm run check:production
```

Then send the explicit synthetic RFQ:

```bash
RFQ_SMOKE_URL=https://exoticalloycn.com/api/rfq npm run smoke:rfq:production
```

Only after both pass should buyer traffic and SEO promotion be switched on.

## 8. Rollback static release

List available immutable releases:

```bash
ls -1 /var/www/exoticalloycn/releases
```

Point `current` back to a known-good SHA and reload Nginx:

```bash
sudo ln -sfn /var/www/exoticalloycn/releases/<GOOD_SHA> /var/www/exoticalloycn/current
sudo nginx -t && sudo systemctl reload nginx
```

If the API code must also roll back, checkout the same known-good Git commit in `/opt/tongjun-overseas/app` and restart:

```bash
git checkout <GOOD_SHA>
sudo systemctl restart tongjun-api
```

## Launch rule

The release is considered ready only when all four layers agree:

1. Git release branch / commit
2. `/.well-known/release.json`
3. `/api/health`
4. the deployed static `current` symlink

That prevents a new homepage being served with an old RFQ API, or vice versa.
