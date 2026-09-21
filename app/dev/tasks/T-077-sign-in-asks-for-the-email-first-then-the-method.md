---
id: T-077
title: Sign-in asks for the email first, then the method
stream: identity
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-077 — Sign-in asks for the email first, then the method

## Why

The owner reviewed sign-in on 13 September 2026, back on the page after a
sign-out, and asked for an adjustment. Passkey is a separate function and may
stay where it is, below the rule. Password and Email link are not separate
functions: they are two ways of finishing the same sign-in, both need the
address first, and the choice belongs after it. `T-036` put the choice first,
as a pair of tabs, with an email field inside each panel; the composition reads
as "pick a tab, then fill in a form" when the person's own order is "who am I,
then how do I prove it".

Afterwards the page has one email field at the top, always mounted, the
Password / Email link choice directly under it, and only the chosen method's
controls beneath that. Switching method never remounts the field, never loses
the address, never moves focus, and clears the other method's errors.

## Decisions taken to make this specifiable

**One form whose action follows the choice.** `T-036` gave each panel its own
`Form`, which is why each panel had to own an email field: a field belongs to
one form. With the field above the choice, either two fields are kept and one
hidden, or the whole form remounts on every switch and the keyboard loses its
place, or there is one `Form` and its `action` is computed from the method.
The third is the plain one. The password controls are rendered only in the
password panel and the link panel renders none, so a link request never
carries a password and a password sign-in never carries anything the link
endpoint would see. What the two methods share is the address and the frame;
they still never share a payload.

**Errors are cleared on switch.** Fortify puts "these credentials do not
match" on `email`. Left standing while the person moves to Email link, it
would sit under the address as if the address were wrong. Choosing a method
calls the form's `clearErrors()`.

**The instruction moves into the composition.** `T-036` left the layout's
description, "Choose how you would like to sign in", standing above "Check
your email" once a link was requested, and recorded it as found, not fixed.
The page keeps the layout's title only and the composition says "Enter your
email, then choose how to sign in" itself, so the sentence disappears with the
form it describes. `VerifyEmail.vue` already does exactly this (`T-008`).

**Tabs stay tabs.** The chooser keeps Reka's tabs with manual activation, so
arrow keys move focus without changing what the person is about to do, and the
selected state keeps the lighter fill `T-036` chose for this palette. The list
gets an `aria-label` because a segmented control between two fields needs a
name that the visible sentence above does not give it.

**Nothing about the link request or the confirmation changes.** `LinkSent`,
the neutral sentence, the throttle and the resend are untouched.

## Preconditions

None.

## Scope

**In:**

- The composition in `SignInMethods.vue`: intro line, one email field, the
  chooser under it, one form.
- The two copy lines, passed as props from the login view.
- `Login.vue` keeps the layout title only.
- The tests that read the composition, so they assert the new order.
- A stale comment in the design-review command about a second email field.
- `docs/flows/auth.md`, `docs/planning/decisions.md`,
  `docs/planning/ui-components-and-sign-in.md`, the identity stream.

**Out:**

- Passkey. It stays below the rule, as the owner said.
- `LinkSent`, the magic-link endpoint, throttling, 2FA, registration, reset.
- The layout's spacing or the auth lockup.
- Converting the remaining inline labels to lang (§13, `T-006`).

## Files

| Path                                             | Change | Notes                                                        |
| ------------------------------------------------ | ------ | ------------------------------------------------------------ |
| `resources/js/components/auth/SignInMethods.vue` | edit   | One form; the email field first; the chooser under it        |
| `resources/js/pages/auth/Login.vue`              | edit   | Layout title only; two new props through                     |
| `app/Providers/FortifyServiceProvider.php`       | edit   | `introLabel`, `methodLabel`                                  |
| `lang/en/auth.php`                               | edit   | `sign_in.intro`, `sign_in.method`                            |
| `app/Console/Commands/DesignReviewCommand.php`   | edit   | Comment only: the page has had one email field since `T-036` |
| `tests/Feature/Auth/SignInCompositionTest.php`   | edit   | The count is the property again; two new cases               |
| `docs/flows/auth.md`                             | edit   | The page's shape, one paragraph                              |
| `docs/planning/decisions.md`                     | edit   | Email first, then the method                                 |
| `docs/planning/ui-components-and-sign-in.md`     | edit   | Dated revision note under the proposed composition           |
| `docs/planning/streams/identity.md`              | edit   | This task                                                    |

