---
stream: onboarding
---

# Stream: onboarding

**Goal.** Onboarding follows why the person arrived. A Series-link recipient
confirms basic details, completes payment/access and opens that Series. A
creator meets one screen, "What will you share first?", that makes their first
Series in a couple of clicks; Stripe and Google Drive are asked where they are
needed (`D-056`, 23 September 2026, superseding the staged setup).

**Done when.** Those two paths work without crossing into the wrong setup;
name, email and timezone are confirmed without needless re-entry; Series context
survives authentication and checkout; a new creator reaches the first
Episode's form two clicks after typing a title; a vendor round trip begun from
a Series comes back to it; seller readiness is prompted before paid selling. The required browser and server
checks still apply.

## How it got here

**11 September 2026.** Direct Share and Learn registration both landed on the
receiving home after verification, and a public Series lost its destination
when its verification email was opened
([R-003](../../design/reviews/passes/R-003-2026-09-11-registration-and-first-run.md)).
The owner separated the two paths (`D-001`): a person from a Series link
confirms their details, gets access and opens that Series, and never meets
creator onboarding; a creator was to walk details, storage, integrations and
seller payments, each skippable, before a guided first Series.

**13 September 2026.** The owner registered fresh and was asked nothing: none
of this stream had been built. `T-068` asked for the Group's name first. Walking
both paths again, the owner found the creator side "version zero" and the Peer
side missing — from a Series link a stranger met seven screens and a change of
app before anything was bought — so `T-073`, `T-074` and `T-075` were cut from
the drafts, and `T-076` from a verification tab refreshed after verifying in
another.

**21–22 September 2026.** The [first-share journey](../journeys/first-share.md)
was walked from the home page to a Peer finishing, and its rough edges were
taken off the path (`T-086`, `T-174`, `T-175`, `T-177`). A Peer agrees to the
terms for what they get, and the creator's emails are optional (`T-178`,
`D-049`).

**23 September 2026 (`D-056`).** About ten screens stood between registering
and a share link. The staged setup is superseded for creators: one screen makes
the first Series (`T-026`), the three parts are retired (`T-195`), and Stripe
and Google Drive are asked from the Series and come back to it (`T-028`). What
stands from `D-001` is the whole receiving path, and seller setup stays
optional and is prompted before paid selling.

## The receiving path

A person arriving through an EDM or Series link confirms name, email and
personal timezone, completes payment if the Series is paid or takes free
access, and enters that Series. They never meet creator onboarding, including
when their account also creates Series. Existing access avoids another
purchase. Direct receiving signup without a Series ends in receiving guidance,
not a creator dashboard.

