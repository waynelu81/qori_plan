# Journey: a creator's first share

A stranger arrives, becomes a creator, puts one thing in a Series and shares
it; somebody they send the link to gets in and finishes. Everything else in
onboarding and storage is a branch off one of these steps. Walked end to end on
21 September 2026 — evidence in [`walkthroughs.md`](../walkthroughs.md).

**Works** — walks clean. **Rough** — works, and a person would stumble.
**Breaks** — a person cannot do what the step is for.

## The happy path

| # | The person | Today |
| --- | --- | --- |
| 1 | Lands on the home page and presses Start sharing | Works |
| 2 | Picks "I want to share", gives name, email, password | Rough — "Set up a school"; four fields and no passwordless sign-up |
| 3 | Confirms their address from the email | Works — the email is Laravel's stock text (`T-055`) |
| 4 | Names their Group | Rough — the URL keeps the name Qori made up, forever |
| 5 | Connects their payment account | **Breaks** — Stripe Connect is not configured, so the step can only be skipped |
| 6 | Connects where their files live | **Breaks** — nothing to connect; Google is built and hidden behind `T-094` → `T-091` |
| 7 | Lands on their dashboard, told what to do next | Rough — the rename form again (`T-086`); no word about what was skipped |
| 8 | Names their first Series | Works |
| 9 | Adds the first Episode | Works for a Qori upload. **Breaks** for Audio and Dropbox — it saves, and no Peer can ever open it |
| 10 | Makes it ready and copies the link | Rough — the link is at the bottom of a very long page |
| 11 | A Peer opens the link, gives name and email, types the code | Works — the code email never names who shared it |
| 12 | The Peer opens the Episode and marks it done | Works (certificates suspended, `T-158`) |

## Branches, hung off their step

| Step | Branch | Today |
| --- | --- | --- |
| 3 | Opens the verification link on another device, signed out | Rough — "Log in" with no context; an email link then verifies and continues |
| 5 | Skips payments, later sets a price | **Breaks** — saves silently; the public page offers to buy; pressing it does nothing visible (`T-085`, `T-028`) |
| 6 | Connects Google Drive, picks a file, a Peer is granted on open | Not built — `T-091`/`T-094` |
| 6 | Connects Dropbox | Not built — and `D-042`'s free-or-drop call is open (`T-095`) |
| 11 | Gives access by email to someone with no account | Not built (`T-043`) |
| 11 | Doesn't want emails from the creator | **Breaks** — consent is required to get in, and the button just looks dead |

## What to do, in order

1. **Stop the traps (S, now).** Hide Audio and the Dropbox option on the
   Episode form while no Dropbox connection can exist, so step 9 cannot build
   something unopenable. Setup part 3 says plainly that documents upload to
   Qori today and external storage is coming, with one button.
2. **Step 5 comes alive (owner, minutes).** Turn on Connect OAuth in the Stripe
   test dashboard and set `STRIPE_CLIENT_ID`. Then walk step 5 and its branch.
3. **The step-5 branch (S–M).** Setting a price without payments says so beside
   the price with the Connect button; the public page does not offer to buy;
   a refused checkout shows its message. This is what is left of `T-028` plus `T-085`.
4. **Step 6, as a vertical slice (M–L).** Google Drive: connect (built), pick
   one file for an Episode, and grant the Peer reader access when they open it
   (`D-040`). `T-091`'s 39 open questions become the branch list after it, not
   the gate before it. Unhides the Google section in the same change.
5. **Step 4 (S).** Naming the Group during setup sets the slug too, while
   nothing has been shared.
6. **Rough edges on the path (S each).** The step-7 dashboard (`T-086`, and a
   line for what was skipped), the share link after ready, the code email
   naming the Group and Series.
7. **Everything else is [`fixups.md`](../fixups.md).**

## Asked, and carrying on meanwhile

- Build Drive as the slice in 4 — connect, pick, grant on open — before
  `T-091`'s edge cases, and unhide Google when the picker lands in it?
- Stripe Connect OAuth on in test mode, and `STRIPE_CLIENT_ID` in `.env`?
- Naming the Group at setup also sets its slug?
- Must a Peer agree to the creator's emails to get free access?
- Local development uploads to R2 bucket `useqori-app-bucket` — is that the
  production bucket?
