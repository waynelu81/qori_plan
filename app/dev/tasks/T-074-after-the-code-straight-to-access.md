---
id: T-074
title: After the code, straight to access
stream: onboarding
status: done
owner: claude
estimate: M
depends: T-073
blocks: none
---

# T-074 — After the code, straight to access

## Why

`T-073` gets a stranger signed in on the Series page. It still leaves them one
click short: the consent box and the access button, which they already meant
when they typed their name. The owner's words on 13 September 2026 were "get
them register and get to payment quickly". So the consent moves onto the form
they fill first, travels with the pending step, and the moment the code is
right the page does what the button would have done: grants a free Series and
opens it, or sends them to pay for a paid one.

Two more pieces of the same journey are wrong today and were found reading the
code, not in a browser. Stripe's success URL is the shared Series page, which
refuses anybody without access; when the browser comes back before the webhook
has granted it, the buyer who has just paid sees a 403. And the cancel URL is
the shared index, a page listing nothing, when the person was standing on the
Series they decided not to buy.

## Decisions taken to make this specifiable

**Consent is asked once, on the first form.** The box moves from beside the
button to the name and email form, still required, still the sentence from
`accesses.consent.peer`. It is stored in the pending step as `consented: true`
and read at continuation. For a signed-in person the button's own box stays.

**Continuation is the same code the buttons run.** Free: `AccessService::selfGrant()`
then `shared.show`. Paid: `CheckoutService::begin()` then `Inertia::location()`,
because the verify form is an Inertia form (`T-071`).

**A payment is remembered while it settles.** `CheckoutController::store()`
puts `checkout.pending.{seriesId}` in the session with the time before sending
the buyer to Stripe. `SharedController::show()` with no access and that marker
present renders a confirming page rather than refusing; without the marker it
refuses as it does now. The marker is forgotten once access exists or after
`CONFIRMING_MINUTES`.

**The confirming page asks the server, not the buyer.** It reloads itself
every three seconds through Inertia's partial reload until access appears,
offers a manual "Check again", and never offers to buy. After two minutes it
adds a line saying the receipt from Stripe means the payment went through and
access follows.

**Cancel lands on the Series.** `cancel_url` becomes `series.public` for the
Series with a `checkout.cancelled` toast.

## Preconditions

`T-073` done: the pending step, the code and the guest form exist.

## Scope

**In:**

- Consent on the guest form; continuation after a right code.
- The pending-payment marker, the confirming page and its copy.
- The cancel URL and its toast.
- `docs/flows/checkout.md` "The path back".

**Out:**

- Any change to fulfilment: the webhook grants, this task only waits for it.
- Anything on the sign-in page.

## Files

| Path                                                | Change | Notes                                            |
| --------------------------------------------------- | ------ | ------------------------------------------------ |
| `app/Support/SeriesAccessPending.php`               | edit   | `consented` in the shape                         |
| `app/Http/Requests/StartSeriesAccessRequest.php`    | edit   | `consent` accepted                               |
| `app/Http/Controllers/SeriesAccessController.php`   | edit   | `verify()` continues; constructor gains services |
| `app/Support/CheckoutPending.php`                   | new    | The marker                                       |
| `app/Http/Controllers/CheckoutController.php`       | edit   | Marker; cancel URL                               |
| `app/Http/Controllers/Shared/SharedController.php`  | edit   | Confirming branch                                |
| `resources/js/pages/shared/Confirming.vue`          | new    | Title, spinner, reload, Check again              |
| `resources/js/pages/public/Series.vue`              | edit   | Consent on the guest form                        |
| `lang/en/accesses.php`                              | edit   | `confirming.*`, `checkout_cancelled`             |
| `docs/flows/checkout.md`                            | edit   | The path back                                    |
| `tests/Feature/Access/SeriesAccessContinueTest.php` | new    | 6 cases                                          |
| `tests/Feature/Checkout/ConfirmingTest.php`         | new    | 5 cases                                          |

## Database

None.

## Code

```php
// App\Support\SeriesAccessPending — shape gains consented: bool
public static function remember(Series $series, User $user, bool $consented): void;
```

```php
// App\Http\Controllers\SeriesAccessController::verify(), after Auth::login()
if ($series->isFree()) {
    $this->accesses->selfGrant($series, $user);          // consent already recorded in the step
    return to_route('shared.show', (string) $series->getKey());
}
$session = $this->checkout->begin($series, $user, route('shared.show', $id), route('series.public', [$group->slug, $series->slug]));
CheckoutPending::mark($series);
return Inertia::location($session->url);
```

`selfGrant()` today reads consent from `GrantInSeriesRequest`; check its
signature and, if consent is a parameter, pass the recorded value. The
constructor gains `AccessService $accesses` and `CheckoutService $checkout`.
The method's return type widens to `Symfony\Component\HttpFoundation\Response`.

```php
namespace App\Support;

class CheckoutPending
{
    public const CONFIRMING_MINUTES = 30;
    public static function mark(Series $series): void;      // session 'checkout.pending.'.$id => now()->toIso8601String()
    public static function since(Series $series): ?Carbon;  // null when absent or older than CONFIRMING_MINUTES
    public static function forget(Series $series): void;
}
```

