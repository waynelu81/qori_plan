---
id: T-113
title: Payouts connect only through Stripe's sign-in
stream: selling
status: done
owner: claude
estimate: M
depends: T-112
blocks: T-114
---

# T-113 — Payouts connect only through Stripe's sign-in

## Why

A creator can get paid through two doors (`D-010`). One creates a Stripe account
for them on Accounts v2 after asking their country
(`App\Integrations\Stripe\Connect::createAccount()`, `onboardingUrl()`,
`PayoutsController::connect()`, `refresh()` and `return()`). The other sends
them to Stripe's OAuth sign-in to connect an account they have
(`Connect::authorizeUrl()`, `exchangeCode()`, `PayoutsReturnController`). The
owner decided on 17 September 2026 that opening a Stripe account is the
creator's concern, and Qori runs only the sign-in that lets them choose
(`D-023`).

Afterwards there is one door. `Connect`'s onboarding is `beginOnboarding()`,
`finaliseOnboarding()` and `declineOnboarding()`, which `finaliseOnboarding()`
calls when the creator stops partway at Stripe. Qori asks no country, creates
no account and mints no account link. The landing's Stripe words are read in
the Stripe folder, not the controller, and a landing Stripe refuses says
nothing was connected instead of reporting an outage.

## Decisions taken to make this specifiable

**`declineOnboarding()` is public on `Connect` and not on the contract.** The
owner named it as one of the three and said `finaliseOnboarding()` calls it.
No Service calls it, so `SellsSeries` does not declare it. It makes no call to
Stripe: a decline at the sign-in leaves nothing at Stripe to undo.

**The contract asks two new questions instead of Services reading Stripe's
config.** `offersOnboarding()` replaces the `services.stripe.client_id` reads
in `app/Support/PayoutDoors.php:26` and `app/Services/PayoutsService.php:139`,
and `dashboardUrl()` gives the Integrations page somewhere to send an
unfinished account. Both keep Stripe's names out of Services and Support
(`D-022`).

**Without a client id, the page says payments cannot be connected, and the
route refuses.** An empty section would look broken, and a redirect with an
empty `client_id` lands on Stripe's error page with no way back.

**An unfinished account is sent to the creator's Stripe dashboard.** Qori can
no longer mint a resume link. "Continue on Stripe" becomes "Open your Stripe
dashboard", opening in a new tab.

**Accounts Qori created before this stay connected.** Nothing clears them. An
owner can disconnect as before.

**The nonce is checked by `Connect` against the value the Service hands it,
and spent by the Service on every landing.** The state parameter and its place
in the query are Stripe's; the session and its value are Qori's. A decline
whose state is present and wrong connects nothing and is refused; a decline
with no state is still a decline, because it stores nothing.

**A landing Stripe refuses is `errors.payouts.connect_failed`, not a 502.** A
4xx from `oauth/token` (an expired or reused code, a test and live mismatch),
a landing with no code, or a landing with an error other than
`access_denied` says nothing was connected and to start again. A 5xx or a
connection failure still reaches `unwrap()` and reports the service as
unavailable.

**A decline returns to where the creator started, like a success.** Today it
always lands on Integrations and leaves setup's forwarding address in the
session, so the next connect from Integrations jumped to setup.

**Names that describe the page stay.** The route `share.payouts.oauth`, the
action `PayoutsController::oauth()`, `PayoutDoors` and `PayoutsReturn` keep
their names, so the Vue and the drafts citing them move less.

**`Client::getClientV2()` is deleted.** Its only callers were
`createAccount()` and `onboardingUrl()`. `unwrap()` is unchanged.

## Preconditions

**Data this task verifies against:** a clean database for the tests. For the
browser check, a probe owner whose Group has no `connect_account_id`, deleted
afterwards.

