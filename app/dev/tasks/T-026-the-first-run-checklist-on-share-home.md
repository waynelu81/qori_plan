---
id: T-026
title: Creator setup followed by guided first-Series creation
stream: onboarding
status: draft
owner: unassigned
estimate: L
depends: T-068, T-024
blocks: T-028
---

# T-026 — Creator setup followed by guided first-Series creation

> **Draft.** Revised by owner direction on 2026-09-11; not to be started.
> See [PROCESS.md](../PROCESS.md). The broader scope needs bounded implementation
> slices and literal specifications before it can be ready.

## Why

> **Narrowed 2026-09-13.** Naming the Group before anything else is `T-068`,
> built and small. What remains here is the guided first Series and whatever
> setup the journey still wants after that; the L estimate is a sign it should
> be cut again before it is `ready`.

R-003 F-2/F-3 found that new creators land on the receiving dashboard and must
find their Group before reaching the existing first-Series action. The owner
subsequently specified the desired sequence: basic details, advanced/Group
details including timezone, optional storage/integrations/seller setup, then
guided creation. The previous checklist-only proposal no longer defines this
onboarding task.

## Scope

**In:**

- A creator setup frame entered after direct creator registration or an
  explicit Start sharing choice, with required verification handled in context.
- Basic name/email confirmation, followed by advanced/Group details including
  personal timezone, Group name and Group scheduling timezone. Reuse existing
  profile, email-change, timezone and Group primitives.
- A saved progression contract with Back, retained values, resume and the
  optional stages supplied by T-028, before the first-Series guide.
- Guided first Series → first Episode → ready → share, using the existing
  actions and a real object rather than zero meters.
- Separate profile confirmation, Group setup completion and first-Series
  graduation. Completed or skipped optional stages permit continuing; they do
  not establish connector or seller readiness.
- Entry routing that preserves a requested Series ahead of creator setup,
  coordinated with T-008/T-027. Existing accounts may have both modes.
- Blocking and permission states ahead of encouraging actions.

**Out:**

- Running creator setup for an EDM/Series-link recipient, even if that account
  also creates Series. The receiving journey is T-027.
- Making storage, integrations or seller setup compulsory before draft creation.
- Rebuilding timezone storage (T-024 done) or account/payment services.
- Implementing every external connector inside this frame; T-028 inventories
  and supplies the optional capabilities through separately specified slices.

## Before this can be ready

- Specify and split the frame, profile/Group confirmation, routing and creation
  guide into bounded changes. Estimate L replaces the former M because the
  owner expanded the task beyond a dashboard checklist.
- Name every file, route/response owner, step contract, copy key, completion
  record and migration, including reuse of existing email-change semantics.
- Define account versus Group ownership, stage completion/skipping, return from
  verification/providers, resumption in later sessions and the tracked first
  Series. Follow the behaviour in [ui-onboarding.md](../ui-onboarding.md).
- Define the T-028 extension boundary so this task can establish the frame
  without claiming optional provider implementations already work. The final
  owner journey requires both tasks; do not introduce a dependency cycle.
- Validate direct creator entry, explicit conversion from receiving, accounts
  with both modes, Series-link precedence, each interruption/return, retained
  details, first draft and permissions/caps. Specify runtime UI checks as well
  as server invariants.

## Re-scope log

**2026-09-11 — owner changed the target while this task was draft.** The prior
exclusion of any staged setup, the Series-first onboarding order and the
collapse-only checklist recommendation are superseded. Setup comes first;
storage, integrations and seller payments can be skipped. No implementation
attempt was started or stopped.

**2026-09-13 — the frame is cut out.** `T-075` builds the three-part skippable setup (name, Stripe, storage) with progress on the Group. What remains here is the basic-details confirmation and the guided first Series after it.

## Notes

R-003's recorded path and working first-Series form remain valid historical
evidence. T-024 is completed work to reuse. The next-sprint creator-home
composition applies after setup and must be designed with this guide, not
implemented as a competing first-run page. Seller setup is prompted before
paid selling if it was skipped or remains incomplete; T-028 owns that rule.

**17 September 2026 — [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-9.** Fresh zero/one-Series home captures still prioritise meter layouts over a Series-shaped beginning or the one real object. The first action itself held up live: Fern's Create Series opens and focuses Title, then saves a private draft with a clear missing-Episode explanation. Do not report first-Series creation as absent. Keep object composition/guidance together in this draft; no competing meter-removal task was created. Upload and the complete ready/share loop were not verified because browser file-chooser tooling failed.

**23 September 2026 — the owner, reading the Kajabi note's blueprint
proposal:** onboarding "is not quite there yet; it needs to be simple,
streamlined, a no-brainer, a couple of clicks." Today a new creator meets
about ten screens before a share link: register, verify, three setup parts,
the first-Series action, the Series form, the Episode form, make ready, the
link. A streamlined shape was put to the owner the same day — one screen
asking what they will share first, with three shapes that create the Series
and its draft Episodes, the Group name defaulted, Stripe and storage asked
only when a price is set or a file chosen. If the owner takes it, this task is
re-scoped to that and the 11 September order (setup first) is superseded by a
decision record.
