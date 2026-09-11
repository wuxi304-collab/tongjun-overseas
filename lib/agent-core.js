const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX = 18;
const buckets = new Map();

function clean(value, max = 6000){
  return String(value ?? '').replace(/\u0000/g,'').trim().slice(0,max);
}

function allowedOrigin(req){
  const origin=req.headers.origin;
  if(!origin) return true;
  const configured=(process.env.AGENT_ALLOWED_ORIGINS||'https://exoticalloycn.com,https://www.exoticalloycn.com')
    .split(',').map(s=>s.trim()).filter(Boolean);
  if(process.env.VERCEL_URL) configured.push(`https://${process.env.VERCEL_URL}`);
  return configured.includes(origin);
}

function withinRateLimit(req,res){
  const raw=req.headers['x-forwarded-for']||'';
  const key=String(raw).split(',')[0].trim().slice(0,80);
  if(!key) return true;
  const now=Date.now();
  let b=buckets.get(key);
  if(!b || now-b.started>=RATE_WINDOW_MS){b={started:now,count:0};buckets.set(key,b)}
  b.count+=1;
  res.setHeader('X-RateLimit-Limit',String(RATE_MAX));
  res.setHeader('X-RateLimit-Remaining',String(Math.max(0,RATE_MAX-b.count)));
  if(buckets.size>800){for(const [k,v] of buckets) if(now-v.started>=RATE_WINDOW_MS) buckets.delete(k)}
  if(b.count>RATE_MAX){res.setHeader('Retry-After',String(Math.ceil((RATE_WINDOW_MS-(now-b.started))/1000)));return false}
  return true;
}

function stripThink(text){
  return clean(text,20000).replace(/<think>[\s\S]*?<\/think>/gi,'').trim();
}

function parseJsonReply(text){
  let t=stripThink(text).replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'').trim();
  try{return JSON.parse(t)}catch{}
  const a=t.indexOf('{'), b=t.lastIndexOf('}');
  if(a>=0 && b>a){try{return JSON.parse(t.slice(a,b+1))}catch{}}
  return null;
}

async function callMiniMax(system,user){
  const key=process.env.MINIMAX_API_KEY;
  if(!key) return {configured:false};
  const url=process.env.MINIMAX_API_URL||'https://api.minimax.io/v1/chat/completions';
  const model=process.env.MINIMAX_MODEL||'MiniMax-M3';
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),18000);
  try{
    const r=await fetch(url,{
      method:'POST',signal:controller.signal,
      headers:{'Authorization':`Bearer ${key}`,'Content-Type':'application/json'},
      body:JSON.stringify({model,messages:[{role:'system',content:system},{role:'user',content:user}],stream:false})
    });
    const body=await r.json().catch(()=>null);
    if(!r.ok) throw new Error(`minimax_${r.status}`);
    const content=body?.choices?.[0]?.message?.content||'';
    return {configured:true,model,content:stripThink(content),json:parseJsonReply(content)};
  } finally {clearTimeout(timer)}
}

function sendError(res,status,error){return res.status(status).json({ok:false,error})}
module.exports={clean,allowedOrigin,withinRateLimit,callMiniMax,sendError};
