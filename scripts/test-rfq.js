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

  console.log('PASS: RFQ V22 buyer-decision + qualified-offer payload + origin gate validated.');
}

run().catch(err=>{ console.error(err); process.exit(1); });
