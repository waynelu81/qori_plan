from __future__ import annotations

import json
import math
import shutil
import subprocess
import textwrap
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
KIT = OUTPUT / "qori-brand-kit"
LOGOS = KIT / "logos"
BANNERS = KIT / "banners"
TOKENS = KIT / "tokens"
GUIDELINES = KIT / "guidelines"
PDF_OUTPUT = OUTPUT / "pdf"
PREVIEW_OUTPUT = OUTPUT / "previews"

PAPER = "#FAF8F5"
CARD = "#FFFDF8"
INK = "#231F1A"
GOLD = "#98661B"
GOLD_HOVER = "#7F5113"
MUTED = "#6E665E"
SOFT = "#F1ECE5"
BORDER = "#DED6CB"
INPUT = "#8A7F73"
SUCCESS = "#286B49"
WARNING = "#8A5A10"
DESTRUCTIVE = "#B42318"
DARK_BG = "#211E19"
DARK_CARD = "#2B2721"
DARK_TEXT = "#F8F2E8"
DARK_MUTED = "#C7BCAF"
DARK_BORDER = "#4D463D"
DARK_GOLD = "#F0B85A"


def ensure_dirs() -> None:
    for directory in (LOGOS, BANNERS, TOKENS, GUIDELINES, PDF_OUTPUT, PREVIEW_OUTPUT):
        directory.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def mark_svg(stroke: str, background: str | None = None, rounded: bool = False) -> str:
    bg = ""
    if background:
        radius = 24 if rounded else 0
        bg = f'<rect width="100" height="100" rx="{radius}" fill="{background}"/>'
    return f"""
{bg}
<g fill="none" stroke="{stroke}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="50" cy="50" r="31" stroke-dasharray="158 37" transform="rotate(42 50 50)"/>
  <path d="M66 66 L83 83"/>
</g>
"""


def wordmark_shapes(mark_color: str, word_color: str) -> str:
    return f"""
<g transform="translate(8 8)">
  <g transform="scale(1.04)">{mark_svg(mark_color)}</g>
  <g fill="none" stroke="{word_color}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="146" cy="60" r="22"/>
    <path d="M191 82 V39 M191 57 C197 45 207 39 220 43"/>
    <path d="M247 55 V82"/>
  </g>
  <circle cx="247" cy="39" r="5" fill="{word_color}"/>
</g>
"""


def svg_document(width: int, height: int, body: str, view_box: str | None = None) -> str:
    vb = view_box or f"0 0 {width} {height}"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{vb}" role="img">
{body}
</svg>"""


def build_logo_assets() -> None:
    write_text(
        LOGOS / "qori-mark.svg",
        svg_document(100, 100, f'<title>Qori open-circle mark</title>{mark_svg(GOLD)}'),
    )
    write_text(
        LOGOS / "qori-app-icon.svg",
        svg_document(100, 100, f'<title>Qori app icon</title>{mark_svg(PAPER, GOLD, rounded=True)}'),
    )
    write_text(
        LOGOS / "qori-logo-primary.svg",
        svg_document(
            300,
            116,
            f'<title>Qori primary logo</title>{wordmark_shapes(GOLD, INK)}',
            "0 0 300 116",
        ),
    )
    write_text(
        LOGOS / "qori-logo-reverse.svg",
        svg_document(
            300,
            116,
            f'<title>Qori reverse logo</title>{wordmark_shapes(DARK_GOLD, PAPER)}',
            "0 0 300 116",
        ),
    )
    write_text(
        LOGOS / "qori-logo-mono-ink.svg",
        svg_document(
            300,
            116,
            f'<title>Qori monochrome logo</title>{wordmark_shapes(INK, INK)}',
            "0 0 300 116",
        ),
    )


def logo_group_svg(x: float, y: float, scale: float, mark_color: str, word_color: str) -> str:
    return f'<g transform="translate({x} {y}) scale({scale})">{wordmark_shapes(mark_color, word_color)}</g>'


def build_banner_assets() -> None:
    hero = f"""
<title>Qori brand banner - sharing is caring</title>
<defs>
  <linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#F5DCA9"/>
    <stop offset="0.55" stop-color="#D99A39"/>
    <stop offset="1" stop-color="#8A5717"/>
  </linearGradient>
</defs>
<rect width="1600" height="640" fill="{PAPER}"/>
<circle cx="1500" cy="52" r="235" fill="none" stroke="{GOLD}" stroke-width="2" opacity="0.10"/>
<circle cx="1500" cy="52" r="175" fill="none" stroke="{GOLD}" stroke-width="2" opacity="0.16"/>
<circle cx="1500" cy="52" r="116" fill="none" stroke="{GOLD}" stroke-width="2" opacity="0.22"/>
{logo_group_svg(88, 52, 0.72, GOLD, INK)}
<text x="96" y="285" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="76" font-weight="700" letter-spacing="-3" fill="{INK}">sharing is caring</text>
<text x="100" y="343" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="27" font-weight="400" fill="{MUTED}">A private classroom for people you already teach.</text>
<line x1="100" y1="395" x2="175" y2="395" stroke="{GOLD}" stroke-width="7" stroke-linecap="round"/>
<text x="100" y="455" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="19" font-weight="600" letter-spacing="2" fill="{GOLD}">TEACH • SHARE • CONTINUE</text>

