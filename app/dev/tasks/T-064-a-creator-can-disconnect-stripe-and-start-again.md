---
id: T-064
title: A creator can disconnect Stripe and start again
stream: selling
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-064 — A creator can disconnect Stripe and start again

## Why

Once a Group holds a `connect_account_id` there is no way to let go of it: no
button, no route, and the webhook ignores `account.application.deauthorized`,
so a creator who disconnects Qori from inside their Stripe dashboard leaves
Qori sending checkouts to an account that will refuse them. The owner asked on
13 September 2026 for a disconnect that puts the page cleanly back to its
"connect" state, and then, once their sandbox account went active, asked why
the connected state still offered "Continue on Stripe". It does because the
page renders one form for every state and only swaps its label.

Afterwards: a connected account offers Disconnect and nothing else; an owner
can disconnect after a confirmation that says what it will cost them; the page
returns to offering the connect door; and a disconnect made from Stripe's side
is honoured within one webhook.

## Decisions taken to make this specifiable

**Disconnect is Qori forgetting.** `connect_account_id` becomes null. Qori does
not delete the creator's Stripe account: it is theirs, may be used elsewhere,
and a live Standard account cannot be deleted by a platform anyway. Telling
Stripe the connection is over needs the OAuth client id, which `T-063` brings;
that task adds the `/oauth/deauthorize` call in front of this one's clearing.

**Owner-only.** §15 puts Connect with billing and deletion, and
`errors.billing.owner_only` already says so in a comment; the controller never
enforced it. This task adds `guardOwner()` to the controller and the
`errors.payouts.owner_only` copy, and applies the guard to `disconnect()`.
`connect()` joins it in `T-062`, which is also where that action changes verb.

**The buttons follow the state.** Not started: "Connect with Stripe", as today.
Pending: "Continue on Stripe", because the form may be unfinished, and
Disconnect beside it for starting over. Ready: Disconnect only. Nothing else
on the page changes.

**`PayoutsService` starts here.** With the read, the disconnect and the
webhook's forget. `T-062` gives it the connect and refresh writes and moves
`connect()` onto it; until then `connect()` keeps its method-injected
`SellsSeries` and its request class, untouched.

**Priced Series stay priced.** `CheckoutService` already refuses with
`errors.checkout.not_connected`, and the Series page already says payouts are
needed (`T-054`). The confirmation says how many priced Series stop being
purchasable, so the creator decides knowing that.

**Reconnecting creates afresh.** After a disconnect, the connect button creates
a new account. The old one still exists at Stripe under the creator's login;
`T-063` is the door for using it again.

**Re-sequenced on 13 September.** This task first waited on `T-062`. Nothing
in it needs the POST form or the un-pinned country, and `T-062` carries a
sandbox check that could stall it, so it now goes first and `T-062` builds on
the service and the guard it leaves behind.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The route, the action, and `PayoutsService` with `account()`,
  `disconnect()` and `forget()`.
- `guardOwner()` on the controller, applied to `disconnect()`.
- The `account.application.deauthorized` branch in the webhook controller.
- The connected states of the Payments page: the confirmation dialog, and the
  "Continue on Stripe" form hidden when the account is ready.
- One paragraph in `docs/flows/checkout.md`.

**Out:**

- Any call to Stripe (`T-063`).
- `connect()`, its verb, its request class and its guard (`T-062`).
- Unpricing Series, warning peers, or touching accesses already granted. A
  purchase made before the disconnect stays an access.
- A record of past connections. Null is the whole state.

## Files

| Path                                               | Change | Notes                                                       |
| -------------------------------------------------- | ------ | ----------------------------------------------------------- |
| `routes/share.php`                                 | edit   | `DELETE payouts/connection`                                 |
| `app/Http/Controllers/Share/PayoutsController.php` | edit   | Service by constructor; `disconnect()`; guard; dialog props |
| `app/Services/PayoutsService.php`                  | new    | `account()`, `disconnect()`, `forget()`                     |
| `app/Http/Controllers/StripeWebhookController.php` | edit   | One branch; service by constructor                          |
| `resources/js/pages/share/Payouts.vue`             | edit   | Dialog; form hidden when ready                              |
| `lang/en/payouts.php`                              | edit   | Seven lines                                                 |
| `lang/en/errors.php`                               | edit   | `payouts.owner_only`                                        |
| `docs/flows/checkout.md`                           | edit   | Disconnect, both directions                                 |
| `tests/Feature/Share/PayoutsDisconnectTest.php`    | new    | 7 cases                                                     |

## Database

None.

## Code

```php
namespace App\Services;

class PayoutsService
{
    public function __construct(private SellsSeries $payments) {}

    /** What the vendor holds for this Group, or null when no account exists. */
    public function account(Group $group): ?ConnectAccount;

    /** Forget the account. The Stripe side is T-063's. */
    public function disconnect(Group $group): void;

    /** Stripe said the creator disconnected: clear every Group holding this id. Returns rows cleared. */
    public function forget(string $accountId): int;
}
```

`forget()` is `Group::query()->where('connect_account_id', $accountId)->update(['connect_account_id' => null])`,
and answers 0 for an empty id without querying. `Group` carries no group
scope, so no escape hatch is needed.

```php
// App\Http\Controllers\Share\PayoutsController
public function __construct(private PayoutsService $payouts) {}

public function show(string $group, CurrentGroup $current, Terminology $terminology): Response;
public function disconnect(string $group, CurrentGroup $current): RedirectResponse;
// guardOwner; $this->payouts->disconnect($model);
// Inertia::flash('toast', ['type' => 'success', 'message' => __('payouts.disconnected')]);
// to_route('share.payouts.show', $model->slug)

private function guardOwner(CurrentGroup $current): void;
// AppException::forbidden('errors.payouts.owner_only', devMessage: 'Payouts are owner-only (§15).')
```

