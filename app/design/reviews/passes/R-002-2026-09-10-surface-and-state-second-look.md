---
pass: R-002
date: 2026-09-10
reviewer: codex
lanes: surface, state
commit: 561095f-dirty
run: docs/design-review/2026-09-10-0300-561095f-dirty
status: closed
---

# R-002 — a second look at the surface and fixture states

The paper, charcoal and gold foundation is coherent. The most consequential
problems concern what the interface directs people to do: an archived Series
becomes the creator's next action, and a non-owner is offered a billing link
that the same run proves they cannot use. Object hierarchy and small-screen
Series identity also fall short of the approved brief.

Closed means every finding below has a disposition. Nothing was fixed, no task
files were created, and no changes were committed.

## Scope

**Lanes run:** [surface](../lanes/surface.md) and
[state](../lanes/state.md), limited to the recorded screens and states. Surface
inspection was followed by a targeted source check of shared tokens, page
containers, forms and heading composition; source-derived evidence is identified
explicitly below.

**Lanes not run, and why:**

- [Responsive](../lanes/responsive.md): the run captures 390px and 1440px.
  There was no resizing, 360px/768px check, 200% zoom, overflow measurement or
  real-device examination. A finding at the captured mobile width is not a
  completed responsive lane.
- [Keyboard](../lanes/keyboard.md): no visible application walkthrough or input
  testing. The saved headless captures cannot establish keyboard operation.
- [Contrast](../lanes/contrast.md): no measured foreground/background, control,
  focus or state-pair audit. Reading token definitions is not a contrast pass.
- [Copy](../lanes/copy.md): no systematic `lang/`, terminology, custom-noun,
  email or PDF copy audit. Observing visible labels does not certify copy.
- [Journey](../lanes/journey.md): no creator/Peer loop, authentication return,
  interaction or payment flow was driven. Cross-screen contradictions below
  are state evidence, not a claim that a journey was walked.

**Surfaces:** all 63 named screens in the supplied contact sheet, all four
variants: welcome, pricing, authentication, public Series/certificate, creator
home/Series/Peers/billing/payments/vocabulary, account settings, receiving views,
unsubscribe, admin, and the empty/one/many/long/locked/restricted/validation/error
fixtures. This is the harness inventory, not every possible product screen.
Screens and states behind interactions remain unexamined.

The standard is the product outcomes, interaction contract, copy section and
release gate in [ui-redesign.md](../../ui-redesign.md). The brand guide supplied
context for the open-Q mark, Instrument Sans and warm palette. Its earlier
classroom positioning and “sharing is caring” line are superseded by the current
brief and recorded decisions; they are not grounds for reversing the redesign.

## Evidence

The existing run was used, not regenerated. The documented capture command is:

```bash
php artisan qori:design-review
```

| What                                  | Where                                                                                                                                                                                                                                                                      |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Screenshot run                        | `docs/design-review/2026-09-10-0300-561095f-dirty`                                                                                                                                                                                                                         |
| Contact sheet                         | `index.html`, read before individual screen inspection                                                                                                                                                                                                                     |
| Manifest                              | `run.json`: captured `2026-09-10T03:00:32+00:00`, branch `main`, commit `561095f-dirty`                                                                                                                                                                                    |
| Capture coverage                      | 63 screens × mobile/light, mobile/dark, desktop/light, desktop/dark = 252 images; zero reported failures or redirects                                                                                                                                                      |
| Viewports                             | Mobile 390 × 844; desktop 1440 × 900 CSS pixels; full-page images may be taller                                                                                                                                                                                            |
| Current checkout                      | Clean at the start: `2b3801df6e6c196c3fb47d3ced20a534dc08fbce`, branch `design-review-harness`                                                                                                                                                                             |
| Freshness at review start             | Git's committed changed-file inventory since `561095f` contains the harness, fixtures, dependencies and review documentation, with no UI file changes. This is the newest available run. Its dirty state is not a reconstructable clean commit; retain that qualification. |
| Concurrent work at final verification | Other working-tree changes appeared during the review, including Series create/edit UI and T-030/T-031. They are outside this captured pass. The supplied run no longer establishes the latest working-tree UI; a new capture is required to review those changes.         |
| Source follow-up                      | `resources/css/app.css`, shared shell primitives, settings layout/pages, Series forms, error layout and layout registration; read after the screens                                                                                                                        |
| Gate                                  | `composer ci:check` **not run**. This documentation-only pass makes no claim about the current release gate and does not reuse R-001's reported result.                                                                                                                    |

The browser refused the local `file:` contact-sheet URL. Its HTML inventory was
read as a local file, and the referenced PNGs were inspected through static
contact-sheet overviews in the same order, then full-size images/crops. The page
was not executed through an alternative browser route. Temporary inspection
images live outside the repository; none is necessary to understand this pass.

