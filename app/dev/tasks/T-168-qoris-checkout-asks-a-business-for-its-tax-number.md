---
id: T-168
title: Qori's checkout asks a business for its tax number
stream: selling
status: ready
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-168 — Qori's checkout asks a business for its tax number

## Why

Qori's creators are mostly businesses, and Qori's subscription checkout never
asks for a tax number. Today:

- a business abroad has no way to give its VAT or GST number, so nothing
  records that it accounts for the tax itself;
- its invoice carries the Group's name, not its legal business name;
- nothing is ready for the day Qori registers for tax somewhere.

`D-046` keeps Qori's subscription on Stripe Billing rather than a merchant of
record, which makes this Qori's job.

Afterwards:

- Stripe's page offers the tax number field;
- the number and the legal name are saved on the Stripe customer and printed
  on its invoices (Stripe checks ABNs and EU and UK VAT numbers against
  government records on its own);
- tax calculation is one setting away, for when it is needed.

## Decisions taken to make this specifiable

- **The tax number is asked for on every subscription checkout and never
  required.** A private person may subscribe, and requiring a number would
  turn away a creator who has none. Stripe shows the field only where the
  buyer's location supports one.
- **`customer_update[name]=auto` goes with it.** This is Stripe's documented
  form for an existing customer
  ([Stripe](https://docs.stripe.com/tax/checkout/tax-ids)). The legal name
  typed on Stripe's page replaces the Group's name on the Stripe customer,
  which is what an invoice should carry. Qori never reads the customer's name
  back, so nothing in Qori changes.
- **`customer_update[address]=auto` goes with it too.** The billing address
  typed on Stripe's page is saved to the customer. Stripe uses it to decide
  whether to show the tax number field, and any later tax calculation reads
  it.
- **Calculating tax sits behind a switch, `services.stripe.automatic_tax`
  (`STRIPE_AUTOMATIC_TAX`), off by default.** While Qori is registered nowhere
  it calculates nothing. And unless the Stripe account has Stripe Tax set up,
  a session asking for it should be refused (the spike checks this), which
  would fail every upgrade on a deploy that went out before the dashboard was
  set up. Turning it on is part of registering, on the release checklist, not
  a deploy.
- **The switch is in `config/services.php`, beside `client_id`.** It mirrors a
  setting on Stripe's side of the account, the way `client_id` does.

## Preconditions

**Data this task verifies against:** a local Group owned by a user, whose
`start` monthly row points at a sandbox price. `docs/tinker/e2e-first-share.md`
has the owner's sandbox; any Group the owner can sign in as will do.

**Equipment:**

- The Stripe sandbox, with `STRIPE_SECRET` in `.env`.
- `stripe listen --forward-to localhost:8001/webhooks/stripe` running.
- A browser.

**Spike.** The request parameters are Stripe's documented ones, and nothing
Qori reads back changes, so this needs no fixture. Two things are checked
against the sandbox and written in the report:

1. Subscribe from `/g/{group}/billing` with the new parameters. On Stripe's
   page, pick a German billing address, tick the business purchase, enter
   `DE123456789` and a legal name, and pay with `4242 4242 4242 4242`. Then
   read the customer back (`stripe customers retrieve <id> --expand tax_ids`):
   its `name` is the legal name, and `tax_ids` holds the number.
2. Create one session with `automatic_tax[enabled]=true` against the sandbox
   and keep Stripe's answer. A refusal confirms the reason for the switch.
   Success means the sandbox already has Stripe Tax set up; say so, and the
   switch stays anyway.

## Scope

**In:**

- `tax_id_collection[enabled]`, `customer_update[name]` and
  `customer_update[address]` on every session `Subscription::subscribeUrl()`
  creates.
- `automatic_tax[enabled]` on those sessions only while
  `services.stripe.automatic_tax` is true.
- `docs/flows/billing.md` saying both.

**Out:**

- Registering for tax anywhere, setting up Stripe Tax, and whether the prices
  include tax. These are release checklist (`D-046`, `release-prerequisites.md`).
- Requiring the number (`tax_id_collection[required]`). See Decisions.
- Storing the number in Qori. Stripe keeps it on the customer and prints it on
  invoices; nothing in Qori reads it.
- Editing tax numbers in the Customer Portal. That is a portal setting in
  Stripe's dashboard, not code.
- The currency of the prices: `T-167`.

## Files

| Path                                          | Change | Notes                                           |
| --------------------------------------------- | ------ | ----------------------------------------------- |
| `app/Integrations/Stripe/Subscription.php`    | edit   | the four parameters in `subscribeUrl()`         |
| `config/services.php`                         | edit   | `stripe.automatic_tax`, with its reason         |
| `.env.example`                                | edit   | `STRIPE_AUTOMATIC_TAX=false` in the Stripe block |
| `docs/flows/billing.md`                       | edit   | "Qori billing the creator": what checkout asks for |
| `tests/Feature/Checkout/SubscriptionTest.php` | edit   | three cases                                     |

## Database

None.

## Code

```php
// config/services.php, inside 'stripe'
// Whether checkout asks Stripe to calculate tax. Off until Stripe Tax is set
// up on the account and Qori is registered somewhere: a session asking for it
// before then is refused, which would fail every upgrade (D-046).
'automatic_tax' => (bool) env('STRIPE_AUTOMATIC_TAX', false),
```

```php
// App\Integrations\Stripe\Subscription::subscribeUrl() — added to the
// checkout/sessions body, after the metadata
// A business abroad that gives its VAT or GST number accounts for the tax
// itself, and its invoice carries the number and its legal name (D-046).
'tax_id_collection[enabled]' => 'true',
'customer_update[name]' => 'auto',
'customer_update[address]' => 'auto',
...(config('services.stripe.automatic_tax') ? ['automatic_tax[enabled]' => 'true'] : []),
```

The strings `'true'` follow `Connect::requestCapabilities()`, which sends
Stripe's booleans the same way.

## Copy

None. The field and its label are on Stripe's page.

## Routes

None.

## Tests

**Changed: `tests/Feature/Checkout/SubscriptionTest.php` — 3 new cases**

1. `test_the_checkout_asks_for_a_tax_number` — `Http::fake()` the session
   call, subscribe, and assert the body carries `tax_id_collection[enabled]` =
   `true`, `customer_update[name]` = `auto` and `customer_update[address]` =
   `auto`.
2. `test_the_checkout_does_not_calculate_tax_while_it_is_switched_off` — with
   the default config, the body has no `automatic_tax[enabled]`.
3. `test_the_checkout_calculates_tax_when_it_is_switched_on` —
   `config(['services.stripe.automatic_tax' => true])`, and the body carries
   `automatic_tax[enabled]` = `true`.

Total: 3. `EnvExampleTest` passes because of the `.env.example` line.

## Acceptance

- [ ] Stripe's page offered the tax number, and the number and legal name landed on the sandbox customer
- [ ] Stripe's answer to a session with `automatic_tax` on is recorded in the report
- [ ] With the switch off a session carries no `automatic_tax`; with it on, it does
- [ ] `docs/flows/billing.md` says what checkout asks for and that tax calculation waits on `STRIPE_AUTOMATIC_TAX`
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

- Written 22 September 2026 from `D-046`, at the owner's request to follow
  the decision with the checkout change.
- `T-164` (done the same day) rewrote the Connect sections of
  `docs/flows/billing.md`. This task edits only "Qori billing the creator".
