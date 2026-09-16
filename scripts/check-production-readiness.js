const assert = require('assert');
const dns = require('dns').promises;

const BASE = String(process.env.PRODUCTION_BASE_URL || 'https://exoticalloycn.com').replace(/\/$/, '');
const EXPECTED_HOST = new URL(BASE).hostname;
const TIMEOUT_MS = Number(process.env.PRODUCTION_CHECK_TIMEOUT_MS || 12000);

async function fetchChecked(url, options={}){
  return fetch(url, {...options, signal: AbortSignal.timeout(TIMEOUT_MS)});
}

async function resolveHost(host){
  const results=[];
  try{ results.push(...(await dns.resolve4(host)).map(v=>`A ${v}`)); }catch{}
  try{ results.push(...(await dns.resolve6(host)).map(v=>`AAAA ${v}`)); }catch{}
  assert.ok(results.length>0, `DNS resolution failed for ${host}`);
  return results;
}

function assertSecurityHeaders(response){
  assert.equal((response.headers.get('x-content-type-options')||'').toLowerCase(),'nosniff','X-Content-Type-Options must be nosniff');
  assert.equal((response.headers.get('x-frame-options')||'').toUpperCase(),'DENY','X-Frame-Options must be DENY');
  assert.match(response.headers.get('strict-transport-security')||'',/max-age=\d+/i,'HSTS header missing');
  assert.ok(response.headers.get('content-security-policy'),'Content-Security-Policy header missing');
  assert.ok(response.headers.get('referrer-policy'),'Referrer-Policy header missing');
}

async function run(){
  const baseUrl=new URL(BASE);
  assert.equal(baseUrl.protocol,'https:','Production base URL must use HTTPS');
  const resolved=await resolveHost(baseUrl.hostname);
  console.log(`DNS: ${resolved.join(', ')}`);

  const wwwUrl=`https://www.${EXPECTED_HOST}/`;
  const www=await fetchChecked(wwwUrl,{redirect:'manual'});
  assert.ok([301,302,307,308].includes(www.status),`www redirect expected 30x, got ${www.status}`);
  const location=www.headers.get('location')||'';
  assert.ok(location===`${BASE}/` || location===BASE,`www must redirect to apex; got ${location||'(missing)'}`);
  console.log(`WWW redirect: ${www.status} -> ${location}`);

  const home=await fetchChecked(`${BASE}/`,{redirect:'follow'});
  assert.equal(home.status,200,`Homepage expected 200, got ${home.status}`);
  assertSecurityHeaders(home);
  const html=await home.text();
  assert.match(html,/<link\b[^>]*rel=["']canonical["'][^>]*href=["']https:\/\/exoticalloycn\.com\/?["']/i,'Production canonical missing or wrong');
  const robots=(html.match(/<meta\b[^>]*name=["']robots["'][^>]*content=["']([^"']+)["'][^>]*>/i)||[])[1]||'';
  assert.ok(!/noindex/i.test(robots),'Production homepage must not be noindex');
  assert.match(html,/assets\/site\.js\?v=20260916-r14-2/,'Expected R14.2 runtime asset is not active');
  console.log('Homepage: 200, indexable, canonical + security headers + current runtime verified.');

  const rfq=await fetchChecked(`${BASE}/rfq`,{redirect:'follow'});
  assert.equal(rfq.status,200,`/rfq expected 200, got ${rfq.status}`);
  const rfqHtml=await rfq.text();
  assert.match(rfqHtml,/id=["']rfqForm["']/,'/rfq missing #rfqForm');
  assert.ok(!/name=["']robots["'][^>]*content=["'][^"']*noindex/i.test(rfqHtml),'/rfq must not be noindex in production');
  console.log('/rfq: 200 and buyer form present.');

  const thankYou=await fetchChecked(`${BASE}/thank-you`,{redirect:'follow'});
  assert.equal(thankYou.status,200,`/thank-you expected 200, got ${thankYou.status}`);
  console.log('/thank-you: 200.');

  const health=await fetchChecked(`${BASE}/api/health`,{headers:{Accept:'application/json'}});
  let body={};
  try{body=await health.json();}catch{}
  assert.equal(health.status,200,`/api/health expected 200, got ${health.status} (${body.error||'no JSON error'})`);
  assert.equal(body.ok,true,'/api/health must return ok=true');
  assert.equal(body.service,'tongjun-overseas','Unexpected health service identity');
  assert.equal(body.rfq_route_configured,true,'RFQ secure route is not configured');
  assert.ok(body.release,'Health response must expose a non-secret release identifier');
  console.log(`/api/health: READY · release ${body.release}`);

  console.log('PASS: production DNS, HTTPS, redirect, indexability, security headers, critical pages and RFQ readiness are all healthy.');
}

run().catch(err=>{
  console.error(`FAIL: ${err.message}`);
  process.exit(1);
});
