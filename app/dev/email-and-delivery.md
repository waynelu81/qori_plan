# Email economics and delivery build spec

> Cost research and the phased SES broadcast specification; transactional Postmark remains a separate production prerequisite.

[Current plan](../../PLAN.md) | [Planning index](README.md)

Visual composition and message-family requirements are in the proposed
[system email design](ui-system-email.md). That specification distinguishes the
six current transactional messages from unbuilt OTP, order and fulfilment
notifications; the economics below are preserved research, not a visual spec.

## Email economics — researched 2026-09-06

Prompted by a real Mailjet invoice from the human's current role (ParkCollect),
August 2026. The question was whether including EDM at free/Start can ever pay.

**The short answer: yes, but not on a per-1,000 price like that, and never
uncapped.** Two separate problems were tangled together — provider choice and
plan design — and they need separate fixes.

### What the invoice actually says

|                      |                                        |
| -------------------- | -------------------------------------- |
| Mailjet Premium plan | $470.00 — includes 500,000 messages    |
| Overage              | 268,384 × $0.0012 = $322.06            |
| **Total**            | **$792.06 for 768,384 messages/month** |
| Blended              | **$1.03 per 1,000**                    |
| Marginal             | **$1.20 per 1,000**                    |

Correcting an earlier estimate in this file: the working assumption was ~240,000
messages a month, which made the markup look worse than it is. At 768,384 the
$470 base amortises much better, and Mailjet's blended $1.03/1,000 is a
reasonable commercial rate — the structure (high base, cheap margin) is actually
platform-friendly compared with Postmark's.

### 500k is the top tier, so overage is permanent

A dashboard reading on day 6 of the following month: **139,194 / 500,000** —
23,199/day, projecting 696,000–719,000 for the month, consistent with the
invoice.

The cap is crossed on **day 21.6**. Roughly **eight days of every month are pure
overage**, and since Premium's 500,000 is the largest published tier, the
"Upgrade now!" prompt in that dashboard leads nowhere. There is no bigger plan.
Every additional email costs full marginal rate, permanently, and the bill grows
linearly with the business:

| Volume/month       | Mailjet | SES  | Saving                  |
| ------------------ | ------- | ---- | ----------------------- |
| 768,384 _(actual)_ | $792    | $102 | $690/mo — **$8,283/yr** |
| 1,000,000          | $1,070  | $125 | $945/mo — $11,341/yr    |
| 1,500,000          | $1,670  | $175 | $1,495/mo — $17,941/yr  |
| 2,000,000          | $2,270  | $225 | $2,045/mo — $24,541/yr  |

**The gap widens with growth**, because SES has no tier structure at all: $0.10
per 1,000 at ten thousand emails and at a hundred million. Mailjet's leverage is
exhausted; SES's never engages.

There is a cheaper-to-execute option worth trying first: **a permanent overage
of ~200k/month at the top of the published card is real negotiating leverage.**
Mailjet lists a custom Enterprise tier, and a negotiated rate could plausibly
halve the overage with no engineering at all. Worth one email before committing
to a migration — the SES case survives either way, it just gets less urgent.

### The connection to Qori's own promise

Worth naming, because it is the same argument twice. Qori's pitch to creators is
_your success does not raise your bill_ — the thing that makes 0% on their own
Stripe structural rather than promotional. A platform making that promise should
not buy its own infrastructure from a vendor whose pricing does the opposite. A
send tier that runs out is exactly the shape of the student cap Qori refuses to
impose.

### The rate card, 2026, per 1,000 emails

| Provider        | Marginal rate  | Notes                                                                                                     |
| --------------- | -------------- | --------------------------------------------------------------------------------------------------------- |
| **Amazon SES**  | **$0.10**      | Flat at any volume. +$24.95/mo per dedicated IP, ~$0.12/GB transfer                                       |
| Resend          | ~$0.40–0.80    | Pro $20 covers 50k. Its _marketing_ product bills by contacts, the wrong model here                       |
| Mailjet Premium | $1.20          | Observed. $1.03 blended at 768k                                                                           |
| **Postmark**    | **$1.20–1.80** | $15/mo includes 10k; overage $1.80 Basic, $1.20 Platform. Transactional and broadcast share one allowance |
| Brevo           | ~$1.80 entry   | Bills by sends with unlimited contacts — right _shape_, Postmark's price                                  |

### Same volume, priced every way

| Provider                   | Cost for 768,384/month                          |
| -------------------------- | ----------------------------------------------- |
| **Amazon SES**             | **$101.79** ($76.84 send + $24.95 dedicated IP) |
| Mailjet Premium _(actual)_ | $792.06                                         |
| Postmark Platform          | $922.06                                         |
| Postmark Basic             | $1,383.09                                       |

Two conclusions, and the second one revises the spec:

