const assert = require('assert');
const crypto = require('crypto');

function makeRes(){
  let statusCode=200,payload=null;
  const headers={};
  return {
    setHeader(k,v){headers[k]=v;},
    status(n){statusCode=n;return this;},
    json(x){payload=x;return x;},
    get statusCode(){return statusCode;}, get payload(){return payload;}, get headers(){return headers;}
  };
}

function requestIdLooksValid(id){
  return /^TJ-\d{8}-[0-9A-F]{12}$/.test(String(id||''));
}
function assertTrace(res){
  assert.equal(requestIdLooksValid(res.payload && res.payload.request_id),true);
  assert.equal(res.headers['X-Tongjun-Request-Id'],res.payload.request_id);
}

async function run(){
  process.env.RFQ_WEBHOOK_URL='https://example.invalid/hook';
  process.env.RFQ_ALLOWED_ORIGINS='https://exoticalloycn.com';
  process.env.RFQ_SHARED_SECRET='unit-test-secret';

  let sent=null;
  let sentBodyText='';
  let sentHeaders=null;
  let fetchMode='success';
  let fetchCount=0;
  global.fetch=async (_url,opts)=>{
    fetchCount+=1;
    sentBodyText=String(opts.body||'');
    sent=JSON.parse(sentBodyText);
    sentHeaders=opts.headers||{};
    if(fetchMode==='throw') throw new Error('network_down');
    if(fetchMode==='fail') return {ok:false,status:503};
    return {ok:true,status:202};
  };

  const handler=require('../api/rfq.js');
  const baseBody={
    name:'Buyer',company:'Example',email:'buyer@example.com',country:'DE',grade:'UNS N06625',
    standard:'ASTM B443',form:'Sheet / Plate',size:'3 x 1000 x 2000 mm',condition:'Solution annealed',
    qty:'2 t',application:'Chemical service',certificate:'EN 10204 3.1 + PMI',origin:'China origin accepted',
    procurement_stage:'trial',buyer_gate:'approval',decision_ref:'BR-20260907-ABC123',
    approval:'Project AVL',incoterm:'CIF',destination:'Hamburg, Germany',delivery_target:'2026-11-15',packing:'Export seaworthy',offer_ref:'OF-20260907-ABC123',
    quote_assumptions:'Lead time starts after technical release',deviation_status:'buyer-decision',deviation_register:'DEV-01 | width tolerance | buyer decision',
    alternate_route_permission:'separate-alternate',certificate_responsibility:'buyer-specifies-source-provides',inspection_responsibility:'third-party-witness',
    release_status:'QUALIFIED WITH CONDITIONS',release_checklist:'technical=READY | deviations=CONDITIONAL',technical_review_plan:'VERIFY > QUALIFY > ALIGN > OFFER',
    notes:'Buyer note',source:'resource-page',product:'alloy-625',first_landing:'/alloy-625-china',first_referrer:'google.com',first_seen:'2026-09-16T03:00:00.000Z'
  };
  const req=(body=baseBody,headers={})=>({
    method:'POST',
    headers:{origin:'https://exoticalloycn.com','content-type':'application/json',...headers},
    body:{...body}
  });

  // Successful secure routing preserves advanced technical + attribution context.
  let res=makeRes();
  await handler(req(),res);
  assert.equal(res.statusCode,202);
  assert.equal(res.payload.ok,true);
  assertTrace(res);
  assert.equal(sent.request_id,res.payload.request_id);
  assert.equal(sent.procurement_stage,'trial');
  assert.equal(sent.buyer_gate,'approval');
  assert.equal(sent.decision_ref,'BR-20260907-ABC123');
  assert.equal(sent.approval,'Project AVL');
  assert.equal(sent.incoterm,'CIF');
  assert.equal(sent.destination,'Hamburg, Germany');
  assert.equal(sent.delivery_target,'2026-11-15');
  assert.equal(sent.packing,'Export seaworthy');
  assert.equal(sent.offer_ref,'OF-20260907-ABC123');
  assert.equal(sent.quote_assumptions,'Lead time starts after technical release');
  assert.equal(sent.deviation_status,'buyer-decision');
  assert.match(sent.deviation_register,/DEV-01/);
  assert.equal(sent.alternate_route_permission,'separate-alternate');
  assert.equal(sent.certificate_responsibility,'buyer-specifies-source-provides');
  assert.equal(sent.inspection_responsibility,'third-party-witness');
  assert.equal(sent.release_status,'QUALIFIED WITH CONDITIONS');
  assert.match(sent.release_checklist,/technical=READY/);
  assert.equal(sent.technical_review_plan,'VERIFY > QUALIFY > ALIGN > OFFER');
  assert.equal(sent.product,'alloy-625');
  assert.equal(sent.first_seen,'2026-09-16T03:00:00.000Z');

  // Shared-secret mode adds an integrity signature over timestamp + exact JSON body.
  assert.equal(sentHeaders['X-Tongjun-Webhook-Secret'],undefined);
  assert.equal(sentHeaders['X-Tongjun-Webhook-Signature-Version'],'v1');
  assert.match(String(sentHeaders['X-Tongjun-Webhook-Timestamp']||''),/^\d{10}$/);
  const expectedSignature=crypto
    .createHmac('sha256','unit-test-secret')
    .update(`${sentHeaders['X-Tongjun-Webhook-Timestamp']}.${sentBodyText}`)
    .digest('hex');
  assert.equal(sentHeaders['X-Tongjun-Webhook-Signature'],`sha256=${expectedSignature}`);
  assert.equal(sentHeaders['X-Tongjun-Request-Id'],res.payload.request_id);

  // Raw shared-secret forwarding is disabled by default and only available as an explicit migration switch.
  process.env.RFQ_LEGACY_SECRET_HEADER='1';
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.21'}),res);
  assert.equal(res.statusCode,202);
  assertTrace(res);
  assert.equal(sentHeaders['X-Tongjun-Webhook-Secret'],'unit-test-secret');
  assert.equal(sentHeaders['X-Tongjun-Webhook-Signature-Version'],'v1');
  delete process.env.RFQ_LEGACY_SECRET_HEADER;

  // Only POST is accepted.
  res=makeRes();
  await handler({method:'GET',headers:{},body:{}},res);
  assert.equal(res.statusCode,405);
  assert.equal(res.headers.Allow,'POST');

  // Non-JSON POSTs are rejected before origin/rate/delivery handling, but remain traceable.
  const beforeMediaTypeFetches=fetchCount;
  res=makeRes();
  await handler(req(baseBody,{'content-type':'text/plain','x-forwarded-for':'198.51.100.9'}),res);
  assert.equal(res.statusCode,415);
  assert.equal(res.payload.error,'unsupported_media_type');
  assertTrace(res);
  assert.equal(fetchCount,beforeMediaTypeFetches);

  // Standards-based +json media types are accepted.
  res=makeRes();
  await handler(req(baseBody,{'content-type':'application/vnd.tongjun.rfq+json','x-forwarded-for':'198.51.100.19'}),res);
  assert.equal(res.statusCode,202);
  assertTrace(res);

  // Origin gate rejects explicit untrusted browser origins.
  res=makeRes();
  await handler(req(baseBody,{origin:'https://untrusted.example','x-forwarded-for':'198.51.100.10'}),res);
  assert.equal(res.statusCode,403);
  assert.equal(res.payload.error,'origin_not_allowed');
  assertTrace(res);

  // Direct JSON clients without an Origin remain supported; Origin is not authentication.
  res=makeRes();
  const direct=req(baseBody,{'x-forwarded-for':'198.51.100.20'});
  delete direct.headers.origin;
  await handler(direct,res);
  assert.equal(res.statusCode,202);
  assertTrace(res);

  // Required-field and email validation are traceable and do not call the webhook.
  const beforeValidationFetches=fetchCount;
  const missing={...baseBody}; delete missing.grade;
  res=makeRes();
  await handler(req(missing,{'x-forwarded-for':'198.51.100.11'}),res);
  assert.equal(res.statusCode,400);
  assert.equal(res.payload.error,'missing_fields');
  assert.deepEqual(res.payload.missing,['grade']);
  assertTrace(res);

  res=makeRes();
  await handler(req({...baseBody,email:'not-an-email'},{'x-forwarded-for':'198.51.100.12'}),res);
  assert.equal(res.statusCode,400);
  assert.equal(res.payload.error,'invalid_email');
  assertTrace(res);
  assert.equal(fetchCount,beforeValidationFetches);

  // Honeypot submissions are accepted silently without delivery.
  res=makeRes();
  await handler(req({...baseBody,website:'https://spam.example'},{'x-forwarded-for':'198.51.100.13'}),res);
  assert.equal(res.statusCode,202);
  assert.equal(res.payload.ok,true);
  assertTrace(res);
  assert.equal(fetchCount,beforeValidationFetches);

  // Payload guard is byte-based and runs before field validation.
  res=makeRes();
  await handler(req({...baseBody,notes:'钢'.repeat(8500)},{'x-forwarded-for':'198.51.100.14'}),res);
  assert.equal(res.statusCode,413);
  assert.equal(res.payload.error,'payload_too_large');
  assertTrace(res);

  // Field limits are enforced before delivery.
  res=makeRes();
  await handler(req({...baseBody,name:'N'.repeat(180),application:'A'.repeat(2800)},{'x-forwarded-for':'198.51.100.15'}),res);
  assert.equal(res.statusCode,202);
  assert.equal(sent.name.length,120);
  assert.equal(sent.application.length,2500);

  // Missing, invalid or unsigned downstream routes fail closed with traceable IDs.
  const oldWebhook=process.env.RFQ_WEBHOOK_URL;
  const oldSecret=process.env.RFQ_SHARED_SECRET;

  delete process.env.RFQ_WEBHOOK_URL;
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.16'}),res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.error,'rfq_route_not_configured');
  assertTrace(res);

  process.env.RFQ_WEBHOOK_URL='http://example.invalid/hook';
  process.env.RFQ_SHARED_SECRET='unit-test-secret';
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.22'}),res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.error,'rfq_route_invalid');
  assertTrace(res);

  process.env.RFQ_WEBHOOK_URL='https://example.invalid/hook';
  delete process.env.RFQ_SHARED_SECRET;
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.23'}),res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.error,'rfq_signature_not_configured');
  assertTrace(res);

  process.env.RFQ_WEBHOOK_URL=oldWebhook;
  process.env.RFQ_SHARED_SECRET=oldSecret;

  // Downstream non-2xx and network failures become traceable 502 responses.
  fetchMode='fail';
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.17'}),res);
  assert.equal(res.statusCode,502);
  assert.equal(res.payload.error,'rfq_delivery_failed');
  assertTrace(res);

  fetchMode='throw';
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.18'}),res);
  assert.equal(res.statusCode,502);
  assert.equal(res.payload.error,'rfq_delivery_failed');
  assertTrace(res);
  fetchMode='success';

  // Per-instance abuse gate remains bounded and exposes retry metadata.
  for(let i=1;i<=9;i++){
    res=makeRes();
    await handler(req(baseBody,{'x-forwarded-for':'198.51.100.24'}),res);
    if(i<=8) {
      assert.equal(res.statusCode,202);
      assertTrace(res);
    } else {
      assert.equal(res.statusCode,429);
      assert.equal(res.payload.error,'rate_limited');
      assert.ok(Number(res.headers['Retry-After'])>0);
      assertTrace(res);
    }
  }

  console.log('PASS: RFQ handler — JSON media gate, 48-bit trace IDs, origin semantics, validation, UTF-8 byte limit, honeypot, HMAC webhook integrity, route failures and rate gate validated.');
}

run().catch(err=>{ console.error(err); process.exit(1); });