**Equipment:** a browser. No Stripe sandbox: OAuth is not enabled in the
sandbox and `STRIPE_CLIENT_ID` is not set locally (17 September 2026), so the
round trip is verified with faked Stripe responses only. The token response
shape is the one `PayoutsOauthTest` already fakes from `T-063`
(`stripe_user_id`). The landing's `error=access_denied` comes from Stripe's
Connect OAuth reference and has not been captured from a real decline.

## Scope

**In:**

- The six methods and two questions on `Connect` and `SellsSeries`, and
  removing account creation and account links.
- `PayoutsService`, the two payouts controllers, `IntegrationsController` and
  `SetupController::payments()` on the new contract.
- One door on the Integrations page and in setup part two; the dashboard link
  for an unfinished account.
- Deleting `ConnectPayoutsRequest`, three routes, the country config, their
  lang keys and their tests.
- The live docs and planning documents that describe two doors.

**Out:**

- `PLAN.md`'s "Waiting on the owner" line: the owner's file. The report asks
  for it.
- Disconnecting an account Qori created, if Stripe refuses to deauthorise it.
  Unverified; a finding in the report.
- The direct-charge refactor and the webhook findings.
- `ConnectAccount::fromStripe()` moving into the Stripe folder (`D-022`).
- The purge command's behaviour. Only its comments naming `createAccount()`
  change.

## Files

| Path                                                           | Change | Notes                                                                                                                                                                                                             |
| -------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/Integrations/Contracts/SellsSeries.php`                   | edit   | the contract below                                                                                                                                                                                                |
| `app/Integrations/Stripe/Connect.php`                          | edit   | the methods below; `createAccount()`, `onboardingUrl()`, `authorizeUrl()`, `exchangeCode()` go; class docblock                                                                                                    |
| `app/Integrations/Stripe/Client.php`                           | edit   | delete `getClientV2()`                                                                                                                                                                                            |
| `app/Data/OnboardingOutcome.php`                               | new    |                                                                                                                                                                                                                   |
| `app/Enums/OnboardingStatus.php`                               | new    |                                                                                                                                                                                                                   |
| `app/Services/PayoutsService.php`                              | edit   | `connectUrl()`, `refreshUrl()` go; `authorizeUrl()` and `completeAuthorization()` become `beginOnboarding()` and `finaliseOnboarding()`; `offersOnboarding()`, `dashboardUrl()`; `disconnect()` asks the contract |
| `app/Http/Controllers/Share/PayoutsController.php`             | edit   | `connect()`, `refresh()`, `return()` go; `oauth()` calls `beginOnboarding()`; docblocks                                                                                                                           |
| `app/Http/Controllers/Settings/PayoutsReturnController.php`    | edit   | hands the query to the Service; one toast match; forwarding address on every outcome                                                                                                                              |
| `app/Http/Controllers/Share/IntegrationsController.php`        | edit   | `PayoutDoors::props()` argument; `dashboardUrl`, `dashboardLabel`                                                                                                                                                 |
| `app/Http/Controllers/Share/SetupController.php`               | edit   | `payments()` method-injects `PayoutsService`                                                                                                                                                                      |
| `app/Http/Requests/Share/ConnectPayoutsRequest.php`            | delete |                                                                                                                                                                                                                   |
| `app/Support/PayoutDoors.php`                                  | edit   | one door                                                                                                                                                                                                          |
| `app/Support/PayoutsReturn.php`                                | edit   | docblock                                                                                                                                                                                                          |
| `app/Console/Commands/StripePurgeConnectedAccountsCommand.php` | edit   | comments only                                                                                                                                                                                                     |
| `routes/share/payouts.php`                                     | edit   | `payouts.connect`, `payouts.refresh`, `payouts.return` go; comments                                                                                                                                               |
| `routes/settings.php`                                          | edit   | the landing's comment                                                                                                                                                                                             |
| `config/qori.php`                                              | edit   | `payments.countries`, `payments.default_country` and their comment go; `reachability.allowed` becomes empty                                                                                                       |
| `config/services.php`                                          | edit   | comments                                                                                                                                                                                                          |
| `.env.example`                                                 | edit   | `QORI_PAYMENTS_COUNTRY` goes; the Stripe comment says the client id is required                                                                                                                                   |
| `lang/en/payouts.php`                                          | edit   | the Copy table                                                                                                                                                                                                    |
| `lang/en/errors.php`                                           | edit   | the Copy table                                                                                                                                                                                                    |
| `resources/js/components/share/PayoutDoors.vue`                | edit   | one door                                                                                                                                                                                                          |
| `resources/js/pages/share/settings/Integrations.vue`           | edit   | props; dashboard link                                                                                                                                                                                             |
| `resources/js/pages/share/setup/Payments.vue`                  | edit   | props                                                                                                                                                                                                             |
| `tests/Feature/Share/PayoutsConnectTest.php`                   | delete |                                                                                                                                                                                                                   |
| `tests/Feature/Share/PayoutsReturnTest.php`                    | delete |                                                                                                                                                                                                                   |
| `tests/Feature/Checkout/ConnectOnboardingTest.php`             | edit   | 4 cases go, 4 come                                                                                                                                                                                                |
| `tests/Feature/Share/PayoutsOauthTest.php`                     | edit   | 1 rewritten, 8 new                                                                                                                                                                                                |
| `tests/Feature/Share/PayoutsDisconnectTest.php`                | edit   | 1 rewritten                                                                                                                                                                                                       |
| `tests/Feature/Share/SetupStepsTest.php`                       | edit   | 2 rewritten                                                                                                                                                                                                       |
| `docs/flows/billing.md`                                        | edit   | one door; the landing's outcomes                                                                                                                                                                                  |
| `docs/flows/checkout.md`                                       | edit   | nothing uses v2                                                                                                                                                                                                   |
| `docs/flows/onboarding.md`                                     | edit   | one door                                                                                                                                                                                                          |
| `docs/tinker/design-review.md`                                 | edit   | the account comes from Stripe's sign-in                                                                                                                                                                           |
| `docs/project-plan.md`                                         | edit   | §7: the creator brings or opens their own account                                                                                                                                                                 |
| `docs/planning/release-prerequisites.md`                       | edit   | OAuth is required, v2 creation retired                                                                                                                                                                            |

## Database

None.

## Code

```php
namespace App\Enums;

