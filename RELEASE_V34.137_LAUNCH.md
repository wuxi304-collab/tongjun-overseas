# V34.137 Launch Candidate — Two-Agent Desk

This launch patch extends the verified V34.137 source with two controlled AI workflows:

- Quote Agent on `/rfq`: raw inquiry → structured quote basis, open gates, RFQ field application. It never invents price, stock, lead time, mill approval or certification.
- Material Selection Agent on `/material-compare`: service condition → candidate material routes, open questions and qualification boundary. It never authorizes a substitution.
- MiniMax is server-side only. Configure `MINIMAX_API_KEY`, optional `MINIMAX_MODEL`, and optional `MINIMAX_API_URL` in Vercel. No key is shipped to the browser.
- Both agents retain a deterministic rules fallback so the site remains functional before the MiniMax key is configured.
- Existing RFQ, material compare and qualification workflows remain usable without AI.
- Optional live pricing adapter: `QUOTE_PRICE_FEED_URL` (+ optional token). Without it, the Quote Agent explicitly holds price for commercial confirmation instead of fabricating a number.

Launch gate: `npm run check` must pass before promotion.
