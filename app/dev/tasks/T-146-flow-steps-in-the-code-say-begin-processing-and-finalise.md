---
id: T-146
title: The Stripe sign-in's code says payments, begin and finalise
stream: selling
status: done
owner: wayne
estimate: M
depends: none
blocks: none
---

# T-146 — The Stripe sign-in's code says payments, begin and finalise

## Why

Two words in the code describe this flow wrongly.

**Payouts.** Qori charges on the creator's own Stripe account (a direct
charge, `D-023`). A Peer pays the creator, and Stripe pays the creator's bank.
Qori never pays the creator anything, but the code calls the creator's account
"payouts" everywhere: `PayoutsService`, `PayoutsController`, `PayoutDoors`,
`routes/share/payouts.php`, `lang/en/payouts.php`, `errors.payouts.*`, and the
props `payoutsConnected`, `payoutsUrl` and `needsPayouts`. The copy people read
already says "payments" ("Only the owner can change how payments are taken",
"Payments can't be connected here yet"), and so does setup part two
(`share.setup.payments`, `setup/Payments.vue`). The owner, 19 September 2026:
"The creator does not get payout from Qori."

**Return.** `D-032` names a flow's steps `begin`, `processing` and `finalise`,
and says a place to go afterwards is a destination. The Stripe sign-in's
landing is still `PayoutsReturnController` at `u/payouts/stripe/return`, named
`payouts.oauth.return`. Its forwarding address is `PayoutsReturn`, and its
Connect button's step is `PayoutsController::oauth()`. The owner, 19 September
2026: "Return should not be used, just follow the naming convention", and
earlier the same day, "Connect button use begin and finalise also".

Afterwards the creator's Stripe account is **payments** in every code name.
The Connect button's step is `PaymentsController::begin()` at
`g/{group}/payments/stripe/begin`, and the landing is
`PaymentsFinaliseController` at `u/payments/stripe/finalise`. The forwarding
address is `PaymentsDestination`, and `BillsGroups::billingPortalUrl()` takes a
`$destinationUrl`.

## Decisions taken to make this specifiable

**The owner limited this to code: PHP and JavaScript identifiers, route
paths, route names, session keys and lang keys. No text a person reads
changes.** So `series.price_needs_payouts` becomes `series.price_needs_payments`,
but its string, "Nobody can pay for this :series until you connect payouts.",
stays as it is. The same goes for `price_connect_payouts` ("Connect payouts").
Those are the only two strings that say "payouts" to a person, and they are
reported for the owner to decide on. Comments and docblocks are code, so they
change where they call the account a payout account.

**The noun is `payments`, and `Payments` in class names.** The copy and setup
part two already use it. The alternatives were weighed and turned down:

- `Connect` is Stripe's product name, and the vendor's name belongs in
  `app/Integrations/Stripe` only.
- `PaymentAccount` is precise, but it would make three words (payouts,
  payments, payment account) where the copy uses one.
- `Selling` names the stream, not the thing held.

The collision with `CheckoutService` (a Peer paying) is not real. Checkout
stays `checkout`, and `payments` is the creator's side of it.

**`PaymentDoors` is singular, like `PayoutDoors` was.** It names the doors
into payments. The Vue component is `PaymentDoors.vue` for the same reason.

**`ConnectAccount::payoutsEnabled` keeps its name.** It says whether Stripe
will pay the connected account out to its bank, which is true, and it maps
Stripe's own `payouts_enabled`. Stripe paying out to the creator is exactly
the kind of payout that exists. The test fixtures' `payouts_enabled` are
Stripe's field and stay too.

**The landing says `finalise` in all four names, and the forwarding address is
a destination.** `PaymentsFinaliseController`, `payments.oauth.finalise`,
`u/payments/stripe/finalise` and `PaymentsDestination`, with `KEY =
'payments.destination'`. `remember()` and `take()` keep their names, as
`SignInDestination`'s do.

**The Connect button's step says `begin` in all three names.**
`PaymentsController::begin()`, `share.payments.begin` and
`g/{group}/payments/stripe/begin`. `PaymentsService::OAUTH_SESSION` becomes
`payments.oauth`: it names the state of the pending sign-in, not a step.

