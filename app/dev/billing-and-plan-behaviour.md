# Billing and plan behaviour

> Downgrade, cap, paid-fulfilment, allowance, refund and deletion behaviour.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## Downgrade: what a plan cap means once you are over it

Downgrade already happens and is automatic — `BillingService::applySubscription()`
sets `plan = 'free'` for any Stripe status that is not `active` or `trialing`, on
the webhook. So a Pro workspace with 20 courses, 5,000 contacts and 3 admins
becomes a free workspace with caps of 1, 50 and 1 the moment a card fails. The
question is what that should mean.

### The principle

**A plan cap gates what the creator initiates. It must never gate what a student
has already paid for.**

That single line resolves almost every case, and it is the one the code mostly
follows already — `guardCourseLimit` counts on _create_, so twenty existing
courses survive a downgrade and nothing gates reads. Students keep everything.

### Four kinds of limit, and they behave differently

| Kind                                   | Examples                                                                         | On downgrade                                                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Stock** — things already made        | courses, lessons, contacts, stored files                                         | **Keep all of it.** The cap gates creation only, and being over it is a valid permanent state |
| **Flow** — a recurring allowance       | EDM per day and per month                                                        | Simply becomes the new plan's number next period. Nothing to grandfather                      |
| **Capability** — features              | catalogue listing, custom templates, own sending domain, reminders, upsell block | **Off immediately.** These are the actual pressure to pay                                     |
| **Seats** — other people's live access | studio admins                                                                    | The hard case, below                                                                          |

**Nothing is ever deleted, and no student ever loses access.** §5 and §14 both
say it, and the reason is stronger than politeness: the student's contract is
with the _creator_, not with Qori. Revoking access for the creator's unpaid bill
would be Qori breaking a promise between two other parties, and the creator would
wear the blame.

### What actually creates pressure to pay

Not clawing back courses — **the Pro ladder does it by itself.** On dropping to
free a creator loses their catalogue row, their own sending domain, custom
templates, reminders and the upsell block, their EDM drops to 300/month, and they
cannot create a second course. Every one of those is felt by the creator and
none of them touches a student. That is a far better shape than capacity
clawback, and it is already the design — it just has to be allowed to work.

### Seats are the one thing that has to shrink

A seat is not stored content; it is a person who can log in and act. Keeping 20
admins on a one-seat plan means the cap never bites at all. Today
`hasSeatAvailable()` only blocks _adding_ a member, so that is exactly what
happens.

Proposed: **the owner always keeps their seat; the others are suspended, not
removed.** The `workspace_members` row stays, studio access stops, and upgrading
restores everyone instantly. Nothing is destroyed, and the capability genuinely
shrinks. Their user account and any courses they are enrolled in as a student are
untouched — those are a different relationship (§21.1).

### Still open

- **Does a downgrade get announced?** §5 specifies "3-month friction: a banner,
  freeze edits, or hibernate the studio" and none of it is built. The plan flips
  silently on a webhook today. At minimum the creator should be told what they
  lost, in the email and in the studio, before they discover it by trying.
- **Is 50 contacts right for free**, given free creators may take student
  payments (§5, §17.1)? At 50 they cannot sell to a 51st person. That is
  defensible as the pressure point, but it should be a decision rather than a
  side effect.

## A paid enrolment can be refused after the money is taken

Found while working through the above. **Live now, not only after a downgrade.**

```
Student pays on Stripe
  → webhook → CheckoutService::fulfil()
      → EnrolmentService::enrol() → contactFor()
          → guardContactLimit()  ← throws when the workspace is at its cap
```

`contactFor()` checks the contact cap when creating a contact for a **new**
buyer. Nothing catches it: there is no try/catch in `CheckoutService` or
`StripeWebhookController`, so the exception leaves the controller as a non-2xx,
Stripe retries for days, and every retry throws again.

**The student has paid and has no access, permanently.** It needs no downgrade to
happen: a free creator sitting at 50 contacts hits it on their 51st sale today.

