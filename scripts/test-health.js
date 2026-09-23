const assert = require('assert');

// Health readiness is now a statement about mail delivery config, not about a webhook hop.

const MAIL_KEYS = [
  'RFQ_MAIL_TRANSPORT',
  'RFQ_MAIL_TO',
  'RFQ_MAIL_FROM',
  'RFQ_MAIL_FROM_NAME',
  'RESEND_API_KEY',
  'MS_GRAPH_TENANT_ID',
  'MS_GRAPH_CLIENT_ID',
  'MS_GRAPH_CLIENT_SECRET',
  'MS_GRAPH_REFRESH_TOKEN',
  'RFQ_SMTP_HOST',
  'RFQ_SMTP_PORT',
  'RFQ_SMTP_USER',
  'RFQ_SMTP_PASS'
];

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
  const saved={};
  for(const key of MAIL_KEYS) saved[key]=process.env[key];
  const oldSha=process.env.TONGJUN_RELEASE_COMMIT;
  const oldEnv=process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT;
  const oldLedger=process.env.RFQ_LEDGER_PATH;

  for(const key of MAIL_KEYS) delete process.env[key];
  delete process.env.RFQ_LEDGER_DISABLED;
  process.env.TONGJUN_RELEASE_COMMIT='1234567890abcdef1234567890abcdef12345678';
  process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT='production';
  process.env.RFQ_LEDGER_PATH='/var/lib/tongjun-rfq/rfq-ledger.jsonl';

  let res=makeRes();
  await handler({method:'GET',headers:{}},res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.ok,false);
  assert.equal(res.payload.mail_transport_configured,false);
  assert.equal(res.payload.mail_recipient_configured,false);
  assert.equal(res.payload.mail_sender_configured,false);
  assert.equal(res.payload.mail_delivery_mode,'unconfigured');
  assert.equal(res.payload.rfq_delivery,'email');
  assert.deepEqual(res.payload.mail_missing_env.includes('RFQ_MAIL_TRANSPORT'),true);
  // The recipient and sender variables belong in the same list: an operator whose only window
  // is /api/health must see every prerequisite, not just the transport one.
  assert.equal(res.payload.mail_missing_env.includes('RFQ_MAIL_TO'),true);
  assert.equal(res.payload.mail_missing_env.includes('RFQ_MAIL_FROM'),true);
  assert.equal(res.payload.rfq_ledger_configured,true);
  assert.equal(res.payload.rfq_ledger_path,'/var/lib/tongjun-rfq/rfq-ledger.jsonl');
  assert.equal(res.payload.site_release,'V34.152 R15.26');
  assert.equal(res.payload.visual_release,'V34.152 R15.7');
  assert.equal(res.payload.hero_release,'V34.152 R15.24');
  assert.equal(res.payload.release,'1234567890abcdef1234567890abcdef12345678'.slice(0,40));
  assert.equal(res.payload.deployment_environment,'production');
  assert.equal(res.headers['Cache-Control'],'no-store');
  assert.equal(res.headers['X-Tongjun-Release'],'V34.152 R15.26');

  // The retired webhook readiness fields must be gone.
  assert.equal('rfq_route_configured' in res.payload,false);
  assert.equal('rfq_route_https_valid' in res.payload,false);
  assert.equal('rfq_signature_configured' in res.payload,false);

  // A recipient without a sender is still not ready.
  process.env.RFQ_MAIL_TRANSPORT='resend';
  process.env.RFQ_MAIL_TO='wuxi304@outlook.com';
  process.env.RESEND_API_KEY='re_test';
  res=makeRes();
  await handler({method:'GET',headers:{}},res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.mail_recipient_configured,true);
  assert.equal(res.payload.mail_sender_configured,false);
  assert.equal(res.payload.ok,false);
  assert.equal(res.payload.mail_missing_env.includes('RFQ_MAIL_FROM'),true);
  assert.equal(res.payload.mail_missing_env.includes('RFQ_MAIL_TO'),false);

  // A consumer-domain sender cannot work with a transactional provider.
  process.env.RFQ_MAIL_FROM='wuxi304@outlook.com';
  res=makeRes();
  await handler({method:'GET',headers:{}},res);
  assert.equal(res.statusCode,503);
  assert.equal(res.payload.mail_sender_configured,true);
  assert.equal(res.payload.mail_transport_configured,false);
  assert.deepEqual(res.payload.mail_invalid_env,['RFQ_MAIL_FROM']);

  // A fully configured deployment reports ready.
  process.env.RFQ_MAIL_FROM='rfq@exoticalloycn.com';
  res=makeRes();
  await handler({method:'GET',headers:{}},res);
  assert.equal(res.statusCode,200);
  assert.equal(res.payload.ok,true);
  assert.equal(res.payload.service,'tongjun-overseas');
  assert.equal(res.payload.mail_transport_configured,true);
  assert.equal(res.payload.mail_recipient_configured,true);
  assert.equal(res.payload.mail_sender_configured,true);
  assert.equal(res.payload.mail_delivery_mode,'resend/http-api');
  assert.deepEqual(res.payload.mail_missing_env,[]);
  assert.deepEqual(res.payload.mail_invalid_env,[]);
  assert.match(res.payload.checked_at,/^\d{4}-\d{2}-\d{2}T/);

  // Graph application mode is ready once tenant, client and secret are present.
  delete process.env.RESEND_API_KEY;
  process.env.RFQ_MAIL_TRANSPORT='graph';
  process.env.MS_GRAPH_TENANT_ID='contoso.onmicrosoft.com';
  process.env.MS_GRAPH_CLIENT_ID='client-id';
  process.env.MS_GRAPH_CLIENT_SECRET='client-secret';
  res=makeRes();
  await handler({method:'GET',headers:{}},res);
  assert.equal(res.statusCode,200);
  assert.equal(res.payload.mail_delivery_mode,'graph/client_credentials');

  // The log transport must never let production report healthy.
  process.env.RFQ_MAIL_TRANSPORT='log';
  res=makeRes();
  await handler({method:'GET',headers:{}},res);
  assert.equal(res.statusCode,503,'log-only delivery must not be production ready');
  assert.equal(res.payload.mail_transport_configured,true);
  assert.equal(res.payload.mail_delivery_mode_safe,false);
  assert.equal(res.payload.ok,false);

  res=makeRes();
  await handler({method:'HEAD',headers:{}},res);
  assert.equal(res.statusCode,503);
  assert.equal(res.ended,true);
  assert.equal(res.headers['X-Tongjun-Release'],'V34.152 R15.26');

  process.env.RFQ_MAIL_TRANSPORT='resend';
  process.env.RESEND_API_KEY='re_test';
  res=makeRes();
  await handler({method:'HEAD',headers:{}},res);
  assert.equal(res.statusCode,200);
  assert.equal(res.ended,true);

  res=makeRes();
  await handler({method:'POST',headers:{}},res);
  assert.equal(res.statusCode,405);
  assert.equal(res.payload.error,'method_not_allowed');
  assert.equal(res.headers.Allow,'GET, HEAD');

  for(const key of MAIL_KEYS){
    if(saved[key]===undefined) delete process.env[key];
    else process.env[key]=saved[key];
  }
  if(oldSha===undefined) delete process.env.TONGJUN_RELEASE_COMMIT;
  else process.env.TONGJUN_RELEASE_COMMIT=oldSha;
  if(oldEnv===undefined) delete process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT;
  else process.env.TONGJUN_DEPLOYMENT_ENVIRONMENT=oldEnv;
  if(oldLedger===undefined) delete process.env.RFQ_LEDGER_PATH;
  else process.env.RFQ_LEDGER_PATH=oldLedger;

  console.log('PASS: R15.26 self-hosted production health now gates on mail delivery readiness (recipient + sender + transport, log refused in production), with release identity, ledger state, HEAD and method gates validated.');
}

run().catch(err=>{console.error(err);process.exit(1);});
