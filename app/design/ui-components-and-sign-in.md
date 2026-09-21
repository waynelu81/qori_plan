# UI components and a coherent sign-in screen

Recorded 2026-09-10. Recommendation report for the next redesign sprint.

[Planning index](README.md) · [Next sprint direction](ui-redesign-next-sprint.md) ·
[Interface pass R-002](design-review/passes/R-002-2026-09-10-surface-and-state-second-look.md)

**Planning follow-up, 2026-09-11:**
[T-036](tasks/T-036-one-sign-in-composition.md) now specifies this composition:
Password / Email link in the chooser, passkey retained as a quiet secondary
entry, and manual tab activation. These placement and activation choices were
not settled in the original recommendation below. Its tabindex instruction is
superseded by completed [T-035](tasks/T-035-remove-positive-tabindex-from-the-auth-forms.md).
The neutral response already renders and the endpoint is already throttled;
the dedicated confirmation is a presentation upgrade. Read the
[handoff lessons](ui-recommendation-handoff.md) before planning further work
from this report. Task files and the design stream hold the execution scope.

## Recommendation

Keep Qori's existing Vue, Tailwind, Reka UI and locally owned shadcn-style
components. The largest gains come from composing those foundations around
Series identity, the current action and complete form states. No additional
general-purpose UI framework is recommended.

For login, make **Password** and **Email link** clearly visible choices in one
sign-in composition with one email field. The owner explicitly confirmed that
both methods should remain available. App-based QR login belongs in a later
extension when the app and approval flow exist.

## What the login screen does today

The `030-sign-in` capture and current `resources/js/pages/auth/Login.vue` show:

1. A heading describing email-and-password login.
2. A passkey button, followed by “Or continue with email.”
3. Email, password, remember-me and the main login button.
4. The registration prompt, which visually ends the sign-in form.
5. Another divider, another email field and an outlined magic-link button.

This explains why magic link feels attached afterwards. It appears below the
registration exit, repeats information already requested, has weaker emphasis,
and receives no support from the heading. The passkey button adds another
prominent method outside the owner's requested password/link choices.

`PasskeyVerify.vue` is already connected to `@laravel/passkeys`; it is a separate
authentication method, not Qori-app QR login. Recommend removing its prominence
from the main chooser. Any removal of existing passkey access needs an explicit
product decision and a recovery path for existing users; no passkey functionality
was changed or disabled during this review.

## Proposed sign-in composition

> **Revised 13 September 2026 (`T-077`).** Built as proposed by `T-036`, then
> reordered on the owner's review: the email field comes first and the
> Password / Email link choice sits under it, in one form whose action
> follows the choice. Passkey stays below the composition as its own entry.
> The rest of this section is the original proposal.
>
> **Revised 15 September 2026 (`T-087`).** The address now has a step of its
> own: the email field and Next, then the address with a way back to change
> it, the Password / Email link choice and the chosen method's controls. Next
> asks the server nothing, so the first step reveals nothing about who is
> registered. Passkey stays below both steps.

- A consistent Qori lockup and a neutral heading such as **Welcome back**.
- One labelled segmented choice: **Password / Email link**. Both stay visible.
- One **Email address** field whose value survives method switches.
- In Password mode: password/reveal, password recovery, the existing remember-me
  choice and one gold **Sign in** button.
- In Email link mode: a short explanation that no password is needed and one
  gold **Email me a sign-in link** button. Hide and exclude password controls
  from this request.
- Put **Create an account** after the whole sign-in composition, in one place.

Keep Password as the initial selection for continuity with the existing screen;
this is a design recommendation, not an owner decision about the default.
“Email link” is the user-facing option label; “magic link” need not be exposed
as terminology people must understand.

Use one shared visual frame and email value while keeping the two server
operations, processing states and errors correctly scoped. A shared composition
does not require nested forms or posting both methods' fields together. Preserve
the existing password/2FA flow and intended Series destination.

### Give the link request a complete next state

After a successful request response, replace the form body with **Check your
email**, the address entered, and the existing neutral response: “If that email
has an account, a sign-in link is on its way.” Do not claim that an account was
found or that delivery has already succeeded.

Provide **Use a different email**, **Send another link**, and a way back to
Password. Keep these recovery choices secondary to the instruction to check
the inbox. Resend availability must follow server throttling rather than an
invented client-only allowance. Preserve the email during method changes and
recoverable failures. Keep errors and progress beside the active task; use the
same semantic status colours as the rest of Qori.

Specify loading, request failure, validation, rate limit, expired/used link and
successful return behaviour before implementation. Any visible expiry duration
must come from the actual server setting. Verify destination preservation when
the link is opened in another browser/device; the existing session-based intended
redirect alone does not establish that behaviour.

### Reserve QR for the app phase

When available, add one explicit **Use the Qori app** entry within this same
sign-in frame. Its content should explain scan, approve in the app, then continue
on the web, and cover waiting, expiration, refresh, cancellation and success.
Avoid another permanently stacked form. Leave the entry absent until usable;
do not ship a disabled placeholder on the current sign-in screen.

A QR rendering component only draws the code. It does not provide a secure
browser-to-app approval flow. That later feature needs a short-lived challenge
bound to the requesting browser and explicit approval on the authenticated app;
do not substitute a reusable login credential or a QR containing a magic-link
bearer URL for that flow. Detailed protocol work is outside this design report.

## Packages and primitives to reuse or add

Package capabilities were checked against the primary documentation on
2026-09-10. Local versions below are dependency ranges from `package.json`, not
claims about the exact installed lockfile version.

