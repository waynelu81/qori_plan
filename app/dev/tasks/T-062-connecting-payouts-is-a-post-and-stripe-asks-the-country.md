---
id: T-062
title: Connecting payouts is a POST, and Qori asks only the country
stream: selling
status: done
owner: claude
estimate: M
depends: T-067
blocks: T-063, T-075
---

# T-062 — Connecting payouts is a POST, and Qori asks only the country

**Rewritten 13 September 2026** after the sandbox refused the first version's
payload. The Re-scope log at the end holds what it said; this is the spec
written on that answer.

## Why

Two things are wrong with the way a creator connects payouts, and the owner
found both reading the code on 13 September 2026.

**A GET writes.** `GET /g/{group}/payouts/connect` creates a Stripe account and
stores its id on the Group, because one endpoint was made to serve both the
"Connect with Stripe" button and Stripe's `refresh_url`. Stripe's `refresh_url`
is a bare browser GET with no parameters, so _a_ GET has to mint a fresh link;
the code let the same GET also create the account. That breaks this project's
own rule that GET renders and POST acts, Stripe's page warns that link previews
and back buttons revisit URLs, and two requests before the first write lands
create two accounts.

**Qori answers questions that are Stripe's to ask.** Creation pre-fills
`identity.entity_type` and requests the `card_payments` capability, so the
creator answers "myself or a company" on Qori's page, from a two-entry select,
and Stripe's form, which knows the entity types each country allows and the
capabilities each country needs, is prevented from asking either.

The first version of this task wanted the country left to Stripe too. The
sandbox said no, twice, and the Re-scope log quotes it: a v2 account with a
full dashboard must carry a merchant configuration, and a merchant
configuration must carry a country. So the country is the one thing Qori asks
before creating an account, and a creator who would rather choose it on
Stripe's own signup, or who already has an account, takes `T-063`'s door.

Afterwards: the button is a POST that creates once and redirects; Stripe's
refresh comes back to a GET that only ever mints a link; and the account is
created with the country and nothing else Stripe can ask for itself.

## Decisions taken to make this specifiable

**Two routes, two verbs.** `POST payouts/connect` is the button. `GET
payouts/refresh` is what Qori hands Stripe as `refresh_url`; it mints a link for
an account that exists and sends anybody else back to the page. Nothing reached
by GET writes. The pending state's "Continue on Stripe" is a plain link to the
refresh route, because continuing is exactly what refresh does: a link for an
account that exists.

**The write moves into the service.** `PayoutsService`, which `T-064` started
with the read and the disconnect, gains the connect and refresh writes and
becomes the only writer of `groups.connect_account_id` and the only place that
decides "create if none". The integration's `onboardingUrl()` takes an account
id, so it structurally cannot create one.

**Create with the country and nothing else Stripe can ask for itself.** The
payload keeps `display_name`, `contact_email`, `dashboard: full`, both
responsibilities as `stripe`, `identity.country` and `metadata`. It applies the
`merchant` and `customer` configurations as empty objects, with no
`entity_type` and no requested capability. Proven in the sandbox on
13 September 2026 (Re-scope log): account created, link accepted, the read-back
carries no entity type and no capabilities until Stripe's form asks.

**The country is required on the POST.** `ConnectPayoutsRequest` stays, with
one rule: `country`, required, in `qori.payments.countries`. It was nullable
because the same endpoint served Stripe's parameterless refresh; that endpoint
is its own route now, so nothing on the POST is optional and there is no
default to fall back on. `qori.payments.default_country` stays as the select's
preselection; `entity_types` goes.

**The POST answers through `Inertia::location()`.** The button becomes an
Inertia form, which is an XHR, and an XHR cannot follow a redirect to Stripe's
origin; `T-071` met exactly this on the buy button. `redirect()->away()` is
only right for the GET refresh, which the browser reaches by navigation.

**Sandbox before tests.** Done, and it is why this file was rewritten. The
account it left behind is `acct_1UF9mBKUCxpfYJL2`, a probe, to be removed from
the sandbox dashboard.

**Connecting is owner-only.** §15 puts Connect with billing and deletion.
`T-064` added `guardOwner()` to the controller and the
`errors.payouts.owner_only` copy for `disconnect()`; `connect()` and
`refresh()` take the same guard. `show()` stays readable by admins.

