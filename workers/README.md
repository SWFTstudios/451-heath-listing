# Booking proxy (Cloudflare Worker)

The listing site posts showing requests to this Worker. The Worker forwards them to the **451 Apt Showing Times** table in Airtable (`Rental Lead Manager` base) using your PAT — the token stays off GitHub Pages.

## Deploy

```bash
cd workers
npm install -g wrangler   # or use npx wrangler
wrangler login
wrangler secret put AIRTABLE_TOKEN
# Paste your Airtable Personal Access Token (scopes: data.records:write on this base)

wrangler deploy
```

Copy the deployed Worker URL (e.g. `https://451-heath-booking-proxy.<your-subdomain>.workers.dev`).

## Connect the site

Set `booking_proxy_url` in [`listings/451-heath.json`](../listings/451-heath.json) to that Worker URL (HTTPS, no trailing slash required).

Rebuild:

```bash
python3 build.py --data listings/451-heath.json --assets images --style cream-modern --out .
```

## Env vars

| Variable | Source |
|----------|--------|
| `AIRTABLE_TOKEN` | Wrangler secret |
| `AIRTABLE_BASE_ID` | `wrangler.toml` `[vars]` (matches listing JSON) |
| `AIRTABLE_TABLE_ID` | `wrangler.toml` `[vars]` — table **451 Apt Showing Times** |
