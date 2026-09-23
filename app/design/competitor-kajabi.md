# Kajabi, read for what Qori can take

Written 23 September 2026 at the owner's word, as the follow-up to
[`positioning-solo-creators.md`](positioning-solo-creators.md). Kajabi's prices
are already in the
[competitor review](../dev/pricing-and-competitor-review-2026-09-11.md), which
put it in the "broader creator-business platform" row and said its buyers want
a different thing from Qori's. This note is the rest of the question: is it a
competitor, and which of its flows and design choices would help Qori. Read
from its public site and help centre and three reviews; nobody signed in.

## Is it a competitor

**In the category, yes. For the same person today, no — for the same person
later, yes.** Kajabi is the tool the grown creator moves to. Justin Welsh is
its headline customer ("US$10M+ earned on Kajabi") on every page read, which
puts it at move 5 onward of the path in the positioning note, and Qori at
moves 1–4.

What decides it is the entry price and who Kajabi says it is for:

- Basic is US$179 a month, US$143 billed annually, after a 14-day trial: 5
  products, 2,500 contacts, 1 website, 1 community, 2 admins. Growth US$249
  (50 products, 25,000 contacts), Pro US$499 (unlimited, 3 websites, a branded
  app). A January 2026 restructure raised Basic by US$30, cut its contacts from
  10,000 to 2,500 and hid the US$89 Kickstarter plan. Contacts come in blocks
  of 25,000 for US$125 a month.
- Its pricing FAQ says which plan to start on: if you have not sold anything
  yet, Basic. So Kajabi does ask the pre-revenue person for US$143 a month,
  and that person is Qori's. Qori's answer is the Free plan: one Series, fifty
  Peers, ten invitations a day, payments allowed, no card.
- No revenue share; Kajabi Payments processes at 2.9% + 30¢ on Basic, and a
  third-party processor costs 2% / 1% / 0.5% extra by plan. Qori's is Stripe's
  fee alone, on a direct charge.
- Its pitch is replacement: one system for products, payments, email, funnels,
  website, community, podcast, newsletter, AI ("Cofounder", "Expert Agents", an
  MCP server), a branded app. The Payments page has a "replaces ThriveCart,
  SamCart, Gumroad" table. Qori's pitch is the opposite — keep Drive, Vimeo,
  Stripe and the chat app, add the room — and `PLAN.md` keeps it there.

So: name Kajabi in a comparison as the platform for when the Series count
outgrows Free and the person wants the marketing stack, and never as the
thing Qori beats feature for feature. The line for it, if one is needed, is
"Kajabi replaces your tools; Qori keeps them."

## Its object model, beside Qori's

| Kajabi                                                | Qori                                                                | Note                                                                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Product (course, coaching, community, download…)      | Series                                                              | Kajabi has eight product types; Qori has one object with five Episode kinds                               |
| Module → lesson                                       | Episode, with materials                                             | Kajabi nests modules and submodules; Qori is flat, on purpose                                              |
| Offer: a product plus a price, one product many offers | The Series price, and a price on each invitation (`D-050`)         | The separation is the same idea; Kajabi names it, Qori does not yet                                        |
| Grant an offer (no checkout, immediate access, welcome email) | Give someone access                                          | Same split as Qori's give-access vs the public page's free access with a code and consent                  |
| Free offer through checkout                           | Free access from the Series page                                    | Kajabi still runs checkout for a free offer, to get the contact and the consent; Qori's code step does that |
| Checkout page, embeddable                             | Stripe Checkout                                                     | Kajabi's has order bumps, pay-what-you-want, BNPL; Qori has Stripe's wallets and Adaptive Pricing          |
| Post-purchase: Library page or a thank-you page, email with a Login button | The Series opens; the "you're in" email        | Kajabi lets new customers skip account creation; Qori's Peer never has a password at all                   |
| Library (all owned products, product cards, upsell cards for the rest) | My shared                                            | Qori shows no upsell, by design: nothing is listed                                                         |
| Drip: modules on a date or N days after purchase      | Live Episodes scheduled; materials "after the session"              | No drip for recorded Series in Qori                                                                        |
| Product progress report; automations on finish and on going quiet | The dashboard's next action: who went quiet             | Kajabi emails the student; Qori tells the creator                                                          |
| Coaching: sessions, agendas, booking, native video, private notes per client, recordings | The classroom stream's session card       | Qori pastes a Zoom link and a recording link; no booking, no notes                                         |
| Backstage: a private portal per client, lessons curated from existing content, sessions recorded and summarised | An invitation at its own price | A Series for one Peer is already possible on Qori at no build; Kajabi charges US$49 a seat for the idea  |
| Certificates on completion                            | Certificates, switched off (`QORI_CERTIFICATES`)                    | —                                                                                                          |
| Paywall: a free preview of some content               | The public page lists the contents                                  | No open Episode in Qori                                                                                    |
| Customer settings: receipts, email preferences, billing, password | Profile; receipts are Stripe's                            | Qori sends no receipt; the creator's Stripe account can                                                    |
| Dashboard alerts: failed payout, info required, disputes, failed payments | Blocking states: payments not ready, payment failing | Same rule — blocking outranks encouragement — with disputes still to come (`T-103`)                        |

## What to take

Each is a proposal. None is a task until the owner says so; the stream each
belongs to is named.

