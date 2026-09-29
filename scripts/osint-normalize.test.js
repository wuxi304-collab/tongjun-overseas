"use strict";

const assert = require("assert");
const { normalize, normalizeDomain, acceptedBusinessEmail } = require("./osint-normalize");

assert.equal(normalizeDomain("https://www.Example.com/a"), "example.com");
assert.equal(acceptedBusinessEmail("buyer@example.com", "example.com", false), true);
assert.equal(acceptedBusinessEmail("person@gmail.com", "example.com", false), false);

const base = normalize({
  run_date: "2026-09-29",
  account: { id: "x01", name: "Example", domain: "example.com" },
  official: {
    emails: ["sales@example.com"],
    contacts: [{ name: "Alex Buyer", title: "Purchasing Manager", email: "alex@example.com", source: "https://example.com/team" }]
  },
  theHarvester: { emails: ["hidden@example.com"] },
  maigret: { profiles: ["x"] }
});

assert.equal(base.confidence, "high");
assert.equal(base.business_emails.some(x => x.email === "hidden@example.com"), false);
assert.equal(base.policy_flags.length, 2);
assert.equal(base.writeback["联系人邮箱"], "alex@example.com");

const authorized = normalize({
  account: { name: "Example", domain: "example.com" },
  authorized_security_scope: true,
  official: { emails: [] },
  theHarvester: { emails: ["public@example.com", "other@unrelated.test", "bad@gmail.com"] }
});

assert.equal(authorized.business_emails.some(x => x.email === "public@example.com"), true);
assert.equal(authorized.business_emails.some(x => x.email === "other@unrelated.test"), false);
assert.equal(authorized.business_emails.some(x => x.email === "bad@gmail.com"), false);

console.log("osint-normalize: PASS");
