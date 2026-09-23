'use strict';

// RFQ mail transports. Deliberately dependency-free: the Lighthouse deployment runs
// `node server/tongjun-api.js` with no node_modules at all, so every transport here is
// built on Node core modules plus the global fetch that ships with Node 18+.
//
// Supported channels
//   graph   — Microsoft Graph. authMode=client_credentials (work/school mailbox) or
//             authMode=refresh_token (delegated, required for personal Microsoft accounts,
//             which cannot use application permissions at all).
//   smtp    — implicit TLS (465) or STARTTLS (587) written against net/tls directly.
//   resend  — Resend HTTP API (single API key, sending from a verified domain).
//
// Every transport returns { messageId } or throws MailTransportError. Nothing here ever
// swallows a failure: the caller turns a throw into HTTP 502 so a buyer is never told the
// inquiry was delivered when it was not.

const net = require('net');
const tls = require('tls');
const crypto = require('crypto');

const CONNECT_TIMEOUT_MS = 15000;
const SMTP_DIALOG_TIMEOUT_MS = 20000;

class MailTransportError extends Error {
  constructor(code, detail, status) {
    super(detail ? `${code}: ${detail}` : code);
    this.name = 'MailTransportError';
    this.code = String(code || 'mail_error');
    this.status = Number(status || 0);
    this.detail = detail ? String(detail).replace(/\s+/g, ' ').slice(0, 300) : '';
  }
}

function normalizeAddress(value) {
  return String(value == null ? '' : value).trim().toLowerCase();
}