## Database

None.

## Code

```ts
// resources/js/components/auth/SignInMethods.vue
const props = defineProps<{
    canResetPassword: boolean;
    status?: string;
    checkLabel: string;
    noPasswordLabel: string;
    introLabel: string; // "Enter your email, then choose how to sign in."
    methodLabel: string; // the tablist's aria-label
}>();

const email = ref('');
const method = ref<'password' | 'link'>('password');
const requested = ref(false);

/** The one form posts wherever the chosen method says. */
const action = computed(() =>
    method.value === 'password' ? login() : magicLink(),
);

/** Choosing a method also clears the other method's errors. */
function choose(value: string | number, clearErrors: () => void): void;
```

Template order inside the one `Form`: the intro paragraph; the email field
(`id="email"`, `name="email"`, `v-model="email"`, `autofocus`,
`autocomplete="email"`) with its `InputError`; `Tabs` with a `TabsList`
carrying `:aria-label="methodLabel"` and the two triggers, then
`TabsContent value="password"` (password with reveal, forgot link,
remember-me, `data-test="login-button"`) and `TabsContent value="link"`
(the `noPasswordLabel` sentence, `data-test="magic-link-button"`).
`:reset-on-success="['password']"` stays; `@success` sets `requested` only
when the method is `link`. `LinkSent` still replaces the form when
`requested && status`.

`Login.vue`: `defineOptions({ layout: { title: 'Log in to Qori' } })`, and the
two new props passed through. `FortifyServiceProvider::configureViews()` adds
`'introLabel' => __('auth.sign_in.intro')` and
`'methodLabel' => __('auth.sign_in.method')`.

## Copy

| Key                   | File               | English                                         |
| --------------------- | ------------------ | ----------------------------------------------- |
| `auth.sign_in.intro`  | `lang/en/auth.php` | `Enter your email, then choose how to sign in.` |
| `auth.sign_in.method` | `lang/en/auth.php` | `How to sign in`                                |

## Routes

None.

## Tests

**Changed: `tests/Feature/Auth/SignInCompositionTest.php` — 9 cases (was 7)**

1. `test_the_page_has_one_email_field` — **changed**: exactly one
   `name="email"` in `SignInMethods.vue`, none in `Login.vue`. The count is
   the property again now there is one form.
2. `test_the_email_field_comes_before_the_method_chooser` — **new**: in
   `SignInMethods.vue` the position of `name="email"` is before the position
   of `<TabsList`.
3. `test_the_page_carries_its_instruction_from_lang` — **new**: GET `login`
   renders `auth/Login` with `introLabel` equal to `__('auth.sign_in.intro')`
   and `methodLabel` equal to `__('auth.sign_in.method')`.
4. `test_the_method_chooser_uses_manual_activation` — unchanged.
5. `test_passkey_is_still_reachable` — unchanged.
6. `test_a_password_sign_in_still_works` — unchanged.
7. `test_a_link_request_answers_the_same_for_an_unknown_address` — unchanged.
8. `test_a_link_request_is_throttled` — unchanged.
9. `test_the_intended_destination_survives_a_link_sign_in` — unchanged.

**Changed:** `tests/Feature/Design/TabIndexTest.php` must not need a change:
the "No tabindex here" note stays in `SignInMethods.vue`, attached to the
fields.

## Acceptance

- [x] One email field, at the top, mounted whichever method is chosen
- [x] Password and Email link are the choice directly under it; passkey is unchanged below the rule
- [x] Switching method keeps the address, keeps focus on the chooser, and clears the other method's errors
- [x] A link request carries no password field; a password sign-in posts to Fortify as before
- [x] The instruction disappears with the form when "Check your email" replaces it
- [x] Password sign-in, 2FA, the intended destination and the throttle all still pass
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`T-036`'s report chose "each panel owns its own Form" so that two operations
against two endpoints never became one submission. That is still true here:
one `Form` element, two actions, and the set of fields rendered decides what
is posted. What changed is where the address lives, and the owner's order.
