---
stream: selling
---

# Stream: selling

**Goal.** A creator can put a price on a Series, hand somebody a link to it,
discount it, and invite people to it by name.

**Done when.** A creator can copy the public link to a Series they have made
ready; a person who opens that link can read it and buy it; a creator can invite
up to ten people at once, each at their own price including nothing; and a
voucher code can change what a Series costs for a period the creator sets.

**State, 13 September 2026.** The selling surface is further along than anyone
knew, the sharing surface is not there at all, and connecting payouts had been
broken since 9 September.

- **The public page is built.** `GET /s/{group}/{series}` renders the title,
  summary, price, episode count and episode titles, offers `POST /checkout/…`
  for a paid Series and `POST /s/{seriesId}/grant` for a free one, and knows
  whether the reader already has access. Payment happens on that page today.
- **Nothing linked to it** until `T-050`. Not one Vue file referenced the
  route; the generated helper existed and had no importer, and there was no
  clipboard copy anywhere in the product. A creator had no way to find the URL
  of their own page.
- **Series carried a price, and nothing could set it** until `T-054`.
  `price_cents` and `currency`, nullable, where null means free rather than
  zero — the difference decides whether anybody is sent to checkout. No form
  had ever sent either field; the owner found this testing on 13 September
  2026, and the one priced Series in development had been priced by hand with
  no currency at all.
- **Connecting payouts was broken from 9 to 13 September.** The domain
  rename turned Stripe's `contact_email` parameter into `peer_email`, which
  Stripe refuses; the owner found it testing on 13 September. The same review
  found the connect action was a GET that wrote, that Qori answered the entity
  type Stripe's form should ask, that there is no way to connect a Stripe
  account a creator already has, and no way to disconnect one. All four are
  fixed. On 17 September 2026 the owner closed the create door: opening a
  Stripe account is the creator's concern, and Stripe's sign-in is the only
  way in (`D-023`, `T-113`). That door needs the owner to enable OAuth and
  supply the client id before anyone can connect (`T-063`).
- **There are no vouchers.** `SubscriptionCoupon` is Qori's own plan discount,
  with Stripe coupon ids and durations in months. It is not a creator's discount
  on a Series and must not be extended into one.
- **There are no invitations.** Granting access looks up a user by email and
  refuses when there is none.
- **The public page still offers to buy from a Group that has disconnected.**
  Two browser walks reported it; `T-085` is written from them.

## Why this is its own stream

These tasks touch the public page, the Series builder, checkout and access —
one file set, held together by one question: can a creator actually sell and
share the thing they made. Splitting them across `delivery` and `reachability`
put a mail concern and a routing concern in charge of a commerce decision, and
neither stream's goal describes any of this.

## Tasks, in order

1. `T-050` — The public Series link is not visible to its creator
2. `T-054` — A creator can set what a Series costs
3. `T-061` — Stripe is sent the owner's email under the field it recognises:
   the bug the rename made
4. `T-064` — A creator can disconnect Stripe and start again: a way back, and
   it hides the button a connected account should not show
5. `T-062` — Connecting payouts is a POST, and Qori asks only the country:
   stopped and rewritten once, because v2 refused an account without one
6. `T-063` — Connect the Stripe account a creator already has: the one sandbox
   round trip is owed until the owner enables OAuth in the Stripe dashboard
   and supplies the client id
7. `T-071` — Buying a Series reaches Stripe's page from the button: the
   owner's first real purchase attempt went nowhere
8. `T-072` — A Series says what its payment is called, and how it reads on a
   card statement: the receipt line and the statement line, validated to
   Stripe's rules before Stripe is asked
9. `T-058` — One place formats money: small, and it retires the `'USD'`
   fallbacks `T-054` made unreachable
10. `T-085` — The public Series page still offers to buy when the Group is
    disconnected: the buyer meets the checkout refusal instead of a sentence
11. `T-112` — Stripe's HTTP client lives in the Stripe folder: the owner's
    move, before the onboarding it serves is rewritten (`D-022`)
12. `T-113` — Payouts connect only through Stripe's sign-in: Qori stops
    opening accounts and asking a country, and `Connect` speaks in begin,
    finalise and decline (`D-023`)
13. `T-114` — Stripe's payloads and webhooks are read in the Stripe folder:
    a draft until the owner answers the checkout trust gap and the two
    webhook scopes found on 17 September 2026, and where the direct charge
    becomes begin, finalise and decline
14. `T-043` — Invite people to a Series, in batches of ten
15. `T-049` — A voucher that changes what a Series costs
16. `T-079` — A Group records when its subscription began: the owner asked for
    `subscription_starts_at` on 14 September 2026, and what reads it is the
    open question. The same review kept `stripe_customer_id`: it is Qori's
    own plan customer, not anything a direct charge uses
17. `T-146` — The Stripe sign-in's code says payments, begin and finalise:
    the owner, 19 September 2026, "the creator does not get payout from
    Qori", and no step is named `return` (`D-032`)

`T-050` went first because it was small and entirely specified, `T-054` for the
same reason. The four payouts tasks come before the rest because a price
nobody can be paid for is decoration: `T-061` was the bug, `T-064` gives the
creator a way back, `T-062` makes the connect flow safe and leaves Stripe the
questions v2 lets it ask, and `T-063` opens the door half of them will want
first. `T-064` moved ahead of `T-062` on 13 September: nothing in it needs the
POST form, and `T-062`'s sandbox check could have stalled it. Everything after
assumes a price exists and an account can receive it.

## Notes

`T-043` sends invitations and stops at the send. What happens when somebody
opens one is `T-027` in the `onboarding` stream, which already specifies
arrival, verification, payment and landing on the Series. Two tasks, one journey,
and the seam is the moment the message leaves.

`T-043` depends on `T-032` for a reason worth restating: an invitation that
silently does not arrive is worse than no invitation, because the creator
believes they have shared something.
