'use strict';

// RFQ mail composer + configuration resolver.
//
// Replaces the previous webhook hop (browser -> /api/rfq -> RFQ_WEBHOOK_URL -> ???) with a
// direct server-side send:  browser -> https -> nginx -> 127.0.0.1:8787 -> mailbox.
//
// Three invariants this module exists to protect:
//   1. Fail closed. Missing configuration is reported as unconfigured, never as "sent".
//   2. Fail loud. A delivery throw becomes HTTP 502 upstream; the buyer never sees success.
//   3. Never leak. Only whitelisted, non-sensitive fields reach the local ledger.

const {
  MailTransportError,
  deliver,
  headerValue,
  isValidAddress,
  normalizeAddress
} = require('./mail-transports.js');

const DEFAULT_FROM_NAME = 'Tongjun RFQ Desk';

// Consumer mailbox domains can never be a verified transactional sender.
const CONSUMER_MAIL_DOMAINS = [
  'outlook.com',
  'hotmail.com',
  'live.com',
  'msn.com',
  'gmail.com',
  'googlemail.com',
  'yahoo.com',
  'qq.com',
  'foxmail.com',
  '163.com',
  '126.com',
  'sina.com'
];

const TRANSPORT_ENV_NAMES = {
  graph: 'MS_GRAPH_CLIENT_ID',
  smtp: 'RFQ_SMTP_HOST',
  resend: 'RESEND_API_KEY',
  log: ''
};

function readEnv(env, key) {
  return String((env || process.env)[key] == null ? '' : (env || process.env)[key]).trim();
}

function splitList(value) {
  return String(value == null ? '' : value)
    .split(',')
    .map(item => item.trim())
    .filter(Boolean);
}

function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Header-safe field: newlines collapse, so a customer-supplied company name can never
// inject an extra mail header.
function headerField(value, max) {
  return headerValue(value, max || 240);
}

// Body-safe field: control characters are stripped but newlines survive, because a note or
// an application description is meant to be read as paragraphs.
function bodyField(value, max) {
  return String(value == null ? '' : value)
    .replace(/\r\n?/g, '\n')
    .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, ' ')
    .replace(/[ \t]+$/gm, '')
    .trim()
    .slice(0, max || 4000);
}

/**
 * Resolve every mail setting and report configuration state explicitly.
 * Nothing is inferred silently: an operator can always see which env var is missing.
 */
