const crypto = require('crypto');
const { buildRfqEmail, resolveMailConfig, sendRfqEmail } = require('../server/mailer.js');
const { appendLedger } = require('../server/rfq-ledger.js');

const MAX_BODY_BYTES = 24000;
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX = 8;
const rateBuckets = new Map();
const LIMITS = {
  name:120, company:180, email:240, country:120, grade:180, standard:180, form:120,
  size:240, condition:240, qty:180, certificate:300, origin:300, approval:300, procurement_stage:120, buyer_gate:120, incoterm:80, destination:240, delivery_target:80, packing:500, application:2500,
  quote_assumptions:2500, deviation_status:80, deviation_register:3500, alternate_route_permission:120,
  certificate_responsibility:180, inspection_responsibility:180, release_status:120, release_checklist:2500, technical_review_plan:2500,
  notes:3500, source:300, product:180, utm_source:180, utm_medium:180,
  utm_campaign:240, utm_content:240, ac:80, persona:120, wedge:180,
  first_landing:300, first_referrer:180, first_seen:80, route_ref:80, decision_ref:80, offer_ref:80, subject:300, structured_body:8000, evidence_package:3500, website:240
};

function norm(value, max){
  return String(value ?? '').replace(/\u0000/g,'').trim().slice(0,max);
}
function makeRequestId(){
  return `TJ-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${crypto.randomBytes(6).toString('hex').toUpperCase()}`;
}
function respond(res,status,payload,requestId){
  if(requestId) res.setHeader('X-Tongjun-Request-Id',requestId);
  return res.status(status).json(requestId ? {...payload,request_id:requestId} : payload);
}
function isJsonRequest(req){
  const mediaType=String(req.headers['content-type'] || '').split(';',1)[0].trim().toLowerCase();
  return mediaType === 'application/json' || /^application\/[a-z0-9!#$&^_.+-]+\+json$/.test(mediaType);
}
function clientKey(req){
  const raw=req.headers['x-forwarded-for'] || req.headers['x-real-ip'] || '';
  return String(raw).split(',')[0].trim().slice(0,80);
}
function withinRateLimit(req,res){
  const key=clientKey(req);
  if(!key) return true;
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

/**
 * Record the submission locally before anything else can fail, so a buyer who submitted is
 * never invisible even when mail delivery is broken.
 */
function recordLedger(record, status, extras){
  return appendLedger({
    requestId: record.request_id,
    record,
    status,
    transport: (extras && extras.transport) || '',
    messageId: (extras && extras.messageId) || '',
    deliveredAt: (extras && extras.deliveredAt) || '',
    error: (extras && extras.error) || ''
  });
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control','no-store');
  if (req.method !== 'POST') {
    res.setHeader('Allow','POST');
    return res.status(405).json({ok:false,error:'method_not_allowed'});
  }

  const requestId=makeRequestId();
  res.setHeader('X-Tongjun-Request-Id',requestId);

  if (!isJsonRequest(req)) return respond(res,415,{ok:false,error:'unsupported_media_type'},requestId);
  if (!allowedOrigin(req)) return respond(res,403,{ok:false,error:'origin_not_allowed'},requestId);
  if (!withinRateLimit(req,res)) return respond(res,429,{ok:false,error:'rate_limited'},requestId);
  const raw = req.body || {};
  const rawText=JSON.stringify(raw);
  if (Buffer.byteLength(rawText,'utf8') > MAX_BODY_BYTES) return respond(res,413,{ok:false,error:'payload_too_large'},requestId);
  const b={};
  for(const [key,max] of Object.entries(LIMITS)) b[key]=norm(raw[key],max);
  if (b.website) return respond(res,202,{ok:true},requestId);

  const required=['name','company','email','grade','size','qty','application'];
  const missing=required.filter(k=>!b[k]);
  if(missing.length) return respond(res,400,{ok:false,error:'missing_fields',missing},requestId);
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(b.email)) return respond(res,400,{ok:false,error:'invalid_email'},requestId);

  const record={request_id:requestId,received_at:new Date().toISOString(),site:'exoticalloycn.com',...b};

  const mail=resolveMailConfig(process.env);
  if(!mail.recipientConfigured){
    recordLedger(record,'rejected_config',{error:'mail_recipient_not_configured'});
    return respond(res,503,{ok:false,error:'mail_recipient_not_configured'},requestId);
  }
  if(!mail.senderConfigured){
    recordLedger(record,'rejected_config',{error:'mail_sender_not_configured'});
    return respond(res,503,{ok:false,error:'mail_sender_not_configured'},requestId);
  }
  if(!mail.transportConfigured){
    recordLedger(record,'rejected_config',{error:'mail_transport_not_configured'});
    return respond(res,503,{ok:false,error:'mail_transport_not_configured'},requestId);
  }
  if(!mail.deliveryModeSafe){
    recordLedger(record,'rejected_config',{error:'mail_delivery_mode_unsafe',transport:mail.transport});
    return respond(res,503,{ok:false,error:'mail_delivery_mode_unsafe'},requestId);
  }

  try{
    const message=buildRfqEmail(record,mail);
    const result=await sendRfqEmail(message,mail);
    recordLedger(record,'delivered',{
      transport:result.transport || mail.transport,
      messageId:result.messageId,
      deliveredAt:new Date().toISOString()
    });
    return respond(res,202,{ok:true,delivery:result.transport || mail.transport},requestId);
  } catch(e){
    const code=(e && e.code) || 'mail_delivery_failed';
    console.error('RFQ_MAIL_ERROR', requestId, code, (e && e.message) || 'unknown');
    recordLedger(record,'failed',{transport:mail.transport,error:code});
    return respond(res,502,{ok:false,error:'rfq_delivery_failed',delivery_error:code},requestId);
  }
};
