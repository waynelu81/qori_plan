---
id: T-193
title: The home page shows a Series
stream: design
status: draft
owner: unassigned
estimate: S
depends: T-190
blocks: none
---

# T-193 — The home page shows a Series

> **Draft.** Written on 23 September 2026 from
> [the Kajabi note](../../design/competitor-kajabi.md), proposal 6, at the
> owner's word ("probably need to show it, can be a design review task"). The
> composition is a design pass's to propose, which is what holds this in
> draft.

## Why

`Welcome.vue` is a headline, two sentences and two buttons. A visitor who has
not heard of Qori decides there, and never sees the object the whole product is
about. The brand guide's first UX rule is objects before metrics, and the brand
kit's hero banner already draws a Series in course geometry; Kajabi's hero is
a device frame of the product. Afterwards the home page shows one Series — the
public hero composition from the brand guide, or the banner's drawn one — so
the claim line has a picture.

After `T-190`, which edits the same file.

## Decisions taken to make this specifiable

To be taken from the design pass below. Two are already the brand guide's:
the Series shown is one of its three compositions, not a studio card enlarged,
and nothing in it invents activity — an example is labelled as one.

## Preconditions

**Data this task verifies against:** none; the page reads nothing.

**Equipment:** a browser at 390px and 1440px, light and dark.

## Scope

**In:**

- One Series on the home page, in the composition the pass chooses, at both
  widths and both themes.

**Out:**

- Any change to the words `T-190` lands; a `PublicHeader` (`T-104`).
- A screenshot of the real product, which would date the day it is taken.

## Files

| Path                             | Change | Notes                                     |
| -------------------------------- | ------ | ----------------------------------------- |
| `resources/js/pages/Welcome.vue` | edit   | Composes the Series                       |
| `resources/js/components/marketing/*.vue` | new | The component, named by the pass        |

Flows: none — a marketing page.

## Database

None.

## Code

To be settled when ready, from the pass.

## Copy

To be settled when ready; an example Series title and its label, inline as
the rest of the page is (`T-048`'s reasoning), until `T-006`.

## Routes

None.

## Tests

To be written when ready: the page renders at both widths in the design-review
run (`020-home`), and no product noun is hardcoded in the new component.

## Acceptance

- [ ] A guest at `/` sees one Series beside the claim, at 390px and 1440px,
      light and dark, with no horizontal scroll
- [ ] The example is labelled as one and invents no activity
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- A design pass proposes the composition: the public Series hero from the
  brand guide with example content, or the brand kit's drawn banner, and where
  it sits against the headline at 390px. (the design stream's)
- Whether the example Series carries a real-looking title or a labelled
  placeholder. (the owner's)

## Re-scope log

None.

## Notes

None.
