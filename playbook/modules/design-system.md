# Module: design system

**What it is.** The tokens, states and repeated shapes that make a product look
like one product, and the review process that keeps it that way as screens
multiply.

**Done when.** No surface is unstyled, colour and type come from tokens rather
than from each screen, every interactive state is defined, and a review pass
can be run on demand rather than by eye.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| Where do brand tokens live? | One source, exported to both CSS and JSON | Two hand-kept copies disagree within a month. |
| Are screenshots committed? | **No** | A few hundred images of every screen, twice a week, helps nobody a year later. The review has to stand on its own in words. |
| How is a review run? | A command that drives a real browser over every screen, at both widths and both themes, against a fixture | By eye, at one width, on the reviewer's machine, is how contrast failures ship. |
| Who owns a review? | Each review "world" has its own owner | Otherwise every finding lands on one person and none are actioned. |
| Is the identifying part of a title preserved when space runs out? | Yes | Truncating from the end makes twenty items read identically on a phone. |

## Build order

1. **Tokens**, one source, exported to the formats the code needs.
2. **The shell** — one layout per audience, with a visually distinct one for
   staff so nobody confuses the two. Needs 1.
3. **Error and auth pages in the product's own palette**, with the full
   lockup — these are the pages people see when something has gone wrong, and
   they are the most often left as framework defaults. Needs 1, 2.
4. **Form states**: long-form fields as textareas with remaining room shown,
   tab order that does not jump, one heading per page.
5. **The review command**: every screen, both widths, both themes, into a local
   run directory named by date and commit so two runs compare. Needs 2.
6. **Review lanes with owners**, each ending in what it cannot see. Needs 5.

## Rules that bite

- **Both widths and both themes, or the pass is not a pass.**
- **Keep the run directories local**; name them by date and commit.
- **A review lane states what it cannot see**, so the gap is visible rather
  than assumed covered.

## Native contract

**Not proven.** Tokens exported as JSON are the handover to native; the CSS
export is web-only. Type scale and spacing will not transfer directly.

## Traps

| Symptom | Cause |
| --- | --- |
| "The error page is the framework's default" | Nobody owns the pages that only appear on failure. |
| "Contrast fails only in dark mode on mobile" | A review pass run at one width in one theme. |
| "Every item in the list reads the same on a phone" | Truncating titles from the end. |
| "The repository is enormous" | Committed screenshots. |

## Proven / Not proven

**Proven**: tokens; error and auth pages in the palette; the mobile and
contrast pass; the browser-driven review command with per-lane owners.

**Not proven**: the redesign is not finished — unstyled surfaces remain, which
is why this stream blocks release.

## Source

Qori tasks `T-001`, `T-002`, `T-003`, `T-030`, `T-033` to `T-039`, `T-066`.
Stream `design`.