<g transform="translate(1050 92) rotate(4 225 225)" opacity="0.36">
  <rect width="438" height="452" rx="30" fill="{SOFT}" stroke="{BORDER}"/>
</g>
<rect x="946" y="94" width="480" height="470" rx="30" fill="#5C462F" opacity="0.10"/>
<g transform="translate(930 74)">
  <rect width="480" height="470" rx="30" fill="{CARD}" stroke="{BORDER}" stroke-width="2"/>
  <rect x="24" y="24" width="432" height="224" rx="22" fill="url(#wash)"/>
  <circle cx="381" cy="74" r="76" fill="none" stroke="{PAPER}" stroke-width="4" opacity="0.36"/>
  <circle cx="381" cy="74" r="45" fill="none" stroke="{PAPER}" stroke-width="4" opacity="0.52"/>
  <path d="M397 90 L427 120" fill="none" stroke="{PAPER}" stroke-width="7" stroke-linecap="round" opacity="0.72"/>
  <text x="40" y="302" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="18" font-weight="600" letter-spacing="1.5" fill="{GOLD}">YOUR COURSE</text>
  <text x="40" y="350" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="30" font-weight="700" fill="{INK}">Sourdough from scratch</text>
  <text x="40" y="390" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="20" fill="{MUTED}">8 lessons  •  Continue learning</text>
  <rect x="40" y="422" width="294" height="9" rx="4.5" fill="{SOFT}"/>
  <rect x="40" y="422" width="176" height="9" rx="4.5" fill="{GOLD}"/>
</g>
"""
    write_text(BANNERS / "qori-banner-hero-1600x640.svg", svg_document(1600, 640, hero))

    social = f"""
<title>Qori social banner - sharing is caring</title>
<rect width="1500" height="500" fill="{INK}"/>
<path d="M1120 -115 A360 360 0 1 0 1485 425" fill="none" stroke="{DARK_GOLD}" stroke-width="55" stroke-linecap="round" opacity="0.92"/>
<path d="M1336 338 L1530 532" fill="none" stroke="{DARK_GOLD}" stroke-width="55" stroke-linecap="round" opacity="0.92"/>
<circle cx="1232" cy="138" r="112" fill="none" stroke="{PAPER}" stroke-width="2" opacity="0.10"/>
<circle cx="1232" cy="138" r="72" fill="none" stroke="{PAPER}" stroke-width="2" opacity="0.16"/>
{logo_group_svg(68, 42, 0.65, DARK_GOLD, PAPER)}
<text x="78" y="268" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="72" font-weight="700" letter-spacing="-2.5" fill="{PAPER}">sharing is caring</text>
<text x="82" y="326" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="25" fill="{DARK_MUTED}">A private classroom for people you already teach.</text>
<rect x="82" y="380" width="250" height="50" rx="25" fill="{DARK_GOLD}"/>
<text x="207" y="412" text-anchor="middle" font-family="Instrument Sans, DejaVu Sans, sans-serif" font-size="15" font-weight="700" letter-spacing="1.1" fill="{INK}">PRIVATE CLASSROOMS</text>
"""
    write_text(BANNERS / "qori-banner-social-1500x500.svg", svg_document(1500, 500, social))


def build_tokens() -> None:
    css = f"""
:root {{
  --qori-paper: {PAPER};
  --qori-card: {CARD};
  --qori-ink: {INK};
  --qori-gold: {GOLD};
  --qori-gold-hover: {GOLD_HOVER};
  --qori-muted: {MUTED};
  --qori-soft: {SOFT};
  --qori-border: {BORDER};
  --qori-input: {INPUT};
  --qori-success: {SUCCESS};
  --qori-warning: {WARNING};
  --qori-destructive: {DESTRUCTIVE};

  --background: 40 33% 97%;
  --foreground: 30 15% 12%;
  --card: 40 100% 99%;
  --card-foreground: 30 15% 12%;
  --popover: 40 100% 99%;
  --popover-foreground: 30 15% 12%;
  --primary: 36 70% 35%;
  --primary-foreground: 40 33% 97%;
  --secondary: 34 27% 93%;
  --secondary-foreground: 30 15% 12%;
  --muted: 34 27% 93%;
  --muted-foreground: 30 8% 40%;
  --accent: 38 58% 89%;
  --accent-foreground: 30 15% 12%;
  --destructive: 4 76% 40%;
  --destructive-foreground: 40 33% 97%;
  --border: 34 20% 83%;
  --input: 31 9% 50%;
  --ring: 36 70% 35%;
  --radius: 0.75rem;
}}

