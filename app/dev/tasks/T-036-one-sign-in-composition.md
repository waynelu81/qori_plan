---
id: T-036
title: One sign-in composition, with the method as a visible choice
stream: identity
status: done
owner: claude
estimate: M
depends: none
blocks: none
---

# T-036 — One sign-in composition, with the method as a visible choice

## Why

The sign-in page carries **two fields both labelled "Email address" with the
same `email@example.com` placeholder**, separated by "Don't have an account?
Sign up". A password manager fills one of them. Nothing stops somebody typing in
the first and pressing the button under the second.

Above them sit three ways in and a heading that names one: "Enter your email and
password below to log in", under a prominent "Sign in with a passkey" button,
above an email-and-password form, above a second divider and the magic-link
request. The magic link reads as an afterthought because it is positioned as
one, below the exit from the form it belongs to.

The owner reconfirmed on 10 September 2026 that sign-in must offer **Password**
and **Email link** as choices, with app QR login deferred. The design is
proposed in [`../ui-components-and-sign-in.md`](../ui-components-and-sign-in.md);
this task specifies it.

## Decisions taken to make this specifiable

**Passkey becomes a quiet secondary entry, not a third option in the chooser.
This is the call the design report deferred — overrule it here if it is wrong,
because it changes the composition rather than a detail inside it.** The
recorded decision says the choice is Password and Email link. A two-way control
containing three methods is not two choices. So the chooser holds the two named
methods, and passkey keeps its access as a labelled control below the whole
composition. Nothing is removed and no recovery path is needed, which is what
`decisions.md` requires of any change here.

**Manual tab activation, not automatic.** Reka's Tabs follow Radix, where
activation defaults to automatic and arrow keys change the panel as focus moves.
With a password field in one panel and "email me a link" in the other, that is a
keyboard user changing which operation they are about to perform without meaning
to. Set activation to manual and assert it.

**One email field whose value survives the switch.** The whole point. Two server
operations, two error scopes, one value, one visual frame. A shared composition
does not mean a shared submission and must not become nested forms or a single
post carrying both methods' fields.

**The confirmation state is an upgrade, not a void being filled.**
`MagicLinkLoginController::store()` already returns
`back()->with('status', __('auth.magic_link.sent'))`, the sign-in page already
renders it, and the copy is already the neutral "If that email has an account, a
sign-in link is on its way." This task replaces a banner above an unchanged form
with a dedicated state, and reuses that sentence rather than writing a new one.

**"Email link" is the label. "Magic link" is not exposed.** Route names, the
controller and the notification keep their names; no user has to learn the term.

## Preconditions

None. `T-035` already removed the positive `tabindex` values from this file, so
the DOM order is the tab order and does not need revisiting here.

## Scope

**In:**

- One sign-in composition: one email field, a Password / Email link chooser,
  and the controls belonging to each.
- A dedicated "check your email" state after a link request.
- Passkey demoted to a secondary entry, still reachable.
- One registration exit, after the whole composition.

**Out:**

- QR and the Qori app. `ui-components-and-sign-in.md` is explicit that a QR
  renderer draws a code and is not an approval flow, and that the entry should
  be absent rather than disabled until it works.
- Removing or disabling passkeys. `decisions.md` forbids it without its own
  decision and a recovery path.
- Registration, password reset and 2FA screens. The 2FA flow must keep working
  and is not otherwise touched.
- The auth logo lockup, which is `T-038`.
- New endpoints. Both already exist.

## Files

| Path                                             | Change | Notes                           |
| ------------------------------------------------ | ------ | ------------------------------- |
| `resources/js/components/ui/tabs/Tabs.vue`       | new    | Reka wrapper, manual activation |
| `resources/js/components/ui/tabs/index.ts`       | new    | Exports                         |
| `resources/js/pages/auth/Login.vue`              | edit   | The composition                 |
| `resources/js/components/auth/SignInMethods.vue` | new    | Chooser and the two panels      |
| `resources/js/components/auth/LinkSent.vue`      | new    | The confirmation state          |
| `lang/en/auth.php`                               | edit   | 2 keys                          |
| `tests/Feature/Auth/SignInCompositionTest.php`   | new    | 7 cases                         |

## Database

None.

## Code

