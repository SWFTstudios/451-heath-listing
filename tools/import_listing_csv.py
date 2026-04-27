from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.listing_utils import parse_csv_row, validate_listing_payload, write_listing


def _split_list(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip()]


def _split_pair_list(value: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for token in _split_list(value):
        if "::" in token:
            left, right = token.split("::", 1)
            items.append({"name": left.strip(), "description": right.strip()})
    return items


def map_row_to_listing(row: dict[str, str]) -> dict:
    photos = []
    for idx in range(1, 6):
        photos.append(
            {
                "file": row.get(f"photo{idx}_file", f"photo{idx}.jpg"),
                "label": row.get(f"photo{idx}_label", f"PHOTO {idx}"),
                "alt": row.get(f"photo{idx}_alt", f"Listing photo {idx}"),
            }
        )

    listing = {
        "id": row["id"],
        "property": {
            "address_line1": row["address_line1"],
            "unit": row["unit"],
            "city": row["city"],
            "state": row["state"],
            "zip": row["zip"],
            "county": row["county"],
            "rent": float(row["rent"]),
            "bedrooms": float(row["bedrooms"]),
            "bathrooms": float(row["bathrooms"]),
            "sqft": float(row["sqft"]),
            "year_built": float(row["year_built"]),
            "property_type": row["property_type"],
            "style": row["property_style"],
            "floor": row["floor"],
            "available": row["available"],
            "offer": row["offer"],
            "description_paragraphs": _split_list(row["description_paragraphs"]),
            "chips": _split_list(row["chips"]),
            "features": _split_pair_list(row["features"]),
            "details": [
                {"key": "Monthly Rent", "value": f"${int(float(row['rent'])):,}"},
                {"key": "Square Footage", "value": f"{int(float(row['sqft']))} sq ft"},
                {"key": "Year Built", "value": row["year_built"]},
                {"key": "Property Type", "value": row["property_type"]},
                {"key": "Style", "value": row["property_style"]},
            ],
            "neighborhood": _split_pair_list(row["neighborhood"]),
            "map_query": row["map_query"],
            "hero_alt": row.get("hero_alt", ""),
        },
        "agent": {
            "name": row["agent_name"],
            "title": row["agent_title"],
            "brokerage": row["agent_brokerage"],
            "office_address": row["agent_office_address"],
            "mobile": row["agent_mobile"],
            "office": row["agent_office"],
            "profile_url": row["agent_profile_url"],
        },
        "site": {
            "lead_email": row["lead_email"],
            "site_url": row["site_url"],
            "pdf_url": row["pdf_url"],
            "disclaimer": row["disclaimer"],
        },
        "assets": {
            "hero": row.get("hero_file", "hero.jpg"),
            "photos": photos,
        },
        "theme": {
            "style": row.get("style", "cream-modern"),
            "palette": {
                "ink": row.get("palette_ink", "#1c1917"),
                "accent": row.get("palette_accent", "#d4521e"),
                "cream": row.get("palette_cream", "#eae7e1"),
                "cream_mid": row.get("palette_cream_mid", "#f2f0ec"),
                "white": row.get("palette_white", "#ffffff"),
                "muted": row.get("palette_muted", "#78716c"),
                "light_ink": row.get("palette_light_ink", "#b4b0aa"),
                "faint": row.get("palette_faint", "#8c8882"),
            },
        },
    }
    return listing


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a spreadsheet CSV row into listing JSON.")
    parser.add_argument("--csv", required=True, help="CSV path with listing columns.")
    parser.add_argument("--out", required=True, help="Output JSON path.")
    args = parser.parse_args()

    row = parse_csv_row(Path(args.csv))
    listing = map_row_to_listing(row)
    validate_listing_payload(listing)
    write_listing(Path(args.out), listing)
    print(f"Wrote listing JSON: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
