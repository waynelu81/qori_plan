# Integrations and onboarding

> Preserved information architecture and onboarding research for external connections.

[Current plan](../../PLAN.md) | [Planning index](README.md)

**Superseded onboarding sequence, 2026-09-11:** the owner now wants staged
creator setup before guided Series creation, with storage, integrations and
seller payment setup skippable. Series-link recipients get basic details,
payment/access and their intended Series, with no creator onboarding. Use the
[current plan](ui-onboarding.md) and [decision](decisions.md#onboarding-follows-the-entry-purpose-2026-09-11)
for implementation planning. The dated research below is preserved, including
its old capability claims; it is not the current build inventory.

## Integrations as one place, and an onboarding that asks (2026-09-07, designed not built)

**Confirmed by the owner on 2026-09-13, with one reversal.** Integrations are
settings of the one Group a person owns: one connection per provider,
disconnected before it can be connected again, the same way the plan is one
per Group. The reversal is the order below. The page comes first, with the one
connector that works today (Stripe, `T-067`), and `T-044` adds storage and
video to it — because a creator looking for "where do I connect Stripe" should
find it under Settings now, not after the other connectors exist.

The human's framing, and it is the right one: Stripe Connect, Google Drive,
Dropbox, OneDrive, Zoom, Teams, Vimeo and YouTube are **all the same kind of
thing** — an account the creator already has, connected once, used by many
courses. Today they are scattered: Stripe is a nav item, storage providers
appear as a dropdown _inside the lesson form_, and Zoom/Teams appear there too
with nothing behind them. There is no page that answers "what have I connected".

**Why this is not built yet, stated plainly: nothing can connect.** Checked
2026-09-07 — there are **zero OAuth flows in the codebase**. `DropboxStorage`
and `VimeoVideos` resolve a media reference to a URL and assume a token already
exists in `connections`; nothing puts one there. Zoom, Teams, Google Drive,
OneDrive and YouTube have no integration at all. The only connect route is
Stripe's, and that is blocked on the Accounts v1/v2 decision above.

So an Integrations page today would list seven services of which **six cannot be
connected**. That is the same defect as "Payouts" implying a balance that cannot
exist, or the error copy that offered to "archive" a course when there is no
archive: a surface promising something the product does not do. Build the
connectors, then the page that lists them — not the reverse.

### The shape, when it is built

- **`/w/{workspace}/integrations`**, one page, grouped by what the connection is
  _for_ rather than by vendor, because that is how a creator decides:
    - **Getting paid** — Stripe. Already has its page; it folds in here.
    - **Where files live** — Google Drive, Dropbox, OneDrive. §8's BYO storage.
    - **Video** — Vimeo, YouTube. Hosting, not storage: a different job (already
      settled in the storage-definitions note above).
    - **Live sessions** — Zoom, Teams. Offered, never required.
- **Workspace-scoped, not user-scoped.** `connections` already carries
  `workspace_id`, and that is correct: an admin invited to a school should use
  the school's Vimeo, not be asked for their own. Worth stating because the
  human's phrasing was "settings related to the login user" — the _account_ being
  connected belongs to a person, but the _connection_ belongs to the school, or
  it disappears when that person leaves.
- **The lesson form then narrows to what is connected**, instead of offering
  five providers and failing at save. That is the real payoff and it is
  invisible until the page exists.

### Onboarding

The human's point: connecting things belongs _after signup_, and only for people
who came to teach.

**Half of this is now built** — registration asks teach-or-learn and only a
teacher gets a workspace, so a student no longer lands in a teaching dashboard.
That was the part that could be built without connectors.

The rest waits on them, and should be a **checklist on the studio home, not a
wizard**. Reasons, in order of how much they matter:

- A wizard is a gate, and every step of this one is optional — §8 lets a creator
  teach with no storage connected, §7 lets them teach for free with no Stripe.
  Blocking on optional setup is how a product loses people before they have seen
  it work.
- `StudioDigest` already computes exactly one `nextAction` and the dashboard
  already renders it. A checklist is that mechanism with more entries, not a new
  one.
- It survives being abandoned. Someone who connects nothing on day one and
  Stripe in week three sees the same list, still true.

Sequence when built: create a course → add a lesson → publish → connect payments
_if they want to charge_ → connect storage _if they hit the 100MB course cap_.
The last two are conditional on purpose — offering Stripe to someone teaching a
free course is the same noise as offering a workspace to a student.

## Still open

1. **Final call on EDM tiering** — recommendation is now concrete: keep the module, cap sends per tier (300 / 5,000 / 25,000), and split Postmark-transactional from SES-broadcast. See the email economics section above.
2. **Is a group the unit of enrolment, or an additional grant alongside it?** This is the largest modelling question currently outstanding.
3. **Whole-course storage cap for the free tier** — a number is needed.
4. **Does the catalogue need categories defined up front**, and who defines them — staff, or free text from creators?
