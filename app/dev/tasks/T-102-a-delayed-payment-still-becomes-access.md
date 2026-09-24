---
id: T-102
title: A delayed payment still becomes access, and Confirming survives the browser
stream: selling
status: draft
owner: unassigned
estimate: M
depends: T-027
blocks: T-094
---

# T-102 — A delayed payment still becomes access, and Confirming survives the browser

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016` and the owner's BYO blueprint; reviewed the same day against the
> developer's review of the plan that day, whose asks for this task —
> close the delayed-payment and refund races before paid access is released
> on any provider, keep fulfilment replayable when saving its own state
> fails, and bound any vendor call made inside a page load — are folded in
> below.

## Why

Two gaps on the paid path break the owner's first priority — a Peer gets
working access right after buying — whatever the Series holds. First, the
webhook acts on `checkout.session.completed` only when `payment_status` is
`paid` (`app/Http/Controllers/StripeWebhookController.php:73-75`) and answers
every other event type with `ignored` (`:57-61`); nothing handles
`checkout.session.async_payment_succeeded` or `async_payment_failed`, and
`Connect::checkoutFor()` sends no `payment_method_types`
(`app/Integrations/Stripe/Connect.php:197-218`), so the creator's own Stripe
dashboard decides what a buyer may pay with. A buyer who pays by a bank debit
is charged days later and never granted. Second, the Confirming page lives in
the browser session: `CheckoutPending` keeps a marker for
`CONFIRMING_MINUTES = 30` (`app/Support/CheckoutPending.php:20`), and
`SharedController::show()` renders `shared/Confirming` only while that marker
is present (`app/Http/Controllers/Shared/SharedController.php:97-118`).
Returning from Stripe in another browser, or after a webhook more than thirty
minutes late, meets `AppException::forbidden('errors.access.not_granted')`
(`:114-117`), and `success_url` is the bare Series page
(`app/Http/Controllers/CheckoutController.php:41`,
`app/Http/Controllers/SeriesAccessController.php:155`) with no
`{CHECKOUT_SESSION_ID}`, so the page cannot ask Stripe what happened.

Afterwards the `payment_fulfilments` row is written the moment a checkout
begins and is the one record of the payment from then on: the webhook moves
it through `pending`, `granted`, `failed` or `abandoned` on four
`checkout.session.*` events; the Series page keys Confirming on that row, in
any browser, for as long as the money is in flight, and says in one sentence
when it has failed; the success URL carries the session id, and landing with
it fulfils from a retrieve when Stripe already says `paid`, so a late webhook
never keeps a buyer out. Nothing after `AccessService::grant()` can undo an
Access, and a failure after it propagates so Stripe redelivers.

This is where the `storage` stream's paid path lands. `D-016` puts the vendor
grant inside `grant()` (`T-091`), and the stream file says `T-102` and `T-103`
come before any paid Series uses a provider: a delayed payment that never
becomes access, or a Confirming page that expires, is the same broken promise
whether the Series holds a Qori file or a creator's folder. Which providers
enter before beta is the owner's open decision in `decisions.md`; nothing here
waits on it, because every case below exists today with Qori's own storage.

## Decisions taken to make this specifiable

**The pending row is written when the checkout begins, and it is the one
record of the payment from then on.** `CheckoutService::begin()` records a
`pending` row after `SellsSeries::checkoutFor()` answers; every later step —
`fulfil()`, `awaitPayment()`, `fail()`, `abandon()`, `cancel()`, `confirm()` —
updates that row by `session_id`, the unique key the table already has
(`database/migrations/2026_09_09_000000_create_payment_fulfilments_table.php:29`).
`App\Support\CheckoutPending` and its session marker are deleted; no cookie is
consulted. A row survives a browser change and has no thirty-minute cliff.

**`success_url` carries `{CHECKOUT_SESSION_ID}` as a literal, appended by
string concatenation, never as a route parameter.** `route()` percent-encodes
the braces and Stripe substitutes only the literal string
(<https://docs.stripe.com/payments/checkout/custom-success-page?payment-ui=stripe-hosted>:
"This is a literal string and you must add it exactly as you see it here").
`begin()` appends `?session_id={CHECKOUT_SESSION_ID}` to the URL its callers
already pass, so `CheckoutController::store()` and
`SeriesAccessController::verify()` change only by losing their
`CheckoutPending::mark()` line. `Http::asForm()` encodes the body, which is
what Stripe's own example does with `--data-urlencode`.

**The landing page fulfils too, from a retrieve made as the connected
account.** Stripe: webhooks are required, and fulfilling from the landing page
is recommended because "webhooks can sometimes be delayed"
(<https://docs.stripe.com/checkout/fulfillment?payment-ui=stripe-hosted>).
`confirm()` reads the session with the `Stripe-Account` header — the session
belongs to the creator's account, and "you must make API requests for that
object as the connected account" (<https://docs.stripe.com/connect/webhooks>)
— with `CONFIRM_TIMEOUT_SECONDS` (provisional 5) and no retry, and maps
`payment_status` `paid` to `fulfil()`, `status` `complete` to
`awaitPayment()`, `status` `expired` to `abandon()`, and anything else,
including a timeout, to nothing but a `checked_at`. Confirming reloads every
three seconds (`resources/js/pages/shared/Confirming.vue:24`), so
`CONFIRM_RECHECK_SECONDS` (provisional 15) throttles the retrieve per row.

**The webhook dispatches four `checkout.session.*` events, and only
`checkout.session.completed` is gated on `payment_status`.** Stripe's own
handler calls its fulfilment function for `completed` and
`async_payment_succeeded` alike and checks `payment_status` inside it; the
events themselves are "Occurs when a Checkout Session has been successfully
completed", "Occurs when a payment intent using a delayed payment method
finally succeeds", "… fails", and "Occurs when a Checkout Session is expired"
(<https://docs.stripe.com/api/events/types#event_types-checkout.session.async_payment_succeeded>).
So: `completed` with `paid` fulfils, as today; `completed` with anything else
records the session's `payment_intent` and `completed_at` on the pending row
and grants nothing — that is what lets a refund (`T-103`) find a payment that
has not settled yet; `async_payment_succeeded` fulfils on the event's meaning
alone; `async_payment_failed` records `failed` with `payment_failed`;
`expired` abandons a pending row. Every other type stays `ignored`.
`no_payment_required` is treated as not paid: `guardSellable()` refuses a
free Series (`app/Services/CheckoutService.php:232-237`), so a session with
nothing to pay is not one Qori made — stricter than Stripe's `!= 'unpaid'`.

**`payment_method_types` stays unset** (provisional — the owner's question).
Omitted, Checkout offers the methods managed in the account's Dashboard, and
for a direct charge that account is the creator's — the merchant of record
(§7.2) choosing their own methods. Restricting Qori's sessions to `card` would
be a product decision the owner has not taken; this task makes the delayed
path safe instead, and a test pins the absence so it cannot creep in.

**Four fulfilment states, and `failure_code` says which failure.** `pending`
(a session exists and Stripe has not said the money is in), `granted`,
`failed` (`payment_failed` from Stripe, `unplaceable` metadata, or a rule that
`refused`) and `abandoned` (cancel or expiry, unpaid). `abandoned` is never
sticky: a later Stripe event for the same session overwrites it, because a
buyer who pressed back can still pay from the browser's history while the
session is open. Nothing ever downgrades `granted`.

**Confirming is chosen from the newest row for this person and Series, and
the row's shape decides.** `pending` with `completed_at` set: Confirming
however old, with the delayed-payment line — the money is in flight and may
take days. `pending` and still open: Confirming for `CONFIRMING_MINUTES`
(30, kept from `T-074`) from `created_at`, then refused as today, because
Stripe keeps a session open for 24 hours by default (`expires_at`,
<https://docs.stripe.com/api/checkout/sessions/create>) and a Series someone
never paid for must not confirm for a day; landing with the session id
settles the open case exactly through the retrieve. `failed`: the sentence
for its code and a way back to the public page. `abandoned`, or no row:
refused as today.

**Cancel marks the row abandoned, on the same GET that forgot the marker.**
`PublicSeriesController::show()` with `cancelled=1` already writes to the
session (`app/Http/Controllers/PublicSeriesController.php:66-70`); it now
abandons the signed-in person's newest open row for the Series instead.

**Fulfilment stays replayable: nothing after `grant()` can undo the Access,
and a failure after it propagates so Stripe redelivers.** The order inside
`fulfil()` is the refund check, `grant()`, `record()`. `grant()` is idempotent
(`app/Services/AccessService.php:74-88`); `T-091`'s ensure step runs inside it
and never throws; a `record()` that throws is not an `AppException`
(`CheckoutService.php:124`), so it propagates, the webhook answers non-2xx,
and the redelivery takes the existing-access branch and records `granted`. A
`fulfil()` for a row already `granted` still calls `grant()` — the replay is
what re-runs the ensure step (`T-091`, case 5).

**A vendor grant is never a condition of the money becoming access, and this
task reads none of it.** `T-091`'s ensure step runs inside `grant()`, never
throws, and records its own outcome on its own row, whose `VendorGrantStatus`
is `awaiting_identity` (the Peer resolves it, by signing in with the vendor —
`T-092`), `awaiting_acceptance` (the Peer resolves it, by taking up a Dropbox
Join or a OneDrive invite), `pending` (Qori retries; nobody needs to act),
`needs_creator` (the creator reconnects, or a policy, plan or cap has to
change), `granted`, or `revoked`. None of them changes what `fulfil()` writes,
what Confirming shows, or whether an Access exists — a buyer who has paid has
access, and a vendor state still waiting on somebody is the Series page's
message (`T-091`), not the checkout's. The two `pending`s are different words:
`FulfilmentStatus::Pending` means Stripe has not said the money is in;
`VendorGrantStatus::Pending` means Qori will try the vendor again.

**A vendor read inside a page load is bounded, here as in `T-091`.**
`CONFIRM_TIMEOUT_SECONDS` is this task's version of
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` (`T-091`), and behaves the same
way: a timeout leaves the row as it was for the next attempt and the page
renders its waiting state, rather than the buyer paying for a slow vendor with
a spinner or a 500. `checked_at` throttles the retrieve, as `T-091`'s
`checked_at` throttles its re-check of a `granted` row.

