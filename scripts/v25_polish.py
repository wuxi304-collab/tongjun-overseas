from pathlib import Path
import re, json
root=Path(__file__).resolve().parents[1]

meta={
'index.html':('Special Metals Sourcing & Qualification | Tongjun','Engineering-led sourcing and qualification for nickel alloys, precision strip, Invar, heavy plate, titanium and other high-performance materials from China.'),
'about.html':('About Tongjun Special Metals | Sourcing & Qualification','Tongjun Special Metals is the international sourcing desk of Tongjun Metal Technology (Wuxi) Co., Ltd., focused on material qualification and supply routes.'),
'distribution-supply-desk.html':('Distribution Supply Desk | Tongjun Special Metals','Technical distribution and sourcing support for special metals, with source role, processing responsibility, traceability and buyer approval kept explicit.'),
'extra-wide-stainless-plate-china.html':('Extra-Wide Stainless Plate from China | Tongjun','Qualification-led sourcing for extra-wide stainless plate from China, including width capability, heat treatment, inspection, origin and delivery route.'),
'heavy-plate-pressure-equipment.html':('Heavy Plate for Pressure Equipment | Tongjun','Heavy and extra-wide plate sourcing for pressure equipment, screened by product standard, dimensions, heat treatment, NDT, approval and traceability.'),
'heavy-plate.html':('Heavy & Extra-Wide Plate Sourcing | Tongjun','Heavy and extra-wide special-metal plate sourcing from China, screened by width, thickness, heat treatment, flatness, NDT, cut condition and origin.'),
'invar-aerospace-tooling.html':('Invar 36 for Aerospace Tooling | Tongjun','Invar 36 sourcing for aerospace tooling and precision structures, with CTE acceptance, product form, heat treatment, dimensions and evidence route defined.'),
'invar-lng.html':('Invar 36 for LNG & Cryogenic Service | Tongjun','Invar 36 sourcing for LNG and cryogenic applications, with material identity, CTE acceptance, dimensional control, source route and project approval defined.'),
'nickel-alloys.html':('Nickel & Corrosion Alloys | Tongjun Special Metals','Nickel and corrosion-alloy sourcing from China, screened by service environment, product form, governing standard, condition, source route and buyer approval.'),
'nickel-process-equipment.html':('Nickel Alloys for Process Equipment | Tongjun','Nickel-alloy sourcing for chemical and process equipment, screened by corrosion environment, product form, standards, condition, inspection and approvals.'),
'precision-strip-bellows.html':('Precision Strip for Bellows & Components | Tongjun','Precision stainless and special-alloy strip for bellows and formed components, screened by thickness distribution, temper, edge, camber and coil consistency.'),
'precision-strip.html':('Precision Strip & Foil Sourcing | Tongjun','Precision strip and foil sourcing for stainless and special alloys, controlled by thickness distribution, temper, edge, flatness, camber, coil build and traceability.'),
'resource-invar-lng-vs-tooling.html':('Invar 36: LNG vs Aerospace Tooling | Tongjun','Buyer guide to how Invar 36 requirements differ between LNG containment and aerospace tooling, including CTE acceptance, form, dimensions and qualification.'),
'resource-precision-strip-buyers-guide.html':('Precision Strip Buyer Guide | Tongjun Special Metals','Buyer guide to precision strip sourcing: thickness distribution, temper, edge, camber, coil build, traceability and the evidence needed before release.'),
'resource-qualify-china-special-metals.html':('Qualifying Special-Metal Sources in China | Tongjun','A practical buyer framework for qualifying special-metal sources in China across capability, product form, source role, traceability, evidence and approval.'),
'technical-alloy-718.html':('Alloy 718 Technical Data | Tongjun','Controlled technical reference for Alloy 718 / UNS N07718 covering identity, product-form standards, reference properties, qualification gates and purchase focus.'),
'technical-invar-36.html':('Invar 36 Technical Data | Tongjun Special Metals','Controlled technical reference for 36Ni-Fe / Invar 36 covering identity, CTE acceptance, product forms, reference properties, qualification and purchase focus.'),
'titanium-heat-exchangers.html':('Titanium for Heat Exchangers | Tongjun Special Metals','Titanium sourcing for heat exchangers, screened by grade, product standard, tube or plate form, surface and processing boundary, inspection and traceability.'),
'titanium-zirconium.html':('Titanium & Zirconium Sourcing | Tongjun','Titanium and zirconium sourcing routes from China, controlled by grade, product standard, form, surface and processing boundary, inspection and traceability.'),
'privacy.html':('Privacy Notice | Tongjun Special Metals','Privacy notice for exoticalloycn.com covering RFQ and contact information, technical requirement data, service providers, retention, security and buyer choices.'),
'terms.html':('Terms of Use | Tongjun Special Metals','Terms governing use of exoticalloycn.com, including technical information, availability, third-party names, quotation boundaries and commercial contracts.'),
}

