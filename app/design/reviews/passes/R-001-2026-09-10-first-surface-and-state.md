---
pass: R-001
date: 2026-09-10
reviewer: claude
lanes: surface, state
commit: 561095f
run: docs/design-review/2026-09-10-0249-561095f-dirty
status: open
---

# R-001 — first look at every screen, and at the states a healthy fixture hides

The first pass through the new harness, and the first time the product's empty,
crowded, over-cap and refused states have been looked at as a set rather than
one at a time.

## Scope

**Lanes run:** [surface](../lanes/surface.md), [state](../lanes/state.md).

**Lanes not run, and why:**

- [keyboard](../lanes/keyboard.md) — the run is headless, which is the exact
  condition that lane refuses to work under. Unchanged from `T-003`.
- [responsive](../lanes/responsive.md) — two widths were captured, 390 and 1440. The 360px overflow measurement, 768px and 200% zoom were not run, so
  this lane is **not** covered by the fact that mobile screenshots exist.
- [contrast](../lanes/contrast.md) — `PaletteContrastTest` is green in the gate
  below, which covers the token pairs. The "status never relies on colour alone"
  check was spot-read on a few screens, not walked.
- [copy](../lanes/copy.md) — **not run systematically.** Four of the findings
  below are copy findings that surfaced while reading screenshots for other
  reasons. A real copy pass would find more, and the absence of further copy
  findings here means nothing.
- [journey](../lanes/journey.md) — not walked. F-7 came from a screenshot, not
  from following the loop.

**Surfaces:** everything the harness reaches — 63 screens, which is the whole
product except anything behind an interaction (menus, dialogs, hovers) and the
admin two-factor setup screen.

## Evidence

```bash
php artisan qori:design-review
```

| What           | Where                                                 |
| -------------- | ----------------------------------------------------- |
| Screenshot run | `docs/design-review/2026-09-10-0249-561095f-dirty`    |
| Images         | 252 — 63 screens × 2 widths × 2 themes, none failed   |
| Gate           | `composer ci:check` green, 494 tests, 1981 assertions |

## Findings

| #   | Lane    | Severity | Where                                       | Now                                                                                                                                             | Should be                                                                                                                                                                             | Disposition          |
| --- | ------- | -------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| F-1 | copy    | blocker  | `040-register`                              | The intent chooser reads "Set up a school and publish series." and "Take series someone has shared with you."                                   | No school-coded language, and Series capitalised and resolved through the terminology layer. This is the first screen a stranger reads.                                               | Needs a task         |
| F-2 | surface | defect   | `615-empty-shared-index`, sidebar           | "Shared with me" carries a mortarboard icon. The school vocabulary was retired; the school iconography was not.                                 | An icon that does not encode a classroom.                                                                                                                                             | Needs a task         |
| F-3 | state   | defect   | `720-register-validation`                   | Submitting the form empty produces the browser's own bubble, "Please fill out this field", anchored to the Name field.                          | Qori's inline error, associated with the field. `required` intercepts before the server's copy is ever reached, so the designed error state is unreachable on the commonest failure.  | Needs a task         |
| F-4 | state   | defect   | `600-empty-group-dashboard`                 | A Group with nothing in it still renders four meters reading 0/1, 0, 0/50 and 0/300 beneath the next action.                                    | The next action and the Group, and nothing to measure until there is something to measure. The redesign brief's own diagnosis is that Qori shows meters where it should show objects. | Needs a task         |
| F-5 | copy    | defect   | `600-empty-group-dashboard`                 | Two adjacent tiles read "PEERS — with access right now" and "PEOPLE YOU KNOW — 0/50". Same noun, different meanings, no way to tell them apart. | One label each that says what it counts.                                                                                                                                              | Needs a task         |
| F-6 | copy    | defect   | `685-capped-series-index`                   | Over cap, the page subtitle reads "3 of 1 Series used on your plan".                                                                            | Words, not arithmetic nobody writes. The banner below it already does this correctly.                                                                                                 | Needs a task         |
| F-7 | journey | defect   | `210-group-dashboard`                       | The next action nominates an archived Series: "Workshops We No Longer Run has no Episodes yet".                                                 | Archived Series are out of circulation and cannot be the nominated next action.                                                                                                       | Task already spawned |
| F-8 | surface | polish   | `665-long-title-series`, `400-shared-index` | The Series tile shows the first two letters of the title — "FO", "RS" — which carry no meaning and read as a placeholder somebody forgot.       | Either initials that mean something, or a colour block derived from the Series, or nothing.                                                                                           | Accepted for now     |

## Held up

Worth recording so nobody re-examines them:

- **Long titles.** A 97-character title wraps cleanly on the Series page, the
  index and the public page, at both widths, without pushing the status pill off
  its row.
- **The plan lock.** `685-capped-series-index` leads with "Upgrade to unlock
  them" and offers archiving second, which is what `LocksOverCapSeries` says it
  should do and the opposite of what most products do.
- **The non-owner refusal.** `705-restricted-billing` is a branded 403 saying
  "Only the group owner can change billing" with a resolution and a way back.
  Nothing about it looks like an accident.
- **Dark theme.** Complete on all 63 screens. No inherited zinc, no surface that
  forgot it had a second theme.
- **Error pages.** Same palette and mark as the product, in both themes.

## Could not see

- **Keyboard, focus and dialogs** — headless run.
- **Loading and submitting**, and **server failure** — the app does not hold
  still in either, and the harness does not fake them.
- **768px and 200% zoom**, and any real device.
- **Anything behind an interaction** — the group switcher open, a dropdown, a
  confirmation dialog, a hover state.
- **The email steps of the loop**, which local mail sends to the log.

## Disposition

| #   | Went to                      | Note                                             |
| --- | ---------------------------- | ------------------------------------------------ |
| F-1 | Task needed, `design` stream | Group with F-5 and F-6 — all three are lang keys |
| F-2 | Task needed, `design` stream | One icon                                         |
| F-3 | Task needed, `design` stream | Affects every form carrying `required`           |
| F-4 | Task needed, `design` stream | Touches `ShareDigest` and the dashboard          |
| F-5 | Task needed, `design` stream | With F-1                                         |
| F-6 | Task needed, `design` stream | With F-1                                         |
| F-7 | Spawned already              | Archived Series must not be the next action      |
| F-8 | Accepted                     | Revisit if a Series cover is ever added          |

## Notes

**The harness found its own gaps.** Three things the state lane wants and cannot
photograph: a dialog, a hover state, and the group switcher open. All three need
the capture script to perform a step before shooting, which it can already do —
they are missing from the screen list, not from the tool.

**F-3 is a class, not an instance.** Any form relying on the `required`
attribute has the same problem, and the screenshot only caught it on register
because that is the form this pass happened to submit empty. Whoever takes it
should check the others rather than fixing the one screen named here.

**The copy lane will be the expensive one.** Four copy findings fell out of a
pass that was not looking for them, on four of the sixty-three screens read
closely. That is not a rate anybody should extrapolate calmly.