enum OnboardingStatus: string
{
    case Connected = 'connected';
    case Declined = 'declined';
    case Failed = 'failed';
    case NotFromQori = 'not_from_qori';
}

namespace App\Data;

class OnboardingOutcome
{
    public function __construct(
        public OnboardingStatus $status,
        public ?string $accountId = null,
    ) {}

    public static function connected(string $accountId): self;
    public static function declined(): self;
    public static function failed(): self;
    public static function notFromQori(): self;
}

namespace App\Integrations\Contracts;

interface SellsSeries
{
    /** Whether a creator can be sent to the vendor to connect: its sign-in is configured. */
    public function offersOnboarding(): bool;

    /** Where to send the owner to sign in to, or open, their own account. $state comes back on the landing. */
    public function beginOnboarding(Group $group, string $redirectUrl, string $state): string;

    /**
     * Read the landing the vendor sent the owner back with.
     *
     * @param  array<string, mixed>  $landing
     */
    public function finaliseOnboarding(array $landing, string $expectedState): OnboardingOutcome;

    public function account(string $accountId): ConnectAccount;

    /** Where a creator manages their own account at the vendor. */
    public function dashboardUrl(): string;

    public function deauthorize(string $accountId): void;

    public function checkoutFor(Series $series, Group $group, User $peer, string $successUrl, string $cancelUrl): HostedCheckout;
}

namespace App\Integrations\Stripe;

class Connect implements SellsSeries
{
    public const DASHBOARD_URL = 'https://dashboard.stripe.com/';

    public function __construct(private Client $client) {}

    public function offersOnboarding(): bool; // filled(config('services.stripe.client_id'))