**The disconnect route moves with the noun.** `DELETE
g/{group}/payments/connection`, `share.payments.disconnect`.

**`$returnUrl` becomes `$destinationUrl`** on `BillsGroups::billingPortalUrl()`,
`Subscription::billingPortalUrl()` and `BillingService::portal()`. Stripe's
`return_url` field stays, because it is Stripe's field in the Stripe folder.

**The composables' `Use…Return` types keep their names.** `UseInitialsReturn`,
`UseTerminologyReturn` and the rest name a function's return value, the same
sense as TypeScript's `ReturnType`. They are not flow steps, and `D-032` is
about steps.

**The old paths are removed, not redirected.** Stripe only sends a person to a
URI on its list, and the owner registers the new one (Preconditions). A
redirect would keep the name this retires. Before beta, nobody is mid-flow. A
round trip that starts before the deploy and lands after it gets a 404.

**The session keys change with the classes, and nothing reads the old ones as
a fallback.** If a forwarding address is left in a session across the deploy,
it is lost. That creator lands on Integrations, the same place a refused
landing sends them.

**Test classes and test names follow the code.** `PayoutsOauthTest` becomes
`PaymentsOauthTest`, and `PayoutsDisconnectTest` becomes
`PaymentsDisconnectTest`. Where a test name uses `return` for the step, it
says `landing` instead, as `T-113`'s tests already do, or `destination` for
the remembered place. Where `return` is the English verb, the name stays
(`test_returning_from_stripe_lands_on_storage`,
`test_a_decline_returns_to_where_the_creator_started`).

**`IntegrationsPageTest::test_the_old_payouts_address_is_gone` stays as it
is.** It guards `/g/{group}/payouts`, a page `T-067` removed. That path is
still gone and still wrong, so the test still holds.

**The old code names join `DocumentationTest::reversedClaims()`.** Then a live
document cannot bring them back. The pattern matches identifiers and paths
only, never the English word "payouts". `docs/project-plan.md` §7.2 and the
tinker heading use that word for Stripe's payouts, and they are prose.

**No decision record.** This follows `D-032` and the owner's instruction
above. It decides nothing new about how the product behaves.

## Preconditions

**Stripe's redirect URIs are the owner's.** Stripe matches `redirect_uri`
exactly against its list. The owner registers
`http://localhost:8001/u/payments/stripe/finalise` in the sandbox (Connect →
Onboarding options → OAuth → Redirect URIs), and later
`https://useqori.com/u/payments/stripe/finalise` in live. If a deploy goes out
before that registration, the Connect Stripe button breaks for every
deployment that has OAuth enabled. None does today (`T-063` is open).

**Wayfinder is generated, not edited.** `resources/js/actions` and
`resources/js/routes` are gitignored. `php artisan wayfinder:generate
--with-form` rewrites them and prunes the stale files. No hand-written Vue or
TS imports a generated payouts helper. The two literal paths
(`PayoutDoors.vue:29` and `Integrations.vue:73`) are edited by hand.

**Data:** a clean test database. **Equipment:** none beyond the test suite.
The real Stripe round trip still waits on `T-063`'s OAuth setting.

## Scope

**In:**

- Every PHP and JS/Vue identifier, file name, route path, route name, session
  key and lang key that says payout or payouts for the creator's account.
- The landing's and the begin step's names under `D-032`, and the
  destination's.
- `$returnUrl` → `$destinationUrl` on the billing portal.
- The tests, flow docs, `CLAUDE.md` sentences and the
  `release-prerequisites.md` line that name any of them.
- `DocumentationTest`'s reversed claims, and two tests that the old paths
  are gone.

**Out:**

- Every string a person reads. That includes the two `series.php` lines that
  still say "payouts", which go to the owner (Notes).
