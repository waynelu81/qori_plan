---
id: T-063
title: Connect the Stripe account a creator already has
stream: selling
status: done
owner: claude
estimate: M
depends: T-062
blocks: none
---

# T-063 — Connect the Stripe account a creator already has

## Why

About half of creators already hold a Stripe account. That is the owner's
figure from six years of e-commerce, given on 13 September 2026, and the
direction with it: offer to connect the account they have, without a second
KYC, beside creating a new one. Today the only door creates a new connected
account under Qori. Stripe's networked onboarding softens that by letting the
owner copy a verified legal entity into the new account, but it is still a new
account.

The flow Stripe provides for "use the account I have" is OAuth: Qori sends the
creator to Stripe, they sign in and pick an account or create one there, and
Stripe returns the account id. Stripe's own words: "The process of creating a
Stripe account is incorporated into our authorization flow. You don't need to
worry about whether or not your users already have accounts." The end state is
the same column direct charges already read, `groups.connect_account_id`
holding an `acct_…`, and `checkoutFor()` runs on it unchanged.

Two facts from Stripe's docs shape the build, and both are decisions to record:

- The Accounts v2 page lists OAuth under "you must use Accounts v1". Creation
  stays on v2 (`T-062`); OAuth runs beside it on Stripe's OAuth endpoints.
- The same page says a v2 account id "can still" be passed to a v1 endpoint and
  is answered in the v1 shape. So reading an account back moves to
  `GET /v1/accounts/{id}` for every account, whichever door it came through,
  and `ConnectAccount` reads `charges_enabled`, `payouts_enabled`,
  `details_submitted`, `country` and `default_currency` from that shape. One
  reader, and it is the shape Checkout lives in.

Stripe also says OAuth "isn't recommended for new Connect platforms", must be
switched on in the dashboard, and since June 2021 cannot connect a Standard
account that another platform controls. None of that stops a creator
connecting their own account, which is the case here.

## Decisions taken to make this specifiable

**Callback without a group in the path.** Stripe matches `redirect_uri` exactly
against the list in the dashboard, so the landing route cannot carry
`{group}`. It lives under `/u/`, which is where a person's own account actions
go, and the Group travels in `state`. The handler resolves the Group, checks
the signed-in user owns it, and only then exchanges the code.

**State is a session nonce.** `Str::random(40)` and the Group id are stored in
the session under `payouts.oauth` before the redirect out; the return compares
with `hash_equals` and refuses a mismatch with `errors.payouts.oauth_state`.

**The client id is configuration.** `services.stripe.client_id` from
`STRIPE_CLIENT_ID`. `.env.example` gains the line. `.env.testing` does not
(no `STRIPE_*` there, by rule); tests set it with `config([...])`.

**Disconnect finishes at Stripe.** `T-064` makes disconnect "Qori forgets".
With a client id available, `PayoutsService::disconnect()` first posts to
`/oauth/deauthorize`, which Stripe documents for any account with dashboard
access, and then clears the id. Without a client id it skips the call and only
clears, so `T-064` keeps working where OAuth was never enabled.

**A declined sign-in is not an error.** Stripe returns `error=access_denied`
to the same URL; the handler sends the creator back to the page with
`payouts.declined` as an info toast and stores nothing.

## Preconditions

The owner, in the Stripe sandbox dashboard: enable OAuth under Connect
onboarding options, add `http://localhost:8001/u/payouts/stripe/return` to the
redirect URIs, and put the sandbox `ca_…` in `.env` as `STRIPE_CLIENT_ID`. The
code and its tests can be written without this; the sandbox acceptance line
cannot be ticked without it, and the report must say if it was not.

`T-062` done: the POST form and the one-question creation this task's second
door sits beside (the country stays Qori's question; `T-062`'s re-scope log
says why). `T-064`'s `disconnect()` is what gains the deauthorize call.

## Scope

**In:**