It is also the precise failure this product's positioning is against — the
category's own complaint list is full of platforms taking money and withholding
what was bought.

**The fix is to move the check, not to remove it.** The contact cap belongs in
`CheckoutService::begin()`, beside `guardSellable()`, where being over it stops
the student reaching Stripe at all and nobody is charged. `fulfil()` then never
refuses: by the time it runs the money is taken, and a cap is a _sales_ limit,
not a fulfilment one. A race that puts the workspace one over between begin and
fulfil is the correct thing to allow.

The existing copy is already right for it — `errors.enrolment.contacts_full`
says the class is full and points at the teacher, never at billing, because the
person who hits it has no idea what plan their teacher is on.

## The send cap versus a course with 100 students

Asked: if EDM is capped, what happens to a scheduled send, or to a course whose
class is larger than the remaining allowance?

`guardMonthlyAllowance()` today refuses the **whole** send if it would cross the
line, which is right for a launch campaign and wrong for everything else. The
resolution is the same split already made for consent: **the four §9 types are
not alike, and one meter over all of them is the mistake.**

| Type                           | Has another channel?                                                              | Metered?               | On exhaustion                  |
| ------------------------------ | --------------------------------------------------------------------------------- | ---------------------- | ------------------------------ |
| Receipt, access, magic link    | No — it _is_ the delivery                                                         | **Never**              | Must always send. Contractual  |
| New lesson, stalled, reminders | **Yes** — the lesson is already in the course, the session is already on the page | Separately, generously | Stops sending. Nothing is lost |
| Launch campaign                | No — the email _is_ the message                                                   | Yes, hard stop         | Refused whole                  |

The asymmetry that decides it: a new-lesson email **notifies someone of something
already visible**; a launch campaign is the only form the message takes. Refusing
the first costs a convenience. Refusing the second costs the message.

So a course with 100 students never gets half-notified — service messages are not
drawn from the marketing allowance, and a creator cannot be prevented from
telling paying students that their course changed. That would be Qori degrading
something a student already bought to settle a bill with the creator, which is
the same line the downgrade policy draws.

**Never partial-send a launch.** Fifty of a hundred students hearing about a
launch is worse than none: the creator cannot tell who, and cannot safely resend.
All-or-nothing is correct there.

**Service messages still need a bound**, because on paid tiers contacts are
unlimited: 5,000 students × a weekly lesson is 20,000 messages a month. Give them
their own allowance, sized against enrolment rather than list size, since that is
the number that tracks a real business rather than one that can be inflated.

**A scheduled send checks at fire time, not at schedule time** — that is already
how `send()` works — and a scheduled send that is refused has to _tell someone_.
Silently not sending is the worst of the three outcomes, and it is the one a
scheduler makes easy.

## The extreme case: build everything on Pro, then downgrade

Asked directly: a creator takes Pro, sets up beautifully, downgrades the next
day. Do they keep the Pro benefits?

**As things stand today, yes — all of them.** `Workspace::allows()`, the method
that answers "does this plan permit that", **has no call sites at all.**
`public_listing` is defined in the plan config and checked nowhere. Nothing is
being exploited yet only because none of the Pro features are built.

Which makes this exactly the moment to write the rule, because it is free now
and expensive later:

> **Check the plan at the moment of use. Never stamp a capability into data.**

Every Pro feature has a tempting shortcut that breaks this:

| Feature                | The shortcut that leaks                     | What it must do instead                                                                         |
| ---------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Catalogue listing      | An `is_listed` flag set when they subscribe | Ask `allows('public_listing')` when building the catalogue                                      |
| Own sending domain     | A verified domain stored on the workspace   | Check the plan when choosing the from-address                                                   |
| Custom email templates | The template row exists, so it renders      | Check the plan at render, and fall back to Qori's                                               |
| Upsell block           | Part of the stored template                 | Same check, same fallback                                                                       |
| Reminders              | Scheduled rows that a worker fires          | Check the plan when the reminder fires                                                          |
| Private group          | The group exists, so it works               | Group stays **readable** — students inside it keep access — but no new groups, no customisation |