.dark {{
  --background: 36 13% 11%;
  --foreground: 37 53% 94%;
  --card: 35 13% 15%;
  --card-foreground: 37 53% 94%;
  --popover: 35 13% 15%;
  --popover-foreground: 37 53% 94%;
  --primary: 39 82% 65%;
  --primary-foreground: 36 13% 11%;
  --secondary: 34 12% 20%;
  --secondary-foreground: 37 53% 94%;
  --muted: 34 12% 20%;
  --muted-foreground: 33 15% 73%;
  --accent: 35 22% 24%;
  --accent-foreground: 37 53% 94%;
  --destructive: 5 69% 58%;
  --destructive-foreground: 36 13% 11%;
  --border: 34 12% 27%;
  --input: 33 10% 52%;
  --ring: 39 82% 65%;
}}
"""
    write_text(TOKENS / "qori-brand-tokens.css", css)

    token_data = {
        "meta": {"name": "Qori", "version": "1.0", "date": "2026-09-08"},
        "light": {
            "paper": PAPER,
            "card": CARD,
            "ink": INK,
            "gold": GOLD,
            "goldHover": GOLD_HOVER,
            "mutedText": MUTED,
            "softSurface": SOFT,
            "decorativeBorder": BORDER,
            "inputBoundary": INPUT,
            "success": SUCCESS,
            "warning": WARNING,
            "destructive": DESTRUCTIVE,
        },
        "dark": {
            "background": DARK_BG,
            "card": DARK_CARD,
            "text": DARK_TEXT,
            "mutedText": DARK_MUTED,
            "border": DARK_BORDER,
            "gold": DARK_GOLD,
        },
        "shape": {"radius": {"control": 10, "panel": 12, "feature": 20}, "unit": "px"},
        "spacing": {"base": 8, "unit": "px"},
        "type": {
            "ui": "Instrument Sans",
            "fallback": "Inter, system-ui, sans-serif",
            "weights": [400, 500, 600, 700],
        },
    }
    write_text(TOKENS / "qori-brand-tokens.json", json.dumps(token_data, indent=2))


def build_markdown_guide() -> None:
    guide = f"""
# Qori brand and interface guide

Version 1.0 - 8 September 2026

## Brand idea

Qori is a private classroom for people a teacher already knows. The identity should feel warm, clear, capable and human. It should never feel like a public social feed, a finance dashboard or an untouched software starter kit.

The open-circle Q represents knowledge moving between people. The opening matters: sharing is an invitation, not a closed system. The short tail keeps the mark recognisable as Q at favicon size.

"sharing is caring" is a brand line, not the product explanation. Pair it with a concrete subline such as "A private classroom for people you already teach" anywhere a visitor does not already know Qori.

## Logo files

- `logos/qori-logo-primary.svg`: default transparent lockup on paper or other light backgrounds.
- `logos/qori-logo-reverse.svg`: lockup prepared on an ink panel.
- `logos/qori-logo-mono-ink.svg`: one-colour use when colour is unavailable.
- `logos/qori-mark.svg`: standalone open-circle mark.
- `logos/qori-app-icon.svg`: gold rounded-square app icon.
- PNG exports are provided for systems that cannot use SVG.

### Logo rules

- Keep clear space equal to the stroke width of the Q mark on every side of the lockup.
- Minimum digital sizes: mark 24px; horizontal logo 96px wide.
- Use only paper, ink or Qori gold versions.
- Do not close the ring, rotate the mark, recolour individual letters, add a shadow, stretch the lockup or place it over a busy image.
- The SVG logo uses vector geometry and does not depend on a font file.

## Colour

| Token | Hex | Purpose |
|---|---:|---|
| Paper | `{PAPER}` | Main background |
| Card | `{CARD}` | Raised content surface |
| Ink | `{INK}` | Primary text and dark fields |
| Qori Gold | `{GOLD}` | Primary actions and brand identity |
| Gold Hover | `{GOLD_HOVER}` | Hover/pressed action state |
| Muted Text | `{MUTED}` | Secondary copy on paper |
| Soft Surface | `{SOFT}` | Muted panels and inactive regions |
| Decorative Border | `{BORDER}` | Non-essential panel separation |
| Input Boundary | `{INPUT}` | Essential control outline |
| Success | `{SUCCESS}` | Positive semantic state |
| Warning | `{WARNING}` | Warning semantic state |
| Destructive | `{DESTRUCTIVE}` | Destructive/error semantic state |

Qori Gold (`{GOLD}`) with Paper (`{PAPER}`) is approximately 4.66:1 and is suitable for normal button text. Gold is not the only status signal: status always includes a label or icon. Decorative borders may be subtle; essential input boundaries and focus rings must remain perceivable at 3:1.

Dark mode uses warm charcoal, not blue-black or zinc. Use `{DARK_BG}` for the page, `{DARK_CARD}` for cards, `{DARK_TEXT}` for primary text and `{DARK_GOLD}` for actions. If dark mode is exposed, test every component in it; otherwise ship the light theme alone.

## Typography

Use Instrument Sans for product UI and marketing. Recommended fallback: Inter, then the system sans-serif. Use only 400, 500, 600 and 700.

| Role | Desktop | Mobile | Weight | Line height |
|---|---:|---:|---:|---:|
| Display | 56px | 40px | 700 | 1.05 |
| Page H1 | 32px | 28px | 650-700 | 1.15 |
| Section H2 | 22px | 20px | 650 | 1.25 |
| Card title | 18px | 18px | 600 | 1.3 |
| Body | 16px | 16px | 400 | 1.55 |
| UI/label | 14px | 14px | 500-600 | 1.4 |
| Caption | 12px | 12px | 500 | 1.4 |

Do not introduce a decorative second font in the first design pass. Warmth comes from colour, spacing, course objects and language.

## Layout and shape

- Base spacing unit: 8px. Use 4px only for tight icon/text relationships.
- Control radius: 10px. Panel radius: 12px. Feature/cover radius: 20px.
- Keep one aligned page header: H1, one-line context, one ranked primary action.
- Use a comfortable desktop content width; do not stretch forms to fill a wide panel.
- At 360px the sidebar becomes the existing drawer. No page-level horizontal scrolling.
- Primary mobile targets are at least 44px high.
- Shadows are quiet and rare. Borders and space define the hierarchy.

