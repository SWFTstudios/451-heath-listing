from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pdf.generator import generate_pdf
from tools.listing_utils import (
    ListingValidationError,
    load_listing,
    validate_assets_exist,
    validate_listing_payload,
)


ROOT = Path(__file__).parent


def _fmt_money(value: float | int) -> str:
    return f"{int(value):,}"


def _render_template(template: str, mapping: dict[str, str]) -> str:
    output = template
    for key, value in mapping.items():
        output = output.replace(f"__{key}__", value)
    return output


def _render_feature_items(features: list[dict[str, Any]]) -> str:
    return "".join(
        f'<article class="feature-card"><h3>{item["name"]}</h3><p>{item["description"]}</p></article>'
        for item in features
    )


def _render_detail_items(details: list[dict[str, Any]]) -> str:
    return "".join(
        f'<article class="detail-card"><p><strong>{item["key"]}</strong></p><p>{item["value"]}</p></article>'
        for item in details
    )


def _render_neighborhood_items(items: list[dict[str, Any]]) -> str:
    return "".join(
        f'<article class="location-card"><h3>{item["name"]}</h3><p>{item["description"]}</p></article>'
        for item in items
    )


def _render_photo_grid(photos: list[dict[str, Any]]) -> str:
    return "".join(
        f'<div class="photo-cell"><img src="images/{item["file"]}" alt="{item["alt"]}" /></div>'
        for item in photos
    )


def _render_list(values: list[str], class_name: str) -> str:
    return "".join(f'<span class="{class_name}">{v}</span>' for v in values)


def _build_html(listing: dict[str, Any], style_text: str) -> str:
    template_path = ROOT / "templates" / "listing.html"
    template = template_path.read_text(encoding="utf-8")

    prop = listing["property"]
    site = listing["site"]
    photos = listing["assets"]["photos"]

    sidebar_facts = [
        f"<p><strong>Bedrooms:</strong> {prop['bedrooms']} Bed</p>",
        f"<p><strong>Bathrooms:</strong> {prop['bathrooms']} Bath</p>",
        f"<p><strong>Size:</strong> {prop['sqft']} sq ft</p>",
        "<p><strong>Utilities:</strong> Heat + Hot Water + Parking</p>",
    ]

    mapping = {
        "INLINE_STYLE": style_text,
        "TITLE": f"{prop['address_line1']} {prop['unit']} — {prop['city']}, {prop['state']} | {prop['bedrooms']}BR for Rent",
        "META_DESCRIPTION": f"{prop['bedrooms']} bed / {prop['bathrooms']} bath rental in {prop['city']}, {prop['state']}. {prop['sqft']} sq ft at ${_fmt_money(prop['rent'])}/mo.",
        "NAV_BRAND": f"{prop['address_line1']} · {prop['city']}",
        "AVAILABLE_TEXT": f"{prop['available']} — {prop['city']}, {prop['state']}",
        "ADDRESS_LINE1": prop["address_line1"],
        "UNIT": prop["unit"],
        "CITY_STATE_ZIP": f"{prop['city']}, {prop['state']} {prop['zip']}",
        "COUNTY": prop["county"],
        "RENT": _fmt_money(prop["rent"]),
        "OFFER": prop["offer"],
        "HERO_FILE": listing["assets"]["hero"],
        "HERO_ALT": prop.get("hero_alt", photos[0]["alt"]),
        "BEDROOMS": str(prop["bedrooms"]),
        "BATHROOMS": str(prop["bathrooms"]),
        "SQFT": str(prop["sqft"]),
        "PHOTO_GRID_ITEMS": _render_photo_grid(photos),
        "ABOUT_TITLE": f"{prop['sqft']} sq ft of Comfortable City Living",
        "DESCRIPTION_PARAGRAPHS": "".join(f"<p>{p}</p>" for p in prop["description_paragraphs"]),
        "CHIPS": _render_list(prop["chips"], "chip"),
        "SIDEBAR_FACTS": "".join(sidebar_facts),
        "FEATURE_ITEMS": _render_feature_items(prop["features"]),
        "DETAIL_ITEMS": _render_detail_items(prop["details"]),
        "LOCATION_TITLE": f"{prop['city']} at Your Doorstep",
        "MAP_QUERY": prop["map_query"],
        "NEIGHBORHOOD_ITEMS": _render_neighborhood_items(prop["neighborhood"]),
        "FOOTER_LINE1": f"{prop['address_line1']}, {prop['unit']} · {prop['city']}, {prop['state']} {prop['zip']} · ${_fmt_money(prop['rent'])}/month",
        "DISCLAIMER": site["disclaimer"],
        "LISTING_JSON": json.dumps(listing, ensure_ascii=True),
    }
    return _render_template(template, mapping)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate listing HTML and PDF from listing JSON.")
    parser.add_argument("--data", required=True, help="Path to listing JSON data.")
    parser.add_argument("--assets", default="images", help="Path to listing assets directory.")
    parser.add_argument("--style", default="", help="Style key (overrides listing.theme.style).")
    parser.add_argument("--out", default=".", help="Output directory.")
    parser.add_argument("--validate-only", action="store_true", help="Only validate input files.")
    args = parser.parse_args()

    data_path = (ROOT / args.data).resolve() if not Path(args.data).is_absolute() else Path(args.data)
    assets_dir = (ROOT / args.assets).resolve() if not Path(args.assets).is_absolute() else Path(args.assets)
    out_dir = (ROOT / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)

    listing = load_listing(data_path)
    validate_listing_payload(listing)
    validate_assets_exist(listing, assets_dir)

    style_key = args.style or listing["theme"]["style"]
    style_path = ROOT / "styles" / f"{style_key}.css"
    if not style_path.exists():
        raise ListingValidationError(f"Unknown style '{style_key}'. Expected file: {style_path}")
    style_text = style_path.read_text(encoding="utf-8")

    if args.validate_only:
        print("Validation successful.")
        print(f"Data: {data_path}")
        print(f"Assets: {assets_dir}")
        print(f"Style: {style_path}")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    html_output = out_dir / "index.html"
    pdf_output = out_dir / "listing-info.pdf"

    html_output.write_text(_build_html(listing, style_text), encoding="utf-8")
    generate_pdf(listing=listing, assets_dir=assets_dir, out_path=pdf_output, fonts_dir=ROOT / "fonts")

    print(f"Generated HTML: {html_output}")
    print(f"Generated PDF:  {pdf_output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ListingValidationError as exc:
        print(f"Validation error: {exc}")
        raise SystemExit(2)