Note the last row is not the same as the others: the private group holds
students, so switching it off would take access away from people who did nothing
wrong. It degrades rather than disappears, consistent with the rule that a cap
never reaches a student.

**Stored artifacts are a different matter and stay.** Courses, lessons, uploaded
files and templates made while on Pro are _stock_ — the creator made them, and
§14 does not delete. Keeping a template file while refusing to render it is
correct and is also what makes an upgrade restore everything instantly.

So the honest answer to the extreme case, once the rule is followed: they keep
what they **made**, and lose what they **use**.

**That framing was too generous — see the correction below.** Keeping fifty
courses fully editable and sellable on a one-course plan is itself the exploit,
and protecting the student never required it.

## Correction: "keep what they made" was too generous, and it is the exploit

The earlier framing — _they keep what they made, and lose what they use_ — sounds
principled and is wrong. Spelled out as an arbitrage it reads:

> Pay $44 for one month of Start. Create fifty courses. Downgrade. Keep editing
> all fifty, keep selling them, and have Qori store them forever, for $44 once.

That is the exploit, and it exists because two different things got conflated:

- **A student must not lose access to what they bought.** Non-negotiable, and
  nothing below touches it.
- **A creator must keep full use of fifty courses on a one-course plan.** Does
  not follow, and was never implied by the first.

Protecting the student requires only that enrolled students keep _reading_. It
requires nothing at all about the creator's ability to _edit_, _publish_, or
_sell_. §5 already said as much and it was not applied — "3-month friction:
inconvenience for the creator (banner, **freeze edits**, or hibernate Studio).
Enrolled students keep access."

### Settled: everything locks, and obligations survive

Stricter than the "pick which N stay active" sketch above, and better. On
downgrading over the cap:

**Locked — the whole set, not a chosen subset.** All fifty courses go inert
together. No "keep your best one" negotiation, no default to argue with, and
nothing for a creator to game by shuffling which course is live.

| Removed                      | Kept                                  |
| ---------------------------- | ------------------------------------- |
| Enrol a student              | **See who is enrolled**               |
| Edit a course or its lessons | **See what each of them paid**        |
| Change or upload material    | **Refund**                            |
| Publish or unpublish         | **Re-send a past receipt on request** |
|                              | **Delete**                            |
|                              | Students keep reading, always         |

The principle underneath, worth stating once and applying everywhere:

> **A plan cap removes capabilities. It never removes the ability to honour an
> obligation already incurred.**

Selling is a capability. Refunding is an obligation. A student who paid can ask
for their money back or for a copy of their receipt a year later, and the fact
that their teacher stopped paying Qori has nothing to do with them. Locking a
creator out of answering them would make Qori the reason a student cannot be
made whole — which is the same line the whole downgrade policy is drawn on.

### Say the limit on the control, not in the refusal

The human's example is the whole rule: a **disabled Create button reading
`(50/1)`**. It states the situation before anyone tries, in less space than an
error message, and needs no explanation. Nobody has to click something to find
out they cannot.

Generalised: **anything with a cap shows `used/limit` on the control itself.**
Courses `(50/1)`, contacts, storage on a course, seats. The email allowance
already works this way on the studio dashboard, so this is a rule the codebase
has half-adopted and should finish.

The counter is also the most honest upgrade prompt available. `(50/1)` beside an
Upgrade button is not a nag — it is a fact, and the reader can check it. That is
the right shape for a product whose competitive case rests on not doing what
Kajabi and Teachable do.

**Wording points at the creator and leads with the recoverable action.**
"Upgrade to unlock these" before "delete the ones you don't need" — delete is the
escape hatch, not the instruction, and a platform whose first suggestion is
_destroy your work_ has picked the wrong primary action. §23 already requires
every failure to carry a resolution; here there are two, and the order matters.

### The mechanic has to start before the lock, not at it

