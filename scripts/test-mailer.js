'use strict';

// Mail-delivery regression suite for the webhook-free RFQ architecture.
//
// Covers: configuration resolution and its fail-closed semantics, subject/body composition,
// header-injection defence, all four transports (Graph via fetch stub, Resend via fetch stub,
// SMTP against a real loopback mock server, log), the 502-on-failure contract, and the
// privacy guarantee that the local ledger never stores an inquiry body.

const assert = require('assert');
const fs = require('fs');
const net = require('net');
const os = require('os');
const path = require('path');

const {
  buildRfqEmail,
  buildRfqSubject,
  resolveMailConfig,
  sendRfqEmail
} = require('../server/mailer.js');
const { MailTransportError, encodeHeaderText } = require('../server/mail-transports.js');
const { appendLedger, buildEntry, LEDGER_FIELDS } = require('../server/rfq-ledger.js');

const ROOT = path.join(__dirname, '..');

function tempDir(label) {
  return fs.mkdtempSync(path.join(os.tmpdir(), `tongjun-${label}-`));
}

function baseRecord(overrides) {
  return {
    request_id: 'TJ-20260923-ABCDEF123456',
    received_at: '2026-09-23T03:20:00.000Z',
    site: 'exoticalloycn.com',
    name: 'Anna Müller',
    company: 'Müller GmbH',
    email: 'anna.mueller@example.com',
    country: 'Germany',
    grade: 'Inconel 625',
    standard: 'ASTM B443',
    form: 'Sheet / Plate',
    size: '3 x 1000 x 2000 mm',
    condition: 'Solution annealed',
    qty: '2 t',
    application: 'Chemical service\nWet chloride exposure',
    certificate: 'EN 10204 3.1 + PMI',
    origin: 'China origin accepted',
    incoterm: 'CIF',
    destination: 'Hamburg, Germany',
    notes: 'Need delivery before Q4 shutdown.',
    source: 'resource-page',
    product: 'alloy-625',
    first_landing: '/alloy-625-china',
    first_seen: '2026-09-16T03:00:00.000Z',
    utm_source: 'google',
    website: '',
    ...(overrides || {})
  };
}

function configFor(env) {
  return resolveMailConfig(env);
}

// ------------------------------------------------------------------ configuration

