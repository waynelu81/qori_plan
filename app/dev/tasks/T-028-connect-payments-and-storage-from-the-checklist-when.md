---
id: T-028
title: Connecting Stripe or Google Drive from a Series comes back to it
stream: onboarding
status: draft
owner: unassigned
estimate: M
depends: T-044
blocks: none
---

# T-028 — Connecting Stripe or Google Drive from a Series comes back to it

> **Draft.** Revised by owner direction on 2026-09-11; not to be started.
> See [PROCESS.md](../PROCESS.md). Split capability work into bounded tasks
> after confirming what will actually be offered.

## Why

Since `D-056` a new creator is asked for nothing up front: Stripe is asked
where a price is typed (`series.price_needs_payments` and its Connect Stripe),
and Google Drive where a file is chosen (`series.*.not_connected` and Connect
Google Drive). Both send the creator to the vendor and back — to
Integrations, not to the Series they were in the middle of. The couple of
clicks `D-056` promised becomes a hunt for the Series again.

Afterwards a connection begun from the Series page lands back on that Series,
at the control that asked for it, whether the creator connected or stopped
partway.

## Scope

**In:**

- The price field's Connect Stripe and the Episode form's Connect Google
  Drive leaving a forwarding address to the Series and its control, through
  `PaymentsDestination` and `ConnectionsDestination`, the mechanism setup's
  part two and three used.
- The landing spending it once, whatever happened at the vendor, as it does
  today.
- Seller readiness at the paid action read from Stripe's capabilities, not an
  account id, as `T-164` already reads it.

**Out:**

- Setup stages of any kind (`D-056` removed them).
- The connectors themselves (`storage` stream, `T-044`).
- Buyer checkout (`T-027`).

## Before this can be ready

- Name the controls on the Series page that start a vendor round trip today,
  and each finalise controller's current landing. (anyone's, from the code)
- The fragment each lands on: `#price` for Stripe, `#new-episode` for Drive
  with the form reopened on the kind it had. (anyone's)
- Name literal files, copy keys and tests. (anyone's)

## Re-scope log

**2026-09-11 — owner revised this draft.** Setup now appears before the first
Series guide, and integrations are included. The owner explicitly confirmed
seller setup can be skipped during onboarding and is prompted before paid
selling. The former blanket connector exclusion and cap-trigger-only sequence
are superseded. No implementation was started.

**2026-09-13 — the seller stage is cut out.** `T-075` places the Stripe doors and a storage explanation in the setup frame, each skippable. What remains here is the prompt for seller setup at the paid action and the storage connectors once `T-044` exists.

**2026-09-16 — the connectors are the `storage` stream's.** `D-016` settled how every storage and live-session integration works and moved `T-044` into a stream of its own, with one task per provider after it. The "inventory the connection flows" bullet above is answered there. What this draft keeps is the storage stage itself: its copy, the link to the Integrations page's provider sections (where the creator picks a tier and reads its limitations), and the seller prompt at the paid action.

**2026-09-23 — the stages are gone (`D-056`).** The owner replaced creator
setup with one first-Series screen, and Stripe and Google Drive are asked
where they are needed. Rewritten to the one piece that still matters: coming
back to the Series afterwards. `T-026` no longer comes first, so the
dependency on it is dropped.

## Notes

Existing Payments/Connect screens and provider capability reads can be reused;
Qori uploads already work without an external account. Dropbox/Vimeo media
resolvers are not connection flows. The
[onboarding plan](../ui-onboarding.md) distinguishes existing capabilities from
new stage presentation, context persistence and provider work.

**23 September 2026, from `T-026`'s walk.** The files shape lands on the
Episode form with "Where it lives" on Google Drive, the first provider the
server offers for a file, so a brand-new creator's first view asks them to
connect Drive although Qori storage needs nothing. Whether the form should
start on Qori storage while Drive is not connected belongs with this task's
round trip.