## Course identity

`CourseCover` is the shared identity primitive. Generate its wash from an immutable course id, not the mutable title. Stay in the paper/gold range; avoid random rainbow covers and empty grey rectangles.

Use separate compositions for separate jobs:

- Studio course card: status, lesson count, price and edit/open action.
- Learning course card: classroom/teacher, progress, next lesson and Continue/Start.
- Public course hero: teacher/classroom, summary, real contents, known duration, price and enrolment state.

Do not make the public page a studio card enlarged. Do not add internal draft language to learner/public surfaces. A progress bar includes text such as "3 of 8 lessons" and an accessible value.

## Voice

Qori sounds like a calm, capable teaching partner. Use plain verbs and name the result.

| Prefer | Avoid |
|---|---|
| Create course | Submit |
| Publish course | Continue |
| Invite student | Add contact |
| Your classroom | Workspace (customer-facing) |
| 3 of 8 lessons complete | 38% (on its own) |
| We could not publish this course. Add one lesson, then try again. | Something went wrong |

Do not use jokes to fill empty states, invent activity, or promise unavailable features. "sharing is caring" should never stand alone as the value proposition.

## UX rules

1. Objects before metrics: show the course before aggregate counts.
2. One next action: use `TeachDigest.nextAction` and land at the completing control.
3. Blocking and permission states outrank encouragement.
4. Success changes the visible object and offers the next useful action; it is not only a toast.
5. Empty states occupy the future object's space and show only actions the role/plan permits.
6. Every changed surface covers loading, empty, populated, failure, success, permission and locked states.
7. One logical H1, visible focus, keyboard operation, associated form errors, 200% zoom and 360px review are part of done.

## Banner files

- `banners/qori-banner-hero-1600x640.*`: light product/website hero treatment.
- `banners/qori-banner-social-1500x500.*`: dark social/profile cover treatment.

