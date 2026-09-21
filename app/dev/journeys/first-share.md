# Journey: a creator's first share

A stranger arrives, becomes a creator, **connects the Stripe account and the
Google Drive they already have during setup**, sells one Series made from a
file in their Drive, and somebody they send the link to pays, gets in and opens
it in Drive. Those two connections are what Qori sells, so they are the path,
not a branch (owner, 21 September 2026). Everything else is a branch off one of
these steps. Walked on 21 September 2026 as far as it goes today — evidence in
[`walkthroughs.md`](../walkthroughs.md).

**Works** — walks clean. **Rough** — works, and a person would stumble.
**Built** — the code exists and has not been walked. **Breaks** — a person
cannot do what the step is for.

## The happy path

| # | The person | Today |
| --- | --- | --- |
| 1 | Lands on the home page and presses Start sharing | Works |
| 2 | Picks "I want to share", gives name, email, password | Rough — "Set up a school"; four fields and no passwordless sign-up |
| 3 | Confirms their address from the email | Works — the email is Laravel's stock text (`T-055`) |
| 4 | Names their Group | Rough — the URL keeps the name Qori made up, forever |
| 5 | **Connects their Stripe account**: Stripe's sign-in, and back to setup | **Breaks** — the door is built (`T-063`) and needs `STRIPE_CLIENT_ID`, which is not set |
| 6 | **Connects their Google Drive**: Google's consent, and back to setup | Built (`T-159`) — setup part 3 links to it; one page via Integrations, where the account kind is chosen |
| 7 | Lands on their dashboard, told what to do next | Rough — the rename form again (`T-086`) |
| 8 | Names their first Series and gives it a price | Works |
| 9 | **Adds the first Episode by picking a file from their Drive** | Built (`T-159`) — the Picker has not yet run against a real account |
| 10 | Makes it ready and copies the link | Rough — the link is at the bottom of a very long page |
| 11 | A Peer opens the link, gives name and email, types the code | Works — the code email never names who shared it |
| 12 | **The Peer pays on Stripe's checkout** | Built — checkout, direct charge and webhook fulfilment; never walked with a connected account (`T-121`) |
| 13 | The Peer lands on the Series: "Confirming your payment", then in | Built (`T-074`) |
| 14 | **The Peer presses Open on the Drive Episode, is granted reader on that one file, and lands in Drive** | Built (`T-160`) — a real refusal walked; a real grant not yet |
| 15 | The Peer marks it done | Works (certificates suspended, `T-158`) |

## Branches, hung off their step

| Step | Branch | Today |
| --- | --- | --- |
| 3 | Opens the verification link on another device, signed out | Rough — "Log in" with no context; an email link then verifies and continues |
| 5 | Skips payments, later sets a price | **Breaks** — saves silently; the public page offers to buy; pressing it does nothing visible (`T-085`, `T-028`) |
| 6 | Connects Dropbox | Not built — and `D-042`'s free-or-drop call is open (`T-095`) |
| 8 | A free Series — no price, no checkout | Works — walked end to end on 21 September 2026 |
| 9 | Uploads a document to Qori instead | Works |
| 9 | Picks Audio, or Dropbox | Rough — offered, then refused on save: "That storage can't be connected to Qori yet" (`T-152`); Audio offers nothing else |
| 11 | Gives access by email to someone with no account | Not built (`T-043`) |
| 11 | Doesn't want emails from the creator | **Breaks** — consent is required to get in, and the button just looks dead |
| 14 | The Peer's Google account is not their Qori email | Not built (`T-092`); the happy path grants the Qori email |
| 14 | The grant is refused — no Google account for that email, the file moved | The vendor's reason is shown and Open again retries (`D-040`) |

## What to do, in order

1. **Config only the owner can set (minutes).** Stripe, test mode: Connect →
   Settings → OAuth on, add `http://localhost:8001/u/payments/stripe/finalise`
   as a redirect URI, and put the `ca_…` client id in `STRIPE_CLIENT_ID`.
   Google Cloud: `http://localhost:8001/u/connections/google/finalise` as an
   authorised redirect URI. The app has been _In production_ since 20
   September 2026, so no test users are needed unless it was switched back.
   Step 5 comes alive with no code. Every step, and what an agent may read for
   you in the consoles: `docs/tinker/e2e-first-share.md` in the code
   repository.
2. ~~**`T-159` — Drive from setup to an Episode.**~~ Done 21 September 2026.
3. ~~**`T-160` — Open grants the Peer and sends them to Drive.**~~ Done 21
   September 2026. The owner's real Google connection from `T-044`'s walk is
   live locally, so steps 6, 9 and 14 can be walked by hand now.
4. **`T-161` — the journey as one script (M).** Built 21 September 2026:
   `tests/e2e/first-share.spec.ts` walks every step above, hardcoded only where
   a person must be at a vendor, from the owner's gitignored `.env.e2e`
   (`D-045`). Skipped until that file exists. Next: walk steps 5, 6 and 9 once
   for real, run `php artisan qori:e2e:capture you@… --peer=…`, then
   `php artisan qori:e2e --only=first-share --headed`; and walk it once by hand
   with a test card.
5. **Then the branches**, the step-5 one first: a price without payments says
   so and offers Connect, and the public page stops offering to buy
   (`T-085`, what is left of `T-028`). Stop offering Dropbox, and Audio's
   Dropbox-only choice, on the Episode form while nothing can connect it.
6. **Rough edges on the path (S each)**: the slug at step 4, the step-7
   dashboard (`T-086`), the share link after ready, the code email naming the
   Group and Series.
7. **Everything else is [`fixups.md`](../fixups.md).**

## Asked, and carrying on meanwhile

- Step 1's config — Stripe OAuth, `STRIPE_CLIENT_ID` and the two redirect URIs.
- Which Google account plays the Peer: it goes in `QORI_E2E_PEER_GOOGLE_EMAIL`.
- ~~May the e2e runner take the account id and the refresh token from your
  local `.env`?~~ 21 September 2026: yes — from `.env` or a designated
  gitignored file, skipped where it does not exist (`D-045`).
- Naming the Group at setup also sets its slug?
- Must a Peer agree to the creator's emails to get free access?
- Local development uploads to R2 bucket `useqori-app-bucket` — is that the
  production bucket?
