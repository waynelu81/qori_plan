# Qori system email design

Updated 2026-09-13. **Status: proposed design specification**, requested by the
owner. This defines the composition and content contract; it does not claim
these designs, new message types or preference controls are implemented.

[Planning index](README.md) · [Brand guide](../brand/guidelines/qori-brand-guidelines.md) ·
[Delivery stream](streams/delivery.md) · [Communications policy](communications-policy.md)

## What has actually been reviewed

The previous interface passes did **not** review email appearance in an inbox.
R-001 could not see email steps; R-002 included the `900-unsubscribed` **web page**
and excluded email copy; R-003 followed a locally generated verification link
without auditing the message design. Those passes remain unchanged.

[T-016's report](tasks/reports/T-016-2026-09-11-claude.md) separately records six
transactional messages arriving and rendering in local Mailpit. It checked
subjects, translation keys and placeholders. It did not establish client
compatibility, link correctness or production arrival. The mail-check command's
“every link resolves” conclusion exceeds its implemented content checks.

For this specification, current templates were rendered from the notifications
at commit `b7313a5fa4293a7257007cbf7d862e6cf410ea93`, using synthetic unsaved
models and harmless `example.test` URLs. No mail was sent, accounts created or
payments made. Local Mailpit was not reachable from this session. Browser inspection of these
renders is template evidence, not Gmail, Outlook or Apple Mail evidence.

**Current appearance:** Laravel's default Markdown shell: a linked text “Qori”
header, 570px white card, grey surrounding page, black action button, generic
greeting/sign-off, URL fallback and copyright footer. No Qori logo image or
banner is installed. The existing purchase-related message confirms access;
it has no financial summary. This is a functional starting point, not yet a
defined Qori email family.

### Existing and proposed messages

| Message                         | What exists now                                                                   | Design treatment                                                              |
| ------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Email verification              | Registration/resend notification; no separate welcome email                       | Security layout; verify action; explain actual expiry                         |
| Password reset                  | Fortify notification; currently 60-minute expiry                                  | Security layout; reset action                                                 |
| Email sign-in link              | Existing notification; 15 minutes, single use                                     | Security layout; sign-in action, visually equal to password recovery          |
| Confirm new email               | Sent to the pending address; 60 minutes                                           | Security layout; identify the address being confirmed                         |
| Email changed alert             | Sent to the previous address after the change                                     | Security alert; explain change and give a working recovery contact            |
| Series access                   | Sent to an existing User when access is granted/restored; paid/free copy variants | Access layout; exact Series, Group and destination                            |
| Campaign / EDM                  | Separate broadcast notification with creator content                              | Promotional layout; identified sender and explicit unsubscribe footer         |
| Emailed OTP                     | **Not built**; the present six-digit challenge is authenticator-app TOTP          | Future security variant, only if emailed codes become a product feature       |
| Order confirmation / receipt    | **No Qori implementation**; external receipt settings were not inspected          | New purchase composition; requires purchase data and notification ownership   |
| Paid fulfilment pending / ready | Access-ready overlaps existing access mail; no pending/failure buyer message      | Distinct states; never claim access is ready merely because payment succeeded |

Invitation mail for somebody without an account is also different from access
mail to an existing User. It belongs with draft T-043; upcoming live reminders
are excluded from T-029. Neither is evidence of a currently working email.

## Chosen composition

**Use the Qori logo at the top, not a banner.** Keep one left-aligned reading
column and one primary action. Security and purchase mail should feel like a
clear message from the product the person just used. Identity comes from the
wordmark, colour, typography and named Series, not a large illustration.

| Element             | Specification                                                                                                                    |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Envelope            | 600px maximum outer content width; fluid at smaller widths; centred in the inbox                                                 |
| Outer space         | 24px above/below, 16px side gutters; no horizontal scrolling at a 320px viewport                                                 |
| Inner space         | 32px padding; 20px at 480px and below. Desktop text area: 536px. At a 320px viewport: approximately 248px                        |
| Header              | Full Qori lockup, 120px wide with original aspect ratio (about 46px high); aligned with body text; 24px before the heading       |
| Background          | Paper `#FAF8F5`; content `#FFFDF8`; ink `#231F1A`; secondary text `#6E665E`; dividers `#DED6CB`                                  |
| Action              | Gold `#98661B` with Paper text; 48px minimum height, 20px horizontal padding, 10px radius; full available width on small screens |
| Body                | Arial, Helvetica, sans-serif; 16px / 24px; normal weight                                                                         |
| Heading             | 24px / 32px, bold; one H1 naming the event or action                                                                             |
| Supporting heading  | 18px / 26px, bold; only where content needs a subsection                                                                         |
| Footer and metadata | 14px / 20px; readable contrast; links visibly underlined                                                                         |
| Rhythm              | 16px between paragraphs; 24px between sections; 8px between related label/value lines                                            |
| Shape               | Quiet 12px outer radius; no shadow required; square-corner fallback is acceptable                                                |

600px is an explicit Qori design choice consistent with established email
template practice, not a universal client limit. [Mailchimp template widths](https://mailchimp.com/help/about-template-widths/)

Use the checked brand-kit gold for this email palette. The web application's
HSL tokens have since been adjusted; don't silently translate them into a
different email gold on each template. A future palette alignment changes the
shared email theme once and repeats contrast checks.

### Branding and images

- Use `brand/logos/qori-logo-primary-1200.png` as the source for a small,
  optimised production PNG, at least twice the displayed resolution. Preserve
  the full lockup and safe area. Do not embed the app icon in place of the name.
- Production image URLs must be stable HTTPS assets on Qori's owned asset
  host, without an expiring access signature. Set width, height and `alt="Qori"`.
  The sender name and message text still identify Qori when images are blocked.
- Instrument Sans is appropriate in the application; email must look finished
  with the fallback font alone. Do not make a web-font download necessary.
- No slogan, hero banner, social icons or navigation menu in security,
  confirmation or access mail. The existing 1600×640 website banner is not an
  email header asset.
- For access/purchase messages, the Series title and actual Group name supply
  object identity. An existing Series thumbnail is optional, below the message
  heading, never required to understand the purchase. No invented cover or
  generic decorative placeholder is required for v1.
- A future EDM may contain one relevant content image after its headline. It
  must not push sender identity, the purpose or unsubscribe out of the design.

### Dark appearance

Use warm charcoal `#211E19`, content `#2B2721`, text `#F8F2E8` and action
`#F0B85A` with charcoal text where the client supports deliberate dark styling.
Keep the primary logo on a small Paper backing so it remains legible without
depending on an image swap. The fallback is the complete light design.

Clients may ignore or transform styles. Inline essential colours and geometry;
use media queries as an enhancement. Gmail supports a documented subset of CSS,
which is not evidence for Outlook or other clients. Browser light/dark previews
show design intent only. [Gmail CSS support](https://developers.google.com/workspace/gmail/design/css)

## Shared content order

1. Useful subject and short preheader, both describing the real event. No OTP,
   reset token or sensitive account-change details in the subject/preheader.
2. Qori header, then the event heading. Omit the default “Hello!” heading;
   an optional “Hi {first name},” belongs in the body and disappears cleanly
   if the name is unknown.
3. One or two sentences explaining why this person received this message.
4. The code, Series identity or purchase facts required for this message.
5. One primary action, if one is useful and its destination exists.
6. Expiry, security or fulfilment guidance near that action.
7. A wrapping, selectable fallback URL for action-link messages.
8. The appropriate footer.

Remove generic “Regards, Qori” repetition when the header/footer already names
the sender. Do not remove useful expiry or fallback copy just to make a short
email look cleaner. No animations, embedded forms, JavaScript, copy-code button
or fake progress indicator in delivered email.

### Security family: proposed copy and distinctions

| Type                | Subject / heading                                                        | Body and primary action                                                                                                                                                                                                             |
| ------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Verify email        | “Verify your Qori email address” / “Confirm your email address”          | “Confirm this email address to continue with Qori.” **Verify email address**. Include expiry from the signed-link configuration and “If you didn't create a Qori account, you can ignore this email.”                               |
| Password reset      | “Reset your Qori password” / “Reset your password”                       | “Use the button below to choose a new password for your Qori account.” **Reset password**. “This link expires in :minutes minutes. If you didn't request a password reset, you can ignore this email.”                              |
| Email sign-in link  | “Your Qori sign-in link” / “Your sign-in link”                           | “Use this link to sign in to Qori.” **Sign in to Qori**. “This link can be used once and expires in :minutes minutes. If you didn't request it, you can ignore this email.”                                                         |
| Confirm new address | “Confirm your new Qori email address” / “Confirm your new email address” | “Confirm :email as the new email address for your Qori account.” **Confirm email address**. Explain expiry and that ignoring the request keeps the current address                                                                  |
| Address changed     | “Your Qori email address changed” / “Your email address changed”         | “Your Qori account email address was changed to :email.” Show the real change time, if supplied. “If you didn't make this change, contact Qori support.” Link only to an established monitored route                                |
| OTP, future         | “Your Qori sign-in code” / “Your sign-in code”                           | “Enter this code on the Qori sign-in screen.” One selectable plain-text code, 32px / 40px monospace with modest letter spacing. “This code expires in :minutes minutes. Don't share it with anyone.” No primary button is necessary |

The OTP preview's digits and ten-minute expiry are **illustrative**, not new
authentication policy. Code length, expiry, retry and replacement behaviour
must come from the eventual authentication implementation. Do not replace app
TOTP or introduce a third login choice as part of branding these messages.

The existing old-address alert asks the recipient to reply immediately. No
notification-specific Reply-To was found. Before shipping the revised alert,
name and verify the recovery owner and monitored destination. Do not publish
an invented support address or imply that a reply is monitored when it is not.

For a receiving user, verification and sign-in links must retain the validated
intended Series destination. Returning from email must continue that receiving
journey, not start creator setup. Account-wide security mail uses Qori branding;
it must not accidentally adopt the user's most recently selected Group.

## Purchase and fulfilment family

An order confirmation answers **“Was I charged, for what, and by whom?”**
Fulfilment answers **“Can I open what I paid for?”** Access confirmation for a
free invitation answers neither financial question. Keep the distinctions in
the send trigger as well as the heading.

| State                                       | Heading and content                                                                                                                                                                     | Primary action                                                                                                                  |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Payment confirmed, access ready immediately | “Payment confirmed. Your :series is ready.” Exact title, Group/seller and order summary                                                                                                 | **Open :series** → exact receiving destination                                                                                  |
| Payment confirmed, access still pending     | “Payment confirmed. Access is being prepared.” Same order facts; “You don't need to pay again.” State that Qori will email when access is ready only once that follow-up is implemented | **View order status**, only when a durable status destination exists; otherwise factual message and established support contact |
| Previously pending access now ready         | “Your :series is ready.” Title, Group and original order reference; no second receipt or repeated charge implication                                                                    | **Open :series**                                                                                                                |
| Free grant or access restoration            | “You now have access to :title.” “Shared by :name” and Group identity. Restoration may include previously paid access; it is not a new purchase                                         | **Open :series**; no new “payment confirmed” label or zero-dollar receipt                                                       |
| Payment attempt unsuccessful                | Do not send confirmation or ready copy. Any future failure message states the real payment status and safe recovery                                                                     | Determined by the payment flow; no speculative “try paying again” after a confirmed payment                                     |

**Recommended send policy:** when payment and access complete together, send one
combined confirmation with the purchase facts and opening action. If access
is pending, send a factual payment confirmation, then one access-ready message
when fulfilment completes. Deduplicate by the durable purchase/event, including
webhook retries and reconciliation. This is proposed orchestration, not
behaviour the current `SeriesAccessNotification` already implements.

Before an order task becomes ready, specify the canonical purchase reference,
amount/currency/date source, merchant identity, receipt issuer, notification
trigger and retry/deduplication ownership. Confirm whether Stripe already sends
a seller receipt; avoid two competing “official receipts.” The Qori platform
subscription invoice in the billing portal is not the buyer's Series receipt.

### Order facts and tables

The purchase summary contains: reference; paid date with explicit timezone;
seller; full Series title; currency; item amount; applicable discount/tax from
the actual transaction; and total paid. Show payment method last four digits
only when supplied and useful. Never infer a tax amount or call the email a
“tax invoice” without the required seller/transaction data and agreed ownership.

Use a **two-column item / amount table**, with the title wrapping on the left
and numbers aligned on the right. Put quantity, unit price or access details on
additional lines beneath the title when needed. Do not squeeze an admin-style
five-column table into an email.

Example data, not an actual purchase:

| Item                                               |        Amount |
| -------------------------------------------------- | ------------: |
| Puppy Basics: Calm walks and confident first steps |     AUD 49.00 |
| Subtotal                                           |     AUD 49.00 |
| **Total paid**                                     | **AUD 49.00** |

- Use 16px type, at least 12px vertical cell padding and subtle horizontal
  rules. No vertical gridlines, zebra stripes or tiny metadata.
- Keep an approximately 96px amount column at ordinary widths. Allow unusually
  large amounts to wrap at the currency boundary, or switch to labelled stacked
  facts. Never truncate the title or reduce the whole table's font to fit.
- Use real data-table semantics: caption/heading, column headers with scope,
  logical reading order. Layout tables use `role="presentation"`; data tables
  do not. A client that ignores responsive CSS must still expose every value.
- The single-item purchase is v1. Show additional rows only for a real
  supported multi-item transaction; do not imply a cart currently exists.
- Prefer a useful HTML summary with a secondary **View receipt** link when a
  real receipt exists. A PDF attachment must not be the only readable record.

The existing paid access message's “yours to keep” promise is not carried into
this design: email must describe actual access, not promise perpetual hosting
or access regardless of revocation/refund policy.

## Footers and unsubscribe

### Essential account and purchase messages

Use a short reason, such as “You received this email because you requested a
password reset for your Qori account,” plus verified Qori contact/identity.
Purchase mail additionally identifies the actual seller and the correct route
for purchase support. Do not fill the footer with irrelevant product links.

A purely essential security, receipt or access message does not offer a button
to disable that essential service. Optional marketing preferences remain
separate. This is not permission to classify every reminder or announcement as
essential; subscription notifications need their own classification.
[Google subscription-message guidance](https://support.google.com/mail/answer/15263077?hl=en)

### Promotional/EDM messages

Below a divider, left aligned in 14px / 20px readable text:

> Sent by Ruff Club through Qori.
>
> You receive these updates because you chose to hear from Ruff Club.
>
> **Unsubscribe from Ruff Club emails**
>
> This stops marketing from Ruff Club. Account and access emails continue.
>
> [Verified sender business identity and contact details]

The unsubscribe line is a real underlined anchor, with sufficient space for a
44px touch area, not grey legal fine print. Do not precheck a new preference,
require login or ask for a reason before honouring the choice. Sender details
and consent explanation must be true for this recipient. Placeholders above
are implementation inputs; they must not appear in a sent message.

**Current baseline:** the campaign salutation prints “Don't want these?
Unsubscribe: URL” as text. Rendered HTML does not supply an explicit anchor.
GET `/unsubscribe/{peer}` immediately sets that Group-scoped Peer's unsubscribe
time, and the result page is generic. No mailbox one-click headers were found.
Do not describe these as a working preference centre or claim client auto-linking
is guaranteed.

### Proposed web flow and mailbox action

1. **Body link opens a safe landing page.** Qori logo, heading “Stop marketing
   emails from :groupName?”, short scope explanation, primary **Unsubscribe
   from :groupName**, and a quiet **Keep my subscription** exit. Opening a GET
   link does not itself change consent; mail scanners may open links.
2. **Confirmation submits the change.** No sign-in, new email entry, survey or
   additional preferences required. On success: “You're unsubscribed from
   :groupName marketing emails.” Explain that account/access mail continues.
   Already unsubscribed is the same successful state. No re-subscribe button
   that can silently restore consent. Failure remains visible with a retry.
3. **Mailbox one-click is separate.** Supply RFC 8058 `List-Unsubscribe` HTTPS
   and `List-Unsubscribe-Post: List-Unsubscribe=One-Click` headers for promotional
   mail. The mailbox sends the POST directly, without the web confirmation,
   cookies or login. Use a validated opaque token, no redirect, and DKIM coverage
   of both headers. Do not claim headers alone guarantee a Gmail UI control.
4. **Scope stays explicit.** Remove marketing for the associated Group/list;
   do not revoke Series access or unsubscribe the person from every creator.
   Unknown/invalid tokens must not expose an address or Group from an untrusted
   query parameter. Offer a neutral unavailable-link result with a verified
   contact path; never fabricate a successful consent update.

The target is immediate suppression. Keep the link usable for the required
period and test older messages. Google distinguishes the body link from mailbox
one-click; ACMA requires clear identification and an easy unsubscribe facility
for commercial mail. These sources inform the proposed flow, rather than
establishing a legal classification for every future Qori message.
[Google sender FAQ](https://support.google.com/mail/answer/14229414?hl=en) ·
[RFC 8058](https://www.rfc-editor.org/rfc/rfc8058.html) ·
[ACMA sending guidance](https://www.acma.gov.au/avoid-sending-spam)

**Open product decision:** the preserved communications policy proposes Pro
upsells inside access confirmations and categorically excludes unsubscribe
there. That assumption conflicts with current guidance on commercial content.
Recommend a separate consented promotional message while keeping access mail
factual. The proposed change is recorded in
[decisions.md](decisions.md#open-decision-promotional-content-in-access-confirmations-2026-09-13);
it is not silently adopted here or turned into a task.

## Components and implementation boundary

**For the first branded release, reuse Laravel Markdown mail.** Publish and
customise the shared mail/notification views and theme in application-owned
paths; never edit `vendor/`. Laravel supports shared component customisation
and CSS inlining. This gets the existing messages into one Qori family without
requiring an editor product. [Laravel Markdown notifications](https://laravel.com/framework/docs/13.x/notifications#customizing-the-components)

Design primitives to implement once: `EmailShell`, `EmailHeader`, `EmailAction`,
`EmailLinkFallback`, `EmailSecurityNote`, `EmailSeriesSummary`, `EmailOrderSummary`,
`EmailTransactionalFooter` and `EmailMarketingFooter`. These are proposed
component responsibilities, not claims that these classes already exist.

Use the same shell for built-in verification/reset and custom notifications;
otherwise the most familiar account messages will remain visually different.
Footer selection must be explicit by message purpose, not inferred from whether
someone supplied an action button. Provide HTML and plain-text versions.

The recorded Templatical/MJML editor direction remains a **pending spike** and
the root plan defers custom template systems. Do not install another framework
or make the builder a dependency of this visual refresh. When editable EDMs
become work, retain separate platform-owned transactional templates and
Group-owned campaign templates, compile MJML at save time as planned, and
preserve these footer/identity constraints. MJML generates email HTML but still
requires client verification. [MJML documentation](https://documentation.mjml.io/)

All production copy belongs in the relevant `lang/en/*.php` feature files;
expiry, currency and counts come from their authoritative values. Resolve
Group vocabulary through `Terminology` for the message's Group. Use complete
translated sentences, preserve noun casing and never derive plurals. Preview
strings are examples, not permission to hardcode production nouns.

## Handoff and validation

Suggested work order, **not new task files or changes to frozen tasks**:

1. Shared shell and six existing messages, including the actual support route
   for the old-address alert. Re-run T-016's local content checks; keep T-032's
   real-delivery verification distinct.
2. Explicit campaign footer, scoped unsubscribe confirmation and RFC 8058
   endpoint/header support. Coordinate with the campaign reachability work;
   don't make essential security branding depend on the editor.
3. Purchase data/receipt ownership, then combined confirmation and delayed
   fulfilment messages. Specify pending, failed, retried and duplicate event
   behaviour before calling this ready.
4. Emailed OTP only after authentication product scope explicitly includes it.

Before implementation is signed off:

- Render every existing message plus any newly implemented variant with short
  and long names, long Series titles, unknown names and two Groups with different
  terminology. Check text alternatives and all replaced values.
- Inspect 320px, 360px and desktop; also 200% text zoom, images blocked and long
  fallback URLs. Check table reading order and keyboard link order.
- Check light/dark and image blocking in actual Gmail web/mobile, Apple Mail
  and Outlook, including classic Windows Outlook if supported. Document client
  and version; browser rendering or MJML compilation does not pass this check.
- Verify contrast for text/actions, clear headings, meaningful links and no
  status communicated by colour alone. Check plain text for the same facts,
  action URL, expiry and unsubscribe scope.
- Check URLs/expiry/intended-Series return paths with controlled accounts.
  Body-link GET must not unsubscribe; web POST and mailbox POST must update
  the same intended Group/list exactly once. Check invalid, replayed and older
  tokens, failure/retry and the sent headers.
- Verify confirmed payment with ready access, confirmed payment with delayed
  access, failure to fulfil, later recovery and duplicate webhooks. No double
  receipt, false-ready message, second charge prompt or invented ETA.
- Inspect actual sender/Reply-To and recipient evidence. Test support routing
  before retaining a reply promise. Keep a fixture manifest with commit, type,
  subject, client and viewport; describe failures in words if images are local.

The accompanying design gallery is a browser prototype using example data.
OTP, order and pending/fulfilment examples illustrate future compositions. It
is not a sent-email template or evidence that those features work. This work
does not implement mail, create tasks, claim an inbox compatibility pass or
change delivery release status.

**Checks performed for this proposal:** existing reset, paid-access and campaign
renders inspected; gallery message selection and unsubscribe confirmation →
completion exercised in the browser; ten gallery variants checked for container,
table and action overflow with a 320px browser viewport (none detected).
Desktop composition inspected in the host's dark appearance. Local document
links and whitespace checks passed. Actual inbox rendering, light-mode visual
inspection, assistive-technology testing and real notification delivery remain
outside this evidence.
