'use strict';

// Lightweight RFQ delivery ledger: one JSON object per line, append only.
//
// Why this exists: mail can be delayed, land in junk, or fail after the buyer already saw a
// confirmation. Without a local delivery trail a submission can vanish with nobody aware.
//
// What it deliberately does NOT store: the inquiry body. No application text, no notes, no
// size/quantity/price context. Only routing metadata needed to prove a submission happened
// and to reconcile it against the mailbox.

const fs = require('fs');
const path = require('path');

const DEFAULT_LEDGER_PATH = '/var/lib/tongjun-rfq/rfq-ledger.jsonl';
const MAX_FIELD_CHARS = 160;

// Whitelist, not blacklist: a new customer field can never leak in by accident.
const LEDGER_FIELDS = [
  'request_id',
  'received_at',
  'delivered_at',
  'status',
  'transport',
  'message_id',
  'company',
  'email',
  'country',
  'grade',
  'form',
  'error'
];

const STATUSES = new Set(['delivered', 'failed', 'rejected_config', 'rejected_validation']);

function ledgerPath(env) {
  const configured = String(((env || process.env).RFQ_LEDGER_PATH) || '').trim();
  return configured || DEFAULT_LEDGER_PATH;
}

function ledgerEnabled(env) {
  const source = env || process.env;
  if (String(source.RFQ_LEDGER_DISABLED || '').trim() === '1') return false;
  return true;
}

function compact(value) {
  return String(value == null ? '' : value)
    .replace(/[\u0000-\u001f\u007f]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, MAX_FIELD_CHARS);
}

/**
 * Build a ledger entry from an RFQ record. Only whitelisted fields survive, so the inquiry
 * body is structurally incapable of reaching disk.
 */
function buildEntry(input) {
  const source = input || {};
  const record = source.record || {};
  const raw = {
    request_id: compact(source.requestId || record.request_id),
    received_at: compact(record.received_at) || new Date().toISOString(),
    delivered_at: source.deliveredAt ? compact(source.deliveredAt) : '',
    status: STATUSES.has(source.status) ? source.status : 'failed',
    transport: compact(source.transport),
    message_id: compact(source.messageId),
    company: compact(record.company),
    email: compact(record.email),
    country: compact(record.country),
    grade: compact(record.grade),
    form: compact(record.form),
    error: compact(source.error)
  };
  const entry = {};
  for (const key of LEDGER_FIELDS) entry[key] = raw[key];
  return entry;
}

/**
 * Append one entry. Never throws: losing a log line must not break the buyer's submission,
 * but the failure is reported to the caller and logged so it is visible in journalctl.
 */
function appendLedger(input, options) {
  const opts = options || {};
  const env = opts.env || process.env;
  const entry = buildEntry(input);

  if (ledgerEnabled(env) === false) {
    return { written: false, skipped: 'disabled', path: ledgerPath(env), entry };
  }

  const target = opts.path || ledgerPath(env);
  try {
    fs.mkdirSync(path.dirname(target), { recursive: true, mode: 0o750 });
    fs.appendFileSync(target, `${JSON.stringify(entry)}\n`, { encoding: 'utf8', mode: 0o640 });
    return { written: true, path: target, entry };
  } catch (err) {
    const message = (err && err.message) || 'unknown ledger error';
    console.error('RFQ_LEDGER_WRITE_FAILED', target, message);
    return { written: false, error: message, path: target, entry };
  }
}

module.exports = {
  DEFAULT_LEDGER_PATH,
  LEDGER_FIELDS,
  STATUSES,
  appendLedger,
  buildEntry,
  ledgerEnabled,
  ledgerPath
};
