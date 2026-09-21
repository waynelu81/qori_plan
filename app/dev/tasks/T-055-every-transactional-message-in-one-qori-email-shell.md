---
id: T-055
title: Every transactional message in one Qori email shell
stream: delivery
status: draft
owner: unassigned
estimate: L
depends: T-016
blocks: none
---

# T-055 — Every transactional message in one Qori email shell

## Why

Qori's six transactional messages render in Laravel's default Markdown shell: a
text "Qori" link for a header, a 570px white card on grey, a black button, a
generic greeting and sign-off. No logo, no paper, no gold. They are correct and
they are anonymous — the one place the product speaks to somebody who is not
looking at it, and it does not look like itself.

The designer's [system email design](../ui-system-email.md), 13 September
2026, specifies the family: a logo-led 600px shell in the brand palette, a
security variant for the five account messages, an access variant for the
Series message, content order, footers, dark appearance and a validation
checklist. The owner asked for it to become a task the same day. This is that
task, cut to the first step of the design's own handoff order: **the shared
shell and the six messages that exist.**

## Before this can be ready

- **The support route for the address-changed alert.** The current message asks
  the old address to reply; no notification-specific Reply-To exists and nobody
  has said which inbox is monitored. The design refuses to invent one. The owner
  names it, or the alert stops promising a reply.
- **A stable HTTPS home for the logo.** The design wants a small optimised PNG
  from `docs/brand/logos/qori-logo-primary-1200.png` at a permanent URL without
  an expiring signature. Whether that is the application's own `public/` on
  `useqori.com` or a public R2 bucket is a decision, and it decides a file path
  in this task.
- **The open decision on promotional content** in
  [`decisions.md`](../decisions.md#open-decision-promotional-content-in-access-confirmations-2026-09-13)
  is settled, or this task explicitly excludes any Pro offer from access mail,
  which the design recommends.
- **The message-by-message copy in the design's security table** is confirmed
  or amended by the owner, since it changes subjects and headings that `T-016`'s
  checks and any inbox filter already know.

## Scope

**In:**

- Publishing the mail views and theme into application-owned paths and
  restyling them to the design: envelope, header lockup, palette, action,
  footer, dark appearance, plain-text variant.
- The six existing messages moved onto that shell with the design's content
  order: verify, reset, sign-in link, confirm new address, address changed,
  Series access.
- Re-running `qori:mail:check`, and extending `MailContent` with whatever the
  design's fixed elements make checkable.

**Out:**

- Order confirmation, fulfilment pending and fulfilment ready. They need a
  purchase reference, receipt ownership and a trigger that do not exist;
  `T-043` and a receipt task come first.
- The campaign footer, the unsubscribe confirmation page and RFC 8058
  one-click headers. Same shell, different obligations, own task.
- Emailed OTP. Not a product feature.
- MJML, an editor, or any template system. The design says reuse Markdown mail
  and the plan defers custom templates.
- Real inbox verification in Gmail, Apple Mail and Outlook. That is `T-032`'s
  arrival check widened, and it needs the production sender.

## Files

| Path                                               | Change | Notes                                   |
| -------------------------------------------------- | ------ | --------------------------------------- |
| `resources/views/vendor/mail/html/*.blade.php`     | new    | Published, then edited                  |
| `resources/views/vendor/mail/text/*.blade.php`     | new    | Published, then edited                  |
| `resources/views/vendor/mail/html/themes/qori.css` | new    | The palette and geometry, inlined       |
| `config/mail.php`                                  | edit   | `markdown.theme` → `qori`               |
| `app/Notifications/*.php`                          | edit   | Five, onto the shell's content order    |
| `lang/en/auth.php`, `lang/en/accesses.php`         | edit   | Subjects and lines per the design table |
| `app/Support/MailContent.php`                      | edit   | New checks                              |
| `tests/Feature/Mail/EmailShellTest.php`            | new    | Cases set when ready                    |

Fortify's verify and reset notifications are framework classes; the shell reaches
them through the published views, and their subjects through the existing
`VerifyEmail::toMailUsing()` / `ResetPassword::toMailUsing()` hooks if the copy
table is adopted.

## Database

None.

## Code

To be named when ready: the Blade components the design calls `EmailShell`,
`EmailHeader`, `EmailAction`, `EmailLinkFallback`, `EmailSecurityNote`,
`EmailSeriesSummary` and `EmailTransactionalFooter`, as published-view partials
rather than Vue.

## Copy

Per the design's security-family table, once confirmed. Every line stays in
`lang/en/*.php`; expiry minutes and Group nouns are interpolated, never typed.

## Routes

None.

## Tests

To be listed when ready. The shape: one rendered fixture per message, the
`MailContent` checks, the logo `alt`, one primary action per message, the
plain-text twin carrying the same URL and expiry, and no product noun hardcoded.

## Acceptance

- [ ] All six messages render in the Qori shell, light and dark, with a
      plain-text twin
- [ ] No Vimeo/website banner, slogan, social links or navigation in any of them
- [ ] `qori:mail:check` green with the new checks
- [ ] `composer ci:check` green from a clean tree
- [ ] Board regenerated (`php artisan qori:tasks`)
- [ ] Report written in `reports/`

## Re-scope log

None.

## Notes

The design's own handoff order is the order of tasks: this one; then the
campaign footer and unsubscribe flow; then purchase and fulfilment mail once a
receipt has an owner; OTP never, unless authentication scope changes. Its
validation checklist — 320px, images blocked, 200% zoom, real clients — is the
acceptance list to copy in when this becomes ready.
