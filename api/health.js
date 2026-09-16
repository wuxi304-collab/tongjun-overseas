module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('Allow', 'GET, HEAD');
    return res.status(405).json({ok:false,error:'method_not_allowed'});
  }

  const routeConfigured = Boolean(String(process.env.RFQ_WEBHOOK_URL || '').trim());
  const payload = {
    ok: routeConfigured,
    service: 'tongjun-overseas',
    rfq_route_configured: routeConfigured,
    release: String(process.env.VERCEL_GIT_COMMIT_SHA || process.env.VERCEL_GIT_COMMIT_REF || 'local').slice(0, 40),
    checked_at: new Date().toISOString()
  };

  if (req.method === 'HEAD') return res.status(routeConfigured ? 200 : 503).end();
  return res.status(routeConfigured ? 200 : 503).json(payload);
};
