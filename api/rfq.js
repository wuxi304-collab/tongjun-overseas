const crypto = require('crypto');

const MAX_BODY_CHARS = 24000;
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX = 8;
const rateBuckets = new Map();
const LIMITS = {
  name:120, company:180, email:240, country:120, grade:180, standard:180, form:120,
  size:240, condition:240, qty:180, certificate:300, origin:300, approval:300, procurement_stage:120, buyer_gate:120, incoterm:80, destination:240, delivery_target:80, packing:500, application:2500,
  notes:3500, source:300, product:180, utm_source:180, utm_medium:180,
  utm_campaign:240, utm_content:240, ac:80, persona:120, wedge:180,
  first_landing:300, first_referrer:180, first_seen:80, route_ref:80, decision_ref:80, offer_ref:80, subject:300, structured_body:8000, evidence_package:3500, website:240
};

function norm(value, max){
  return String(value ?? '').replace(/\u0000/g,'').trim().slice(0,max);
}

function clientKey(req){
  const raw=req.headers['x-forwarded-for'] || '';
  return String(raw).split(',')[0].trim().slice(0,80);
}
function withinRateLimit(req,res){
  const key=clientKey(req);
  if(!key) return true; // local tests / non-Vercel execution
  const now=Date.now();
  let bucket=rateBuckets.get(key);
  if(!bucket || now-bucket.started>=RATE_WINDOW_MS){
    bucket={started:now,count:0};
    rateBuckets.set(key,bucket);
  }
  bucket.count+=1;
  const remaining=Math.max(0,RATE_MAX-bucket.count);
  res.setHeader('X-RateLimit-Limit',String(RATE_MAX));
  res.setHeader('X-RateLimit-Remaining',String(remaining));
  if(rateBuckets.size>500){
    for(const [k,v] of rateBuckets) if(now-v.started>=RATE_WINDOW_MS) rateBuckets.delete(k);
  }
  if(bucket.count>RATE_MAX){
    res.setHeader('Retry-After',String(Math.ceil((RATE_WINDOW_MS-(now-bucket.started))/1000)));
    return false;
  }
  return true;
}

function allowedOrigin(req){
  const origin = req.headers.origin;
  if (!origin) return true;
  const configured=(process.env.RFQ_ALLOWED_ORIGINS||'https://exoticalloycn.com,https://www.exoticalloycn.com')
    .split(',').map(s=>s.trim()).filter(Boolean);
  if (process.env.VERCEL_URL) configured.push(`https://${process.env.VERCEL_URL}`);
  return configured.includes(origin);
}
async function postWebhook(url, body, requestId){
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),8000);
  try{
    const headers={'Content-Type':'application/json','X-Tongjun-Request-Id':requestId};
    if(process.env.RFQ_SHARED_SECRET) headers['X-Tongjun-Webhook-Secret']=process.env.RFQ_SHARED_SECRET;
    return await fetch(url,{method:'POST',headers,body:JSON.stringify(body),signal:controller.signal});
  } finally { clearTimeout(timer); }
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control','no-store');
  if (req.method !== 'POST') {
    res.setHeader('Allow','POST');
    return res.status(405).json({ok:false,error:'method_not_allowed'});
  }
  if (!allowedOrigin(req)) return res.status(403).json({ok:false,error:'origin_not_allowed'});
  if (!withinRateLimit(req,res)) return res.status(429).json({ok:false,error:'rate_limited'});
  const raw = req.body || {};
  if (JSON.stringify(raw).length > MAX_BODY_CHARS) return res.status(413).json({ok:false,error:'payload_too_large'});
  const b={};
  for(const [key,max] of Object.entries(LIMITS)) b[key]=norm(raw[key],max);
  if (b.website) return res.status(202).json({ok:true}); // honeypot: silently accept bots

  const required=['name','company','email','grade','size','qty','application'];
  const missing=required.filter(k=>!b[k]);
  if(missing.length) return res.status(400).json({ok:false,error:'missing_fields',missing});
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(b.email)) return res.status(400).json({ok:false,error:'invalid_email'});

  const requestId=`TJ-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
  const record={request_id:requestId,received_at:new Date().toISOString(),site:'exoticalloycn.com',...b};
  const webhook=process.env.RFQ_WEBHOOK_URL;
  if(!webhook) return res.status(503).json({ok:false,error:'rfq_route_not_configured',request_id:requestId});

  try{
    const r=await postWebhook(webhook,record,requestId);
    if(!r.ok) throw new Error(`webhook_${r.status}`);
    return res.status(202).json({ok:true,request_id:requestId});
  } catch(e){
    console.error('RFQ_WEBHOOK_ERROR', requestId, e && e.message ? e.message : 'unknown');
    return res.status(502).json({ok:false,error:'rfq_delivery_failed',request_id:requestId});
  }
};
