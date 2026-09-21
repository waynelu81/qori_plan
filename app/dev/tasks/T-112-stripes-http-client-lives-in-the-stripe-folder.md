---
id: T-112
title: Stripe's HTTP client lives in the Stripe folder
stream: selling
status: done
owner: claude
estimate: S
depends: none
blocks: T-113
---

# T-112 — Stripe's HTTP client lives in the Stripe folder

## Why

Stripe's three HTTP clients and its error decoding are a trait,
`App\Integrations\Concerns\StripeHttpClient` (`app/Integrations/Concerns/StripeHttpClient.php:18-105`),
in a folder meant for behaviour shared across vendors. Only
`App\Integrations\Stripe\Connect` and `Subscription` use it, and `D-022` puts
everything written for one vendor in that vendor's folder, with no `Concerns`.

Afterwards the client is a class, `App\Integrations\Stripe\Client`, injected
into `Connect` and `Subscription`, with the owner's method names, and
`app/Integrations/Concerns` is gone. Nothing a creator or a Peer sees changes.

## Decisions taken to make this specifiable

**A class, not a trait.** `CLAUDE.md` wants trait names to be verb phrases, and
the owner's name is `Client`. A class injected by constructor is the shape the
rest of `app/Integrations` already has for dependencies.

**The owner's names: `stripe()` becomes `getClientV1()`, `stripeV2()` becomes
`getClientV2()`, and `stripeOAuth()` becomes `getClientOAuth()` to match.**
`unwrap()` keeps its name. All four are public, because `Connect` and
`Subscription` call them from outside the class now.

**Behaviour is moved, not changed.** Base URLs, headers, timeouts, the retry
counts and the error decoding are identical. `T-113` deletes `getClientV2()`
with its last callers.

**`ArchitectureTest` swaps the trait name for the folder.** Its Services rule
looked for the string `StripeHttpClient`, which would match nothing after the
move and pass while guarding nothing. `use App\Integrations\Stripe\` says the
real rule: a Service calls a contract, never a Stripe class. No Service
imports one today. A second case asserts `app/Integrations/Concerns` does not
exist, because `CLAUDE.md` says the rules a test can check are checked.

## Preconditions

**Data this task verifies against:** a clean database.

**Equipment:** None. Every Stripe call is faked.

## Scope

**In:**

- `App\Integrations\Stripe\Client`, and `Connect` and `Subscription` calling it.
- Deleting the trait and its folder.
- The two `ArchitectureTest` changes.

**Out:**

- Removing account creation and reshaping onboarding: `T-113`.
- Moving the `fromStripe()` factories out of `app/Data`, the webhook signature
  check out of the controller, and the purge command's own clients. Findings
  under `D-022`, listed in the report.

## Files

| Path                                               | Change | Notes                                                   |
| -------------------------------------------------- | ------ | ------------------------------------------------------- |
| `app/Integrations/Stripe/Client.php`               | new    | the trait's body as a class, methods renamed and public |
| `app/Integrations/Concerns/StripeHttpClient.php`   | delete | folder removed with it                                  |
| `app/Integrations/Stripe/Connect.php`              | edit   | constructor-injects `Client`; calls renamed             |
| `app/Integrations/Stripe/Subscription.php`         | edit   | constructor-injects `Client`; calls renamed             |
| `tests/Feature/Integrations/Stripe/ClientTest.php` | new    | 4 cases                                                 |
| `tests/Feature/ArchitectureTest.php`               | edit   | the Services needle; 1 new case                         |

Flows: none — no call chain changes; the same Stripe calls move from a trait
into an injected class inside `app/Integrations/Stripe`.

## Database

None.

## Code

```php
namespace App\Integrations\Stripe;

use Illuminate\Http\Client\PendingRequest;
use Illuminate\Http\Client\Response;

class Client
{
    /** v1: form-encoded, Stripe-Version, Stripe-Account when $connectedAccount is given. */
    public function getClientV1(?string $connectedAccount = null): PendingRequest;

    /** v2: JSON, /v2. Removed by T-113 with its last callers. */
    public function getClientV2(): PendingRequest;

    /** connect.stripe.com/oauth: basic auth with the secret, no version header, no retry. */
    public function getClientOAuth(): PendingRequest;

    /** @return array<string, mixed> */
    public function unwrap(Response $response, string $context): array;
}

class Connect implements SellsSeries
{
    public function __construct(private Client $client) {}
}

class Subscription implements BillsGroups
{
    public function __construct(private Client $client) {}
}
```

Each `$this->stripe(…)` becomes `$this->client->getClientV1(…)`,
`$this->stripeV2()` becomes `$this->client->getClientV2()`,
`$this->stripeOAuth()` becomes `$this->client->getClientOAuth()`, and
`$this->unwrap(…)` becomes `$this->client->unwrap(…)`. The trait's docblocks
move with the methods.

`ArchitectureTest::test_services_make_no_vendor_http_calls()` replaces the
needle `'StripeHttpClient'` with `'use App\\Integrations\\Stripe\\'`.

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Integrations/Stripe/ClientTest.php` — 4 cases**

1. `test_v1_sends_the_platform_key_and_version_without_an_account_header` — a
   faked `api.stripe.com/v1` call carries the bearer secret and
   `Stripe-Version`, is form-encoded, and has no `Stripe-Account`.
2. `test_v1_for_a_connected_account_sends_the_account_header` — the header
   carries the id given.
3. `test_oauth_uses_basic_auth_and_no_version_header` — a faked
   `connect.stripe.com/oauth` call.
4. `test_unwrap_reads_each_error_shape` — v1 `error.message`, OAuth
   `error_description` and v2 top-level `message` each throw
   `AppException` with code `upstream_unavailable` and the status as `upstream`.

**New in `tests/Feature/ArchitectureTest.php` — 1 case**

5. `test_integrations_keep_no_shared_concerns_folder` — `app/Integrations/Concerns`
   does not exist.

**Changed:** none expected. `ConnectOnboardingTest`, `PayoutsOauthTest`,
`StatementDescriptorTest`, `SubscriptionTest` and `StripeWebhookTest` resolve
`Connect` and `Subscription` from the container and must pass unchanged.

Total new: 5.

## Acceptance

- [x] `app/Integrations/Concerns` does not exist, and nothing references `StripeHttpClient`
- [x] `Connect` and `Subscription` reach Stripe only through `Client`
- [x] Every existing Stripe test passes unchanged
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Built and verified on its own branch before `T-113`; the full gate ran once
over `T-111` to `T-113` together (see the report).

Written from the owner's instruction of 17 September 2026 to move
`StripeHttpClient` to `App\Integrations\Stripe\Client` and rename `stripe` and
`stripeV2`, given as approval to build.