In the table below, **all variants** means all four directories named above.
Each screen reference resolves as `<run>/<variant>/<screen>.png`.

## Findings

**9 findings: 2 blockers, 6 defects, 1 polish.**

| #   | Lane    | Severity | Where                                                                                                                                                                                                                                                                                                   | Now                                                                                                                                                                                                                                                                                                                                                                                                             | Should be                                                                                                                                                                                                                                                                                                                     | Disposition                                                                                                                           |
| --- | ------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| F-1 | state   | blocker  | `210-group-dashboard`, `700-restricted-group-dashboard`, compared with `220-series-index`; all variants                                                                                                                                                                                                 | Both owner and admin homes lead with “Workshops We No Longer Run has no Episodes yet” and “Add the first Episode.” The index labels that exact Series **Archived**, while also showing an active draft. The primary instruction therefore presents work on an archived object as the next activation step.                                                                                                      | Exclude archived Series from ordinary activation candidates. Select the eligible active Series and its completing action; if none is eligible, show an honest permitted next step. This is a misleading recommendation under product outcomes 2/4, irrespective of whether clicking it produces a refusal.                    | Recommended for owner task selection in the design stream; no task created.                                                           |
| F-2 | state   | blocker  | `710-restricted-payouts`, compared with `705-restricted-billing` and `700-restricted-group-dashboard`; all variants                                                                                                                                                                                     | Ada's Payments footer offers an underlined **Plan and billing** link. Her billing capture is a 403: “Only the group owner can change billing,” with instructions to ask the owner. Her creator sidebar already omits billing. The footer offers a known permission dead end.                                                                                                                                    | Apply the same role boundary to the footer: show the billing link to owners, and explain who handles billing to non-owners without directing them to a forbidden screen. The release gate forbids actions ending in predictable refusal.                                                                                      | Recommended for owner task selection in the design stream; no task created.                                                           |
| F-3 | state   | defect   | `600-empty-group-dashboard`, `630-one-group-dashboard`; all variants                                                                                                                                                                                                                                    | Fresh Start displays four zero-valued metric tiles after the next-action and rename panels. Solo Practice displays four metric tiles, including a Series count of one, but no Series cover/card; the real Series appears only as a name inside instruction text.                                                                                                                                                | In the empty state, put the permitted create action with a Series-shaped beginning and suppress unhelpful zero meters. With one Series, show that real object's identity and next action before any useful aggregates. These are the brief's explicit object-before-meters requirements.                                      | Recommended for owner task selection in the design stream; related draft T-026 does not establish coverage of this finding.           |
| F-4 | state   | defect   | `240-series-draft`, `665-long-title-series`, `655-many-series-index`; mobile-light and mobile-dark                                                                                                                                                                                                      | The editor keeps the cover and action/status beside the title. “Notes on Being Interrupted” becomes a narrow four-line column; the long fixture title takes eleven lines, with its summary also squeezed. In the index, full-width status labels leave titles such as “Facilitating Difficult …”, “What Nobody Tells Y…” and “Saying No Without B…”. Object identification loses space to status/action chrome. | At the captured narrow width, move the action/status below the title when needed and give the heading/summary the available content width. Let list titles wrap sufficiently to retain identifying words, with status on a separate line when necessary. Verify those changes later at the responsive lane's required widths. | Recommended for owner task selection in the design stream; one task can address the editor and list manifestations of title priority. |
| F-5 | surface | defect   | `400-shared-index`, compared with `410-shared-series`; all variants                                                                                                                                                                                                                                     | The receiving card shows the RS cover, title, four-Episode count, joined date and a bar labelled 50%. It omits Group/sharer attribution, the next Episode and a visible Continue/Start action. The detail page identifies the available continuation as “3. Silence, and what it costs.”                                                                                                                        | Give the receiving card the Day 4 hierarchy: attribution, “2 of 4 Episodes,” and a named continuation action for the next Episode. Preserve the shared cover/title identity. This finding concerns visible information and action hierarchy; the existing card's click behaviour was not tested.                              | Recommended for owner task selection in the design stream; no task created.                                                           |
| F-6 | surface | defect   | `220-series-index`, `230-series-published`, `240-series-draft`; desktop-light and desktop-dark                                                                                                                                                                                                          | New Series fields, including the short numeric Hours field, span almost the entire desktop content panel. The Give someone access email field also spans the panel, unlike the bounded Group-name and account forms.                                                                                                                                                                                            | Constrain these form interiors to the established readable form width while retaining the shared page/panel alignment. Short fields should not inherit a wide inventory panel's entire width. The foundation explicitly says forms must not stretch merely because space exists.                                              | Recommended for owner task selection in the design stream; no task created.                                                           |
| F-7 | surface | defect   | `300-profile`, `310-appearance`, `330-security`; source: `resources/js/layouts/settings/Layout.vue:39`, `resources/js/components/shell/PageHeader.vue:31`, `resources/js/pages/settings/Profile.vue:39`, `resources/js/pages/settings/Appearance.vue:22`, `resources/js/pages/settings/Security.vue:42` | The visible User settings header looks consistent, but source composition supplies its H1 through PageHeader and adds a second, screen-reader-only H1 in each settings page. `resources/js/app.ts:31` registers both layouts for these pages. This is source evidence; the extra heading is invisible in the PNGs.                                                                                              | Retain one logical H1 per rendered settings page and use subordinate headings for its sections. Remove or demote the duplicate heading without losing the specific page context. This enforces the surface lane's type/heading contract, not a claim of keyboard or assistive-technology testing.                             | Recommended for owner task selection in the design stream; no task created.                                                           |
| F-8 | surface | defect   | `030-sign-in`, `040-register`, `050-forgot-password`, `060-reset-password`, `110-verify-email`, `320-confirm-password`, `100-not-found`, `9403-error-403`, `9419-error-419`, `9429-error-429`, `9500-error-500`, `9503-error-503`; all variants                                                         | These authentication and error compositions show the gold mark alone. Welcome and the desktop product shell pair the same mark with the Qori wordmark.                                                                                                                                                                                                                                                          | Use the specified mark-plus-wordmark treatment consistently on auth and errors, preserving the independent error-page rendering. This is the surface lane's explicit logo rule, not a proposal for a new identity or a new public-page header.                                                                                | Recommended for owner task selection in the design stream; lowest-priority defect.                                                    |
| F-9 | surface | polish   | `010-welcome`; mobile-light and mobile-dark                                                                                                                                                                                                                                                             | At the join between the ink and gold headline portions, the captured mobile headline reads “today.Their” without sentence separation. Desktop places the portions on separate lines.                                                                                                                                                                                                                            | Preserve a visible space or intentional line break between the two sentences at narrow widths.                                                                                                                                                                                                                                | Accepted for now: the message remains intelligible; retain for a future welcome typography edit, not a standalone task.               |