function testConfiguration() {
  const bare = configFor({});
  assert.equal(bare.transport, '');
  assert.equal(bare.ready, false, 'an unconfigured deployment must never report ready');
  assert.equal(bare.recipientConfigured, false);
  assert.equal(bare.transportConfigured, false);

  const recipientOnly = configFor({ RFQ_MAIL_TRANSPORT: 'resend', RFQ_MAIL_TO: 'wuxi304@outlook.com' });
  assert.equal(recipientOnly.recipientConfigured, true);
  assert.equal(recipientOnly.senderConfigured, false);
  assert.equal(recipientOnly.ready, false, 'a recipient without a sender is not ready');
  assert.ok(recipientOnly.missing.includes('RESEND_API_KEY'));

  const invalidRecipient = configFor({ RFQ_MAIL_TRANSPORT: 'resend', RFQ_MAIL_TO: 'not-an-address' });
  assert.equal(invalidRecipient.recipientConfigured, false, 'malformed recipients must fail closed');

  const graphApp = configFor({
    RFQ_MAIL_TRANSPORT: 'graph',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@tongjun-metal.com',
    MS_GRAPH_TENANT_ID: 'contoso.onmicrosoft.com',
    MS_GRAPH_CLIENT_ID: 'client-id',
    MS_GRAPH_CLIENT_SECRET: 'client-secret'
  });
  assert.equal(graphApp.authMode, 'client_credentials');
  assert.equal(graphApp.ready, true);
  assert.equal(graphApp.transportDetail, 'graph/client_credentials');

  const graphAppMissingSecret = configFor({
    RFQ_MAIL_TRANSPORT: 'graph',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@tongjun-metal.com',
    MS_GRAPH_TENANT_ID: 'contoso.onmicrosoft.com',
    MS_GRAPH_CLIENT_ID: 'client-id'
  });
  assert.equal(graphAppMissingSecret.ready, false);
  assert.ok(graphAppMissingSecret.missing.includes('MS_GRAPH_CLIENT_SECRET'));

  const graphDelegated = configFor({
    RFQ_MAIL_TRANSPORT: 'graph',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'wuxi304@outlook.com',
    MS_GRAPH_CLIENT_ID: 'client-id',
    MS_GRAPH_REFRESH_TOKEN: 'refresh-token'
  });
  assert.equal(graphDelegated.authMode, 'refresh_token');
  assert.equal(graphDelegated.tenantId, 'common', 'delegated personal-account mode must default to /common');
  assert.equal(graphDelegated.ready, true);

  const smtp = configFor({
    RFQ_MAIL_TRANSPORT: 'smtp',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@exoticalloycn.com',
    RFQ_SMTP_HOST: 'smtp.example.com',
    RFQ_SMTP_USER: 'apikey',
    RFQ_SMTP_PASS: 'secret'
  });
  assert.equal(smtp.ready, true);
  assert.equal(smtp.secure, true, 'SMTP must default to implicit TLS');

  const resend = configFor({
    RFQ_MAIL_TRANSPORT: 'resend',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@exoticalloycn.com',
    RESEND_API_KEY: 're_test'
  });
  assert.equal(resend.ready, true);

  const resendConsumerSender = configFor({
    RFQ_MAIL_TRANSPORT: 'resend',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'wuxi304@outlook.com',
    RESEND_API_KEY: 're_test'
  });
  assert.equal(resendConsumerSender.transportConfigured, false, 'a consumer-domain sender cannot be used with Resend');
  assert.ok(resendConsumerSender.notes.join(' ').includes('verified sending domain'));

  // A log transport must never let production look healthy: that is the silent-failure trap.
  const logInProduction = configFor({
    RFQ_MAIL_TRANSPORT: 'log',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@exoticalloycn.com',
    TONGJUN_DEPLOYMENT_ENVIRONMENT: 'production'
  });
  assert.equal(logInProduction.transportConfigured, true);
  assert.equal(logInProduction.deliveryModeSafe, false);
  assert.equal(logInProduction.ready, false, 'log transport must never be production-ready');

  const logLocal = configFor({
    RFQ_MAIL_TRANSPORT: 'log',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@exoticalloycn.com',
    TONGJUN_DEPLOYMENT_ENVIRONMENT: 'local'
  });
  assert.equal(logLocal.ready, true, 'log transport is allowed outside production');

  const unknown = configFor({ RFQ_MAIL_TRANSPORT: 'carrier-pigeon', RFQ_MAIL_TO: 'a@b.com', RFQ_MAIL_FROM: 'c@d.com' });
  assert.equal(unknown.ready, false);
}

// ---------------------------------------------------------------- subject + body

function testSubject() {
  const subject = buildRfqSubject(baseRecord());
  assert.equal(subject, '[Tongjun RFQ] Inconel 625 · Sheet · Germany · Müller GmbH');

  // A customer-supplied company name must not be able to inject headers.
  const injected = buildRfqSubject(baseRecord({
    company: 'Acme\r\nBcc: attacker@example.com',
    country: 'Germany\r\nX-Injected: yes'
  }));
  assert.ok(!/[\r\n]/.test(injected), 'subject must contain no CR/LF');
  assert.ok(!/Bcc:/i.test(injected), 'subject must not carry injected headers');
  assert.ok(injected.includes('Acme'), 'the legitimate part of the name must survive');

  assert.equal(encodeHeaderText('Müller GmbH').startsWith('=?UTF-8?B?'), true);
  assert.equal(encodeHeaderText('Plain ASCII Ltd'), 'Plain ASCII Ltd');
}

