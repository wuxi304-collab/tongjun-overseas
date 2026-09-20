const SITE_RELEASE = 'V34.152 R15.13';
const VISUAL_RELEASE = 'V34.152 R15.7';

function validHttpsWebhook(value){
  const raw=String(value||'').trim();
  if(!raw) return false;
  try{
    const url=new URL(raw);
    return url.protocol==='https:' && Boolean(url.hostname);
  }catch{
    return false;
  }
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('X-Tongjun-Release', SITE_RELEASE);

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('Allow', 'GET, HEAD');
    return res.status(405).json({ok:false,error:'method_not_allowed'});
  }

  const routeConfigured=Boolean(String(process.env.RFQ_WEBHOOK_URL||'').trim());
  const routeValid=validHttpsWebhook(process.env.RFQ_WEBHOOK_URL);
  const signatureConfigured=Boolean(String(process.env.RFQ_SHARED_SECRET||'').trim());
  const ready=routeValid && signatureConfigured;
  const release = String(
    process.env.VERCEL_GIT_COMMIT_SHA ||
    process.env.GITHUB_SHA ||
    process.env.VERCEL_GIT_COMMIT_REF ||
    'local'
  ).slice(0, 40);
  const payload = {
    ok: ready,
    service: 'tongjun-overseas',
    site_release: SITE_RELEASE,
    visual_release: VISUAL_RELEASE,
    release,
    deployment_environment: String(process.env.VERCEL_ENV || 'local').slice(0, 40),
    rfq_route_configured: routeConfigured,
    rfq_route_https_valid: routeValid,
    rfq_signature_configured: signatureConfigured,
    checked_at: new Date().toISOString()
  };

  if (req.method === 'HEAD') return res.status(ready ? 200 : 503).end();
  return res.status(ready ? 200 : 503).json(payload);
};