## Held up

- **A recognisable foundation:** `010-welcome`, the auth captures, `210-group-dashboard`,
  `260-billing`, `270-payouts`, `300-profile` and the receiving screens use a
  consistent warm light/dark family and gold actions. No starter-kit illustration
  or Laravel promotional links appear in welcome/auth. This is visual evidence,
  not a completed copy or contrast audit.
- **Shared product geometry:** creator home, billing, Payments, Peers and the
  receiving indexes align titles and content panels. The source follow-up confirms
  shared PageBody/PageHeader/Panel use and semantic light/dark definitions in
  `app.css`. Standalone error CSS is explicitly documented as duplicated for
  failure independence; its existence is not an unexplained second shell.
- **Series recognition across audiences:** the RS cover and “Reading a Room
  Before You Speak” title agree in `220-series-index`, `070-series-public-free`,
  `400-shared-index` and `410-shared-series`. The public free/paid pages show
  summary, price and actual contents without creator editing controls. Rename
  stability of that identity was not demonstrated.
- **Empty and one-row Series containers:** `605-empty-series-index` uses a
  cover-shaped placeholder with an explicit future-object message and the create
  form immediately below it. `635-one-series-index` fits its single row instead
  of reserving a list panel for several nonexistent objects.
- **Recovery takes priority at the cap:** `680-capped-group-dashboard`,
  `685-capped-series-index` and `690-capped-series` identify read-only state.
  The index/editor promote upgrading before archiving; the create form is
  replaced by a plan explanation, and editor submit controls appear subdued.
  These observations do not prove disabled-control behaviour or upgrade success.
- **The photographed billing refusal explains itself:** `705-restricted-billing`
  names the owner as the person who can act and provides a return control.
  `700-restricted-group-dashboard` omits the owner-only billing navigation item.
  F-2 identifies the inconsistent footer, not a failure of this refusal message.
- **Some long-content compositions work:** `670-long-title-public` preserves
  the complete title, price and access control at 390px in both themes. Desktop
  `655-many-series-index` retains readable names and statuses. This does not
  excuse the separate mobile Series failures in F-4.
- **A captured inline error:** `725-sign-in-validation` retains the form and
  displays the credential error below Email. Only that photographed failure
  treatment is verified.
- **Admin is intentionally distinct:** `500-admin-sign-in` through
  `560-admin-pricing` retain the staff-labelled slate console. Its different
  palette is the brief's allowed exception, not an unfinished product theme.

## Could not see

