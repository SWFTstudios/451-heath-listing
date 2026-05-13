from __future__ import annotations

import argparse
import html
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

# Heroicons-style stroke icons matched to chip meaning (24x24, stroke-width 1.5).
_SVG_CHIP_DEFAULT = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'
    "</svg>"
)
_SVG_CHIP_HEAT = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"/>'
    "</svg>"
)
_SVG_CHIP_HOT_WATER = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 2.25c-3 4.5-6.75 7.5-6.75 10.5a6.75 6.75 0 1013.5 0c0-3-3.75-6-6.75-10.5z"/>'
    "</svg>"
)
_SVG_CHIP_LAUNDRY = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M7.5 4.5h9A2.25 2.25 0 0118.75 6.75v10.5A2.25 2.25 0 0116.5 19.5h-9A2.25 2.25 0 015.25 17.25V6.75A2.25 2.25 0 017.5 4.5z"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M7.5 4.5V3.75A.75.75 0 018.25 3h7.5a.75.75 0 01.75.75V4.5"/>'
    '<circle cx="12" cy="13" r="2.75"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M9 8.25h.008v.008H9V8.25zm2.25 0h.008v.008h-.008V8.25zm2.25 0h.008v.008h-.008V8.25z"/>'
    "</svg>"
)
_SVG_CHIP_PARKING = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>'
    "</svg>"
)
_SVG_CHIP_SUN_OUTDOOR = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.886l-1.591 1.591M21 12h-2.25m-.886 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"/>'
    "</svg>"
)
_SVG_CHIP_LEAF = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 21c-4.5-3-7.5-6.75-7.5-10.5A7.5 7.5 0 0119.5 6c0 3.75-3 7.5-7.5 10.5z"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 21V11"/>'
    "</svg>"
)
_SVG_CHIP_GRID_LAYOUT = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/>'
    "</svg>"
)
_SVG_CHIP_STAIRS = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M5 19h14M5 15h10M5 11h6M5 7h3"/>'
    "</svg>"
)
_SVG_CHIP_HEART = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733C11.285 4.876 9.623 3.75 7.688 3.75 5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"/>'
    "</svg>"
)
_SVG_CHIP_CALENDAR = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5a2.25 2.25 0 002.25-2.25m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5a2.25 2.25 0 012.25 2.25m-18 0v7.5"/>'
    "</svg>"
)

_SVG_FEATURE_HOME = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.875c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>'
    "</svg>"
)
_SVG_FEATURE_KITCHEN = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>'
    "</svg>"
)
_SVG_FEATURE_CUBE = (
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="m21 16.5-5.25-3.048m-10.5 0L3 16.5m6.75-3.75L12 20.25l2.25-7.5m-9-4.5h18M3.75 6h16.5L12 2.25 3.75 6z"/>'
    "</svg>"
)


def _amenity_icon_from_text(low: str) -> str:
    """Pick a semantic SVG (24x24 outline) for chips and feature cards from combined lowercase text."""
    if "private" in low and ("walk" in low or "walk-up" in low or "walk up" in low or "stair" in low or "entrance" in low):
        return _SVG_FEATURE_HOME
    if (
        "kitchen" in low
        or "refrigerator" in low
        or "countertop" in low
        or "counter top" in low
        or "appliance" in low
        or "cupboard" in low
    ):
        return _SVG_FEATURE_KITCHEN
    if "furnish" in low or "furniture" in low or "sectional" in low or ("king" in low and "bed" in low) or "dresser" in low:
        return _SVG_FEATURE_CUBE
    if "laundry" in low or "washer" in low or "dryer" in low:
        return _SVG_CHIP_LAUNDRY
    if "courtyard" in low or "patio" in low or "deck" in low or "balcony" in low:
        return _SVG_CHIP_SUN_OUTDOOR
    if ("garden" in low or "yard" in low or "lawn" in low) and "garden-style" not in low:
        return _SVG_CHIP_LEAF
    if "parking" in low or "garage" in low or "street" in low or ("car" in low and "electric" not in low):
        return _SVG_CHIP_PARKING
    if "pet" in low or "dog" in low or "cat" in low:
        return _SVG_CHIP_HEART
    if "hot water" in low or ("water" in low and "hot" in low):
        return _SVG_CHIP_HOT_WATER
    if "heat" in low and "water" not in low:
        return _SVG_CHIP_HEAT
    if "floor plan" in low or ("open" in low and "plan" in low):
        return _SVG_CHIP_GRID_LAYOUT
    if "walk" in low or "stair" in low:
        return _SVG_CHIP_STAIRS
    if "built" in low or low.startswith("year "):
        return _SVG_CHIP_CALENDAR
    if "open" in low:
        return _SVG_CHIP_GRID_LAYOUT
    return _SVG_CHIP_DEFAULT


def _chip_icon_svg(label: str) -> str:
    return _amenity_icon_from_text(label.strip().lower())


def _feature_icon_svg(name: str, description: str) -> str:
    return _amenity_icon_from_text(f"{name} {description}".lower())


def _render_chips(chips: list[str]) -> str:
    return "".join(
        (
            f'<span class="chip">'
            f'<span class="chip-icon" aria-hidden="true">{_chip_icon_svg(label)}</span>'
            f'<span class="chip-text">{html.escape(label.strip())}</span>'
            f"</span>"
        )
        for label in chips
    )


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
            f'<div class="feat-icon-wrap">{_feature_icon_svg(item["name"], item.get("description", ""))}</div>'
            f'<h3>{html.escape(item["name"])}</h3><p>{html.escape(item.get("description", ""))}</p></article>'
        )
        for item in features
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
        "<p><strong>Move-In:</strong> June 1st or sooner</p>",
        "<p><strong>Utilities:</strong> Heat + Hot Water</p>",
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
        "CHIPS": _render_chips(prop["chips"]),
        "SIDEBAR_FACTS": "".join(sidebar_facts),
        "FEATURE_ITEMS": _render_feature_items(prop["features"]),
        "DETAIL_ITEMS": _render_detail_items(prop["details"]),
        "LOCATION_TITLE": f"{prop['city']} at Your Doorstep",
        "MAP_QUERY": prop["map_query"],
        "NEIGHBORHOOD_ITEMS": _render_neighborhood_items(prop["neighborhood"]),
        "FOOTER_LINE1": f"{prop['address_line1']}, {prop['unit']} · {prop['city']}, {prop['state']} {prop['zip']} · ${_fmt_money(prop['rent'])}/month",
        "DISCLAIMER": site["disclaimer"],
        "NEXT_STEPS_URL": site.get("next_steps_url", "").strip(),
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