Both use course geometry and the open circle rather than stock photos. Replace copy for a specific campaign, but preserve the logo safe area, warm palette and single-message hierarchy.
"""
    write_text(GUIDELINES / "qori-brand-guidelines.md", guide)


def export_svg(svg_path: Path, png_path: Path, width: int | None = None, height: int | None = None) -> None:
    command = ["inkscape", str(svg_path), "--export-background-opacity=0", f"--export-filename={png_path}"]
    if width:
        command.append(f"--export-width={width}")
    if height:
        command.append(f"--export-height={height}")
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def export_png_assets() -> None:
    export_svg(LOGOS / "qori-mark.svg", LOGOS / "qori-mark-512.png", width=512)
    export_svg(LOGOS / "qori-app-icon.svg", LOGOS / "qori-app-icon-512.png", width=512)
    export_svg(LOGOS / "qori-logo-primary.svg", LOGOS / "qori-logo-primary-1200.png", width=1200)
    export_svg(LOGOS / "qori-logo-reverse.svg", LOGOS / "qori-logo-reverse-1200.png", width=1200)
    export_svg(BANNERS / "qori-banner-hero-1600x640.svg", BANNERS / "qori-banner-hero-1600x640.png", width=1600)
    export_svg(BANNERS / "qori-banner-social-1500x500.svg", BANNERS / "qori-banner-social-1500x500.png", width=1500)


def register_fonts() -> tuple[str, str]:
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("QoriSans", regular))
    pdfmetrics.registerFont(TTFont("QoriSansBold", bold))
    return "QoriSans", "QoriSansBold"


def hex_color(value: str):
    from reportlab.lib.colors import HexColor

    return HexColor(value)


def wrap_lines(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class BrandPdf:
    def __init__(self, path: Path):
        self.path = path
        self.width, self.height = landscape(A4)
        self.c = canvas.Canvas(str(path), pagesize=(self.width, self.height))
        self.c.setTitle("Qori Brand and Interface Guide")
        self.c.setAuthor("Qori")
        self.c.setSubject("Logo, colour, typography, interface and UX guidelines")
        self.c.setKeywords("Qori, brand, logo, design system, interface, UX")
        self.c.setCreator("Qori brand kit generator")
        self.regular, self.bold = register_fonts()
        self.page_no = 0

    def text(self, x: float, y: float, value: str, size: float = 12, color: str = INK, bold: bool = False):
        self.c.setFont(self.bold if bold else self.regular, size)
        self.c.setFillColor(hex_color(color))
        self.c.drawString(x, y, value)

    def wrapped(
        self,
        x: float,
        y: float,
        value: str,
        width: float,
        size: float = 11,
        leading: float | None = None,
        color: str = MUTED,
        bold: bool = False,
        max_lines: int | None = None,
    ) -> float:
        leading = leading or size * 1.45
        lines = wrap_lines(value, self.bold if bold else self.regular, size, width)
        if max_lines:
            lines = lines[:max_lines]
        for line in lines:
            self.text(x, y, line, size, color, bold)
            y -= leading
        return y

    def footer(self, dark: bool = False):
        color = DARK_MUTED if dark else MUTED
        self.text(42, 24, "Qori brand & interface guide  /  v1.0", 7.5, color)
        label = f"{self.page_no:02d}"
        w = pdfmetrics.stringWidth(label, self.bold, 8)
        self.text(self.width - 42 - w, 24, label, 8, color, True)

    def start(self, title: str | None = None, dark: bool = False, eyebrow: str | None = None):
        self.page_no += 1
        self.c.setFillColor(hex_color(DARK_BG if dark else PAPER))
        self.c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        if eyebrow:
            self.text(44, self.height - 48, eyebrow.upper(), 8.5, DARK_GOLD if dark else GOLD, True)
        if title:
            self.text(44, self.height - 82, title, 25, DARK_TEXT if dark else INK, True)
        self.footer(dark)

    def finish_page(self):
        self.c.showPage()

    def card(self, x: float, y: float, w: float, h: float, fill: str = CARD, stroke: str = BORDER, radius: float = 12):
        self.c.setFillColor(hex_color(fill))
        self.c.setStrokeColor(hex_color(stroke))
        self.c.setLineWidth(0.8)
        self.c.roundRect(x, y, w, h, radius, fill=1, stroke=1)

    def pill(self, x: float, y: float, text: str, fill: str = GOLD, text_color: str = PAPER):
        width = pdfmetrics.stringWidth(text, self.bold, 8) + 22
        self.c.setFillColor(hex_color(fill))
        self.c.roundRect(x, y, width, 24, 12, fill=1, stroke=0)
        self.text(x + 11, y + 7.5, text, 8, text_color, True)
        return width

    def image(self, path: Path, x: float, y: float, w: float, h: float, preserve: bool = True):
        self.c.drawImage(ImageReader(str(path)), x, y, width=w, height=h, preserveAspectRatio=preserve, mask="auto", anchor="c")

    def draw_mark(self, x: float, y: float, size: float, color: str = GOLD, width: float | None = None):
        width = width or max(2.0, size * 0.085)
        self.c.setStrokeColor(hex_color(color))
        self.c.setLineWidth(width)
        self.c.setLineCap(1)
        inset = size * 0.19
        self.c.arc(x + inset, y + inset, x + size - inset, y + size - inset, startAng=38, extent=286)
        self.c.line(x + size * 0.63, y + size * 0.37, x + size * 0.82, y + size * 0.18)

    def build(self) -> None:
        self.cover_page()
        self.idea_page()
        self.logo_page()
        self.colour_page()
        self.type_page()
        self.ui_page()
        self.course_page()
        self.voice_page()
        self.handoff_page()
        self.c.save()

    def cover_page(self):
        self.start(dark=True)
        self.draw_mark(self.width - 280, self.height - 285, 315, DARK_GOLD, 30)
        self.image(LOGOS / "qori-logo-reverse-1200.png", 42, self.height - 138, 210, 82)
        self.text(48, 280, "Brand &", 45, PAPER, True)
        self.text(48, 230, "interface guide", 45, PAPER, True)
        self.text(50, 176, "sharing is caring", 18, DARK_GOLD, True)
        self.wrapped(50, 143, "A warm, object-first identity for private classrooms and the people who make them feel alive.", 390, 12, 18, DARK_MUTED)
        self.text(50, 67, "VERSION 1.0  /  8 SEPTEMBER 2026", 8, DARK_MUTED, True)
        self.finish_page()

    def idea_page(self):
        self.start("A classroom, not a dashboard", eyebrow="01 / Brand idea")
        self.text(44, 466, "Qori should feel warm, clear, capable and human.", 18, GOLD, True)
        self.wrapped(44, 431, "The product is for people a teacher already knows. Its identity should help someone begin and continue a real course - never imitate a public feed, a finance tool or an untouched starter kit.", 720, 12, 18, INK)
        cards = [
            ("Warm", "Paper, ink and grounded gold. Friendly without becoming childish."),
            ("Clear", "One next action, plain verbs and honest states. No decorative noise."),
            ("Alive", "Courses, progress and people appear before meters and abstract totals."),
        ]
        for i, (title, body) in enumerate(cards):
            x = 44 + i * 254
            self.card(x, 195, 228, 164)
            self.draw_mark(x + 18, 302, 35, GOLD, 3.2)
            self.text(x + 20, 274, title, 17, INK, True)
            self.wrapped(x + 20, 245, body, 188, 10.2, 15, MUTED)
        self.text(44, 144, "THE LINE", 8, GOLD, True)
        self.text(44, 110, "sharing is caring", 26, INK, True)
        self.wrapped(342, 118, "Treat this as a memorable brand line, not the product explanation. Pair it with: A private classroom for people you already teach.", 420, 10.5, 15, MUTED)
        self.finish_page()

    def logo_page(self):
        self.start("The open-circle Q", eyebrow="02 / Logo system")
        self.wrapped(44, 468, "An open learning loop: knowledge moves between people instead of being sealed away. The tail keeps the form recognisable as Q at small sizes.", 710, 11, 16, MUTED)
        self.card(44, 285, 354, 145)
        self.image(LOGOS / "qori-logo-primary-1200.png", 73, 319, 295, 78)
        self.card(420, 285, 377, 145, fill=INK, stroke=INK)
        self.image(LOGOS / "qori-logo-reverse-1200.png", 454, 319, 300, 78)
        self.text(44, 263, "PRIMARY ON PAPER", 7.5, MUTED, True)
        self.text(420, 263, "REVERSE ON INK", 7.5, MUTED, True)

        self.card(44, 86, 168, 148)
        self.image(LOGOS / "qori-app-icon-512.png", 83, 115, 90, 90)
        self.text(91, 99, "APP ICON", 7.5, MUTED, True)

        self.text(248, 216, "Clear space", 14, INK, True)
        self.wrapped(248, 191, "Keep at least one mark-stroke of breathing room on every side.", 220, 9.5, 14, MUTED)
        self.c.setStrokeColor(hex_color(GOLD))
        self.c.setDash(3, 3)
        self.c.rect(502, 110, 116, 116, fill=0, stroke=1)
        self.c.setDash()
        self.draw_mark(520, 128, 80, GOLD, 7)
        self.text(647, 208, "Minimum digital size", 14, INK, True)
        self.text(647, 178, "Mark 24px", 10, MUTED)
        self.text(647, 157, "Lockup 96px wide", 10, MUTED)
        self.text(647, 126, "Never stretch, rotate, shadow", 9.5, DESTRUCTIVE, True)
        self.text(647, 108, "or recolour individual letters.", 9.5, DESTRUCTIVE, True)
        self.finish_page()

    def colour_page(self):
        self.start("Paper, ink and one grounded gold", eyebrow="03 / Colour")
        self.wrapped(44, 468, "Gold carries identity and action. It is not body copy, a rainbow chart system or the only way to communicate status.", 720, 11, 16, MUTED)
        swatches = [
            ("Paper", PAPER, INK),
            ("Card", CARD, INK),
            ("Ink", INK, PAPER),
            ("Qori Gold", GOLD, PAPER),
            ("Soft", SOFT, INK),
            ("Muted text", MUTED, PAPER),
        ]
        for i, (name, color, text_color) in enumerate(swatches):
            x = 44 + (i % 3) * 253
            y = 302 - (i // 3) * 132
            self.c.setFillColor(hex_color(color))
            self.c.roundRect(x, y, 227, 104, 12, fill=1, stroke=0)
            self.text(x + 15, y + 53, name, 12, text_color, True)
            self.text(x + 15, y + 27, color, 9, text_color)
        self.text(44, 137, "CONTRAST", 8, GOLD, True)
        self.text(44, 111, "Gold / Paper", 12, INK, True)
        self.text(174, 111, "4.66:1  AA normal text", 11, SUCCESS, True)
        self.text(423, 111, "Input boundaries + focus", 12, INK, True)
        self.text(632, 111, "3:1 minimum", 11, SUCCESS, True)
        self.wrapped(44, 80, "Decorative borders may be quiet. An input cannot rely on a low-contrast line alone to look interactive. Status always includes words or an icon.", 720, 9.5, 14, MUTED)
        self.finish_page()

    def type_page(self):
        self.start("Instrument Sans, with restraint", eyebrow="04 / Typography")
        self.text(44, 435, "sharing is caring", 47, INK, True)
        self.text(47, 399, "DISPLAY / 56 DESKTOP / 40 MOBILE / 700", 8, GOLD, True)
        specimens = [
            ("Page title", "Build a course people finish", 27, "700 / 1.15"),
            ("Section", "Pick up where you left off", 19, "650 / 1.25"),
            ("Body", "A private classroom for people you already teach.", 12, "400 / 1.55"),
            ("UI label", "PUBLISH COURSE", 9, "600 / 1.4"),
        ]
        y = 335
        for name, sample, size, spec in specimens:
            self.text(44, y + 10, name.upper(), 7.5, MUTED, True)
            self.text(160, y, sample, size, INK, size >= 19 or name == "UI label")
            self.text(673, y + 4, spec, 8.5, MUTED)
            self.c.setStrokeColor(hex_color(BORDER))
            self.c.line(44, y - 22, 797, y - 22)
            y -= 72
        self.pill(44, 69, "NO SECOND FONT")
        self.wrapped(189, 83, "Warmth comes from colour, spacing, course objects and language - not a decorative typeface added during redesign week.", 570, 9.5, 14, MUTED)
        self.finish_page()

    def ui_page(self):
        self.start("Objects before metrics", eyebrow="05 / Layout & UI")
        self.wrapped(44, 468, "One H1, one ranked action, one content rhythm. Show the course and the next useful step before counts about the system.", 720, 11, 16, MUTED)
        self.card(44, 103, 488, 315)
        self.text(68, 380, "Good morning, Rita", 22, INK, True)
        self.text(68, 355, "Your classroom is ready for its first course.", 9.5, MUTED)
        self.card(68, 217, 440, 111, fill="#FBF1DE", stroke="#E7CAA0")
        self.text(88, 296, "NEXT STEP", 7.5, GOLD, True)
        self.text(88, 267, "Name your first course", 17, INK, True)
        self.text(88, 243, "Create the object first. Details can come later.", 9, MUTED)
        self.pill(354, 252, "CREATE COURSE")
        self.text(68, 187, "Courses", 13, INK, True)
        self.c.setFillColor(hex_color(SOFT))
        self.c.roundRect(68, 127, 136, 42, 10, fill=1, stroke=0)
        self.text(82, 143, "Your course appears here", 7.5, MUTED)

        self.text(567, 394, "8px", 25, GOLD, True)
        self.text(632, 399, "base spacing", 10, MUTED)
        self.text(567, 345, "10 / 12 / 20", 20, INK, True)
        self.text(567, 322, "control / panel / feature radius", 9, MUTED)
        self.text(567, 278, "360px", 20, INK, True)
        self.text(639, 282, "minimum review width", 9, MUTED)
        self.text(567, 232, "44px", 20, INK, True)
        self.text(627, 236, "primary mobile target", 9, MUTED)
        self.text(567, 184, "Rule", 8, GOLD, True)
        self.wrapped(567, 161, "A disabled action explains why. An empty state only offers actions the current role and plan permit.", 220, 9.5, 14, MUTED)
        self.finish_page()

    def course_page(self):
        self.start("One identity, three jobs", eyebrow="06 / Course surfaces")
        self.wrapped(44, 468, "Share CourseCover and visual language. Compose studio, learner and public surfaces around the question each audience is asking.", 720, 11, 16, MUTED)
        labels = [
            ("STUDIO", "What needs work?", "Draft  /  8 lessons  /  $89", "OPEN COURSE"),
            ("LEARNING", "Where do I continue?", "3 of 8 lessons complete", "CONTINUE"),
            ("PUBLIC", "Should I enrol?", "Rita's classroom  /  8 lessons", "ENROL"),
        ]
        for i, (eyebrow, title, detail, action) in enumerate(labels):
            x = 44 + i * 254
            self.card(x, 160, 228, 255)
            self.c.setFillColor(hex_color("#D9A247" if i != 1 else "#B67C29"))
            self.c.roundRect(x + 14, 290, 200, 108, 14, fill=1, stroke=0)
            self.draw_mark(x + 147, 315, 52, PAPER, 4)
            self.text(x + 18, 268, eyebrow, 7.5, GOLD, True)
            self.text(x + 18, 240, title, 13, INK, True)
            self.wrapped(x + 18, 217, detail, 188, 8.5, 12, MUTED)
            if i == 1:
                self.c.setFillColor(hex_color(SOFT))
                self.c.roundRect(x + 18, 185, 188, 6, 3, fill=1, stroke=0)
                self.c.setFillColor(hex_color(GOLD))
                self.c.roundRect(x + 18, 185, 70, 6, 3, fill=1, stroke=0)
            self.text(x + 18, 171, action, 7.5, GOLD, True)
        self.text(44, 122, "COVER RECIPE", 8, GOLD, True)
        self.wrapped(44, 97, "Derive a stable warm wash from immutable course id. The cover is decorative beside a visible title. No random rainbow, no grey void and no image upload in this pass.", 720, 10, 14.5, MUTED)
        self.finish_page()

    def voice_page(self):
        self.start("Calm, direct and useful", eyebrow="07 / Voice & states")
        self.wrapped(44, 468, "Qori sounds like a capable teaching partner. Buttons name the result. Errors explain recovery. Success visibly changes the object.", 720, 11, 16, MUTED)
        self.text(44, 418, "PREFER", 8, SUCCESS, True)
        self.text(430, 418, "AVOID", 8, DESTRUCTIVE, True)
        rows = [
            ("Create course", "Submit"),
            ("Invite student", "Add contact"),
            ("Your classroom", "Workspace"),
            ("3 of 8 lessons complete", "38% on its own"),
            ("Add one lesson, then try again.", "Something went wrong"),
        ]
        y = 383
        for left, right in rows:
            self.text(44, y, left, 12, INK, True)
            self.text(430, y, right, 12, MUTED)
            self.c.setStrokeColor(hex_color(BORDER))
            self.c.line(44, y - 17, 797, y - 17)
            y -= 52
        self.card(44, 73, 753, 72, fill="#FBF1DE", stroke="#E7CAA0")
        self.text(62, 117, "STATE PRIORITY", 7.5, GOLD, True)
        self.text(62, 91, "Blocked or paused  >  permission  >  next action  >  recent objects  >  metrics", 11, INK, True)
        self.finish_page()

    def handoff_page(self):
        self.start("The handoff", eyebrow="08 / Build checklist", dark=True)
        self.text(44, 466, "Ship one coherent week, then stop.", 22, DARK_GOLD, True)
        checklist = [
            "Use the supplied SVG logo; do not redraw the mark per screen.",
            "Load qori-brand-tokens.css, then map existing shadcn variables.",
            "Use CourseCover as the shared identity primitive, not one universal card.",
            "Route each primary action directly to the completing control.",
            "Review empty, populated, failure, permission and plan-locked states.",
            "Check 360px, 768px, desktop, keyboard, focus, contrast and 200% zoom.",
            "Keep sharing is caring paired with a concrete product explanation.",
            "Run the existing quality gate and creator/learner walkthroughs.",
        ]
        y = 412
        for item in checklist:
            self.c.setStrokeColor(hex_color(DARK_GOLD))
            self.c.setLineWidth(1.6)
            self.c.circle(52, y + 4, 6, fill=0, stroke=1)
            self.c.line(49, y + 4, 52, y + 1)
            self.c.line(52, y + 1, 57, y + 8)
            self.wrapped(72, y, item, 690, 10.5, 15, DARK_TEXT)
            y -= 42
        self.image(LOGOS / "qori-logo-reverse-1200.png", 44, 54, 180, 70)
        self.text(591, 82, "sharing is caring", 17, DARK_GOLD, True)
        self.text(591, 61, "A private classroom for people you already teach.", 8.5, DARK_MUTED)
        self.finish_page()


def build_pdf() -> Path:
    pdf_path = PDF_OUTPUT / "Qori-Brand-and-Interface-Guide.pdf"
    BrandPdf(pdf_path).build()
    shutil.copy2(pdf_path, GUIDELINES / pdf_path.name)
    return pdf_path


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size)


def contain(img: Image.Image, box: tuple[int, int], background=(250, 248, 245, 255), padding: int = 28) -> Image.Image:
    target = Image.new("RGBA", box, background)
    copy = img.convert("RGBA")
    copy.thumbnail((box[0] - 2 * padding, box[1] - 2 * padding), Image.Resampling.LANCZOS)
    x = (box[0] - copy.width) // 2
    y = (box[1] - copy.height) // 2
    target.alpha_composite(copy, (x, y))
    return target


def build_preview() -> Path:
    preview = Image.new("RGB", (1800, 1460), PAPER)
    draw = ImageDraw.Draw(preview)
    draw.text((70, 55), "Qori brand kit", fill=INK, font=font(52, True))
    draw.text((72, 122), "Warm paper. Grounded gold. Courses before metrics.", fill=MUTED, font=font(23))

    primary = Image.open(LOGOS / "qori-logo-primary-1200.png")
    reverse = Image.open(LOGOS / "qori-logo-reverse-1200.png")
    app_icon = Image.open(LOGOS / "qori-app-icon-512.png")
    hero = Image.open(BANNERS / "qori-banner-hero-1600x640.png")
    social = Image.open(BANNERS / "qori-banner-social-1500x500.png")

    panel1 = contain(primary, (700, 250), background=(255, 253, 248, 255))
    panel2 = contain(reverse, (700, 250), background=(35, 31, 26, 255))
    preview.paste(panel1.convert("RGB"), (70, 190))
    preview.paste(panel2.convert("RGB"), (820, 190))
    icon_panel = contain(app_icon, (210, 210), background=(241, 236, 229, 255), padding=25)
    preview.paste(icon_panel.convert("RGB"), (1520, 210))

    hero_panel = contain(hero, (1120, 520), background=(241, 236, 229, 255), padding=20)
    preview.paste(hero_panel.convert("RGB"), (70, 500))

    social_panel = contain(social, (560, 520), background=(35, 31, 26, 255), padding=20)
    preview.paste(social_panel.convert("RGB"), (1240, 500))

    swatches = [PAPER, INK, GOLD, GOLD_HOVER, MUTED, SOFT, SUCCESS, DESTRUCTIVE]
    x = 70
    for color in swatches:
        draw.rounded_rectangle((x, 1090, x + 180, 1240), radius=18, fill=color)
        tc = PAPER if color in (INK, GOLD, GOLD_HOVER, MUTED, SUCCESS, DESTRUCTIVE) else INK
        draw.text((x + 18, 1197), color, fill=tc, font=font(17, True))
        x += 210
    draw.text((70, 1322), "Open-circle Q / deterministic course washes / one clear next action", fill=INK, font=font(25, True))
    draw.text((70, 1370), "Source SVG, PNG exports, implementation tokens and full PDF guide are included.", fill=MUTED, font=font(19))

    path = PREVIEW_OUTPUT / "Qori-Brand-Kit-Preview.png"
    preview.save(path, quality=95)
    return path


def build_readme() -> None:
    readme = """