for fn,(title,desc) in meta.items():
    p=root/fn
    text=p.read_text('utf-8')
    text=re.sub(r'<title>.*?</title>',f'<title>{title}</title>',text,count=1,flags=re.S)
    text=re.sub(r'<meta content="[^"]*" name="description"\s*/>',f'<meta content="{desc}" name="description"/>',text,count=1)
    # keep OG title/description aligned for indexable pages where tags exist
    text=re.sub(r'<meta content="[^"]*" property="og:title"\s*/>',f'<meta content="{title}" property="og:title"/>',text,count=1)
    text=re.sub(r'<meta content="[^"]*" property="og:description"\s*/>',f'<meta content="{desc}" property="og:description"/>',text,count=1)
    p.write_text(text,'utf-8')

# Homepage: add WebSite schema and strengthen organization schema contact point.
p=root/'index.html'; text=p.read_text('utf-8')
org={"@context":"https://schema.org","@type":"Organization","name":"Tongjun Special Metals","legalName":"Tongjun Metal Technology (Wuxi) Co., Ltd.","url":"https://exoticalloycn.com","email":"ask2205@outlook.com","address":{"@type":"PostalAddress","addressLocality":"Wuxi","addressRegion":"Jiangsu","addressCountry":"CN"},"contactPoint":{"@type":"ContactPoint","contactType":"sales and technical enquiries","email":"ask2205@outlook.com","availableLanguage":["en","zh"]},"description":"High-performance materials sourcing, source qualification and non-standard supply-route development from China."}
website={"@context":"https://schema.org","@type":"WebSite","name":"Tongjun Special Metals","url":"https://exoticalloycn.com/","publisher":{"@type":"Organization","name":"Tongjun Special Metals","url":"https://exoticalloycn.com"},"inLanguage":"en"}
text=re.sub(r'<script data-site-schema="org" type="application/ld\+json">.*?</script>', '<script data-site-schema="org" type="application/ld+json">'+json.dumps(org,separators=(',',':'))+'</script><script data-site-schema="website" type="application/ld+json">'+json.dumps(website,separators=(',',':'))+'</script>', text, count=1, flags=re.S)
p.write_text(text,'utf-8')

