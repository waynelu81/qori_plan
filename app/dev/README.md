# Qori planning index

Three kinds of document live here, and mixing them is what made the original
`PLAN.md` unreadable.

**Execution** — what to build, who has it, and exactly how:

| File                                     | Use it for                                                  |
| ---------------------------------------- | ----------------------------------------------------------- |
| [`../PLAN.md`](../PLAN.md)               | Intent, current state, release gates                        |
| [`PROCESS.md`](PROCESS.md)               | How planning works: lifecycle, specs, re-scoping            |
| `bin/tasks`                              | Every task and its status — rendered locally, not committed |
| [`streams/`](streams/)                   | Why each line of work exists, and in what order             |
| [`journeys/`](journeys/)                 | What a person meets end to end — happy path, then branches  |
| [`fixups.md`](fixups.md)                 | Small slips fixed in passing, never tasks                   |
| [`tasks/`](tasks/)                       | One file per task                                           |
| [`tasks/TEMPLATE.md`](tasks/TEMPLATE.md) | The shape a task must have to be `ready`                    |
| [`../design/reviews/`](../design/reviews/) | Looking at what is already built, and what to do about it   |

**Reference** — settled decisions and preserved research. Read the relevant
section, not the file; several are long.

| File                                                                                         | Use it for                                                                                                                                                      |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`decisions.md`](decisions.md)                                                               | Settled product and architecture decisions, with rationale                                                                                                      |
| [`status-history.md`](status-history.md)                                                     | Recorded product state and completed work                                                                                                                       |
| [`risk-register.md`](risk-register.md)                                                       | Current risk register and architecture-review findings                                                                                                          |
| [`../design/ui-redesign.md`](../design/ui-redesign.md)                                                           | Approved UI/UX redesign brief and acceptance criteria                                                                                                           |
| [`../design/ui-redesign-next-sprint.md`](../design/ui-redesign-next-sprint.md)                                   | Proposed next sprint: stronger Series identity, composition and task hierarchy                                                                                  |
| [`../design/ui-components-and-sign-in.md`](../design/ui-components-and-sign-in.md)                               | Component/package recommendations and the Password / Email link sign-in proposal                                                                                |
| [`../design/ui-recommendation-handoff.md`](../design/ui-recommendation-handoff.md)                               | Lessons for future UI/UX recommendations: decisions, current evidence and scope                                                                                 |
| [`../design/ui-onboarding.md`](../design/ui-onboarding.md)                                                       | Owner-confirmed receiving purchase flow and creator setup before guided creation                                                                                |
| [`course-classroom.md`](course-classroom.md)                                                 | The merged course-classroom proposal: the story, the two proposals compared, the live-session lifecycle, spike questions, acceptance scenarios and vendor facts |
| [`../design/ui-system-email.md`](../design/ui-system-email.md)                                                   | Proposed email family: branding, layout, security, orders, fulfilment and unsubscribe                                                                           |
| [`terminology-refactor.md`](terminology-refactor.md)                                         | Default product language, higher-tier custom labels and implementation phases                                                                                   |
| [`product-and-pricing.md`](product-and-pricing.md)                                           | Pro proposition, catalogue debate, storage and connector economics                                                                                              |
| [`pricing-and-competitor-review-2026-09-11.md`](pricing-and-competitor-review-2026-09-11.md) | Official-source competitor prices, current entitlements, feature gaps and proposed packaging                                                                    |
| [`email-and-delivery.md`](email-and-delivery.md)                                             | Email economics and the SES broadcast build specification                                                                                                       |
| [`integrations-and-onboarding.md`](integrations-and-onboarding.md)                           | Integration IA and onboarding research                                                                                                                          |
| [`communications-policy.md`](communications-policy.md)                                       | Consent, reminders, upsell and workspace timezone                                                                                                               |
| [`operations-and-observability.md`](operations-and-observability.md)                         | Queue, scheduler, activity log, Sentry and error contracts                                                                                                      |
| [`billing-and-plan-behaviour.md`](billing-and-plan-behaviour.md)                             | Downgrade rules, plan caps, paid fulfilment and refunds                                                                                                         |
| [`reporting-social-and-flags.md`](reporting-social-and-flags.md)                             | Reporting, social-feature fit and stored-flag audit                                                                                                             |
| [`release-prerequisites.md`](release-prerequisites.md)                                       | Domain, Stripe, email, Vimeo and queue inputs requiring the owner                                                                                               |
| [`vendor-accounts.md`](vendor-accounts.md)                                                   | What to open, sign up for and pay for per storage and live-session vendor, and how Qori gets developer access                                                   |
| [`reachability.md`](reachability.md)                                                         | The hand-walked inventory of what is built and reachable from nothing, and what the command can see                                                             |
| [`engineering-runbook.md`](engineering-runbook.md)                                           | Environment traps, commands and agent workflow                                                                                                                  |
| [`walkthroughs.md`](walkthroughs.md)                                                         | Real browser walkthrough evidence and open UX findings                                                                                                          |
| [`archive/PLAN-2026-09-08.md`](archive/PLAN-2026-09-08.md)                                   | Byte-for-byte copy of the former living plan                                                                                                                    |

## Where a thing goes

| It is…                                  | It goes in…                       |
| --------------------------------------- | --------------------------------- |
| What to build next, in detail           | a task file                       |
| Why a body of work exists               | a stream file                     |
| A choice made, and why                  | `decisions.md`                    |
| Something seen in a browser             | `walkthroughs.md`                 |
| A design looked at on purpose           | a pass in `design-review/passes/` |
| Work finished, in narrative             | `status-history.md`               |
| An operator command or a recurring trap | `engineering-runbook.md`          |
| Deep research                           | the relevant topic file           |
| Product specification                   | `../project-plan.md`              |

Rules that hold across all of them:

- `PLAN.md` is authoritative for intent and release state. Under 150 lines.
- The board is rendered, not committed. Change a task file and run `php artisan qori:tasks`.
- A settled choice goes in `decisions.md` **with its reasoning**, so a later
  reader can tell whether the reason still holds.
- Do not silently rewrite the archive.

Some preserved notes describe an earlier state and may be contradicted by later entries. The date and evidence remain valuable; the current root plan wins when there is a conflict.
