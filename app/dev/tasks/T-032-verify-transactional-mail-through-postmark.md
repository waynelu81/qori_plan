---
id: T-032
title: Verify every transactional message through the production sender
stream: delivery
status: draft
owner: unassigned
estimate: M
depends: T-015, T-016
blocks: T-043
---

# T-032 — Verify every transactional message through the production sender

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

This is the half of the old `T-016` that needs the owner. That task now builds a
local inbox and reads every message back, which proves the templates render and
the links resolve. It proves nothing about **arrival**: a message that is
perfect in Mailpit can still be rejected by a receiving server, land in spam, or
never leave because DKIM was never signed.

Splitting the two is what lets the cheap half happen now. Mailpit is an SMTP
sink on localhost and cannot answer any question about deliverability, so
keeping both in one task meant neither could start until a Postmark account
existed.

## Scope

**In:**

- Sending each of the six transactional messages through Postmark to real
  mailboxes on at least two different providers.
- Confirming SPF, DKIM and DMARC pass on what arrives.
- Recording the evidence in `../walkthroughs.md`.

**Out:**

- Rewriting copy, unless a message is actually wrong.
- Broadcast and campaign mail, which is SES and a separate decision (§9).
- Bounce and complaint handling, which is `T-017`.

## Before this can be ready

- `T-015` first, necessarily: domain, DNS and a verified sender.
- `T-016` first, because sending a template with a placeholder still in it to a
  real mailbox wastes a send and a reputation.
- **Decide which receiving mailboxes count.** Gmail and Outlook are the two that
  matter commercially and behave differently; a self-hosted domain proves
  nothing about either.
- **Decide where the evidence lives.** Recommend a `walkthroughs.md` entry with
  the checklist kept here, matching how browser evidence is already handled.
- **Decide whether a missing receipt blocks this.** Qori sends none, and
  `T-016`'s notes record that two model docblocks describe one as though it
  existed. If a receipt is written first, this task verifies seven messages
  rather than six.

## Re-scope log

None.

## Notes

None.
