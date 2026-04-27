from fpdf import FPDF
from pathlib import Path
from PIL import Image

IMG = Path("/Users/elombe.kisala/Desktop/FOLDERS/Work/CLAUDE PROJECTS/451-heath-listing/images")
OUT = Path("/Users/elombe.kisala/Desktop/FOLDERS/Work/CLAUDE PROJECTS/451-heath-listing/listing-info.pdf")
TMP = Path("/tmp/listing_pdf_tmp")
TMP.mkdir(exist_ok=True)

FONT_DIR = Path("/System/Library/Fonts/Supplemental")

# Palette
INK       = (28,  25,  23)
ACCENT    = (212, 82,  30)
CREAM     = (234, 231, 225)
CREAM_MID = (242, 240, 236)
MUTED     = (120, 113, 108)
WHITE     = (255, 255, 255)
LIGHT_INK = (180, 176, 170)
FAINT     = (140, 136, 130)


MAX_PX = 1200  # cap pixel width to keep file size small

def crop_to_ratio(src: Path, w_mm: float, h_mm: float, tmp: Path) -> str:
    img = Image.open(src).convert("RGB")
    iw, ih = img.size
    ratio = w_mm / h_mm
    cur   = iw / ih
    if cur > ratio:
        nw = int(ih * ratio)
        img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / ratio)
        img = img.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    # Downscale to max width to reduce file size
    if img.width > MAX_PX:
        img = img.resize((MAX_PX, int(MAX_PX * img.height / img.width)), Image.LANCZOS)
    img.save(tmp, "JPEG", quality=72, optimize=True)
    return str(tmp)


class PDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 6,
            "451 Heath Place, Apt 2  \u00b7  Hackensack, NJ 07601  \u00b7  $1,925/month  \u00b7  "
            "swftstudios.github.io/451-heath-listing",
            align="C")


pdf = PDF(orientation="P", unit="mm", format="Letter")

# Register Arial variants for Unicode support
pdf.add_font("Arial",  "",   str(FONT_DIR / "Arial.ttf"))
pdf.add_font("Arial",  "B",  str(FONT_DIR / "Arial Bold.ttf"))
pdf.add_font("Arial",  "I",  str(FONT_DIR / "Arial Italic.ttf"))
pdf.add_font("Arial",  "BI", str(FONT_DIR / "Arial Bold Italic.ttf"))
# Arial Unicode for glyphs (checkmark ✓) missing from standard Arial
pdf.add_font("ArialU", "",   "/Library/Fonts/Arial Unicode.ttf")

pdf.set_auto_page_break(auto=True, margin=14)
pdf.set_margins(0, 0, 0)

W  = 215.9
H  = 279.4
M  = 14
CW = W - 2 * M


# ═══════════════════════════════════════════════════
#  PAGE 1
# ═══════════════════════════════════════════════════
pdf.add_page()

# ── Header bar
BAR_H = 20
pdf.set_fill_color(*INK)
pdf.rect(0, 0, W, BAR_H, "F")
pdf.set_font("Arial", "B", 9)
pdf.set_text_color(*WHITE)
pdf.set_xy(M, 6)
pdf.cell(CW * 0.55, 8, "451 HEATH PLACE, APT 2", align="L")
pdf.set_font("Arial", "", 9)
pdf.set_text_color(*LIGHT_INK)
pdf.set_xy(W * 0.5, 6)
pdf.cell(CW * 0.5, 8, "HACKENSACK, NJ 07601  \u00b7  BERGEN COUNTY", align="R")

# ── Price + offer badge
pdf.set_font("Arial", "B", 34)
pdf.set_text_color(*INK)
pdf.set_xy(M, BAR_H + 5)
pdf.cell(52, 14, "$1,925", align="L")

pdf.set_font("Arial", "", 11)
pdf.set_text_color(*MUTED)
pdf.set_xy(M + 52, BAR_H + 10)
pdf.cell(28, 8, "/ month", align="L")

BADGE_W = 86
BADGE_X = W - M - BADGE_W
BADGE_Y = BAR_H + 7
pdf.set_fill_color(*ACCENT)
pdf.set_font("Arial", "B", 9)
pdf.set_text_color(*WHITE)
pdf.set_xy(BADGE_X, BADGE_Y)
pdf.cell(BADGE_W, 10, "ONE MONTH FREE \u2014 Lease by May 15th", fill=True, align="C")

# ── Hero photo
HERO_Y = BAR_H + 22
HERO_H = 80
hero_p = crop_to_ratio(IMG / "photo1.jpg", CW, HERO_H, TMP / "hero.jpg")
pdf.image(hero_p, M, HERO_Y, CW, HERO_H)

# Photo corner label
pdf.set_fill_color(*INK)
pdf.rect(M, HERO_Y + HERO_H - 9, 34, 9, "F")
pdf.set_font("Arial", "B", 6.5)
pdf.set_text_color(*WHITE)
pdf.set_xy(M + 3, HERO_Y + HERO_H - 7.5)
pdf.cell(30, 6, "LIVING ROOM")

