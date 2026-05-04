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

FEATURE_ICON_SVGS = [
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
]

DETAIL_ICON_SVGS = [
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>',
]

LOCATION_ICON_SVGS = [
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/></svg>',
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>',
]


def _fmt_money(value: float | int) -> str:
    return f"{int(value):,}"


def _render_template(template: str, mapping: dict[str, str]) -> str:
    output = template
    for key, value in mapping.items():
        output = output.replace(f"__{key}__", value)
    return output


def _render_feature_items(features: list[dict[str, Any]]) -> str:
    return "".join(
        (
            f'<article class="feature-card">'
            f'<div class="feat-icon-wrap">{FEATURE_ICON_SVGS[i % len(FEATURE_ICON_SVGS)]}</div>'
            f'<h3>{item["name"]}</h3><p>{item["description"]}</p></article>'
        )
        for i, item in enumerate(features)
    )


def _render_detail_items(details: list[dict[str, Any]]) -> str:
    return "".join(
        (
            f'<article class="detail-card"><p><strong><span class="detail-icon">{DETAIL_ICON_SVGS[i % len(DETAIL_ICON_SVGS)]}</span>{item["key"]}</strong></p>'
            f'<p>{item["value"]}</p></article>'
        )
        for i, item in enumerate(details)
    )


def _render_neighborhood_items(items: list[dict[str, Any]]) -> str:
    return "".join(
        (
            f'<article class="location-card"><h3><span class="loc-icon">{LOCATION_ICON_SVGS[i % len(LOCATION_ICON_SVGS)]}</span>{item["name"]}</h3>'
            f'<p>{item["description"]}</p></article>'
        )
        for i, item in enumerate(items)
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
