# Lane: contrast

**Asks.** Can it be read, in both themes, by somebody who is not looking at a
calibrated screen in a dark room?

**Needs.** The stylesheet. This is the one lane that is mostly already a test.

**Evidence.** `tests/Feature/PaletteContrastTest.php` — six tests, 232
assertions, parsed from the stylesheet rather than eyeballed. Run the gate.

```bash
php artisan test --filter=PaletteContrastTest
```

## Checks

- **4.5:1 for normal text, 3:1 for large text**, in both themes.
- **3:1 for focus indicators and essential component boundaries** against
  whatever sits next to them. An input that relies on a decorative low-contrast
  border to look interactive fails this, and a decorative card border does not.
- **Status never relies on colour alone.** Draft, ready, failed and complete
  each carry a label or an icon as well as a hue. This one is not a stylesheet
  property and has to be read off the screenshots.
- **The error pages match their source.** `resources/views/errors/layout.blade.php`
  duplicates six palette values because it must render without the build, and a
  test compares the inlined hex to the tokens. Three of them had already drifted
  by the time that test was written.
- **Gold is an action colour**, not body copy and not the only signal.

## What it cannot see

- **Composited contrast.** The test reads token pairs. Text over an image, over
  a gradient, or over a translucent overlay is computed at render time and
  nothing here checks it.
- **Anything a screenshot renders but the stylesheet does not declare** —
  including inline styles and anything a third-party embed brings with it.
- **Colour vision deficiency.** Passing 4.5:1 says nothing about whether two
  statuses are distinguishable to somebody who cannot separate the hues. Reading
  the status-label check above is the substitute, and it is a weak one.