A creator must never discover this by clicking. The path in is a failed renewal,
so the notification belongs at that moment, while the card is still fixable —
email plus a studio banner, both naming the card and linking to the billing
portal. Discovering fifty inert courses is the failure mode; being told "your
card failed, here is the link" is the same event handled well.

**Fixed today, because the code got this wrong.** `BillingService` treated
`past_due` as not-paying and dropped the workspace to free on the **first failed
charge** — days before Stripe had finished retrying, and back again when a retry
succeeded. With the lock policy above, one expired card would have inerted a
creator's whole catalogue and then silently restored it. `past_due` now holds the
plan the workspace already had, `unpaid` and `canceled` still downgrade, and
`Workspace::isPaymentFailing()` exists for the banner.

Grace **preserves, it never grants**: a workspace on Pro whose renewal fails
keeps Pro; one on free whose very first charge fails stays free rather than being
handed a plan nobody has paid for. That distinction is what the existing test
`test_an_unpaid_subscription_does_not_grant_a_plan` was already protecting, and
it survived the change.

### How long the grace period lasts — Stripe decides, and one setting is mandatory

**Qori sets no grace period.** `applySubscription()` is called from the Stripe
webhook and nowhere else, `subscription_ends_at` is written but never read, and
there is no scheduled job. So the plan is held for exactly as long as Stripe
leaves the subscription in `past_due`, and the length lives in Stripe's dunning
configuration rather than in this codebase.

Stripe's retry window is roughly **three weeks over about four attempts** by
default, configurable under _Settings → Billing → Subscriptions and emails →
Manage failed payments_.

**The mandatory part.** That same screen chooses what happens once retries are
exhausted, and one of the options is _leave the subscription as-is_ — which keeps
it `past_due` **indefinitely**. Combined with grace holding the plan, that would
be a permanently free Pro account, with no event to end it and nothing in Qori
that could. It must be set to **cancel the subscription** or **mark it unpaid**,
both of which fire `customer.subscription.updated` and downgrade correctly.

This is a dashboard setting the code cannot enforce, so it belongs on the setup
list beside the webhook secret.

**Relying on Stripe's window is the recommendation**, not just the current state.
Stripe also sends the recovery emails and hosts the card-update page, so the
retry schedule and the messages about it stay in one place. A second grace clock
inside Qori would eventually disagree with Stripe about whether someone has paid,
and that disagreement is worse than either answer.

**A longer, Qori-run grace is the intended direction** — see the parked sketch
below. §5's "3-month friction" is a larger number than three weeks, though it
reads as being about dormant free accounts rather than failed cards.

**`subscription_ends_at` is the banner's material.** It is written and never
read, which the flag audit would have caught eventually. "Your access continues
until 3 March" is a far better thing to show a creator with a failing card than a
bare warning, and the value is already there.

### Parked: Stripe's window stands, but Qori's own dunning is the intended direction

**Current behaviour stays** — `past_due` holds the plan, Stripe's retry schedule
decides how long, and the mandatory dashboard setting above is what ends it. Do
not build the below until asked.

The direction, when it is: **Qori runs its own clock and warns the creator
several times, naming the date.** Sketched here while the reasoning is fresh.

**Why it is worth building at all.** Stripe's dunning email says "update your
payment method". Qori's can say _what will actually stop working_: "on 3 March
your fifty courses become read-only. Your students keep their access." Only Qori
knows the consequence, and the consequence is the whole message. That is the
entire case for replacing something Stripe already does adequately.

**A stamped date, never a status.** `grace_until`, written when `past_due` first
arrives. Holding a plan on the strength of a status is what created the
indefinite-hold hole; a date has a clock and a status does not. It is also the
value the emails and the banner interpolate, so there is exactly one place the
deadline is decided.

**Clear it when Stripe recovers.** Stripe keeps retrying and may succeed on day
ten, so `customer.subscription.updated` returning to `active` has to clear
`grace_until` and stop the sequence. This is the disagreement risk of running two
clocks, and it is manageable only because the webhook is the single writer.

**Record what has been sent.** A scheduler that re-evaluates daily will re-send
"three days left" every day unless each step is stamped. One field holding the
last step sent is enough; the activity log gets the narrative line for free.

