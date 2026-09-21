---
id: T-038
title: Auth and error pages get the full lockup
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-038 — Auth and error pages get the full lockup

## Why

`R-002` F-8. Twelve captured screens show the gold mark alone: sign in,
register, forgot and reset password, verify email, confirm password, and every
error page from 403 to 503. The welcome page and the product shell pair the same
mark with the Qori wordmark. The surface lane's logo rule says the pair.

These are the screens a person meets before they are signed in and the screens
they meet when something has broken. Both are exactly when a product should say
its own name.

## Decisions taken to make this specifiable

**`AppLogo` does not drop in as it stands.** It exists and pairs the two, and it
is shaped for the sidebar: a flex row with `ml-1`, `truncate` and a
`text-left` grid. An auth header is centred and stacked. So this needs either an
orientation prop on `AppLogo` or a small shared part underneath both, and the
task takes the second: one component that renders mark and wordmark, with the
sidebar and the auth layout composing it differently.

**The error pages keep their own copy.** `errors/layout.blade.php` inlines a raw
SVG and its own CSS, deliberately, so a failure renders when Vite and the
application do not. That independence is worth more than sharing a component, so
the wordmark is added to that file as markup rather than by importing anything.
`PaletteContrastTest` already guards the drift this creates.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The wordmark beside the mark on the auth layout and the error layout.
- One shared Vue part for mark-plus-wordmark, composed by both sidebar and auth.

**Out:**

- A new identity, a new mark, or a public-page header. `R-002` says so
  explicitly and it is worth repeating.
- The admin console, whose separate slate identity is the brief's allowed
  exception.

## Files

| Path                                             | Change | Notes                          |
| ------------------------------------------------ | ------ | ------------------------------ |
| `resources/js/components/AppLogoLockup.vue`      | new    | Mark and wordmark, orientable  |
| `resources/js/components/AppLogo.vue`            | edit   | Composes the lockup            |
| `resources/js/layouts/auth/AuthSimpleLayout.vue` | edit   | Uses it, stacked and centred   |
| `resources/views/errors/layout.blade.php`        | edit   | Wordmark markup beside the SVG |
| `tests/Feature/Design/LockupTest.php`            | new    | 2 cases                        |

## Database

None.

## Code

```vue
// resources/js/components/AppLogoLockup.vue defineProps<{ orientation?: 'row' |
'stacked' }>(); // default 'row'
```

The name comes from the shared `name` page prop, as `AppLogo` already reads it,
so the wordmark is never a hardcoded string.

## Copy

None. The product name is already a shared prop.

## Routes

None.

## Tests

**New: `tests/Feature/Design/LockupTest.php` — 2 cases**

1. `test_the_auth_layout_shows_the_wordmark` — reads
   `AuthSimpleLayout.vue` and requires the lockup rather than the bare icon.
2. `test_an_error_page_renders_the_product_name` — renders `errors.layout`
   through the view and asserts the name appears in the body rather than only in
   `<title>`. This one exercises the Blade rather than reading it, because that
   view is a pure renderer and can be called directly.

**Changed:** none expected. `PaletteContrastTest` parses the error layout's
colours and should be unaffected by added markup; if it is not, that is a signal
the change touched more than the lockup.

## Acceptance

- [x] Auth screens show mark and wordmark
- [x] Error pages show mark and wordmark, still with no Vite dependency
- [x] One Vue part renders the pair, composed differently by sidebar and auth
- [x] No new identity, no public-page header, admin untouched
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Lowest-priority of the `R-002` defects by the pass's own ranking, and included
because it is small, unambiguous and touches files nothing else in flight does.