function resolveMailConfig(env) {
  const source = env || process.env;
  const transport = readEnv(source, 'RFQ_MAIL_TRANSPORT').toLowerCase();

  const recipientList = splitList(readEnv(source, 'RFQ_MAIL_TO'));
  const invalidRecipients = recipientList.filter(address => !isValidAddress(address));
  const recipients = recipientList.filter(address => isValidAddress(address)).map(normalizeAddress);
  const recipientConfigured = recipients.length > 0 && invalidRecipients.length === 0;

  const fromAddress = normalizeAddress(readEnv(source, 'RFQ_MAIL_FROM'));
  const senderConfigured = isValidAddress(fromAddress);

  const config = {
    transport,
    recipients,
    recipientConfigured,
    recipientInvalid: invalidRecipients,
    fromAddress,
    senderConfigured,
    fromName: readEnv(source, 'RFQ_MAIL_FROM_NAME') || DEFAULT_FROM_NAME,
    replyToCustomer: readEnv(source, 'RFQ_MAIL_REPLY_TO_CUSTOMER') !== '0',
    requestTimeoutMs: Number(readEnv(source, 'RFQ_MAIL_TIMEOUT_MS') || 15000),
    transportConfigured: false,
    transportDetail: '',
    missing: [],
    invalid: [],
    notes: []
  };

  const need = key => {
    const value = readEnv(source, key);
    if (!value) config.missing.push(key);
    return value;
  };

  if (transport === 'graph') {
    const refreshToken = readEnv(source, 'MS_GRAPH_REFRESH_TOKEN');
    config.clientId = need('MS_GRAPH_CLIENT_ID');
    if (refreshToken) {
      config.authMode = 'refresh_token';
      config.refreshToken = refreshToken;
      config.clientSecret = readEnv(source, 'MS_GRAPH_CLIENT_SECRET');
      config.tenantId = readEnv(source, 'MS_GRAPH_TENANT_ID') || 'common';
      config.notes.push(
        'delegated refresh-token mode: required for personal Microsoft accounts, which cannot use application permissions'
      );
    } else {
      config.authMode = 'client_credentials';
      config.clientSecret = need('MS_GRAPH_CLIENT_SECRET');
      config.tenantId = need('MS_GRAPH_TENANT_ID');
      config.notes.push('application mode: requires a Microsoft 365 work/school tenant mailbox');
    }
    config.transportConfigured = config.missing.length === 0;
    config.transportDetail = `graph/${config.authMode}`;
  } else if (transport === 'smtp') {
    config.host = need('RFQ_SMTP_HOST');
    config.port = Number(readEnv(source, 'RFQ_SMTP_PORT') || 0) || undefined;
    config.secure = readEnv(source, 'RFQ_SMTP_SECURE') !== '0';
    config.starttls = readEnv(source, 'RFQ_SMTP_STARTTLS') !== '0';
    config.allowCleartext = readEnv(source, 'RFQ_SMTP_ALLOW_PLAINTEXT') === '1';
    config.user = need('RFQ_SMTP_USER');
    config.pass = need('RFQ_SMTP_PASS');
    config.heloHost = readEnv(source, 'RFQ_SMTP_HELO') || 'exoticalloycn.com';
    config.transportConfigured = config.missing.length === 0;
    config.transportDetail = `smtp/${config.secure ? '465-tls' : '587-starttls'}`;
  } else if (transport === 'resend') {
    config.apiKey = need('RESEND_API_KEY');
    const domain = config.senderConfigured ? fromAddress.split('@')[1] || '' : '';
    if (config.senderConfigured && CONSUMER_MAIL_DOMAINS.some(consumer => domain === consumer)) {
      if (readEnv(source, 'RFQ_RESEND_ALLOW_UNVERIFIED_DOMAIN') === '1') {
        config.notes.push(`RFQ_MAIL_FROM=${fromAddress} is a consumer mailbox domain and cannot be a verified Resend sender`);
      } else {
        // Resend can only send from a domain you control and have verified. Catching this at
        // configuration time beats discovering it as a 422 on the buyer's submission.
        config.invalid.push('RFQ_MAIL_FROM');
        config.notes.push(
          `RFQ_MAIL_FROM=${fromAddress} is a consumer mailbox domain; Resend requires a verified sending`
          + ' domain such as rfq@exoticalloycn.com (set RFQ_RESEND_ALLOW_UNVERIFIED_DOMAIN=1 to override)'
        );
      }
    }
    config.transportConfigured = config.missing.length === 0 && config.invalid.length === 0 && config.senderConfigured;
    config.transportDetail = 'resend/http-api';
  } else if (transport === 'log') {
    config.logTarget = readEnv(source, 'RFQ_MAIL_LOG_TARGET') || 'stdout';
    config.transportConfigured = true;
    config.transportDetail = 'log';
    config.notes.push('log transport writes the message locally and delivers nothing');
  } else if (transport) {
    config.missing.push('RFQ_MAIL_TRANSPORT');
    config.transportDetail = `unknown:${transport}`;
  } else {
    config.missing.push('RFQ_MAIL_TRANSPORT');
    config.transportDetail = 'unconfigured';
  }

  const environment = readEnv(source, 'TONGJUN_DEPLOYMENT_ENVIRONMENT') || readEnv(source, 'NODE_ENV') || 'local';
  config.environment = environment;
  // A log transport must never let production report healthy: that is exactly the
  // "buyer thinks it was submitted, nobody received it" failure mode.
  config.deliveryModeSafe = !(transport === 'log' && /^prod/i.test(environment));
  config.ready =
    config.recipientConfigured && config.senderConfigured && config.transportConfigured && config.deliveryModeSafe;

  return config;
}

function transportEnvName(transport) {
  return TRANSPORT_ENV_NAMES[transport] || '';
}

// ------------------------------------------------------------------- composition