`show()` and `return()` read through `$this->payouts->account($model)`.
`show()` gains two props, both null-or-absent when `status` is `not_started`:

```php
'pricedSeriesCount' => Series::query()->whereNotNull('price_cents')->count(),   // group-scoped by the trait
'disconnect' => [
    'label' => __('payouts.disconnect_label'),
    'title' => __('payouts.disconnect_title'),
    'body' => $terminology->line('payouts.disconnect_body', [], $model),
    'priced' => $terminology->choice('payouts.disconnect_priced', $count, [], $model),
    'confirm' => __('payouts.disconnect_confirm'),
    'keep' => __('payouts.disconnect_keep'),
],
```

```php
// App\Http\Controllers\StripeWebhookController — before the checkout branch
if ($type === 'account.application.deauthorized') {
    $this->payouts->forget((string) ($event['account'] ?? ''));

    return response()->json(['handled' => $type]);
}
```

Connect events carry the connected account id at the top level of the event
as `account`. The constructor gains `private PayoutsService $payouts`.

In `Payouts.vue`, the existing GET form gets `v-if="status !== 'ready'"`. The
`ready` and `pending` states render a `Dialog` (the archive dialog in
`share/series/Show.vue` is the pattern): `DialogTrigger` is an outline
`Button` with `disconnect.label`; the content shows `disconnect.title`,
`disconnect.body` and, when `pricedSeriesCount > 0`, `disconnect.priced`; the
footer has `DialogClose` with `disconnect.keep` and a
`<Form method="delete" :action="`/g/${group.slug}/payouts/connection`">` whose
submit is a destructive `Button` with `disconnect.confirm`.

## Copy

| Key                                    | File                  | English                                                                                                                                |
| -------------------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `payouts.disconnect_label`             | `lang/en/payouts.php` | Disconnect Stripe                                                                                                                      |
| `payouts.disconnect_title`             | `lang/en/payouts.php` | Disconnect Stripe?                                                                                                                     |
| `payouts.disconnect_body`              | `lang/en/payouts.php` | Qori will stop taking payments for your :series_plural until you connect again. Your Stripe account and the money in it are untouched. |
| `payouts.disconnect_priced`            | `lang/en/payouts.php` | `{1} One priced :series will stop being purchasable.\|[2,*] :count priced :series_plural will stop being purchasable.`                 |
| `payouts.disconnect_confirm`           | `lang/en/payouts.php` | Disconnect                                                                                                                             |
| `payouts.disconnect_keep`              | `lang/en/payouts.php` | Keep it                                                                                                                                |
| `payouts.disconnected`                 | `lang/en/payouts.php` | Stripe is disconnected. Connect again whenever you're ready.                                                                           |
| `errors.payouts.owner_only.message`    | `lang/en/errors.php`  | Only the owner can change how payments are taken.                                                                                      |
| `errors.payouts.owner_only.resolution` | `lang/en/errors.php`  | Ask the owner to make the change.                                                                                                      |

## Routes

| Verb   | Path                           | Name                       | Action                         |
| ------ | ------------------------------ | -------------------------- | ------------------------------ |
| DELETE | `g/{group}/payouts/connection` | `share.payouts.disconnect` | `PayoutsController@disconnect` |

## Tests

**New: `tests/Feature/Share/PayoutsDisconnectTest.php` — 7 cases**

1. `test_the_owner_can_disconnect` — DELETE as owner with an id stored: id
   null, 302 to `share.payouts.show`.
2. `test_an_admin_is_refused` — 302 back with an error toast, which is how an
   `AppException` renders on a non-GET request, and the id unchanged.
3. `test_the_page_offers_disconnect_only_when_connected` — `disconnect` prop
   present with an account (v2 read faked), absent without.
4. `test_the_page_counts_priced_series_for_the_dialog` — two priced and one
   free Series in the Group, one priced in another Group: `pricedSeriesCount`
   is 2.
5. `test_stripe_saying_the_creator_disconnected_clears_the_account` — a signed
   `account.application.deauthorized` event with `account: acct_x` (signed
   the way `StripeWebhookTest::send()` signs): 200, the Group holding `acct_x`
   is cleared, a Group holding `acct_y` is not.
6. `test_an_unknown_account_in_that_event_is_acknowledged_and_changes_nothing`
   — 200, no Group changed.
7. `test_after_disconnecting_the_button_creates_a_fresh_account` — disconnect,
   then the connect action with both endpoints faked: a new id is stored.

**Changed:** none.

## Acceptance

- [x] A connected account offers Disconnect and not "Continue on Stripe"
- [x] An owner can disconnect from the Payments page after a confirmation that
      names the priced Series count
- [x] After disconnecting, the page offers the connect door again and the next
      connect creates a fresh account
- [x] A non-owner cannot disconnect
- [x] `account.application.deauthorized` clears the matching Group and is
      acknowledged
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

The public Series page still shows a price and a buy button for a Series whose
Group has disconnected; the peer finds out at checkout, with
`errors.checkout.not_connected`. That was true before this task and belongs to
the public page, not here. Worth a task of its own once `T-058` lands, since
that is the file it would touch.

The page is Vue and there is no JavaScript test runner, so which button
renders in which state is asserted through the props the template branches on,
not the rendered markup. Same limit `PayoutsPageTest` states.
