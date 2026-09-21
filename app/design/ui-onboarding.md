# Onboarding by entry purpose

Updated 2026-09-11 following the owner's clarification after
[R-003](design-review/passes/R-003-2026-09-11-registration-and-first-run.md).
The review remains the record of what was observed; this document describes the
new target, not behaviour already built.

**Status:** owner-confirmed journey direction, with implementation details still
in draft. This supersedes the earlier recommendation to take creators directly
to the first-Series checklist. The owner wants profile and creator setup first,
then guided creation. Storage, integrations **and seller payment setup can be
skipped**. Seller setup is prompted again before selling a paid Series.

**2026-09-13:** the owner walked a fresh registration and met no onboarding at
all. The first slice, naming the Group before anything else, is `T-068`;
`T-026` keeps the guided first Series. Integrations are a settings page now
(`T-067`), which is where the skippable stages will point.

[Decision record](decisions.md#onboarding-follows-the-entry-purpose-2026-09-11) ·
[Onboarding stream](streams/onboarding.md) · [Planning process](PROCESS.md)

## Two entry paths

| Entry purpose                                           | Ordered journey                                                                                                                                                                     | Excluded from this journey                                                              |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Receive a specific Series, including a link sent by EDM | Register/sign in → confirm name, email and personal timezone → verification when required → payment for a paid Series or free access → open that same Series                        | Group creation, creator setup, storage, integrations and seller payment setup           |
| Create and sell/share Series                            | Register/sign in → basic profile → advanced/Group details including timezone → storage, skippable → integrations, skippable → seller payment setup, skippable → guided first Series | Buyer checkout and any requirement to connect optional services before creating a draft |

The receiving path is determined by the known Series destination, including an
EDM link. Do not ask that person to choose Share or Learn when their purpose is
already established. Direct registration without a Series may retain the
explicit creator/receiving choice. These are journey choices, not permission
roles: one account can create and receive, and neither a campaign parameter nor
a signup selection grants content access or changes permissions.

An existing creator following an EDM link uses the receiving path for that
Series. An existing receiving user who explicitly chooses **Start sharing**
starts creator setup. Preserve the account and its confirmed details in both
cases; do not create a duplicate account or repeat completed profile work.

## Receiving a Series through an EDM or shared link

Keep the Series title and source visible throughout account confirmation and
checkout so the person knows what they are joining. Preserve the Series identity
through registration, verification, profile/email correction, checkout, provider
return, interruption and resumption. A generic dashboard is not the completion
of this journey.

1. **Register or sign in in the Series context.** New receiving users do not
   get a creator Group. Existing accounts sign in normally. Prefill known
   account details; do not overwrite identity from an email-link parameter.
2. **Confirm basic details.** Show name, email and personal timezone. Reuse what
   registration or the existing account already supplied rather than requesting
   it again in empty fields. Suggest the device timezone and ask the person to
   confirm/save it. Preserve the destination through required email verification
   and the existing confirmation process for changing an email address.
3. **Resolve access before payment.** If the person already has valid access,
   open the Series without another purchase. If it is free, use the existing
   explicit access action and applicable consent. A link click alone does not
   establish access.
4. **For a paid Series, show its price and enter buyer checkout.** This is the
   purchase of the selected Series, not a Qori subscription and not seller
   payout setup. Payment completion must come from the confirmed server state.
5. **Open the same Series once access is granted.** Show Start or Continue as
   appropriate. Keep the Series context during cancellation, refusal, payment
   failure or a delay between payment and access fulfilment.

Specify a payment-confirmation state for a browser that returns before the
webhook grants access. Keep the Series identity visible, explain that access is
being confirmed, and provide a safe status/recovery action. Do not send the
person to a permission-denied page or invite a second payment while the first
is pending. Cancellation returns to that Series's purchase step with their
profile retained. Unavailable Series or a refusal before payment explains the
real limitation; it must not silently switch to creator onboarding.

For someone who registers to receive without a Series link, use the same basic
profile confirmation, then an honest receiving welcome explaining how to open
the sender's link. There is no catalogue or compulsory creator setup. An
established receiving home may retain a secondary Start sharing route; the
Series-linked onboarding itself should contain no creator diversion.

## Creator setup, then guided creation

Use a consistent staged setup frame with visible progress, Back, retained values
and explicit Skip for the three optional stages. Recommended composition:

| Stage                      | Details and completion                                                                                                                      | Reuse or new work                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Basic details              | Confirm name and email; show verification/correction feedback in context                                                                    | Existing identity and email-change behaviour; new onboarding presentation/return handling |
| Advanced and Group details | Confirm personal timezone, Group name and Group scheduling timezone; suggest the personal zone for the Group and make the distinction clear | Existing timezone fields, validation and Group-name controls                              |
| Storage                    | Explain the available storage choices and connect a supported account, or **Skip for now**                                                  | Qori file storage already works; external account connection flows need implementation    |
| Integrations               | Offer only usable connections relevant to Series content, or **Skip for now**                                                               | Provider enums/adapters exist; a usable account-connection flow is not yet established    |
| Seller payment setup       | Explain getting paid, offer the existing seller onboarding flow, or **Skip for now**                                                        | Existing Payments/Connect flow, with new return/resume handling and readiness integration |
| First Series guide         | Create a Series → add its first Episode → make it ready → share it                                                                          | Existing Series actions, with new guided presentation and saved progress                  |

Timezone is a required confirmation in the proposed setup, not a request to
rebuild timezone storage. Personal timezone controls the person's displayed
schedule; Group timezone controls the Group's schedule. Do not treat a silently
inherited zone as explicit confirmation. Do not add biography, organisation
size or other advanced questions without a demonstrated use in this flow.

Skipping an optional stage records **skipped**, not connected or ready, and
continues to the next stage. The person can return to it through the appropriate
setup/settings entry. When no provider can actually be connected, explain that
briefly and allow continuation; do not ship a collection of dead Connect
buttons. Choosing Skip must not depend on building those connectors first.

**Seller setup is optional during onboarding.** If skipped or incomplete,
creating a draft and sharing free Series remain available. Before paid selling
is enabled, prompt the owner to complete seller setup and then resume the paid
Series action. An account ID or return from the payment provider is not proof
of selling readiness; use the authoritative capability status. Treat a pending
review, abandoned provider visit and provider failure as separate visible
states with a way to continue later. Nobody without selling authority gets a
setup action they cannot complete.

After setup, show a Series-shaped beginning with the single next action,
**Create a new Series**, using the existing minimal form. The real draft
replaces the empty object; its next action opens the Episode form. Name/timezone
setup has already been handled, so the guide should not restart that sequence.
Paid-selling requirements still take priority when relevant, and plan or
permission restrictions still outrank encouragement.

## Progress, completion and interruption

Distinguish three records of progress: the person's profile confirmation, the
creator's Group setup, and the first-Series guide. A recipient's purchase/access
journey belongs to the selected Series, not to creator setup completion.

Save completed stages, skipped optional stages and current destination on the
server so provider redirects and later sessions can resume appropriately.
**Setup complete** means required details are confirmed and each optional stage
is completed or explicitly skipped. It does not mean the person has connected
every service, can sell, or has shared a Series. Seller readiness is checked
again at the paid action regardless of the setup-complete state.

For the first-Series guide, derive steps from saved work for one tracked Series,
not visits or unrelated Series. Recommend permanent graduation after the first
successful share, so later archive/delete does not restart onboarding. Keep
unfinished guidance resumable and secondary to the actual Series. The ready
specification must name the storage, completion predicates and behaviour if the
tracked draft is removed before graduation.

## Existing capabilities and actual gaps

The R-003 browser walk confirmed direct registration, verification from local
logged mail, first-Series creation and the lost Series-return path. The following
additional capability checks are source evidence, not a new payment walkthrough:

- Profile and personal timezone update endpoints exist, but return to Profile;
  onboarding-specific continuation is new work.
- Free access and hosted paid checkout exist. The public page already avoids
  offering purchase to someone with access. Keep those server checks on resume.
- Signed paid checkout events grant access idempotently. Current checkout
  cancellation returns to the shared index; success goes directly to shared
  content, which can refuse a return before access is granted. Contextual
  cancelled/pending/confirmed states are work to specify and validate.
- Seller Payments supports starting, resuming and inspecting connected-account
  onboarding. Its return goes to Group home; the new sequence needs to resume
  at the correct setup stage. Checkout's current account-exists check is not a
  complete seller-readiness gate.
- Qori uploads need no external account connection. The Connection model and
  Dropbox/Vimeo media resolvers do not supply storage/integration account setup.
  No routed OAuth/account-connection flow was found in this source check.
- T-024 timezone capture and T-029 live-session scheduling are done. Consistent
  use of saved timezones across all dates remains T-025.

## Task ownership and readiness

- **T-008:** preserve the intended Series through verification and its related
  account-confirmation detours.
- **T-026:** creator setup frame, required details, persisted setup progress and
  the subsequent first-Series guide. Coordinate the object composition with the
  next redesign sprint.
- **T-027:** receiving onboarding for both Series-link and direct entry,
  profile confirmation, checkout/access continuation and recovery. This is
  broader than its former empty-state-only draft.
- **T-028:** the skippable storage/integration/seller-payment stages and seller
  readiness prompt before paid selling. Separate real connector implementation
  from the setup frame; do not assume provider support because a model names it.

These drafts have changed scope following the owner's decision. Re-estimate
and split them into bounded implementation slices before marking them ready;
no ready spec or historical pass is being rewritten. A shared setup frame may
be reused, but a receiving journey must not depend on completing creator setup.
Keep filenames and task IDs stable while updating their titles and generated
board. Literal files, APIs, copy keys, completion records, dependency boundaries
and tests still belong in those ready specifications.

Validate both intents and both account states; EDM/shared-link context with an
existing creator account; confirmed versus missing profile details; email
correction; verification before and after attempting access; free, paid and
already-accessible Series; cancellation; delayed or failed fulfilment; abandoned
and resumed setup; every Skip; seller readiness before charging; and restored
first-Series guidance. Match server tests to provisioning/payment invariants,
and browser tests to rendered state, retained input and focus. Required widths,
both themes and keyboard remain release checks.

No new checkout or seller onboarding was executed for this planning revision.
No application changes or package installations were made.
