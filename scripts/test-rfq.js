const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

// RFQ handler regression suite for the mail-delivery architecture: browser -> /api/rfq ->
// mail transport -> buyer-facing mailbox, with a body-free local delivery ledger.

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

function readLedger(file){
  try{
    return fs.readFileSync(file,'utf8').trim().split('\n').filter(Boolean).map(line=>JSON.parse(line));
  }catch{
    return [];
  }
}

async function run(){
  const ledgerDir=fs.mkdtempSync(path.join(os.tmpdir(),'tongjun-rfq-test-'));
  const ledgerFile=path.join(ledgerDir,'rfq-ledger.jsonl');

  process.env.RFQ_MAIL_TRANSPORT='resend';
  process.env.RFQ_MAIL_TO='wuxi304@outlook.com';
  process.env.RFQ_MAIL_FROM='rfq@exoticalloycn.com';
  process.env.RESEND_API_KEY='re_unit_test';
  process.env.RFQ_ALLOWED_ORIGINS='https://exoticalloycn.com';
  process.env.RFQ_LEDGER_PATH=ledgerFile;
  delete process.env.RFQ_LEDGER_DISABLED;
  process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT='production';

  let sentMail=null;
  let fetchMode='success';
  let fetchCount=0;
  global.fetch=async (url,opts)=>{
    fetchCount+=1;
    sentMail=JSON.parse(String(opts.body||'{}'));
    if(fetchMode==='throw') throw new Error('network_down');
    if(fetchMode==='fail') return {ok:false,status:503,json:async()=>({message:'relay_unavailable'})};
    return {ok:true,status:200,json:async()=>({id:`msg-${fetchCount}`})};
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
  const mailHas=value=>assert.ok(String(sentMail&&sentMail.text||'').includes(value),`email body missing: ${value}`);

  // Successful delivery preserves advanced technical + attribution context in the email body.
  let res=makeRes();
  await handler(req(),res);
  assert.equal(res.statusCode,202);
  assert.equal(res.payload.ok,true);
  assert.equal(res.payload.delivery,'resend');
  assertTrace(res);
  assert.deepEqual(sentMail.to,['wuxi304@outlook.com']);
  assert.equal(sentMail.reply_to,'buyer@example.com','Reply-To must be the buyer');
  assert.equal(sentMail.headers['X-Tongjun-Request-Id'],res.payload.request_id);
  assert.ok(sentMail.subject.startsWith('[Tongjun RFQ] UNS N06625 · Sheet'),`unexpected subject: ${sentMail.subject}`);
  mailHas(res.payload.request_id);
  mailHas('trial');
  mailHas('approval');
  mailHas('BR-20260907-ABC123');
  mailHas('Project AVL');
  mailHas('CIF');
  mailHas('Hamburg, Germany');
  mailHas('2026-11-15');
  mailHas('Export seaworthy');
  mailHas('OF-20260907-ABC123');
  mailHas('Lead time starts after technical release');
  mailHas('buyer-decision');
  mailHas('DEV-01');
  mailHas('separate-alternate');
  mailHas('buyer-specifies-source-provides');
  mailHas('third-party-witness');
  mailHas('QUALIFIED WITH CONDITIONS');
  mailHas('technical=READY');
  mailHas('VERIFY > QUALIFY > ALIGN > OFFER');
  mailHas('alloy-625');
  mailHas('2026-09-16T03:00:00.000Z');
  mailHas('Buyer note');

  // The local ledger records delivery without ever storing the inquiry body.
  let ledger=readLedger(ledgerFile);
  assert.equal(ledger.length,1,'one submission must produce exactly one ledger line');
  assert.equal(ledger[0].status,'delivered');
  assert.equal(ledger[0].request_id,res.payload.request_id);
  assert.equal(ledger[0].message_id,'msg-1');
  assert.equal(ledger[0].transport,'resend');
  assert.equal(ledger[0].company,'Example');
  assert.ok(!('notes' in ledger[0]) && !('application' in ledger[0]),'the inquiry body must never reach the ledger');
  assert.ok(!JSON.stringify(ledger[0]).includes('Buyer note'),'customer notes must never reach the ledger');

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

  // Required-field and email validation are traceable and never reach the transport.
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

  // Honeypot submissions are accepted silently without delivery or ledger noise.
  const ledgerBeforeHoneypot=readLedger(ledgerFile).length;
  res=makeRes();
  await handler(req({...baseBody,website:'https://spam.example'},{'x-forwarded-for':'198.51.100.13'}),res);
  assert.equal(res.statusCode,202);
  assert.equal(res.payload.ok,true);
  assertTrace(res);
  assert.equal(fetchCount,beforeValidationFetches);
  assert.equal(readLedger(ledgerFile).length,ledgerBeforeHoneypot);
  assert.ok(!String(sentMail.text).includes('spam.example'),'the honeypot value must never be delivered');

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
  assert.ok(sentMail.text.includes('N'.repeat(120)),'name must be truncated to 120 characters');
  assert.ok(!sentMail.text.includes('N'.repeat(121)),'name must not exceed 120 characters');
  assert.ok(sentMail.text.includes('A'.repeat(2500)),'application must be truncated to 2500 characters');
  assert.ok(!sentMail.text.includes('A'.repeat(2501)),'application must not exceed 2500 characters');

  // Mail configuration gaps fail closed with distinct, traceable 503 errors.
  const mailEnv=['RFQ_MAIL_TRANSPORT','RFQ_MAIL_TO','RFQ_MAIL_FROM','RESEND_API_KEY'];
  const savedMailEnv={};
  for(const key of mailEnv) savedMailEnv[key]=process.env[key];

  delete process.env.RFQ_MAIL_TO;
  const ledgerBeforeConfigFailure=readLedger(ledgerFile).length;
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.16'}),res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.error,'mail_recipient_not_configured');
  assertTrace(res);

  process.env.RFQ_MAIL_TO='wuxi304@outlook.com';
  delete process.env.RFQ_MAIL_FROM;
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.21'}),res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.error,'mail_sender_not_configured');
  assertTrace(res);

  process.env.RFQ_MAIL_FROM='rfq@exoticalloycn.com';
  delete process.env.RESEND_API_KEY;
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.22'}),res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.error,'mail_transport_not_configured');
  assertTrace(res);

  // A submission that could not be delivered must still be visible locally.
  const configFailures=readLedger(ledgerFile).slice(ledgerBeforeConfigFailure);
  assert.equal(configFailures.length,3,'every undeliverable submission must be recorded');
  assert.ok(configFailures.every(entry=>entry.status==='rejected_config'));

  // A log transport in production is refused outright rather than pretending to deliver.
  process.env.RFQ_MAIL_TRANSPORT='log';
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.23'}),res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.error,'mail_delivery_mode_unsafe','a log-only transport must never look like a working delivery path');
  assertTrace(res);

  process.env.RFQ_MAIL_TRANSPORT='resend';
  process.env.RESEND_API_KEY='re_unit_test';
  for(const key of mailEnv) if(savedMailEnv[key]===undefined) delete process.env[key]; else process.env[key]=savedMailEnv[key];

  // Transport failures and network errors become traceable 502 responses, and are logged.
  const ledgerBeforeDeliveryFailure=readLedger(ledgerFile).length;
  fetchMode='fail';
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.17'}),res);
  assert.equal(res.statusCode,502);
  assert.equal(res.payload.error,'rfq_delivery_failed');
  assert.equal(res.payload.delivery_error,'resend_send_rejected');
  assertTrace(res);

  fetchMode='throw';
  res=makeRes();
  await handler(req(baseBody,{'x-forwarded-for':'198.51.100.18'}),res);
  assert.equal(res.statusCode,502);
  assert.equal(res.payload.error,'rfq_delivery_failed');
  assert.equal(res.payload.delivery_error,'resend_unreachable');
  assertTrace(res);
  fetchMode='success';

  const deliveryFailures=readLedger(ledgerFile).slice(ledgerBeforeDeliveryFailure);
  assert.equal(deliveryFailures.length,2);
  assert.ok(deliveryFailures.every(entry=>entry.status==='failed'));
  assert.equal(deliveryFailures[0].error,'resend_send_rejected');

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

  // Every reply the buyer can send goes to the buyer, never back to the server.
  res=makeRes();
  await handler(req({...baseBody,email:'second.buyer@example.org'},{'x-forwarded-for':'198.51.100.25'}),res);
  assert.equal(res.statusCode,202);
  assert.equal(sentMail.reply_to,'second.buyer@example.org');

  delete process.env.RFQ_LEDGER_PATH;
  fs.rmSync(ledgerDir,{recursive:true,force:true});

  console.log('PASS: RFQ handler — JSON media gate, 48-bit trace IDs, origin semantics, validation, UTF-8 byte limit, honeypot, mail delivery with buyer Reply-To, fail-closed mail configuration, 502 delivery failures, body-free ledger and rate gate validated.');
}

run().catch(err=>{ console.error(err); process.exit(1); });
