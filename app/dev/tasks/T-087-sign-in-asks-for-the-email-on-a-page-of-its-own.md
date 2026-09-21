---
id: T-087
title: Sign-in asks for the email on a step of its own
stream: identity
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-087 — Sign-in asks for the email on a step of its own

## Why

The owner looked at sign-in again on 15 September 2026, after `T-077`, and
still did not like it: the address, the method chooser, the password field,
"Forgot your password?", remember-me and the button all arrive at once. They
asked for the order a large mail provider's sign-in uses — enter the address,
have it accepted, and only then see the password and the email link — with
passkey allowed to stay at the bottom.

Afterwards the first thing on the page is the email field and **Next**, alone.
Next shows the second step: the address, a way back to change it, then the
Password / Email link choice `T-077` built and the chosen method's controls.
Passkey and the exit to registration are below both steps, unchanged.

## Decisions taken to make this specifiable

**Next asks the server nothing.** A mail provider's first step answers
"couldn't find your account". Qori's link request deliberately says "if that
email has an account", and Fortify's failure is the same sentence for a wrong
password and an unknown address, so that sign-in cannot be used to discover
who is registered. A first step that looked the address up would give that
away for free, without a throttle. Next checks only that the address is well
formed, with the browser's own `type="email"` and `required` validation, and
moves on for any address.

**Two steps in one component, not two pages.** No route, no URL per step.
The second step is the existing one-form composition (`D-013`), and a failed
sign-in stays on it because Inertia preserves component state on a non-GET
visit (`@inertiajs/vue3` 3.7, `Form`'s `preserveState` defaults to
`method !== 'get'`). The price is that the browser's Back button leaves
sign-in instead of returning to the address, and a reload starts at step
one; the visible **Use a different email** is the way back.

**The first step is a plain `<form>`, the second the Inertia `Form`.** Enter
in the email field has to mean Next, and a native form with
`@submit.prevent="next"` gets Enter, the browser's validation and no request.
The Inertia `Form` mounts only for the second step, so nothing on the first
step can post.

**The address travels in a hidden field with `autocomplete="username"`.** The
visible field is gone on the second step. A hidden
`<input type="text" name="email" hidden readonly>` carries it to either
endpoint, and it is also what a password manager reads as the username when
it fills or saves a password on that step. The first step's field keeps
`id="email"` and drops `name`: it is never posted, and one `name="email"` in
the composition is the one the server receives. Its `autocomplete` becomes
`username` for the same password-manager reason.

**Focus follows the step.** Next puts focus on the chosen method's first
control — the password field, or the link button when Email link was the last
choice. Going back puts focus in the email field, with the address kept.

**The method choice survives going back.** Someone who chose Email link,
changed the address and pressed Next again meant Email link.

**Use a different email means the first step, from both places.** From the
second step, and from `LinkSent`'s button of the same name, which today
returns to the chooser with the same address still in it (`T-077`'s report,
found not fixed). `LinkSent` itself is not edited: it already emits
`different`, and this component decides where that goes.

**Going back clears the form's errors.** "These credentials do not match"
belongs to the address that failed, not the one about to be typed.

**The two new strings come from lang.** "Next" and "Use a different email"
are passed as props like `checkLabel`, because `CLAUDE.md` forbids adding
inline English to Vue. The existing inline labels stay (`T-006`).

## Preconditions

**Data this task verifies against:** a clean database; one factory user with a
known password for the browser walk.

**Equipment:** a browser against `localhost:8001` for the walk. Everything
else runs from the terminal.

## Scope

**In:**

- `SignInMethods.vue`: a first step (intro, email field, Next) and a second
  step (address with Use a different email, hidden `email` field, the chooser
  and panels as `T-077` left them).
- Two props from the login view, two lang keys.
- The design-review sign-in steps, which must press Next between the fields.
- The composition tests, for the new shape and the enumeration property.
- `docs/flows/auth.md`, `docs/planning/decisions.md`,
  `docs/planning/ui-components-and-sign-in.md`, the identity stream.

**Out:**

- Any server lookup of the address, and any "no account with that email"
  message.
- A URL or history entry per step.
- Passkey, registration, reset, 2FA, `LinkSent`'s markup and copy, the
  magic-link endpoint and its throttle.
- Converting the existing inline labels, and the "Log in" / "sign in" verb
  mix (`T-006`).

## Files

| Path                                             | Change | Notes                                                 |
| ------------------------------------------------ | ------ | ----------------------------------------------------- |
| `resources/js/components/auth/SignInMethods.vue` | edit   | Two steps: the address alone, then the ways in        |
| `resources/js/pages/auth/Login.vue`              | edit   | Two new props through                                 |
| `app/Providers/FortifyServiceProvider.php`       | edit   | `nextLabel`, `changeEmailLabel`                       |
| `lang/en/auth.php`                               | edit   | `sign_in.next`, `sign_in.change_email`                |
| `app/Console/Commands/DesignReviewCommand.php`   | edit   | Both sign-in step lists press Next between the fields |
| `tests/Feature/Auth/SignInCompositionTest.php`   | edit   | 11 cases (was 9)                                      |
| `docs/flows/auth.md`                             | edit   | The page's shape, one paragraph                       |
| `docs/planning/decisions.md`                     | edit   | `D-015`                                               |
| `docs/planning/ui-components-and-sign-in.md`     | edit   | Dated revision note under the proposed composition    |
| `docs/planning/streams/identity.md`              | edit   | This task                                             |

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
    introLabel: string;
    methodLabel: string;
    nextLabel: string; // "Next"
    changeEmailLabel: string; // "Use a different email"
}>();