- `ConnectAccount::payoutsEnabled` and Stripe's `payouts_enabled`.
- The other flow-step candidates this draft used to list: `CheckoutService::begin()`,
  `SeriesAccessController::start()`, `ProgressService::complete()`,
  `OnboardingService::complete()`, `HomeController::startSharing()` and the
  webhook's "callback" docblock. The owner asked for Payouts and Return only.
  The recommendation for each is kept under Notes.
- Registering or removing a redirect URI at Stripe. That is the owner's job.
- Task files other than this one, the stream file and reports. The drafts
  that cite the old names (`T-044`, `T-089`, `T-092`, `T-131`) are being
  rewritten in another session's uncommitted work, so their wording is left
  to that session (Notes).
- `PLAN.md`, `decisions.md`, `docs/project-plan.md`: prose, or the owner's.

## Files

| Path                                                           | Change | Notes                                                                                                                              |
| -------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| `app/Services/PayoutsService.php`                              | delete | `git mv` to the row below                                                                                                          |
| `app/Services/PaymentsService.php`                             | new    | class name, `OAUTH_SESSION = 'payments.oauth'`, `errors.payments.*` keys, docblock                                                 |
| `app/Support/PayoutDoors.php`                                  | delete | `git mv` to the row below                                                                                                          |
| `app/Support/PaymentDoors.php`                                 | new    | class name; `payments.*` lang keys                                                                                                 |
| `app/Support/PayoutsReturn.php`                                | delete | `git mv` to the row below                                                                                                          |
| `app/Support/PaymentsDestination.php`                          | new    | class name, `KEY = 'payments.destination'`                                                                                         |
| `app/Http/Controllers/Share/PayoutsController.php`             | delete | `git mv` to the row below                                                                                                          |
| `app/Http/Controllers/Share/PaymentsController.php`            | new    | class name; `oauth()` → `begin()`; `route('payments.oauth.finalise')`; `$payments`; lang keys                                      |
| `app/Http/Controllers/Settings/PayoutsReturnController.php`    | delete | `git mv` to the row below                                                                                                          |
| `app/Http/Controllers/Settings/PaymentsFinaliseController.php` | new    | class name; `$returnTo` → `$destination`; `PaymentsDestination`; `$payments`; lang keys                                            |
| `app/Http/Controllers/Share/IntegrationsController.php`        | edit   | `PaymentsService $payments`, `PaymentDoors`, `payments.*` keys                                                                     |
| `app/Http/Controllers/Share/SetupController.php`               | edit   | imports, `PaymentsService $payments`, `PaymentsDestination::remember()`, `PaymentDoors`                                            |
| `app/Http/Controllers/Share/SeriesController.php`              | edit   | props `paymentsConnected`, `paymentsUrl`, `needsPayments`; `series.price_needs_payments`, `series.price_connect_payments`; comment |
| `app/Http/Controllers/StripeWebhookController.php`             | edit   | `PaymentsService $payments`                                                                                                        |
| `app/Services/CheckoutService.php`                             | edit   | `devMessage` "payment account"                                                                                                     |
| `app/Services/BillingService.php`                              | edit   | `portal(Group $group, string $destinationUrl)`                                                                                     |
| `app/Integrations/Contracts/BillsGroups.php`                   | edit   | `billingPortalUrl(Group $group, string $destinationUrl)`                                                                           |
| `app/Integrations/Stripe/Subscription.php`                     | edit   | the same parameter; `'return_url' => $destinationUrl`                                                                              |
| `app/Console/Commands/DesignReviewCommand.php`                 | edit   | comment                                                                                                                            |
| `database/seeders/DesignReviewSeeder.php`                      | edit   | two docblocks                                                                                                                      |
| `routes/share/payouts.php`                                     | delete | `git mv` to the row below                                                                                                          |
| `routes/share/payments.php`                                    | new    | `payments/stripe/begin` → `begin`, `payments.begin`; `payments/connection` → `payments.disconnect`; comments                       |
| `routes/share.php`                                             | edit   | `require __DIR__.'/share/payments.php'`                                                                                            |
| `routes/share/group.php`                                       | edit   | comment naming `routes/share/payments.php`                                                                                         |
| `routes/settings.php`                                          | edit   | import; `u/payments/stripe/finalise`, `payments.oauth.finalise`; comment                                                           |
| `lang/en/payouts.php`                                          | delete | `git mv` to the row below                                                                                                          |
| `lang/en/payments.php`                                         | new    | same keys and strings; header comment                                                                                              |
| `lang/en/errors.php`                                           | edit   | `'payouts' =>` → `'payments' =>`; section and inline comments                                                                      |
| `lang/en/series.php`                                           | edit   | keys `price_needs_payments`, `price_connect_payments`; strings unchanged                                                           |
| `resources/js/components/share/PayoutDoors.vue`                | delete | `git mv` to the row below                                                                                                          |
| `resources/js/components/share/PaymentDoors.vue`               | new    | link `/g/${slug}/payments/stripe/begin`                                                                                            |
| `resources/js/pages/share/settings/Integrations.vue`           | edit   | import `PaymentDoors`; `disconnectUrl` `/g/${…}/payments/connection`                                                               |
| `resources/js/pages/share/setup/Payments.vue`                  | edit   | import `PaymentDoors`                                                                                                              |
| `resources/js/components/series/SeriesForm.vue`                | edit   | props `paymentsConnected`, `paymentsUrl`, `needsPayments`; the computed is `needsPayments`                                         |
| `resources/js/pages/share/series/Show.vue`                     | edit   | the same three props                                                                                                               |
| `tests/Feature/Share/PayoutsOauthTest.php`                     | delete | `git mv` to the row below                                                                                                          |
| `tests/Feature/Share/PaymentsOauthTest.php`                    | new    | Tests                                                                                                                              |
| `tests/Feature/Share/PayoutsDisconnectTest.php`                | delete | `git mv` to the row below                                                                                                          |
| `tests/Feature/Share/PaymentsDisconnectTest.php`               | new    | Tests                                                                                                                              |
| `tests/Feature/Share/SetupStepsTest.php`                       | edit   | Tests                                                                                                                              |
| `tests/Feature/Checkout/ConnectOnboardingTest.php`             | edit   | Tests                                                                                                                              |
| `tests/Feature/Series/SeriesPriceTest.php`                     | edit   | Tests                                                                                                                              |
| `tests/Feature/Checkout/CheckoutTest.php`                      | edit   | one failure message "no payment account"                                                                                           |
| `tests/Feature/DocumentationTest.php`                          | edit   | one pattern in `reversedClaims()`                                                                                                  |
| `CLAUDE.md`                                                    | edit   | the `D-032` bullet's T-146 sentence goes; `D-033`'s example path; "payment account" in Tenancy                                     |
| `docs/flows/billing.md`                                        | edit   | every code name above                                                                                                              |
| `docs/flows/onboarding.md`                                     | edit   | `PaymentsDestination`, `PaymentDoors`                                                                                              |
| `docs/flows/series.md`                                         | edit   | `routes/share/{…,payments}.php`                                                                                                    |
| `docs/flows/README.md`                                         | edit   | the billing row                                                                                                                    |
| `docs/architecture/tenancy.md`                                 | edit   | "payment account"                                                                                                                  |
| `docs/planning/release-prerequisites.md`                       | edit   | the redirect URI is `…/u/payments/stripe/finalise`                                                                                 |
| `docs/planning/streams/selling.md`                             | edit   | `T-146` in the task list                                                                                                           |