- **Surface limits:** menus, hover/pressed states, open dialogs/sheets,
  interaction focus and rendering outside captured Chromium. The source checks
  are targeted, not an exhaustive audit of every component or semantic landmark.
  The surface lane establishes consistency against the brief, not general proof
  that the design is good.
- **State limits:** loading, submitting, mid-form server/network failure,
  double-submit behaviour, post-save advancement and concurrent editing. Static
  `9403`/`9419`/`9429`/`9500`/`9503` fixtures are rendered error views with no
  landed route; they do not reproduce failures arriving during a task.
- **Validation coverage:** `720-register-validation` and
  `730-new-series-validation` show Chromium's required-field bubble. They do
  not establish application/server validation, persistence after dismissal,
  error-summary behaviour or programmatic field association. No conclusion
  about those unseen states is drawn from the fixture names.
- **Incomplete state matrix:** no paused-Group capture; no combined non-owner
  and over-cap fixture; no completed receiving-index/record capture; no
  unavailable/revoked Episode, signed-in public access alternatives, or admin
  two-factor setup/challenge capture. `090-certificate` does not substitute for
  the completed Peer journey.
- **Unrun lanes:** actual navigation and authentication return paths, playback,
  billing/payment submission, keyboard and focus, touch target sizes, required
  responsive widths/zoom, contrast ratios, reduced motion, custom terminology,
  email and PDF output. This pass is not release sign-off.

## Disposition

The owner requested one pass file and no task creation. Findings needing code
are therefore handed to the owner here for selection into the
[design stream](../../streams/design.md); this routing is complete even though
the work has not been authorised, scheduled or implemented.

| #   | Went to                           | Note                                                                                                                                                                                                                                        |
| --- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F-1 | Owner task selection — priority 1 | Fix the misleading archived-Series recommendation. R-001 F-7 noted it; that pass names no task ID, and current task files do not establish existing coverage. Do not treat it as already assigned.                                          |
| F-2 | Owner task selection — priority 2 | Remove the non-owner's known billing dead end.                                                                                                                                                                                              |
| F-3 | Owner task selection — priority 3 | Restore the empty/one-Series object hierarchy. R-001 F-4 overlaps the zero-meter observation. T-026 is a related draft onboarding proposal, not a verified task for this finding.                                                           |
| F-4 | Owner task selection — priority 4 | Restore title priority in narrow Series headers and rows; include later responsive verification.                                                                                                                                            |
| F-5 | Owner task selection — priority 5 | Put attribution and continuation on the receiving card.                                                                                                                                                                                     |
| F-6 | Owner task selection — priority 6 | Bring Series/access form widths into the existing form rhythm. Concurrent T-030/T-031 change the Series forms; their scopes do not explicitly cover this width issue. Recheck a fresh capture before specifying work against the new forms. |
| F-7 | Owner task selection — priority 7 | Correct duplicate settings H1 composition. The separate blocked T-022 keyboard task does not make this source finding fixed or verified.                                                                                                    |
| F-8 | Owner task selection — priority 8 | Align auth/error lockups with the explicit logo rule.                                                                                                                                                                                       |
| F-9 | Accepted in this pass             | Legible despite the missing separation; revisit during a future welcome edit. No standalone task recommended.                                                                                                                               |

## Notes

- **No new product-intent decision proposed.** Findings apply the current brief.
  A future change to the brief's identity or activation rules would belong in
  `decisions.md` before becoming implementation work. Nothing was added there.
- R-001 was read after independent screenshot judgement. Its older `0249` run
  is not present here, so this pass does not claim visual improvement/regression
  against that run. In particular, its statement that long titles held up is
  not supported by this run's mobile evidence in F-4. R-001 remains unchanged.
- R-001's copy findings are not reassessed or closed by this pass. Archive
  controls are visible, and T-009 is recorded done; the brief's conditional ban
  on promising an unavailable archive is not evidence that today's archive is
  unimplemented. Its behaviour was not tested here.
- Improve fixture coverage by capturing application validation separately from
  native constraint bubbles, an archived Series detail page, a paused Group,
  the combined non-owner/over-cap state and completed/unavailable receiving
  states. These are review-equipment recommendations, not created tasks.
- The state-lane document says six states are photographed but lists seven
  captured categories. Report the categories actually observed, including the
  validation qualification, rather than inheriting that count.
- This reviewer modified no application, translation, task, prior pass or brand asset.
  Final verification detected independent work, including T-030 (textarea/count)
  and T-031 (Series editing), both marked done. Those changes were left untouched
  and were not retrospectively treated as part of the 03:00 snapshot. Findings
  describe the supplied capture; they must not be presented as verification of
  the concurrently revised interface.
  No full quality gate or browser interaction test was run for this record.