function testBodyCoversEveryAcceptedField() {
  const source = fs.readFileSync(path.join(ROOT, 'api', 'rfq.js'), 'utf8');
  const limits = /const\s+LIMITS\s*=\s*\{(.*?)\};/s.exec(source);
  assert.ok(limits, 'api/rfq.js LIMITS block not found');
  const keys = [...limits[1].matchAll(/\b([A-Za-z_][A-Za-z0-9_]*)\s*:/g)].map(m => m[1]);
  assert.ok(keys.length > 30, `expected a substantial field list, saw ${keys.length}`);

  const record = baseRecord();
  for (const key of keys) {
    if (key === 'website') continue;
    record[key] = `VAL_${key}`;
  }

  const config = configFor({
    RFQ_MAIL_TRANSPORT: 'log',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@exoticalloycn.com',
    TONGJUN_DEPLOYMENT_ENVIRONMENT: 'local'
  });
  const message = buildRfqEmail(record, config);

  const dropped = keys.filter(key => key !== 'website' && !message.text.includes(`VAL_${key}`));
  assert.deepEqual(dropped, [], `fields accepted by the API but missing from the email: ${dropped.join(', ')}`);
  assert.ok(!message.text.includes('VAL_website'), 'the honeypot field must never be forwarded');

  // A buyer's newlines must survive in the body for readability (checked on a pristine record,
  // because the loop above overwrote every field with a placeholder). Continuation lines are
  // indented to the value column, so the break is asserted with the indent allowed for.
  const pristine = buildRfqEmail(baseRecord(), config);
  assert.ok(
    /Chemical service\n\s+Wet chloride exposure/.test(pristine.text),
    'body must preserve paragraph breaks'
  );
  assert.ok(pristine.text.includes('Reply to this message to answer Anna Müller directly.'));

  // Reply-To is the buyer, not the website server.
  assert.equal(pristine.replyTo, 'anna.mueller@example.com');
  assert.equal(pristine.fromAddress, 'rfq@exoticalloycn.com');
  assert.equal(pristine.subject, '[Tongjun RFQ] Inconel 625 · Sheet · Germany · Müller GmbH');

  // HTML must escape customer input.
  const hostile = buildRfqEmail(baseRecord({ company: '<script>alert(1)</script>', notes: 'a & b' }), config);
  assert.ok(!hostile.html.includes('<script>'), 'customer input must be HTML-escaped');
  assert.ok(hostile.html.includes('&lt;script&gt;'), 'escaped form expected in the HTML body');
  assert.ok(hostile.html.includes('a &amp; b'), 'ampersands must be escaped in the HTML body');
}

// ------------------------------------------------------------------ transports

