---
pass: R-004
date: 2026-09-17
reviewer: Codex
lanes: surface, state, contrast, copy, responsive, keyboard, journey
commit: 6d0c761-dirty
run: docs/design-review/2026-09-16-0337-6d0c761-dirty
status: closed
---

# R-004 — current web interface, with bounded live checks

## Scope

**Lanes run:** [surface](../lanes/surface.md),
[state](../lanes/state.md), [contrast](../lanes/contrast.md),
[copy](../lanes/copy.md), [responsive](../lanes/responsive.md),
[keyboard](../lanes/keyboard.md) and [journey](../lanes/journey.md), with the
limits below. This is a completed review record, **not a release sign-off**.

Surface and state cover the 66-screen inventory at 390px and 1440px, light and
dark. Three intended screens were unavailable: Integrations for owner and
collaborator rendered dependency errors, and New Series validation failed in
the harness. Contrast covers the documented automated palette pairs. Copy is
a targeted reading of public pricing, auth, Series entry, receiving and
certificate wording, supported by terminology/article checks; it is not a
complete language audit.

Responsive checks were driven on the Peer Series page at **360 × 800,
768 × 1024 and 1440 × 900**, plus sign-in and the Peer dashboard at 360px.
Keyboard checks used a visible browser with `document.hidden === false`:
sign-in step focus and manual tab activation, first-Series title focus, and
the mobile sidebar's focus containment, Escape and focus return. Journey
checks cover sign-in-link request feedback, creator home to a private draft,
and an existing Peer's continuation/progress/completion. They do not establish
the complete creator-to-recipient loop.

**Lanes not run, and why:** None wholly omitted. The full responsive, keyboard,
copy and journey matrices were **not completed**. There was no supported,
verified 200% browser-zoom check; no exhaustive keyboard walk in both themes;
no custom-vocabulary render; and no successful upload, vendor-content,
registration/verification or paid-access walkthrough. Equipment and fixture
limits are recorded under Could not see. Listing seven lane names does not
claim seven complete sign-offs.

**Surfaces:** Welcome, pricing, authentication, public Series, creator homes,
Series inventories/details, Peers, billing, settings, setup, receiving,
certificates, unsubscribe confirmation, admin and errors. Existing empty,
one/many, long-title, cap and permission fixtures were inspected. Initial
orientation used the previous contact sheet while capture ran; current
judgements began with the new generated contact sheet and its referenced
images. UI source inspection followed visual observation. Capture tooling,
configuration and planning documents were read before capture.

The standard is `ui-redesign.md`, current terminology rules and accepted
decisions. D-015's email-first sign-in supersedes the earlier tabs-first
proposal. D-016's provider direction is planned work, not evidence that those
connections already work. D-017's destination rules are not reopened. Owner
direction still keeps Series recipients out of creator setup, allows storage,
integrations and seller setup to be skipped, and prompts seller readiness
before paid selling. The next-sprint composition is not treated as already
implemented.

## Evidence

```bash
docker compose up -d
APP_URL=http://localhost:8016 php artisan serve --host=127.0.0.1 --port=8016
APP_URL=http://localhost:8016 php artisan qori:design-review --url=http://localhost:8016
APP_URL=http://localhost:8016 php artisan qori:design-review --url=http://localhost:8016 --no-seed --theme=light
APP_URL=http://localhost:8016 php artisan qori:design-review --url=http://localhost:8016 --no-seed --theme=dark
```

The local PostgreSQL service and an existing Mailpit sink were used. Compose
could not bind a second Mailpit to occupied port 8025; the existing sink was
left intact. Vite at `[::1]:5174` was verified to run from this checkout.
The review server used port 8016; other development servers were left alone.
No database rebuild or `--fresh` was used. Test commands used the separate
`qori_r004_testing` database.

