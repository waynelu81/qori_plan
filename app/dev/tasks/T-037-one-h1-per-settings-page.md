---
id: T-037
title: One heading per settings page, not two
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-037 — One heading per settings page, not two

## Why

`R-002` F-7. The settings layout renders `PageHeader`, which emits an `<h1>`
reading "User settings". Each settings page then adds its own
`<h1 class="sr-only">` — "Profile settings", "Appearance settings", "Security
settings". Every settings page therefore has two level-one headings, one of them
invisible.

It looks fine, which is why it survived: the finding is source evidence and does
not appear in a screenshot. To anyone navigating by headings it reads as two
documents stacked, and the specific page context is announced as a peer of the
section rather than inside it.

## Decisions taken to make this specifiable

**Keep the layout's `<h1>` and demote the page's.** The layout's is the visible
one and names the section a reader can see. The page-level heading exists to
supply the specific context a visually hidden reader would otherwise lack, which
is a real need — so it becomes an `<h2>` rather than disappearing. Removing it
would trade one defect for a worse one.

**Do not make it visible.** The visible design is not in question here and
`R-002` says so; this is a semantics fix, not a layout change.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The three settings pages carrying a second `<h1>`.
- A test that stops a fourth being added.

**Out:**

- The visible header, which is correct.
- Heading structure anywhere else in the product. If the same shape exists on
  other pages this test will say so, and fixing those is a separate task with
  its own reading.
- `T-022`, which owns keyboard and focus as observed properties.

## Files

| Path                                         | Change | Notes       |
| -------------------------------------------- | ------ | ----------- |
| `resources/js/pages/settings/Profile.vue`    | edit   | `h1` → `h2` |
| `resources/js/pages/settings/Appearance.vue` | edit   | Same        |
| `resources/js/pages/settings/Security.vue`   | edit   | Same        |
| `tests/Feature/Design/HeadingsTest.php`      | new    | 2 cases     |

## Database

None.

## Code

No new code. Three tag changes, each keeping `class="sr-only"` and its text.

## Copy

None. The words do not change.

## Routes

None.

## Tests

**New: `tests/Feature/Design/HeadingsTest.php` — 2 cases**

Read from the files, as `TabIndexTest` does.

1. `test_no_page_using_the_settings_layout_declares_its_own_h1` — walks
   `resources/js/pages/settings`, fails on any `<h1`. Names the file.
2. `test_the_settings_layout_still_has_one` — the other half, so this cannot be
   satisfied by deleting the visible heading instead.

**Changed:** none expected.

## Acceptance

- [x] Each settings page has exactly one `<h1>`, from the layout
- [x] The specific page context is still announced, as an `<h2>`
- [x] Nothing visible changes
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`resources/js/app.ts` registers both layouts for these pages, which is how the
two headings ended up composed together. That registration is not the defect and
is not touched.