Flows: `docs/flows/billing.md` and `docs/flows/onboarding.md`. `docs/tinker/`
has no recipe that names a changed identifier. `design-review.md`'s heading
says the English word and stays.

## Database

None. No column says payout. `connect_account_id` and
`statement_descriptor_prefix` stay.

## Code

```php
namespace App\Services;

/** A creator's payment account, as Qori holds it (docs/project-plan.md §7.2). */
class PaymentsService
{
    public const OAUTH_SESSION = 'payments.oauth';
    // every method unchanged: account, offersOnboarding, dashboardUrl,
    // beginOnboarding, finaliseOnboarding, disconnect, forget
}

namespace App\Support;

class PaymentDoors
{
    /** @return array{connectLabel: ?string, connectHelp: string, unavailableNote: string, ownerNote: string} */
    public static function props(bool $offered): array; // reads payments.* keys
}

class PaymentsDestination
{
    public const KEY = 'payments.destination';
    public static function remember(string $url): void;
    public static function take(): ?string;
}

namespace App\Http\Controllers\Share;

class PaymentsController extends Controller
{
    public function __construct(private PaymentsService $payments) {}
    public function begin(string $group, CurrentGroup $current): RedirectResponse;      // was oauth()
    public function disconnect(string $group, CurrentGroup $current): RedirectResponse; // unchanged
}

namespace App\Http\Controllers\Settings;

class PaymentsFinaliseController extends Controller
{
    public function __construct(private PaymentsService $payments) {}
    public function __invoke(Request $request): RedirectResponse; // $destination = PaymentsDestination::take()
}

namespace App\Integrations\Contracts;

interface BillsGroups
{
    public function billingPortalUrl(Group $group, string $destinationUrl): string;
}
// BillingService::portal(Group $group, string $destinationUrl): string
```