1. **SES is 7.8× cheaper all-in and 12× cheaper at the margin.** On the current
   role's volume that is **$690/month, or $8,283/year**, being spent on
   deliverability management, bounce handling and a UI. Real value for a single
   business with no engineering; poor value for a platform, which amortises that
   work across every tenant.
2. **§9's choice of Postmark would be worse than the thing being complained
   about.** At this volume Postmark costs $130–591/month _more_ than Mailjet.
   Postmark is excellent and correctly chosen for transactional mail, where
   volume is low and a missing magic link is fatal. As a broadcast provider at
   scale it is the most expensive option on the list.

### The real risk is variance, not the average

Modelled against Start at $44/month with **unlimited** sending, marginal cost only:

| Creator profile          | Emails/mo | SES    | % of $44 | Postmark | % of $44   |
| ------------------------ | --------- | ------ | -------- | -------- | ---------- |
| 500 contacts, weekly     | 2,000     | $0.20  | 0.5%     | $3.60    | 8%         |
| 2,000 contacts, weekly   | 8,000     | $0.80  | 2%       | $14.40   | 33%        |
| 10,000 contacts, 2×/week | 80,000    | $8.00  | 18%      | $144     | **327%**   |
| 30,000 contacts, 3×/week | 360,000   | $36.00 | 82%      | $648     | **1,473%** |

The average creator costs almost nothing. **One heavy sender on Postmark wipes
out the margin of three to fifteen others**, and unlimited sending on a flat
price means unbounded cost per account against bounded revenue. That asymmetry
is the whole problem — not the price of email.

It is also why every competitor meters this: Kajabi cut Basic's contacts from
10,000 to 2,500 _while_ raising the price, and Circle charges $99/month for its
Email Hub, more than its own entry plan. The $500–900 bill is the same lesson
arriving empirically.

### Recommendation, three parts

**1. Cap sends per tier. Do not remove the module.** §4's funnel depends on EDM
("they invite their people → learner enrols"), and mail at the base tier is a
verified edge — Skool sends no campaigns at all, Circle charges extra. Removing
it surrenders that to save a cost a cap already controls.

| Tier   | Monthly send allowance    | Worst-case cost on SES  |
| ------ | ------------------------- | ----------------------- |
| Free   | 300 (the existing 10/day) | $0.03                   |
| Start  | 5,000                     | $0.50 — 1.1% of revenue |
| Pro    | 25,000 + their own domain | $2.50 — 2.5% of revenue |
| School | Negotiated                | —                       |

A normal creator — 500 contacts, weekly — sends 2,000/month and never sees the
cap. It binds only on the accounts that actually cost money, which is what a
meter is for. This is also the "meter contacts/email volume" conclusion already
recorded under pricing, now with a number attached.

**2. Split the providers along the split already decided.** §9 picked Postmark
for deliverability, which is right for transactional and wrong for broadcast:

- **Postmark → transactional**, on the primary domain. Magic links, receipts,
  access. Low volume, high stakes, and $15/month covers 10,000 of them.
- **SES → broadcast**, on the marketing subdomain. High volume, cost-dominated,
  and a slightly lower inbox rate on a campaign is survivable in a way a
  missing sign-in link is not.

This is the same boundary the domain separation already needed for reputation
containment, so it is one decision doing two jobs: a campaign cannot damage
sign-in deliverability, _and_ it cannot damage the margin. Note the cap alone
does not fix this — even at Pro's 25,000, Postmark would be 45% of revenue.

At 1,000 Start creators averaging 2,000 broadcast emails each: **SES $225/month
(0.5% of $44k revenue) against Postmark's $3,600 (8.2%)** — about $3,400/month
saved, and the per-account worst case bounded rather than open-ended.

The invoice is also a useful calibration for the caps below. ParkCollect's client
base averages somewhere between 4,000 and 15,000 messages per client per month
depending on how many clients share that 768k. A Start allowance of 5,000 sits
inside that range rather than below it, which suggests it is neither absurdly
tight nor generous enough to be meaningless — though course creators email
smaller lists than parking operators do, so treat it as an upper bound on what
Qori should expect.

**3. Budget the SES engineering honestly.** It is not free, it is one-off:

- Sandbox removal — a request, roughly a day of waiting
- Bounce and complaint handling: SNS topic → suppression list. `CampaignRecipient`
  already exists and is the natural home for it
- Dedicated IP and warm-up once volume justifies it ($24.95/month)
- No sending UI — but Qori is building its own campaign surface anyway, so the
  main thing Postmark sells above SES is something this project is not buying

Call it a week, amortised across every creator forever.

## Build spec — SES broadcast path (not built)

Four phases, each shippable on its own. Phase 1 is correct even before SES is
live and should land first, because it draws the boundary while there are only
two notification classes to move rather than fifteen.

### What is already true