## Preconditions

`T-064` done: `PayoutsService`, `guardOwner()` and the disconnect exist, and
the controller already takes the service by constructor. `T-067` done: the page
is `settings/integrations`, rendered by `IntegrationsController::show()`, and
the component is `resources/js/pages/share/settings/Integrations.vue`.

## Scope

**In:**

- The two routes and the two controller actions; `return()` keeps its
  behaviour, landing on the Integrations page.
- `connectUrl()` and `refreshUrl()` on `PayoutsService`; `connect()` moves onto
  it, and `SellsSeries` leaves the controller.
- The creation payload and the two integration signatures.
- `ConnectPayoutsRequest` reduced to the one required `country` rule;
  `qori.payments.entity_types` deleted (nothing else reads it; verified by
  grep).
- Applying `guardOwner()` to `connect()` and `refresh()`.
- The Vue form: an Inertia POST with the country select and the button, shown
  to the owner only; the entity select and its warning line go; the pending
  state's button becomes a link to refresh.
- The onboarding section of `docs/flows/checkout.md`.

**Out:**

- Disconnecting (`T-064`).
- Connecting an existing Stripe account, and choosing the country on Stripe's
  own signup (`T-063`).
- `qori.payments.currencies` and `default_currency` (`T-054`), and anything on
  the Series page.
- How the account is read back. `account()` and `INCLUDE_ON_READ` stay as they
  are until `T-063`.

## Files

| Path                                                    | Change | Notes                                      |
| ------------------------------------------------------- | ------ | ------------------------------------------ |
| `routes/share.php`                                      | edit   | `connect` becomes POST; `refresh` added    |
| `app/Http/Controllers/Share/PayoutsController.php`      | edit   | Service by constructor; `refresh()`; guard |
| `app/Http/Requests/Share/ConnectPayoutsRequest.php`     | edit   | `country` only, required                   |
| `app/Services/PayoutsService.php`                       | edit   | `connectUrl()`, `refreshUrl()`             |
| `app/Integrations/Contracts/SellsSeries.php`            | edit   | Two signatures                             |
| `app/Integrations/Stripe/Connect.php`                   | edit   | Payload; `onboardingUrl()` takes an id     |
| `app/Http/Controllers/Share/IntegrationsController.php` | edit   | Props: `needsDetails` out, two lines in    |
| `config/qori.php`                                       | edit   | `entity_types` removed                     |
| `resources/js/pages/share/settings/Integrations.vue`    | edit   | POST form, country only, owner-only        |
| `lang/en/payouts.php`                                   | edit   | Two lines                                  |
| `docs/flows/checkout.md`                                | edit   | Onboarding call chain                      |
| `tests/Feature/Checkout/ConnectOnboardingTest.php`      | edit   | Payload and signature changes              |
| `tests/Feature/Share/PayoutsDisconnectTest.php`         | edit   | The fresh-account case posts               |
| `tests/Feature/Share/PayoutsConnectTest.php`            | new    | 9 cases                                    |

## Database

None.

## Code

```php
namespace App\Integrations\Contracts;

interface SellsSeries
{
    /** Create the account a Group has none of yet. Never called twice for one Group. */
    public function createAccount(Group $group, string $country): ConnectAccount;

    /** A fresh single-use onboarding link for an account that already exists. */
    public function onboardingUrl(string $accountId, string $returnUrl, string $refreshUrl): string;

    public function account(string $accountId): ConnectAccount;

    public function checkoutFor(/* unchanged */): HostedCheckout;
}
```

```php
// App\Integrations\Stripe\Connect::createAccount() — the whole payload
[
    'display_name' => $group->name,
    'contact_email' => $group->owner?->email,
    'dashboard' => 'full',
    'defaults' => [
        'responsibilities' => ['fees_collector' => 'stripe', 'losses_collector' => 'stripe'],
    ],
    // The one answer v2 insists on before a merchant configuration exists.
    'identity' => ['country' => mb_strtoupper($country)],
    // Applied, not configured: no entity type and no requested capability, so
    // Stripe's own form asks the type and requests what the country needs.
    'configuration' => ['merchant' => new \stdClass, 'customer' => new \stdClass],
    'metadata' => ['group_id' => (string) $group->getKey(), 'group_slug' => $group->slug],
]
```