- The OAuth start and return routes and handlers.
- `stripeOAuth()` on the HTTP trait; `authorizeUrl()`, `exchangeCode()` and
  `deauthorize()` on the contract and the integration.
- Reading every account through v1, and `ConnectAccount` reading the v1 shape.
- A third page state, `incomplete`, for an account whose form was never
  finished: `details_submitted` false and `charges_enabled` false. The owner
  saw "Stripe is still checking your details. Nothing to do" on 13 September
  after leaving Stripe's form at its first screen, when the one thing to do was
  go back. `pending` keeps its copy for the case it was written for: details
  submitted, Stripe still deciding.
- The deauthorize call inside `disconnect()`, guarded by the client id.
- The page offering both doors, from lang.
- `decisions.md`, `docs/flows/checkout.md`, `release-prerequisites.md`.

**Out:**

- Any change to how a new account is created (`T-062`).
- A "which door did this come through" column. Nothing needs it: the read is
  unified and deauthorize is guarded by configuration, not by provenance.
- Storage, video and meeting OAuth (`T-044`). Same shape, different table,
  different task.

## Files

| Path                                                        | Change | Notes                                                                      |
| ----------------------------------------------------------- | ------ | -------------------------------------------------------------------------- |
| `routes/share.php`                                          | edit   | `payouts/stripe` start                                                     |
| `routes/settings.php`                                       | edit   | `u/payouts/stripe/return`                                                  |
| `app/Http/Controllers/Share/PayoutsController.php`          | edit   | `oauth()`; props for the two doors                                         |
| `app/Http/Controllers/Settings/PayoutsReturnController.php` | new    | Invokable landing                                                          |
| `app/Services/PayoutsService.php`                           | edit   | `authorizeUrl()`, `completeAuthorization()`; deauthorize in `disconnect()` |
| `app/Integrations/Contracts/SellsSeries.php`                | edit   | Three signatures                                                           |
| `app/Integrations/Stripe/Connect.php`                       | edit   | OAuth calls; `account()` reads v1                                          |
| `app/Integrations/Concerns/StripeHttpClient.php`            | edit   | `stripeOAuth()`                                                            |
| `app/Data/ConnectAccount.php`                               | edit   | `fromStripe()` reads the v1 shape                                          |
| `config/services.php`                                       | edit   | `stripe.client_id`                                                         |
| `.env.example`                                              | edit   | `STRIPE_CLIENT_ID=`                                                        |
| `resources/js/pages/share/settings/Integrations.vue`        | edit   | Two doors                                                                  |
| `lang/en/payouts.php`                                       | edit   | Four lines                                                                 |
| `lang/en/errors.php`                                        | edit   | `payouts.oauth_state`                                                      |
| `docs/planning/decisions.md`                                | edit   | Two decisions                                                              |
| `docs/planning/release-prerequisites.md`                    | edit   | Three owner items                                                          |
| `docs/flows/checkout.md`                                    | edit   | Second door; v1 read                                                       |
| `tests/Feature/Share/PayoutsOauthTest.php`                  | new    | 8 cases                                                                    |
| `tests/Feature/Checkout/ConnectOnboardingTest.php`          | edit   | Three read cases move to the v1 shape                                      |

## Database

None.

## Code

```php
// App\Integrations\Concerns\StripeHttpClient
/** connect.stripe.com: form-encoded, secret key as the basic-auth user, no version header. */
private function stripeOAuth(): PendingRequest;
```

```php
namespace App\Integrations\Contracts;

interface SellsSeries
{
    // … T-062's four methods, then:

    /** Stripe's authorize URL: response_type=code, client_id, scope=read_write, state, redirect_uri, stripe_user[email]. */
    public function authorizeUrl(Group $group, string $redirectUrl, string $state): string;

    /** POST /oauth/token with grant_type=authorization_code; returns stripe_user_id. */
    public function exchangeCode(string $code): string;

    /** POST /oauth/deauthorize with client_id and stripe_user_id. */
    public function deauthorize(string $accountId): void;
}
```