Constructor properties named `$payouts` become `$payments`. That is in
`IntegrationsController`, `StripeWebhookController` and both payments
controllers, plus `SetupController::payments()`'s injected parameter.
`PaymentsService`'s own `SellsSeries $payments` keeps its name.

The new entry in `DocumentationTest::reversedClaims()`:

```php
'/\bPayouts?(?:Service|Controller|Doors|Return)|payouts\.(?:oauth|return_to|disconnect)|share\.payouts\.|errors\.payouts\.|payouts\/(?:stripe|connection)|share\/payouts\.php|payoutsConnected|needsPayouts/' => 'The creator\'s Stripe account is payments in code: `PaymentsService`, `PaymentsController::begin()` (`share.payments.begin`), `PaymentsFinaliseController` at `u/payments/stripe/finalise` (`payments.oauth.finalise`), `PaymentsDestination` and `PaymentDoors` (T-146, D-032).',
```

## Copy

No string changes. Keys that move:

| Was                                 | Is                                    |
| ----------------------------------- | ------------------------------------- |
| `lang/en/payouts.php` (`payouts.*`) | `lang/en/payments.php` (`payments.*`) |
| `errors.payouts.*`                  | `errors.payments.*`                   |
| `series.price_needs_payouts`        | `series.price_needs_payments`         |
| `series.price_connect_payouts`      | `series.price_connect_payments`       |

## Routes

| Verb   | Path                              | Name                        | Action                          |
| ------ | --------------------------------- | --------------------------- | ------------------------------- |
| GET    | `g/{group}/payments/stripe/begin` | `share.payments.begin`      | `PaymentsController@begin`      |
| DELETE | `g/{group}/payments/connection`   | `share.payments.disconnect` | `PaymentsController@disconnect` |
| GET    | `u/payments/stripe/finalise`      | `payments.oauth.finalise`   | `PaymentsFinaliseController`    |

Removed: `GET g/{group}/payouts/stripe` (`share.payouts.oauth`),
`DELETE g/{group}/payouts/connection` (`share.payouts.disconnect`) and
`GET u/payouts/stripe/return` (`payouts.oauth.return`).

## Tests

**New in `PaymentsOauthTest` — 2 cases**

1. `test_the_old_landing_is_gone`: an owner with a stored nonce gets a 404
   from `GET /u/payouts/stripe/return?code=ac_1&state=nonce-1`. Also checks
   `Http::assertNothingSent()`, that `connect_account_id` stays null, and that
   `Route::has('payouts.oauth.return')` is false.
2. `test_the_old_begin_and_disconnect_paths_are_gone`: the owner gets a 404
   from `GET /g/{slug}/payouts/stripe` and from `DELETE
/g/{slug}/payouts/connection`. Nothing is stored under
   `PaymentsService::OAUTH_SESSION`, `connect_account_id` is unchanged, and
   `Route::has('share.payouts.oauth')` and `Route::has('share.payouts.disconnect')`
   are false.

**Renamed:**