```php
namespace App\Http\Requests\Share;

class ConnectPayoutsRequest extends FormRequest
{
    /** @return array<string, mixed> */
    public function rules(): array
    {
        return ['country' => ['required', 'string', Rule::in(array_keys((array) config('qori.payments.countries')))]];
    }

    public function country(): string;   // the validated value, uppercased
}
```

```php
namespace App\Services;

class PayoutsService
{
    // account(), disconnect() and forget() from T-064, then:

    /** Create the account if the Group has none, store its id, then a fresh link. */
    public function connectUrl(Group $group, string $country, string $returnUrl, string $refreshUrl): string;

    /** A fresh link for an account that exists; null when there is none, so a GET never creates. */
    public function refreshUrl(Group $group, string $returnUrl, string $refreshUrl): ?string;
}
```

```php
namespace App\Http\Controllers\Share;

class PayoutsController extends Controller
{
    // Constructor, return(), disconnect() and guardOwner() from T-064.
    public function connect(ConnectPayoutsRequest $request, string $group, CurrentGroup $current): Response;  // POST; guardOwner; Inertia::location()
    public function refresh(string $group, CurrentGroup $current): RedirectResponse;                           // GET; guardOwner; redirect()->away(), or to_route('share.settings.integrations') when there is no account
}
```

`Response` is `Symfony\Component\HttpFoundation\Response`, as `CheckoutController::store()` returns it.

`IntegrationsController::show()` loses `needsDetails` and gains `connectHelp`
and `ownerNote`; `countries`, `defaultCountry`, `status`, `pricedSeriesCount`
and `disconnect` stay.

In `Integrations.vue` the not-started state's form is
`<Form method="post" :action="`/g/${group.slug}/payouts/connect`">` with the
country select and the button, shown `v-if="isOwner"` (the page already
computes it); non-owners see `ownerNote` in its place. The entity select, the
"can't change either of these later" line and the `needsDetails` prop are
removed. `connectHelp` renders as a muted line under the button. The pending
state's "Continue on Stripe" is an anchor to `/g/${group.slug}/payouts/refresh`,
owner-only too.

## Copy

| Key                       | File                  | English                                                                                                            |
| ------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `payouts.connect_help`    | `lang/en/payouts.php` | Stripe asks the rest on its own form: whether you share as yourself or as a company, and what it needs to pay you. |
| `payouts.owner_only_note` | `lang/en/payouts.php` | Connecting payments is the owner's to do.                                                                          |

## Routes

| Verb | Path                        | Name                    | Action                      |
| ---- | --------------------------- | ----------------------- | --------------------------- |
| POST | `g/{group}/payouts/connect` | `share.payouts.connect` | `PayoutsController@connect` |
| GET  | `g/{group}/payouts/refresh` | `share.payouts.refresh` | `PayoutsController@refresh` |
| GET  | `g/{group}/payouts/connect` | —                       | Removed; answers 405        |

`refresh_url` handed to Stripe is `route('share.payouts.refresh', $slug)`;
`return_url` stays `route('share.payouts.return', $slug)`.

## Tests

**New: `tests/Feature/Share/PayoutsConnectTest.php` — 9 cases**

1. `test_the_button_creates_the_account_and_sends_the_owner_to_stripe` — POST
   `country=NZ` as owner with no account, both endpoints faked: 302 to the
   link URL, `connect_account_id` stored, and the creation payload carried
   `identity.country` `NZ`, no `identity.entity_type` and no `capabilities`
   under `configuration.merchant`.
2. `test_the_inertia_form_is_told_where_to_go` — the same POST with the
   `X-Inertia` header answers 409 with `X-Inertia-Location` set to the link.
3. `test_the_button_resumes_an_existing_account_without_creating_another` —
   POST with an id already stored: 302 to the link, nothing sent to
   `/v2/core/accounts`.
4. `test_the_country_is_required` — POST with no country: validation error on
   `country`, `Http::assertNothingSent()`, id still null.
5. `test_refresh_mints_a_new_link_for_an_existing_account` — GET refresh with
   an id: 302 to the link, nothing sent to `/v2/core/accounts`.