**A refund that arrived first wins** (provisional — `T-103`'s column).
Stripe's fulfilment function "might be called multiple times, possibly
concurrently", and events are not delivered in order, so `charge.refunded`
can land before `async_payment_succeeded`. `fulfil()` reads `refunded_at` on
the row — the name is `T-103`'s to confirm — and, when set, grants nothing,
writes nothing and returns null. The reverse order, a refund after the grant,
is `T-103`'s revoke.

**The buyer-facing failure copy lives in `errors.php` and renders on the
page, never as a throw.** Failures belong there (CLAUDE.md); Confirming
renders the `message` as its heading and the `resolution` beneath, the way a
failed action's toast does (`docs/architecture/errors.md`, "How it surfaces"),
both through `Terminology::line()` so `:series` is the Group's word.

**No sweep command here.** Stripe retries a failed delivery for days
(`StripeWebhookController.php:79-82` already relies on it), the landing page
covers the browser, and `checkout.session.expired` closes an unpaid session.
A `qori:checkout:reconcile` over `pending` rows older than a day is
`operations`' if one is ever found — decided: not here.

**No email to the buyer when a delayed payment fails** (provisional — the
owner's question). Stripe suggests one; Confirming already says it, and the
bank and Stripe both write to the buyer. The access email on success is
`AccessService::announce()`'s (`:115-118`), unchanged.

## Preconditions

A clean checkout; tests run on the local Postgres (`_testing`).

**Data this task verifies against:** a clean database. The sandbox walk needs
the Group whose Connect account `T-062` created, with a bank-debit method
enabled in that account's Dashboard payment method settings.

**Equipment:** the Stripe CLI signed in to the sandbox, forwarding Connect
events to a local server: `stripe listen --forward-connect-to
localhost:8000/webhooks/stripe`, then `stripe trigger --stripe-account
acct_… checkout.session.async_payment_succeeded` and the same for
`checkout.session.completed` and `checkout.session.async_payment_failed`, all
three of which `stripe trigger` supports (<https://docs.stripe.com/cli/trigger>).
`checkout.session.expired` is not triggerable: capture it from the sandbox's
event log after a session created with `expires_at` thirty minutes out, the
minimum. A second browser, signed out, for the other-browser check.

**Spike:** none owed by a separate task; the fixtures are this task's first
step. No `tests/Fixtures/stripe/` exists today, and every webhook payload the
suite sends is hand-written (`tests/Feature/Checkout/StripeWebhookTest.php:68-81`),
not observed. Before the tests below are written, capture and commit, redacted
and dated: `checkout-session-completed-unpaid.json`,
`checkout-session-async-payment-succeeded.json`,
`checkout-session-async-payment-failed.json`, `checkout-session-expired.json`,
`checkout-session-retrieve-paid.json` and `checkout-session-retrieve-open.json`
(the last two from `GET /v1/checkout/sessions/{id}` with `Stripe-Account`,
<https://docs.stripe.com/api/checkout/sessions/retrieve>). The field names in
the Code section — `id`, `status`, `payment_status`, `payment_intent`,
`amount_total`, `currency`, `metadata`, `mode` — come from the object
reference (<https://docs.stripe.com/api/checkout/sessions/object>), and the
fixtures confirm them; an expected response is not a fixture.

## Scope

**In:**

- `payment_fulfilments`: the `pending` and `abandoned` states,
  `failure_code`, `completed_at`, `checked_at`, and the row written at
  `begin()`.
- The webhook's four `checkout.session.*` events through `CheckoutService`.
- `success_url` with the session id; `SellsSeries::checkoutStatus()` and its
  `Connect` implementation; `confirm()` on the landing page.
- Confirming keyed on the row: the delayed line, the failed sentence and its
  way back, no polling once failed; cancel abandons the row.
- Deleting `CheckoutPending`.
- `docs/flows/checkout.md` and `billing.md`, a tinker recipe, the fixtures.

**Out:**

- Refunds and revocation, including the refund column itself — `T-103`; this
  task only reads it.
- The vendor grant on the paid path — `T-091`, whose ensure step runs inside
  `grant()`; nothing here reads a grant, and no grant state reaches Confirming.
- Asking a buyer for the vendor account a Series needs, before or after they
  pay — `T-092`'s step, wherever it decides to stand.
- A vendor's own per-container sharing cap checked before a sale, the way the
  Peer cap is checked in `begin()` — the provider tasks', once a spike has
  confirmed a hard number.
- Restricting or choosing payment methods — the owner's, above.
- An email to the buyer on a failed delayed payment — the owner's, above.
- A scheduled sweep over `pending` rows — decided above.
- The public page still offering to buy from a disconnected Group (`T-085`),
  and the staff view of failed fulfilments the enum comment points at
  (`app/Enums/FulfilmentStatus.php:8-10`).
- Anything in sign-in's stored destination: a buyer who lands signed out is
  bounced to sign-in and returned to the URL, session id and all, by the
  password path `D-017` left unchanged; `app/Support/SignInDestination.php` is
  not touched.

## Files

| Path                                                                                                                                                                                                    | Change | Notes                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------ |
| `database/migrations/2026_09_17_000000_add_pending_state_to_payment_fulfilments.php`                                                                                                                    | new    | Three columns, one index                                                                               |
| `app/Enums/FulfilmentStatus.php`                                                                                                                                                                        | edit   | `Pending`, `Abandoned`, `isSettled()`                                                                  |
| `app/Models/PaymentFulfilment.php`                                                                                                                                                                      | edit   | Columns, casts, `HasFactory`, `latestFor()`; still not group-scoped (`:11-18`)                         |
| `database/factories/PaymentFulfilmentFactory.php`                                                                                                                                                       | new    | Default `pending`; states `granted()`, `failed(string $code)`, `abandoned()`, `completed()`            |
| `app/Data/CheckoutStatus.php`                                                                                                                                                                           | new    | The retrieve's shape                                                                                   |
| `app/Integrations/Contracts/SellsSeries.php`                                                                                                                                                            | edit   | `checkoutStatus()`                                                                                     |
| `app/Integrations/Stripe/Connect.php`                                                                                                                                                                   | edit   | `checkoutStatus()`; `checkoutFor()` unchanged                                                          |
| `app/Services/CheckoutService.php`                                                                                                                                                                      | edit   | Constants; the row at `begin()`; six methods; the refund guard in `fulfil()`                           |
| `app/Support/CheckoutPending.php`                                                                                                                                                                       | delete | The session marker                                                                                     |
| `app/Http/Controllers/StripeWebhookController.php`                                                                                                                                                      | edit   | Four `checkout.session.*` events                                                                       |
| `app/Http/Controllers/CheckoutController.php`                                                                                                                                                           | edit   | Drop `CheckoutPending::mark()` (`:51`)                                                                 |
| `app/Http/Controllers/SeriesAccessController.php`                                                                                                                                                       | edit   | Drop `CheckoutPending::mark()` (`:159`) and the import (`:13`)                                         |
| `app/Http/Controllers/PublicSeriesController.php`                                                                                                                                                       | edit   | `cancelled=1` calls `cancel()` (`:66-70`)                                                              |
| `app/Http/Controllers/Shared/SharedController.php`                                                                                                                                                      | edit   | `CheckoutService` by constructor; `confirm()` on landing; Confirming from the row                      |
| `resources/js/pages/shared/Confirming.vue`                                                                                                                                                              | edit   | `state`, `completedAt`, `tryAgainUrl`; failed renders, does not poll                                   |
| `lang/en/accesses.php` `lang/en/errors.php`                                                                                                                                                             | edit   | Copy below                                                                                             |
| `tests/Fixtures/stripe/checkout-session-completed-unpaid.json` `tests/Fixtures/stripe/checkout-session-async-payment-succeeded.json` `tests/Fixtures/stripe/checkout-session-async-payment-failed.json` | new    | Captured by `stripe listen`, redacted, dated                                                           |
| `tests/Fixtures/stripe/checkout-session-expired.json` `tests/Fixtures/stripe/checkout-session-retrieve-paid.json` `tests/Fixtures/stripe/checkout-session-retrieve-open.json`                           | new    | The event log and the retrieve                                                                         |
| `tests/Feature/Checkout/StripeWebhookTest.php` `tests/Feature/Checkout/ConfirmingTest.php` `tests/Feature/Checkout/PaidFulfilmentTest.php` `tests/Feature/Checkout/CheckoutTest.php`                    | edit   | Cases below; payloads from the fixtures; `ConfirmingTest::markerKey()` (`:62-65`) goes with the marker |
| `tests/Feature/Access/SeriesAccessContinueTest.php`                                                                                                                                                     | edit   | `:145` asserts a `pending` row, not the marker; drop the import (`:10`)                                |
| `docs/flows/checkout.md`                                                                                                                                                                                | edit   | "The path back" (`:61-103`): the four events, the row, the landing retrieve                            |
| `docs/flows/billing.md`                                                                                                                                                                                 | edit   | The dispatch lines (`:85-86`)                                                                          |
| `docs/tinker/accesses.md`                                                                                                                                                                               | edit   | A "Pay for one" recipe: `stripe listen --forward-connect-to`, `stripe trigger --stripe-account`        |

## Database

Only what changes; the table is in
`database/migrations/2026_09_09_000000_create_payment_fulfilments_table.php`.

| Table                 | Column         | Type       | Null | Default | Index / constraint                                                             |
| --------------------- | -------------- | ---------- | ---- | ------- | ------------------------------------------------------------------------------ |
| `payment_fulfilments` | `failure_code` | string(50) | yes  | null    | `payment_failed`, `unplaceable` or `refused`; set only when `status` is failed |
| `payment_fulfilments` | `completed_at` | timestamp  | yes  | null    | When Stripe reported the session complete, paid or not                         |
| `payment_fulfilments` | `checked_at`   | timestamp  | yes  | null    | The last retrieve; throttles `confirm()`                                       |
| `payment_fulfilments` | —              | —          | —    | —       | index `(user_id, series_id, created_at)` — the Confirming lookup               |

`status` keeps no default; `begin()` sets `pending`. `T-103`'s refund column
is its own migration.

Migration: `database/migrations/2026_09_17_000000_add_pending_state_to_payment_fulfilments.php`

## Code

```php
namespace App\Enums;

enum FulfilmentStatus: string
{
    case Pending = 'pending';       // a session exists; Stripe has not said the money is in
    case Granted = 'granted';
    case Failed = 'failed';         // failure_code says which failure
    case Abandoned = 'abandoned';   // cancelled or expired unpaid; a later event overwrites it

    /** Granted or Failed: nothing more is expected from Stripe. */
    public function isSettled(): bool;
}
```

```php
namespace App\Models;

class PaymentFulfilment extends Model   // HasUlids, HasFactory; deliberately not group-scoped
{
    public const FAILURE_PAYMENT_FAILED = 'payment_failed';
    public const FAILURE_UNPLACEABLE = 'unplaceable';
    public const FAILURE_REFUSED = 'refused';
    // fillable gains failure_code, completed_at, checked_at; casts gain both timestamps as 'datetime'
    public function isPending(): bool;
    public function wasCompleted(): bool;      // completed_at !== null
    public function isPaymentFailure(): bool;  // Failed and failure_code === FAILURE_PAYMENT_FAILED
    /** The newest row for this person and Series, whatever its status; null when none. */
    public static function latestFor(User $user, string $seriesId): ?self;
    public function group(): BelongsTo;
}
```

```php
namespace App\Data;

/** A checkout read back from the vendor. Field names from the Stripe object reference; the fixtures confirm them. */
class CheckoutStatus
{
    public const STATUS_OPEN = 'open';
    public const STATUS_COMPLETE = 'complete';
    public const STATUS_EXPIRED = 'expired';
    public const PAYMENT_PAID = 'paid';

    /** @param array<string, mixed> $metadata */
    public function __construct(
        public string $id,
        public string $status,             // open | complete | expired
        public string $paymentStatus,      // paid | unpaid | no_payment_required
        public ?string $paymentReference,  // payment_intent
        public ?int $amountCents,          // amount_total
        public ?string $currency,
        public array $metadata = [],
    ) {}

    /** @param array<string, mixed> $payload */
    public static function fromStripe(array $payload): self;
    public function isPaid(): bool;       // paymentStatus === PAYMENT_PAID
    public function isComplete(): bool;   // status === STATUS_COMPLETE
    public function isExpired(): bool;
}
```

```php
// App\Integrations\Contracts\SellsSeries — one addition
/**
 * Read a checkout back, as the creator's account. $timeoutSeconds bounds the wait a page
 * can be made to pay; a timeout is thrown as AppException::upstreamTimeout, nothing else.
 */
public function checkoutStatus(Group $group, string $sessionId, int $timeoutSeconds): CheckoutStatus;

// App\Integrations\Stripe\Connect
public function checkoutStatus(Group $group, string $sessionId, int $timeoutSeconds): CheckoutStatus
{
    // $this->stripe($group->connect_account_id)->timeout($timeoutSeconds)->retry(1, 0, throw: false)
    //     ->get("checkout/sessions/{$sessionId}") — retry(1) is one attempt; a ConnectionException
    //     becomes AppException::upstreamTimeout(devMessage: …, upstream: 'timeout', previous: $e).
    // Blank connect_account_id throws errors.checkout.not_connected as checkoutFor() does (:190-195).
    return CheckoutStatus::fromStripe($this->unwrap($response, 'checkout lookup'));
}
```

```php
namespace App\Services;

class CheckoutService
{
    /** The query parameter the success URL carries; Stripe fills the literal placeholder. */
    public const SESSION_ID_PARAMETER = 'session_id';
    /** An open session confirms for this long from its start; after it the page refuses as before. */
    public const CONFIRMING_MINUTES = 30;
    /** Seconds one retrieve may take inside a page load. Provisional. */
    public const CONFIRM_TIMEOUT_SECONDS = 5;
    /** A row is not retrieved again within this many seconds. Provisional. */
    public const CONFIRM_RECHECK_SECONDS = 15;

    /** Unchanged signature. Appends SESSION_ID_PARAMETER.'={CHECKOUT_SESSION_ID}' ('?' or '&'); records pending after checkoutFor(). */
    public function begin(Series $series, User $peer, string $successUrl, string $cancelUrl): HostedCheckout;
    /** Unchanged signature. First the refund guard (null, nothing written), then grant(), then record(). */
    public function fulfil(string $sessionId, array $metadata, ?string $paymentReference, ?int $amountCents, ?string $currency): ?Access;
    /** completed with payment_status other than paid: pending, payment_reference, completed_at. A granted row keeps granted and gains the two fields. */
    public function awaitPayment(string $sessionId, array $metadata, ?string $paymentReference, ?int $amountCents, ?string $currency): void;
    /** async_payment_failed: failed, failure_code. A granted row is left alone with Log::warning. */
    public function fail(string $sessionId, array $metadata, ?string $paymentReference, ?int $amountCents, ?string $currency, string $failureCode): void;
    /** expired: pending → abandoned; anything else untouched. */
    public function abandon(string $sessionId): void;
    /** cancel_url: the person's newest pending row for the Series with no completed_at → abandoned. */
    public function cancel(User $peer, Series $series): void;
    /** The landing page. Null when the row is not this person's, is failed, was checked within CONFIRM_RECHECK_SECONDS, or the retrieve could not answer. */
    public function confirm(string $sessionId, User $peer): ?Access;
    /** What the Series page shows someone with no Access: the row Confirming renders, or null to refuse. */
    public function confirmingFor(User $peer, string $seriesId): ?PaymentFulfilment;
    /** Gains ?string $failureCode and ?CarbonInterface $completedAt; returns the row. */
    private function record(/* … */): PaymentFulfilment;
}
```

`begin()` writes the row with `group_id`, `series_id`, `user_id`,
`amount_cents` from `$series->price_cents`, `currency` upper-cased as
`fulfil()` does (`:96`), `status` `pending`, and the session id from
`HostedCheckout::$id` (`app/Data/HostedCheckout.php:14`). `fulfil()`'s
existing `record()` calls gain the code: `FAILURE_UNPLACEABLE` at `:105-108`,
`FAILURE_REFUSED` at `:128-130`, none on `granted`. `confirm()`, in order: the
row by `session_id`, null unless `user_id` is `$peer`; `granted` with an
active Access → that Access; `failed` → null; `checked_at` within
`CONFIRM_RECHECK_SECONDS` → null; else `checked_at` is set to now and
`$this->payments->checkoutStatus($row->group, $sessionId, CONFIRM_TIMEOUT_SECONDS)`
runs inside a `try` that catches `AppException`, logs a warning with the
session id and returns null — an `abandoned` row is retrieved too, because the
buyer may have paid from the browser's history. Then `isPaid()` →
`fulfil($status->id, $status->metadata, $status->paymentReference, $status->amountCents, $status->currency)`;
`isComplete()` → `awaitPayment(…)` and null; `isExpired()` → `abandon()` and
null; open → null. `confirmingFor()`: `latestFor()`, then the row when it is
`pending` with `completed_at`, or `pending` and `created_at` within
`CONFIRMING_MINUTES`, or `failed`; null otherwise.

```php
// App\Http\Controllers\StripeWebhookController::__invoke — after the two existing branches
if (! str_starts_with($type, 'checkout.session.')) {
    return response()->json(['ignored' => $type]);
}
$session = (array) ($event['data']['object'] ?? []);
if (($session['mode'] ?? null) === 'subscription') {
    return response()->json(['handled' => 'subscription checkout']);   // as today (:69-71)
}
[$id, $metadata, $reference, $amount, $currency] = $this->sessionArguments($session);   // the five reads at :84-88, once
match ($type) {
    'checkout.session.completed' => ($session['payment_status'] ?? null) === 'paid'
        ? $checkout->fulfil($id, $metadata, $reference, $amount, $currency)
        : $checkout->awaitPayment($id, $metadata, $reference, $amount, $currency),
    'checkout.session.async_payment_succeeded' => $checkout->fulfil($id, $metadata, $reference, $amount, $currency),
    'checkout.session.async_payment_failed' => $checkout->fail($id, $metadata, $reference, $amount, $currency, PaymentFulfilment::FAILURE_PAYMENT_FAILED),
    'checkout.session.expired' => $checkout->abandon($id),
    default => null,   // acknowledged: ['ignored' => $type]
};
return response()->json(['handled' => $type]);
```

```php
// App\Http\Controllers\Shared\SharedController
public function __construct(private CheckoutService $checkout) {}

public function show(Request $request, string $series): Response|RedirectResponse
{
    $peer = CurrentUser::orFail($request);
    $access = Access::forUser($peer)->where('series_id', $series)->first();

    if ($access === null) {
        $sessionId = $request->query(CheckoutService::SESSION_ID_PARAMETER);

        if (is_string($sessionId) && $sessionId !== '' && $this->checkout->confirm($sessionId, $peer) !== null) {
            return to_route('shared.show', $series);   // the clean URL; the Series renders on the next request
        }

        $row = $this->checkout->confirmingFor($peer, $series);
        $paying = $row === null ? null : Series::findForPeer($series);

        if ($row !== null && $paying instanceof Series) {
            return $this->confirming($row, $paying);
        }

        throw AppException::forbidden('errors.access.not_granted', devMessage: …);   // as today (:114-117)
    }
    // CheckoutPending::forget() (:121) is gone; the rest of show() is unchanged.
}

/** shared/Confirming with the props below. */
private function confirming(PaymentFulfilment $row, Series $series): Response;
```

Confirming's props: `series` `{id, title}` as today; `state` `'pending'` or
`'failed'`; `startedAt` from `created_at`; `completedAt` from `completed_at`
or null; `tryAgainUrl` = `route('series.public', [$series->group->slug, $series->slug])`;
`copy` with `title`, `body`, `slow`, `delayed`, `check`, `tryAgain` from
`accesses.confirming.*` and, when failed, `failed` `{message, resolution}`
from `errors.checkout.payment_not_completed` for `isPaymentFailure()` and
`errors.checkout.not_placed` otherwise — every line through
`Terminology::line()` with `['creator' => $series->group->name]` and the
Series' Group. `Confirming.vue`: `state === 'failed'` sets no timer, renders
`failed.message` as the heading and `failed.resolution` beneath, and a `Button`
`as="a"` to `tryAgainUrl` labelled `copy.tryAgain`; `state === 'pending'`
polls as today (`:36-43`) and shows `copy.delayed` instead of `copy.slow`
whenever `completedAt` is set.

## Copy

| Key                                                | File                   | English                                                                                                                                                                |
| -------------------------------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `accesses.confirming.delayed`                      | `lang/en/accesses.php` | Your bank is still confirming the payment. That can take a few days. When it goes through you'll get an email, and the :series page shows anything left for you to do. |
| `accesses.confirming.try_again`                    | `lang/en/accesses.php` | Back to the :series                                                                                                                                                    |
| `errors.checkout.payment_not_completed.message`    | `lang/en/errors.php`   | The payment didn't go through, so the :series hasn't opened.                                                                                                           |
| `errors.checkout.payment_not_completed.resolution` | `lang/en/errors.php`   | Try again from the :series page, with another way to pay if you have one.                                                                                              |
| `errors.checkout.not_placed.message`               | `lang/en/errors.php`   | The payment went through, but the :series could not be opened for you.                                                                                                 |
| `errors.checkout.not_placed.resolution`            | `lang/en/errors.php`   | Let :creator know: they can open it for you, and nothing needs to be paid again.                                                                                       |

`accesses.confirming.title`, `body`, `slow` and `check` (`lang/en/accesses.php:63-68`)
are unchanged. `:creator` is the Group's name, as `accesses.consent.peer`
uses it.

## Routes

None. `shared.show` (`routes/shared.php`) gains the optional `session_id`
query parameter, as `series.public` gained `cancelled` in `T-074`;
`webhooks.stripe` and `checkout.store` (`routes/web.php:38-48`) are unchanged.

## Tests

Every webhook case sends a payload built from the matching fixture under
`tests/Fixtures/stripe/` with the ids and metadata swapped in, through the
existing signed `send()` helper (`StripeWebhookTest.php:49-62`); every retrieve
is `Http::fake()` on `api.stripe.com/v1/checkout/sessions/{id}` answering a
fixture, with `Http::preventStrayRequests()`.

**Changed: `tests/Feature/Checkout/StripeWebhookTest.php` — 8 new cases**

`test_an_unpaid_session_grants_nothing` also asserts the row is `pending`
with `payment_reference` `pi_test_1` and a `completed_at`.

1. `test_an_async_payment_succeeded_event_grants_access` — after a completed-unpaid event for `cs_test_1`, the success event: one active paid Access, row `granted` with `access_id`.
2. `test_an_async_payment_succeeded_event_grants_without_a_prior_completed_event` — delivery order reversed: still granted, the row created by the grant.
3. `test_an_async_payment_succeeded_replay_grants_once` — the same event twice: one Access, one row, one notification.
4. `test_an_async_payment_failed_event_records_the_failure_and_grants_nothing` — 200; row `failed`, `failure_code` `payment_failed`, no Access.
5. `test_a_failed_event_never_downgrades_a_granted_row` — granted first, then `async_payment_failed`: row `granted`, Access active.
6. `test_an_expired_session_is_abandoned_and_a_paid_one_is_not` — `expired` on a pending row → `abandoned`; on a granted row → untouched.
7. `test_a_completed_event_after_the_success_keeps_the_grant` — completed-unpaid after `async_payment_succeeded`: row `granted`, `completed_at` set.
8. `test_other_checkout_session_events_are_acknowledged` — `checkout.session.something_else` → 200 with `ignored`, no row.

**Changed: `tests/Feature/Checkout/ConfirmingTest.php` — 5 rewritten, 12 new**

`test_starting_checkout_remembers_the_payment` asserts a `pending` row for
the buyer and the Series with `cs_1`, 4900 `AUD`, no session key, and the sent
`success_url` decoding to `…/shared/{id}?session_id={CHECKOUT_SESSION_ID}`.
`test_coming_back_before_the_webhook_shows_confirming_not_a_refusal` drops
`withSession()` — a pending row and nothing in the cookie is the other-browser
case — and asserts `state` `pending`. `test_coming_back_with_no_payment_in_progress_is_still_refused`
is unchanged. `test_once_access_exists_the_marker_is_forgotten` becomes
`test_once_access_exists_the_series_renders_and_stripe_is_not_asked`: GET with
`session_id` and an Access → `shared/Show`, `Http::assertNothingSent()`.
`test_cancelling_lands_on_the_series_with_a_note` asserts the row is
`abandoned` instead of the session key missing.

9. `test_landing_with_a_paid_session_grants_before_the_webhook` — Stripe answers the paid fixture: 302 to the clean `shared.show`, Access active and paid, row `granted`, the retrieve carried `Stripe-Account: acct_test`.
10. `test_landing_with_an_open_session_shows_confirming_and_marks_the_check` — the open fixture: Confirming, `checked_at` set, no Access.
11. `test_a_completed_delayed_payment_confirms_however_old_it_is` — pending row, `completed_at` set, `created_at` two days ago, no `session_id`: Confirming with `completedAt`.
12. `test_an_open_session_stops_confirming_after_thirty_minutes` — pending, no `completed_at`, created 31 minutes ago, no `session_id`: 403.
13. `test_landing_with_an_old_open_session_still_asks_stripe` — the same row with `session_id`, Stripe answers paid: granted.
14. `test_a_failed_payment_shows_the_failure_and_a_way_back` — `failed`/`payment_failed`: Confirming, `state` `failed`, `copy.failed.message` is `errors.checkout.payment_not_completed.message`, `tryAgainUrl` the public page.
15. `test_a_payment_that_could_not_be_placed_says_so` — `failed`/`refused`: `errors.checkout.not_placed.message`.
16. `test_an_abandoned_checkout_is_refused` — 403, no retrieve.
17. `test_a_retrieve_that_cannot_connect_leaves_the_row_pending` — `Http::fake()` with `Http::failedConnection()`: Confirming, `checked_at` set, no Access, no exception.
18. `test_the_page_does_not_ask_stripe_twice_within_the_recheck_window` — `checked_at` five seconds ago, GET with `session_id`: `Http::assertNothingSent()`.
19. `test_someone_elses_session_id_is_ignored` — the row belongs to another user: 403, `Http::assertNothingSent()`.
20. `test_a_paid_session_whose_row_was_abandoned_is_still_granted` — `abandoned` row, Stripe answers paid: granted.

**Changed: `tests/Feature/Checkout/PaidFulfilmentTest.php` — 3 new cases**

`test_an_unplaceable_payment_is_recorded_as_failed` also asserts
`failure_code` `unplaceable`.

21. `test_a_failure_after_the_grant_propagates_and_the_replay_records_it` — `PaymentFulfilment::saving()` throws once: `fulfil()` throws `RuntimeException`, the Access exists; the second `fulfil()` returns the same Access, row `granted`, one notification in all.
22. `test_a_rule_refusal_is_recorded_with_its_code` — `AccessService` mocked to throw `AppException::invalidRequest()`: null, row `failed`, `failure_code` `refused`.
23. `test_a_refund_that_arrived_first_is_not_granted` — row with the refund column set (provisional on `T-103`): null, no Access, row untouched.

**Changed: `tests/Feature/Checkout/CheckoutTest.php` — 3 new cases**

24. `test_beginning_a_checkout_records_a_pending_fulfilment` — row `pending`, `cs_test_1`, Series, buyer, Group, 4900 `AUD`, no Access.
25. `test_the_success_url_carries_the_session_id_placeholder_unencoded` — the decoded body contains `success_url=https://ok.test?session_id={CHECKOUT_SESSION_ID}`.
26. `test_the_checkout_sets_no_payment_method_types` — the decoded body contains no `payment_method_types`, pinned the way `test_the_checkout_carries_no_application_fee` pins the fee (`:157-172`).

Total: 26 new; 7 existing cases change as described.

**Changed:**

- `tests/Feature/Access/SeriesAccessContinueTest.php:145` — asserts a `pending` row for the user and Series instead of `CheckoutPending::since()`.
- `tests/Feature/Checkout/StripeWebhookTest.php:168` — `test_other_events_are_acknowledged` stays as it is; case 8 below is the sibling case for an unhandled `checkout.session.*` type.
- `tests/Feature/Enums/ModelEnumTest.php` — untouched; the cast it checks (`:67`) is the same.

## Acceptance

- [ ] A buyer who pays by a delayed method is granted when Stripe's
      `checkout.session.async_payment_succeeded` arrives, in whichever order
      the events are delivered, once; one whose payment fails sees the
      sentence and a way back to the Series; nothing downgrades a grant
- [ ] Returning from Stripe in a different browser, or hours later, shows
      Confirming while the money is in flight and the Series once it lands;
      landing with the session id grants before the webhook when Stripe
      already says paid, within `CONFIRM_TIMEOUT_SECONDS`; an open session
      older than `CONFIRMING_MINUTES` without the id is refused as today
- [ ] A failure after the Access is written propagates, Stripe's redelivery
      ends `granted`, and no later step ever undoes an Access
- [ ] The six fixtures are committed, redacted and dated; the sandbox walk is
      in the report: one `4242` purchase landing in a second, signed-out
      browser, and one `stripe trigger --stripe-account`
      `async_payment_succeeded` against a session the app created
- [ ] `docs/flows/checkout.md`, `billing.md` and the tinker recipe describe
      what was built; `CheckoutPending` is gone and nothing references it
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Leave `payment_method_types` unset, so the creator's Dashboard decides, or
  restrict Qori's sessions to `card` — the owner's.
- Whether a buyer whose delayed payment failed also gets an email, and from
  which stream — the owner's; the draft sends none.
- The provisional numbers: `CONFIRM_TIMEOUT_SECONDS` 5,
  `CONFIRM_RECHECK_SECONDS` 15, `CONFIRMING_MINUTES` 30 — the owner's.
- The name of `T-103`'s refund column, and whether a refund arriving first is
  recorded on the fulfilment row at all — anyone's, with `T-103`.
- Capture the six fixtures; confirm whether `async_payment_succeeded` carries
  `payment_status` `paid` — anyone with the sandbox.
- Confirm from the same capture that Connect events reach the platform
  endpoint with `account` at the top level
  (`StripeWebhookController.php:48-50`) — anyone with the sandbox.
- Whether `checkout.session.expired` is delivered for a connected account; if
  not, `abandon()` is reached only from the retrieve — anyone, same capture.
- `T-091` claims `SharedController.php`, `lang/en/errors.php` and
  `docs/tinker/accesses.md` too; whichever is specified second depends on the
  first — the two stream owners'.
- `T-091`'s case 39 asserts a `granted` fulfilment while its vendor grant is
  `pending`; keep it and case 21 here saying the same thing — anyone's.
- `T-102` and `T-103` are not yet listed in `streams/selling.md`'s order —
  the owner's, as the stream file is.

### From the storage review, 20 September 2026

- **Fulfilled payment can mean an indefinite wait nobody owns** (`F06`). A
  delayed payment that completes at 02:00 can leave the vendor grant
  `needs_creator` while this task records fulfilment as `Granted`: the buyer
  reads that the creator has been told and has nothing to do, a token failure
  emails the creator once, and an ordinary policy or capacity refusal emails
  nobody and appears only on a settings page the creator may never open.
  Delivery needs an age, an accountable owner and an escalation path, and the
  measure has to be payment to usable access rather than payment to an Access
  row — the owner's, with `T-103`.

## Re-scope log

None.

## Notes

The blueprint's citations were a day old when this was written and several
moved. Read after `T-084`'s commit (`ffb3c54`, 16 September 2026), which added
a line to `SeriesAccessController::verify()`: the Confirming branch is
`SharedController.php:97-118`, `CheckoutPending::mark()` is
`SeriesAccessController.php:159` and `CheckoutController.php:51`, and
`success_url` is `SeriesAccessController.php:155`. The payload block in
`Connect.php:197-218` and `CheckoutController.php:38-58` are as first cited.
Re-read all of them when claiming.

Stripe's fulfilment guide says Checkout "waits up to 10 seconds for your
server to respond to the webhook event delivery before redirecting", so with
a healthy endpoint the browser usually lands after the grant; the row and the
retrieve are for every other case, and for the endpoint `PLAN.md` still lists
as unconfigured in production.

`CLAUDE.md` says integrations expose `name()` and are bound in
`AppServiceProvider`; the code binds `SellsSeries` to `Connect` in
`app/Providers/IntegrationServiceProvider.php:29` and nothing here needs a
slug. `errors.php` entries older than the vocabulary rule spell "series" in
lower case (`lang/en/errors.php:255-263`); this task's lines carry `:series`
and are rendered through `Terminology`, and the older ones are not its job.

The `unplaceable` row keeps `group_id` and `user_id` null and is the reason
the table is not group-scoped (`app/Models/PaymentFulfilment.php:11-18`);
`latestFor()` can never find it, which is right — it belongs to nobody Qori
can name.

**23 September 2026 — `T-027` reads the marker in three more places.** While
`CheckoutPending::since()` holds and there is no Access, the public Series
page shows "Your payment is being confirmed" in place of the button, and
`CheckoutController::store()` and the priced branch of
`AcceptsInvitations::acceptInvitation()` send a second attempt to the
Confirming page instead of calling `begin()`; `DELETE s/{seriesId}/checkout`
(`series.checkout.abandon`) forgets the marker for a buyer who did not pay.
When this task replaces the marker with the pending row, those reads move to
the row and Start again abandons it. It depends on `T-027` for
`PublicSeriesController.php`, `CheckoutController.php` and `ConfirmingTest.php`.

**24 September 2026 — `T-027` built.** One gap it left for this task: the
Confirming page offers no way back to the Series for somebody who did not pay.
"Check now" on the Series page lands there, and only the Series page's "Didn't
pay? Start again" forgets the marker, so a buyer who pressed Check now waits
on "Confirming your payment" until they find the Series link again. When
Confirming is chosen from the row, it can carry Start again itself.
