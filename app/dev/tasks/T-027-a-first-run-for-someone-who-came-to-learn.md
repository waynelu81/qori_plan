---
id: T-027
title: The Series page confirms who is getting it, and never sells it twice
stream: onboarding
status: ready
owner: unassigned
estimate: M
depends: T-008, T-024
blocks: T-102, T-196, T-198
---

# T-027 — The Series page confirms who is getting it, and never sells it twice

## Why

`D-001` has a person from a Series link confirm their name, email and
personal timezone, get access or pay, and open that Series — never meeting
creator setup. `T-073`, `T-074` and `T-181` built everything but the
confirming. Today a signed-in person meets the terms, the emails box and "Get
access" with nothing saying which account gets the Series
(`resources/js/pages/public/Series.vue:254-318` never reads the account), so a
forwarded link opened on a shared computer grants whoever is signed in. No
path on the page asks a timezone, so every Peer made by the code step has
`users.timezone` null (`SeriesAccessController::start()`,
`app/Http/Controllers/SeriesAccessController.php:74-78`). A buyer back on the
page before the webhook sees "Get access — A$89.00" again and can open a
second Stripe session: `PublicSeriesController::show()` only ever forgets
`CheckoutPending` (`:71-75`), and `CheckoutService::begin()` refuses only an
active Access (`:81-87`). And a priced Series says of the code "Type it here
and you're in" (`accesses.join.intro`), though payment follows (R-004 F-7).

Afterwards, signed in, the page says whose account gets it and offers a way
out; the timezone is shown, or asked once where the person already is; a
payment in progress stops the page selling again until the person says they
did not pay; and the paid sentence says what happens next.

## Decisions taken to make this specifiable

**What remains of the draft is the confirming, on the Series page itself.**
Its other bullets are answered by what was built after it was written. The
Series context survives authentication because the code step never leaves the
page (`T-073`), and a password sign-in carries it as `SignInDestination`
through verification (`T-008`, `T-084`). Checkout's cancel, confirming and
already-granted states are `T-074`'s, and an invitation's arrival is
`T-181`'s. Two parts of the draft were cut on 23 September 2026 as small
tasks of their own: the receiving home for someone with no Series (`T-197`),
which shares no file with this one and can be built beside it, and
registering from a Series page's sign-in link (`T-196`), which follows this
one because both edit `docs/flows/auth.md`.

**Signed in, the page names the account above the button, and "Not you?" is
the ordinary sign-out.** "You're getting this as :name (:email)." answers
the draft's forwarded-link case: nothing switches identity silently, and the
person sees whose it will be before pressing. Sign-out lands on sign-in with
its sentence, as `D-006` has it for every sign-out. A second sign-out that
came back to the Series would be a behaviour `D-006` does not have, and the
link they followed is still in their inbox.

**The timezone is asked once, where the person already is, and never
overwritten.** Signed in with none: `TimezoneField` in the form, filled in
from the device and saying so, as it does on Profile and the first-Series
screen (`T-024`). Signed in with one: shown, not asked — "Your timezone is
:timezone." — and changed on Profile as today. The line states the setting
and promises nothing about it: every time on this page is still shown in the
browser's own zone (`SessionTime` is given none), and showing times in the
saved zone is `T-025`'s. A guest: asked in the
name-and-email form, carried through the code with the rest of the step, and
saved at verify only on an account with none, because the form is filled
before the code proves who is typing. `User::confirmTimezone()` is the one
rule for all four places a zone arrives. The server infers nothing: the value
saved is the person's submission of a field they saw.

**The name and address are shown, not re-asked, and not changed here.** A
guest types them once (`T-073`). An account the code finds keeps its own
name; the one typed is not written over it. Changing either stays on
Profile, whose email change is proved by a link to the new inbox
(`EmailChangeService`), a round trip a Series page should not start. So the
draft's "contextual returns missing from Profile" are not built: nothing on
this path sends anybody to Profile.