```php
// App\Integrations\Stripe\Connect::account() — the read, for every account
$response = $this->stripe()->get("accounts/{$accountId}");   // v1, no include[]
return ConnectAccount::fromStripe($this->unwrap($response, 'account lookup'));
// INCLUDE_ON_READ is deleted.
```

```php
// App\Data\ConnectAccount::fromStripe() — the v1 shape
chargesEnabled:   (bool) ($payload['charges_enabled'] ?? false),
payoutsEnabled:   (bool) ($payload['payouts_enabled'] ?? false),
detailsSubmitted: (bool) ($payload['details_submitted'] ?? false),
country:          isset($payload['country']) ? mb_strtoupper((string) $payload['country']) : null,
defaultCurrency:  isset($payload['default_currency']) ? mb_strtoupper((string) $payload['default_currency']) : null,
// isActive() and hasNothingOutstanding() are deleted.
```

```php
// App\Services\PayoutsService
public const OAUTH_SESSION = 'payouts.oauth';

/** Stores ['state' => …, 'group_id' => …] in the session and returns the URL to redirect to. */
public function authorizeUrl(Group $group, string $redirectUrl): string;

/** Verifies state, exchanges the code, stores the id, reads the account back. */
public function completeAuthorization(Group $group, string $state, string $code): ConnectAccount;

public function disconnect(Group $group): void;   // T-064's body, preceded by deauthorize() when config('services.stripe.client_id') is filled
```

```php
// App\Http\Controllers\Share\PayoutsController
public function oauth(string $group, CurrentGroup $current): RedirectResponse;   // GET; guardOwner; redirect()->away()

// App\Http\Controllers\Settings\PayoutsReturnController
public function __invoke(Request $request): RedirectResponse;
// error=access_denied → to_route('share.settings.integrations') with payouts.declined (info)
// otherwise: Group from session; owner check (errors.payouts.owner_only);
// completeAuthorization(); to_route('share.settings.integrations') with payouts.connected (success)
// or payouts.pending (info) by canSell().
```

`IntegrationsController::show()` gains `existingLabel` and `createLabel`. In `Integrations.vue` the
not-started state shows two buttons: `existingLabel` as a link to
`/g/{slug}/payouts/stripe`, and `createLabel` as the POST form from `T-062`.

Its `status` match also gains an arm, placed before `default => 'pending'`:
`! $account->detailsSubmitted && ! $account->canSell() => 'incomplete'`.
`Integrations.vue` renders `payouts.incomplete` for it, with the same "Continue on
Stripe" button.

## Copy

| Key                                     | File                  | English                                                                  |
| --------------------------------------- | --------------------- | ------------------------------------------------------------------------ |
| `payouts.connect_existing`              | `lang/en/payouts.php` | Connect the Stripe account I have                                        |
| `payouts.create_new`                    | `lang/en/payouts.php` | Create a new Stripe account                                              |
| `payouts.connected`                     | `lang/en/payouts.php` | Your Stripe account is connected. Peers can pay you directly.            |
| `payouts.declined`                      | `lang/en/payouts.php` | Nothing was connected. You can try again whenever you like.              |
| `payouts.incomplete`                    | `lang/en/payouts.php` | Stripe doesn't have everything it needs yet. Pick up where you left off. |
| `errors.payouts.oauth_state.message`    | `lang/en/errors.php`  | That sign-in didn't start from Qori, so nothing was connected.           |
| `errors.payouts.oauth_state.resolution` | `lang/en/errors.php`  | Start again from Payments.                                               |

## Routes

| Verb | Path                       | Name                   | Action                    |
| ---- | -------------------------- | ---------------------- | ------------------------- |
| GET  | `g/{group}/payouts/stripe` | `share.payouts.oauth`  | `PayoutsController@oauth` |
| GET  | `u/payouts/stripe/return`  | `payouts.oauth.return` | `PayoutsReturnController` |

