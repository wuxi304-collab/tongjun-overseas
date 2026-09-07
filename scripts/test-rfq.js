const assert = require('assert');

async function run(){
  process.env.RFQ_WEBHOOK_URL='https://example.invalid/hook';
  process.env.RFQ_ALLOWED_ORIGINS='https://exoticalloycn.com';
  let sent=null;
  global.fetch=async (_url,opts)=>{ sent=JSON.parse(opts.body); return {ok:true,status:202}; };
  const handler=require('../api/rfq.js');

  const req={
    method:'POST',
    headers:{origin:'https://exoticalloycn.com'},
    body:{
      name:'Buyer',company:'Example',email:'buyer@example.com',grade:'UNS N06625',
      size:'3 x 1000 x 2000 mm',qty:'2 t',application:'Chemical service',
      procurement_stage:'trial',buyer_gate:'approval',decision_ref:'BR-20260907-ABC123',
      approval:'Project AVL',incoterm:'CIF',destination:'Hamburg, Germany',delivery_target:'2026-11-15',packing:'Export seaworthy',offer_ref:'OF-20260907-ABC123'
    }
  };
  let statusCode=200, payload=null;
  const res={setHeader(){},status(n){statusCode=n;return this},json(x){payload=x;return x}};
  await handler(req,res);

  assert.equal(statusCode,202);
  assert.equal(payload.ok,true);
  assert.match(payload.request_id,/^TJ-\d{8}-[0-9A-F]{8}$/);
  assert.equal(sent.procurement_stage,'trial');
  assert.equal(sent.buyer_gate,'approval');
  assert.equal(sent.decision_ref,'BR-20260907-ABC123');
  assert.equal(sent.approval,'Project AVL');
  assert.equal(sent.incoterm,'CIF');
  assert.equal(sent.destination,'Hamburg, Germany');
  assert.equal(sent.delivery_target,'2026-11-15');
  assert.equal(sent.packing,'Export seaworthy');
  assert.equal(sent.offer_ref,'OF-20260907-ABC123');

  const badReq={...req,headers:{origin:'https://untrusted.example'}};
  let badStatus=200;
  const badRes={setHeader(){},status(n){badStatus=n;return this},json(x){return x}};
  await handler(badReq,badRes);
  assert.equal(badStatus,403);

  // No production route: API must fail closed so the browser can invoke the email fallback.
  delete process.env.RFQ_WEBHOOK_URL;
  let routeStatus=200, routePayload=null;
  const routeRes={setHeader(){},status(n){routeStatus=n;return this},json(x){routePayload=x;return x}};
  await handler(req,routeRes);
  assert.equal(routeStatus,503);
  assert.equal(routePayload.error,'rfq_route_not_configured');
  process.env.RFQ_WEBHOOK_URL='https://example.invalid/hook';

  // Lightweight per-instance rate gate: the ninth request from one forwarded IP is rejected.
  let limitedStatus=0;
  for(let i=0;i<9;i++){
    let currentStatus=200;
    const rateReq={...req,headers:{origin:'https://exoticalloycn.com','x-forwarded-for':'203.0.113.25'}};
    const rateRes={setHeader(){},status(n){currentStatus=n;return this},json(x){return x}};
    await handler(rateReq,rateRes);
    limitedStatus=currentStatus;
  }
  assert.equal(limitedStatus,429);

  console.log('PASS: RFQ V25 payload, origin gate, fail-closed fallback path and rate gate validated.');
}

run().catch(err=>{ console.error(err); process.exit(1); });
