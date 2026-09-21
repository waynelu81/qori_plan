---
id: T-086
title: The dashboard rename card still says "Name your Group" once named
stream: onboarding
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-086 — The dashboard rename card still says "Name your Group" once named

## Why

`share/Dashboard.vue` rendered a `Panel` titled `Name your ${noun('group')}`
whenever the next action was not the naming prompt. After setup has named the
Group the card is the rename control, and its title still asked for a name
that exists: the description switched on `nameChosen`, the title did not.
Three browser walks in a row reported it, and the 21 September 2026 walk a
fourth time (`fixups.md`). Afterwards, the card's title says what the control
does — rename — once a name has been chosen, and asks for one only before.

## Decisions taken to make this specifiable

- **"Rename your :group"** once a name is chosen — the draft's obvious line,
  with the noun interpolated because it may be a customer's word. The owner
  can change the words.
- **The description keeps its two branches.** Before a name is chosen it says
  the name is Qori's made-up one (`groups.name_prompt.detail`, which names it);
  after, it says where the name appears. Both are true, and the first is the
  reason to act.
- **Both come from lang through the controller**, so the card's inline English
  goes, as `T-006` asks of every page.

## Preconditions

None.

**Data this task verifies against:** a clean database for the test; the
design-review world's `harbour-lane-studio` for the walk.

**Equipment:** a browser.

## Scope

**In:**

- The card's title and description from lang, switching on whether a name has
  been chosen.

**Out:**

- Moving the card, or whether a named Group's dashboard should carry a rename
  control at all — the object hierarchy `ui-redesign-next-sprint.md` §2
  proposes rebuilding.
- `GroupNameForm`'s Save button reading "Save" where "Continue" would say
  what happens next (`T-068`'s report); that belongs to the setup frame.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Http/Controllers/Share/DashboardController.php` | edit | `nameCard` |
| `resources/js/pages/share/Dashboard.vue` | edit | reads it |
| `lang/en/groups.php` | edit | `rename.title`, `rename.detail` |
| `tests/Feature/Share/OnboardingHomeTest.php` | edit | one case |

Flows: none — the card's words move to lang; no call chain changes.

## Database

None.

## Code

`DashboardController::show()` sends `nameCard: {title, description}`.

## Copy

| Key | File | English |
| --- | --- | --- |
| `rename.title` | `lang/en/groups.php` | "Rename your :group" |
| `rename.detail` | `lang/en/groups.php` | "Your :peer_plural see this name in every invitation and on every page you share." |

## Routes

None.

## Tests

**Changed: `tests/Feature/Share/OnboardingHomeTest.php` — 1 new case**

1. `test_the_name_card_asks_for_a_name_then_offers_a_rename`

## Acceptance

- [x] A named Group's dashboard card is titled "Rename your :group"; an
      unnamed one's asks for a name
- [x] The card's words come from lang
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

None.
