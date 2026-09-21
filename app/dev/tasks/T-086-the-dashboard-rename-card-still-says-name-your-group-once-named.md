---
id: T-086
title: The dashboard rename card still says "Name your Group" once named
stream: onboarding
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-086 — The dashboard rename card still says "Name your Group" once named

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 14 September 2026 from
> three reports that met the same thing: `T-075`, `T-076` and `T-078`.

## Why

`share/Dashboard.vue` renders a `Panel` titled `Name your ${noun('group')}`
whenever the next action is not the naming prompt. After setup has named the
Group the card is the rename control, and its title still asks for a name
that exists: the description already switches on `nameChosen`, the title does
not. Three browser walks in a row reported it, each saying `T-068` left it so
on purpose and that it deserves its own line.

Afterwards, the card's title says what the control does — rename — once a
name has been chosen, and asks for one only before.

## Scope

**In:**

- The title switches on `nameChosen`, the same prop the description reads.
- Both titles come through lang (`groups.name_prompt.label` is the existing
  one; the rename line is new), since the panel's inline English is exactly
  what `T-006` is for and this task should not add to it.
- One case in the dashboard's test asserting the title for each state.

**Out:**

- Moving the card, or the question of whether a named Group's dashboard
  should carry a rename control at all — that is the object hierarchy
  `ui-redesign-next-sprint.md` §2 proposes rebuilding.
- `GroupNameForm`'s Save button reading "Save" where "Continue" would say
  what happens next (`T-068`'s report); that belongs to the setup frame.

## Before this can be ready

- The rename line's wording, from the owner: "Rename your Group" is the
  obvious one and it sits on a page where the noun may be a customer's word,
  so the sentence is authored with `:group` interpolated.
- Whether the description keeps its two branches once the title carries the
  distinction, or collapses to the one sentence that is true in both states.

## Re-scope log

None.

## Notes

`T-075`'s report found it first; `T-076`'s and `T-078`'s repeated it because
nothing had acted on it.