**These are transactional.** A billing warning is not marketing: never
consent-gated, never counted against the send allowance, and it goes out on the
transactional mailer and domain, per the split already settled.

A cadence worth starting from — every message naming the same date rather than a
countdown, because a date survives being read late:

| Day | Message                                                                |
| --- | ---------------------------------------------------------------------- |
| 0   | The charge failed. Here is the link. Nothing has changed yet           |
| 7   | Still failing. On _date_, this is what stops working                   |
| 14  | Same, more specific about their own numbers — "50 courses", "3 admins" |
| 21  | Tomorrow, and what to do in one sentence                               |
| 22  | It happened. What they kept, and how to get it back                    |

**Decide downgrade versus suspension before building.** They are different states
and the settled lock policy covers only the first: downgrade drops to free and
locks over-cap courses while students keep access; suspension is §21.8's
hibernate, which is heavier and stops more. Picking both is how a mechanic
becomes two mechanics that disagree.

**It needs the scheduler**, which is now the second thing waiting on one —
reminders being the other. Campaign sending is user-triggered and needs nothing;
activity-log pruning was designed around a Mongo TTL index so it needed nothing
either. Two features, one dependency, still deferred.

### On refund and re-send not existing yet

They do not need to. The lock policy is a **mechanic**, and it describes what
those functions must remain able to do whenever they are built. For course sales
most of them may never be built at all — direct charges put refunds and receipts
in the creator's own Stripe dashboard, where Qori cannot take them away. What
Qori owes the mechanic is narrower: keep the **enrolment list readable on every
plan**, because that is the only place a Stripe charge id becomes a person.

### The architecture already guarantees the important half

Checked, and it is better than expected: **there is no refund surface, no invoice
surface and no course delete in Qori at all.** For course sales that is correct
and should stay that way.

Direct charges (§7.2) put the money in the creator's **own** Stripe account.
Refunds, receipts and invoices for course sales therefore live in _their_ Stripe
dashboard, on _their_ balance — Qori does not mediate them and **cannot** lock a
creator out of them whatever their plan. The obligation is honourable by
construction rather than by policy.

What Qori does have to keep readable is the piece Stripe cannot supply: **which
person a charge belongs to.** `enrolments` holds `price_cents`, `currency` and
`payment_reference`, and that row is what turns a Stripe charge id into "Sam, who
bought Beginner Piano in March". Without it a creator has a payment they cannot
attribute and a student they cannot help.

So: **the enrolment list stays visible on every plan, forever.** It is not a
feature, it is the record.

### Delete has to be built, and it collides with one rule

There is no course delete today. It needs designing, because it is the one action
where a creator can legitimately take something from a student who paid — and
that is their call to make, not Qori's, the way a shop may close.

Two things it must do:

- **Keep the enrolment rows.** §14 already keeps paid enrolments, and a refund
  may still be owed after the course is gone. Deleting the course must not
  delete the evidence of who bought it.
- **Say what it costs, before it happens.** A course with active paid enrolments
  is not the same as an empty draft, and the confirmation should name the number
  of students who lose access.

### Getting back under the cap unlocks the survivors (settled, parked)

Deleting down to the plan's cap **unlocks** what is left. The lock means "you are
over your plan", so it ends when you are not.

The alternative — everything stays dead until you delete all fifty and start
fresh — makes destroying forty-nine courses buy the creator nothing, which is a
platform pushing people to destroy more work than the rule requires. "Get under
your limit or upgrade" explains itself; "delete everything or it stays dead" does
not.

Parked rather than closed: it is a policy call, nothing is built against it yet,
and it can be revisited if the arbitrage turns out to be worth more than the
goodwill. Note the free cap of 1 makes the practical difference small — deleting
to one course is nearly deleting everything anyway. It matters more if the free
cap ever rises.

### Related

**§17.4 matters more now**: free being "1 course" versus "1 course with a lesson
cap" changes how much a single paid month can bank before the lock falls.
