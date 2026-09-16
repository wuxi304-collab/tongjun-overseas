const assert = require('assert');

function makeRes(){
  let statusCode=200,payload=null,ended=false;
  const headers={};
  return {
    setHeader(k,v){headers[k]=v;},
    status(n){statusCode=n;return this;},
    json(x){payload=x;return x;},
    end(){ended=true;return this;},
    get statusCode(){return statusCode;},
    get payload(){return payload;},
    get headers(){return headers;},
    get ended(){return ended;}
  };
}

async function run(){
  const handler=require('../api/health.js');
  const oldWebhook=process.env.RFQ_WEBHOOK_URL;
  const oldSha=process.env.VERCEL_GIT_COMMIT_SHA;

  delete process.env.RFQ_WEBHOOK_URL;
  process.env.VERCEL_GIT_COMMIT_SHA='1234567890abcdef1234567890abcdef12345678';
  let res=makeRes();
  await handler({method:'GET',headers:{}},res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.ok,false);
  assert.equal(res.payload.rfq_route_configured,false);
  assert.equal(res.payload.release,'1234567890abcdef1234567890abcdef12345678'.slice(0,40));
  assert.equal(res.headers['Cache-Control'],'no-store');

  process.env.RFQ_WEBHOOK_URL='https://example.invalid/hook';
  res=makeRes();
  await handler({method:'GET',headers:{}},res);
  assert.equal(res.statusCode,200);
  assert.equal(res.payload.ok,true);
  assert.equal(res.payload.service,'tongjun-overseas');
  assert.equal(res.payload.rfq_route_configured,true);
  assert.match(res.payload.checked_at,/^\d{4}-\d{2}-\d{2}T/);

  res=makeRes();
  await handler({method:'HEAD',headers:{}},res);
  assert.equal(res.statusCode,200);
  assert.equal(res.ended,true);

  res=makeRes();
  await handler({method:'POST',headers:{}},res);
  assert.equal(res.statusCode,405);
  assert.equal(res.payload.error,'method_not_allowed');
  assert.equal(res.headers.Allow,'GET, HEAD');

  if(oldWebhook===undefined) delete process.env.RFQ_WEBHOOK_URL;
  else process.env.RFQ_WEBHOOK_URL=oldWebhook;
  if(oldSha===undefined) delete process.env.VERCEL_GIT_COMMIT_SHA;
  else process.env.VERCEL_GIT_COMMIT_SHA=oldSha;

  console.log('PASS: production health endpoint readiness, HEAD and method gate validated.');
}

run().catch(err=>{console.error(err);process.exit(1);});