- `PayoutsOauthTest` → `PaymentsOauthTest`, and `PayoutsDisconnectTest` →
  `PaymentsDisconnectTest`
- `test_a_valid_return_stores_the_account_the_creator_chose` →
  `test_a_valid_landing_stores_the_account_the_creator_chose`
- `test_a_return_with_the_wrong_state_connects_nothing` →
  `test_a_landing_with_the_wrong_state_connects_nothing`
- `SeriesPriceTest::test_the_series_page_says_when_payouts_are_not_connected` →
  `test_the_series_page_says_when_payments_are_not_connected`
- `SetupStepsTest::test_the_payments_part_shows_the_connect_button_and_remembers_where_to_return`
  → `test_the_payments_part_shows_the_connect_button_and_remembers_the_destination`

**Changed only in names:** every `route('payouts.oauth.return', …)`,
`route('share.payouts.oauth', …)`, `route('share.payouts.disconnect', …)`,
`PayoutsReturn::KEY`, `PayoutsService`, `__('payouts.…')` and `errors.payouts.…`
in the files above. `PaymentsOauthTest::test_the_owner_is_sent_to_stripe_to_sign_in`
also asserts that `redirect_uri` equals the literal `url('u/payments/stripe/finalise')`,
because that string is what Stripe has registered.
`ConnectOnboardingTest::test_begin_builds_stripes_sign_in_url`'s literal URL
becomes `https://qori.test/u/payments/stripe/finalise`.

Total: 2 new, 4 renamed cases, 2 renamed classes.

## Acceptance

- [x] The Connect Stripe button goes to `GET /g/{group}/payments/stripe/begin` (`share.payments.begin`, `PaymentsController::begin()`); `/g/{group}/payouts/stripe` answers 404
- [x] Disconnect is `DELETE /g/{group}/payments/connection` (`share.payments.disconnect`)
- [x] The landing is `PaymentsFinaliseController` at `GET /u/payments/stripe/finalise` (`payments.oauth.finalise`); `/u/payouts/stripe/return` answers 404
- [x] After `php artisan wayfinder:generate --with-form`, `grep -rniE "payouts?(Service|Controller|Doors|Return)|payouts\.|payouts/|payoutsConnected|payoutsUrl|needsPayouts|returnUrl|returnTo" app routes resources/js lang tests config` finds only `DocumentationTest`'s pattern, the old-path tests, `IntegrationsPageTest`'s old `/payouts` page and `payouts_enabled` fixtures
- [x] No string a person reads changed: `git diff` on `lang/` shows key renames and comments only
- [x] The `ready` specs have been grepped for the old names (PROCESS.md)
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Added during execution

| Path                                                                               | Change | Why                                                                                                                                    |
| ---------------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/planning/tasks/T-131-a-peer-opens-materials-before-and-after-the-session.md` | edit   | Wording: it cited `PayoutsReturnController` and its line numbers as precedent. It is the one citing draft not held by another session. |

## Re-scope log

None.

## Notes

**For the owner, outside this task's scope because the owner kept it to code:**

- `lang/en/series.php` still tells the creator "Nobody can pay for this
  :series until you connect payouts." and offers "Connect payouts". Every
  other string already says payments.
- The drafts `T-044`, `T-089`, `T-091`, `T-092` and `T-094` cite the old
  names as precedent. Another session was rewriting them while this ran, so
  their wording is theirs to fix. `T-131`'s was fixed here.

**Flow-step candidates this draft listed and the owner did not ask for.**
Recommendations as of 19 September 2026, `main` at `25e8793`:

- `CheckoutService::begin()` → `beginCheckout()`. It has no finalise, because
  the webhook's `fulfil()` is the last step.
- `SeriesAccessController::start()`/`verify()` → `begin()`/`finalise()`, with
  the URLs kept.
- `ProgressService::complete()`, `OnboardingService::complete()` and
  `HomeController::startSharing()`: keep all three. They are product concepts,
  not steps of a flow that leaves Qori.
- `StripeWebhookController`'s "Stripe's callback" docblock → "Stripe's webhook".
