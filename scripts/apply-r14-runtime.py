from pathlib import Path
import re

JS = Path('assets/site.js')
VERSION = '20260916-r14-2'
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

old_error = """        if(!r.ok) throw new Error(result.error||'rfq_route_unavailable');
"""
new_error = """        if(!r.ok){
          const routeError=new Error(result.error||'rfq_route_unavailable');
          routeError.requestId=safe(result.request_id,80);
          throw routeError;
        }
"""
if old_error not in s and 'routeError.requestId=safe(result.request_id,80)' not in s:
    raise SystemExit('ERROR: RFQ non-2xx handling block not found in site.js')
if 'routeError.requestId=safe(result.request_id,80)' not in s:
    s = s.replace(old_error, new_error, 1)

old_fallback = """        showToast('Secure routing is not active yet. Opening email fallback.');
        setTimeout(()=>{location.href=`mailto:ask2205@outlook.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;},350);
"""
old_fallback_r141 = """        setStore('tj_last_rfq','email_fallback');
        showToast('Secure routing unavailable. Opening email fallback; use Copy Structured RFQ if no mail app opens.');
        setTimeout(()=>{location.href=`mailto:ask2205@outlook.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;},350);
"""
new_fallback = """        const fallbackRef=safe(err&&err.requestId,80);
        if(fallbackRef) setStore('tj_rfq_id',fallbackRef);
        const fallbackBody=fallbackRef?`${body}\n\nSecure Route Attempt: ${fallbackRef}`:body;
        setStore('tj_last_rfq','email_fallback');
        showToast(fallbackRef?`Secure routing failed · ${fallbackRef}. Opening email fallback; use Copy Structured RFQ if no mail app opens.`:'Secure routing unavailable. Opening email fallback; use Copy Structured RFQ if no mail app opens.');
        setTimeout(()=>{location.href=`mailto:ask2205@outlook.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(fallbackBody)}`;},350);
"""
if 'Secure Route Attempt:' not in s:
    if old_fallback_r141 in s:
        s = s.replace(old_fallback_r141, new_fallback, 1)
    elif old_fallback in s:
        s = s.replace(old_fallback, new_fallback, 1)
    else:
        raise SystemExit('ERROR: RFQ email fallback block not found in site.js')

required = (
    'Product Context:',
    'First Seen:',
    'routeError.requestId=safe(result.request_id,80)',
    'Secure Route Attempt:',
    "setStore('tj_last_rfq','email_fallback')",
    'use Copy Structured RFQ if no mail app opens.',
)
for marker in required:
    if marker not in s:
        raise SystemExit(f'ERROR: R14.2 runtime marker missing after patch: {marker}')

if s != old:
    JS.write_text(s, encoding='utf-8')

# Critical form runtime must not depend on stale asset caching after deployment.
html_changed = 0
site_ref = f'/assets/site.js?v={VERSION}'
for p in Path('.').glob('*.html'):
    text = p.read_text(encoding='utf-8')
    updated = re.sub(r'/assets/site\.js(?:\?v=[^"\']+)?', site_ref, text)
    if updated != text:
        p.write_text(updated, encoding='utf-8')
        html_changed += 1

rfq = Path('rfq.html').read_text(encoding='utf-8')
if site_ref not in rfq:
    raise SystemExit('ERROR: R14.2 versioned site.js reference missing from RFQ page')

print(f'PASS: R14.2 RFQ runtime trace fallback patched; site.js cache-busted on {html_changed} HTML files.')