function testGraphTransportIsTwoStepAndFailsLoud() {
  const config = configFor({
    RFQ_MAIL_TRANSPORT: 'graph',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@tongjun-metal.com',
    MS_GRAPH_TENANT_ID: 'contoso.onmicrosoft.com',
    MS_GRAPH_CLIENT_ID: 'client-id',
    MS_GRAPH_CLIENT_SECRET: 'client-secret'
  });
  const calls = [];
  const fetchStub = async (url, options) => {
    calls.push(String(url));
    if (String(url).includes('login.microsoftonline.com')) {
      return { ok: true, status: 200, json: async () => ({ access_token: 'token-abc' }) };
    }
    if (String(url).endsWith('/messages')) {
      const body = JSON.parse(options.body);
      assert.equal(body.subject, '[Tongjun RFQ] Inconel 625 · Sheet · Germany · Müller GmbH');
      assert.equal(body.replyTo[0].emailAddress.address, 'anna.mueller@example.com');
      assert.equal(body.toRecipients[0].emailAddress.address, 'wuxi304@outlook.com');
      assert.equal(body.body.contentType, 'HTML');
      assert.ok(body.body.content.includes('Müller GmbH') || body.body.content.includes('&#'));
      return { ok: true, status: 201, json: async () => ({ id: 'AAMkAGI2TAAA=' }) };
    }
    if (String(url).endsWith('/send')) return { ok: true, status: 202, json: async () => null };
    throw new Error(`unexpected graph call ${url}`);
  };

  return (async () => {
    const message = buildRfqEmail(baseRecord(), config);
    const result = await sendRfqEmail(message, config, { fetch: fetchStub });
    assert.equal(result.messageId, 'AAMkAGI2TAAA=');
    assert.equal(result.transport, 'graph');
    assert.equal(calls.length, 3, `expected token + draft + send, saw ${calls.length}`);
    assert.ok(calls[0].includes('login.microsoftonline.com'), 'token endpoint first');
    assert.ok(calls[1].includes('/users/rfq%40tongjun-metal.com/messages'), `mailbox-addressed draft expected, got ${calls[1]}`);
    assert.ok(calls[2].endsWith('/messages/AAMkAGI2TAAA%3D/send') || calls[2].includes('/send'), 'draft must be sent');

    // A rejected send must surface as an error, never as a silent success.
    const rejecting = async (url) => {
      if (String(url).includes('login.microsoftonline.com')) {
        return { ok: true, status: 200, json: async () => ({ access_token: 'token-abc' }) };
      }
      return { ok: false, status: 403, json: async () => ({ error: { code: 'ErrorAccessDenied', message: 'no Mail.Send' } }) };
    };
    await assert.rejects(
      () => sendRfqEmail(buildRfqEmail(baseRecord(), config), config, { fetch: rejecting }),
      err => err instanceof MailTransportError && /graph_send_rejected/.test(err.code),
      'a Graph rejection must throw'
    );

    // Token acquisition failure is its own diagnostic.
    const tokenDown = async () => ({ ok: false, status: 401, json: async () => ({ error: 'invalid_client' }) });
    await assert.rejects(
      () => sendRfqEmail(buildRfqEmail(baseRecord(), config), config, { fetch: tokenDown }),
      err => err instanceof MailTransportError && /graph_token_rejected/.test(err.code)
    );

    const networkDown = async () => {
      throw new Error('ECONNREFUSED');
    };
    await assert.rejects(
      () => sendRfqEmail(buildRfqEmail(baseRecord(), config), config, { fetch: networkDown }),
      err => err instanceof MailTransportError && /graph_token_unreachable/.test(err.code)
    );

    // An unconfigured transport must refuse before touching the network.
    await assert.rejects(
      () => sendRfqEmail(buildRfqEmail(baseRecord(), configFor({})), configFor({}), { fetch: fetchStub }),
      err => err instanceof MailTransportError && /mail_not_configured/.test(err.code)
    );
  })();
}

function testResendTransport() {
  const config = configFor({
    RFQ_MAIL_TRANSPORT: 'resend',
    RFQ_MAIL_TO: 'wuxi304@outlook.com',
    RFQ_MAIL_FROM: 'rfq@exoticalloycn.com',
    RFQ_MAIL_FROM_NAME: 'Tongjun RFQ',
    RESEND_API_KEY: 're_test'
  });
  return (async () => {
    let captured = null;
    const ok = async (url, options) => {
      assert.equal(String(url), 'https://api.resend.com/emails');
      assert.equal(options.headers.Authorization, 'Bearer re_test');
      captured = JSON.parse(options.body);
      return { ok: true, status: 200, json: async () => ({ id: 'resend-message-id' }) };
    };
    const result = await sendRfqEmail(buildRfqEmail(baseRecord(), config), config, { fetch: ok });
    assert.equal(result.messageId, 'resend-message-id');
    assert.deepEqual(captured.to, ['wuxi304@outlook.com']);
    assert.equal(captured.reply_to, 'anna.mueller@example.com');
    assert.equal(captured.from, '"Tongjun RFQ" <rfq@exoticalloycn.com>');
    assert.ok(captured.subject.includes('Müller GmbH'));

    const failing = async () => ({ ok: false, status: 422, json: async () => ({ message: 'domain not verified' }) });
    await assert.rejects(
      () => sendRfqEmail(buildRfqEmail(baseRecord(), config), config, { fetch: failing }),
      err => err instanceof MailTransportError && /resend_send_rejected/.test(err.code)
    );
  })();
}