**A payment this session started stops the page selling again.** While
`CheckoutPending::since()` holds for the Series and there is no Access, the
page shows "Your payment is being confirmed" with Check now (the Confirming
page) and "Didn't pay? Start again" in place of the button, and the two
places a paid checkout begins for a signed-in person —
`CheckoutController::store()` and the paid branch of
`AcceptsInvitations::acceptInvitation()` — send a second attempt to the
Confirming page instead of calling `begin()`. Start again forgets the marker,
because a buyer who closed Stripe's tab would otherwise wait
`CONFIRMING_MINUTES` to try again. `SeriesAccessController::verify()` needs no
guard of its own: a guest's session holds no marker, since sign-out
invalidates it, and its invitation branch goes through the guarded trait.

**It is built on `CheckoutPending` as it stands.** `T-102` replaces the
session marker with the `payment_fulfilments` row, so a payment is seen in
any browser; the three reads added here move with it, and `T-102` depends on
this task. Waiting for that would leave the second purchase open until a
draft with five open questions is built.

**The paid intro says the code confirms the address and payment follows.**
`accesses.join.intro` stays for a free Series and a free invitation;
`accesses.join.intro_paid` is for a priced Series and an invitation at a
price. It names Stripe, which `D-035` confirms for public copy. It restates no
price: the page shows it above in the visitor's own locale, and a price
formatted on the server reads differently (`T-182`).

**The invitation's full address reaches nobody it is not for.** Outside the
`waiting` state `email` is masked and `forAddress` is null.
`PublicSeriesController::invitation()` masks `email` and the notice only in
the `someone-else` state (`T-181`), builds `forAddress` from the full address
in every state (`:228`), and matches `accepted` and `ended` before
`someone-else` (`:210-215`) — so somebody signed in as another account who
follows a forwarded invitation gets the full address in their page data,
unrendered, and gets it in `email` too once the invitation has ended. Nothing
reads either outside `waiting` (`Series.vue`'s `invited`,
`InvitationOffer.vue:37-40`). It is this task's wrong-account case.

**It shares two files with ready tasks in the classroom stream without a
dependency.** `T-136` adds `accesses.mail.*` keys to `lang/en/accesses.php`
and `T-134` a sentence to `docs/flows/series.md`'s "Adding episodes"; this
task adds other keys and edits the public page's section. Both wait on
unfinished tasks of their own, and chaining three streams through a lang
array would cost more than whichever lands second rebasing two hunks.

**Verification when required stays `T-008`'s detour.** A signed-in person
whose address is unproved meets the `verified` wall after pressing, and comes
back to the Series; `D-001`'s "verification when required" is that.

**The receiving cards stay with the redesign.** Attribution, "2 of 4" and a
named Continue (R-004 F-10) are
[`ui-redesign-next-sprint.md`](../../design/ui-redesign-next-sprint.md) §5,
which the design stream holds back from tasks deliberately so the composition
is rebuilt once.

## Preconditions

**Data this task verifies against:** a clean database for the suite. For the
browser walk, `php artisan qori:reset full`: the design-review cast has a free
Series, a priced one whose Group can take payments, and one whose Group
cannot.

**Equipment:** a browser at 375px and desktop width; Mailpit on 1025/8025 for
the code, read without emptying it; Docker for `php artisan qori:e2e`.

## Scope

**In:**

- Signed in: the account that gets the Series, "Not you? Sign out", and the
  timezone shown or asked.
- A guest: the timezone asked beside name and email, carried through the
  code, and saved on an account with none.
- The paid intro sentence, for a priced Series and an invitation at a price.
- A payment in progress: the page's notice, the two guarded places a checkout
  begins, and Start again.
- The invitation's `email` and `forAddress` outside the `waiting` state.

**Out:**

- Registering from the sign-in page a Series sent somebody to → `T-196`.
- The receiving home for someone with no Series → `T-197`.
- The receiving cards' composition → the redesign sprint, §5.
- A payment seen in another browser, and delayed payment methods → `T-102`.
- An address typed in capitals → `T-198`; a password for an account the code
  made → `T-199`; Peer rows after an address change → `T-200`.
