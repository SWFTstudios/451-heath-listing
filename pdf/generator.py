from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fpdf import FPDF
from PIL import Image


MAX_PX = 1200


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.strip().lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


@dataclass
class Palette:
    ink: tuple[int, int, int]
    accent: tuple[int, int, int]
    cream: tuple[int, int, int]
    cream_mid: tuple[int, int, int]
    white: tuple[int, int, int]
    muted: tuple[int, int, int]
    light_ink: tuple[int, int, int]
    faint: tuple[int, int, int]

    @classmethod
    def from_listing(cls, listing: dict[str, Any]) -> "Palette":
        palette = listing["theme"]["palette"]
        return cls(
            ink=hex_to_rgb(palette["ink"]),
            accent=hex_to_rgb(palette["accent"]),
            cream=hex_to_rgb(palette["cream"]),
            cream_mid=hex_to_rgb(palette["cream_mid"]),
            white=hex_to_rgb(palette["white"]),
            muted=hex_to_rgb(palette["muted"]),
            light_ink=hex_to_rgb(palette["light_ink"]),
            faint=hex_to_rgb(palette["faint"]),
        )


def crop_to_ratio(src: Path, w_mm: float, h_mm: float, tmp: Path) -> str:
    img = Image.open(src).convert("RGB")
    iw, ih = img.size
    ratio = w_mm / h_mm
    cur = iw / ih
    if cur > ratio:
        nw = int(ih * ratio)
        img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / ratio)
        img = img.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    if img.width > MAX_PX:
        img = img.resize((MAX_PX, int(MAX_PX * img.height / img.width)), Image.LANCZOS)
    tmp.parent.mkdir(parents=True, exist_ok=True)
    img.save(tmp, "JPEG", quality=72, optimize=True)
    return str(tmp)


