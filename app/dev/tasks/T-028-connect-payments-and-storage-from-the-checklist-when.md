---
id: T-028
title: Skippable storage, integrations and seller payment setup
stream: onboarding
status: draft
owner: unassigned
estimate: L
depends: T-026, T-044
blocks: none
---

# T-028 — Skippable storage, integrations and seller payment setup

> **Draft.** Revised by owner direction on 2026-09-11; not to be started.
> See [PROCESS.md](../PROCESS.md). Split capability work into bounded tasks
> after confirming what will actually be offered.

## Why

The owner wants creators to encounter storage, integrations and seller payment
setup before guided first-Series creation, with Skip available on all three.
Seller setup should be prompted again before selling a paid Series. This
supersedes the old draft's rule to show setup only after a Series has a price
or an upload cap is reached.

## Scope

**In:**

- Three optional stages in the T-026 frame, ordered storage → integrations →
  seller payments, each with explicit Skip, saved progress and a destination
  to come back to.
- An honest storage stage that distinguishes usable Qori uploads from external
  storage connections, and an integration stage showing only working choices.
- Inventory and separately specify the minimal supported external connection
  flow(s). If none is ready, the stage still allows continuation and makes no
  false connection claim; provider implementation remains recorded work.
- Reuse the existing seller Payments/Connect flow, with onboarding-specific
  finalise/resume and unstarted, pending, ready, cancelled and failed states.
- Prompt for seller setup before enabling paid selling when skipped or not
  ready; resume the intended Series action after authoritative readiness.
- A persistent route back to supported setup actions after Skip. Skipped does
  not mean connected, paid, complete at the provider or ready to sell.

**Out:**

- Requiring optional connection/setup before draft creation or free sharing.
- Buyer checkout, which belongs to T-027, and Qori subscription billing.
- Assuming Connection enum/model support supplies OAuth, or implementing every
  named provider as one undifferentiated task.
- A broad integrations-directory redesign beyond the setup/resume controls.

## Before this can be ready

- Choose the first supported provider(s), or explicitly defer each, and name
  the begin/finalise/refresh/disconnect work as bounded implementation slices.
  No routed external OAuth/account-connection flow was found in this review.
- Define the contract with T-026's frame so the final order is correct without
  a circular task dependency. Re-estimate/split this expanded L scope.
- Specify readiness using seller capabilities, not merely an account ID or a
  landing from the provider. The existing checkout guard is not the complete
  new rule.
- Name exactly where paid selling becomes enabled and the prompt's destination
  in the Series. Draft preparation remains possible before seller setup.
- Specify Skip, revisit, pending provider review, cancellation, failures and
  permissions for each stage. Reuse current limits/configuration when describing
  uploads; a dated storage-cap research number is not an implementation fact.
- Name literal files, copy keys, completion records, APIs and tests. Separate
  mocked handling, local UI verification and live provider verification.

## Re-scope log

**2026-09-11 — owner revised this draft.** Setup now appears before the first
Series guide, and integrations are included. The owner explicitly confirmed
seller setup can be skipped during onboarding and is prompted before paid
selling. The former blanket connector exclusion and cap-trigger-only sequence
are superseded. No implementation was started.

**2026-09-13 — the seller stage is cut out.** `T-075` places the Stripe doors and a storage explanation in the setup frame, each skippable. What remains here is the prompt for seller setup at the paid action and the storage connectors once `T-044` exists.

**2026-09-16 — the connectors are the `storage` stream's.** `D-016` settled how every storage and live-session integration works and moved `T-044` into a stream of its own, with one task per provider after it. The "inventory the connection flows" bullet above is answered there. What this draft keeps is the storage stage itself: its copy, the link to the Integrations page's provider sections (where the creator picks a tier and reads its limitations), and the seller prompt at the paid action.

## Notes

Existing Payments/Connect screens and provider capability reads can be reused;
Qori uploads already work without an external account. Dropbox/Vimeo media
resolvers are not connection flows. The
[onboarding plan](../ui-onboarding.md) distinguishes existing capabilities from
new stage presentation, context persistence and provider work.
