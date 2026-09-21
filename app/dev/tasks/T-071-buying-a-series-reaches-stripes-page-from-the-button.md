---
id: T-071
title: Buying a Series reaches Stripe's page from the button
stream: selling
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-071 — Buying a Series reaches Stripe's page from the button

## Why

The owner signed up a Peer, opened a priced Series and pressed "Get access —
$90". Nothing happened on screen, so they pressed it again. Stripe holds two
open, unpaid checkout sessions for that Peer five seconds apart and no payment
attempt: the sessions were created, the browser never reached Stripe's page.

The public page submits through Inertia's `<Form>`, which is an XHR, and
`CheckoutController::store()` answers with `redirect()->away()`, a plain 302
to `checkout.stripe.com`. Inertia cannot follow a redirect to another origin
from an XHR; it needs `Inertia::location()`, which answers 409 with the URL in
a header and lets the client set `window.location`. The billing page links
out with plain anchors and the connect button is a native GET form, so those
two never met this. The connect button will, when `T-062` makes it a POST.

Afterwards: pressing the button lands on Stripe's payment page, once.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- `CheckoutController::store()` answering through `Inertia::location()`.
- Two tests: an Inertia request gets the 409 and the URL; a plain request
  still gets the 302.
- A line on `T-062` so `connect()` does the same when it becomes a POST.

**Out:**

- The billing redirects, which plain anchors reach.
- Anything about the Stripe page itself.

## Files

| Path                                          | Change | Notes                    |
| --------------------------------------------- | ------ | ------------------------ |
| `app/Http/Controllers/CheckoutController.php` | edit   | `Inertia::location()`    |
| `tests/Feature/Checkout/BuyButtonTest.php`    | new    | 2 cases                  |
| `docs/planning/tasks/T-062-…`                 | edit   | One line under Decisions |

## Database

None.

## Code

```php
// App\Http\Controllers\CheckoutController::store()
return Inertia::location($session->url);
// return type: \Symfony\Component\HttpFoundation\Response
```

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/Checkout/BuyButtonTest.php` — 2 cases**

1. `test_the_button_sends_the_browser_to_stripe` — a signed-in Peer posts
   `checkout.store` with the `X-Inertia` header for a published, priced Series
   whose Group has an account, Stripe's session endpoint faked: status 409 and
   `X-Inertia-Location` is the session URL. **Fails today** with a 302.
2. `test_a_plain_request_is_still_redirected` — the same without the header:
   302 to the session URL.

## Acceptance

- [x] Pressing "Get access" on a priced Series opens Stripe's payment page
- [x] A non-Inertia client is still redirected
- [x] `T-062` says `connect()` answers through `Inertia::location()`
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Found the same afternoon: the local `.env` webhook secret did not match the
Stripe CLI's, so a completed payment would have been rejected as an invalid
signature and no access granted. Local configuration, not code; fixed on the
owner's machine and recorded here so the next person checks it first.