class ListingPDF(FPDF):
    def __init__(self, footer_text: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.footer_text = footer_text

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Arial", "I", 7)
        self.set_text_color(120, 113, 108)
        self.cell(0, 6, self.footer_text, align="C")


def _add_fonts(pdf: ListingPDF, fonts_dir: Path) -> None:
    font_files = {
        ("Arial", ""): fonts_dir / "Arial.ttf",
        ("Arial", "B"): fonts_dir / "Arial Bold.ttf",
        ("Arial", "I"): fonts_dir / "Arial Italic.ttf",
        ("Arial", "BI"): fonts_dir / "Arial Bold Italic.ttf",
    }
    all_exist = all(path.exists() for path in font_files.values())
    if not all_exist:
        return

    for (family, style), path in font_files.items():
        pdf.add_font(family, style, str(path))


def generate_pdf(listing: dict[str, Any], assets_dir: Path, out_path: Path, fonts_dir: Path) -> Path:
    prop = listing["property"]
    site = listing["site"]
    photos = listing["assets"]["photos"]
    palette = Palette.from_listing(listing)

    addr_line = f"{prop['address_line1']}, {prop['unit']}"
    city_line = f"{prop['city']}, {prop['state']} {prop['zip']}  ·  {prop['county']}"
    footer_text = f"{addr_line}  ·  ${int(prop['rent']):,}/month  ·  {site['site_url'].replace('https://', '')}"

    pdf = ListingPDF(footer_text=footer_text, orientation="P", unit="mm", format="Letter")
    _add_fonts(pdf, fonts_dir)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(0, 0, 0)

    W = 215.9
    H = 279.4
    M = 14
    CW = W - 2 * M

    tmp = out_path.parent / ".tmp_pdf"
    tmp.mkdir(exist_ok=True)

    # Page 1
    pdf.add_page()
    bar_h = 20
    pdf.set_fill_color(*palette.ink)
    pdf.rect(0, 0, W, bar_h, "F")
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(*palette.white)
    pdf.set_xy(M, 6)
    pdf.cell(CW * 0.55, 8, addr_line.upper(), align="L")
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(*palette.light_ink)
    pdf.set_xy(W * 0.5, 6)
    pdf.cell(CW * 0.5, 8, city_line.upper(), align="R")

    pdf.set_font("Arial", "B", 34)
    pdf.set_text_color(*palette.ink)
    pdf.set_xy(M, bar_h + 5)
    pdf.cell(52, 14, f"${int(prop['rent']):,}", align="L")
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(*palette.muted)
    pdf.set_xy(M + 52, bar_h + 10)
    pdf.cell(28, 8, "/ month", align="L")

    badge_w = 96
    badge_x = W - M - badge_w
    badge_y = bar_h + 7
    pdf.set_fill_color(*palette.accent)
    pdf.set_font("Arial", "B", 8.5)
    pdf.set_text_color(*palette.white)
    pdf.set_xy(badge_x, badge_y)
    pdf.cell(badge_w, 10, prop["offer"], fill=True, align="C")

    hero_y = bar_h + 22
    hero_h = 80
    hero_file = assets_dir / photos[0]["file"]
    hero_tmp = tmp / "hero.jpg"
    pdf.image(crop_to_ratio(hero_file, CW, hero_h, hero_tmp), M, hero_y, CW, hero_h)

    pdf.set_fill_color(*palette.ink)
    pdf.rect(M, hero_y + hero_h - 9, 34, 9, "F")
    pdf.set_font("Arial", "B", 6.5)
    pdf.set_text_color(*palette.white)
    pdf.set_xy(M + 3, hero_y + hero_h - 7.5)
    pdf.cell(30, 6, photos[0]["label"])

    stats_y = hero_y + hero_h + 1
    stats_h = 20
    pdf.set_fill_color(*palette.cream)
    pdf.rect(M, stats_y, CW, stats_h, "F")
    stats = [
        (str(prop["bedrooms"]), "BEDROOM"),
        (str(prop["bathrooms"]), "BATHROOM"),
        (f"{int(prop['sqft'])} SF", "LIVING SPACE"),
        (prop["floor"].upper(), "FLOOR"),
    ]
    col_w = CW / len(stats)
    for i, (num, lbl) in enumerate(stats):
        x = M + i * col_w
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(*palette.ink)
        pdf.set_xy(x, stats_y + 2)
        pdf.cell(col_w, 8, num, align="C")
        pdf.set_font("Arial", "", 6.5)
        pdf.set_text_color(*palette.muted)
        pdf.set_xy(x, stats_y + 11)
        pdf.cell(col_w, 6, lbl, align="C")

    y = stats_y + stats_h + 7
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*palette.ink)
    pdf.set_xy(M, y)
    pdf.cell(CW, 7, "About This Home")
    pdf.set_draw_color(*palette.accent)
    pdf.set_line_width(0.6)
    pdf.line(M, y + 7.5, M + 36, y + 7.5)
    pdf.set_line_width(0.2)
    y += 11

    desc = "\n\n".join(prop["description_paragraphs"])
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(60, 56, 52)
    pdf.set_xy(M, y)
    pdf.multi_cell(CW, 5.2, desc)
    y = pdf.get_y() + 7

    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*palette.ink)
    pdf.set_xy(M, y)
    pdf.cell(CW, 7, "What's Included")
    pdf.set_draw_color(*palette.accent)
    pdf.set_line_width(0.6)
    pdf.line(M, y + 7.5, M + 38, y + 7.5)
    pdf.set_line_width(0.2)
    y += 11

    half = CW / 2
    for i, feature in enumerate(prop["features"]):
        c = i % 2
        r = i // 2
        x = M + c * half
        fy = y + r * 7
        pdf.set_xy(x, fy)
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(*palette.accent)
        pdf.cell(6, 6, "-")
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(60, 56, 52)
        pdf.cell(half - 6, 6, feature["name"])

    # Page 2
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    pdf.set_fill_color(*palette.cream)
    pdf.rect(0, 0, W, 13, "F")
    pdf.set_font("Arial", "B", 7.5)
    pdf.set_text_color(*palette.ink)
    pdf.set_xy(M, 3)
    pdf.cell(CW * 0.6, 7, f"{addr_line.upper()}  ·  {prop['city'].upper()}, {prop['state']}")

    grid_y = 16
    gap = 4
    ph_w = (CW - gap) / 2
    ph_h = 50
    grid_photos = photos[1:5]
    for i, photo in enumerate(grid_photos):
        ci = i % 2
        ri = i // 2
        px = M + ci * (ph_w + gap)
        py = grid_y + ri * (ph_h + gap)
        tmp_i = tmp / f"grid{i}.jpg"
        src = assets_dir / photo["file"]
        pdf.image(crop_to_ratio(src, ph_w, ph_h, tmp_i), px, py, ph_w, ph_h)
        pdf.set_fill_color(*palette.ink)
        pdf.rect(px, py + ph_h - 9, 28, 9, "F")
        pdf.set_font("Arial", "B", 6.5)
        pdf.set_text_color(*palette.white)
        pdf.set_xy(px + 2, py + ph_h - 7.5)
        pdf.cell(26, 6, photo["label"])

    tbl_y = grid_y + 2 * (ph_h + gap) + 7
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*palette.ink)
    pdf.set_xy(M, tbl_y)
    pdf.cell(CW, 7, "Property Details")
    pdf.set_draw_color(*palette.accent)
    pdf.set_line_width(0.6)
    pdf.line(M, tbl_y + 7.5, M + 38, tbl_y + 7.5)
    pdf.set_line_width(0.2)
    tbl_y += 11

    rows = [
        ("Monthly Rent", f"${int(prop['rent']):,} / month"),
        ("Special Offer", prop["offer"]),
        ("Square Footage", f"{int(prop['sqft'])} sq ft"),
        ("Bedrooms", f"{prop['bedrooms']} Bedroom"),
        ("Bathrooms", f"{prop['bathrooms']} Full Bathroom"),
        ("Year Built", str(prop["year_built"])),
        ("Type", prop["property_type"]),
        ("Style", prop["style"]),
        ("Utilities", "Heat & Hot Water Included"),
        ("Parking", "Included"),
        ("Pets", "Considered case-by-case"),
    ]
    row_h = 6.8
    key_w = CW * 0.38
    for i, (k, v) in enumerate(rows):
        bg = palette.cream_mid if i % 2 == 0 else palette.white
        pdf.set_fill_color(*bg)
        pdf.rect(M, tbl_y, CW, row_h, "F")
        pdf.set_xy(M + 4, tbl_y + 1.0)
        pdf.set_font("Arial", "", 8.5)
        pdf.set_text_color(*palette.muted)
        pdf.cell(key_w, 5.5, k)
        pdf.set_font("Arial", "B", 8.5)
        pdf.set_text_color(*palette.ink)
        pdf.cell(CW - key_w - 4, 5.5, v)
        tbl_y += row_h

    card_y = tbl_y + 5
    card_h = 36
    pdf.set_fill_color(*palette.ink)
    pdf.rect(M, card_y, CW, card_h, "F")
    pdf.set_font("Arial", "B", 7.5)
    pdf.set_text_color(*palette.accent)
    pdf.set_xy(M + 10, card_y + 6)
    pdf.cell(CW - 20, 6, "OWNER CONTACT")
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(*palette.white)
    pdf.set_xy(M + 10, card_y + 13)
    pdf.cell(CW - 20, 10, "Property Owner")
    pdf.set_font("Arial", "", 8.5)
    pdf.set_text_color(*palette.light_ink)
    pdf.set_xy(M + 10, card_y + 23)
    pdf.cell(CW - 20, 6, f"Inquiries: {site['lead_email']}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    return out_path