# Qori brand kit

This kit translates the Qori product direction into a small, implementation-ready visual system.

## Start here

1. Read `guidelines/Qori-Brand-and-Interface-Guide.pdf` for the visual overview.
2. Use `logos/qori-logo-primary.svg` for normal light surfaces.
3. Use `logos/qori-logo-reverse.svg` on ink/dark surfaces.
4. Map `tokens/qori-brand-tokens.css` into the existing shadcn variables.
5. Use the banner SVGs as editable source; PNGs are convenience exports.

## Contents

- `logos/`: editable vector logo, mark, app icon, reverse and monochrome variants, plus PNG exports.
- `banners/`: 1600x640 light hero and 1500x500 dark social/profile banner in SVG and PNG.
- `tokens/`: CSS variables and JSON token reference.
- `guidelines/`: PDF and Markdown design/UX guide.

The logo geometry is vector-based and has no font dependency. Banner text uses Instrument Sans when available and falls back to a system sans-serif. The product UI should load Instrument Sans as specified in the guide.
"""
    write_text(KIT / "README.md", readme)


def copy_source() -> None:
    shutil.copy2(Path(__file__), KIT / "build_qori_brand_kit.py")


def build_zip() -> Path:
    zip_path = OUTPUT / "Qori-Brand-Kit.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(KIT.rglob("*")):
            if path.is_file():
                archive.write(path, Path("Qori-Brand-Kit") / path.relative_to(KIT))
    return zip_path


def main() -> None:
    ensure_dirs()
    build_logo_assets()
    build_banner_assets()
    build_tokens()
    build_markdown_guide()
    export_png_assets()
    pdf_path = build_pdf()
    preview_path = build_preview()
    build_readme()
    copy_source()
    zip_path = build_zip()
    print(json.dumps({
        "pdf": str(pdf_path),
        "preview": str(preview_path),
        "zip": str(zip_path),
        "kit": str(KIT),
    }, indent=2))


if __name__ == "__main__":
    main()
