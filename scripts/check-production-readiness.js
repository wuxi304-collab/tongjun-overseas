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

function attr(tag,name){
  const m=tag.match(new RegExp(`\\b${name}\\s*=\\s*["']([^"']*)["']`,'i'));
  return m ? m[1] : '';
}

function robotsContent(html){
  const tags=html.match(/<meta\b[^>]*>/gi)||[];
  for(const tag of tags){
    if(attr(tag,'name').toLowerCase()==='robots') return attr(tag,'content');
  }
  return '';
}

function canonicalHref(html){
  const tags=html.match(/<link\b[^>]*>/gi)||[];
  for(const tag of tags){
    const rel=attr(tag,'rel').toLowerCase().split(/\s+/).filter(Boolean);
    if(rel.includes('canonical')) return attr(tag,'href');
  }
  return '';
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
  const canonical=canonicalHref(html);
  assert.ok(canonical==='https://exoticalloycn.com/' || canonical==='https://exoticalloycn.com',`Production canonical missing or wrong: ${canonical||'(missing)'}`);
  const robots=robotsContent(html);
  assert.ok(robots,'Production homepage robots meta is missing');
  assert.ok(!/noindex/i.test(robots),'Production homepage must not be noindex');
  assert.match(html,/assets\/site\.js\?v=20260916-r14-2/,'Expected R14.2 runtime asset is not active');
  console.log('Homepage: 200, indexable, canonical + security headers + current runtime verified.');

  const rfq=await fetchChecked(`${BASE}/rfq`,{redirect:'follow'});
  assert.equal(rfq.status,200,`/rfq expected 200, got ${rfq.status}`);
  const rfqHtml=await rfq.text();
  assert.match(rfqHtml,/id=["']rfqForm["']/,'/rfq missing #rfqForm');
  const rfqRobots=robotsContent(rfqHtml);
  assert.ok(rfqRobots,'/rfq robots meta is missing');
  assert.ok(!/noindex/i.test(rfqRobots),'/rfq must not be noindex in production');
  console.log('/rfq: 200, indexable and buyer form present.');

  const thankYou=await fetchChecked(`${BASE}/thank-you`,{redirect:'follow'});
  assert.equal(thankYou.status,200,`/thank-you expected 200, got ${thankYou.status}`);
  console.log('/thank-you: 200.');

  const health=await fetchChecked(`${BASE}/api/health`,{headers:{Accept:'application/json'}});
  let body={};
  try{body=await health.json();}catch{}
  assert.equal(health.status,200,`/api/health expected 200, got ${health.status} (${body.error||'no JSON error'})`);
  assert.equal(body.ok,true,'/api/health must return ok=true');
  assert.equal(body.service,'tongjun-overseas','Unexpected health service identity');
  assert.equal(body.site_release,'V34.152 R15.25','Unexpected health site release');
  assert.equal(body.visual_release,'V34.152 R15.7','Unexpected health visual release');
  assert.equal(body.hero_release,'V34.152 R15.24','Unexpected homepage HERO release');
  assert.equal(body.rfq_route_configured,true,'RFQ secure route is not configured');
  assert.equal(body.rfq_route_https_valid,true,'RFQ webhook must be a valid HTTPS URL');
  assert.equal(body.rfq_signature_configured,true,'RFQ HMAC signing secret is not configured');
  assert.match(String(body.release||''),/^[0-9a-f]{40}$/i,'Health response must expose the production commit SHA');
  assert.equal(health.headers.get('x-tongjun-release'),'V34.152 R15.25','Health release header mismatch');
  console.log(`/api/health: READY · ${body.site_release} · HTTPS webhook + HMAC · commit ${body.release.slice(0,12)}`);

  const releaseResponse=await fetchChecked(`${BASE}/.well-known/release.json`,{headers:{Accept:'application/json'}});
  assert.equal(releaseResponse.status,200,`/.well-known/release.json expected 200, got ${releaseResponse.status}`);
  assert.match(releaseResponse.headers.get('cache-control')||'',/no-store/i,'release.json must be no-store');
  const release=await releaseResponse.json();
  assert.equal(release.service,'tongjun-overseas','Static release service identity mismatch');
  assert.equal(release.site_release,body.site_release,'Static/API site release mismatch');
  assert.equal(release.visual_release,body.visual_release,'Static/API visual release mismatch');
  assert.equal(release.hero_release,body.hero_release,'Static/API homepage HERO release mismatch');
  assert.equal(release.environment,'production','Static release environment must be production');
  assert.match(String(release.visual_manifest_sha256||''),/^[0-9a-f]{64}$/i,'Visual manifest SHA256 missing');
  assert.equal(release.source_commit,body.release,'Static/API source commit mismatch');
  console.log(`/.well-known/release.json: ${release.site_release} · ${release.source_commit.slice(0,12)} · visuals ${release.visual_release}`);

  console.log('PASS: production DNS, HTTPS, redirect, indexability, security headers, static/API release identity and RFQ readiness are all healthy.');
}

run().catch(err=>{
  console.error(`FAIL: ${err.message}`);
  process.exit(1);
});