# ── Stats bar
STATS_Y = HERO_Y + HERO_H + 1
STATS_H = 20
pdf.set_fill_color(*CREAM)
pdf.rect(M, STATS_Y, CW, STATS_H, "F")

stats = [("1", "BEDROOM"), ("1", "BATHROOM"), ("663 SF", "LIVING SPACE"), ("2ND FL.", "WALK-UP")]
col_w = CW / len(stats)
for i, (num, lbl) in enumerate(stats):
    x = M + i * col_w
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*INK)
    pdf.set_xy(x, STATS_Y + 2)
    pdf.cell(col_w, 8, num, align="C")
    pdf.set_font("Arial", "", 6.5)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(x, STATS_Y + 11)
    pdf.cell(col_w, 6, lbl, align="C")
    if i > 0:
        pdf.set_draw_color(*CREAM_MID)
        pdf.line(x, STATS_Y + 4, x, STATS_Y + 16)

# ── About
y = STATS_Y + STATS_H + 7
pdf.set_font("Arial", "B", 12)
pdf.set_text_color(*INK)
pdf.set_xy(M, y)
pdf.cell(CW, 7, "About This Home")

# Accent underline
pdf.set_draw_color(*ACCENT)
pdf.set_line_width(0.6)
pdf.line(M, y + 7.5, M + 36, y + 7.5)
pdf.set_line_width(0.2)
y += 11

desc = (
    "Welcome to 451 Heath Place, Apt 2 \u2014 a bright, garden-style 1-bedroom condo tucked into a "
    "quiet courtyard setting in Hackensack, NJ. Step inside and head up the private staircase to "
    "your sun-filled retreat on the second floor.\n\n"
    "The open floor plan makes excellent use of 663 square feet. The updated kitchen features new "
    "flooring, fresh countertops, and a brand-new refrigerator. The bedroom comfortably fits a "
    "king-size bed; additional furniture is available on request.\n\n"
    "Heat, hot water, and parking are all included in rent \u2014 move in knowing your biggest "
    "utility costs are covered. Rare for Bergen County."
)
pdf.set_font("Arial", "", 9)
pdf.set_text_color(60, 56, 52)
pdf.set_xy(M, y)
pdf.multi_cell(CW, 5.2, desc)
y = pdf.get_y() + 7

# ── Features
pdf.set_font("Arial", "B", 12)
pdf.set_text_color(*INK)
pdf.set_xy(M, y)
pdf.cell(CW, 7, "What\u2019s Included")

pdf.set_draw_color(*ACCENT)
pdf.set_line_width(0.6)
pdf.line(M, y + 7.5, M + 38, y + 7.5)
pdf.set_line_width(0.2)
y += 11

features = [
    "Heat Included",          "Hot Water Included",
    "Parking Included",       "Updated Kitchen",
    "Garden Style Walk-Up",   "Furnished Option Available",
    "Courtyard Setting",      "Pets Considered",
    "Open Floor Plan",        "Near NYC Transit",
]
half = CW / 2
for i, feat in enumerate(features):
    c = i % 2
    r = i // 2
    x = M + c * half
    fy = y + r * 7
    pdf.set_xy(x, fy)
    pdf.set_font("ArialU", "", 9)
    pdf.set_text_color(*ACCENT)
    pdf.cell(6, 6, "\u2713")
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(60, 56, 52)
    pdf.cell(half - 6, 6, feat)


# ═══════════════════════════════════════════════════
#  PAGE 2
# ═══════════════════════════════════════════════════
pdf.add_page()

# ── Thin header
pdf.set_fill_color(*CREAM)
pdf.rect(0, 0, W, 13, "F")
pdf.set_font("Arial", "B", 7.5)
pdf.set_text_color(*INK)
pdf.set_xy(M, 3)
pdf.cell(CW * 0.6, 7, "451 HEATH PLACE, APT 2  \u00b7  HACKENSACK, NJ 07601")
pdf.set_font("Arial", "", 7.5)
pdf.set_text_color(*MUTED)
pdf.set_xy(W * 0.55, 3)
pdf.cell(CW * 0.45, 7, "PHOTO TOUR", align="R")

# ── 2×2 photo grid
GRID_Y = 16
GAP    = 4
PH_W   = (CW - GAP) / 2
PH_H   = 60
grid_photos = [
    (IMG / "photo2.jpg", "KITCHEN"),
    (IMG / "photo3.jpg", "BEDROOM"),
    (IMG / "photo4.jpg", "BATHROOM"),
    (IMG / "photo5.jpg", "EXTERIOR"),
]
for i, (src, lbl) in enumerate(grid_photos):
    ci = i % 2
    ri = i // 2
    px = M + ci * (PH_W + GAP)
    py = GRID_Y + ri * (PH_H + GAP)
    tmp_i = TMP / f"grid{i}.jpg"
    try:
        pdf.image(crop_to_ratio(src, PH_W, PH_H, tmp_i), px, py, PH_W, PH_H)
    except Exception as ex:
        print(f"  Warning: could not embed {src.name}: {ex}")
        pdf.set_fill_color(*CREAM_MID)
        pdf.rect(px, py, PH_W, PH_H, "F")
    # Corner label
    pdf.set_fill_color(*INK)
    pdf.rect(px, py + PH_H - 9, 28, 9, "F")
    pdf.set_font("Arial", "B", 6.5)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(px + 2, py + PH_H - 7.5)
    pdf.cell(26, 6, lbl)