    /** The authorize URL today's authorizeUrl() builds, unchanged. No call is sent. */
    public function beginOnboarding(Group $group, string $redirectUrl, string $state): string;

    /**
     * In order:
     * 1. error === 'access_denied': a present, non-matching state returns notFromQori(); otherwise return $this->declineOnboarding($landing).
     * 2. any other non-empty error: failed().
     * 3. state missing, $expectedState === '', or ! hash_equals($expectedState, $state): notFromQori().
     * 4. blank code: failed().
     * 5. POST oauth/token (grant_type=authorization_code, code) through getClientOAuth():
     *    a 4xx is failed(); otherwise connected((string) unwrap(...)['stripe_user_id']).
     * @param  array<string, mixed>  $landing
     */
    public function finaliseOnboarding(array $landing, string $expectedState): OnboardingOutcome;

    /**
     * The creator stopped partway at Stripe. Nothing at Stripe to undo.
     * @param  array<string, mixed>  $landing
     */
    public function declineOnboarding(array $landing): OnboardingOutcome; // OnboardingOutcome::declined()

    public function account(string $accountId): ConnectAccount; // unchanged
    public function dashboardUrl(): string; // self::DASHBOARD_URL
    public function deauthorize(string $accountId): void; // unchanged
    public function checkoutFor(/* unchanged */): HostedCheckout;
}

namespace App\Services;

class PayoutsService
{
    public const OAUTH_SESSION = 'payouts.oauth';

    public function account(Group $group): ?ConnectAccount; // unchanged
    public function offersOnboarding(): bool;
    public function dashboardUrl(): string;

    /**
     * Refuses with AppException::unsupported('errors.payouts.onboarding_unavailable')
     * when ! offersOnboarding(); otherwise stores the nonce and group as today.
     */
    public function beginOnboarding(Group $group, string $redirectUrl): string;

    /**
     * The stored group_id must match the Group, or forbidden('errors.payouts.oauth_state').
     * Forgets OAUTH_SESSION, then asks the contract with the stored state (or '').
     * Declined: null. NotFromQori: forbidden('errors.payouts.oauth_state').
     * Failed: invalidRequest('errors.payouts.connect_failed').
     * Connected: saves connect_account_id and returns read().
     *
     * @param  array<string, mixed>  $landing
     */
    public function finaliseOnboarding(Group $group, array $landing): ?ConnectAccount;

    public function disconnect(Group $group): void; // deauthorises when offersOnboarding(), then clears
    public function forget(string $accountId): int; // unchanged
}

namespace App\Support;

