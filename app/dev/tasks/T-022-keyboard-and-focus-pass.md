---
id: T-022
title: Keyboard and focus pass
stream: design
status: blocked
owner: unassigned
estimate: M
depends: T-003
blocks: none
---

# T-022 — Keyboard and focus pass

> **Blocked on the environment, not on us.** Split out of `T-003` on
> 9 September 2026 — see that task's Re-scope log. Nothing about it is
> undecided; it needs a browser that receives key events.

## Why

`T-003` covered the mobile and contrast thirds of the redesign's QA pass and
could not cover the keyboard third. The pane it ran in was hidden, and
`document.hidden === true` means key events do not reach the document and CSS
animations do not run — so tab order and focus rings could not be observed at
all, and dialog dismissal could only be observed halfway (Escape sets
`data-state="closed"`; the unmount and focus restore are gated on an
`animationend` that never fires).

Nothing here is speculative. Every control in the product is reachable by mouse
and none of it has been driven by a keyboard.

## Scope

**In:**

- Tab order on every product page: sensible, and no traps.
- A visible focus indicator on every interactive element, in both themes.
- Escape closes every dialog, sheet, dropdown and popover, and returns focus to
  whatever opened it.
- The mobile sidebar drawer: opens, traps focus while open, closes, restores.

**Out:**

- Screen-reader testing. A different discipline and a different task.
- Automated accessibility tooling — same reasoning as `T-003`.
- Anything visual that is not focus. `T-003` covered it.

## Preconditions

**A browser window that is actually visible and receives key events.** Verify
before starting:

```js
document.hidden === false;
```

If that is `true`, stop — every observation this task makes will be wrong in
the same direction, silently. This is the third time a hidden pane has changed
what was observable in this project; the first cost two broken implementations
of `useDeepLinkedControl` before anyone noticed.

## Blocked on

What: a browser session that is visible and receives key events — the agent
panes used so far render hidden, and a hidden pane never delivers `Tab`.

Who: wayne, by running the pass in a browser on the desk, or by giving an
agent a visible one. Nobody else can supply this.

## Files

Unknown until the pass runs — that is the nature of it. The likely candidates,
from where the interactive elements are:

| Path                                     | Change | Notes                       |
| ---------------------------------------- | ------ | --------------------------- |
| `resources/js/components/ui/**`          | edit   | Where focus styles live     |
| `resources/js/components/AppSidebar.vue` | edit   | The drawer                  |
| `resources/css/app.css`                  | edit   | If a focus token is missing |

## Database

None.

## Code

None specified. This is a verification pass; the fixes are whatever it finds.
Apply `T-003`'s rule: fix anything under roughly ten minutes, spawn the rest.

## Copy

None.

## Routes

None.

## Tests

There is no JavaScript test runner, so none of this can be regression-tested.
Say so in the report. The one durable artefact available is a written record of
what was checked, in `walkthroughs.md`.

If the pass finds that a focus indicator is missing because a _token_ is
missing rather than because a component forgot it, that part is testable —
`PaletteContrastTest` already asserts `ring` against its grounds and can be
extended.

## Acceptance

- [ ] `document.hidden === false` confirmed before starting
- [ ] Tab order walked on every product page, both themes
- [ ] Every interactive element shows a visible focus indicator
- [ ] Every dialog, sheet, dropdown and popover closes on Escape and returns
      focus to its trigger
- [ ] The mobile drawer traps focus while open and restores it on close
- [ ] Findings under ten minutes fixed; the rest spawned
- [ ] `composer ci:check` green from a clean tree
- [ ] Report written in `reports/`

## Re-scope log

None.

## Notes

`T-003` verified as far as it could: Escape reaches Reka and sets
`data-state="closed"` on the archive dialog. What is unknown is everything
after that.

**17 September 2026 — bounded evidence from [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md).** A visible Codex browser did report `document.hidden === false` and receive real key events. Sign-in moved focus to Password after Next; arrow focus alone did not activate Email link, Enter did, and its gold focus ring was visible. The 360px mobile sidebar focused inside, wrapped backwards/forwards, and Escape removed it and returned focus to Toggle sidebar. Create Series focused Title. These are partial checks recorded in walkthroughs.md, not this task's exhaustive both-theme page/dialog pass. No status or acceptance checkbox is changed; the historical claim that an agent cannot obtain a visible browser now has this counterexample for the next reviewer.
