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

## Troubleshooting

### `PUBLIC_API_BILLING_LIMIT_EXCEEDED` (HTTP 429)

The Worker is working, but **Airtable** is refusing new writes because the workspace hit its **monthly API limit** (common on free or low tiers). Upgrade the Airtable plan, wait for the billing period to reset, or reduce API usage elsewhere. Check usage under **Airtable workspace settings**.

The listing page **POSTs a backup copy to FormSubmit** (`https://formsubmit.co/ajax/…` using `site.booking_backup_email`, or `lead_email` if unset) when the Worker/Airtable save fails. The backup email contains the same **visitor-facing inquiry** as a successful save (no API error payloads or raw responses). The UI only shows “Your message was sent…” after FormSubmit returns a successful JSON response; if that backup fails too, the visitor is asked to use **Get in Touch**.

### `Server misconfigured`

The Worker is missing **`AIRTABLE_TOKEN`**. From the `workers/` directory run `npx wrangler secret put AIRTABLE_TOKEN`, then `npx wrangler deploy`.

### Permissions or field errors

Confirm the PAT has **`data.records:write`** on this base, and that table **451 Apt Showing Times** field names match what [`booking-proxy.js`](booking-proxy.js) sends: `Name`, `Email`, `Phone`, `Showing Date`, `Showing Time`, `Move-In Date Preference`, `Status`. The listing site collects a **preferred day** only; **`Showing Time`** is set to a placeholder (`Coordinate time with listing agent`) until the prospect schedules a slot with the listing agent. **`Email` and `Phone` are both required** on the public form.
