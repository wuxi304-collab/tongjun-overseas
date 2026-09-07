const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const root = path.resolve(__dirname, '..');
const manifestPath = path.join(root, 'SOURCE_MANIFEST_V27.gitsha1');
const manifestName = path.basename(manifestPath);

function gitBlobSha(buf) {
  const header = Buffer.from(`blob ${buf.length}\0`);
  return crypto.createHash('sha1').update(header).update(buf).digest('hex');
}

if (!fs.existsSync(manifestPath)) {
  console.error(`FAIL: missing ${manifestName}`);
  process.exit(1);
}

const lines = fs.readFileSync(manifestPath, 'utf8').split(/\r?\n/).filter(Boolean);
const failures = [];
for (const line of lines) {
  const m = line.match(/^([0-9a-f]{40})\t(.+)$/);
  if (!m) { failures.push(`malformed manifest line: ${line}`); continue; }
  const [, expected, rel] = m;
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) { failures.push(`missing: ${rel}`); continue; }
  const actual = gitBlobSha(fs.readFileSync(abs));
  if (actual !== expected) failures.push(`blob mismatch: ${rel}`);
}

if (failures.length) {
  console.error('FAIL: source manifest verification');
  for (const f of failures) console.error(`- ${f}`);
  process.exit(1);
}
console.log(`PASS: ${lines.length} source files match ${manifestName}`);