```php
// App\Http\Controllers\Shared\SharedController::show(), where it refuses today
if ($access === null && CheckoutPending::since($series) !== null) {
    return Inertia::render('shared/Confirming', [
        'series' => ['id' => …, 'title' => …],
        'startedAt' => CheckoutPending::since($series)->toIso8601String(),
        'copy' => [ 'title' => __('accesses.confirming.title'), 'body' => __('accesses.confirming.body'),
                    'slow' => __('accesses.confirming.slow'), 'check' => __('accesses.confirming.check') ],
    ]);
}
// and where access is found: CheckoutPending::forget($series);
```

`CheckoutController::store()` calls `CheckoutPending::mark($model)` and passes
`route('series.public', [$model->group->slug, $model->slug, 'cancelled' => 1])`
as the cancel URL. Stripe returns to it by a plain GET, so Qori cannot flash
anything before the redirect; `PublicSeriesController::show()` flashes
`accesses.checkout_cancelled` when it sees `cancelled=1` and the viewer is
signed in, and forgets the pending-payment marker.

`Confirming.vue`: `router.reload({ only: [] })` every 3000 ms while mounted;
the `slow` line appears when `Date.now() - startedAt` exceeds 120 s; a Check
again `Button` calls the same reload.

## Copy

| Key                           | File                   | English                                                                                                     |
| ----------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| `accesses.confirming.title`   | `lang/en/accesses.php` | Confirming your payment                                                                                     |
| `accesses.confirming.body`    | `lang/en/accesses.php` | This usually takes a few seconds. Stay here and the :series will open on its own.                           |
| `accesses.confirming.slow`    | `lang/en/accesses.php` | Taking longer than usual. If Stripe has emailed you a receipt, the payment went through and access follows. |
| `accesses.confirming.check`   | `lang/en/accesses.php` | Check again                                                                                                 |
| `accesses.checkout_cancelled` | `lang/en/accesses.php` | Nothing was charged. The :series is here whenever you're ready.                                             |

`body` and `checkout_cancelled` go through `Terminology::line()` with the
Series's Group, so `:series` is that Group's word.

## Routes

None new. `series.public` gains the optional `cancelled` query parameter.

## Tests

**New: `tests/Feature/Access/SeriesAccessContinueTest.php` — 6 cases**

1. `test_consent_is_required_on_the_first_form` — POST start without `consent`:
   validation error on `consent`, no user created, no code sent.
2. `test_a_free_series_is_granted_the_moment_the_code_is_right` — verify:
   an active Access exists for the user, 302 to `shared.show`.
3. `test_a_paid_series_goes_to_stripe_the_moment_the_code_is_right` — Group
   with a connected account, Checkout faked: verify with the `X-Inertia`
   header answers 409 with `X-Inertia-Location` set to the session URL, and
   the pending-payment marker is in the session.
4. `test_a_paid_series_without_a_connected_account_is_refused_after_sign_in` —
   verify: signed in, `errors.checkout.not_connected`, back on the Series page.
5. `test_the_recorded_consent_reaches_the_peer_row` — after case 2, the Peer
   row for the user in the Group carries consent.
6. `test_a_signed_in_person_still_uses_the_button` — POST grant as a user with
   consent: unchanged behaviour.

**New: `tests/Feature/Checkout/ConfirmingTest.php` — 5 cases**

1. `test_starting_checkout_remembers_the_payment` — POST checkout: session
   marker present; the session's `cancel_url` is the Series page with
   `cancelled=1`.
2. `test_coming_back_before_the_webhook_shows_confirming_not_a_refusal` — GET
   `shared.show` with the marker and no access: 200, component
   `shared/Confirming`.
3. `test_coming_back_with_no_payment_in_progress_is_still_refused` — GET
   without the marker: 403 as today.
4. `test_once_access_exists_the_marker_is_forgotten` — grant, GET: the Series
   page, marker gone.
5. `test_cancelling_lands_on_the_series_with_a_note` — GET `series.public`
   with `cancelled=1` signed in: `accesses.checkout_cancelled` flashed.

## Acceptance

- [x] Signed out on a phone-width window, a stranger reaches Stripe's payment
      page from the Series page with a name, an email, a tick and a code, and
      nothing else
- [x] A free Series opens the moment the code is right
- [x] Coming back from Stripe before the webhook shows "Confirming your
      payment", which turns into the Series on its own
- [x] Cancelling at Stripe lands back on the Series with "Nothing was charged"
- [ ] Sandbox: one real purchase with `4242 4242 4242 4242` walked end to end — **not run on 13 September 2026: typing a card number into Stripe's form is the owner's to do; the path reached Stripe's checkout with the email filled in, and the confirming page was seen polling (report)**
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Cut from `T-027` on 13 September 2026 as its second slice. The confirming
state is the one `ui-onboarding.md` asked for under "Specify a
payment-confirmation state for a browser that returns before the webhook".

The public Series page still shows a buy button for a Series whose Group has
disconnected Stripe (found on `T-064`); case 4 above is what a buyer meets
then. A separate task should hide the button when `canSell()` is false.
