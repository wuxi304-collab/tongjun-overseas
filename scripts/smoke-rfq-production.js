const assert = require('assert');

function requiredEnv(name){
  const value=String(process.env[name]||'').trim();
  if(!value) throw new Error(`${name} is required. Example: RFQ_SMOKE_URL=https://exoticalloycn.com/api/rfq`);
  return value;
}

async function run(){
  const endpoint=requiredEnv('RFQ_SMOKE_URL');
  const url=new URL(endpoint);
  if(url.protocol!=='https:') throw new Error('RFQ_SMOKE_URL must use https');

  const origin=String(process.env.RFQ_SMOKE_ORIGIN||url.origin).trim();
  const stamp=new Date().toISOString();
  const payload={
    name:'Tongjun Production Smoke',
    company:'Tongjun Metal Technology (Wuxi) Co., Ltd.',
    email:String(process.env.RFQ_SMOKE_EMAIL||'ask2205@outlook.com').trim(),
    country:'CN',
    grade:'UNS N06625',
    standard:'ASTM B443',
    form:'Sheet / Plate',
    size:'3 x 1000 x 2000 mm',
    condition:'Solution annealed',
    qty:'SMOKE TEST — NO COMMERCIAL ORDER',
    application:'Automated production delivery smoke test. Do not quote or source material.',
    certificate:'EN 10204 3.1',
    origin:'No commercial requirement — smoke test only',
    procurement_stage:'source-screen',
    buyer_gate:'technical',
    source:'production-smoke',
    product:'rfq-delivery-contract',
    first_landing:'/rfq',
    first_referrer:'production-smoke',
    first_seen:stamp,
    notes:`PRODUCTION SMOKE TEST ${stamp}. This is not a customer inquiry and must not trigger sourcing activity.`
  };

  const response=await fetch(endpoint,{
    method:'POST',
    headers:{
      'Content-Type':'application/json',
      'Origin':origin,
      'User-Agent':'Tongjun-RFQ-Production-Smoke/1.1'
    },
    body:JSON.stringify(payload),
    signal:AbortSignal.timeout(12000)
  });

  let body={};
  try{ body=await response.json(); }catch{}
  const headerId=response.headers.get('x-tongjun-request-id')||'';
  const bodyId=String(body.request_id||'');

  console.log(`RFQ smoke status: ${response.status}`);
  console.log(`RFQ smoke request ID: ${bodyId||headerId||'(missing)'}`);
  console.log(`RFQ smoke delivery channel: ${body.delivery||'(not reported)'}`);

  assert.equal(response.status,202,`Expected secure delivery 202, got ${response.status} (${body.error||'no JSON error'})`);
  assert.equal(body.ok,true,'Expected response body ok=true');
  assert.match(bodyId,/^TJ-\d{8}-[0-9A-F]{12}$/,'Response request_id format is invalid');
  assert.equal(headerId,bodyId,'X-Tongjun-Request-Id must match response body request_id');
  assert.ok(body.delivery,'Response must report which mail transport delivered the inquiry');

  console.log(`PASS: production RFQ endpoint delivered the synthetic smoke inquiry by ${body.delivery} and returned a correlated trace ID.`);
}

run().catch(err=>{
  console.error(`FAIL: ${err.message}`);
  process.exit(1);
});
