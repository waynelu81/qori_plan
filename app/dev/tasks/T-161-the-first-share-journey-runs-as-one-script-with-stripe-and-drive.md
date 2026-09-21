---
id: T-161
title: The first-share journey runs as one script, with Stripe and Drive
stream: onboarding
status: draft
owner: unassigned
estimate: M
depends: T-159, T-160
blocks: none
---

# T-161 — The first-share journey runs as one script, with Stripe and Drive

## Why

[The first-share journey](../journeys/first-share.md) is the product's core,
and connecting Stripe and Google Drive during setup is its point (owner,
21 September 2026). It should run as one e2e script, every step, so a change
that breaks it is caught the day it lands. Where a person has to sign in to a
vendor or type a card, the script is **hardcoded** — the owner's word for it:
"Even if it needs to be hardcoded for end to end testing."

## Before this can be ready

- **Stripe's sign-in** is replaced by a test connected account id written
  through `PaymentsService`, from `QORI_E2E_CONNECT_ACCOUNT`. _Asked_: may it
  come from the owner's local `.env` once they have connected for real?
- **Google's consent and Picker** are replaced by a stored refresh token and a
  file the creator has already picked, from `QORI_E2E_GOOGLE_REFRESH_TOKEN`
  and `QORI_E2E_GOOGLE_FILE_ID`, and the Peer plays the Google account in
  `QORI_E2E_PEER_GOOGLE_EMAIL`. _Asked_: which Google account is the Peer?
  A Testing-status refresh token lasts seven days (`T-093`), so the runner
  says so when it has expired rather than failing somewhere later.
- **The test card** is replaced by the checkout completion delivered as a
  signed `checkout.session.completed` built from the real session read back
  from Stripe — `T-121`'s second option, taken.
- `php artisan qori:e2e` empties Mailpit first, and the Mailpit on 1025/8025 is
  another project's; the runner reads by recipient instead of emptying.
- Then the owner walks the journey once by hand for real — two sign-ins and a
  test card — and the result goes in `walkthroughs.md`.

## Re-scope log

None.

## Notes

None.
