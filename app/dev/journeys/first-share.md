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
| 4 | Names their Group | Works — naming it in setup gives it the URL of its name (`T-177`) |
| 5 | **Connects their Stripe account**: Stripe's sign-in, and back to setup | Works — the owner connected through Stripe's sign-in on 21 September 2026, once `STRIPE_CLIENT_ID` was set |
| 6 | **Connects their Google Drive**: Google's consent, and back to setup | Built (`T-159`) — setup part 3 links to it; one page via Integrations, where the account kind is chosen |
| 7 | Lands on their dashboard, told what to do next | Works — the name card offers a rename once named (`T-086`) |
| 8 | Names their first Series and gives it a price | Works |
| 9 | **Adds the first Episode by picking a file from their Drive** | Built (`T-159`) — the Picker has not yet run against a real account |
| 10 | Makes it ready and copies the link | Works — making it ready lands on the share link with Copy focused (`T-174`) |
| 11 | A Peer opens the link, gives name and email, types the code | Works — the code email names the Series and who shared it (`T-175`) |
| 12 | **The Peer pays on Stripe's checkout** | Built — checkout, direct charge and webhook fulfilment; never walked with a connected account (`T-121`) |
| 13 | The Peer lands on the Series: "Confirming your payment", then in | Built (`T-074`) |
| 14 | **The Peer presses Open on the Drive Episode, is granted reader on that one file, and lands in Drive** | Built (`T-160`) — a real refusal walked; a real grant not yet |
| 15 | The Peer marks it done | Works (certificates suspended, `T-158`) |

## Branches, hung off their step

| Step | Branch | Today |
| --- | --- | --- |
| 3 | Opens the verification link on another device, signed out | Rough — "Log in" with no context; an email link then verifies and continues |
| 5 | Skips payments, later sets a price | Built (`T-085`) — the price field says nobody can pay until Stripe is connected, with a Connect link (`T-054`); the public page names the Group and says it isn't taking payments yet, in place of the forms |
| 5 | Connects an account Stripe will not let charge yet — a document, a detail or the terms still due | Built (`T-164`) — Integrations lists each thing Stripe asked for with a link to its page in the creator's Stripe dashboard; connecting says where the list is; the dashboard and the price field say payments are held back |
| 6 | Connects Dropbox | Not built — and `D-042`'s free-or-drop call is open (`T-095`) |
| 8 | A free Series — no price, no checkout | Works — walked end to end on 21 September 2026 |
| 9 | Uploads a document to Qori instead | Works |
| 9 | Picks Audio, or Dropbox | Built (`T-171`) — Dropbox is no longer offered for any kind, and Audio offers Google Drive |
| 11 | Gives access by email to someone with no account | Not built (`T-043`) |
| 12 | The creator's Stripe account cannot take payments | The Peer still reaches Stripe's Checkout — test mode creates it — and cannot pay there; the owner accepts that, and the creator is the one told (`T-164`, 22 September 2026) |
| 11 | Doesn't want emails from the creator | Built (`T-178`, `D-049`) — the terms are required, the emails optional; a box left unticked answers with the reason |
| 14 | The Peer's Google account is not their Qori email | Not built (`T-092`); the happy path grants the Qori email |
| 14 | The grant is refused — no Google account for that email, the file moved | The vendor's reason is shown and Open again retries (`D-040`) |

## What to do, in order

1. ~~**Config only the owner can set (minutes).**~~ Set on 21 September 2026. Stripe, test mode: Connect →
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
   (~~`T-085`~~, done 22 September 2026, with a Toaster on every layout so a
   refusal on a page without the app shell is seen). ~~Stop offering Dropbox, and
   Audio's Dropbox-only choice, on the Episode form while nothing can connect
   it~~ (`T-171`, done 22 September 2026).
6. **Rough edges on the path (S each)**: the slug at step 4 (~~`T-177`~~), the
   step-7 dashboard (~~`T-086`~~), the share link after ready (~~`T-174`~~),
   the code email naming the Group and Series (~~`T-175`~~) — the last three
   done 22 September 2026.
7. **Everything else is [`fixups.md`](../fixups.md).**

## Asked, and carrying on meanwhile

- ~~Step 1's config — Stripe OAuth, `STRIPE_CLIENT_ID` and the two redirect
  URIs.~~ Set on 21 September 2026.
- ~~Which Google account plays the Peer: it goes in
  `QORI_E2E_PEER_GOOGLE_EMAIL`.~~ Answered in the owner's `.env.e2e`, 21
  September 2026.
- ~~May the e2e runner take the account id and the refresh token from your
  local `.env`?~~ 21 September 2026: yes — from `.env` or a designated
  gitignored file, skipped where it does not exist (`D-045`).
- ~~Naming the Group at setup also sets its slug?~~ Yes, 22 September 2026 (`T-177`).
- ~~Must a Peer agree to the creator's emails to get free access?~~ No: they
  agree to the terms, Qori's own until creators write theirs, and emails are
  optional — 22 September 2026 (`D-049`, `T-178`, `T-179`).
- ~~Local development uploads to R2 bucket `useqori-app-bucket` — is that the
  production bucket?~~ Yes; local development uses `useqori-app-bucket-test`
  from 22 September 2026.
