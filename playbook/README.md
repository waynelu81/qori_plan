# The playbook

**What a product like Qori costs to build, written so the next one does not pay
it twice.**

Qori is a web application with iOS and Android to follow: multi-tenant, with
sign-in, onboarding, billing, payouts to its customers, integrations into other
people's storage and video accounts, live sessions, transactional email and a
staff console. Most products of that shape need the same twelve or so pieces,
and each piece has perhaps ten decisions in it that take a week to discover and
five minutes to write down once you know.

This folder is those decisions. It is written from work that was actually built
and walked in a browser, not from intentions — where Qori has not proven
something, the module says so rather than guessing.

## How to start a new product from it

1. Read [`stack.md`](stack.md). If the new product's shape is different enough
   that the stack does not fit, most of the rest still applies but the file
   paths will not.
2. Read [`conventions.md`](conventions.md) and adopt or consciously reject it.
   Naming is cheap to set on day one and expensive on day four hundred.
3. Walk [`modules/`](modules/) and pick the ones the product needs. Each module
   opens with **Decide first** — a short list of questions you must answer
   before any code, each with the answer Qori reached and why. Take the answer
   or diverge knowingly; do not rediscover the question.
4. Turn each module's **Build order** into tasks in your own planning system.
   [`process.md`](process.md) is the one Qori uses if you want it.

## What a module is for

A module answers "we need login" with something better than a blank page. It
does not answer "what should this product be" — that is the product's own work.

The test for a module is: **could a competent developer who has never seen Qori
execute the build order without stopping to make a judgement call that someone
has already made?** Where the answer is no, the module has a gap and should say
so.

## The modules

| Module | Covers |
| --- | --- |
| [identity-and-sign-in](modules/identity-and-sign-in.md) | Email-first sign-in, magic links, passkeys, verification, where sign-in lands |
| [tenancy](modules/tenancy.md) | The organising unit, scoping every read, seats vs. customers |
| [onboarding](modules/onboarding.md) | Landing a new person where their purpose points, progress that survives |
| [payments-and-payouts](modules/payments-and-payouts.md) | Charging for the product, and paying its customers through a connected account |
| [byo-vendor-integration](modules/byo-vendor-integration.md) | Connecting a customer's own storage, video or meeting account and granting their customers access |
| [transactional-email](modules/transactional-email.md) | Mail that arrives, and knowing it did |
| [errors-and-copy](modules/errors-and-copy.md) | One exception type, one error vocabulary, every string in a lang file |
| [live-sessions](modules/live-sessions.md) | Scheduled sessions with a start, an end and a recording |
| [recovery-and-deletion](modules/recovery-and-deletion.md) | Archive, delete on a timer, and never a dead end |
| [design-system](modules/design-system.md) | Tokens, states, contrast, the shapes every screen reuses |
| [reachability](modules/reachability.md) | Proving nothing built is invisible |
| [developer-workflow](modules/developer-workflow.md) | Several hands, clone-to-green, the gate |

## Honesty rules for this folder

- **Write only what was built.** A module section describing something Qori
  designed but never ran says **Not proven** and says what is missing.
- **Cite the source.** Every module ends with the Qori tasks, reports and
  decisions behind it, so a reader can check the claim against the record.
- **A decision keeps its reason.** "Do X" is worth a tenth of "do X, because Y
  happened when we did not." The reason is what lets the next product diverge
  safely.
- **Native is a contract, not a guess.** Nothing native is built yet. Each
  module states what iOS and Android will need *from* the module — the API
  surface, token handling, deep links — and stops there.