const email = ref('');
const step = ref<'email' | 'method'>('email');
const method = ref<'password' | 'link'>('password');
const requested = ref(false);

const emailInput = useTemplateRef('emailInput');
const passwordInput = useTemplateRef('passwordInput');
const linkButton = useTemplateRef('linkButton');

/** The address is in: show the ways to finish, focus the chosen one. */
async function next(): Promise<void>;

/** Back to the address, kept, and focused. */
async function back(): Promise<void>;

/** Use a different email, from the second step: clear what was said about the old one. */
function change(clearErrors: () => void): void;

function choose(value: string | number, clearErrors: () => void): void; // unchanged
function sent(): void; // unchanged
```

Template, in order: `LinkSent` (`v-if="requested && status"`,
`@different="back"`); then `<form v-else-if="step === 'email'"
data-test="email-step" @submit.prevent="next">` holding the intro paragraph,
the email field (`ref="emailInput"`, `id="email"`, `type="email"`,
`v-model="email"`, `required`, `autofocus`, `autocomplete="username"`, no
`name`) and a submit `Button` with `data-test="next-button"` reading
`nextLabel`; then `<Form v-else>` holding the address (`data-test="sign-in-address"`)
beside a `type="button"` control with `data-test="change-email-button"`
calling `change(clearErrors)`, the hidden
`<input type="text" name="email" :value="email" autocomplete="username" hidden readonly />`,
`InputError` for `errors.email`, and the `Tabs` block as `T-077` left it, with
`ref="passwordInput"` on `PasswordInput` and `ref="linkButton"` on the link
submit `Button`.

`Login.vue` passes `:next-label` and `:change-email-label` through.
`FortifyServiceProvider::configureViews()` adds
`'nextLabel' => __('auth.sign_in.next')` and
`'changeEmailLabel' => __('auth.sign_in.change_email')`.

## Copy

| Key                         | File               | English                 |
| --------------------------- | ------------------ | ----------------------- |
| `auth.sign_in.next`         | `lang/en/auth.php` | `Next`                  |
| `auth.sign_in.change_email` | `lang/en/auth.php` | `Use a different email` |

`auth.sign_in.intro` stays as it is: "Enter your email, then choose how to
sign in." describes the two steps exactly.

## Routes

None.

## Tests

**Changed: `tests/Feature/Auth/SignInCompositionTest.php` — 11 cases (was 9)**

1. `test_the_page_has_one_email_field` — **changed**: exactly one
   `type="email"` (the field a person types in) and exactly one `name="email"`
   (the field the server receives) in `SignInMethods.vue`; neither in
   `Login.vue`.
2. `test_the_email_field_comes_before_the_method_chooser` — **changed**:
   compares the position of `type="email"` with `<TabsList`.
3. `test_the_email_is_asked_for_on_its_own_step` — **new**: the composition
   contains `@submit.prevent="next"` and `data-test="next-button"`, and the
   Next button comes before `<TabsList`.
4. `test_the_page_carries_its_instruction_from_lang` — **changed**: also
   `nextLabel` equal to `__('auth.sign_in.next')` and `changeEmailLabel` equal
   to `__('auth.sign_in.change_email')`.
5. `test_a_wrong_password_answers_the_same_as_an_unknown_address` — **new**:
   posts a wrong password for a real user and any password for
   `nobody@example.test`; both redirect back to `login` with
   `__('auth.failed')` on `email`, and nobody is signed in.
6. `test_the_method_chooser_uses_manual_activation` — unchanged.
7. `test_passkey_is_still_reachable` — unchanged.
8. `test_a_password_sign_in_still_works` — unchanged.
9. `test_a_link_request_answers_the_same_for_an_unknown_address` — unchanged.
10. `test_a_link_request_is_throttled` — unchanged.
11. `test_the_intended_destination_survives_a_link_sign_in` — unchanged.

**Must not change:** `tests/Feature/Design/TabIndexTest.php` — the "No
tabindex here" note stays in `SignInMethods.vue`, attached to the first
step's field.

## Acceptance

- [x] The first step is the email field and Next; passkey and Sign up stay below
- [x] Next validates the address in the browser and makes no request
- [x] The second step shows the address and Use a different email, then Password / Email link, with focus on the chosen method's first control
- [x] Use a different email, from the second step or the confirmation, returns to the first step with the address kept and focused and no error standing
- [x] A failed password stays on the second step with the error under the address
- [x] A wrong password and an unknown address answer the same
- [x] Password sign-in, the link request, its throttle and the intended destination still pass
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Added during execution

| Path                                                                               | Change | Reason                                                                               |
| ---------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------ |
| `docs/planning/tasks/T-006-convert-the-remaining-inline-english-in-vue-to-lang.md` | edit   | Notes: `LinkSent`'s inline "Use a different email" now has a lang key waiting for it |

## Re-scope log

None.

## Notes

The slug says "page" and the title says "step": the stub was generated before
the spec settled on one component with two steps rather than two pages. The
file name is left alone so the id and the path stay as the tool wrote them.

The Code section named the address row's `data-test` and nothing about its
layout. At 375px a long address widened the whole second step past the
screen, because a grid item does not shrink below its content and `truncate`
never applied. `min-w-0` on the address block and its row is required; the
address also carries `title`, and Use a different email has `-my-1 py-1` for
a 28px target. All in `SignInMethods.vue` (report, Departures).
