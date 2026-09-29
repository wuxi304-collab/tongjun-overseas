#!/usr/bin/env node
"use strict";

const fs = require("fs");

const CONSUMER_DOMAINS = new Set([
  "gmail.com","googlemail.com","outlook.com","hotmail.com","live.com",
  "yahoo.com","icloud.com","qq.com","163.com","126.com","proton.me","protonmail.com"
]);

function uniq(items) {
  return [...new Set(items.filter(Boolean).map(v => String(v).trim()).filter(Boolean))];
}

function normalizeDomain(value="") {
  let s = String(value).trim().toLowerCase();
  if (!s) return "";
  try {
    if (!/^https?:\/\//.test(s)) s = "https://" + s;
    return new URL(s).hostname.replace(/^www\./, "");
  } catch {
    return s.replace(/^https?:\/\//, "").replace(/^www\./, "").split("/")[0];
  }
}

function emailDomain(email="") {
  const at = String(email).trim().toLowerCase().lastIndexOf("@");
  return at > 0 ? String(email).trim().toLowerCase().slice(at + 1) : "";
}

function isEmail(v) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v || "").trim());
}

function sameBusinessDomain(email, accountDomain) {
  const ed = emailDomain(email);
  const ad = normalizeDomain(accountDomain);
  return !!ed && !!ad && (ed === ad || ed.endsWith("." + ad));
}

function acceptedBusinessEmail(email, accountDomain, official=false) {
  if (!isEmail(email)) return false;
  const d = emailDomain(email);
  if (CONSUMER_DOMAINS.has(d) && !official) return false;
  if (official) return true;
  return sameBusinessDomain(email, accountDomain);
}

function pushEmail(out, seen, email, source, level, accountDomain, official=false) {
  const clean = String(email || "").trim().toLowerCase();
  if (!acceptedBusinessEmail(clean, accountDomain, official) || seen.has(clean)) return;
  seen.add(clean);
  out.push({ email: clean, source, evidence_level: level, official });
}

function normalize(input) {
  const account = input.account || {};
  const domain = normalizeDomain(account.domain || account.website || "");
  const policyFlags = [];
  const emails = [];
  const emailSeen = new Set();
  const urls = [];
  const contacts = [];

  const official = input.official || {};
  for (const e of official.emails || []) {
    pushEmail(emails, emailSeen, e, "official", "L1", domain, true);
  }
  for (const u of official.urls || []) urls.push({ url: String(u), source: "official", evidence_level: "L1" });
  for (const c of official.contacts || []) {
    if (!c || !c.name) continue;
    contacts.push({
      name: String(c.name).trim(),
      title: String(c.title || "").trim(),
      email: isEmail(c.email) ? String(c.email).trim().toLowerCase() : "",
      source: String(c.source || "official"),
      evidence_level: "L1"
    });
  }

  if (input.theHarvester) {
    if (input.authorized_security_scope !== true) {
      policyFlags.push("theHarvester output ignored: authorized_security_scope is not true");
    } else {
      for (const e of input.theHarvester.emails || []) {
        pushEmail(emails, emailSeen, e, "theHarvester", "L4", domain, false);
      }
      for (const u of input.theHarvester.urls || []) urls.push({ url: String(u), source: "theHarvester", evidence_level: "L4" });
    }
  }

  if (input.spiderFoot) {
    for (const ev of input.spiderFoot.events || []) {
      if (!ev) continue;
      const type = String(ev.type || ev.eventType || "").toUpperCase();
      const data = String(ev.data || ev.value || "").trim();
      if (type.includes("EMAIL")) {
        pushEmail(emails, emailSeen, data, "SpiderFoot-passive", "L4", domain, false);
      } else if (type.includes("URL") && /^https?:\/\//i.test(data)) {
        urls.push({ url: data, source: "SpiderFoot-passive", evidence_level: "L4" });
      }
    }
  }

  if (input.maigret) {
    if (input.allow_person_account_checks !== true) {
      policyFlags.push("Maigret output ignored: allow_person_account_checks is not true");
    } else {
      policyFlags.push("Maigret evidence retained for manual identity review only; not auto-written to contact fields");
    }
  }

  const officialChannels = emails
    .filter(x => x.official)
    .map(x => x.email);

  const strongestContact = contacts.find(c => c.evidence_level === "L1") || null;
  const strongestEmail = strongestContact && strongestContact.email
    ? strongestContact.email
    : (officialChannels[0] || "");

  const confidence = strongestContact && strongestEmail ? "high"
    : officialChannels.length ? "medium"
    : "low";

  const today = input.run_date || new Date().toISOString().slice(0,10);

  return {
    schema_version: "1.0.0",
    account: {
      id: account.id || "",
      name: account.name || "",
      country: account.country || "",
      domain
    },
    business_emails: emails,
    contacts,
    urls: uniq(urls.map(x => JSON.stringify(x))).map(x => JSON.parse(x)),
    confidence,
    policy_flags: policyFlags,
    writeback: {
      "公开联系渠道": officialChannels.join("；"),
      "实际联系人": strongestContact ? strongestContact.name : "",
      "实际职务": strongestContact ? strongestContact.title : "",
      "联系人来源/LinkedIn": strongestContact ? strongestContact.source : "",
      "联系人邮箱": strongestEmail,
      "情报完整度": confidence === "high"
        ? "L1：官网实名业务联系人/邮箱已确认"
        : confidence === "medium"
          ? "L1：官方联系渠道已确认；实名业务联系人待核验"
          : "公开商业联系渠道待核验",
      "最近核验": today
    }
  };
}

function main() {
  const path = process.argv[2];
  const raw = path ? fs.readFileSync(path, "utf8") : fs.readFileSync(0, "utf8");
  const input = JSON.parse(raw);
  process.stdout.write(JSON.stringify(normalize(input), null, 2) + "\n");
}

if (require.main === module) main();
module.exports = { normalize, normalizeDomain, acceptedBusinessEmail };
