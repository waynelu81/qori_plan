---
id: T-032
title: Verify every transactional message through the production sender
stream: delivery
status: done
owner: wayne
estimate: M
depends: T-015, T-016
blocks: T-043
---

# T-032 — Verify every transactional message through the production sender

> **Done, 21 September 2026.** Cleared by the owner directly: mail through the
> production sender was verified as arriving. It never passed through `ready`
> or `doing`, so there is no report and no spec was frozen — see **Notes** for
> what that means for the record.

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

None. The task was cleared without being specified.

## Notes

**Closed out of process, deliberately.** The owner ran the verification and
cleared the task on 21 September 2026 rather than specifying it, claiming it
and reporting on it. That is the owner's call to make, and the outcome — mail
arrives — is what the task existed to establish.

**What is not on the record.** `Scope` asked for three things, and only the
first is known to be satisfied:

- [x] Messages sent through the production sender arrive.
- [ ] **Which receiving providers were used.** The scope named at least two,
      with Gmail and Outlook as the two that matter commercially.
- [ ] **SPF, DKIM and DMARC confirmed passing on what arrived.**
- [ ] **Evidence recorded in `../walkthroughs.md`.**

Those are not claims this file can make on the owner's behalf. If the checks
were done, a line in `walkthroughs.md` closes the gap and costs a minute; if
they were not, the arrival is proven for whatever path was tested and the
authentication result is still unknown. Either way `T-017` (bounce and
complaint handling) is the next thing that touches it, and it will need to know.

**What this unblocks.** `T-043` — inviting people to a Series — which was
waiting on mail that works.
