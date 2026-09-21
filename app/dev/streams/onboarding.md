---
stream: onboarding
---

# Stream: onboarding

**Goal.** Onboarding follows why the person arrived. A Series-link recipient
confirms basic details, completes payment/access and opens that Series. A
creator completes staged setup, with optional connections skippable, then
receives guided first-Series creation.

**Done when.** Those two paths work without crossing into the wrong setup;
name, email and timezone are confirmed without needless re-entry; Series context
survives authentication and checkout; creator setup resumes after skips or
provider returns; seller readiness is prompted before paid selling; and the
first-Series guide leads to real saved work. The required browser and server
checks still apply.

## Current state and revised direction

**Observed 2026-09-11:** direct Share and Learn registration both land on the
receiving home after verification. Share creates a Group, but its owner must
find **You also share / Open** before reaching creation guidance. The Group's
first-Series action and name/timezone form work, and saving a draft shows the
Episode form. Public-Series registration preserves the destination initially;
opening its verification email immediately afterwards loses it. See
[R-003](../design-review/passes/R-003-2026-09-11-registration-and-first-run.md).

**Owner decision after that review:** setup precedes guided creation for
creators. Basic details → advanced/Group details including timezone → storage
(skip allowed) → integrations (skip allowed) → seller payments (skip allowed)
→ first-Series guide. Prompt again for seller setup before paid selling. The
old checklist-only/no-wizard direction is superseded; it must not be used to
skip the setup the owner has now requested.

Receiving users arriving through an EDM/Series link instead confirm name, email
and personal timezone, complete payment if paid or free access if applicable,
and enter that Series. They never encounter creator onboarding, including when
their account also creates Series. Existing access avoids another purchase.
Direct receiving signup without a Series ends in receiving guidance, not a
creator dashboard.

The [decision record](../decisions.md#onboarding-follows-the-entry-purpose-2026-09-11)
and [current onboarding plan](../ui-onboarding.md) are the target. R-003 and its
walkthrough remain historical evidence; payment and provider behaviour described
in the plan was inspected in source, not exercised as a new live journey.

**13 September 2026.** The owner registered fresh, confirmed the address and
landed on the dashboard with nothing asked. Nothing in this stream had been
built; its tasks were drafts in a stream `PLAN.md` did not list. `T-068` was
the first slice, cut from `T-026`: name the Group, once, before anything else.

**13 September 2026, later.** The owner walked both paths after `T-068` and
`T-072`. The creator side worked and was "version zero": one page, two fields,
no why, no skip. The Peer side was not there: from a Series link a stranger
met seven screens and a change of app before anything was bought. `T-073`,
`T-074` and `T-075` were cut from the drafts on that finding, and `T-076` from
the owner refreshing the verification tab after verifying in another:
Fortify's page sends a verified person to the home route, so the home route
has to honour the setup record.

## Tasks, in order

1. `T-024` — Ask for a timezone: personal and Group timezone capture, which
   every later stage reuses
2. `T-029` — Live session times: scheduling with a confirmed Group timezone;
   its report records the verification limits
3. `T-068` — A new creator is asked to name their Group first: after
   verification, on sign-in and on "start sharing", an owner whose Group has no
   chosen name lands on a page that asks for it, then the Group's home
4. `T-073` — Get access from the Series page without leaving it: a stranger
   gets an account and proves the address with a typed code, on the Series
   page. Cut from `T-027`
5. `T-074` — After the code, straight to access: consent carried, a free
   Series opens, a paid one goes to Stripe; a confirming page for the browser
   that returns before the webhook; cancel lands on the Series. Cut from
   `T-027`. The one real test-card purchase is the owner's to walk
6. `T-075` — Creator setup in three parts, each saying why and each skippable:
   name, Stripe, storage. Storage explains and moves on until `T-044` gives it
   something to connect. Cut from `T-026` and `T-028`
7. `T-076` — Onboarding progress lives on the person: the record of setup
   progress moved from the Group to the User, and the two home routes send an
   owner with an unfinished part to it
8. `T-078` — The Group keeps no `name_set_at`: whether the name was chosen is
   the owner's onboarding record, which `T-076` made the source of everything
   else about setup; the column was the same bookkeeping kept twice. From the
   owner's Group-model review on 14 September 2026
9. `T-086` — The dashboard's rename card still says "Name your Group" once the
   name is chosen: three browser walks in a row reported it
10. `T-026` — Guided first-Series creation, and whatever setup remains after
    `T-068` took the name; still needs bounded implementation slices
11. `T-027` — Series-linked receiving signup, details, checkout/access
    continuation and direct receiving welcome: what remains after `T-073` and
    `T-074`
12. `T-028` — Storage and integrations stages in `T-026`'s frame, and the
    seller-readiness prompt at the paid action; waits on `T-044` for a
    connector to offer
13. `T-025` — Consume the saved timezone consistently across dates; separate
    from capturing it
14. `T-174` — Making a Series ready lands on its share link: the first-share
    walk of 21 September 2026 found the link at the foot of a long page
15. `T-175` — The code email names the Series and who shared it: the same walk
    found a bare "Your Qori code" from a name the Peer did not know

`T-008`, in the identity stream, fixed the confirmed verification-return defect
and established context ownership before the onboarding continuations.

Use shared components where appropriate, but keep the two journeys independent.
The setup frame and its later capability stages must have explicit boundaries
before their specs become ready; a task for the frame alone must not claim the
complete owner flow already works.

## Capabilities to reuse and capabilities to build

Name/email updates, confirmed email changes, timezone fields, Group naming,
Series actions, free access, buyer checkout and seller Payments/Connect already
have implementations. Their current return routes do not supply the new
onboarding continuation. Reuse the services and validation, specify the missing
context and presentation, and recheck the resulting journey.

Qori file uploads work without a connection. Connection records and
Dropbox/Vimeo media adapters do not mean an external account can be connected
through the product: no routed OAuth/account-connection flow was found in the
source check. T-028 must identify which connectors to build and which to defer.
Each optional stage must still allow continuation if no connection is available.
The older [integrations research](../integrations-and-onboarding.md) is context,
not proof of current capability or the new stage order.

Buyer payment and seller onboarding are separate. T-027 must handle checkout
cancellation and pending/confirmed access while preserving the requested Series.
T-028 must use seller capability status before paid selling, not a provider
return or stored account ID alone. Skipping seller setup permits draft creation
and free sharing; it does not mean the creator can already charge buyers.

## Timezone: whose?

- **Personal timezone:** the person's display preference, confirmed in receiving
  basic details and creator advanced details. T-024 stores it; T-025 owns
  consistent consumption across the interface, emails, certificates and PDFs.
- **Group timezone:** the creator's scheduling context, confirmed separately in
  advanced/Group setup. It may be suggested from the personal timezone, but an
  inherited/default value is not explicit confirmation. Existing live-session
  scheduling already requires that Group confirmation.

Read the [timezone report](../tasks/reports/T-024-2026-09-10-claude.md) and
[scheduling report](../tasks/reports/T-029-2026-09-10-claude.md) for what was
verified. Updating onboarding does not re-open those completed implementations.

## Where it touches other streams

Coordinate T-008 with identity, buyer and seller returns with checkout, and
connector slices with capability planning. Design T-026's post-setup object
composition with the next redesign sprint so the same creator home is not
rebuilt twice. The generated board records each task's status; this stream
records why the paths are separate.
