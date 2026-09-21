# Lane: responsive

**Asks.** Does it work at the widths people actually use, and at the zoom levels
they actually set?

**Needs.** A renderer that can be resized. Two of the four checks below also need
a real device or a person, and this lane says which.

**Evidence.** Every run captures 390px and 1440px. 768px and 200% zoom are not
in the harness and have to be driven by hand.

```bash
php artisan qori:design-review --viewport=mobile
```

## Checks

- **No page-level horizontal scroll at 360px.** `scrollWidth - clientWidth` is 0.
  `T-003` measured this across sixteen pages and it is the check most likely to
  regress silently, because a developer's window is never that narrow.
- **Three widths, not two.** The contract names 360, 768 and desktop. 768 is the
  one nothing checks: it is where a sidebar collapses and a two-column layout has
  to decide what it is.
- **Wide content scrolls inside its own container.** A table or a code block
  that forces the page sideways is a finding; the same content in an
  `overflow-x: auto` box is not.
- **44px touch targets** for primary mobile controls.
- **Usable at 200% zoom.** Not the same as narrow: zoom reflows text without
  changing the viewport's device width, and layouts pinned to `vw` fail here and
  nowhere else.
- **The Peer player** gets this pass whatever else is skipped. It is a core
  journey and it is the surface most likely to be opened on a phone.

## What it cannot see

- **Real devices.** Emulation gets geometry right and gets touch, scroll inertia,
  safe areas, on-screen keyboards and address-bar collapse wrong. A finding
  about any of those needs a phone.
- **768px and 200% zoom** until somebody adds them to the harness or drives them
  by hand. Say which, in the pass.
- **Orientation change**, and what happens to a dialog that was open when it
  happened.
