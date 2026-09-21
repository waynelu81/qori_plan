---
id: T-017
title: Bounce and complaint handling
stream: delivery
status: draft
owner: unassigned
estimate: M
depends: T-015
blocks: none
---

# T-017 — Bounce and complaint handling

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

`App\Services\SuppressionService` and the `email_suppressions` table exist. Nothing feeds them from a real provider, so a hard bounce today is invisible and the address stays on the list.

## Scope

**In:**

- A Postmark webhook that records bounces and complaints as suppressions.
- Signature verification on the endpoint.

**Out:**

- Changing how suppressions are consumed — that already works.

## Before this can be ready

- Read `SuppressionService` and the existing table before specifying. The shape may already be right, in which case this is a controller and a route.
- Contractual transactional messages must stay outside marketing consent gates — confirm the suppression check does not block a receipt.

## Re-scope log

None.

## Notes

None.