const EMAIL_SECTIONS = [
  {
    title: 'Buyer contact',
    rows: [
      ['RFQ number', 'request_id'],
      ['Submitted (UTC)', 'received_at'],
      ['Name', 'name'],
      ['Company', 'company'],
      ['Country / Region', 'country'],
      ['Business email', 'email']
    ]
  },
  {
    title: 'Material definition',
    rows: [
      ['Material / Grade', 'grade'],
      ['Standard', 'standard'],
      ['Product form', 'form'],
      ['Size', 'size'],
      ['Condition / heat treatment', 'condition'],
      ['Quantity', 'qty']
    ]
  },
  {
    title: 'Application and acceptance',
    rows: [
      ['Application', 'application'],
      ['Certificate', 'certificate'],
      ['Certificate responsibility', 'certificate_responsibility'],
      ['Inspection responsibility', 'inspection_responsibility'],
      ['Origin / designated mill', 'origin'],
      ['Approval boundary', 'approval'],
      ['Deviation status', 'deviation_status'],
      ['Deviation register', 'deviation_register'],
      ['Alternate route permission', 'alternate_route_permission']
    ]
  },
  {
    title: 'Commercial and delivery',
    rows: [
      ['Incoterm', 'incoterm'],
      ['Destination', 'destination'],
      ['Delivery target', 'delivery_target'],
      ['Packing', 'packing'],
      ['Procurement stage', 'procurement_stage'],
      ['Buyer gate', 'buyer_gate'],
      ['Quote assumptions', 'quote_assumptions']
    ]
  },
  {
    title: 'Review state',
    rows: [
      ['Release status', 'release_status'],
      ['Release checklist', 'release_checklist'],
      ['Technical review plan', 'technical_review_plan']
    ]
  },
  {
    title: 'Attribution',
    rows: [
      ['Source page', 'source'],
      ['Product context', 'product'],
      ['First landing', 'first_landing'],
      ['First referrer', 'first_referrer'],
      ['First seen', 'first_seen'],
      ['UTM source', 'utm_source'],
      ['UTM medium', 'utm_medium'],
      ['UTM campaign', 'utm_campaign'],
      ['UTM content', 'utm_content'],
      ['Route reference', 'route_ref'],
      ['Decision reference', 'decision_ref'],
      ['Offer reference', 'offer_ref']
    ]
  },
  {
    title: 'Customer note',
    rows: [
      ['Notes', 'notes']
    ]
  }
];

// Every field the API accepts must be reachable in the email; anything not placed in a
// named section above is still emitted so no buyer input is silently dropped.
function attributedKeys() {
  const used = new Set();
  for (const section of EMAIL_SECTIONS) for (const row of section.rows) used.add(row[1]);
  return used;
}

function unreservedRows(record) {
  const used = attributedKeys();
  const skip = new Set(['website', 'subject', 'structured_body', 'evidence_package']);
  return Object.keys(record)
    .filter(key => !used.has(key) && !skip.has(key))
    .sort()
    .map(key => [key, key]);
}

function subjectForm(form) {
  const raw = headerField(form, 60);
  if (!raw) return '';
  return raw.split('/')[0].replace(/\s+/g, ' ').trim();
}

/**
 * Subject line, e.g. "[Tongjun RFQ] Inconel 625 · Sheet · Germany · Müller GmbH".
 * Every component is customer-supplied, so all of it passes through headerField().
 */
function buildRfqSubject(record) {
  const parts = [
    headerField(record.grade, 60) || 'Unspecified grade',
    subjectForm(record.form),
    headerField(record.country, 40),
    headerField(record.company, 70)
  ].filter(Boolean);
  return headerField(`[Tongjun RFQ] ${parts.join(' \u00b7 ')}`, 240);
}

function renderText(record, meta) {
  const lines = [];
  lines.push('TONGJUN METAL TECHNOLOGY (WUXI) CO., LTD.');
  lines.push('New request for quotation');
  lines.push('='.repeat(64));
  lines.push('');

  const sections = EMAIL_SECTIONS.slice();
  const extras = unreservedRows(record);
  if (extras.length) sections.push({ title: 'Additional submitted fields', rows: extras });

  for (const section of sections) {
    const rendered = [];
    for (const [label, key] of section.rows) {
      const value = bodyField(record[key]);
      if (!value) continue;
      rendered.push([label, value]);
    }
    if (!rendered.length) continue;
    const width = rendered.reduce((max, row) => Math.max(max, row[0].length), 0);
    lines.push(`[ ${section.title} ]`);
    for (const [label, value] of rendered) {
      const [first, ...rest] = value.split('\n');
      lines.push(`${label.padEnd(width)} : ${first}`);
      for (const continuation of rest) lines.push(`${' '.repeat(width)}   ${continuation}`);
    }
    lines.push('');
  }

  if (bodyField(record.subject)) {
    lines.push('--- Client-generated subject ---');
    lines.push(bodyField(record.subject));
    lines.push('');
  }
  if (bodyField(record.structured_body)) {
    lines.push('--- Client-generated structured body ---');
    lines.push(bodyField(record.structured_body));
    lines.push('');
  }
  if (bodyField(record.evidence_package)) {
    lines.push('--- Client-generated evidence package ---');
    lines.push(bodyField(record.evidence_package));
    lines.push('');
  }

  lines.push('-'.repeat(64));
  if (meta.replyTo) {
    lines.push(`Reply to this message to answer ${bodyField(record.name) || 'the buyer'} directly.`);
    lines.push(`Reply-To is already set to ${meta.replyTo}.`);
  } else {
    lines.push('Reply-To was suppressed because the submitted address failed validation.');
  }
  lines.push(`Delivered by ${meta.transportDetail} at ${meta.deliveredAt}.`);
  return lines.join('\n');
}