`T-073` and `T-074` put the account, the typed code, free access, checkout and
the confirming state on the Series page itself, and `T-181` brings an
invitation there. What remains is `T-027` on the Series page, `T-196` for a
sign-up that leaves it for the register page, and `T-197` for somebody who
signs up with no link at all. The
[decision record](../decisions.md#onboarding-follows-the-entry-purpose-2026-09-11)
and the receiving half of the
[onboarding plan](../../design/ui-onboarding.md) are the target; R-003 and its
walkthrough remain historical evidence.

## Tasks, in order

1. `T-024` — Ask for a timezone: personal and Group timezone capture, which
   every later task reuses
2. `T-029` — Live session times: scheduling with a confirmed Group timezone;
   its report records the verification limits
3. `T-068` — A new creator is asked to name their Group first: the owner
   registered on 13 September 2026 and was asked nothing
4. `T-073` — Get access from the Series page without leaving it: a stranger
   gets an account and proves the address with a typed code, on the Series
   page. Cut from `T-027`
5. `T-074` — After the code, straight to access: consent carried, a free
   Series opens, a paid one goes to Stripe; a confirming page for the browser
   that returns before the webhook; cancel lands on the Series. Cut from
   `T-027`
6. `T-075` — Creator setup in three parts, each saying why and each skippable:
   name, Stripe, storage. Cut from `T-026` and `T-028`; `D-056` retired it
7. `T-076` — Onboarding progress lives on the person: an admin in somebody
   else's Group must never be sent through its onboarding, and the two home
   routes honour the record
8. `T-078` — The Group keeps no `name_set_at`: the owner's onboarding record
   already says whether the name was chosen. From the owner's Group-model
   review on 14 September 2026
9. `T-086` — The dashboard's rename card still said "Name your Group" once the
   name was chosen: three browser walks in a row reported it
10. `T-174` — Making a Series ready lands on its share link: the first-share
    walk of 21 September 2026 found the link at the foot of a long page
11. `T-175` — The code email names the Series and who shared it: the same walk
    found a bare "Your Qori code" from a name the Peer did not know
12. `T-177` — Naming the Group gives it the URL of its name: the same walk
    found "Walk Studio" living at `walks-group` in every link
13. `T-178` — A Peer agrees to the terms and chooses emails: consent to the
    creator's emails was the price of access (`D-049`)
14. `T-161` — The first-share journey runs as one script, with Stripe and
    Drive: a change that breaks the core journey is caught the day it lands.
    The owner's walk by hand, with a test card, is its last box
15. `T-026` — A new creator's first screen makes their first Series: one
    screen, three shapes, the Episode form opened for the shape (`D-056`)
16. `T-195` — The three-part setup is retired: what `T-026` left with no way
    in goes, and the dashboard's name card takes `T-177`'s URL rule
17. `T-028` — Connecting Stripe or Google Drive from a Series comes back to
    it: the one part of the old stages `D-056` kept
18. `T-191` — The first steps speak to the first ten people: the dashboard's
    first three next actions, the price help and the invitation page's intro
    say start with the people who already ask, with no number restated
19. `T-027` — The Series page confirms who is getting it, and never sells it
    twice: the account named when signed in, the timezone asked once, the
    paid sentence honest, and no second checkout while one is confirming
20. `T-196` — Signing up from a Series page makes no Group: the sign-in link
    on a Series page leads to a register page that made one by default
21. `T-197` — Someone who signs up to receive is told how a Series reaches
    them: the receiving home said only that Series "show up here"
22. `T-025` — Show and send every time in a timezone somebody chose: emails,
    certificates and PDFs still render in UTC
23. `T-179` — A creator supplies their own terms for Peers: `T-178` shows
    Qori's own until creators write theirs

`T-008`, in the identity stream, fixed the confirmed verification-return defect
and established context ownership before the onboarding continuations.

Use shared components where appropriate, but keep the two journeys independent:
completing anything on the creator's side is never a prerequisite for receiving
a Series.

## What the receiving path reuses

Name and email updates, confirmed email changes, the personal timezone field,
free access, buyer checkout and its confirming state already exist, and
`T-073` and `T-074` put them on the Series page. What `D-001` found missing was
the continuation — each detour coming back to the Series it left — and that is
built: the code step never leaves the page, and a password sign-in carries the
Series through verification (`T-008`). What is left is the confirming itself,
`T-027`.

Buyer payment and seller onboarding stay separate. Skipping seller setup
permits drafts and free sharing, not charging buyers: the price field and the
public page say so while the Group's Stripe account cannot take payments
(`T-085`, `T-164`), from Stripe's own status rather than a stored account id.

## Timezone: whose?

- **Personal timezone** (`users.timezone`): the person's display preference.
  `T-024` stores it and the profile page sets it; a receiving person confirms
  it with their basic details (`T-027`). `T-025` owns showing every date in
  it — the interface, emails, certificates and PDFs — and `D-028` settles that
  a Peer's dates follow their own zone, falling back to the Group's.
- **Group timezone** (`groups.timezone`): the creator's scheduling context.
  The first-Series screen asks it only for "A class, week by week", and only
  when the Group has none (`T-026`); the dashboard's card changes it. It may be
  suggested from the device, but an inherited or default value is not explicit
  confirmation, and live-session scheduling still requires it (`T-029`).

Read the [timezone report](../tasks/reports/T-024-2026-09-10-claude.md) and
[scheduling report](../tasks/reports/T-029-2026-09-10-claude.md) for what was
verified.

## Where it touches other streams

The receiving path shares the Series page with selling (checkout, `T-181`'s
invitations) and the verification return with identity (`T-008`); `T-027`
names the files it shares with them. The first-Series screen and the Series
page it lands on are the design stream's surfaces too. The generated board
records each task's status; this stream records why the paths are separate.