# ── Property details table
TBL_Y = GRID_Y + 2 * (PH_H + GAP) + 7
pdf.set_font("Arial", "B", 12)
pdf.set_text_color(*INK)
pdf.set_xy(M, TBL_Y)
pdf.cell(CW, 7, "Property Details")
pdf.set_draw_color(*ACCENT)
pdf.set_line_width(0.6)
pdf.line(M, TBL_Y + 7.5, M + 38, TBL_Y + 7.5)
pdf.set_line_width(0.2)
TBL_Y += 11

rows = [
    ("Monthly Rent",     "$1,925 / month"),
    ("Special Offer",    "1 Month FREE \u2014 Lease by May 15th"),
    ("Square Footage",   "663 sq ft"),
    ("Bedrooms",         "1 Bedroom"),
    ("Bathrooms",        "1 Full Bathroom"),
    ("Year Built",       "1950"),
    ("Type",             "Condominium"),
    ("Style",            "Garden / 2nd Floor Walk-Up"),
    ("Utilities",        "Heat & Hot Water Included"),
    ("Parking",          "Included"),
    ("Pets",             "Considered case-by-case"),
]
ROW_H = 7.2
KEY_W = CW * 0.38
for i, (k, v) in enumerate(rows):
    bg = CREAM_MID if i % 2 == 0 else WHITE
    pdf.set_fill_color(*bg)
    pdf.rect(M, TBL_Y, CW, ROW_H, "F")
    pdf.set_xy(M + 4, TBL_Y + 1.2)
    pdf.set_font("Arial", "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(KEY_W, 5.5, k)
    pdf.set_font("Arial", "B", 8.5)
    pdf.set_text_color(*INK)
    pdf.cell(CW - KEY_W - 4, 5.5, v)
    TBL_Y += ROW_H

# ── Agent card
CARD_Y = TBL_Y + 8
CARD_H = 54
pdf.set_fill_color(*INK)
pdf.rect(M, CARD_Y, CW, CARD_H, "F")

pdf.set_font("Arial", "B", 7.5)
pdf.set_text_color(*ACCENT)
pdf.set_xy(M + 10, CARD_Y + 8)
pdf.cell(CW - 20, 6, "YOUR LISTING AGENT")

pdf.set_font("Arial", "B", 18)
pdf.set_text_color(*WHITE)
pdf.set_xy(M + 10, CARD_Y + 15)
pdf.cell(CW - 20, 10, "Roosevelt Hall")

pdf.set_font("Arial", "", 8.5)
pdf.set_text_color(*LIGHT_INK)
pdf.set_xy(M + 10, CARD_Y + 26)
pdf.cell(CW - 20, 6, "REALTOR\u00ae  \u00b7  Coldwell Banker Realty  \u00b7  50 Broadway, Hillsdale, NJ 07642")

pdf.set_font("Arial", "B", 9)
pdf.set_text_color(*WHITE)
pdf.set_xy(M + 10, CARD_Y + 33)
pdf.cell(54, 6, "Mobile: (201) 280-6333")
pdf.set_font("Arial", "", 9)
pdf.set_text_color(*LIGHT_INK)
pdf.cell(CW - 64, 6, "Office: (201) 599-1100")

pdf.set_font("Arial", "I", 7.5)
pdf.set_text_color(*FAINT)
pdf.set_xy(M + 10, CARD_Y + 40)
pdf.cell(CW - 20, 6, "realtor.com/realestateagents/5673e76b89a689010069dbc1")

# Divider + closing line
pdf.set_draw_color(55, 52, 48)
pdf.set_line_width(0.3)
pdf.line(M + 10, CARD_Y + CARD_H - 11, M + CW - 10, CARD_Y + CARD_H - 11)
pdf.set_line_width(0.2)
pdf.set_font("Arial", "", 7.5)
pdf.set_text_color(110, 106, 100)
pdf.set_xy(M + 10, CARD_Y + CARD_H - 9)
pdf.cell(CW - 20, 6,
    "To schedule a showing, contact Roosevelt directly or reply to this email.",
    align="C")

# ── Save
pdf.output(str(OUT))
sz = OUT.stat().st_size
print(f"PDF created:  {OUT}")
print(f"Size:         {sz / 1024:.0f} KB  ({sz:,} bytes)")
