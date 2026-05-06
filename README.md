# Listing Generator

This project generates a listing website and matching PDF from structured listing data and an image folder.

## Inputs

- Listing data JSON: `listings/<listing-id>.json`
- Listing images: `images/` (or another folder passed with `--assets`)
- Optional spreadsheet CSV: `listings/sample-listing.csv`

## Build

Validate only:

```bash
python build.py --data listings/451-heath.json --assets images --validate-only
```

Generate HTML + PDF:

```bash
python build.py --data listings/451-heath.json --assets images --style cream-modern --out .
```

Generate with second style:

```bash
python build.py --data listings/451-heath.json --assets images --style dark-luxury --out .
```

## Spreadsheet Import

Convert one CSV row to listing JSON:

```bash
python tools/import_listing_csv.py --csv listings/sample-listing.csv --out listings/from-csv.json
```

Then build from the generated JSON:

```bash
python build.py --data listings/from-csv.json --assets images --out .
```

## Realtor Intake Checklist

1. Provide one spreadsheet row with fields matching `listings/sample-listing.csv` headers.
2. Provide photos in the assets folder (`hero.jpg`, `photo1.jpg` ... `photo5.jpg`) or set explicit names in CSV/JSON.
3. Choose a style key (`cream-modern` or `dark-luxury`).
4. Confirm lead delivery email in `site.lead_email`.
5. Showing bookings: deploy the Cloudflare Worker in [`workers/`](workers/README.md), then set `site.booking_proxy_url` in your listing JSON to the Worker URL and rebuild.

## Troubleshooting

- **Validation error:** required field missing in JSON/CSV mapping.
- **Unknown style:** missing stylesheet in `styles/<style>.css`.
- **Missing assets:** one or more files in `assets.hero` or `assets.photos` does not exist.
- **Font mismatch in PDF:** add TTF files into `fonts/` for custom embedded font support (script falls back to base fonts when not present).

## Smoke Test

```bash
python tests/smoke_test.py
```