function startMockSmtp() {
  return new Promise(resolve => {
    const state = { commands: [], authPlain: '', mailFrom: '', rcptTo: [], data: '' };
    const server = net.createServer(socket => {
      socket.setEncoding('utf8');
      socket.write('220 mock.tongjun.test ESMTP ready\r\n');
      let buffer = '';
      let inData = false;
      let dataLines = [];
      socket.on('data', chunk => {
        buffer += chunk;
        let index = buffer.indexOf('\r\n');
        while (index >= 0) {
          const line = buffer.slice(0, index);
          buffer = buffer.slice(index + 2);
          if (inData) {
            if (line === '.') {
              inData = false;
              state.data = dataLines.join('\r\n');
              socket.write('250 2.0.0 Ok: queued as MOCKQID123\r\n');
            } else {
              dataLines.push(line.startsWith('..') ? line.slice(1) : line);
            }
          } else if (line) {
            state.commands.push(line);
            const upper = line.toUpperCase();
            if (upper.startsWith('EHLO')) {
              socket.write('250-mock.tongjun.test\r\n250-AUTH PLAIN LOGIN\r\n250 SIZE 10485760\r\n');
            } else if (upper.startsWith('AUTH PLAIN')) {
              state.authPlain = line.slice(11).trim();
              socket.write('235 2.7.0 Authentication successful\r\n');
            } else if (upper.startsWith('MAIL FROM')) {
              state.mailFrom = line;
              socket.write('250 2.1.0 Ok\r\n');
            } else if (upper.startsWith('RCPT TO')) {
              state.rcptTo.push(line);
              socket.write('250 2.1.5 Ok\r\n');
            } else if (upper === 'DATA') {
              inData = true;
              dataLines = [];
              socket.write('354 End data with <CR><LF>.<CR><LF>\r\n');
            } else if (upper === 'QUIT') {
              socket.write('221 2.0.0 Bye\r\n');
              socket.end();
            } else {
              socket.write('250 2.0.0 Ok\r\n');
            }
          }
          index = buffer.indexOf('\r\n');
        }
      });
      socket.on('error', () => {});
    });
    server.listen(0, '127.0.0.1', () => resolve({ server, state, port: server.address().port }));
  });
}

function decodeBase64Part(data, contentType) {
  const marker = `Content-Type: ${contentType}`;
  const start = data.indexOf(marker);
  if (start < 0) return '';
  const after = data.slice(start);
  const blank = after.indexOf('\r\n\r\n');
  const bodyStart = blank + 4;
  const end = after.indexOf('\r\n--', bodyStart);
  const encoded = after.slice(bodyStart, end < 0 ? undefined : end).replace(/\s+/g, '');
  return Buffer.from(encoded, 'base64').toString('utf8');
}

