# Release prerequisites requiring the owner

> External account, domain, payment, email, video and queue inputs that code alone cannot complete.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## External setup checklist

- ~~**Register `useqori.com` at Cloudflare Registrar**~~ — **done.** Registered, on Cloudflare nameservers, serving the application over HTTPS as of 11 September 2026. The advice below stands for the renewal and for the account itself (decided 2026-09-07). At cost, no markup ever (~$10.44 = $10.26 registry + $0.18 ICANN), free WHOIS privacy on by default, billed in **USD**. It does direct registration now — that was transfer-only for years, so older advice saying otherwise is stale.
    - **Register 2–3 years, before 1 November 2026.** Verisign raises the `.com` wholesale fee 7% that day ($10.26 → $10.97), so multi-year now locks the lower rate. The bigger reason is that a lapsed domain takes sign-in email with it, and multi-year plus auto-renew removes the commonest way that happens.
    - **The registrar account email must not be `@useqori.com`.** If the domain lapses, recovery mail sent to that domain is unreachable — the usual way people get properly locked out.
    - **2FA on the Cloudflare account**, recovery codes kept with the Stripe ones. That account will hold the domain, DNS, the R2 bucket and the Worker, which makes it the most valuable credential in the project.
    - Cloudflare Registrar **requires Cloudflare nameservers**. Fine here — R2 and the Worker are going there anyway — and transferring out later is always available after the 60-day post-registration lock. Note SES needs only DKIM CNAMEs and SPF/DMARC TXT records, which Cloudflare DNS serves happily, so broadcast mail never forces a move to Route 53.
- **Stripe — one mandatory dashboard setting**: under _Settings → Billing → Subscriptions and emails → Manage failed payments_, the action after retries are exhausted must be **cancel** or **mark unpaid**, never "leave as-is". `past_due` now holds a workspace's plan as a grace period, and "leave as-is" would hold it forever with no event to end it. See the grace-period note in the downgrade section.
- **Stripe**: **done in test mode** (2026-09-07) — sandbox account, `STRIPE_SECRET`/`STRIPE_WEBHOOK_SECRET` in `.env`, products and prices created, `SubscriptionPrice` rows carrying the real `price_…` ids, and the whole upgrade/downgrade cycle driven in a browser. What is still outstanding is **live mode**: the same setup again on the live account, the keys in the Laravel Cloud dashboard, and a real webhook endpoint at `/webhooks/stripe` subscribed to `checkout.session.completed` **and** `customer.subscription.*`. Plan price ids are not env vars — create the prices in Stripe, then enter each `price_…` at `/admin/pricing` as a staff owner.
    - Locally the webhook is driven by `stripe listen --forward-to localhost:8001/webhooks/stripe`, whose printed signing secret must match `STRIPE_WEBHOOK_SECRET` or every event 400s on signature verification.
    - **Opening the live account, in this order** (`D-046` to `D-048`, 22 September 2026). Stripe reviews the website before it activates an account, so the pages come before the account:
        1. **An ABN.** Free at abr.gov.au and minutes for a sole trader. Stripe does not require one for an individual, but Wise Business will ask for it, a tax invoice to an Australian business carries it, and registering for GST needs it.
        2. **Wise Business**, with its Australian account details (BSB and account number) in the same legal name as the Stripe account. Stripe pays AUD into them. Stripe's USD payouts refuse Wise ("Wise, Airwallex, Virtual, or Neobank account[s]"), so the AUD details are the ones to give it.
        3. **The website live** with pricing, terms, a refund and cancellation policy, a privacy policy and contact details (`T-155`), before asking Stripe to activate.
        4. **The live account as a sole trader**, payouts to the Wise details, the card statement name set to `QORI`, and API version `2026-08-26.dahlia` on the account and on the webhook endpoint, matching `config/services.php` — a new account defaults to whatever version is current the day it is made.
        5. **Settings → Adaptive Pricing on** (it converts from AUD for every currency without a fixed price, `D-048`), and **Stripe Tax threshold monitoring on**. Monitoring warns when sales in a country near its registration threshold. Calculating tax stays off (`T-168`) until Qori registers somewhere, and before it goes on, each currency option on each price needs a tax behaviour, or Stripe shows that buyer the AUD price instead.
        6. **The live prices, published from Qori** (`D-048`). In `/admin/pricing`, set Start at US$39 and Pro at US$99. Qori calculates each fixed currency from the day's rates, rounds it up to a whole unit, and creates the Stripe price itself (`T-169`, `T-172`). At 21 September that made A$55/139, €34/87, £30/74, C$55/139, NZ$69/173 and S$50/127. **Do not create prices or coupons in Stripe's dashboard**: Qori owns them, and vouchers are made in Qori's admin too (`T-173`). Plan coupons are percent-off.
        7. **Optional, once USD sales are steady: ask Stripe for USD payouts.** Every sale not in AUD pays Stripe's 2% conversion (`D-047`). With USD payouts, USD sales pay 1% per payout instead (US$10 minimum). They go to an Australian bank's USD account — NAB, not Wise — and USD suppliers can be paid from it. Stripe offers this to a limited number of Australian businesses, and a USD account can be added only after the account is activated.
        8. **Ask the accountant** whether to register for GST below A$75k — overseas suppliers add 10% GST to Qori's bills until it is registered — and, if so, whether the fixed prices include GST.
    - The **Customer Portal needed no configuration** in test mode — it rendered subscription, card, invoice history and a working cancel out of the box.
