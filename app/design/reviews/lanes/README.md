# Lanes

A lane is one question about the design, paired with the equipment needed to
answer it. See [`../README.md`](../README.md) for how a pass uses them.

| Lane                        | Asks                                                      | Needs                          |
| --------------------------- | --------------------------------------------------------- | ------------------------------ |
| [surface](surface.md)       | Does every screen look like the same product?             | A renderer                     |
| [state](state.md)           | Does it hold up when the data is not friendly?            | Fixtures, a renderer           |
| [responsive](responsive.md) | Does it work at the widths people actually use?           | A resizable renderer           |
| [contrast](contrast.md)     | Can it be read, in both themes?                           | The stylesheet                 |
| [keyboard](keyboard.md)     | Can it be operated without a mouse?                       | A **visible** browser          |
| [copy](copy.md)             | Does it say true things, in Qori's words?                 | `lang/`, the terminology layer |
| [journey](journey.md)       | Can a person get through the loop without being stranded? | A driveable browser, fixtures  |

**Split by equipment, not by screen.** `T-003` bundled mobile, contrast and
keyboard into one task and could only finish two thirds of it, because the third
needed an input device the session did not have. Its report is where this
structure comes from.

Each lane says what it checks, what it can see, and — the section that matters —
**what it cannot see**. A lane that reports a clean pass over something it was
never able to look at is worse than no lane.

## Where the checks come from

Almost nothing here is invented. The interaction, responsive and accessibility
contract in [`../ui-redesign.md`](../ui-redesign.md) is the source, along with
the product outcomes and release gate in the same file, the terminology rules in
[`../terminology-refactor.md`](../terminology-refactor.md), and §23's rules on
error copy. Where a lane adds a check of its own, it says so.