| What                       | Where / result                                                                                                                                                                                                                                                                                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Initial full capture       | `docs/design-review/2026-09-16-0316-6d0c761-dirty/`; exceeded the command's 900-second timeout before final metadata/contact sheet. Not used as the completed run.                                                                                                                                                                                                                                            |
| Completed theme batches    | `docs/design-review/2026-09-16-0337-6d0c761-dirty/`; each command reported **130 captured, 2 failed, 0 redirected**. Four folders contain **260 PNGs**.                                                                                                                                                                                                                                                       |
| Surviving provenance       | `run.json` and `index.html` describe **dark only**, captured at `2026-09-16T03:37:53+00:00`. Both commands started in the same minute and the later finalisation replaced the light metadata. Light PNGs are companion visual evidence backed by the command output, not a surviving per-screen manifest. Neither metadata nor landings were fabricated to conceal this collision.                            |
| Failed screen              | `730-new-series-validation`, both widths in each theme. Its manifest signs in as Rita (`creator`) but asks for Fern's Fresh Start Group; the expected submit selector never appears. This is a fixture/context gap, not proof creation is broken. A later live visit as Fern reached the form and native required-title validation.                                                                           |
| Misleading capture success | `270-integrations`, `710-restricted-integrations`: expected path, but a local **502 debug exception page**, “A service Qori relies on isn't responding right now.” No Integrations composition was reviewed. A path match is insufficient to call a screen healthy.                                                                                                                                           |
| Code at capture            | `main`, `6d0c761bb2ff510133f478d3aa87fb2ed5e2b98f` plus existing uncommitted changes.                                                                                                                                                                                                                                                                                                                         |
| Concurrent commits         | HEAD later became `ffb3c544c415937822eee66035bff4000683b1d9`. The diff against `6d0c761` for `app`, `resources`, `routes` and `lang` was byte-identical to the saved 03:24 UTC diff: SHA-256 `b14e84e95634403d3a7d8ab4e35e5a512660ed9444367a2a49bb8b31344d0cd4`. Those commits did not change the UI implementation being compared. Planning changed concurrently; this was not an atomic clean-tree capture. |
| `composer ci:check`        | **Failed** at planning validation; Pint passed. Six dependency mismatches: T-044, T-089, T-091, T-093, T-095, T-097; storage also names T-044 although it belongs to reachability.                                                                                                                                                                                                                            |
| Focused design checks      | **20 tests, 276 assertions passed**: palette 6/232; terminology/article 14/44.                                                                                                                                                                                                                                                                                                                                |
| Types                      | `composer types:check`: passed, zero PHPStan errors. `npm run types:check`: passed.                                                                                                                                                                                                                                                                                                                           |
| Full PHPUnit               | **780 tests: 778 passed, 2 failed; 3,892 assertions**. Both failures were TaskBoard planning consistency; no other failures were reported.                                                                                                                                                                                                                                                                    |
| `npm run check`            | **Failed** on formatting in T-089, T-091, T-093, T-095, T-097. These checks preceded the review-document edits and are time-bounded evidence, not a clean-tree gate claim.                                                                                                                                                                                                                                    |
| Gate logs                  | `docs/design-review/2026-09-16-0316-6d0c761-dirty/checks/`, including `ci-check.log`, `phpunit-full.log`, `composer-types-check.log`, `npm-types-check.log`, `npm-check.log`, `palette-terminology.log`.                                                                                                                                                                                                      |
| Review-document checks     | Repository formatter passed on the eight edited review documents; required headings, relative links, finding counts and `git diff --check` passed.                                                                                                                                                                                                                                                            |
| Live evidence              | [Walkthrough, 16–17 September](../../walkthroughs.md#16–17-september-2026--r-004-current-web-review). Browser observations and measurements below are independent of headless screenshots.                                                                                                                                                                                                                    |

Images and logs are gitignored. The findings describe the evidence in words so
their argument survives without those files. **Counts: 1 blocker, 11 defects,
1 polish.** The blocker is explicitly limited to the represented local pricing
catalogue; production catalogue contents were not inspected.

## Findings

| #    | Lane              | Severity | Where                                                                                             | Now                                                                                                                                                                                                                                                                                                       | Should be                                                                                                                                                                                                                                | Disposition                                                                                                                                             |
| ---- | ----------------- | -------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F-1  | copy              | blocker  | `020-pricing`, all variants                                                                       | Start advertises **“20 studio logins”** and Pro **“Public listing”**. These sell capabilities contrary to deferred collaborators and the invitation-led product. Post-visual inspection traced the represented benefits to `PricingSeeder`/database rows; this is not evidence of the deployed catalogue. | The catalogue used for review and release must advertise only supported, approved benefits. Validate actual release catalogue data as well as the fixture; do not implement deferred capabilities to make this copy true.                | Existing draft **T-011**, note added. Blocks accepting this represented catalogue, not a claim that production contains these rows.                     |
| F-2  | copy              | defect   | `020-pricing`, all variants                                                                       | Plan prices are **$19/month** and **$49/month** without a currency qualifier. Their captured rows are USD; the Series purchase elsewhere is explicitly **A$89.00**.                                                                                                                                       | Identify USD unambiguously and use the shared money formatter. Whole-price decimal precision is a separate owner decision.                                                                                                               | Existing draft **T-088**, review evidence and recommendation added; broader pricing composition remains outside that task.                              |
| F-3  | surface, journey  | defect   | `020-pricing`, all variants                                                                       | The page ends with three plan cards. It has no sign-up, sign-in, home or plan-selection action, and no linked brand identity. A direct visitor has to use browser navigation to continue.                                                                                                                 | Add the public identity/navigation and a clear **Start sharing** route into the current signup journey; do not imply that clicking a card completes a subscription.                                                                      | Routed to draft **T-104** on 17 September 2026. T-088 expressly excludes this scope.                                                                    |
| F-4  | responsive        | defect   | `030-sign-in` / `725-sign-in-validation` live method states; `410-shared-series`, 360px           | **Log in** and **Email me a sign-in link** are 36px high; the Peer's named **Continue** control is 20px high and **Mark as done** 16px. The brief requires at least 44px touch targets for primary mobile controls.                                                                                       | Give the actual interactive bounds of mobile sign-in, continuation and progress controls at least 44px, retaining clear hierarchy. Do not enlarge only the decoration around a smaller hit target.                                       | Routed to draft **T-105** on 17 September 2026. This is measured live evidence, not an inference from 390px screenshots.                                |
| F-5  | state, responsive | defect   | `725-sign-in-validation`, mobile; live `030-sign-in` second step at 360px                         | The retained address is ellipsised (`rita@design-review.qori.t…` in the capture, `sam@design-review…` live) while **Use a different email** consumes the other half of its row. The domain cannot be checked beside a neutral credential error.                                                           | Display the full address, wrapping if necessary, with the correction action below or otherwise subordinate. Preserve D-015's two steps, Password/Email link choices and neutral errors.                                                  | Routed to draft **T-106** on 17 September 2026, a narrow follow-up to completed T-087; its sign-in composition is not reopened.                         |
| F-6  | state             | defect   | `520-admin-creators`, `530-admin-creator`, both mobile variants                                   | Group names/slugs in the creator list and Series titles in creator detail collapse to a sliver of their first character. Plan, status and counts keep their width, so staff cannot identify the visible rows before opening them.                                                                         | Give identity a readable wrapping first row, or retain a usable identity column in an explicitly scrollable table. Metadata must not consume all name space.                                                                             | Routed to draft **T-107** on 17 September 2026. T-039's creator-facing title work does not cover this.                                                  |
| F-7  | copy              | defect   | `080-series-public-paid`, all variants                                                            | The A$89.00 Series says the email code works as **“Type it here and you're in.”** The approved path still requires payment after verification.                                                                                                                                                            | Say that the code confirms the email and payment then obtains access, naming the price when useful. Keep the free and paid explanations truthful to their different next steps.                                                          | Existing **T-011** note; related remaining **T-027** work also receives the evidence. No payment failure is claimed from a screenshot.                  |
| F-8  | copy              | defect   | `040-register`, `720-register-validation`, all variants                                           | Signup-intent descriptions still say **“Set up a school and publish series”** and **“Take series someone has shared with you.”** They do not use the selected product nouns or receiving language.                                                                                                        | Resolve Group/Series through the terminology layer and describe sharing versus receiving clearly.                                                                                                                                        | Reconfirmed R-001 F-1; routed to draft **T-108** on 17 September 2026. T-048's receiving-home sentence is related but its narrow scope is not expanded. |
| F-9  | state             | defect   | `600-empty-group-dashboard`, `630-one-group-dashboard`                                            | The zero-data page places four zero meters after its creation/naming panels. The one-Series home names the Series in an instruction but does not show the real Series object before the meters.                                                                                                           | Use the Series-shaped beginning and real one-Series identity/action required by the brief; introduce aggregates when they help the current owner act.                                                                                    | Existing **T-026** note; retain R-002 F-3's next-sprint composition disposition. The improved first action is recorded under Held up.                   |
| F-10 | state, copy       | defect   | `400-shared-index`, `615-empty-shared-index`                                                      | The receiving card has a title, four Episodes, joined date and **50%**, but no Group attribution, completed count or named Continue. The empty list says **“Nothing yet”** without explaining how to return to the sender's Series link or check the receiving address.                                   | In the receiving composition, show attribution and **2 of 4 Episodes**, with the known next Episode; give the empty state an honest sender-link/address recovery path. Do not invent a catalogue or route recipients into creator setup. | Existing **T-027** note and R-002 F-5 next-sprint disposition. Rebuild this composition once; no isolated card patch task created.                      |
| F-11 | surface           | defect   | `220-series-index`, `605-empty-series-index`, `635-one-series-index`, Series access form; desktop | New Series fields and the access email field span the inventory panel. Live at 1440px, both Title and the short numeric Hours control measured **934px** wide; the Group form is visibly bounded.                                                                                                         | Define one readable form-interior rule and apply it consistently; size short numeric fields for their content. Keep the existing page/panel alignment.                                                                                   | Existing draft **T-040** note. Its fresh-capture prerequisite is now evidenced; the common-width decision remains open.                                 |
| F-12 | journey, copy     | defect   | `090-certificate` and live certificate reached from `410-shared-series`                           | After Sam marked the remaining Episodes done, a certificate appeared saying **“Harbour Lane Studio marked this series complete for this peer.”** No creator approval occurred in this walk.                                                                                                               | Describe what Qori actually recorded: the Peer marked all Episodes done. Keep the creator's stated-hours attribution and non-accreditation wording; do not imply a separate creator attestation.                                         | Routed to draft **T-109** on 17 September 2026. T-005 owns vocabulary, not a new approval workflow.                                                     |
| F-13 | copy              | polish   | `010-welcome`, both mobile themes                                                                 | The headline still joins **“today.Their”** at the ink/gold transition.                                                                                                                                                                                                                                    | Preserve the sentence break with a visible space or deliberate line break at narrow widths.                                                                                                                                              | **Accepted**, retaining R-002 F-9's decision: fix when the headline is next touched; no standalone task.                                                |

## Held up

- **Sign-in composition and real keyboard behaviour:** the first step asks
  only for email, then focuses Password. Arrow Right moved focus to Email link
  without changing the selected panel; Enter activated it. A visible gold
  focus ring distinguished the focused tab. Passkey remains a labelled
  secondary entry. The submitted email-link request showed a disabled loading
  control, then a dedicated neutral **Check your email** state with the full
  address, resend and correction actions. No account-existence leak is inferred
  from the neutral copy.
- **Brand continuity:** auth and standalone errors now show both mark and
  Qori, resolving the earlier missing-wordmark observation on those captures.
  The warm light/dark treatments remain consistent; admin's distinct palette
  is internally consistent. Measured palette pairs and terminology/article
  tests passed.
- **Creator action:** `210-group-dashboard` and
  `700-restricted-group-dashboard` recommend active **Notes on Being
  Interrupted**, not archived **Workshops We No Longer Run**. Fresh Start's
  **Create Series** action reaches the form and focuses Title. Saving a title
  creates a private draft and explains that an Episode is needed before
  sharing. The empty form's native required-title feedback was observed under
  the correct owner. This does not claim server-validation coverage.
- **Permission and cap states:** `705-restricted-billing` identifies the owner
  boundary and whom to ask. Ada's desktop navigation omits billing.
  `685-capped-series-index` explains read-only status, upgrading and the
  secondary archive alternative; `690-capped-series` explains the disabled
  editing controls. The unavailable Integrations screen is excluded.
- **Long content:** `655-many-series-index` gives identity two lines and puts
  status below it at 390px. `670-long-title-public` retains the full long title
  and form controls. `635-one-series-index` fits a single real row to its
  content. Admin list identity is the separate F-6 failure.
- **Setup composition:** `691-setup-name`, `692-setup-payments` and
  `693-setup-storage` show the three-part sequence, reasons and **Set this up
  later**. Storage says external connections are coming. These are observed
  screens, not proof of provider readiness or a complete post-registration
  walkthrough.
- **Receiving:** public Series pages show their identity, summary, contents
  and free/paid status before the entry form. The form is Series-specific,
  without the generic creator/learner chooser. The Peer Series page names the
  next Episode, uses text for Done, and shows a live time with zone. At 360,
  768 and 1440px it had no page-level horizontal overflow. Progress saved,
  advanced the named next action and eventually exposed a certificate.
- **Mobile navigation:** in the visible browser the sidebar opened with focus
  inside, Shift-Tab wrapped to its last control, Tab wrapped back, and Escape
  removed the dialog and restored focus to Toggle sidebar. This is evidence
  for that drawer, not every dialog or every keyboard control.

## Could not see

- **Surface/state:** Integrations' intended UI, the failed harness validation
  state, hover, real provider/account states, revoked receiving access and
  every long-form error. Headless screenshots cannot establish submission,
  concurrency, dialogs or keyboard behaviour. Only the explicitly described
  live pending states and Episode-open error were observed. The standalone
  error fixtures are rendered templates, not induced live 419/500 failures.
- **Responsive:** 200% actual browser zoom, physical touch, safe areas,
  orientation changes, mobile keyboards, Safari/Firefox and every screen at
  360/768. The tested widths are not substitutes for zoom or real devices.
  The Peer page layout was checked, but fixture audio failed to open; the
  embedded/provider content experience was unavailable.
- **Keyboard:** exhaustive page/tab order in both themes, archive/delete and
  payment dialogs, all menus/popovers, skip links and every accessible name.
  No screen reader, voice or switch input. T-022 remains unfinished; a working
  visible-browser precondition does not complete its acceptance checklist.
- **Contrast/copy:** composited opacity, imagery, embeds, unlisted inline
  colours, colour-vision simulation, all custom nouns, full translation
  inventory, email-client rendering, PDFs and comprehension with real users.
  The new six-digit Series-entry code is implemented by T-073; older email
  planning text calling OTP unbuilt is stale. This pass does not re-audit email.
- **Journey:** direct creator/receiver registration, Series-code verification,
  D-017's full cross-account return matrix, payment/cancellation/delayed
  fulfilment, seller onboarding and actual vendor content delivery. The local
  audio fixture produced a persistent **That didn't open** message, so
  successful consumption is not claimed. Creating a draft succeeded, but the
  browser's file-chooser tooling failed twice (timeout, then stale backend
  element); Episode upload, ready/share and a new recipient loop remain
  unverified. These tool/fixture gaps are not diagnosed as product defects.

