# UI/UX recommendations that can be planned

Recorded 2026-09-11 after reading the owner's planning feedback, T-035 through
T-040, the T-035 completion report, and the design stream alongside the original
recommendations. This records lessons for future design work; it does not revise
R-002, change a ready task or certify the current interface.

[Planning process](PROCESS.md) · [Review protocol](design-review/README.md) ·
[Component proposal](ui-components-and-sign-in.md) · [Design stream](streams/design.md)

## Resolve the composition, and identify whose decision it is

The owner confirmed **Password / Email link**. My report recommended reducing
passkey prominence but left its placement unresolved. [T-036](tasks/T-036-one-sign-in-composition.md)
supplied the missing recommendation: preserve passkey as a quiet, labelled
secondary entry below the composition, outside the two-choice control.

Next time, show where every existing entry belongs and state any material
assumption explicitly, with the reason and what would change if overruled.
Distinguish an owner decision from a designer recommendation. Do not make an
unanswered secondary question hold up a reversible recommendation when the
confirmed direction supports a concrete choice. Apply a restriction only to the
action it governs: moving an entry does not remove the authentication method.

## Separate existing behaviour, proposed work and regression checks

Before handoff, reconcile the screenshot baseline with current source and
completed task reports. Keep the historical observation intact, but describe
the remaining work against the current baseline.

| Baseline identified in this planning round                                                              | Actual remaining work                                                                         |
| ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| The neutral sent-link response already renders as a banner                                              | Upgrade its presentation to a dedicated next state and reuse the response                     |
| The link-request endpoint already has throttling                                                        | Present that refusal and recovery coherently; retain regression coverage                      |
| [T-035](tasks/T-035-remove-positive-tabindex-from-the-auth-forms.md) removed positive `tabindex` values | Preserve natural ordering and verify the new composition; do not estimate the deletions again |

An existing capability can still need verification after a UI change. Calling
it a regression check prevents that work being mistaken for a missing feature.
The independent tabindex defect also deserved an explicit disposition rather
than being buried in the future redesign's validation list.

## Specify behaviour alongside the package or component

“Use Reka Tabs” left an interaction decision to the planner. T-036 chooses
manual activation for this method selector: arrows move focus; explicit
activation selects the method. That is a choice for this interaction, not a
universal rule that automatic tabs are inaccessible.

A component recommendation should name what is already installed, what local
wrapper is needed, which defaults affect the task, and the intended behaviour.
For sign-in that includes retained email, separate submissions and error scopes,
focus after a transition, and password-manager behaviour. Check library
capabilities against primary documentation and the local version; a library's
accessibility support does not establish the accessibility of our composition.

A list of states is not yet a state design. Before calling the handoff ready,
describe the visible feedback, enabled actions, retained input and recovery for
each relevant state. “Submitting”, “failed” and “rate limited” alone leave those
decisions to implementation. Separate presentation changes from existing server
behaviour, including expired or used links.

## Refresh stale evidence and measure shared rules once

[T-040](tasks/T-040-series-form-widths-after-a-fresh-capture.md) correctly remains
a draft. T-030/T-031 changed the forms photographed in R-002, so that run cannot
establish the remaining width defect. A fresh capture is a prerequisite to
specifying the change, not a verification step postponed until afterwards.

“Readable width” also needs an explicit, measured rule. Compare the relevant
forms, choose and document the shared token or class and any justified
field-specific variation. Matching another form “in spirit” is not a reason for
a particular width. Preserve the distinction between panel alignment, form
interior width and the space a short individual field needs.

## Plan against the next composition and retain every disposition

Read the stream and proposed sprint before recommending isolated fixes.
R-002 F-3 and F-5 wait for the proposed creator and receiving compositions;
patching the old hierarchy first would risk work the sprint replaces. F-9 is
accepted polish. Those are deliberate outcomes, not forgotten findings.

The [design stream](streams/design.md) records selected work and omissions.
Use that record instead of creating a competing queue. Prioritise misleading or
blocked paths, then concrete usability defects; judge small independent fixes
on their value and likely survival through the redesign. A future sprint does
not automatically postpone every fix. Owner selection still determines which
findings become tasks.

## Make the verification match the claim

The [T-035 report](tasks/reports/T-035-2026-09-10-claude.md) distinguishes deleting
provably wrong attributes from observing the resulting keyboard order. Carry
that distinction into every recommendation: source inspection, server tests,
rendered evidence and interaction checks establish different properties.

Test plans must also follow component boundaries. T-036 proposes putting the
email field in `SignInMethods.vue` but counting fields in `Login.vue`; that
source assertion needs reconciliation with the planned composition. A source
count cannot prove the rendered field count or retained email. Likewise, a
390px screenshot cannot certify the responsive lane. Record unavailable checks
plainly and use the planning process to resolve specification mismatches.

## Use this at the next handoff

Keep the recommendation concise, but make these facts easy to find: the current
evidence and its date; the problem and intended outcome; existing versus new
work; settled decisions and explicit recommendations; behaviour and states;
task overlap and deliberate deferrals; and how each claim will be verified.
Use the existing task template when implementation planning is requested. Do
not label a direction as ready while composition decisions or stale evidence
still determine what will be built.
