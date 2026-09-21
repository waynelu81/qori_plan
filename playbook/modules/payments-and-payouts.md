# Module: payments and payouts

**What it is.** Two different money problems that get confused. **Billing** is
the product charging its own customers for the product. **Payouts** is the
product letting its customers take money from *their* customers and keeping
none of it. They share a vendor and almost nothing else.

**Done when.** A creator can connect the payout account they already have, set
a price with a currency, and a buyer can pay — with the access that payment
bought delivered whatever the creator's plan says.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| Does the product create payout accounts, or connect existing ones? | **Connect only.** Send them to the vendor's own sign-in; they use the account they have or open one there | See the case study. Creating accounts drags in country, entity type, capabilities and hosted onboarding — all of it the vendor's own form does better. |
| Direct or destination charges? | Direct — the money never touches the platform | Different regulatory posture, different refund ownership, different terms. Decide before writing the terms of service, not after. |
| What is the platform's cut? | 0% at release | Whatever it is, it is a decision with legal copy attached. |
| Can a price exist without a currency? | No — one field pair, validated, written and constrained together | A price with no currency reaches the vendor as an empty string. A database check constraint, not just a form rule. |
| Does repricing change what existing customers paid? | No — the entitlement carries its own price and currency from fulfilment | Otherwise a reprice rewrites history and every receipt disagrees with the record. |
| Who is the vendor's customer — the person or the tenant? | The tenant | Get this wrong and a person with two tenants has one billing relationship for two plans. |
| Can a plan limit refuse fulfilment after payment? | **Never** | Money creates an obligation. Check the limit before taking the money. |
| Is the vendor named in customer-facing copy? | Yes, for the payment gateway specifically, confirmed one vendor at a time | "Connect Stripe" tells a creator more than "Connect payouts". Naming other vendors is a separate decision each time. |

## Connect what they have; do not open one for them

Qori built the other way first, and the reversal is worth the page.

The original design created a connected account through the vendor's newer
Accounts API, minted an onboarding link, and sent the creator to fill it in.
That meant the product had to ask a country first — the sandbox refused every
account shape without one — so the product grew a country selector, a
capability request, and an entity-type question, each one a thing to validate,
translate and support.

Then the requirement was stated plainly: *creators already have an account;
connect that*. The vendor's newer API has no flow for "use the account I have"
— its own documentation points back to OAuth for that. So the whole creation
path came out: no account creation, no account links, no country question.
Onboarding became three methods — build the sign-in URL, read the landing and
exchange the code, handle the decline — and the creator picks their own
country on the vendor's page, where they were going to have to anyway.

**The lesson that transfers:** when a vendor offers both "create an account for
your user" and "connect the account your user has", the second is almost always
the product you want, and it is almost always documented worse. Check which one
your customers actually need *before* designing to the API that markets itself
harder.

A second one from the same work: **two doors, one column.** Whichever way an
account arrives, read it back through one endpoint and store it in one field,
so the rest of the product never asks how it got there.

## Build order

1. **Money as a type.** Integer minor units plus an explicit currency, one
   formatter, everywhere. Never a float. Needs nothing, and everything needs it.
2. **Price on the sellable thing**, as a constrained pair. Needs 1.
3. **Connect the payout account** through the vendor's OAuth: begin, finalise,
   decline. Needs nothing.
4. **Disconnect**, so a creator can start again. Needs 3.
5. **Checkout** — the buy button reaches the vendor's hosted page. Needs 2, 3.
6. **Fulfilment** — the webhook grants what was bought and sends the mail that
   says so. Needs 5.
7. **Statement descriptor** — the Series says how the charge will read on a
   card statement. Needs 5.
8. **Billing for the product's own plans**, tenant as the vendor's customer.
   Independent of 3–7.

## Rules that bite

- **Fulfilment cannot be refused by a plan limit.** Check before the money.
- **The webhook is the source of truth, not the redirect.** A buyer closing the
  tab still paid.
- **Reconciliation age is a metric worth having** — how long between a payment
  and the entitlement it bought.
- **An entitlement stores the price it was bought at.** So does a refund.
- **The platform's own billing and the creator's payouts are separate code
  paths** that happen to share a vendor folder. Sharing an abstraction between
  them couples two things with different lifecycles.

## Native contract

**Not proven.** What iOS and Android will need:

- Hosted checkout opens in a **system browser**, not a webview — card
  autofill, 3-D Secure and the vendor's own fraud signals all degrade in one.
- App-store rules may require their own purchase mechanism for digital goods
  sold to consumers. This is a commercial decision with a revenue-share
  attached and it must be settled before a native release, not during review.
- The OAuth connect flow is the creator's, not the buyer's — likely web-only
  for the first native release.

## Traps

| Symptom | Cause |
| --- | --- |
| "Checkout fails with an empty currency" | A price column with no currency beside it. |
| "The vendor refuses every account we create" | A newer accounts API needing a merchant configuration the product never sent. The fix was not sending more; it was not creating accounts. |
| "A creator connected the wrong account and cannot change it" | No disconnect. |
| "Someone paid and got nothing" | Fulfilment behind a plan limit, or fulfilment on the redirect rather than the webhook. |
| "The charge is disputed because they did not recognise it" | No statement descriptor. |

## Proven / Not proven

**Proven** against the real vendor in test mode: OAuth connect and disconnect,
reading the account back, pricing with currency, the buy button reaching hosted
checkout.

**Not proven**: live-mode configuration and the production webhook endpoint;
refunds end to end; the product's own subscription billing under load;
reconciliation age as an observed metric.

## Source

Qori tasks `T-050`, `T-054`, `T-058`, `T-061`, `T-062`, `T-063`, `T-064`,
`T-071`, `T-072`, `T-112`, `T-113`, `T-146`. Decisions `D-005`, `D-009`,
`D-010`, `D-023`, `D-035`. Stream `selling`.