async function testSmtpTransport() {
  const { server, state, port } = await startMockSmtp();
  try {
    const config = configFor({
      RFQ_MAIL_TRANSPORT: 'smtp',
      RFQ_MAIL_TO: 'wuxi304@outlook.com',
      RFQ_MAIL_FROM: 'rfq@exoticalloycn.com',
      RFQ_MAIL_FROM_NAME: 'Tongjun RFQ Desk',
      RFQ_SMTP_HOST: '127.0.0.1',
      RFQ_SMTP_PORT: String(port),
      RFQ_SMTP_SECURE: '0',
      RFQ_SMTP_STARTTLS: '0',
      RFQ_SMTP_ALLOW_PLAINTEXT: '1',
      RFQ_SMTP_USER: 'smtp-user',
      RFQ_SMTP_PASS: 'smtp-pass'
    });
    assert.equal(config.ready, true);

    const result = await sendRfqEmail(buildRfqEmail(baseRecord(), config), config);
    assert.equal(result.transport, 'smtp');
    assert.equal(result.messageId, 'MOCKQID123', 'a queue id from the relay should be captured');

    assert.ok(state.commands[0].startsWith('EHLO'), `EHLO expected first, saw ${state.commands[0]}`);
    assert.equal(state.authPlain, Buffer.from('\u0000smtp-user\u0000smtp-pass', 'utf8').toString('base64'));
    assert.ok(state.mailFrom.includes('<rfq@exoticalloycn.com>'), `MAIL FROM wrong: ${state.mailFrom}`);
    assert.ok(state.rcptTo[0].includes('<wuxi304@outlook.com>'), `RCPT TO wrong: ${state.rcptTo[0]}`);
    assert.ok(state.commands.includes('DATA'));

    assert.ok(/^From: "Tongjun RFQ Desk" <rfq@exoticalloycn\.com>$/m.test(state.data), 'From header with display name');
    assert.ok(/^Reply-To: anna\.mueller@example\.com$/m.test(state.data), 'Reply-To must be the buyer');
    assert.ok(/^Subject: =\?UTF-8\?B\?/m.test(state.data), 'non-ASCII subject must be RFC 2047 encoded');
    assert.ok(/^Message-ID: <tj-[0-9a-f]+@exoticalloycn\.com>$/m.test(state.data), 'Message-ID must be generated');
    assert.ok(/^X-Tongjun-Request-Id: TJ-20260923-ABCDEF123456$/m.test(state.data), 'request id must be traceable in the header');
    assert.ok(state.data.includes('multipart/alternative'), 'the message must carry both text and HTML parts');

    const text = decodeBase64Part(state.data, 'text/plain; charset=utf-8');
    const html = decodeBase64Part(state.data, 'text/html; charset=utf-8');
    assert.ok(text.includes('Müller GmbH'), 'text part must carry the customer data');
    assert.ok(text.includes('VAL_') === false, 'no placeholder leakage');
    assert.ok(html.includes('<table'), 'HTML part must render the field table');
    assert.ok(html.includes('Müller GmbH'));

    // Plaintext credentials must be refused once the target is not loopback.
    const remoteCleartext = configFor({
      RFQ_MAIL_TRANSPORT: 'smtp',
      RFQ_MAIL_TO: 'wuxi304@outlook.com',
      RFQ_MAIL_FROM: 'rfq@exoticalloycn.com',
      RFQ_SMTP_HOST: 'smtp.remote.example',
      RFQ_SMTP_PORT: '25',
      RFQ_SMTP_SECURE: '0',
      RFQ_SMTP_STARTTLS: '0',
      RFQ_SMTP_ALLOW_PLAINTEXT: '1',
      RFQ_SMTP_USER: 'u',
      RFQ_SMTP_PASS: 'p'
    });
    await assert.rejects(
      () => sendRfqEmail(buildRfqEmail(baseRecord(), remoteCleartext), remoteCleartext),
      err => err instanceof MailTransportError && /smtp_insecure_refused/.test(err.code),
      'cleartext SMTP to a remote host must be refused'
    );

    // A 550 at RCPT time must fail the whole submission rather than be swallowed.
    const rejectingPort = await (() => new Promise(resolve => {
      const s = net.createServer(socket => {
        socket.setEncoding('utf8');
        socket.write('220 mock.reject\r\n');
        socket.on('data', chunk => {
          const upper = String(chunk).toUpperCase();
          if (upper.startsWith('EHLO')) socket.write('250-mock\r\n250 AUTH PLAIN\r\n');
          else if (upper.startsWith('AUTH')) socket.write('235 ok\r\n');
          else if (upper.startsWith('MAIL FROM')) socket.write('250 ok\r\n');
          else if (upper.startsWith('RCPT TO')) socket.write('550 5.1.1 mailbox unavailable\r\n');
          else socket.write('221 bye\r\n');
        });
        socket.on('error', () => {});
      });
      s.listen(0, '127.0.0.1', () => resolve({ server: s, port: s.address().port }));
    }))();
    try {
      const rejectConfig = { ...config, port: rejectingPort.port, transportDetail: 'smtp/test' };
      await assert.rejects(
        () => sendRfqEmail(buildRfqEmail(baseRecord(), rejectConfig), rejectConfig),
        err => err instanceof MailTransportError && /smtp_command_rejected/.test(err.code)
      );
    } finally {
      rejectingPort.server.close();
    }
  } finally {
    server.close();
  }
}