```vue
// resources/js/components/auth/SignInMethods.vue defineProps<{
canResetPassword: boolean; /** Non-null once a link has been requested, which
switches to LinkSent. */ sentTo?: string | null; }>();
```

The email value lives here and is passed into whichever panel is showing, so
switching method cannot lose it. Each panel owns its own `Form`, its own
processing state and its own errors; the frame owns neither.

Password panel: password with reveal, "Forgot your password?", remember-me, one
gold **Sign in**. Email link panel: one sentence saying no password is needed,
and one gold **Email me a sign-in link**. Password controls are not rendered in
the link panel, so they cannot be submitted with the request.

```vue
// resources/js/components/auth/LinkSent.vue defineProps<{ email: string;
status: string }>();
```

Replaces the form body. Shows **Check your email**, the address entered, and
`status` unchanged from the server. Offers **Use a different email** and a way
back to Password, both secondary to the instruction. **Send another link** posts
the same endpoint, which is already behind `throttle:magic-link` — the button
leans on that refusal rather than inventing a client-side allowance.

It must not claim an account was found or that delivery succeeded. The existing
copy is careful about this and exists to stop the endpoint being used to
discover who is registered.

## Copy

| Key                           | File               | English                                                                  |
| ----------------------------- | ------------------ | ------------------------------------------------------------------------ |
| `auth.magic_link.check`       | `lang/en/auth.php` | `Check your email`                                                       |
| `auth.magic_link.no_password` | `lang/en/auth.php` | `No password needed. We'll email you a link that signs you straight in.` |

`auth.magic_link.sent` already exists and is reused verbatim. Field labels and
button text stay inline like every other form (§13's unwired i18n, `T-006`).

## Routes

None. `magic-link.store` and Fortify's login POST both exist.

## Tests

**New: `tests/Feature/Auth/SignInCompositionTest.php` — 7 cases**

The composition is Vue and there is no JavaScript test runner, so four of these
assert server behaviour and three read the file, as `TabIndexTest` and
`PaletteContrastTest` already do.

1. `test_the_page_has_one_email_field` — reads `Login.vue` and counts
   `name="email"`. **This is the defect, asserted directly**: two fields with
   the same label is what the page has today.
2. `test_the_method_chooser_uses_manual_activation` — reads the file and
   requires manual activation, so a keyboard user cannot change operation by
   arrowing.
3. `test_passkey_is_still_reachable` — reads the file; the entry may be demoted
   and may not disappear.
4. `test_a_password_sign_in_still_works` — the flow that must not regress.
5. `test_a_link_request_answers_the_same_for_an_unknown_address` — the
   enumeration property, which the neutral copy exists to protect.
6. `test_a_link_request_is_throttled` — exceed `throttle:magic-link` and get 429,
   so "Send another link" has a real limit behind it.
7. `test_the_intended_destination_survives_a_link_sign_in` — request a protected
   page, sign in by link, land where you were going.

**Changed:** existing auth tests should not need changes. If one does, the
composition has moved behaviour rather than layout — stop and re-scope.

**Changed during execution**, and judged against that condition rather than
around it: `tests/Feature/Design/TabIndexTest.php`. It asserts the tabindex note
lives in `Login.vue`; the note is attached to the fields and moved with them
into `SignInMethods.vue`. No behaviour moved — see the report.

## Acceptance

- [x] One email field on the page, whose value survives switching method
- [x] Password and Email link are both visible choices in one frame
- [x] Arrow keys move focus in the chooser without changing the operation
- [x] A link request replaces the form with a confirmation that names the address
- [x] The neutral response is reused and still reveals nothing
- [x] Passkey sign-in is still reachable
- [x] One registration exit, after the whole composition
- [x] Password sign-in, 2FA and the intended destination all still work
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Three items from the design report's validation checklist are already settled
and should not be redone here: the positive `tabindex` values are gone (`T-035`),
`magic-link.store` is throttled through a named limiter in `AppServiceProvider`,
and the neutral sent response already renders. What remains genuinely unspecified
in that report is the set of states it lists and defers — loading, request
failure, rate limit, expired and used links. Expired and used are already handled
by `MagicLinkLoginController::login()`, which sends the reader back to sign-in
rather than to an error page; the rest are ordinary form states this composition
has to show rather than new behaviour.
