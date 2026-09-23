const { resolveMailConfig, transportEnvName } = require('../server/mailer.js');
const { ledgerEnabled, ledgerPath } = require('../server/rfq-ledger.js');

const SITE_RELEASE = 'V34.152 R15.26';
const VISUAL_RELEASE = 'V34.152 R15.7';
const HERO_RELEASE = 'V34.152 R15.24';

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('X-Tongjun-Release', SITE_RELEASE);

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('Allow', 'GET, HEAD');
    return res.status(405).json({ok:false,error:'method_not_allowed'});
  }

  // Readiness is now a question about mail delivery, not about a downstream webhook hop.
  const mail = resolveMailConfig(process.env);
  const ready = mail.ready;
  const release = String(
    process.env.TONGJUN_RELEASE_COMMIT ||
    process.env.GITHUB_SHA ||
    process.env.VERCEL_GIT_COMMIT_SHA ||
    process.env.VERCEL_GIT_COMMIT_REF ||
    'local'
  ).slice(0, 40);
  const payload = {
    ok: ready,
    service: 'tongjun-overseas',
    site_release: SITE_RELEASE,
    visual_release: VISUAL_RELEASE,
    hero_release: HERO_RELEASE,
    release,
    deployment_environment: String(process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT || process.env.VERCEL_ENV || 'local').slice(0, 40),
    rfq_delivery: 'email',
    mail_transport: mail.transport || transportEnvName(mail.transport) || 'unconfigured',
    mail_delivery_mode: mail.transportDetail,
    mail_transport_configured: mail.transportConfigured,
    mail_recipient_configured: mail.recipientConfigured,
    mail_sender_configured: mail.senderConfigured,
    mail_delivery_mode_safe: mail.deliveryModeSafe,
    // Environment variable NAMES only — never values. Lets an operator debug without shell access.
    mail_missing_env: mail.missing.slice(0, 12),
    mail_invalid_env: mail.invalid.slice(0, 12),
    rfq_ledger_configured: ledgerEnabled(process.env),
    rfq_ledger_path: ledgerPath(process.env),
    checked_at: new Date().toISOString()
  };

  if (req.method === 'HEAD') return res.status(ready ? 200 : 503).end();
  return res.status(ready ? 200 : 503).json(payload);
};
