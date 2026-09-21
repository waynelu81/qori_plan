---
id: T-043
title: Invite people to a Series, ten at a time
stream: selling
status: draft
owner: unassigned
estimate: L
depends: T-032
blocks: none
---

# T-043 — Invite people to a Series, ten at a time

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). One decision is still open and it is named
> at the bottom. Everything else here is owner direction, recorded 11 September 2026.

## Why

`PLAN.md` calls Qori "an invitation-led knowledge-sharing product". **There are
no invitations.**

`AccessController::store()` takes an email address, looks for a `User` with it,
and refuses when there is none. Its own comment says why and says what is
missing:

> Access grants access to episodes, and access needs somewhere to sign in to —
> so this path only adds people who already have an account. The §4 funnel
> reaches everyone else through an EDM invitation instead, and that flow is not
> built yet, so say so rather than half-grant them.

That is an honest refusal rather than a bug. Its consequence is that a creator's
actual audience — a list of email addresses belonging to people who have never
heard of Qori — cannot be reached at all.

## What the owner asked for, 11 September 2026

A creator opens a Series, presses a button, and gets a page for inviting people
to **that** Series.

- **Up to ten people per batch.** Pressing **Add** appends an empty row.
- **Pasting ten addresses copied out of a spreadsheet fills ten rows.** One
  paste into the first email field, ten rows populated, not one field holding
  ten addresses separated by tabs.
- **Per person: email required; first name, last name and price all optional.**
- **A price of nothing is a real answer.** Somebody invited at no charge
  confirms and gets access without being sent to checkout.

**Yes, a Series has a price.** `series.price_cents` and `series.currency`, both
nullable, where null means free rather than zero — a deliberate distinction,
because it decides whether anybody is sent to checkout at all. The per-person
price on an invitation therefore overrides that Series price for that person,
and "0" and "leave it blank" are two different instructions.

## Decisions taken to make this specifiable

**This task sends. `T-027` receives.** The seam is the moment the message
leaves. `T-027` already specifies arrival, detail confirmation, verification,
free and paid branches, and landing on the Series. Building either half of the
journey twice is the failure to avoid, and the two tasks must not both own the
landing page.

**A Peer row carries the invitation.** `peers` is already group-scoped, unique on
`(group_id, email)`, and has a **nullable `user_id`** — which is exactly the
shape of somebody invited who has not registered. First and last name have a
home there too. Nothing new is needed to hold a person who does not yet exist.

**Access is created on acceptance, not on invitation.** The owner's "confirm
without going through payment" says the recipient confirms, and a confirmation
that grants nothing is theatre. It also keeps the Peer cap honest: a cap is a
limit on selling, and an invitation nobody has accepted has sold nothing.

**One batch is one action, and a bad row does not lose the other nine.** Ten
rows validated together, reported per row, and either all ten send or none do.
A creator who mistypes the seventh address must not have to retype six.

**"Invite", not "campaign".** Ten people chosen by name is not broadcast. §9's
sending caps, the suppression list and SES belong to `T-045`, and an invitation
is transactional: it is the message that carries somebody's access.

## Preconditions

`T-032`, so a message that says it was sent was sent. An invitation that
silently does not arrive is worse than no invitation, because the creator
believes they have shared something.

## Scope

**In, provisionally:**

- A page for inviting up to ten people to one Series.
- Paste-to-populate from a spreadsheet column.
- Per-person email, first name, last name and price, with only email required.
- The invitation record on `peers`, and what the creator sees afterwards.
- The invitation message and the link it carries.

**Out:**

- What happens when somebody opens one. That is `T-027`.
- Campaigns and broadcast, which are `T-045`.
- Importing a list from a file. Pasting ten is what was asked for; a CSV import
  is a different feature with its own failure modes.
- Reminding, resending or chasing. Each is its own decision about how often Qori
  may mail somebody who has not answered.
- Vouchers. A per-person price is not a code anybody types — see `T-049`.

## Before this can be ready

- **Decide whether an invitation link is single-use, and whether it expires.**
  This is the one genuinely open question and it is load-bearing. An invitation
  priced at nothing, forwarded to a stranger, grants a stranger access; the same
  link priced at forty dollars quietly offers a stranger the creator's discount.
  `T-036` answered the same question for magic links — fifteen minutes, one use
  — and an invitation somebody opens a week later is a different promise.
  Binding the link to the address it was sent to is the other shape, and it costs
  a person who forwards it to their own second address.
- **Decide what a price of nothing on a paid Series means for the creator's
  numbers.** The access exists, the money does not, and the Peer counts. Confirm
  that is intended before `ShareDigest` starts reporting it.
- Read `AccessService::peerFor()` before specifying. `qori:reachability` reports
  it as called only from inside its own class, which suggests the
  Peer-resolution half of this was written and never wired up.
- Confirm the paste shape against a real spreadsheet copy. A column copied out of
  Excel arrives as newline-separated text; a row arrives tab-separated; and a
  selection two columns wide arrives as both. Decide which of those are
  supported rather than discovering it in a browser.
- **An accepted invitation lands on the Series page and lets it do the rest.**
  Under `D-016` (16 September 2026) `shared.show` is where every access path
  ends: it asks a Peer for the vendor account a Series needs (`T-092`) and makes
  sure the vendor grant exists (`T-091`). Acceptance should land there rather
  than own a landing page, so the prerequisite is met once. Anyone's question:
  whether `T-027`'s landing already reaches `shared.show`, or needs to.

## Re-scope log

None.

## Notes

`PLAN.md`'s beta gate includes "five representative creators can create and
share a Series without developer help; invited Peers understand how to get
access and continue". As things stand, those five creators can only share with
people who already have Qori accounts, so that gate cannot be attempted. This is
the largest single gap between the plan and the build.
