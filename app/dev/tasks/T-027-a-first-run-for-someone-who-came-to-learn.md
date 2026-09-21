---
id: T-027
title: Series-linked signup, payment and receiving onboarding
stream: onboarding
status: draft
owner: unassigned
estimate: M
depends: T-008, T-024
blocks: none
---

# T-027 — Series-linked signup, payment and receiving onboarding

> **Draft.** Revised by owner direction on 2026-09-11; not to be started.
> See [PROCESS.md](../PROCESS.md). This now covers the receiving entry journey,
> beyond its former no-access empty-state scope.

## Why

An EDM/shared Series link tells Qori what the person is here to receive.
R-003 confirmed that this context can be lost during verification. The owner
requires a short receiving flow: confirm name, email and personal timezone,
complete payment/access as applicable, then open that exact Series. Creator
setup must never interrupt this journey.

## Scope

**In:**

- Series-linked registration/sign-in that establishes receiving intent without
  asking a redundant creator/learner question or creating a creator Group.
- Name/email/personal-timezone confirmation with existing values prefilled,
  required verification and email correction, retaining the Series destination.
- Existing-account handling, including an account that also owns a Group.
- Free access, paid checkout and already-granted access branches. Reuse the
  existing services and applicable consent; an EDM link is not itself access.
- Contextual cancellation, failure, payment-confirmation waiting and granted
  states, followed by Start/Continue for the same Series.
- Direct receiving signup without a Series: the same basic details followed by
  an honest explanation of the sender's link, with no invented catalogue.

**Out:**

- Creator setup, storage/integration connection or seller-payment onboarding.
- Qori subscription checkout. Buyer payment here is for the requested Series.
- Replacing payment fulfilment, granting access on a browser return alone or
  treating a campaign parameter as identity/permission.
- Building an EDM composer or sending campaigns to verify this flow.

## Before this can be ready

- Specify the trusted Series/entry context and its persistence across signup,
  verification, profile correction, provider returns and resumed sessions.
- Name the profile/confirmation components, exact fields and validation reuse,
  routes, copy keys and the contextual returns currently missing from Profile.
- Define checkout return states against server payment/access status, including
  cancellation back to the Series and the interval before webhook fulfilment.
  Prevent accidental repurchase when access exists or payment is pending.
- Decide bounded implementation slices and file ownership with T-008 and
  checkout. T-026 may share visual parts, but completing creator setup must not
  be a prerequisite for this journey. Estimate M replaces the former S.
- Specify server and browser cases for new/existing accounts, an existing
  creator arriving as a buyer, free/paid/existing access, unavailable Series,
  changed email, delayed fulfilment and resume. Test forwarded campaign links
  without silently switching the signed-in identity.

## Re-scope log

**2026-09-11 — owner expanded this draft.** It formerly covered only the empty
receiving home and excluded changing registration. Series-linked entry now
selects the receiving journey, confirms basic details and continues through
payment/access. The dependency on T-026 is replaced by T-008/T-024; the receiving
path does not await creator setup. No implementation was started.

**2026-09-13 — two slices cut.** `T-073` (account and typed code on the Series page) and `T-074` (straight to access, confirming state, cancel to the Series) are `ready`. What remains here is the name, email and personal timezone confirmation and the direct receiving welcome.

## Notes

R-003 F-4 supplies the no-access-home evidence; F-1/T-008 supply the confirmed
verification-return failure. Checkout cancellation to the shared index and a
possible browser-return-before-fulfilment refusal were identified in source,
not reproduced as payment findings in R-003. See
[the current onboarding plan](../ui-onboarding.md) and the owner decision for
the target and remaining validation.

**17 September 2026 — [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-7/F-10.** Fresh receiving cards still omit Group attribution, the completed Episode count and the known named continuation; the empty `/shared` page does not guide the person back to the sender's Series link or the receiving address. Retain R-002's decision to handle this in the receiving composition. Paid entry's “Type it here and you're in” must distinguish email verification from payment (also recorded on T-011). T-073's typed code and T-074's access/payment slices are implemented work to reuse, not missing capabilities. This pass did not repeat the complete registration, code, cross-account return or payment matrix; do not take its static Series form as proof those transitions passed.