1. **A shape for the first Series** (`onboarding`, `T-026`). Kajabi's product
   blueprints — mini course, online course, evergreen — pre-fill categories and
   posts so the creator edits rather than starts blank, and the one thing an
   onboarding reviewer praised was having something others could visit within
   thirty minutes. Qori's guided first Series could offer three shapes: a
   course of files, a class taught live week by week, one thing. Each creates
   draft Episodes with placeholder titles ("Week 1"), from the Episode kinds
   that exist. The dashboard keeps one next action; the shape decides what it
   points at.
2. **Say who each plan is for, in one plain sentence** (no code). Kajabi's
   pricing FAQ answers "which plan should I start on" in the register Qori
   wants: not sold anything yet, Basic; revenue coming in and a list past a few
   thousand, Growth. Qori's price rows carry a features list entered at
   `/admin/pricing`, so the first line of each can be that sentence — "Free:
   until you have sold something" — with no build. `T-104` puts the stance
   sentence above the cards.
3. **Name the offer, without the word.** Kajabi's one product, many offers is
   exactly `D-050`'s price per invitation, and Qori's forms do not say so.
   `T-191`'s price help can say the Series price is what the link charges and
   each invitation can carry its own. Vouchers (`selling`) complete the set.
4. **A private note per Peer** (`classroom`). Kajabi's coaching keeps the
   coach's private progress notes on each client, beside the client's own. The
   `peers` table is Qori's CRM already; one nullable text column and a field on
   the Peer row would give a tutor the thing they now keep in a spreadsheet.
   Small, and it earns the coach angle the positioning note asks about.
5. **An open Episode** (`selling`). Kajabi's paywall shows a sneak peek behind
   a purchase. For Qori the public Series page already lists the contents; one
   Episode marked open to anyone with the link is the smallest preview, and
   it is the beginner's "free sample" without a newsletter.
6. **The home page shows the object** (`design`). Kajabi's hero is a device
   frame of the product beside a face. Qori's home page is words and two
   buttons; the brand kit's hero banner already draws a Series in course
   geometry, and the brand guide says objects before metrics. One Series card
   in the hero, not a screenshot.
7. **Nudge the quiet ones, later** (`selling`, after `T-045` makes campaigns
   reachable). Kajabi automates the email to a student who goes quiet. Qori's
   honest version today tells the creator; the smallest next step is one
   button on that next action that sends one consent-gated email, once.

## What not to take

- **The all-in-one.** Funnels, landing pages, email marketing, website
  builder, podcasts, communities, memberships, affiliates, AI cofounder, MCP.
  `PLAN.md`'s north star names each of these as what Qori is not, and the
  reviews' first complaint is that the consolidation overwhelms rather than
  simplifies, and that where to edit a course versus an offer is not intuitive.
- **Hosted media.** Kajabi stores the video and keeps it view-only; Qori keeps
  video external (`D-016`, §8), which is the whole cost story.
- **Four apps.** The reviews count up to four apps between creator and
  student; Qori is one URL, and stays web-first until beta.
- **Earnings badges and platform totals** ("US$12B earned by experts",
  "6-figure earner"). The project plan's voice rule — no marketplace, bargain
  or hustle copy — rules them out, and Qori cannot verify them anyway.
- **Per-website pricing and contact blocks.** Qori meters sends, not contacts
  or sites (`decisions.md`, the email cost meter), and Peers are never seats.
- **A trial with a card.** Free is free; the pre-revenue person is the one
  Kajabi charges and Qori does not.

## Design, in one paragraph

Black on white, big geometric type, product screenshots in device frames,
founders' faces, a chat widget offering a demo. Clean, and generic SaaS — the
thing the brand guide says Qori must not look like ("an untouched software
starter kit"). The one composition worth remembering is the hero's checklist
card, "The Expert Operating System": preflight, lead magnet, email sequence,
going public, more reach — a programme shown as UI. Qori's equivalent is the
dashboard's single next action, which is the better rule; what Kajabi's card
shows is that the *sequence* can be visible without becoming a backlog.

## Sources

Read 23 September 2026: [kajabi.com](https://www.kajabi.com/),
[pricing](https://www.kajabi.com/pricing),
[online courses](https://www.kajabi.com/product/online-courses),
[coaching](https://www.kajabi.com/product/coaching),
[Backstage](https://www.kajabi.com/product/backstage),
[payments](https://www.kajabi.com/features/payments),
[learn](https://kajabi.com/learn); help centre:
[products overview](https://help.kajabi.com/articles/products/products-overview/kajabi-products-overview),
[create an offer](https://help.kajabi.com/en/articles/12695509-create-an-offer),
[what happens when a customer purchases](https://help.kajabi.com/en/articles/12695540-what-happens-when-a-customer-purchases-my-offer),
[grant an offer](https://help.kajabi.com/en/articles/12695547-how-to-grant-an-offer),
[what customers see](https://help.kajabi.com/hc/en-us/articles/4406001183259-What-do-my-Customers-see),
[the dashboard](https://help.kajabi.com/articles/account-settings/my-kajabi/dashboard-explained);
reviews, secondary and one of them a competitor's:
[Learning Revolution](https://www.learningrevolution.net/kajabi-review/),
[Ruzuku](https://www.ruzuku.com/learn/articles/is-kajabi-any-good),
[ScreenSteps on its onboarding](https://blog.screensteps.com/onboarding-review-kajabi).
The blueprint names come from search summaries of Kajabi's help centre; the
article itself answered 403.