6. `test_refresh_with_no_account_goes_back_to_the_page_and_creates_nothing` —
   GET refresh, no id: 302 to `share.settings.integrations`, `Http::assertNothingSent()`.
7. `test_a_get_on_connect_is_not_a_route` — GET `payouts/connect` answers 405.
8. `test_an_admin_cannot_connect_or_refresh` — POST connect as an admin is
   refused (a redirect back, which is how `AppException` answers a write) with
   nothing sent and the id still null; GET refresh as an admin answers 403.
9. `test_the_page_no_longer_asks_for_an_entity_type` — `show` has no
   `needsDetails` prop and has `countries`, `connectHelp` and `ownerNote`.

**Changed: `tests/Feature/Checkout/ConnectOnboardingTest.php`**

- `test_it_creates_the_account_on_the_v2_endpoint` — `createAccount($group, 'AU')`;
  the `identity` and capability assertions become: `identity.country` present,
  no `identity.entity_type`, and `configuration.merchant` present with no
  `capabilities`.
- `test_it_sends_an_api_version_that_serves_v2` and
  `test_the_owner_email_travels_as_contact_email` — new signature only.
- `test_the_account_link_nests_its_urls_under_use_case` —
  `onboardingUrl('acct_v2_1', …)`; the accounts fake is no longer needed.
- `test_resuming_an_existing_account_does_not_create_another` — **deleted**;
  the signature makes it impossible and case 3 above covers the service.

**Changed: `tests/Feature/Share/PayoutsDisconnectTest.php`**

- `test_after_disconnecting_the_button_creates_a_fresh_account` — POSTs with
  a country.

## Acceptance

- [x] Sandbox: an account created with this payload is accepted, and the link
      is accepted (13 September 2026, `acct_1UF9mBKUCxpfYJL2`; the Re-scope
      log says what the form showed)
- [x] `GET /g/{group}/payouts/connect` answers 405; `POST` creates once and
      answers with Stripe's URL
- [x] `GET /g/{group}/payouts/refresh` never creates an account
- [x] A non-owner cannot connect or refresh
- [x] Nothing reads `qori.payments.entity_types`; creation sends no entity
      type and requests no capability
- [x] `docs/flows/checkout.md` shows the new call chain
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

**13 September 2026, claude.** Stopped at the Decision "Sandbox before
tests", before any test was written. The sandbox refused the payload in
**Code** and every shape near it:

- `POST /v2/core/accounts` with `configuration.merchant` and `customer` as
  empty objects and no `identity`: `400 The field identity.country is required
before setting configuration.merchant.`
- The same with no `configuration` at all, and again with `customer` only:
  `400 You cannot set dashboard unless the account is configured as a merchant
or a recipient with the stripe_balance.stripe_transfers capability.`

So on v2 a full-dashboard account needs a merchant configuration, and a
merchant configuration needs a country. "Stripe asks the country" cannot be
built through this door. The hosted-onboarding sentence the Why quotes
describes an account that reaches onboarding with no merchant configuration,
which v2 will not create with a dashboard.

What the sandbox did accept: `identity.country` alone, `merchant` and
`customer` applied as empty objects, no `entity_type` and no requested
capability. Account `acct_1UF9mBKUCxpfYJL2` was created that way, an
`account_onboarding` link for `['merchant', 'customer']` was accepted, the
read-back showed `identity.entity_type` null and `configuration.merchant.capabilities`
null, and the link opened on Stripe's first screen, which asks for an email
and offers "Have a Stripe account? You can use the same email address."
Nothing was entered on it. The account is a probe and can be removed from the
sandbox dashboard.

The POST, the refresh GET, the write moving into the service and the owner
guard are untouched by this. The country has to stay Qori's one question;
the entity type and the capability request are what Stripe's form can be left
to ask. A creator who wants to choose the country on Stripe's own signup has
`T-063`'s door.

## Notes

The thirteen-country list had Japan in it while `qori.payments.currencies`
deliberately has no JPY (`T-054`), so a Japanese creator could connect payouts
and price nothing. The list stays, so the contradiction stays; whether Qori
sells in yen is still `T-054`'s open decision.
