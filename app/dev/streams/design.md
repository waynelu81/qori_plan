---
stream: design
---

# Stream: design

**Goal.** Finish the approved redesign week, then make the surfaces it did not
cover look like the same product.

**Done when.** Days 4 and 5 of [`../ui-redesign.md`](../ui-redesign.md) pass
their release gate, and no page in the product renders in a palette Qori did
not choose.

**State.** The five-day pass is finished: paper and gold tokens, one shell,
the dashboard's next action, a Series recognisable everywhere, branded error
pages, and a QA pass that turned the palette into a test.

One third of Day 5 is outstanding and cannot be done without a visible browser:
the keyboard and focus pass, `T-022`.

The stream is fed by review findings now rather than by the brief. `R-002`
supplied its current queue.

## Tasks, in order

**The redesign week.**

1. `T-001` — A Series looks like the same Series everywhere (Day 4)
2. `T-002` — Error pages in Qori's own palette (part of Day 5)
3. `T-003` — Mobile and contrast QA pass (Day 5)
4. `T-030` — Long text fields are textareas: the one form control the pass
   found wrong everywhere at once
5. `T-022` — Keyboard and focus pass: waits on a browser that receives key
   events, and its `## Blocked on` says who can supply one

**From review pass `R-002`**, routed 10 September 2026. The pass raised nine
findings, dispositioned every one to owner selection and created no tasks; these
are that selection. Ordered by the pass's own priorities, which put a misleading
instruction above a cosmetic one.

6. `T-033` — The next action never points at an archived Series (F-1)
7. `T-034` — The Payments page stops linking a non-owner to billing (F-2)
8. `T-039` — A Series title keeps its identifying words on a narrow screen (F-4)
9. `T-037` — One heading per settings page, not two (F-7)
10. `T-038` — Auth and error pages get the full lockup (F-8)
11. `T-040` — Series and access form widths (F-6): needs a fresh capture first,
    because `T-030` and `T-031` changed those exact forms during the review
12. `T-066` — Each design-review world has its own owner: the fixture obeys
    the one-Group-per-person rule, and the screenshot run signs in per world

**From `T-058`**, 15 September 2026.

13. `T-088` — The public pricing page uses the one money formatter: the owner
    kept it out of `T-058` on 15 September 2026 until the page has been
    reviewed again, and whether a whole price drops ".00" is decided there

**From review pass `R-004`**, routed 17 September 2026. The pass left six
findings to owner selection and a set of capture-reliability notes; the
planning gatekeeper turned them into drafts, in the pass's own priority. `F-1`
is `T-011`'s in `recovery` and goes first of everything R-004 found; `F-2` is
`T-088` above; `F-7`, `F-9` and `F-10` are notes on `T-011`, `T-026` and
`T-027`; `F-11` is a note on `T-040`.

14. `T-104` — The public pricing page leads somewhere (F-3): a direct visitor
    reaches a dead end after three plan cards; after `T-088`, which edits the
    same page
15. `T-107` — Admin creator lists keep a readable name on a narrow screen
    (F-6): staff cannot tell the rows apart before opening them
16. `T-105` — Primary mobile controls are large enough to touch (F-4): sign-in
    at 36px, Continue at 20px and Mark as done at 16px, measured live
17. `T-106` — The second sign-in step shows the whole address (F-5)
18. `T-109` — The certificate says what Qori recorded (F-12): it claims a
    creator marked the Series complete when the Peer did
19. `T-108` — Registration describes sharing and receiving in Qori's nouns
    (F-8): reconfirms `R-001` F-1, still inline English
20. `T-110` — A design-review run keeps every manifest and never counts an
    error page: the harness overwrote a manifest and counted a 502 as a screen
    in this very pass

`T-035` also came out of that reading, from
[`../ui-components-and-sign-in.md`](../ui-components-and-sign-in.md) rather than
from the pass: positive `tabindex` values on sign-in and register.

**Not turned into tasks, deliberately.**

- **F-3** (empty and one-Series object hierarchy) and **F-5** (attribution and
  continuation on the receiving card) are the subject of
  [`../ui-redesign-next-sprint.md`](../ui-redesign-next-sprint.md) §2, §3 and
  §5, which proposes rebuilding those compositions rather than adjusting them.
  Writing a task against today's layout would specify work the sprint intends to
  replace. They wait for that direction to be settled.
- **F-9** (the welcome headline running together at mobile width) was accepted
  in the pass itself. It is one missing space in `Welcome.vue`, where a `<br>`
  is `hidden sm:inline` with no whitespace before the span, and it belongs to
  whoever next edits that headline.

## Where the work comes from

Two places. The redesign brief's remaining days are the tasks listed above.
Everything after that arrives as a **finding** from a design review pass —
[`../design-review/`](../design-review/) — which is where the product gets
looked at on purpose and where the findings that need code become tasks in this
stream.

## Notes

Day 4's brief says to share the Series' **identity**, not necessarily one whole
card component. Resist a `CourseCover` with `isPublic`, `isPeer` and
`showProgress` flags; three compositions over shared parts is the instruction.