| Recommendation                                             | Existing or new                                                                                                       | Why it fits Qori                                                                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Reka UI Tabs**, styled as a compact method selector      | `reka-ui` already declared at `^2.9.8`; add a local Tabs wrapper, absent from the current UI directory                | Provides the tab semantics and keyboard behaviour for selecting a method. Keep styling in Qori's tokens and check the complete composition. [Official Tabs documentation](https://www.reka-ui.com/docs/components/tabs)                                                                                                                                                         |
| **Existing Dialog / Sheet and Collapsible wrappers**       | Already present; no new runtime dependency                                                                            | Use a focused create surface when appropriate and a quiet disclosure for secondary management. Retain direct entry from the primary CTA, sensible mobile geometry, focus return and visible errors. Reka documents dialog keyboard/focus handling. [Dialog](https://www.reka-ui.com/docs/components/dialog), [Collapsible](https://www.reka-ui.com/docs/components/collapsible) |
| **A Qori field composition**, informed by shadcn-vue Field | Build around current Label, Input, PasswordInput, InputError and TextareaField, or selectively adopt the Field source | Standardise label/help/error spacing, IDs, `aria-describedby`, invalid state and width. The upstream Field family includes description and error parts; validate the resulting associations instead of assuming the wrapper establishes them automatically. [Field documentation](https://www.shadcn-vue.com/docs/components/field)                                             |
| **Inertia Form / useForm**                                 | `@inertiajs/vue3` already declared at `^3.0.0`                                                                        | Retain the existing server-validation model and use its processing/error/success state to finish the UI. A second form-state framework is unnecessary for these forms. [Forms documentation](https://inertiajs.com/docs/v3/the-basics/forms)                                                                                                                                    |
| **qrcode.vue 3.x**, later only                             | Optional new runtime dependency when app QR login is ready                                                            | Vue 3 support and SVG/canvas output make it a reasonable QR renderer. Prefer a clear, high-contrast code with adequate quiet space; decorative gradients/logo overlays add no value to login. It supplies rendering, not authentication. [Maintainer repository](https://github.com/scopewu/qrcode.vue)                                                                         |

Continue using the existing Lucide icons, VueUse utilities and Sonner toasts.
Toasts can acknowledge incidental success; a sent-link instruction or recoverable
form error needs a persistent place in the active composition.

No new package is necessary for the immediate login redesign. The QR renderer
is the only additional runtime package shortlisted here, and its adoption is
deferred. A new design-system library, animation library, carousel or chart
library would not address the observed hierarchy problems.

## Product components worth creating or evolving

These names describe responsibilities for planning; they are not frozen file
names or implementation instructions.

| Component responsibility                             | Recommendation                                                                                                          | Improvement                                                                                                                |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Auth frame + sign-in choice + link-request state** | Evolve AuthSimpleLayout; compose a method chooser and a focused link-status view                                        | Makes Password and Email link equal members of the same flow, with shared identity and one registration exit               |
| **Series identity**                                  | Evolve SeriesCover; share title/cover/attribution primitives across separate creator, receiving and public compositions | Gives Series visible presence without one universal card full of audience flags; retain immutable identity through renames |
| **Creator activation and receiving continuation**    | Compose Series identity with the existing NextAction and SeriesProgress responsibilities                                | Connects the action to the actual object: what needs work for creators, where to resume for Peers                          |
| **Series-shaped empty state**                        | Evolve EmptyState for this object where needed                                                                          | Makes zero content an intentional starting point in the future object's space; only show permitted actions                 |
| **Field and form feedback**                          | Unify repeated field composition and persistent action feedback                                                         | Consistent errors, help, labels, progress, width and success that advances the task                                        |
| **Compact management disclosure**                    | Compose existing Collapsible/Dialog/Sheet where a named secondary task warrants it                                      | Keeps Group naming and secondary editing reachable without permanently expanding every form                                |

The current working tree already contains `TextareaField.vue` and
`series/SeriesForm.vue` from T-030/T-031, including a bounded edit-form width.
Build on that work. Do not create competing textarea or Series-edit components
from the earlier screenshot inventory.

## Suggested order and validation

1. Settle the sign-in composition and complete the link-request states.
2. Establish field/feedback rules through these forms, then apply them to the
   affected Series surfaces.
3. Strengthen Series identity and creator/receiving compositions from the next
   sprint report, using existing dialog/disclosure primitives as needed.
4. Add the app QR entry and renderer only with its working approval flow.

Before shipping login changes, verify both methods, email retention, scoped
errors, submission state, password-manager behaviour, keyboard/focus order,
required mobile widths, both themes, 2FA, expired/used links and intended return.
Replace the current manually numbered positive `tabindex` values with a logical
DOM order during implementation. This report does not certify those behaviours.

## Scope and evidence

Reviewed the existing `030-sign-in` mobile image and prior four-variant review,
current Login/AuthSimpleLayout/PasskeyVerify code, MagicLinkLoginController and
auth language, local UI inventory, and the new textarea/Series form components.
The auth-flow document contains stale architecture notes; current code was used
for the behaviour described here.

A separate interactive concept demonstrates the shared email field, method
switching and link-request confirmation using local simulated actions. It sends
no email, performs no authentication and is not application code. It uses a
wordmark-only header to focus the comparison on method layout; production should
retain the specified complete Qori lockup. It is not a reviewed production UI.

The concept's method switch, retained email, confirmation and return to Password
were exercised locally; the dark-theme layout was inspected at 360px and 736px.
This does not constitute responsive, contrast or keyboard sign-off for Qori.

No dependencies were installed, no authentication behaviour was changed, no
implementation tasks were created, and nothing was committed for this report.
