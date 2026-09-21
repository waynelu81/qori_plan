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
| 6 | **Connects their Google Drive**: Google's consent, and back to setup | **Breaks** — the connector is built and tested (`T-044`) and switched off (`T-159`) |
| 7 | Lands on their dashboard, told what to do next | Rough — the rename form again (`T-086`) |
| 8 | Names their first Series and gives it a price | Works |
| 9 | **Adds the first Episode by picking a file from their Drive** | **Breaks** — no Google Drive Episode and no Picker (`T-159`) |
| 10 | Makes it ready and copies the link | Rough — the link is at the bottom of a very long page |
| 11 | A Peer opens the link, gives name and email, types the code | Works — the code email never names who shared it |
| 12 | **The Peer pays on Stripe's checkout** | Built — checkout, direct charge and webhook fulfilment; never walked with a connected account (`T-121`) |
| 13 | The Peer lands on the Series: "Confirming your payment", then in | Built (`T-074`) |
| 14 | **The Peer presses Open on the Drive Episode, is granted reader on that one file, and lands in Drive** | **Breaks** — the grant is a comment in `PlaybackTicketService::open()` (`T-160`) |
| 15 | The Peer marks it done | Works (certificates suspended, `T-158`) |

## Branches, hung off their step

| Step | Branch | Today |
| --- | --- | --- |
| 3 | Opens the verification link on another device, signed out | Rough — "Log in" with no context; an email link then verifies and continues |
| 5 | Skips payments, later sets a price | **Breaks** — saves silently; the public page offers to buy; pressing it does nothing visible (`T-085`, `T-028`) |
| 6 | Connects Dropbox | Not built — and `D-042`'s free-or-drop call is open (`T-095`) |
| 8 | A free Series — no price, no checkout | Works — walked end to end on 21 September 2026 |
| 9 | Uploads a document to Qori instead | Works |
| 9 | Picks Audio, or Dropbox | **Breaks** — saves an Episode no Peer can open |
| 11 | Gives access by email to someone with no account | Not built (`T-043`) |
| 11 | Doesn't want emails from the creator | **Breaks** — consent is required to get in, and the button just looks dead |
| 14 | The Peer's Google account is not their Qori email | Not built (`T-092`); the happy path grants the Qori email |
| 14 | The grant is refused — no Google account for that email, the file moved | The vendor's reason is shown and Open again retries (`D-040`) |

## What to do, in order

1. **Config only the owner can set (minutes).** Stripe, test mode: Connect →
   Settings → OAuth on, add `http://localhost:8001/u/payments/stripe/finalise`
   as a redirect URI, and put the `ca_…` client id in `STRIPE_CLIENT_ID`.
   Google Cloud: `http://localhost:8001/u/connections/google/finalise` as an
   authorised redirect URI, and the creator's and a Peer's Google accounts on
   the consent screen's test users. Step 5 comes alive with no code.
2. **`T-159` — Drive from setup to an Episode (M).** Switch the Google
   connector on so setup part 3 and Integrations offer it; a Google Drive
   Episode provider; "Choose from Drive" on the Episode form opens Google's
   Picker with a fresh token from `ConnectionService::fresh()`. `drive.file`
   makes the Picker the only way a file becomes Qori's to share (`T-093`).
3. **`T-160` — Open grants the Peer and sends them to Drive (M).** The happy
   path of `T-091`: at Open, reader on that one file for the Peer's Qori email,
   then Drive's viewer (`D-040`). `T-091`'s questions become this step's
   branches, not its gate.
4. **`T-161` — the journey as one script (M).** Every step above in the e2e
   runner, hardcoded only where a person must sign in or type a card: a test
   connected account id for Stripe's sign-in, a stored Google refresh token and
   a file picked once for Google's consent and Picker, and the checkout
   completion delivered as a signed `checkout.session.completed` (`T-121`'s
   second option). Then the owner walks it once by hand for real: two sign-ins
   and a test card.
5. **Then the branches**, the step-5 one first: a price without payments says
   so and offers Connect, and the public page stops offering to buy
   (`T-085`, what is left of `T-028`). Hide Audio and Dropbox on the Episode
   form until Dropbox can connect.
6. **Rough edges on the path (S each)**: the slug at step 4, the step-7
   dashboard (`T-086`), the share link after ready, the code email naming the
   Group and Series.
7. **Everything else is [`fixups.md`](../fixups.md).**

## Asked, and carrying on meanwhile

- Step 1's config — Stripe OAuth, `STRIPE_CLIENT_ID` and the two redirect URIs.
- Which Google account plays the Peer, so it can be on the test-user list.
- For `T-161`'s hardcoding: once you have connected both for real, may the e2e
  runner take the connected account id and the Google refresh token from your
  local `.env`? They stay on your machine and are never committed.
- Naming the Group at setup also sets its slug?
- Must a Peer agree to the creator's emails to get free access?
- Local development uploads to R2 bucket `useqori-app-bucket` — is that the
  production bucket?
