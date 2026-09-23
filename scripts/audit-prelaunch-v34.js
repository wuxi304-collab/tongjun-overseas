const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const htmls=fs.readdirSync(root).filter(f=>f.endsWith('.html')).sort();
const failures=[];
const sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');

function attr(tag,name){
  const m=tag.match(new RegExp(`\\b${name}\\s*=\\s*["']([^"']*)["']`,'i'));
  return m?m[1]:'';
}
function robotsContent(html){
  const tags=html.match(/<meta\b[^>]*>/gi)||[];
  for(const tag of tags) if(attr(tag,'name').toLowerCase()==='robots') return attr(tag,'content');
  return '';
}
function routeFor(file){return file==='index.html'?'/':'/'+file.replace(/\.html$/,'');}

if(htmls.length!==50) failures.push(`expected 50 root HTML files, found ${htmls.length}`);
const forbidden=['SINCE 2010','hero-special-metals.webp','quality-lab-r13','engineering-team-r13','technical-lab-r13','logo-r13.avif','hero-port-r13.avif'];
for(const file of htmls){
  const text=fs.readFileSync(path.join(root,file),'utf8');
  if(!text.includes('assets/site.js?v=20260916-r14-2')) failures.push(`${file}: current site.js release marker missing`);
  for(const marker of forbidden) if(text.includes(marker)) failures.push(`${file}: forbidden release marker ${marker}`);
  const robots=robotsContent(text);
  if(/noindex/i.test(robots)){
    const route=routeFor(file);
    const loc=`<loc>https://exoticalloycn.com${route}</loc>`;
    if(sitemap.includes(loc)) failures.push(`${file}: noindex page appears in sitemap`);
  }
}

for(const required of [
  'api/rfq.js','api/health.js','server/tongjun-api.js',
  'deploy/tencent/nginx-exoticalloycn.conf.template',
  'deploy/tencent/tongjun-api.service.template',
  'deploy/tencent/tongjun-overseas.env.example',
  'deploy/tencent/bootstrap.sh','deploy/tencent/deploy.sh',
  'robots.txt','sitemap.xml','RELEASE_R15_26.json','VISUAL_MANIFEST_R15_7.json',
  'scripts/write-release-metadata.py','scripts/check-production-readiness.js','scripts/smoke-rfq-production.js'
]){
  if(!fs.existsSync(path.join(root,required))) failures.push(`missing production release file ${required}`);
}

const serverAdapter=fs.readFileSync(path.join(root,'server','tongjun-api.js'),'utf8');
for(const marker of ['127.0.0.1','TONGJUN_API_HOST','TONGJUN_API_PORT','/api/health','/api/rfq']){
  if(!serverAdapter.includes(marker)) failures.push(`self-hosted API adapter missing ${marker}`);
}
const nginx=fs.readFileSync(path.join(root,'deploy','tencent','nginx-exoticalloycn.conf.template'),'utf8');
for(const marker of ['server_name exoticalloycn.com','proxy_pass http://127.0.0.1:8787','Strict-Transport-Security','Content-Security-Policy']){
  if(!nginx.includes(marker)) failures.push(`Tencent Nginx template missing ${marker}`);
}

const robotsTxt=fs.readFileSync(path.join(root,'robots.txt'),'utf8');
if(/Disallow:\s*\/$/m.test(robotsTxt)) failures.push('production robots.txt blocks the entire site');

const health=fs.readFileSync(path.join(root,'api','health.js'),'utf8');
for(const marker of ['mail_transport_configured','mail_recipient_configured','mail_sender_configured','mail_delivery_mode_safe','mail_missing_env','mail_invalid_env','rfq_ledger_configured','rfq_ledger_path','Cache-Control','TONGJUN_RELEASE_COMMIT','TONGJUN_DEPLOYMENT_ENVIRONMENT','V34.152 R15.26','X-Tongjun-Release','visual_release','hero_release','V34.152 R15.24']) if(!health.includes(marker)) failures.push(`api/health.js missing ${marker}`);
// The retired webhook contract must not creep back in: readiness is a mail question now.
for(const retired of ['rfq_route_configured','rfq_route_https_valid','rfq_signature_configured','RFQ_WEBHOOK_URL','RFQ_SHARED_SECRET']) if(health.includes(retired)) failures.push(`api/health.js must no longer reference the retired webhook contract: ${retired}`);
if(/MS_GRAPH_CLIENT_SECRET\s*[:=]\s*process\.env\.MS_GRAPH_CLIENT_SECRET|RESEND_API_KEY\s*[:=]\s*process\.env\.RESEND_API_KEY|RFQ_SMTP_PASS\s*[:=]\s*process\.env\.RFQ_SMTP_PASS/.test(health)) failures.push('api/health.js must not serialize mail credentials into the response payload');

// A log-only transport in production is the silent-failure trap this contract exists to block.
const mailer=fs.readFileSync(path.join(root,'server','mailer.js'),'utf8');
for(const marker of ['deliveryModeSafe','mail_not_configured','RFQ_MAIL_TO','RFQ_MAIL_FROM']) if(!mailer.includes(marker)) failures.push(`server/mailer.js missing ${marker}`);
const rfqApi=fs.readFileSync(path.join(root,'api','rfq.js'),'utf8');
if(/RFQ_WEBHOOK_URL|postWebhook|X-Tongjun-Webhook-Signature/.test(rfqApi)) failures.push('api/rfq.js must deliver by mail, not by webhook');
for(const marker of ["'rfq_delivery_failed'",'sendRfqEmail','appendLedger']) if(!rfqApi.includes(marker)) failures.push(`api/rfq.js missing ${marker}`);

const smoke=fs.readFileSync(path.join(root,'scripts','smoke-rfq-production.js'),'utf8');
if(!smoke.includes('RFQ_SMOKE_URL')) failures.push('production RFQ smoke is not explicitly opt-in');
if(!smoke.includes('NO COMMERCIAL ORDER')) failures.push('production RFQ smoke is not clearly marked synthetic');

if(failures.length){console.error('FAIL: R15 prelaunch audit');failures.forEach(x=>console.error(' - '+x));process.exit(1);}
console.log('PASS: R15.26 prelaunch audit — Tencent Lighthouse runtime, Nginx/API boundary, release identity, indexability, health and RFQ smoke contracts validated.');