class PayoutDoors
{
    /** @return array{connectLabel: ?string, connectHelp: string, unavailableNote: string, ownerNote: string} */
    public static function props(bool $offered): array;
}
```

`PayoutsReturnController::__invoke()` keeps the Group lookup and the owner
check, then calls `finaliseOnboarding($group, $request->query())`, flashes
`payouts.declined` (info) for null, `payouts.connected` (success) when the
account can sell and `payouts.pending` (info) otherwise, and redirects to
`PayoutsReturn::take()` or `share.settings.integrations`.

`IntegrationsController::show()` adds `dashboardUrl` (the Service's
`dashboardUrl()` when the status is `incomplete` or `pending`, else null) and
`dashboardLabel` (`payouts.open_dashboard`).

`PayoutDoors.vue` props: `slug`, `isOwner`, `connectLabel: string | null`,
`connectHelp`, `unavailableNote`, `ownerNote`. An owner with a label sees the
link to `/g/{slug}/payouts/stripe` and the help line; an owner without one
sees `unavailableNote`; anyone else sees `ownerNote`. `Integrations.vue`
replaces the refresh link with an external link to `dashboardUrl`
(`target="_blank"`, `rel="noopener noreferrer"`) labelled `dashboardLabel`.

## Copy

| Key                                             | File                  | English                                                                                                               |
| ----------------------------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `payouts.connect`                               | `lang/en/payouts.php` | Connect Stripe                                                                                                        |
| `payouts.connect_help`                          | `lang/en/payouts.php` | Stripe's own page lets you sign in to the account you have or open a new one, and asks there for everything it needs. |
| `payouts.unavailable`                           | `lang/en/payouts.php` | Payments can't be connected here yet.                                                                                 |
| `payouts.open_dashboard`                        | `lang/en/payouts.php` | Open your Stripe dashboard                                                                                            |
| `payouts.incomplete`                            | `lang/en/payouts.php` | Stripe doesn't have everything it needs yet. Finish setting up in your Stripe dashboard.                              |
| `errors.payouts.connect_failed.message`         | `lang/en/errors.php`  | Your payment account wasn't connected.                                                                                |
| `errors.payouts.connect_failed.resolution`      | `lang/en/errors.php`  | Start again from Integrations.                                                                                        |
| `errors.payouts.onboarding_unavailable.message` | `lang/en/errors.php`  | Payments can't be connected here yet.                                                                                 |

Removed: `payouts.ready`, `payouts.create_new`, `payouts.connect_existing`,
and the unused `errors.checkout.connect_failed`.
`errors.payouts.onboarding_unavailable` has no resolution: nothing the creator
does changes it.

## Routes

Removed:

| Verb | Path                         | Name                    | Action                      |
| ---- | ---------------------------- | ----------------------- | --------------------------- |
| POST | `/g/{group}/payouts/connect` | `share.payouts.connect` | `PayoutsController@connect` |
| GET  | `/g/{group}/payouts/refresh` | `share.payouts.refresh` | `PayoutsController@refresh` |
| GET  | `/g/{group}/payouts/return`  | `share.payouts.return`  | `PayoutsController@return`  |

Unchanged: `GET /g/{group}/payouts/stripe` (`share.payouts.oauth`),
`DELETE /g/{group}/payouts/connection` (`share.payouts.disconnect`),
`GET /u/payouts/stripe/return` (`payouts.oauth.return`).

## Tests

**Deleted:** `tests/Feature/Share/PayoutsConnectTest.php` (9 cases) and
`tests/Feature/Share/PayoutsReturnTest.php` (3 cases), which cover only the
removed routes. From `ConnectOnboardingTest`:
`test_it_creates_the_account_on_the_v2_endpoint`,
`test_the_owner_email_travels_as_contact_email`,
`test_it_sends_an_api_version_that_serves_v2` and
`test_the_account_link_nests_its_urls_under_use_case`.

**New in `tests/Feature/Checkout/ConnectOnboardingTest.php` — 4 cases**

1. `test_begin_builds_stripes_sign_in_url` — `response_type`, `client_id`,
   `scope=read_write`, `state`, `redirect_uri` and `stripe_user[email]`;
   nothing sent.
2. `test_finalise_exchanges_the_code_for_the_account_id` — `connected` with
   `stripe_user_id`; the token call is form-encoded with `grant_type` and
   `code`.
3. `test_a_creator_who_stops_partway_is_declined` — `error=access_denied`
   returns what `declineOnboarding()` returns; nothing sent.
4. `test_finalise_refuses_a_state_that_does_not_match` — `not_from_qori`;
   nothing sent.

**New in `tests/Feature/Share/PayoutsOauthTest.php` — 8 cases**

5. `test_starting_the_sign_in_without_a_client_id_is_refused` — 400, and no
   nonce stored.
6. `test_a_decline_carrying_another_state_connects_nothing` — 403.
7. `test_a_decline_returns_to_where_the_creator_started` — with a forwarding
   address remembered, the decline redirects there and spends it.
8. `test_a_landing_without_a_code_connects_nothing` — `connect_failed`, no
   token call.
9. `test_a_code_stripe_refuses_says_nothing_was_connected` — a faked 400
   `invalid_grant` from `oauth/token` gives `connect_failed`, and the column is
   unchanged.
10. `test_a_landing_with_another_error_connects_nothing` —
    `error=invalid_request` gives `connect_failed`, no token call.
11. `test_an_unfinished_account_is_sent_to_the_stripe_dashboard` — an
    incomplete account's page has `dashboardUrl` and `dashboardLabel`; a ready
    one has `dashboardUrl` null.
12. `test_the_create_account_routes_are_gone` — the three removed paths answer
    404 or 405.

**Changed:**

- `PayoutsOauthTest::test_the_existing_account_door_needs_the_client_id`
  becomes `test_the_connect_button_needs_the_client_id`: `connectLabel` is null
  without a client id, with `unavailableNote` present, and
  `payouts.connect` with one.
- `PayoutsDisconnectTest::test_after_disconnecting_the_button_creates_a_fresh_account`
  becomes `test_after_disconnecting_the_page_offers_the_sign_in_again`.
- `SetupStepsTest::test_the_payments_part_shows_both_doors_and_remembers_where_to_return`
  becomes `test_the_payments_part_shows_the_connect_button_and_remembers_where_to_return`.
- `SetupStepsTest::test_returning_from_stripe_lands_on_storage` lands through
  `payouts.oauth.return` with a stored nonce, a faked token and a faked v1
  account.
- Every other case in `PayoutsOauthTest`, `PayoutsDisconnectTest`,
  `IntegrationsPageTest`, `SeriesPriceTest`, `ReachabilityTest` and
  `EnvExampleTest` passes unchanged.

Total new: 12. Deleted: 16. Rewritten: 4.

## Acceptance

- [x] Nothing in `app/`, `routes/`, `config/` or `resources/js` creates a Stripe account, mints an account link or asks a country
- [x] `Connect`'s onboarding is `beginOnboarding()`, `finaliseOnboarding()` and `declineOnboarding()`, and the controller no longer reads Stripe's landing words
- [x] The Integrations page and setup part two show one Connect Stripe button with a client id, and the unavailable sentence without one (browser, both)
- [x] An unfinished account's page links to the Stripe dashboard
- [x] The report asks the owner to enable OAuth in the sandbox and live, register the redirect URI, set `STRIPE_CLIENT_ID`, and update `PLAN.md`'s waiting line
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Added during execution

| Path                                   | Change | Notes                                                                                               |
| -------------------------------------- | ------ | --------------------------------------------------------------------------------------------------- |
| `resources/views/errors/400.blade.php` | new    | Qori's page for `onboarding_unavailable`; the ErrorCode's existing copy                             |
| `resources/views/errors/422.blade.php` | new    | Qori's page for `connect_failed`                                                                    |
| `resources/views/errors/502.blade.php` | new    | Qori's page when Stripe does not answer the exchange                                                |
| `tests/Feature/ErrorPagesTest.php`     | edit   | its example of a status with no view moves from 422 to 504; one case asserts the three pages render |

## Re-scope log

None.

## Notes

Wording and departures, found in execution (17 September 2026):

- A connection failure on `oauth/token` cannot reach `unwrap()`: without a
  retry, `post()` throws first. `finaliseOnboarding()` catches it and throws
  `upstream_unavailable` itself.
- "A landing Stripe refuses says nothing was connected" needed the error views
  under **Added during execution**; without them the landing, a GET, showed the
  framework's bare page with debug off.
- The forwarding address is spent before anything in the landing can throw,
  not only on outcomes the Service returns.
- The page with a client id was checked by tests, not in a browser: no client
  id is configured locally. The browser checked the page without one.

Written from the owner's instruction of 17 September 2026: "beginOnboarding do
not create stripe account, that's user's concern. Only do OAuth v2 flow to
allow user to choose. declineOnboarding is call from finaliseOnboarding where
user decline the onboarding mid way." Read as Stripe Connect's OAuth 2.0 flow;
Stripe has no separate OAuth v2. The owner, as the stream's owner, gave it as
approval to build.
