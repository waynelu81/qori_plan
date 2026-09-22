---
id: T-184
title: Public forms that send email are limited per IP
stream: identity
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-184 — Public forms that send email are limited per IP

## Why

Anyone can post to five routes that make Qori send an email, and none is
limited by where the requests come from. Registration and forgot-password
have no throttle on the route. The magic link and the Series page's code step
allow three a minute for each address from each IP (`throttle:magic-link`),
which bounds one address and not the next. So a script on one machine can
make Qori send verification emails and codes to any number of addresses. Each
is a paid Postmark email, and made-up addresses bounce; a high bounce rate is
what gets a Postmark account paused, which would stop every sign-in code and
magic link for everyone. Afterwards each form is limited per IP as well as per
address.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

## Scope

**In:**

- `POST auth/register`, `POST auth/forgot-password`, `POST auth/magic-link`,
  `POST s/{seriesId}/access` and `POST s/{seriesId}/access/resend`: a limit
  per IP beside the one per address.

**Out:**

- A rule at Cloudflare's edge, or a challenge on the form: production setup,
  asked below.
- Invitations. Only a signed-in creator sends them, and the plan caps them.

## Files

To be settled when ready.

## Database

None.

## Code

To be settled when ready.

## Copy

To be settled when ready: the refusal, if the existing throttle message does
not serve.

## Routes

To be settled when ready: the five routes above gain a limiter.

## Tests

To be settled when ready.

## Acceptance

- [ ] Each of the five routes refuses past a limit per IP, and the limit per address is unchanged
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The numbers, per form and per hour. People behind one school or office
  network share an IP, so a Series shared with a class must not trip it: a
  class of thirty joining in the same few minutes is the case to allow.
- Whether registration and the Series page's form also get a challenge
  (Cloudflare Turnstile) or an edge rate limit, and whether Qori's app sits
  behind Cloudflare's proxy at all. Production setup, the owner's.
- Whether forgot-password needs one: it emails only an address with an
  account, and the password broker already allows one link a minute per
  account (`config/auth.php`, `throttle` 60).

## Re-scope log

None.

## Notes

Found while estimating Qori's email costs for the owner, 22 September 2026:
every other email is bounded by a plan's cap or by what a person does
themselves, and these are not.
