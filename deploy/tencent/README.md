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

## 3. Configure RFQ mail delivery

The bootstrap script creates `/etc/tongjun-overseas.env` from the safe example if the file does not exist.

Buyer submissions are delivered by the Node service itself — there is no webhook hop. Required for full production readiness:

```
RFQ_MAIL_TRANSPORT=resend
RFQ_MAIL_TO=wuxi304@outlook.com
RFQ_MAIL_FROM=rfq@exoticalloycn.com
RESEND_API_KEY=<provider-api-key>
RFQ_ALLOWED_ORIGINS=https://exoticalloycn.com,https://www.exoticalloycn.com
```

This deployment uses **`resend`**. The other rows are kept because the code supports them, not because they are planned.

| Transport | Credentials | Notes |
|---|---|---|
| `resend` | `RESEND_API_KEY` | **Selected.** Sender must be on a domain verified in Resend. One key to store, nothing that expires. |
| `graph` | `MS_GRAPH_TENANT_ID` + `MS_GRAPH_CLIENT_ID` + `MS_GRAPH_CLIENT_SECRET` | Microsoft 365 **work/school** mailbox only. Application permissions. |
| `graph` (delegated) | `MS_GRAPH_CLIENT_ID` + `MS_GRAPH_REFRESH_TOKEN` | The only Graph mode a personal `@outlook.com` account supports. Set `MS_GRAPH_TENANT_ID` to `common` (the default). |
| `smtp` | `RFQ_SMTP_HOST` + `RFQ_SMTP_USER` + `RFQ_SMTP_PASS` | Port 465 implicit TLS, or 587 with STARTTLS. |
| `log` | none | Local only. Delivers nothing, so production readiness is refused. |

Three constraints worth knowing before you choose:

1. **A personal Microsoft account cannot use Graph application permissions.** Microsoft states this plainly ("Personal accounts do not support application permissions, only delegated permissions"). That is a Graph restriction. It is *not* a protocol restriction: OAuth2 for IMAP/POP/SMTP is documented as available to Outlook.com users as well as Microsoft 365 users, and Graph's delegated `Mail.Send` works for personal accounts too. The real reason this deployment does not use Graph is different — delegated mode would mean holding a refresh token tied to one person's Microsoft account and re-consenting whenever it is invalidated, which is more fragile than a single API key.
2. **A transactional provider cannot send from `outlook.com`.** `RFQ_MAIL_FROM` must be on a domain you have verified with the provider. `wuxi304@outlook.com` stays the *recipient*; the *sender* is on `exoticalloycn.com`. The service rejects a consumer-domain sender at configuration time rather than failing on a buyer's submission.
3. **Mail is only one direction here.** Nothing in the RFQ path reads a mailbox. The customer's address travels as `Reply-To`, so replying from Outlook answers the buyer without the server ever needing inbox access.

Keep the file mode at 0600. Never commit the real values.

If mail delivery is not configured, the website still has its client-side email fallback, but `/api/health` deliberately returns 503, lists the missing variables in `mail_missing_env`, and the release is not considered production-ready.

Delivery ledger: every submission appends one JSON line to `RFQ_LEDGER_PATH` (default `/var/lib/tongjun-rfq/rfq-ledger.jsonl`) with `request_id`, timestamps, status, transport, `message_id`, company, email, country, grade and form. The inquiry body is never written, by design.

```bash
# Recent deliveries, newest last
sudo tail -n 20 /var/lib/tongjun-rfq/rfq-ledger.jsonl
# Anything that failed to deliver
sudo grep '"status":"failed"' /var/lib/tongjun-rfq/rfq-ledger.jsonl
```

### Verifying a sending domain with Resend

Resend will not accept a sender on a domain it has not verified. Add the domain in the Resend
dashboard, then create the DNS records it displays in the DNSPod console for the zone. The
shape is always the same three records plus DMARC:

| Type | Host | Value |
|---|---|---|
| TXT | `send` | `v=spf1 include:amazonses.com ~all` |
| MX | `send` | `feedback-smtp.<region>.amazonses.com` (priority 10) |
| TXT | `resend._domainkey` | `p=MIGf...` — the DKIM public key, copy it verbatim |
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@exoticalloycn.com` |

The `send` subdomain is what Resend uses as the envelope (Return-Path) sender, which is why
SPF lives there rather than on the apex. Copy the DKIM value exactly as shown — a truncated or
line-wrapped key verifies as a signature failure rather than a malformed record, so it fails
at delivery time instead of at verification time.

Check propagation before clicking Verify in Resend:

```bash
dig +short TXT send.exoticalloycn.com
dig +short MX  send.exoticalloycn.com
dig +short TXT resend._domainkey.exoticalloycn.com
dig +short TXT _dmarc.exoticalloycn.com
```

A record that is published but not yet propagated returns empty from `dig`, which is
indistinguishable from "never added" if you only look at the dashboard. Confirm with `dig`
first, then verify.

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
- `mail_transport_configured: true`
- `mail_recipient_configured: true`
- `mail_sender_configured: true`
- `mail_delivery_mode_safe: true` (false when a `log` transport is selected in production)
- `rfq_ledger_configured: true`

When it is not ready, `mail_missing_env` and `mail_invalid_env` name the offending variables.

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