The return route is registered in `routes/settings.php` with the same
middleware as `u/profile`.

## Tests

**New: `tests/Feature/Share/PayoutsOauthTest.php` — 8 cases**

1. `test_the_owner_is_sent_to_stripe_to_sign_in` — 302 to
   `connect.stripe.com/oauth/authorize` carrying `client_id`,
   `scope=read_write`, `state` and `redirect_uri`; the session holds the same
   state and the Group id.
2. `test_a_valid_return_stores_the_account_the_creator_chose` — token endpoint
   faked to answer `stripe_user_id: acct_theirs`, v1 read faked: the Group holds
   `acct_theirs`, 302 to `share.settings.integrations`, `payouts.connected` flashed.
3. `test_a_return_with_the_wrong_state_connects_nothing` — 403,
   `Http::assertNothingSent()`, id still null.
4. `test_a_declined_sign_in_returns_to_the_page_with_a_note` —
   `error=access_denied`: 302 to the page, `payouts.declined`, id still null.
5. `test_an_admin_cannot_start_the_sign_in` — 403 on the start route.
6. `test_every_account_is_read_through_v1` — `Connect::account('acct_x')`
   sends `GET https://api.stripe.com/v1/accounts/acct_x` and `ConnectAccount`
   reads `charges_enabled` true as `canSell()`.
7. `test_disconnect_deauthorises_at_stripe_when_a_client_id_is_configured` —
   `DELETE` (`T-064`) with `client_id` set: `POST /oauth/deauthorize` sent with
   `client_id` and `stripe_user_id`, then the id is cleared.
8. `test_disconnect_skips_deauthorise_without_a_client_id` — no call, id
   cleared.

**Changed: `tests/Feature/Checkout/ConnectOnboardingTest.php`**

- `test_reading_an_account_asks_for_the_fields_it_needs` — **deleted**; case 6
  replaces it.
- `test_it_reads_selling_ability_from_the_capability_status` — becomes
  `test_it_reads_selling_ability_from_the_v1_booleans`: `charges_enabled` and
  `payouts_enabled`.
- `test_an_account_read_without_its_configuration_cannot_sell` — a payload
  with only an `id` still reads as cannot sell.

## Acceptance

- [x] From the Payments page an owner can choose "Connect the Stripe account I
      have", sign in at Stripe, and come back with their own `acct_…` stored
- [x] The same button lets a person with no Stripe account create one at Stripe
      and come back connected
- [x] A forged or stale `state` connects nothing
- [x] Disconnecting an OAuth-connected account also deauthorises it at Stripe
- [x] Every account, whichever door, is read through `GET /v1/accounts/{id}`
- [x] An account whose form was left unfinished reads `incomplete`, not
      `pending`, and says to go back rather than to wait
- [ ] Sandbox: one real OAuth round trip completed and the id checked against
      the dashboard (say if the client id was not available) — **not run on
      13 September 2026: OAuth is not enabled in the sandbox and there is no
      client id; the three owner steps are in `release-prerequisites.md`**
- [x] `decisions.md` records the v1 read and OAuth beside v2 creation
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

The v2 reader's `detailsSubmitted` is wrong for a finished account, and the
move to v1 retires it. `ConnectAccount::hasNothingOutstanding()` treats a null
`requirements.summary` as "not submitted", but with `requirements` included in
the read, null is what Stripe returns when nothing is due: the sandbox account
`acct_1UF2SKKUCxNNHqBQ` read `card_payments: active`, no entries, summary null,
and `detailsSubmitted: false` on 13 September 2026. Nothing renders that field
today, so nothing was wrong on screen; case 6 above should assert
`details_submitted` from the v1 shape so it cannot drift again.

`T-044` will want the same callback shape for storage and video providers. The
`/u/…/return` pattern and the session-nonce state are worth lifting into a
shared concern then, not now.
