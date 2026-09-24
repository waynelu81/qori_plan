---
id: T-196
title: Signing up from a Series page makes no Group
stream: onboarding
status: doing
owner: claude
estimate: S
depends: T-027
blocks: T-108
---

# T-196 — Signing up from a Series page makes no Group

## Why

A person from a Series link who prefers a password presses "Have a password?
Sign in instead." and reaches sign-in with the Series remembered as
`SignInDestination` (`PublicSeriesController::signIn()`, `T-084`). Its "Sign
up" link opens the ordinary register page, which knows nothing of the Series,
asks "What brings you here?" with "I want to share" ticked
(`resources/js/pages/auth/Register.vue:70`), and a Peer who leaves it gets a
Group from `CreateGroupForNewUser`. Verification still returns them to the
Series (`T-008`), but from their next sign-in with nothing intended they land
on "What will you share first?" (`T-026`) — the creator onboarding `D-001` says
a person from a Series link never meets. Cut from `T-027` on 23 September
2026.

Afterwards, while a Series is waiting, the register page says which Series
the account is for and asks nothing about sharing, and no Group is made
whatever the request says.

## Decisions taken to make this specifiable

**A waiting `SignInDestination` means the person is receiving.** Only
`PublicSeriesController::signIn()` writes one, so it is always a Series, and
`ui-onboarding.md` says a person whose purpose a Series link established is
not asked to choose Share or Learn.

**The listener decides, not a hidden field.** `CreateGroupForNewUser`
returns before reading `signup_intent` when `SignInDestination::peek()` is not
null, so a page loaded before the Series was remembered, or a post that still
carries `share`, makes no Group either. `D-007` stands: when the question is
asked, the answer is read once from the request; here the Series answers it.

**Nothing is lost by not making the Group.** A receiver who later wants to
share presses Start sharing on the receiving home, which makes the same Group
(`HomeController::startSharing()`).

**The register page keeps its fields.** Name, email and password as today;
only the choice goes, replaced by one line naming the Series. The words of the
two choices on the ordinary register page are `T-108`'s, which follows this
task in the same files.

## Preconditions

**Data this task verifies against:** a clean database; a published Series from
a factory.

**Equipment:** a browser for the walk, and Mailpit for the verification
email.

## Scope

**In:**

- The register page while a Series is waiting: the line naming it, and no
  choice.
- `CreateGroupForNewUser` making no Group while a Series is waiting.

**Out:**

- The two choices' wording on the ordinary register page → `T-108`.
- The Series page's own code step, which already makes no Group (`T-073`).
- Where the new account lands after verifying: already the Series (`T-008`).

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Listeners/CreateGroupForNewUser.php` | edit | returns while a Series is waiting |
| `app/Providers/FortifyServiceProvider.php` | edit | `registerView` passes `receiving` |
| `resources/js/pages/auth/Register.vue` | edit | the line in place of the choice |
| `lang/en/auth.php` | edit | `auth.register.for_series` |
| `docs/flows/auth.md` | edit | Registration: the two ways the listener makes no Group |
| `tests/Feature/Auth/SignupIntentTest.php` | edit | 3 cases |

## Database

None.

## Code

```php
namespace App\Listeners;

class CreateGroupForNewUser
{
    // First, before the collaborations check:
    //   if (SignInDestination::peek() !== null) { return; }
    // with a comment: a person signing up while a Series waits is receiving
    // it (D-001, T-196).
    public function handle(Registered $event): void;
}
```

The `Fortify::registerView()` closure in
`FortifyServiceProvider::configureViews()` renders `auth/Register` with
`passwordRules` as today and `receiving`: null when `SignInDestination::peek()`
is null, else `__('auth.register.for_series', ['label' => ...])` with the
destination's label. The page and the listener test the same thing,
`peek() !== null`; the label is always there, because `signIn()`, the only
writer, passes the Series' title.

`Register.vue` takes `receiving: string | null`. When it is set, the "What
brings you here?" block and its radios are not rendered, and
`<p class="text-sm">{{ receiving }}</p>` stands in their place.

## Copy

| Key | File | English |
| --- | --- | --- |
| `auth.register.for_series` | `lang/en/auth.php` | You're making an account to get :label. |

## Routes

None.

## Tests

**Changed: `tests/Feature/Auth/SignupIntentTest.php` — 3 new cases**

The file gains a published Series from a factory for the first two, and
`Registered` fires inside the registration request before the session is
regenerated (`RegisteredUserController::store()`), so the listener reads the
destination the `series.sign-in` visit left.

1. `test_signing_up_while_a_series_waits_makes_no_group_whatever_is_posted` — `series.sign-in` first, then `register.store` with `signup_intent` `share`: the new user has no Group.
2. `test_the_register_page_names_the_series_instead_of_asking` — after `series.sign-in`, `receiving` is `auth.register.for_series` with the Series' title.
3. `test_the_register_page_asks_when_no_series_waits` — a fresh session: `receiving` is null.

3 new. No existing case changes.

## Acceptance

- [ ] From a Series page's sign-in link, signing up names the Series, asks nothing about sharing, and makes no Group
- [ ] Signed out and in again with nothing intended, that account lands on the receiving home, not the first-Series screen — walked in a browser
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

`T-027`'s specification on 23 September 2026 found the path; the receiving
home's words for somebody with no Series went to `T-197` the same day.
