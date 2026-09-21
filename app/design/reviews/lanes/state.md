# Lane: state

**Asks.** Does the design hold up when the data is not friendly — nothing yet,
one thing, far too many things, a name longer than the column, a refusal?

**Needs.** Fixtures. This is the lane that cannot run without them, which is why
`DesignReviewSeeder` builds five Groups rather than one.

**Evidence.**

```bash
php artisan qori:design-review --lane=state
```

## The matrix

The interaction contract in [`../ui-redesign.md`](../ui-redesign.md) names nine
states. Six are photographed; three are not, and the honest position is to say
which.

| State                     | Fixture                                           | Captured |
| ------------------------- | ------------------------------------------------- | -------- |
| Empty                     | `fresh-start`, and a Peer with nothing shared     | Yes      |
| One item                  | `solo-practice`                                   | Yes      |
| Enough to wrap or scroll  | `the-long-names-collective` — 12 Series, 24 Peers | Yes      |
| Realistic long content    | The longest title in the same Group               | Yes      |
| Validation failure        | Forms submitted empty or wrong                    | Yes      |
| Permission-restricted     | Ada, an admin who does not own Harbour Lane       | Yes      |
| Plan-locked               | `capped-co` — free plan holding three Series      | Yes      |
| Loading or submitting     | —                                                 | **No**   |
| Server or network failure | —                                                 | **No**   |

## Checks

- **Empty states are object-shaped.** A named thing and one button, not a ghost
  icon and two lines of grey. No jokes, no fake activity, no sample metrics.
- **One item does not look like a mistake.** Layouts built for a list often
  leave a single row floating in a panel sized for six.
- **Long content wraps or truncates deliberately.** A title that overflows its
  card, pushes a status pill off the row, or gets clipped without an ellipsis is
  a finding. So is one truncated so hard it loses its meaning.
- **A refusal explains itself and offers the way out.** §23: what happened, and
  what to do about it. An omitted resolution is a statement that the path is
  final, so a refusal that _does_ have a way out and does not name it is wrong.
- **A plan lock leads with the recoverable action.** Upgrade before delete. A
  product whose first suggestion is _destroy your work_ has picked the wrong
  primary action.
- **No action offered that the current user cannot complete.** This is in the
  release gate, and the permission-restricted fixture is what tests it.

## What it cannot see

- **Loading and submitting.** The app does not hold still in those states, and a
  screenshot that happened to catch a skeleton is not evidence the skeleton has
  the right geometry. Checking this needs a throttled browser and a person.
- **Server and network failure.** Provoking a real 500 means breaking the app on
  purpose. The error _pages_ are captured from their Blade views — see the note
  in `docs/tinker/design-review.md` — but a failure arriving mid-form, next to
  the control that caused it, is not.
- **Concurrency.** Two people editing the same Series is a state nobody has
  designed for yet, and this lane will not discover that on its own.
