# Module: transactional email

**What it is.** Mail the product must send for the product to work — verify
this address, here is your access, your session is tomorrow — and the ability
to know it arrived.

**Done when.** Every message the product sends can be triggered and read
locally in one command, the production sender is configured and authenticated,
and delivery, bounce and complaint rates are visible.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| Can every message be read without a provider? | Yes — one command sends the lot to a local inbox and reads them back | Otherwise the only way to review copy is to trigger each flow by hand. |
| Custom sending domains, custom templates? | Deferred | Both are large and neither blocks a first release. |
| Is a notice queued? | Only once there is a worker that can retry | A deferred/after-response driver cannot retry, so a failed send is simply lost. |
| What records that a notice was sent? | A ledger row per (subject, recipient, kind, publication) with status and attempts | The ledger *is* the outbox: it makes "did we send this" answerable and makes a resend idempotent. |

## Build order

1. **Local inbox** and a command that sends every message to it and reads them
   back. Do this first; it is how all later copy gets reviewed.
2. **The provider and the production sender**, with domain authentication.
3. **Delivery, bounce and complaint reporting**, and a suppression list.
4. **The notice ledger**, for anything scheduled rather than immediate. Needs 2.
5. **A real worker** before anything is marked for the queue. Needs 2.

## Rules that bite

- **Configured is not arriving.** Qori sent from an authenticated domain
  through a real provider for days with *none confirmed arriving*, because
  nobody had checked an inbox. Prove receipt.
- **Do not mark work for a queue that cannot retry.** Know which driver you are
  on and what it does on failure.
- **A suppression list is not optional** once real addresses are in play.
- **Interpolate limits and lifetimes** from the constants that enforce them.

## Native contract

**Not proven.** Links in transactional mail must deep-link into the app when it
is installed and fall back to web when it is not — which constrains whether a
link can be single-use at the HTTP layer, since some clients prefetch.

## Traps

| Symptom | Cause |
| --- | --- |
| "Mail sends but nobody receives it" | Sender authenticated, deliverability never tested. The send succeeding tells you nothing. |
| "A job failed and vanished" | A driver that cannot retry, with work marked as queueable. |
| "The same notice went twice" | No ledger, or a ledger without a uniqueness key. |

## Proven / Not proven

**Proven**: the local-inbox command that renders every message; the provider
and sender configured.

**Not proven**: **delivery itself** — none confirmed arriving as of this
writing; bounce and complaint handling; the ledger; any worker.

## Source

Qori tasks `T-015`, `T-016`, `T-032`. Decision `D-028`. Stream `delivery`.
