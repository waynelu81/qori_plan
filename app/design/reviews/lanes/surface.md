# Lane: surface

**Asks.** Does every screen look like the same product, made on purpose, by the
same people?

**Needs.** A renderer. The screenshot run is enough.

**Evidence.** A full run, both widths, both themes.

```bash
php artisan qori:design-review
```

## Checks

- **One token set.** Every colour, radius and shadow resolves through the
  semantic tokens in `resources/css/app.css`. No page-local hex, no leftover
  zinc, no shadcn default that nobody chose.
- **One shell.** Product chrome comes from `components/shell/`. A page that
  hand-rolls `rounded-xl border p-4` is the "two UIs" problem the redesign brief
  diagnosed, and it reads as somebody stopping halfway.
- **One type scale.** Page titles at the display size, body at 14–16px, one H1
  per page, headings that do not skip a level to get a size.
- **One rhythm.** Content width, gutters and vertical spacing agree between
  pages. A form does not stretch to a desktop panel's full width because the
  space exists.
- **The mark.** Open ring on gold, wordmark beside it, and the same treatment
  everywhere including the error pages, which inline their own copy of it.
- **Objects before meters.** A creator with one Series sees the Series before it
  sees a count of Series. Six zeros is worse than one sentence and a button.
- **Admin is allowed to differ**, and only admin. `AdminLayout` is deliberately
  distinct (§24.6); the rest of the product is not.

## What it cannot see

- Whether the design is _good_. This lane finds inconsistency, which is a
  different thing and the only one a screenshot can settle.
- Anything that only appears after an interaction — a menu, a dialog, a hover
  state. Those belong to [journey](journey.md) and [keyboard](keyboard.md).
- Rendering in a browser that is not Chromium.