function isValidAddress(value) {
  const raw = normalizeAddress(value);
  if (!raw || raw.length > 254) return false;
  if (/[\s,;<>"'\\]/.test(raw)) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(raw);
}

// A "keyword:" sequence inside a customer-supplied value is neutralised by dropping the
// colon. Without this a company name of "Acme Bcc: attacker@example.com" survives as literal
// text in the subject line, which trends towards relay mis-parsing and junk scores.
const HEADER_KEYWORD_PATTERN = /(^|[\s("'])(bcc|cc|to|from|sender|reply-to|subject|date|message-id|content-type|mime-version|return-path|received)\s*:/gi;

function neutralizeHeaderKeywords(value) {
  return String(value == null ? '' : value)
    .replace(HEADER_KEYWORD_PATTERN, (match, lead, keyword) => `${lead}${keyword} `);
}

// Any value that reaches a mail header must be free of CR/LF, otherwise a buyer-supplied
// company name could inject extra headers. Everything routed into headers goes through here.
function headerValue(value, max) {
  return neutralizeHeaderKeywords(
    String(value == null ? '' : value).replace(/[\u0000-\u001f\u007f]+/g, ' ')
  )
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, max || 240);
}

// RFC 2047 encodes non-ASCII so a subject such as "Müller GmbH" survives every relay.
function encodeHeaderText(value) {
  const raw = headerValue(value, 240);
  if (!raw) return '';
  if (/^[\x20-\x7e]*$/.test(raw)) return raw;
  return `=?UTF-8?B?${Buffer.from(raw, 'utf8').toString('base64')}?=`;
}

function encodeDisplayName(value) {
  const raw = headerValue(value, 120).replace(/["\\]/g, '');
  if (!raw) return '';
  if (/^[\x20-\x7e]*$/.test(raw)) return `"${raw}"`;
  return encodeHeaderText(raw);
}

function formatAddress(address, displayName) {
  const name = encodeDisplayName(displayName);
  return name ? `${name} <${address}>` : `<${address}>`;
}

function formatRfc5322Date(date) {
  return date.toUTCString().replace(/GMT$/, '+0000');
}

function isLoopbackHost(host) {
  const raw = normalizeAddress(host);
  return raw === '127.0.0.1' || raw === '::1' || raw === 'localhost' || raw === '[::1]';
}

function pickFetch(override) {
  if (typeof override === 'function') return override;
  if (typeof globalThis.fetch === 'function') return globalThis.fetch;
  throw new MailTransportError('fetch_unavailable', 'no global fetch in this Node runtime');
}

async function readJson(response) {
  try {
    return await response.json();
  } catch (err) {
    return null;
  }
}

function errorDetailFrom(payload, fallback) {
  if (!payload || typeof payload !== 'object') return fallback;
  const parts = [];
  for (const key of ['error', 'error_description', 'message', 'name']) {
    const value = payload[key];
    if (typeof value === 'string' && value.trim()) parts.push(value.trim());
  }
  return parts.length ? parts.join(' ') : fallback;
}

// ---------------------------------------------------------------- Microsoft Graph

function graphTokenEndpoint(config) {
  const tenant = headerValue(config.tenantId, 120) || 'common';
  return `https://login.microsoftonline.com/${encodeURIComponent(tenant)}/oauth2/v2.0/token`;
}

async function graphAccessToken(config, fetchImpl) {
  const body = new URLSearchParams();
  if (config.authMode === 'refresh_token') {
    body.set('grant_type', 'refresh_token');
    body.set('refresh_token', config.refreshToken);
    body.set('client_id', config.clientId);
    if (config.clientSecret) body.set('client_secret', config.clientSecret);
    body.set('scope', 'https://graph.microsoft.com/Mail.Send offline_access');
  } else {
    body.set('grant_type', 'client_credentials');
    body.set('client_id', config.clientId);
    body.set('client_secret', config.clientSecret);
    body.set('scope', 'https://graph.microsoft.com/.default');
  }

  let response;
  try {
    response = await fetchImpl(graphTokenEndpoint(config), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
      signal: AbortSignal.timeout(CONNECT_TIMEOUT_MS)
    });
  } catch (err) {
    throw new MailTransportError('graph_token_unreachable', (err && err.message) || 'network error');
  }

  const payload = await readJson(response);
  if (!response.ok || !payload || !payload.access_token) {
    throw new MailTransportError(
      'graph_token_rejected',
      errorDetailFrom(payload, `status_${response.status}`),
      response.status
    );
  }
  return payload.access_token;
}

async function graphFetch(url, token, options, fetchImpl) {
  let response;
  try {
    response = await fetchImpl(url, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...(options && options.headers ? options.headers : {})
      },
      signal: AbortSignal.timeout(CONNECT_TIMEOUT_MS)
    });
  } catch (err) {
    throw new MailTransportError('graph_unreachable', (err && err.message) || 'network error');
  }
  const payload = await readJson(response);
  if (!response.ok) {
    throw new MailTransportError(
      'graph_send_rejected',
      errorDetailFrom(payload, `status_${response.status}`),
      response.status
    );
  }
  return payload;
}

async function graphSend(message, config, fetchImpl) {
  const fetchFn = pickFetch(fetchImpl);
  const token = await graphAccessToken(config, fetchFn);
  const mailbox = normalizeAddress(config.fromAddress);

  // A delegated token represents the signed-in user, so /me is the only valid mailbox
  // target. Application tokens carry no user identity and must name the mailbox.
  const base = config.authMode === 'refresh_token'
    ? 'https://graph.microsoft.com/v1.0/me'
    : `https://graph.microsoft.com/v1.0/users/${encodeURIComponent(mailbox)}`;

  const internetMessageHeaders = [];
  if (message.requestId) internetMessageHeaders.push({ name: 'X-Tongjun-Request-Id', value: headerValue(message.requestId, 80) });
  internetMessageHeaders.push({ name: 'X-Tongjun-Transport', value: 'graph' });

  const draft = {
    subject: message.subject,
    body: { contentType: 'HTML', content: message.html },
    toRecipients: message.to.map(address => ({ emailAddress: { address } })),
    internetMessageHeaders
  };
  if (message.replyTo) draft.replyTo = [{ emailAddress: { address: message.replyTo } }];

  // Create-then-send rather than /sendMail, because Graph returns no body for sendMail and
  // the ledger needs a real message id to reconcile against the mailbox.
  const created = await graphFetch(`${base}/messages`, token, {
    method: 'POST',
    body: JSON.stringify(draft)
  }, fetchFn);

  const messageId = (created && created.id) || '';
  if (!messageId) throw new MailTransportError('graph_draft_without_id', 'Graph returned no message id');

  await graphFetch(`${base}/messages/${encodeURIComponent(messageId)}/send`, token, {
    method: 'POST',
    body: '{}'
  }, fetchFn);

  return { messageId, transport: 'graph' };
}

// ------------------------------------------------------------------------- Resend

async function resendSend(message, config, fetchImpl) {
  const fetchFn = pickFetch(fetchImpl);
  const body = {
    from: formatAddress(normalizeAddress(config.fromAddress), config.fromName),
    to: message.to.slice(),
    subject: message.subject,
    text: message.text,
    html: message.html
  };
  if (message.replyTo) body.reply_to = message.replyTo;
  if (message.requestId) body.headers = { 'X-Tongjun-Request-Id': headerValue(message.requestId, 80) };

  let response;
  try {
    response = await fetchFn('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(CONNECT_TIMEOUT_MS)
    });
  } catch (err) {
    throw new MailTransportError('resend_unreachable', (err && err.message) || 'network error');
  }

  const payload = await readJson(response);
  if (!response.ok || !payload || !payload.id) {
    throw new MailTransportError(
      'resend_send_rejected',
      errorDetailFrom(payload, `status_${response.status}`),
      response.status
    );
  }
  return { messageId: String(payload.id), transport: 'resend' };
}

// --------------------------------------------------------------------------- SMTP

class SmtpConnection {
  constructor(socket, timeoutMs) {
    this.socket = socket;
    this.buffer = '';
    this.pendingLines = [];
    this.waiters = [];
    this.failure = null;
    this.closed = false;

    socket.setEncoding('utf8');
    socket.on('data', chunk => {
      this.buffer += chunk;
      this.drain();
    });
    socket.on('error', err => this.fail(err));
    socket.on('close', () => {
      this.closed = true;
      this.drain();
    });
    if (timeoutMs) socket.setTimeout(timeoutMs, () => this.fail(new Error('smtp_timeout')));
  }

  fail(err) {
    if (!this.failure) this.failure = err instanceof Error ? err : new Error(String(err));
    this.drain();
  }

  drain() {
    let index = this.buffer.indexOf('\r\n');
    while (index >= 0) {
      const line = this.buffer.slice(0, index);
      this.buffer = this.buffer.slice(index + 2);
      const waiter = this.waiters.shift();
      if (waiter) waiter.resolve(line);
      else this.pendingLines.push(line);
      index = this.buffer.indexOf('\r\n');
    }
    if (this.failure) {
      while (this.waiters.length) this.waiters.shift().reject(this.failure);
    } else if (this.closed) {
      while (this.waiters.length) this.waiters.shift().reject(new Error('smtp_connection_closed'));
    }
  }

  readLine() {
    if (this.pendingLines.length) return Promise.resolve(this.pendingLines.shift());
    if (this.failure) return Promise.reject(this.failure);
    if (this.closed) return Promise.reject(new Error('smtp_connection_closed'));
    return new Promise((resolve, reject) => this.waiters.push({ resolve, reject }));
  }

  // SMTP multiline replies use "250-..." for continuation and "250 ..." for the last line.
  async readResponse() {
    const lines = [];
    for (;;) {
      const line = await this.readLine();
      lines.push(line);
      if (/^\d{3} /.test(line)) break;
      if (!/^\d{3}-/.test(line)) throw new MailTransportError('smtp_protocol_error', line);
    }
    const last = lines[lines.length - 1];
    return { code: Number(last.slice(0, 3)), lines, text: lines.join(' / ') };
  }

  write(payload) {
    return new Promise((resolve, reject) => {
      this.socket.write(payload, err => (err ? reject(err) : resolve()));
    });
  }

  async command(line, expectedCodes, redacted) {
    await this.write(`${line}\r\n`);
    const response = await this.readResponse();
    if (expectedCodes && !expectedCodes.includes(response.code)) {
      throw new MailTransportError('smtp_command_rejected', `${redacted || line} -> ${response.text}`);
    }
    return response;
  }

  close() {
    try {
      this.socket.destroy();
    } catch (err) {
      /* nothing useful to do */
    }
  }
}

function dotStuff(body) {
  return String(body)
    .replace(/\r\n|\r|\n/g, '\r\n')
    .split('\r\n')
    .map(line => (line.startsWith('.') ? `.${line}` : line))
    .join('\r\n');
}

function buildSmtpPayload(message, fromHeader) {
  const boundary = `tj-${crypto.randomBytes(12).toString('hex')}`;
  const messageDomain = (normalizeAddress(message.fromAddress).split('@')[1]) || 'exoticalloycn.com';
  const messageId = `<tj-${crypto.randomBytes(12).toString('hex')}@${messageDomain}>`;

  const headers = [
    `From: ${fromHeader}`,
    `To: ${message.to.join(', ')}`,
    `Subject: ${encodeHeaderText(message.subject)}`,
    `Date: ${formatRfc5322Date(new Date())}`,
    `Message-ID: ${messageId}`,
    'MIME-Version: 1.0'
  ];
  if (message.replyTo) headers.push(`Reply-To: ${message.replyTo}`);
  if (message.requestId) headers.push(`X-Tongjun-Request-Id: ${headerValue(message.requestId, 80)}`);
  headers.push('Auto-Submitted: auto-generated');
  headers.push(`Content-Type: multipart/alternative; boundary="${boundary}"`);

  const parts = [
    `--${boundary}`,
    'Content-Type: text/plain; charset=utf-8',
    'Content-Transfer-Encoding: base64',
    '',
    Buffer.from(message.text, 'utf8').toString('base64').replace(/(.{76})/g, '$1\r\n'),
    `--${boundary}`,
    'Content-Type: text/html; charset=utf-8',
    'Content-Transfer-Encoding: base64',
    '',
    Buffer.from(message.html, 'utf8').toString('base64').replace(/(.{76})/g, '$1\r\n'),
    `--${boundary}--`
  ];

  return { data: `${headers.join('\r\n')}\r\n\r\n${parts.join('\r\n')}\r\n`, messageId };
}

function smtpAuthMechanisms(ehloLines) {
  const mechanisms = [];
  for (const line of ehloLines) {
    const match = /AUTH\s+(.+)$/i.exec(line);
    if (match) mechanisms.push(...match[1].trim().split(/\s+/).map(value => value.toUpperCase()));
  }
  return mechanisms;
}

async function smtpSend(message, config) {
  const host = headerValue(config.host, 200);
  const port = Number(config.port || (config.secure ? 465 : 587));
  const secure = config.secure !== false;
  const starttls = !secure && config.starttls !== false;

  if (!host) throw new MailTransportError('smtp_host_missing', 'RFQ_SMTP_HOST is empty');
  if (!secure && !starttls && !(config.allowCleartext === true && isLoopbackHost(host))) {
    throw new MailTransportError(
      'smtp_insecure_refused',
      'plaintext SMTP is refused outside loopback; set RFQ_SMTP_SECURE=1 or leave STARTTLS enabled'
    );
  }
  if (!config.user || !config.pass) {
    throw new MailTransportError('smtp_credentials_missing', 'RFQ_SMTP_USER / RFQ_SMTP_PASS are required');
  }

  const fromAddress = normalizeAddress(config.fromAddress);
  const fromHeader = formatAddress(fromAddress, config.fromName);
  const { data, messageId } = buildSmtpPayload({ ...message, fromAddress }, fromHeader);

  let socket;
  let connection;
  try {
    socket = secure
      ? tls.connect({
          host,
          port,
          servername: host,
          rejectUnauthorized: config.rejectUnauthorized !== false
        })
      : net.connect({ host, port });

    await new Promise((resolve, reject) => {
      const onReady = () => {
        socket.removeListener('error', onError);
        resolve();
      };
      const onError = err => {
        socket.removeListener(secure ? 'secureConnect' : 'connect', onReady);
        reject(new MailTransportError('smtp_unreachable', (err && err.message) || 'connect failed'));
      };
      socket.once('error', onError);
      socket.once(secure ? 'secureConnect' : 'connect', onReady);
    });

    connection = new SmtpConnection(socket, SMTP_DIALOG_TIMEOUT_MS);
    await connection.readResponse(); // server greeting

    let ehlo = await connection.command(`EHLO ${headerValue(config.heloHost, 120) || 'exoticalloycn.com'}`, [250]);

    if (starttls) {
      if (!ehlo.lines.some(line => /STARTTLS/i.test(line))) {
        throw new MailTransportError('smtp_starttls_unsupported', ehlo.text);
      }
      await connection.command('STARTTLS', [220]);
      connection.close();
      socket = tls.connect({
        socket,
        host,
        servername: host,
        rejectUnauthorized: config.rejectUnauthorized !== false
      });
      await new Promise((resolve, reject) => {
        socket.once('secureConnect', resolve);
        socket.once('error', err => reject(new MailTransportError('smtp_starttls_failed', (err && err.message) || 'tls failed')));
      });
      connection = new SmtpConnection(socket, SMTP_DIALOG_TIMEOUT_MS);
      ehlo = await connection.command(`EHLO ${headerValue(config.heloHost, 120) || 'exoticalloycn.com'}`, [250]);
    }

    const mechanisms = smtpAuthMechanisms(ehlo.lines);
    if (mechanisms.includes('PLAIN')) {
      const token = Buffer.from(`\u0000${config.user}\u0000${config.pass}`, 'utf8').toString('base64');
      await connection.command(`AUTH PLAIN ${token}`, [235], 'AUTH PLAIN [redacted]');
    } else if (mechanisms.includes('LOGIN')) {
      await connection.command('AUTH LOGIN', [334]);
      await connection.command(Buffer.from(config.user, 'utf8').toString('base64'), [334], '[user]');
      await connection.command(Buffer.from(config.pass, 'utf8').toString('base64'), [235], '[password]');
    } else {
      throw new MailTransportError('smtp_auth_unsupported', `server advertises: ${mechanisms.join(',') || 'nothing'}`);
    }

    await connection.command(`MAIL FROM:<${fromAddress}>`, [250]);
    for (const recipient of message.to) {
      await connection.command(`RCPT TO:<${normalizeAddress(recipient)}>`, [250, 251]);
    }
    await connection.command('DATA', [354]);
    await connection.write(`${dotStuff(data)}\r\n.\r\n`);
    const accepted = await connection.readResponse();
    if (accepted.code !== 250) {
      throw new MailTransportError('smtp_message_rejected', accepted.text);
    }

    const queued = /queued as (\S+)/i.exec(accepted.text);
    await connection.command('QUIT', [221]).catch(() => {});
    return { messageId: queued ? queued[1] : messageId, transport: 'smtp' };
  } catch (err) {
    if (err instanceof MailTransportError) throw err;
    throw new MailTransportError('smtp_error', (err && err.message) || 'smtp failure');
  } finally {
    if (connection) connection.close();
    else if (socket) {
      try {
        socket.destroy();
      } catch (err) {
        /* nothing useful to do */
      }
    }
  }
}

// ---------------------------------------------------------------------------- log

// Never a silent no-op: the caller refuses to mark production ready while this is active.
async function logSend(message, config) {
  const target = String(config.logTarget || '').trim();
  const line = JSON.stringify({
    event: 'rfq_mail_log_transport',
    request_id: message.requestId || '',
    to: message.to,
    reply_to: message.replyTo || '',
    subject: message.subject,
    text_bytes: Buffer.byteLength(message.text, 'utf8')
  });
  if (target === 'stderr') console.error(line);
  else console.log(line);
  return { messageId: `log-${crypto.randomBytes(8).toString('hex')}`, transport: 'log' };
}

const TRANSPORTS = {
  graph: graphSend,
  smtp: smtpSend,
  resend: resendSend,
  log: logSend
};

async function deliver(message, config, options) {
  const send = TRANSPORTS[config.transport];
  if (!send) throw new MailTransportError('unknown_transport', String(config.transport || '(empty)'));
  const opts = options || {};
  return send(message, config, opts.fetch);
}

module.exports = {
  MailTransportError,
  TRANSPORTS,
  deliver,
  encodeHeaderText,
  formatAddress,
  formatRfc5322Date,
  headerValue,
  isLoopbackHost,
  isValidAddress,
  neutralizeHeaderKeywords,
  normalizeAddress,
  buildSmtpPayload,
  dotStuff,
  graphAccessToken,
  graphTokenEndpoint
};
