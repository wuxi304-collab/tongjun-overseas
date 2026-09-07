const assert = require('assert');

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
  let res=makeRes();
  await handler(req,res);
  assert.equal(res.statusCode,202);
  assert.equal(res.payload.ok,true);
  assert.match(res.payload.request_id,/^TJ-\d{8}-[0-9A-F]{8}$/);
  assert.equal(sent.procurement_stage,'trial');
  assert.equal(sent.buyer_gate,'approval');
  assert.equal(sent.decision_ref,'BR-20260907-ABC123');
  assert.equal(sent.approval,'Project AVL');
  assert.equal(sent.incoterm,'CIF');
  assert.equal(sent.destination,'Hamburg, Germany');
  assert.equal(sent.delivery_target,'2026-11-15');
  assert.equal(sent.packing,'Export seaworthy');
  assert.equal(sent.offer_ref,'OF-20260907-ABC123');

  res=makeRes();
  await handler({...req,headers:{origin:'https://untrusted.example'}},res);
  assert.equal(res.statusCode,403);

  const oldWebhook=process.env.RFQ_WEBHOOK_URL;
  delete process.env.RFQ_WEBHOOK_URL;
  res=makeRes();
  await handler(req,res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.error,'rfq_route_not_configured');
  process.env.RFQ_WEBHOOK_URL=oldWebhook;

  for(let i=1;i<=9;i++){
    res=makeRes();
    await handler({...req,headers:{origin:'https://exoticalloycn.com','x-forwarded-for':'198.51.100.24'}},res);
    if(i<=8) assert.equal(res.statusCode,202);
    else {
      assert.equal(res.statusCode,429);
      assert.equal(res.payload.error,'rate_limited');
      assert.ok(Number(res.headers['Retry-After'])>0);
    }
  }

  console.log('PASS: RFQ payload, origin gate, fail-closed route and rate gate validated.');
}

run().catch(err=>{ console.error(err); process.exit(1); });
