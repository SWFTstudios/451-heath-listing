from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


class ListingValidationError(ValueError):
    pass


def load_listing(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ListingValidationError("Listing file must be a JSON object.")
    return data


def write_listing(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def _require(mapping: dict[str, Any], key: str, section: str) -> Any:
    value = mapping.get(key)
    if value in (None, "", []):
        raise ListingValidationError(f"Missing required value '{section}.{key}'.")
    return value


def validate_listing_payload(data: dict[str, Any]) -> None:
    _require(data, "id", "root")
    prop = _require(data, "property", "root")
    agent = _require(data, "agent", "root")
    site = _require(data, "site", "root")
    assets = _require(data, "assets", "root")
    theme = _require(data, "theme", "root")

    if not isinstance(prop, dict):
        raise ListingValidationError("'property' must be an object.")
    if not isinstance(agent, dict):
        raise ListingValidationError("'agent' must be an object.")
    if not isinstance(site, dict):
        raise ListingValidationError("'site' must be an object.")
    if not isinstance(assets, dict):
        raise ListingValidationError("'assets' must be an object.")
    if not isinstance(theme, dict):
        raise ListingValidationError("'theme' must be an object.")

    for key in (
        "address_line1",
        "unit",
        "city",
        "state",
        "zip",
        "county",
        "rent",
        "bedrooms",
        "bathrooms",
        "sqft",
        "offer",
        "description_paragraphs",
        "features",
        "details",
        "neighborhood",
        "map_query",
    ):
        _require(prop, key, "property")

    for key in ("name", "title", "brokerage", "office_address", "mobile", "office", "profile_url"):
        _require(agent, key, "agent")

    for key in ("lead_email", "site_url", "pdf_url", "disclaimer"):
        _require(site, key, "site")

    _require(assets, "hero", "assets")
    photos = _require(assets, "photos", "assets")
    if not isinstance(photos, list) or len(photos) < 1:
        raise ListingValidationError("'assets.photos' must have at least one image.")
    for idx, photo in enumerate(photos):
        if not isinstance(photo, dict):
            raise ListingValidationError(f"'assets.photos[{idx}]' must be an object.")
        for key in ("file", "label", "alt"):
            _require(photo, key, f"assets.photos[{idx}]")

    palette = _require(theme, "palette", "theme")
    _require(theme, "style", "theme")
    if not isinstance(palette, dict):
        raise ListingValidationError("'theme.palette' must be an object.")
    for key in ("ink", "accent", "cream", "cream_mid", "white", "muted", "light_ink", "faint"):
        _require(palette, key, "theme.palette")


def validate_assets_exist(listing: dict[str, Any], assets_dir: Path) -> None:
    missing: list[str] = []
    hero = listing["assets"]["hero"]
    if not (assets_dir / hero).exists():
        missing.append(hero)

    for photo in listing["assets"]["photos"]:
        file_name = photo["file"]
        if not (assets_dir / file_name).exists():
            missing.append(file_name)

    if missing:
        missing_text = ", ".join(sorted(set(missing)))
        raise ListingValidationError(f"Missing asset files in '{assets_dir}': {missing_text}")


def parse_csv_row(csv_path: Path) -> dict[str, str]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ListingValidationError("CSV file has no data rows.")
    return {k: (v or "").strip() for k, v in rows[0].items()}