- **`aws/aws-sdk-php` is installed** — it arrived with `league/flysystem-aws-s3-v3`
  during the R2 work, so the SES transport needs no new dependency. `Aws\Ses`
  and `Aws\SesV2` are both present.
- **`config/mail.php` already defines `ses` and `postmark` mailers**, and
  `config/services.php` already carries both key blocks. Nothing to scaffold.
- **SES credentials are not R2 credentials.** `services.ses` reads
  `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`; R2 deliberately uses its own
  `R2_ACCESS_KEY_ID` pair because it is Cloudflare. Keep them separate — one IAM
  user for SES with `ses:SendRawEmail` only.
- **`Aws\Sns\MessageValidator` is _not_ in the SDK any more** — the vendored tree
  has `SnsClient` and nothing else. Signature verification needs
  `composer require aws/aws-php-sns-message-validator`.

### Phase 1 — split the mailers (small)

```php
// config/qori.php
'mail' => [
    // Postmark for anything a person is waiting for: a magic link that does not
    // arrive is a login that cannot happen. Low volume, so its price never
    // compounds — which is the half of §9's reasoning that survives.
    'transactional' => env('QORI_MAIL_TRANSACTIONAL', 'log'),

    // SES for campaigns. Volume dominates here and a marginally lower inbox rate
    // on a newsletter is survivable, so this is bought on price: $0.10/1,000
    // against Postmark's $1.20–1.80.
    'broadcast' => env('QORI_MAIL_BROADCAST', 'log'),

    // A separate sending domain, not just a separate provider. Streams isolate
    // IPs; they do not isolate the DKIM d=. One creator's bad list must not be
    // able to reach the reputation that sign-in depends on.
    'broadcast_from' => env('QORI_MAIL_BROADCAST_FROM', 'hello@mail.qori.example'),
],
```

- `CampaignNotification` sets both: `->mailer(config('qori.mail.broadcast'))` and
  `->from(config('qori.mail.broadcast_from'), $workspace->name)`.
- Every other notification keeps the default mailer and `MAIL_FROM_ADDRESS`.
- **Test the boundary, not the transport**: assert `CampaignNotification` resolves
  the broadcast mailer and `CourseAccessNotification` does not. That test is what
  stops a future notification landing on the wrong side by reflex.
- Locally both stay `log`/MailHog, so nothing about dev changes.

### Phase 2 — suppression and the SNS webhook (the real work)

**`App\Models\EmailSuppression` — global, deliberately not workspace-scoped.**
A hard bounce is a fact about the address, not about a tenant. Scoping it per
workspace would let workspace B keep mailing an address that already bounced for
workspace A, and since the sending reputation is shared, A's problem becomes
everyone's. Same class of global model as `SubscriptionPrice`.

| Field                            | Notes                             |
| -------------------------------- | --------------------------------- |
| `email`                          | Unique index                      |
| `scope`                          | `all` or `marketing` — see below  |
| `reason`                         | `bounce` / `complaint` / `manual` |
| `source`                         | `ses` / `manual`                  |
| `suppressed_at`, `last_event_at` |                                   |

**The scope distinction is the part worth getting right:**

| SES event               | Action                                                                                                                                                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bounce, **Permanent**   | Suppress `all`. The address does not exist; sending transactional mail to it is pointless and damages reputation                                                                                                  |
| Complaint (spam button) | Suppress `marketing` **only**, and set `unsubscribed_at` on the Contact. They still bought a course and must keep receiving access mail — suppressing everything would lock a paying student out of what they own |
| Bounce, **Transient**   | Do not suppress. Record it. Repeated transients over a window can escalate to `all` later, but a full mailbox is not a dead address                                                                               |
| Delivery                | Optional, for campaign stats                                                                                                                                                                                      |

**`SnsWebhookController`**, shaped like `StripeWebhookController`:

- Signature verification is **not optional** — without it anyone can POST a
  bounce for any address and silently suppress a competitor's mail. Same
  reasoning as the Stripe webhook, same place in `routes/web.php` outside CSRF.
- Handle `SubscriptionConfirmation` as well as `Notification`: SNS sends the
  confirmation type first and expects a GET to its `SubscribeURL`. Miss it and
  the subscription never activates, with no error anywhere.
- **Idempotent** — SNS retries, and a replayed bounce must not double-write.
  `CheckoutService` already establishes the pattern.

**Send-time skip** in `CampaignService`: one `whereIn` over the batch's addresses,
never a query per recipient — a 5,000-recipient campaign would otherwise be 5,000
round trips. Skipped rows record why, which the existing
`CampaignRecipient::STATUS_SKIPPED` already supports.

**Two new recipient statuses**, so a campaign view can tell the truth about what
happened after the send: `bounced` and `complained` alongside the current
pending / sent / failed / skipped.

