# Design review prompt

> The brief given to a designer, or an agent acting as one, when there is a new
> screenshot run to look at. Fill in the lanes and paste it whole.
>
> It is a template for the same reason [`prompt-template.md`](prompt-template.md)
> is: every time somebody reviews from it and something goes wrong that this
> document could have prevented, fix it here. The process it serves is
> [`docs/planning/design-review/`](docs/planning/design-review/); the passes
> written from it are the evidence for changing this.

---

```
Review the current state of Qori's interface and write it up as a pass.

Lanes to run: <LANES — e.g. surface, state, copy>

BEFORE YOU START
1. Read docs/planning/design-review/README.md in full. It defines what a pass
   is, what a finding is, and what happens to one. Follow it exactly.
2. Read the lane file for each lane you are running, under
   docs/planning/design-review/lanes/. Each ends with what it CANNOT see.
   That section is not filler — it is what you are allowed to claim afterwards.
3. Read docs/planning/ui-redesign.md, specifically the product outcomes, the
   interaction/responsive/accessibility contract, the copy section and the
   release gate. That brief is the standard you are reviewing against. You are
   not being asked for your taste.
4. Running the copy lane? Also read docs/planning/terminology-refactor.md and
   the product-nouns rules in CLAUDE.md.
5. Do NOT read the application code yet. Look at the screens first. A reviewer
   who starts in the code explains what they see instead of judging it.

FIND THE RUN
- Newest run:  ls -dt docs/design-review/*/ | head -1
- Open its index.html. That is the contact sheet: every screen, both widths,
  both themes, on one page. Start there, not in the folders.
- Check run.json: it names the commit and branch the run was taken at, and
  lists anything that failed or landed somewhere other than where it was sent.
  A screen that redirected has been photographed, just not the one you think.
- If there is no run, or the newest one is older than the code you mean to
  review, make one:
      docker compose up -d
      php artisan serve --port=8001
      npm run dev
      php artisan qori:design-review
  First time on this machine: npx playwright install chromium
- To see how a screen has changed, open the same path in two runs:
      open docs/design-review/*/desktop-light/600-empty-group-dashboard.png

RULES THAT MATTER
- A finding says WHAT IS TRUE NOW and WHAT SHOULD BE TRUE INSTEAD. Both
  concrete. "This looks unfinished" cannot become a task. "The empty Group
  shows four zero meters where the brief asks for one object and one button"
  can.
- Severity is blocker, defect or polish. Blocker means it contradicts the
  release gate or the interaction contract and somebody is stopped, misled or
  stuck. Defect means the design is wrong but the path still works. Polish
  means worth remembering, not worth a task.
- CITE THE SCREEN BY ITS NAME from the run — `685-capped-series-index`, not
  "the plan-locked page". Names are stable across runs; descriptions are not.
- THE IMAGES ARE GITIGNORED. Whoever reads your pass may not have them, so
  describe the finding in words. Losing the picture must not lose the argument.
- DO NOT FIX ANYTHING. A pass that turns into a working session stops being a
  record of what the design was that day, which is the only thing it is for.
  The one exception is a single-line copy fix in lang/, and write that down too.
- SAY WHAT YOU COULD NOT SEE, per lane. The harness cannot photograph loading,
  submitting, server failure, hover, a dialog, or anything behind an
  interaction. It is headless, so it cannot test keyboard at all. Two widths
  are captured, so mobile screenshots existing is NOT the responsive lane.
- RECORD WHAT HELD UP, not only what is wrong. A pass listing only problems
  reads as a list of everything wrong with the product, and the next reviewer
  cannot tell what has already been checked and is fine.
- DO NOT EXTRAPOLATE FROM A LANE YOU DID NOT RUN. Finding no copy problems
  while running the surface lane is not evidence that the copy is good.
- If the brief itself looks wrong, that is a DECISION, not a finding. Say so
  plainly; it goes to docs/planning/decisions.md and not into a task.

DONE MEANS
- One file: docs/planning/design-review/passes/R-###-YYYY-MM-DD-slug.md,
  copied from docs/planning/design-review/TEMPLATE.md, every heading kept.
- The next free R number. Never reuse or renumber one.
- Front matter filled in, including the run directory and the commit.
- Every finding has a disposition. `status: closed` means every finding has
  one — NOT that every finding is fixed. Those are different, and confusing
  them is how a review becomes the open-ended polish week the brief refuses.

WHEN YOU FINISH
- Commit nothing unless you were told to. Leave changes in the working tree.
- Do not create task files for your findings unless you were asked to. Which
  findings become work is the owner's call.
- Reply with: lanes run; lanes NOT run and why; findings counted by severity;
  what held up; what you could not see; and which findings you think need a
  task, in priority order.
```

---

## Why each rule is here

| Rule                              | Where it comes from                                                                                                                                                                           |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read the lane's "cannot see"      | `T-003` bundled mobile, contrast and keyboard, then could only finish two thirds of it. Its re-scope note is why lanes are split by equipment at all.                                         |
| Headless cannot test keyboard     | A hidden browser renders, screenshots and measures perfectly, and swallows every key event. That has changed what was observable three times in this project.                                 |
| Do not extrapolate                | `R-001` ran surface and state and produced four copy findings anyway, on the handful of screens it read closely. A quiet lane you did not run has told you nothing.                           |
| Describe findings in words        | Evidence is gitignored here, as it is for task reports, so a pass that points at a PNG says nothing to a reader on another machine.                                                           |
| Cite the screen name              | Screen names are stable between runs, which is what makes two passes comparable. `R-001` is readable a month later only because it names `720-register-validation` and not "the signup form". |
| Do not fix during a pass          | The redesign brief's stop condition exists because "one design week" can turn into open-ended polish. A review is the likeliest place for that to start.                                      |
| Record what held up               | Without it the second pass re-examines everything the first one already cleared.                                                                                                              |
| The brief is the standard         | The brief was written after looking at the live surfaces, and it is the agreed answer to "what should this look like". A pass arguing from taste has nothing anyone can act on.               |
| Findings do not become tasks here | Turning a finding into work is a planning decision with product choices inside it. `R-001` left six findings undispatched on purpose.                                                         |