- ~~**Stripe Connect needs a decision**~~ — **decided 2026-09-07, and changed 17 September 2026 (`D-023`): Connect OAuth is the only way in.** Qori no longer creates connected accounts on Accounts v2, mints account links or asks a country (`T-113`); the creator signs in to the Stripe account they have, or opens one on Stripe's own page, and comes back with it. Accounts created on v2 before that stay connected and are read through v1 like every other. **What needs you, because no creator can get paid without it:** in the sandbox first and the live account later, enable OAuth under Connect → Onboarding options → OAuth; add `http://localhost:8001/u/payments/stripe/finalise` to the redirect URIs (the production URL when live); and put the `ca_…` client id in `.env` as `STRIPE_CLIENT_ID`, and in Laravel Cloud for live. Until then the Integrations page and setup part two say payments cannot be connected, the connect route refuses, and disconnecting only forgets rather than deauthorising at Stripe. The code and its tests are done; one real OAuth round trip against the sandbox is the check still owed, including a decline, and whether deauthorising works on an account Qori created on v2 rather than one connected through OAuth.
- **Vimeo and YouTube**: a creator on Vimeo Free can only make a video Public, and Qori offers that tier with the limit stated rather than refusing it (`D-018`); proving the unlisted link needs one month of Vimeo Starter on Qori's side. The earlier domain-lock reasoning no longer applies, since Episodes open on vimeo.com rather than in a locked embed. Both vendors hold Episodes in paid Series as well as free ones (`D-019`): a paid Series sells the creator's time and knowledge, and the video is course material that may be Public. Nothing here waits on a written permission from either vendor; what their terms say, and how to write to them if that is ever wanted, is in [`vendor-accounts.md`](vendor-accounts.md#two-terms-that-bind-qori-not-the-creator).
- **Before any BYO provider goes live** (`D-016`; all seven are in beta under `D-018`): ~~publish the Google Cloud OAuth app, since refresh tokens issued while it is in Testing expire after seven days~~ — **done 20 September 2026**, project `910317206529` reads In production, and what Google still needs is `T-155`, because the Branding page points at `useqori.com/privacy` and `/terms` and both 404; complete Microsoft Partner Center enrolment and publisher verification, which work and school OneDrive creators cannot connect without; apply for Dropbox production approval before the app links 50 accounts; and submit the Zoom Marketplace review a month or two before the beta date, since Zoom publishes no total turnaround. Step by step, with every price and console address: [`vendor-accounts.md`](vendor-accounts.md).
- **R2 buckets** (the owner, 22 September 2026): `useqori-app-bucket` is production's, and Laravel Cloud's `R2_BUCKET` must name it. Local development uses **`useqori-app-bucket-test`**, made that day with the same account key, its CORS allowing only `http://localhost:8001`; the two objects the production bucket held then, both from local development, were copied into it. The owner's local `.env` names it from that day, and the code repository's `.env.example` says which is which. Nothing local should write to the production bucket again.
- **The terms a Peer agrees to** (`D-049`, `T-178`): every Series page shows an agreement between the creator and their Peers that Qori supplies until creators can write their own (`T-179`), in `lang/en/terms.php`. It is a draft written by the product, not a lawyer, and it needs a legal read before release, beside `T-155`'s terms and privacy policy.
- **Postmark**: **done 11 September 2026** (`T-015`). `qori_production` server, `useqori.com` verified, `MAIL_MAILER=postmark` and the key in Laravel Cloud, return path `pm-bounces → pm.mtasv.net` unproxied, DMARC at `p=none`. Two things this does not establish: that mail arrives (`T-032`), and that the `rua` address `dmarc@useqori.com` routes anywhere — Cloudflare Email Routing needs a rule per address, and without one the aggregate reports bounce and the record is decoration.
- **SES, when broadcast goes live**: production access (sandbox is 200/day to verified addresses only), a verified `mail.` subdomain with DKIM, SPF and DMARC on it, and a configuration set with an SNS topic pointed at `POST /webhooks/ses`. Without the last one the webhook is built and receives nothing.
- **A queue worker**, eventually: campaign sending is inline while the queue is `deferred`, so a large list blocks the request.
- ~~**Turn the scheduler on in Laravel Cloud.**~~ **Done 11 September 2026.** `T-010` added Qori's first scheduled command (`qori:series:purge`, daily) on 11 September 2026, and until something runs `schedule:run` a Series a creator asked to delete stays marked and is never deleted. There is no cron to write: open the environment's **App compute cluster** in the infrastructure canvas, enable the **Scheduler** toggle, save, and **re-deploy** — the toggle alone does nothing until the next deployment. After that `schedule:run` is invoked every minute. Three things about it that are worth knowing before they bite:
    - **The wake-up schedule is captured at deploy time.** With scale to zero, Cloud runs `php artisan schedule:list` on each deployment and stores the result to decide when to wake the environment. A change to a task's frequency therefore does nothing until the next deploy, even though the code is right.
    - **More than one replica means the task runs on all of them** unless it uses Laravel's `onOneServer()`. `qori:series:purge` does not, so this needs answering before the App cluster is scaled past one replica — see the `operations` stream.
    - **Never schedule anything more often than the sleep timeout.** A task every five minutes on a five-minute timeout means an environment that never sleeps. Daily is nowhere near that line.

## Domain: useqori.com (decided 2026-09-07, **registered 2026-09-11**)

`qori.com`, `qori.app`, `getqori.com`, `getqori.app`, `qori.co` and `qori.net`
are all taken. `useqori.com` is available and is the pick.

**The `.com` is the reason, and it is about email rather than vanity.** Qori's
sign-in _is_ email, and `.com`/`.net`/`.org` are the top tier for inbox
placement — every alternative that kept the name unprefixed asked for a
reputation downgrade to do it. `use-` also reads as a deliberate convention
(usefathom, usebasin) where `the-` reads like a lost bidding war.

Ruled out, and why, so this is not re-litigated:

|                       |                                                                                                                                  |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `.mobi`               | Launched 2006 for _mobile-optimised sites_, a category responsive design ended. Signals 2008, and for an app product it misleads |
| `.online`             | Cheap new gTLD, high churn, the low-friction category deliverability filters treat with suspicion                                |
| `.info`               | Not dangerous, but twenty years of cheap has left a content-farm association and nothing offsets it                              |
| `.cc`, `.work`, `.in` | Outside the trusted tier with no upside; `.in` adds a confusing regional signal                                                  |
| `.au`, `.com.au`      | Excellent deliverability and `.au` needs no ABN — ruled out on the human's preference for a non-regional name                    |

**The accepted cost:** brand and domain diverge, so a student told "it's on Qori"
may type `qori.com` and land elsewhere. Smaller than it feels — nearly every
path in is a _link_ rather than a typed domain (the access email, a shared course
URL, an App Store tap), and the one place typing happens is a creator saying the
name aloud, which is a copy problem rather than a domain one. No near-miss
redirect was available to soften it; buying `qori.com` later purely to redirect
stays open if it turns out to be parked rather than in use.

**Consequences already applied:**

- Transactional mail sends from `useqori.com`; broadcast from
  `mail.useqori.com`. **Do not change these once sending starts** — the DKIM
  reputation is the expensive asset, not the registration.
- §2's trademark check is unaffected: it is on the word _Qori_, not the domain,
  so IP Australia and USPTO class 9/42 are unchanged.
- §2's open item "confirm `.com` / `.app`" is now answered: both taken, brand
  kept anyway.