function renderHtml(record, meta) {
  const rowsToHtml = rows => rows
    .map(([label, key]) => {
      const value = bodyField(record[key]);
      if (!value) return '';
      return `<tr><th align="left" style="padding:6px 12px 6px 0;vertical-align:top;font-weight:600;white-space:nowrap;border-bottom:1px solid #eceff3">${escapeHtml(label)}</th>`
        + `<td style="padding:6px 0;vertical-align:top;border-bottom:1px solid #eceff3">${escapeHtml(value).replace(/\n/g, '<br>')}</td></tr>`;
    })
    .filter(Boolean)
    .join('');

  const sections = EMAIL_SECTIONS.slice();
  const extras = unreservedRows(record);
  if (extras.length) sections.push({ title: 'Additional submitted fields', rows: extras });

  const blocks = sections
    .map(section => {
      const body = rowsToHtml(section.rows);
      if (!body) return '';
      return `<h2 style="margin:22px 0 8px;font:600 13px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#8a94a6">${escapeHtml(section.title)}</h2>`
        + `<table cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:#1b2330">${body}</table>`;
    })
    .join('');

  const preBlocks = [
    ['Client-generated subject', record.subject],
    ['Client-generated structured body', record.structured_body],
    ['Client-generated evidence package', record.evidence_package]
  ]
    .filter(([, value]) => bodyField(value))
    .map(([label, value]) =>
      `<h2 style="margin:22px 0 8px;font:600 13px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#8a94a6">${escapeHtml(label)}</h2>`
      + `<pre style="margin:0;padding:12px;background:#f6f8fa;border:1px solid #e3e8ef;border-radius:6px;white-space:pre-wrap;font:12px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;color:#1b2330">${escapeHtml(bodyField(value))}</pre>`
    )
    .join('');

  const replyNote = meta.replyTo
    ? `Replying to this message answers ${escapeHtml(bodyField(record.name) || 'the buyer')} directly — Reply-To is already set to <strong>${escapeHtml(meta.replyTo)}</strong>.`
    : 'Reply-To was suppressed because the submitted address failed validation.';

  return `<!doctype html><html><body style="margin:0;background:#f2f4f7;padding:24px">`
    + `<div style="max-width:720px;margin:0 auto;background:#ffffff;border:1px solid #e3e8ef;border-radius:10px;padding:26px 28px">`
    + `<div style="font:600 11px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:#8a94a6">Tongjun Metal Technology (Wuxi) Co., Ltd.</div>`
    + `<h1 style="margin:6px 0 4px;font:700 22px/1.3 -apple-system,Segoe UI,Roboto,sans-serif;color:#101828">New request for quotation</h1>`
    + `<div style="font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:#475467">${escapeHtml(bodyField(record.request_id))} · received ${escapeHtml(bodyField(record.received_at))}</div>`
    + blocks
    + preBlocks
    + `<p style="margin:24px 0 0;padding-top:14px;border-top:1px solid #e3e8ef;font:13px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#475467">${replyNote}</p>`
    + `<p style="margin:8px 0 0;font:12px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#98a2b3">Delivered by ${escapeHtml(meta.transportDetail)} at ${escapeHtml(meta.deliveredAt)}.</p>`
    + `</div></body></html>`;
}

/**
 * Build the outbound message. Reply-To is the buyer's validated address so that hitting
 * "Reply" in Outlook answers the customer rather than the website server.
 */
function buildRfqEmail(record, config, now) {
  const deliveredAt = (now ? new Date(now) : new Date()).toISOString();
  const replyTo = config.replyToCustomer && isValidAddress(record.email) ? normalizeAddress(record.email) : '';
  const meta = {
    replyTo,
    transportDetail: config.transportDetail || config.transport || 'unconfigured',
    deliveredAt
  };
  return {
    requestId: headerField(record.request_id, 80),
    to: config.recipients.slice(),
    fromAddress: config.fromAddress,
    fromName: config.fromName,
    replyTo,
    subject: buildRfqSubject(record),
    text: renderText(record, meta),
    html: renderHtml(record, meta)
  };
}

async function sendRfqEmail(message, config, options) {
  if (!config || !config.ready) {
    const missing = (config && config.missing) || [];
    throw new MailTransportError('mail_not_configured', missing.join(',') || 'mail configuration incomplete');
  }
  return deliver(message, config, options);
}

module.exports = {
  DEFAULT_FROM_NAME,
  EMAIL_SECTIONS,
  buildRfqEmail,
  buildRfqSubject,
  escapeHtml,
  renderHtml,
  renderText,
  resolveMailConfig,
  sendRfqEmail,
  splitList,
  transportEnvName,
  unreservedRows
};
