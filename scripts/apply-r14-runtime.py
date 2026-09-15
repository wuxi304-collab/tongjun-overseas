from pathlib import Path

JS = Path('assets/site.js')
s = JS.read_text(encoding='utf-8')
old = s

source_block = """        `Landing Source: ${f.get('source')||''}`,
        `First Landing: ${f.get('first_landing')||''}`,
        `First Referrer: ${f.get('first_referrer')||''}`,
"""
replacement_block = """        `Landing Source: ${f.get('source')||''}`,
        `Product Context: ${f.get('product')||''}`,
        `First Landing: ${f.get('first_landing')||''}`,
        `First Referrer: ${f.get('first_referrer')||''}`,
        `First Seen: ${f.get('first_seen')||''}`,
"""
if source_block not in s and 'Product Context:' not in s:
    raise SystemExit('ERROR: RFQ fallback attribution block not found in site.js')
if 'Product Context:' not in s:
    s = s.replace(source_block, replacement_block, 1)

old_fallback = """        showToast('Secure routing is not active yet. Opening email fallback.');
        setTimeout(()=>{location.href=`mailto:ask2205@outlook.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;},350);
"""
new_fallback = """        setStore('tj_last_rfq','email_fallback');
        showToast('Secure routing unavailable. Opening email fallback; use Copy Structured RFQ if no mail app opens.');
        setTimeout(()=>{location.href=`mailto:ask2205@outlook.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;},350);
"""
if old_fallback not in s and "setStore('tj_last_rfq','email_fallback')" not in s:
    raise SystemExit('ERROR: RFQ email fallback block not found in site.js')
if "setStore('tj_last_rfq','email_fallback')" not in s:
    s = s.replace(old_fallback, new_fallback, 1)

required = (
    'Product Context:',
    'First Seen:',
    "setStore('tj_last_rfq','email_fallback')",
    'use Copy Structured RFQ if no mail app opens.',
)
for marker in required:
    if marker not in s:
        raise SystemExit(f'ERROR: R14.1 runtime marker missing after patch: {marker}')

if s != old:
    JS.write_text(s, encoding='utf-8')
    print('PASS: R14.1 RFQ runtime fallback patched with product context and explicit copy fallback.')
else:
    print('PASS: R14.1 RFQ runtime fallback already patched.')