The gate is not green, and the complete journey/accessibility matrices remain
open. Neither “no further blocker found” nor this pass's closed status can be
used as permission to release.

## Disposition

`closed` means every observation below has been routed or accepted. It does
not mean fixed. No application fix, new task file or commit was made. Existing
task notes add evidence without changing status, frozen scope or estimates.

| #    | Went to               | Note                                                                                                                           |
| ---- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| F-1  | T-011 note            | Correct represented benefits and verify actual release catalogue.                                                              |
| F-2  | T-088 note            | Currency clarity required; recommend explicit USD and consistent shared formatting. Owner still chooses whole-price precision. |
| F-3  | T-104 (draft)         | Routed 17 September 2026: public identity, navigation and a Start sharing route; after T-088.                                  |
| F-4  | T-105 (draft)         | Routed 17 September 2026: 44px interactive bounds on sign-in, Continue and Mark as done.                                       |
| F-5  | T-106 (draft)         | Routed 17 September 2026: the whole address on the second step; D-015 intact.                                                  |
| F-6  | T-107 (draft)         | Routed 17 September 2026: admin list identity at narrow widths.                                                                |
| F-7  | T-011 and T-027 notes | Paid entry copy must name the payment step.                                                                                    |
| F-8  | T-108 (draft)         | Routed 17 September 2026: registration hints in Qori's nouns; T-048 not broadened.                                             |
| F-9  | T-026 note            | Preserve next-sprint object composition, no duplicate meter-removal task.                                                      |
| F-10 | T-027 note            | Receiving card and no-access recovery belong in the same planned composition.                                                  |
| F-11 | T-040 note            | Fresh 934px measurement removes the stale-evidence concern.                                                                    |
| F-12 | T-109 (draft)         | Routed 17 September 2026: the certificate says the Peer marked every Episode done.                                             |
| F-13 | Accepted              | Existing polish disposition retained.                                                                                          |