// ---------------------------------------------------------------------- ledger

async function testLedger() {
  const dir = tempDir('ledger');
  const target = path.join(dir, 'rfq-ledger.jsonl');
  const record = baseRecord();

  const written = appendLedger({
    requestId: record.request_id,
    record,
    status: 'delivered',
    transport: 'graph',
    messageId: 'AAMkAGI2TAAA=',
    deliveredAt: '2026-09-23T03:20:07.000Z'
  }, { path: target });
  assert.equal(written.written, true);

  appendLedger({
    requestId: 'TJ-20260923-000000000001',
    record: { request_id: 'TJ-20260923-000000000001', company: 'Fail Ltd', email: 'fail@example.com' },
    status: 'failed',
    transport: 'resend',
    error: 'resend_send_rejected'
  }, { path: target });

  const lines = fs.readFileSync(target, 'utf8').trim().split('\n');
  assert.equal(lines.length, 2);

  const first = JSON.parse(lines[0]);
  assert.deepEqual(Object.keys(first).sort(), [...LEDGER_FIELDS].sort(), 'ledger must contain exactly the whitelisted fields');
  assert.equal(first.status, 'delivered');
  assert.equal(first.company, 'Müller GmbH');
  assert.equal(first.message_id, 'AAMkAGI2TAAA=');

  // The inquiry body must be structurally absent, not merely truncated.
  const serialized = JSON.stringify(first);
  assert.ok(!serialized.includes('Chemical service'), 'application text must never reach the ledger');
  assert.ok(!serialized.includes('Hamburg'), 'destination must never reach the ledger');
  assert.ok(!serialized.includes('Need delivery'), 'customer notes must never reach the ledger');
  assert.ok(!('notes' in first) && !('application' in first) && !('size' in first));

  // Unknown status values are downgraded rather than trusted.
  assert.equal(buildEntry({ status: 'DROP TABLE' }).status, 'failed');

  // A ledger write failure must not throw: losing the log line cannot break a submission.
  const unwritable = appendLedger({ requestId: 'TJ-X', record: {} }, { path: path.join(target, 'nested', 'nope.jsonl') });
  assert.equal(unwritable.written, false);
  assert.ok(unwritable.error, 'the failure must be reported to the caller');

  // Disabling the ledger is respected.
  const disabled = appendLedger({ requestId: 'TJ-Y', record: {} }, { env: { RFQ_LEDGER_DISABLED: '1' }, path: target });
  assert.equal(disabled.written, false);
  assert.equal(disabled.skipped, 'disabled');

  fs.rmSync(dir, { recursive: true, force: true });
}

async function main() {
  testConfiguration();
  testSubject();
  testBodyCoversEveryAcceptedField();
  await testGraphTransportIsTwoStepAndFailsLoud();
  await testResendTransport();
  await testSmtpTransport();
  await testLedger();

  console.log(
    'PASS: RFQ mail delivery — fail-closed configuration (incl. log-in-production refusal), '
    + 'subject/body composition with header-injection defence and full field coverage, '
    + 'graph two-step draft+send with loud failures, resend API, SMTP over a live mock relay, '
    + 'and a body-free local ledger all validated.'
  );
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
