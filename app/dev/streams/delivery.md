---
stream: delivery
owner: wayne
---

# Stream: delivery

**Goal.** Transactional email that actually arrives, from an address that
belongs to Qori.

**Done when.** All six transactional messages have been sent and received
against the production sender, with bounce and complaint handling wired:
verification, password reset, magic link, confirm an email change, notify the
old address that it changed, and Series access.

Six, not the seven the old wording counted. There is no registration mail —
verification _is_ what a new account receives — and **Qori sends no receipt at
all**, although two model docblocks describe one. Found while specifying
`T-016`, and recorded in its notes.

**State, updated 21 September 2026.** T-016 rendered and read all six messages
in local Mailpit; T-015 configured the production sender; **T-032 confirmed
arrival through it** — cleared by the owner on 21 September 2026, out of
process, so no report exists and the authentication checks (SPF, DKIM, DMARC)
and the receiving providers used are not on the record. Arrival is established;
what arrives passing authentication is not. The proposed
[system email design](../ui-system-email.md) defines the branded shell and
future order/fulfilment compositions; it does not change this stream's six-message
exit condition or claim the new variants are built.

## Tasks, in order

1. `T-016` — Read the mail Qori sends, before a provider ever does: every
   template renders against a local inbox before a real send spends a
   reputation
2. `T-015` — Configure Postmark and the production sender: `useqori.com`
   verified, return path and DMARC in place, the app answering on the domain
   (11 September 2026)
3. `T-032` — Verify every transactional message through the production sender:
   the first proof that a message reaches somebody's hands
   (21 September 2026)
4. `T-017` — Bounce and complaint handling: a suppression fed by a real
   provider, so a bad address stops costing reputation
5. `T-055` — Every transactional message in one Qori email shell: the first
   step of the [system email design](../ui-system-email.md)'s own handoff
   order; four owner inputs before it can be ready, listed in the task

`T-055` sits after `T-032` deliberately. A branded message that does not arrive
is still a message that does not arrive, and restyling six templates while the
sender is unproven would put the checks in the wrong order.

## No longer waiting on the owner

Domain registration, DNS and a Postmark account with a verified sender all
landed on 11 September 2026. `T-015` records what was verified and by what
means.

The distinction the whole stream turned on — **configuration being right is not
the same fact as mail arriving** — is settled: `T-016` proved every template
renders, `T-015` proved the domain and sender are set up, and `T-032` put a
message in somebody's hands on 21 September 2026. What is still unproven is the
next layer down: that what arrives passes SPF, DKIM and DMARC at the providers
that matter, which `T-017` will need before it can trust a bounce.