**Recommended task priority:** F-1 first; then F-2/F-3 pricing clarity and
onward navigation, F-6 readable admin identities, F-4 primary mobile targets,
F-5 address correction, F-7/F-12 truthful access/completion wording and F-8
registration nouns. F-9/F-10 remain inside the already proposed redesign;
F-11 should use that sprint's one form-width decision. None of these priorities
authorises or creates a task. Resolve the Integrations/capture and complete-loop
evidence gaps before treating this as final release QA.

**Routed by the planning gatekeeper, 17 September 2026.** The six findings left
to owner selection became drafts `T-104` to `T-109` in the `design` stream, in
the priority above; the capture-reliability notes became draft `T-110`. The
Integrations 502 is also a product gap, not only a capture one:
`IntegrationsController::show` reads Stripe on every render, so one vendor's
failure takes down the whole page. That is recorded on `T-044`, which is about
to add storage sections to the same page. No finding was changed.

## Notes

- **Capture reliability needs its own owner-selected work:** run names have
  minute precision, so theme batches can overwrite each other's manifests;
  use distinct `--out` parents for scoped runs until fixed. Preserve partial
  results on timeout. The 900-second limit is now too small for this full
  matrix under the observed dependency delays. No harness code was changed.
- Fix the **730 context**, and record HTTP status/expected-page identity so a
  502 at the right URL cannot count as the Integrations screen. Do not confuse
  a native required-field bubble with application server validation.
- Add settled second-step sign-in, Check your email, Series-code,
  payment-confirming and receiving profile/timezone states to future evidence.
  Use real local dependency fixtures for upload/content so a reviewer can
  finish the loop. These are coverage recommendations, not extra UI findings.
- **Planning hygiene is separate evidence.** The two test failures and five
  formatting failures belong to planning maintenance, not the UI severity
  count. Concurrent storage drafts were left intact.
- **Review-only data changes:** Sam's third and fourth Episode checks were
  toggled on and returned to their prior unchecked values. The newly earned
  certificate/completion stamp intentionally remains sticky under the existing
  contract. Fern retains the private draft **R-004 review — first Series**;
  no Episode upload or sharing was verified. A sign-in-link request went only
  to the local fixture/Mailpit sink. No external invitation, purchase or
  provider connection was made. Subsequent fixture reseeding will replace the
  review worlds as the documented pipeline normally does.
- No product-intent change was proposed for adoption in this pass, so no new
  decision was appended. Form width and whole-price precision remain owner
  decisions in T-040 and T-088. Existing auth, onboarding and provider decisions
  were respected rather than silently redesigned.
