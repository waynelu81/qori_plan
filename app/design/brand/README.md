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

System email composition is specified in
[`../planning/ui-system-email.md`](../planning/ui-system-email.md): a shared
logo-led layout, message variants, table rules and unsubscribe treatment. It is
a proposed design, not evidence of email-client compatibility. The website and
social banners in this kit are not default transactional-email headers.

The logo geometry is vector-based and has no font dependency. Banner text uses Instrument Sans when available and falls back to a system sans-serif. The product UI should load Instrument Sans as specified in the guide.
