# Listing Template Code Review

**Reviewer:** Senior engineer / code review analyst  
**Scope:** `index.html`, `make_pdf.py`  
**Goal:** Identify cleanup needed to templatize this into a repeatable listing-page generator powered by spreadsheet data + an image folder.

---

## Findings (Ordered by Severity)

### 1) No single source of truth for listing data (High)
- Property, pricing, offer text, description, features, agent data, and URLs are hardcoded repeatedly in both `index.html` and `make_pdf.py`.
- Same facts exist in multiple places (hero, stats, quick facts, footer, form autoresponses, PDF tables/cards), so one update can leave stale values elsewhere.
- This is the core blocker to scale: every listing requires manual string edits across many sections.

### 2) `make_pdf.py` is non-portable due to machine-specific paths (High)
- Uses absolute local paths for `IMG` and `OUT`.
- Uses macOS-only font locations (`/System/Library/Fonts/Supplemental`, `/Library/Fonts/...`).
- Any collaborator/CI/other machine will break without path changes.

### 3) PDF generator is script-style, not a reusable module (High)
- `make_pdf.py` executes top-to-bottom and cannot be called cleanly with different input data.
- No function signature like `generate_pdf(listing, assets_dir, out_path, theme)` and no CLI inputs.
- This prevents automation from spreadsheet rows.

### 4) Form and autoresponse content is tightly hardcoded (Medium)
- `FS_ENDPOINT` is fixed to one email.
- Subject lines and autoresponse templates include hardcoded address, pricing, offer, and agent details.
- This becomes a hidden third copy of listing data and is easy to forget during updates.

### 5) Theme/style data is coupled to implementation (Medium)
- Palette exists separately in CSS variables and Python RGB tuples.
- A one-off style change is fine, but multi-style support will drift unless theme tokens are centralized.

### 6) Asset naming conventions are inconsistent (Low)
- HTML hero uses `images/hero.jpg`, while PDF hero uses `images/photo1.jpg`.
- This creates ambiguity in the asset intake workflow.

### 7) Minor maintainability issues (Low)
- Inline JS style override (`btn.style.background = '#16a34a'`) bypasses theme tokens.
- Footer copy in PDF class is hardcoded directly in the method body.

---

## What To Clean Up For Templatization

### A) Introduce a Data Contract (Required)
Create one listing data file per property (JSON generated from spreadsheet):

- `listing.property`: address, city/state/zip, county, rent, beds, baths, sqft, offer, description, utilities, features, details, map query.
- `listing.agent`: name, title, brokerage, phones, profile URL.
- `listing.site`: lead email endpoint, listing URL slug, PDF filename.
- `listing.assets`: ordered photo list with filename + alt + label.
- `listing.theme`: style key and color token overrides (optional).

This becomes the only editable source for listing facts.

### B) Separate templates from data (Required)
- Convert current page to `templates/listing.html` with placeholders/loops.
- Move CSS to `styles/<theme>.css`.
- Inject a serialized listing object into the page for JS behavior (lightbox, forms, copy blocks).

### C) Refactor PDF into a callable generator (Required)
- Replace script flow with:
  - `generate_pdf(listing: dict, assets_dir: Path, out_path: Path, theme: dict) -> Path`
- Resolve all paths relative to project root.
- Load fonts from a repo `fonts/` directory.
- Build all display strings from listing data object.

### D) Add a build pipeline (Required)
Create a single entry command:

`python build.py --data listings/451-heath.json --style cream-modern`

Build should:
1. Validate required fields.
2. Validate image files exist.
3. Render `index.html` from template.
4. Generate `listing-info.pdf`.
5. Emit clear errors for missing data/assets.

### E) Standardize intake for realtor handoff (Required)
Define one operating contract:
- Spreadsheet columns map 1:1 to JSON keys.
- Assets folder uses fixed names (for example `photo1.jpg`…`photo5.jpg`) or explicit filenames from sheet.
- Optional per-listing style selection (`cream-modern`, `dark-luxury`, etc.).

### F) Add style-variant architecture (Recommended)
- Keep layout component structure stable.
- Swap look via style packs:
  - `styles/cream-modern.css`
  - `styles/dark-luxury.css`
  - `styles/minimal-editorial.css`
- Keep theme tokens (accent/ink/background/radius/shadow) data-driven so HTML and PDF match.

---

## Proposed Target Structure

```text
project/
  build.py
  listings/
    451-heath.json
  assets/
    451-heath/
      photo1.jpg
      photo2.jpg
      photo3.jpg
      photo4.jpg
      photo5.jpg
  templates/
    listing.html
  styles/
    cream-modern.css
    dark-luxury.css
  pdf/
    generator.py
  fonts/
    Arial.ttf
    Arial Bold.ttf
    Arial Italic.ttf
    Arial Bold Italic.ttf
```

---

## Priority Implementation Plan

### Phase 1 (Do now; unlocks reuse)
1. Refactor `make_pdf.py` into reusable function + relative paths.
2. Create first `listing.json` from current values.
3. Replace repeated JS hardcoded strings with reads from injected listing data.

### Phase 2 (Before second client listing)
4. Convert `index.html` to template with placeholders and loops.
5. Add `build.py` to generate both HTML + PDF from one data file.
6. Move font files into repo and remove system font dependency.

### Phase 3 (Productize for multiple styles)
7. Extract current CSS into first style pack.
8. Add second style pack and theme token mapping for both HTML and PDF.
9. Add `--validate` and simple QA checks (missing assets, bad URLs, missing required fields).

---

## Practical Result

After cleanup, your workflow becomes:
- Realtor sends spreadsheet row + photo folder.
- You map/import row to JSON.
- Run one build command with chosen style.
- Output listing page + PDF consistently, without touching template internals.

That is the point where this becomes a scalable listing template product instead of a one-off coded page.