# Privacy: replace core legal content with clearer launch-ready notice.
p=root/'privacy.html'; text=p.read_text('utf-8')
start=text.find('<main id="main-content">'); end=text.find('</main>',start)
if start!=-1 and end!=-1:
    new='''<main id="main-content"><section class="pagehero"><div class="wrap"><h1>Privacy Notice</h1><p>How information submitted through exoticalloycn.com is used when we review a technical or commercial requirement.</p></div></section><section class="section"><div class="wrap prose legal-prose"><h2>Information we receive</h2><p>When you contact Tongjun or submit a Technical RFQ, we may receive your name, company, business email, country or region, material requirement, application, project restrictions, delivery information and other details you choose to provide.</p><h2>How we use it</h2><p>We use this information to respond to enquiries, screen technical feasibility, qualify supply routes, prepare evidence and commercial assumptions, maintain request history, prevent abuse and improve the sourcing workflow.</p><h2>Service providers</h2><p>Website hosting, email delivery and approved workflow providers may process limited information on our behalf where needed to operate the site or deliver your request. We do not sell RFQ or contact information to advertisers or data brokers.</p><h2>Retention and security</h2><p>We retain enquiry and RFQ information only as long as reasonably needed for sourcing, commercial records, dispute prevention, legal obligations and continuity of buyer support. Reasonable technical and organizational safeguards are used, but no internet transmission is guaranteed to be risk-free.</p><h2>Your choices</h2><p>You may ask us to correct or delete contact or RFQ information that is not required for legal, contractual or legitimate business records. Contact <a href="mailto:ask2205@outlook.com">ask2205@outlook.com</a>.</p><h2>Scope</h2><p>This notice applies to exoticalloycn.com. Project contracts, purchase orders or separately agreed data requirements may impose additional terms.</p></div></section>'''
    text=text[:start]+new+text[end+7:]
p.write_text(text,'utf-8')

# Terms: strengthen commercial / liability boundary without pretending to be legal advice.
p=root/'terms.html'; text=p.read_text('utf-8')
start=text.find('<main id="main-content">'); end=text.find('</main>',start)
if start!=-1 and end!=-1:
    new='''<main id="main-content"><section class="pagehero"><div class="wrap"><h1>Terms of Use</h1><p>Terms governing use of exoticalloycn.com and its technical sourcing content.</p></div></section><section class="section"><div class="wrap prose legal-prose"><h2>Technical information</h2><p>Website content supports sourcing orientation and preliminary qualification. It does not replace the governing material specification, buyer specification, project code, purchase order, approved source list, certified material documentation or signed technical agreement.</p><h2>Availability and capability</h2><p>Listed materials, dimensions, source routes and capability examples do not constitute an offer or guarantee of supply. Current manufacturing capability, origin, certification, inspection scope, MOQ, lead time and dimensional feasibility are confirmed against each RFQ.</p><h2>Reference values</h2><p>Typical, nominal or reference values shown on the site are identified as such where applicable. Final acceptance is governed by the current purchase requirement and the controlling specification or project document.</p><h2>Third-party names</h2><p>References to standards, alloy trademarks, industries, mills, licensors or other third parties do not imply authorization, partnership, endorsement or approval unless explicitly documented.</p><h2>Commercial offers</h2><p>A quotation is valid only within its stated scope, validity period, technical assumptions, logistics basis and exclusions. An open technical, evidence or buyer-approval gate remains open unless the quotation or subsequent written agreement explicitly closes it.</p><h2>Contracts</h2><p>Commercial supply is governed by the applicable quotation, purchase order, contract terms, technical specification and any agreed deviations. Where those documents conflict with website content, the transaction documents control.</p><h2>Contact</h2><p>Questions about these terms may be sent to <a href="mailto:ask2205@outlook.com">ask2205@outlook.com</a>.</p></div></section>'''
    text=text[:start]+new+text[end+7:]
p.write_text(text,'utf-8')

# RFQ checkbox now covers privacy + technical acknowledgement.
p=root/'rfq.html'; text=p.read_text('utf-8')
text=text.replace('I understand that final supply capability and qualification must be confirmed against the full technical requirement.','I agree to the <a href="/privacy" target="_blank" rel="noopener">Privacy Notice</a> and understand that final supply capability and qualification must be confirmed against the full technical requirement.')
p.write_text(text,'utf-8')

# Add Privacy / Terms links to footer legal row across public HTML.
for p in root.glob('*.html'):
    text=p.read_text('utf-8')
    if '<div class="legal">' not in text: continue
    if 'href="/privacy"' in text[text.rfind('<div class="legal">'):]: continue
    text=text.replace('<span>Special Metals. Precisely Sourced. · exoticalloycn.com</span>','<span>Special Metals. Precisely Sourced. · exoticalloycn.com · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a></span>')
    p.write_text(text,'utf-8')
