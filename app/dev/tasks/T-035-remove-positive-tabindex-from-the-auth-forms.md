---
id: T-035
title: The auth forms stop jumping the tab order
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-035 — The auth forms stop jumping the tab order

## Why

`Login.vue` and `Register.vue` carry hand-numbered positive `tabindex` values —
1 through 5 on sign-in with **5 used twice**, 1 through 6 on register. A
positive `tabindex` does not reorder a form. It moves those elements into a
separate, document-wide tab sequence that is visited **before every other
focusable element on the page**, including the skip link, the navigation and, on
sign-in, the passkey button that sits above the form.

So the first Tab on the sign-in page lands in the email field rather than at the
top of the document, and the two links sharing index 5 are ordered by DOM
position within their own bucket, which is not what the numbering was trying to
express. These are the two screens every account passes through.

Raised in `ui-components-and-sign-in.md`, where it appears inside a
pre-implementation validation checklist rather than as a finding. It does not
need a sign-in redesign and should not wait for one.

## Decisions taken to make this specifiable

**Delete the attributes rather than renumber them.** The DOM order in both forms
already matches the visual order, so the natural sequence is the correct one.
`Login.vue` places "Forgot your password?" on the Password label's row, which is
where a reader meets it and therefore where a keyboard should. The numbering
existed to push it past the password field, which contradicts the visual order
rather than serving it.

**This is a slice of `T-022`, not a replacement for it.** That task owns tab
order across the product and is blocked on a browser that receives key events
and renders. This is a source-level defect visible without one, and the argument
for the fix does not depend on watching it: a positive `tabindex` is wrong here
whatever the observed order turns out to be. `T-022` still owns verification.

## Preconditions

None. Deliberately: needing a browser is what has kept `T-022` blocked.

## Scope

**In:**

- Removing every positive `tabindex` from `Login.vue` and `Register.vue`.
- Removing the now-unused `tabindex` prop from `TextLink` if nothing else passes
  one.
- A test that stops them coming back.

**Out:**

- Everything else in `T-022`: focus rings, dialog dismissal, focus restore, the
  mobile drawer, traps.
- The sign-in redesign proposed in `ui-components-and-sign-in.md`. This must
  leave that design free, not pre-empt it.
- `tabindex="-1"`, which is a different thing and legitimate.

## Files

| Path                                    | Change | Notes                                   |
| --------------------------------------- | ------ | --------------------------------------- |
| `resources/js/pages/auth/Login.vue`     | edit   | Six attributes                          |
| `resources/js/pages/auth/Register.vue`  | edit   | Six attributes                          |
| `resources/js/components/TextLink.vue`  | edit   | Drop the prop if unused after the above |
| `tests/Feature/Design/TabIndexTest.php` | new    | 2 cases                                 |

## Database

None.

## Code

No new code. The change is deletion.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Design/TabIndexTest.php` — 2 cases**

Vue cannot be unit tested here, so the test reads the files, the same way
`PaletteContrastTest` parses `app.css` and `ModelEnumTest` walks `app/Models`.

1. `test_no_vue_file_sets_a_positive_tabindex` — walks `resources/js`, fails on
   any `tabindex` whose value is a positive integer. `-1` and `0` pass, because
   both are legitimate. Names the file and the line.
2. `test_the_rule_is_stated_where_somebody_will_meet_it` — asserts the sign-in
   page carries the comment explaining why, so the next person adding a field
   does not helpfully renumber it back.

**Changed:** none expected.

## Acceptance

- [x] No positive `tabindex` anywhere in `resources/js`
- [x] Tab order on both forms follows the DOM, which follows the visual order
- [x] A reintroduced positive `tabindex` fails the suite
- [x] `T-022` is not closed or narrowed by this
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**`TextLink`'s `tabindex` prop went with them.** Sign-in was its only caller, so
leaving it would have been an affordance for putting the defect back.

**Twelve attributes, not six each.** `Login.vue` had six and `Register.vue` had
six, which the Files table happened to state correctly per file and which is
worth confirming because the numbering ran 1 to 5 and 1 to 6 respectively.

The duplicate `5` is worth keeping in mind while reading the diff: two elements
sharing a positive index are ordered by document position anyway, so half the
numbering was already doing nothing.