- Changing name or address from the Series page: Profile, unchanged.
- Showing times in the saved zone anywhere → `T-025`.
- The inline English already in `Series.vue` ("Get access", "Free", "What's
  inside", "Open") → `T-006`.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Models/User.php` | edit | `confirmTimezone()` |
| `app/Http/Controllers/PublicSeriesController.php` | edit | `viewer.as`, `viewer.notYou`, `viewer.timezone`, `askTimezone`, `paying`, the paid intro, `forAddress` |
| `app/Support/SeriesAccessPending.php` | edit | `remember()` takes the zone; `timezone()` reads it |
| `app/Http/Controllers/SeriesAccessController.php` | edit | `start()` carries the zone; `verify()` confirms it |
| `app/Http/Requests/StartSeriesAccessRequest.php` | edit | `timezone` rule |
| `app/Http/Requests/GrantInSeriesRequest.php` | edit | `timezone` rule |
| `app/Http/Requests/StartCheckoutRequest.php` | edit | `timezone` rule |
| `app/Http/Requests/AcceptInvitationRequest.php` | edit | `timezone` rule |
| `app/Http/Controllers/PublicAccessController.php` | edit | confirms the zone |
| `app/Http/Controllers/PublicInvitationController.php` | edit | confirms the zone |
| `app/Http/Controllers/CheckoutController.php` | edit | confirms the zone; the guard; `abandon()` |
| `app/Concerns/AcceptsInvitations.php` | edit | the guard on the paid branch |
| `routes/web.php` | edit | `series.checkout.abandon` |
| `resources/js/pages/public/Series.vue` | edit | the account line, sign-out, `TimezoneField` in both forms, the paying notice |
| `resources/js/components/TimezoneField.vue` | edit | optional `suggestedNote` prop |
| `resources/js/components/series/InvitationOffer.vue` | edit | the `forAddress` type may be null |
| `lang/en/accesses.php` | edit | ten keys |
| `docs/flows/series.md` | edit | the public page's new props and states |
| `docs/flows/checkout.md` | edit | the paying state, the guard, Start again |
| `docs/flows/auth.md` | edit | the code step carries the zone; its two stale lines |
| `docs/tinker/auth.md` | edit | "Code from a Series page": where the zone lands |
| `tests/Feature/Access/SeriesAccessIdentityTest.php` | new | 10 cases |
| `tests/Feature/Checkout/ConfirmingTest.php` | edit | 4 cases |
| `tests/Feature/PublicSeriesTest.php` | edit | 2 cases |
| `tests/Feature/Invitations/AcceptInvitationTest.php` | edit | 5 cases |

`docs/flows/auth.md`'s two stale lines: `SeriesAccessPending::remember()` is
shown with two arguments, and `verify()` is said to return to the Series,
which it has not done since `T-074`.

## Database

None. `users.timezone` exists (`T-024`).

## Code

```php
namespace App\Models;

class User
{
    /**
     * The zone somebody confirmed on a Series page (T-027): kept when they
     * had none, ignored when they had one or when it is not in
     * Timezones::all(). Their earlier answer is theirs, and a form that did
     * not show it never overwrites it.
     */
    public function confirmTimezone(?string $timezone): void;
    // null, a saved zone, or ! Timezones::isValid($timezone): return.
    // Otherwise forceFill(['timezone' => $timezone])->save().
}
```

```php
namespace App\Support;

class SeriesAccessPending
{
    // Stores 'timezone' => $timezone beside the agreement.
    public static function remember(Series $series, User $user, AccessAgreement $agreement, ?string $timezone = null): void;

    /** @param array<string, mixed> $pending */
    public static function timezone(array $pending): ?string;
}
```

`peek()` rebuilds the step from named keys and drops any other
(`app/Support/SeriesAccessPending.php:60-79`), so it carries `'timezone' =>
is_string($pending['timezone'] ?? null) ? $pending['timezone'] : null`, and
the `@return` shapes of `peek()` and `for()` gain `timezone: ?string`.
Without that, `verify()` — which reads the step through `for()` — never sees
the zone.

`SeriesAccessController::start()` passes
`$request->filled('timezone') ? $request->string('timezone')->toString() : null`
to `remember()`. `verify()` already holds `$pending` from `for()` at its top;
right after the block that marks the address verified, and before
`Auth::login()`, it calls `$user->confirmTimezone($pending === null ? null :
SeriesAccessPending::timezone($pending))` — so a step remembered before the
terms (the early return after `forget()`) keeps its zone too.

The four Form Requests each gain
`'timezone' => ['nullable', 'string', 'max:64', Rule::in(Timezones::all())]`,
the rule `UpdateTimezoneRequest` already uses. `PublicAccessController::store()`,
`CheckoutController::store()` and `PublicInvitationController::accept()` each
call `$peer->confirmTimezone(...)` with the same expression first.

```php
namespace App\Http\Controllers;

class CheckoutController
{
    // After confirmTimezone(), before begin():
    //   CheckoutPending::since((string) $model->getKey()) !== null
    //   → return to_route('shared.show', (string) $model->getKey());
    public function store(StartCheckoutRequest $request, string $series, CheckoutService $checkout): Response;

    // CheckoutPending::forget($seriesId); Series::findForPeer($seriesId), a
    // missing or unpublished one → AppException::notFound(
    // 'errors.access.series_unavailable'); then redirect to series.public.
    public function abandon(string $seriesId): RedirectResponse;
}
```

`AcceptsInvitations::acceptInvitation()`: the priced branch returns
`to_route('shared.show', (string) $series->getKey())` while
`CheckoutPending::since()` holds for the Series, before `begin()`.

`PublicSeriesController::show()` keeps `$granted`, `$cancelled`, `$pending`,
`$followed`, `$invitation` and `$invitedFree` as they are, then computes:
`$id = (string) $model->getKey()`; `$chosen = $peer !== null &&
$peer->getAttributeValue('timezone') !== null`; `$paying = $peer !== null &&
! $granted && ! $cancelled && CheckoutPending::since($id) !== null`; the
`notTakingPayments` value it already builds, now into `$notTakingPayments`;
and `$asks = ! $granted && ! $paying && $notTakingPayments === null && ($peer
=== null ? $pending === null : ! $chosen)`. The props:

```php
'viewer' => [
    // signedIn, granted and pending as today, then:
    'as' => $peer === null ? null : __('accesses.viewer.as', ['name' => $peer->name, 'email' => $peer->email]),
    'notYou' => $peer === null ? null : __('accesses.viewer.not_you'),
    'timezone' => $chosen ? __('accesses.viewer.timezone', ['timezone' => $peer->timezone()]) : null,
],
'askTimezone' => $asks ? [
    'options' => Timezones::grouped(),
    'value' => $peer?->timezone() ?? Timezones::fallback(),
    'chosen' => false,
    'label' => __('accesses.timezone.label'),
    'suggested' => __('accesses.timezone.suggested'),
] : null,
'paying' => $paying ? [
    'title' => __('accesses.paying.title'),
    'body' => app(Terminology::class)->line('accesses.paying.body', [], $model->group),
    'check' => __('accesses.paying.check'),
    'startAgain' => __('accesses.paying.start_again'),
] : null,
```

`join.intro` is `__('accesses.join.intro_paid')` when the entry is paid —
a waiting invitation at a price, or no waiting invitation and a priced Series
— and `__('accesses.join.intro')` otherwise. In `invitation()`, `'email' =>
$state === 'waiting' ? $invitation->email : $masked` and `'forAddress' =>
$state === 'waiting' ? __('invitations.public.for_address', [...]) : null`.
`InvitationOffer.vue` types `forAddress` as `string | null`; it reads it only
inside `state === 'waiting'`.

`Series.vue`: the props above, typed (`askTimezone` and `paying` nullable
objects, `viewer.as`, `viewer.notYou` and `viewer.timezone` nullable
strings). A branch `v-else-if="paying"` sits after `notTakingPayments` and
before `viewer.signedIn`: an `InlineNotice` with `paying.title` and
`paying.body`, a `Link` to `sharedShow(series.id)` labelled `paying.check`,
and a `Form` with `method="delete"` to `/s/${series.id}/checkout` labelled
`paying.startAgain`. The signed-in branch opens with `viewer.as`, a
`<Link :href="logout()" method="post" as="button">` labelled `viewer.notYou`,
and `viewer.timezone` when set; its form holds `TimezoneField` when
`askTimezone` is set. The guest form holds the same field after the email.
Both bind it the same way: `id="access-timezone"`,
`:options="askTimezone.options"`, `:value="askTimezone.value"`,
`:chosen="askTimezone.chosen"`, `:label="askTimezone.label"`,
`:suggested-note="askTimezone.suggested"` and `:error="errors.timezone"`, the
last so a refused zone shows under the field. `Series.vue` imports `logout`
from `@/routes` and `TimezoneField` from `@/components/TimezoneField.vue`;
neither is imported today.

`TimezoneField.vue` gains `suggestedNote?: string`; when given it replaces
the component's own "Filled in from your device…" sentence, which says "then
save" to a page with no Save.

Flows: `docs/flows/series.md`, `docs/flows/checkout.md` and
`docs/flows/auth.md`, in the Files table.

## Copy

| Key | File | English |
| --- | --- | --- |
| `accesses.join.intro_paid` | `lang/en/accesses.php` | Tell us who you are and we'll email you a code to confirm your address. Then you pay on Stripe, and you're in. |
| `accesses.viewer.as` | `lang/en/accesses.php` | You're getting this as :name (:email). |
| `accesses.viewer.not_you` | `lang/en/accesses.php` | Not you? Sign out |
| `accesses.viewer.timezone` | `lang/en/accesses.php` | Your timezone is :timezone. |
| `accesses.timezone.label` | `lang/en/accesses.php` | Your timezone |
| `accesses.timezone.suggested` | `lang/en/accesses.php` | Filled in from your device. Change it if it's not right. |
| `accesses.paying.title` | `lang/en/accesses.php` | Your payment is being confirmed |
| `accesses.paying.body` | `lang/en/accesses.php` | If you paid, Stripe is confirming it, which usually takes seconds. Check now to open the :series. |
| `accesses.paying.check` | `lang/en/accesses.php` | Check now |
| `accesses.paying.start_again` | `lang/en/accesses.php` | Didn't pay? Start again |

`accesses.join.intro` is unchanged.

## Routes

| Verb | Path | Name | Action |
| --- | --- | --- | --- |
| DELETE | `s/{seriesId}/checkout` | `series.checkout.abandon` | `CheckoutController@abandon`, middleware `auth` |

## Tests

**New: `tests/Feature/Access/SeriesAccessIdentityTest.php` — 10 cases**

1. `test_a_signed_in_viewer_is_told_which_account_gets_it` — `viewer.as` is `accesses.viewer.as` with their name and address, and `viewer.notYou` is set.
2. `test_a_guest_is_named_nowhere` — `viewer.as`, `viewer.notYou` and `viewer.timezone` are null.
3. `test_a_signed_in_viewer_with_no_timezone_is_asked_for_one` — `askTimezone` is set with `chosen` false, and `viewer.timezone` is null.
4. `test_a_signed_in_viewer_with_a_timezone_is_shown_it_and_not_asked` — `viewer.timezone` names their zone, and `askTimezone` is null.
5. `test_a_guest_is_asked_for_a_timezone_until_a_code_is_pending` — `askTimezone` is set on the name-and-email step and null on the code step.
6. `test_the_code_saves_the_timezone_on_a_new_account` — started with `Europe/London`; after the code, `users.timezone` is `Europe/London`.
7. `test_the_code_never_overwrites_a_timezone_already_saved` — an account at `Asia/Tokyo` starts with `Europe/London`; after the code it is still `Asia/Tokyo`.
8. `test_a_timezone_qori_does_not_know_is_refused` — started with `Mars/Olympus_Mons`: a session error on `timezone`, and no code is sent.
9. `test_taking_a_free_series_saves_the_timezone_asked_for` — signed in with none, `series.grant` with `timezone` saves it.
10. `test_starting_checkout_saves_the_timezone_asked_for` — Stripe faked with `Http::fake()`; `checkout.store` with `timezone` saves it.

**Changed: `tests/Feature/Checkout/ConfirmingTest.php` — 4 new cases**

11. `test_the_series_page_says_a_payment_is_being_confirmed_instead_of_selling_again` — the marker set and no Access: `paying` is set and `askTimezone` is null.
12. `test_a_second_checkout_while_one_is_confirming_goes_to_confirming` — the marker set: `checkout.store` redirects to `shared.show`, and `Http::assertNothingSent()`.
13. `test_starting_again_forgets_the_payment_and_offers_the_series` — `series.checkout.abandon` redirects to `series.public`, the marker is gone, and `paying` is null.
14. `test_back_from_stripe_without_paying_is_not_confirming` — `?cancelled=1`: `paying` is null and `notice` is set.

**Changed: `tests/Feature/PublicSeriesTest.php` — 2 new cases**

15. `test_a_priced_series_says_payment_follows_the_code` — `join.intro` is `accesses.join.intro_paid`.
16. `test_a_free_series_keeps_the_short_intro` — `join.intro` is `accesses.join.intro`.

**Changed: `tests/Feature/Invitations/AcceptInvitationTest.php` — 5 new cases**

These need an invitation followed in the session, which is what this file's
private `invited()` helper sets up, for its own address.

17. `test_accepting_an_invitation_saves_the_timezone_asked_for` — a free invitation, signed in as its address: `series.invitation.accept` with `timezone` saves it.
18. `test_a_priced_invitation_is_not_begun_twice_while_confirming` — Stripe faked with `Http::fake()`, `CheckoutPending::mark()` for the Series, and a waiting invitation at a price: accepting redirects to `shared.show`, and `Http::assertNothingSent()`.
19. `test_someone_signed_in_with_another_address_is_not_sent_the_invited_address` — the `someone-else` state: `invitation.forAddress` is null, and `invitation.email` masked as today.
20. `test_an_ended_invitation_shows_nobody_the_full_address` — a withdrawn invitation followed signed in as another account: `invitation.state` is `ended`, `invitation.email` is masked, and `invitation.forAddress` is null.
21. `test_a_free_invitation_to_a_priced_series_keeps_the_short_intro` — a waiting free invitation: `join.intro` is `accesses.join.intro`.

21 new. No existing case changes: `timezone` is nullable everywhere, so every
current post still passes, and nothing asserts `email` outside `waiting` and
`someone-else`.

## Acceptance

- [ ] Signed in, the Series page names the account that gets it, offers "Not you? Sign out", and shows the timezone or asks it
- [ ] A guest's timezone, asked beside name and email, is saved when the code proves an account with none, and never over one
- [ ] A priced Series' intro says the code confirms the address and payment follows
- [ ] While a payment this session started is confirming, the page offers Check now and Start again instead of the button, and a second checkout goes to Confirming
- [ ] Signed in as somebody else, an invitation's page data carries no full address
- [ ] `php artisan qori:e2e` passes: the public-link, invitation and first-share journeys fill the guest form
- [ ] A state-specific browser walk at 375px and desktop: a guest on a free and a priced Series, signed in with and without a timezone, and confirming then Start again
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

**2026-09-11 — owner expanded this draft.** It formerly covered only the empty
receiving home and excluded changing registration. Series-linked entry now
selects the receiving journey, confirms basic details and continues through
payment/access. The dependency on T-026 is replaced by T-008/T-024; the receiving
path does not await creator setup. No implementation was started.

**2026-09-13 — two slices cut.** `T-073` (account and typed code on the Series page) and `T-074` (straight to access, confirming state, cancel to the Series) are `ready`. What remains here is the name, email and personal timezone confirmation and the direct receiving welcome.

**2026-09-23 — specified, and two more slices cut.** Brought to `ready` from
the code as it is after `T-073`, `T-074`, `T-178` and `T-181`. The direct
receiving welcome went to `T-197` and registering from a Series page's
sign-in link to `T-196`; the draft's title, "Series-linked signup, payment and
receiving onboarding", became what is left. Its **Before this can be ready**
bullets, answered:

- ~~Specify the trusted Series/entry context and its persistence across
  signup, verification, profile correction, provider returns and resumed
  sessions.~~ **Answered 23 September 2026:** the code step keeps the person
  on the page (`T-073`); a password sign-in carries `SignInDestination`
  through verification (`T-008`, `T-084`); profile correction is not on this
  path (Decisions); a signed-up-elsewhere path is `T-196`.
- ~~Name the profile/confirmation components, exact fields and validation
  reuse, routes, copy keys and the contextual returns currently missing from
  Profile.~~ **Answered:** Code, Copy and Routes above; no return from Profile
  is built, because nothing here sends anyone there.
- ~~Define checkout return states against server payment/access status,
  including cancellation back to the Series and the interval before webhook
  fulfilment. Prevent accidental repurchase when access exists or payment is
  pending.~~ **Answered:** the return states are `T-074`'s; repurchase while
  access exists was already refused, and while a payment is pending is this
  task's guard.
- ~~Decide bounded implementation slices and file ownership with T-008 and
  checkout.~~ **Answered:** `T-008` is done; `T-102` depends on this task for
  the checkout files; `T-196` and `T-197` are the other slices.
- ~~Specify server and browser cases for new/existing accounts, an existing
  creator arriving as a buyer, free/paid/existing access, unavailable Series,
  changed email, delayed fulfilment and resume. Test forwarded campaign links
  without silently switching the signed-in identity.~~ **Answered:** Tests
  above, and the browser walk in Acceptance. An existing creator arriving as a
  buyer is a signed-in viewer like any other; a changed email is `T-200`'s;
  delayed fulfilment is `T-102`'s.

## Notes

R-003 F-4 supplies the no-access-home evidence; F-1/T-008 supply the confirmed
verification-return failure. Checkout cancellation to the shared index and a
possible browser-return-before-fulfilment refusal were identified in source,
not reproduced as payment findings in R-003. See
[the current onboarding plan](../../design/ui-onboarding.md) and the owner decision for
the target and remaining validation.

**17 September 2026 — [R-004](../../design/reviews/passes/R-004-2026-09-17-final-web-review.md) F-7/F-10.** Fresh receiving cards still omit Group attribution, the completed Episode count and the known named continuation; the empty `/shared` page does not guide the person back to the sender's Series link or the receiving address. Retain R-002's decision to handle this in the receiving composition. Paid entry's “Type it here and you're in” must distinguish email verification from payment (also recorded on T-011). T-073's typed code and T-074's access/payment slices are implemented work to reuse, not missing capabilities. This pass did not repeat the complete registration, code, cross-account return or payment matrix; do not take its static Series form as proof those transitions passed.

- 22 September 2026: an invitation's arrival — its link landing on the
  Series page, the invited address on the code step and the button, checkout
  at the invitation's price — is `T-181`'s (`D-050`). This task keeps the rest
  of the receiving journey.

**23 September 2026 — read fresh before it was marked ready.** An
independent reader checked every name and line against the code and found
two things that would have built the wrong result: `SeriesAccessPending::peek()`
drops any key it does not name, so the guest's zone would never have reached
`verify()`, and "Times show in :timezone." was false, since the page shows
times in the browser's zone. Both are fixed above, with the invitation's
`email` masked in the `ended` and `accepted` states as well, `InvitationOffer.vue`
added to Files, and two invitation cases moved to the file that can set an
invitation up.

**23 September 2026 — found while specifying**, from a read of the code
with a map of the receiving path; each has a home:

- An address typed in capitals makes an account the magic link and a
  password reset cannot find, and a second account on registering →
  draft T-198
- An account the code step made cannot set a password or delete itself
  without "Forgot password" first → draft T-199
- An address change leaves the Peer's old row behind, and the next access
  from that Group makes a second one → draft T-200
- A delayed payment method never becomes access → T-102
- The "Preview" badge on a public Episode opens nothing for a guest → T-011
- `Series.vue` hardcodes the code's length three times, two names for the
  Peer's homes ("Shared with me", "My shared"), and a few stale lines in the
  flow docs → decided: fixups, one line each in `fixups.md`
