from pathlib import Path

from pdf.generator import generate_pdf
from tools.listing_utils import load_listing, validate_assets_exist, validate_listing_payload


def main() -> int:
    root = Path(__file__).parent
    listing = load_listing(root / "listings" / "451-heath.json")
    validate_listing_payload(listing)
    assets_dir = root / "images"
    validate_assets_exist(listing, assets_dir)
    out_path = root / "listing-info.pdf"
    generate_pdf(listing, assets_dir=assets_dir, out_path=out_path, fonts_dir=root / "fonts")
    print(f"PDF created: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