### Phase 3 — the monthly send allowance

- Count `CampaignRecipient` rows with `status = sent` for the workspace in the
  current calendar month. The daily-cap machinery already does this shape.
- Free 300 · Start 5,000 · Pro 25,000 · School negotiated.
- **Hard stop, no overage billing** (decided). §23 applies to the copy: the
  resolution is a real upgrade path, and if there is genuinely none — School —
  then omit the resolution rather than invent one.
- Do not roll unused allowance forward; rolling makes any single month unbounded
  again, which is the exact failure the cap exists to prevent.
- Surface the running total in the studio _before_ it binds. Discovering the cap
  by having a launch refused is the Kajabi experience this product exists to
  avoid.

### Phase 4 — Pro sends from its own domain

- SES `CreateEmailIdentity` for the creator's domain, return the three DKIM
  CNAMEs for them to publish, then poll `GetEmailIdentity` until verified.
- Store the identity and its status against the workspace.
- **Until verified, fall back to the shared marketing subdomain** — a
  half-configured domain must degrade to working mail, never to no mail.
- This is the same connect-and-verify shape as the Dropbox/Vimeo OAuth flows that
  §8 still needs, so build it after those and reuse the pattern.

### Operational prerequisites — not code, but nothing works without them

1. **SES sandbox removal.** Until granted: 200 messages/day, and only to verified
   addresses. Request early; it is not instant.
2. **Verify the `mail.` subdomain** as an SES identity, with DKIM.
3. **SPF and DMARC** on the sending subdomain, separate from the primary domain's
   records — the separation is the point.
4. **A configuration set** with an SNS event destination for bounces and
   complaints, or the webhook receives nothing.
5. **Dedicated IP ($24.95/mo) and warm-up** only once volume justifies it. On
   shared IPs at low volume SES's own reputation carries you; a cold dedicated IP
   is worse than shared until warmed.

### Testing

- `Notification::fake()` for the mailer-boundary assertions; no transport is
  exercised, which is correct — the boundary is the logic.
- SNS webhook: fixture payloads per event type, with the validator injected so a
  test can supply one that accepts. Assert the _effects_ — a permanent bounce
  writes `all`, a complaint writes `marketing` and sets `unsubscribed_at`, a
  transient writes nothing, a replay changes nothing.
- One test that a suppressed address is skipped rather than sent, since that is
  the whole point of the phase.
- Never a real AWS call — `Http::fake()` is the house rule for vendors.

### Order, and why

Phase 1 first because it is cheap and correct now. Phase 2 before any real
sending volume: sending without bounce handling is how an SES account gets its
reputation destroyed and its production access revoked. Phase 3 before opening
EDM to Start. Phase 4 last — it is a Pro feature and needs the connector pattern
that §8 has not built yet.

### Open

- Sell overage blocks above the cap, or hard-stop at it? A hard stop is simpler
  and matches §23's preference for a final answer over a hopeful one, but it
  frustrates a creator mid-launch. **Recommend a hard stop with a clear upgrade
  path**, since overage billing on a platform that promises never to surprise
  people is a bad look.
- Does the Start allowance reset monthly or roll? Monthly, and do not roll —
  rolling makes the cost unbounded again in any single month.
- Resend is a reasonable middle for the transactional half if Postmark's price
  grates ($0.40/1,000 against $1.50), but it does not change the broadcast
  answer and its marketing product bills by contacts, which is the wrong shape.

## Postmark's alternative: Cloudflare Email Service — 22 September 2026

Transactional mail stays on Postmark, and **Cloudflare Email Service is the one
alternative recorded for it** (`D-054`). SES stays the broadcast provider, and
since `D-054` it carries the "you're in" email too (`T-186`).

|                                                 | Postmark Platform          | Cloudflare Email Service                 |
| ----------------------------------------------- | -------------------------- | ---------------------------------------- |
| Base                                            | $18/month, 10,000 included | $5/month on Workers Paid, 3,000 included |
| Per 1,000 after                                 | $1.20                      | $0.35                                    |
| At 747,000 a month (10,000 free creators today) | $902                       | $265                                     |

Why not yet, as its documentation read on 22 September 2026: Email Sending is
in beta and for transactional mail only; new accounts start on an unpublished
daily quota that grows with their sending; and nothing describes bounce or
complaint events, which `T-017` and `T-032` need. It takes a REST API or
authenticated SMTP, so Laravel's `smtp` mailer reaches it, and `useqori.com`'s
DNS is already on Cloudflare. Revisit when it has left beta and reports
bounces.

Sources: [pricing](https://developers.cloudflare.com/email-service/platform/pricing/),
[overview](https://developers.cloudflare.com/email-service/),
[limits](https://developers.cloudflare.com/email-service/platform/limits/),
[Postmark pricing](https://postmarkapp.com/pricing).
