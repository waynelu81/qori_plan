# Module: bring-your-own vendor integration

**What it is.** Letting a customer connect *their own* account at another
vendor — Google Drive, Dropbox, OneDrive, Vimeo, YouTube, Zoom, Teams — and
then, using the customer's authority, granting *their* customers access to
items in it. The product never holds the content. It holds a refresh token, a
set of item ids, and a record of every permission it created.

This is the module that costs the most to discover and the least to copy. The
shape below is the same for all seven vendors; what differs is one table of
per-vendor facts, and every one of those facts has to be found by spiking.

**Done when.** A creator connects an account, picks an item, and a paying
customer opens that item on the vendor's own site with their own vendor
account — and the permission that made it possible is revoked when the
entitlement ends.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| Does the product store the content? | No, never for video or audio | Bandwidth and storage cost scale with someone else's success. The customer already pays a vendor for it. |
| What scope is requested? | The narrowest that allows the rest, plus offline access | Broad scopes fail review, frighten customers, and — see the trap — are not always a superset of what you need. |
| Grant on a container, or per item? | **It depends on the vendor, and you cannot guess** | Qori designed container grants for everything, then found Google Drive's narrow scope forbids it. See the case study. |
| When is a grant made? | At the moment the customer presses Open, inline, for that one item | Granting ahead of use means a scheduled reconciler, which is a second system with its own failure modes. Retry is the person pressing Open again. |
| Is there a reconciliation sweep? | **No** | A sweep is a cron, a lock, a backlog and an alerting story, to fix a case a button already fixes. |
| Who owns a permission when two entitlements overlap? | Key it by (connected account, target, principal); revoke on the **last** entitlement ending | Two of your own grant rows can sit over one physical vendor permission. Revoking on the first one to end silently removes access someone still pays for. |
| Does the product ever delete a customer's file? | **Never** — not deleted, not binned, not moved | The capability exists, so the refusal must be written down. A wrong grant is one call from repaired; a wrong delete may take the only copy. |
| What does disconnect do? | Drops the tokens, revokes nothing | Holding a customer's authority after they revoked it is worse than leaving stale permissions. |
| What is the product allowed to spend to develop this? | Free tiers only; otherwise stop and re-approach | Seven vendors across several tiers each is a standing bill for software nobody has decided to keep. |

## The five verbs

Every BYO integration is the same five steps. Name them the same way in every
vendor's code and the seventh integration reads like the first.

1. **Connect** — the creator authorises once; the product keeps the refresh
   token, encrypted, one connection per provider.
2. **Pick** — the creator chooses items with the *vendor's own picker*; the
   product stores the ids.
3. **Grant** — with the creator's token, the product gives the customer's own
   vendor account read access, notifications off, and records what came back.
4. **Open** — the customer opens the item on the vendor's site, in a new tab,
   through a product route that makes the grant first.
5. **Revoke** — when the entitlement ends, best effort, once; failures are
   surfaced to the creator with a button, not retried silently.

## Build order

1. **The contract.** One interface stating what the product needs in its own
   words, implemented per vendor. Everything else depends on this being
   vendor-neutral.
2. **The vendor folder.** All code that knows how the vendor works in one
   place. Its own HTTP client, its own timeout and retry.
3. **Connect and disconnect**, with the OAuth landing named for the *vendor*,
   not the service — one Google landing serves Drive and YouTube, and which
   service is being connected travels in the session state the begin step
   wrote. Needs 2.
4. **A spike, before any grant code.** See below. Needs 3.
5. **Pick**, using the vendor's picker. Needs 3.
6. **Grant and Open**, inline, under an advisory lock keyed to the permission.
   Needs 4 and 5.
7. **Revoke**, with unresolved failures listed for the creator. Needs 6.
8. **Token refresh**, keeping the connection alive before it expires unused.
   Needs 3.

## Spike before you design

**Step 4 is not optional and it is not a formality.** The case study:

Qori designed one pattern for all seven vendors — grant each customer viewer
access to *one container per Series*, a Drive folder or a Dropbox folder or a
recurring meeting. It was written up, agreed, and turned into tasks for every
provider.

Then the Google Drive spike ran. It found that `drive.file` — the narrow scope
Qori had correctly chosen — **refuses every sharing change on a folder while
any item beneath it has not been picked through the app.** Not a permissions
error you can work around: a new grant, a repeat grant and a removal all fail
the same way. The container design could not work on Google Drive at any
scope the product was willing to ask for.

The result was a reversal: on Drive, grant per file, and a Series has no
folder at all. The spike cost days. Finding it in build would have cost the
schedule, because by then four other providers would have been written to the
container shape.

**What a spike must answer, per vendor:**

- Does the narrow scope actually permit the sharing operation you need, on the
  target you intend — file, folder, or meeting?
- Can a permission be granted to someone who has no account at that vendor?
- What happens on a *repeat* grant of the same permission — idempotent, error,
  or duplicate?
- How is a permission identified on the way back, so it can be revoked?
- Does removing the app's authorisation remove the permissions it created?
  (On Drive: **no** — the customer keeps access.)
- How long does each call actually take? Timeouts set before this are guesses.
- Can all of the above be exercised on a free account?

## Rules that bite

- **Say whose storage an action touches, beside the action.** Every action is
  one of three shapes and the copy names one: it *writes a file to your
  storage*, it *changes who can open a file there* and never the file itself,
  or it *changes nothing outside the product*. Not in help — beside the button.
- **A permission's key is not your grant row's key.** Your bookkeeping row is
  per (tenant, entitlement, item). The physical permission is per (account,
  target, principal). Two rows, one permission, and the counts differ.
- **Every read and write of that key happens under the same lock as the grant.**
- **The vendor's client sets its own timeout**; a caller inside a person's
  request may pass a shorter budget, never a longer one.
- **Name the vendor in customer-facing copy only when it has been confirmed.**
  "Connect Stripe" says more than "Connect payments"; naming a storage vendor
  may give away more about the stack than intended.
- **Disconnect leaves permissions standing, and the copy must say so**, or the
  creator will believe they have revoked access they have not.

## Native contract

**Not proven.** What iOS and Android will need:

- The OAuth begin/finalise pair is a *web* flow. Native clients either open a
  system browser to the same web endpoints and deep-link back, or the product
  grows a native-specific redirect — decide before the first native release,
  because the redirect URI is registered in the vendor's console.
- **Open** must return a URL the client opens in the system browser, not an
  embedded webview: vendor sign-in inside a webview is blocked by several of
  these vendors and is hostile to password managers besides.
- The grant happens server-side on the Open request. Native clients get the
  same latency, so the inline grant's timeout budget applies to them too.

## Traps

| Symptom | Cause |
| --- | --- |
| "Sharing a folder fails for no reason, only sometimes" | A narrow scope that forbids folder sharing when any child was not picked through the app. Looks intermittent because it depends on folder contents. |
| "The customer still has access after the creator disconnected us" | Revoking the app's authorisation does not revoke permissions it created. Nothing sweeps them. |
| "Access disappeared for someone who still pays" | Revoking on the first entitlement to end, where two entitlements shared one physical permission. |
| "A grant worked in testing and times out in production" | Timeouts set before anyone measured the call. |
| "The integration can't be tested" | The vendor gates the needed tier behind a paid plan. Decide free-or-drop before starting, not after. |
| "Two Google integrations fight over the redirect" | The landing was named for the service rather than the vendor. One vendor, one landing; the service travels in session state. |

## Proven / Not proven

**Proven**: connect and disconnect against Google's real OAuth; the
`drive.file` folder-sharing limitation, found by spike; token refresh keeping a
connection alive; Open as a product route that redirects to the vendor; the
product's own object storage as the default for documents.

**Not proven**: the grant/revoke lifecycle end to end on any vendor — the
design is settled, the spikes for Dropbox and OneDrive have not run; anything
native; the unresolved-revocation list.

## Source

Qori tasks `T-044`, `T-089`, `T-093` (the Drive spike), `T-111`, `T-151`,
`T-152`; report `T-093-2026-09-20-wayne.md`. Decisions `D-016`, `D-022`,
`D-025`, `D-034`, `D-036` to `D-042`. Stream `storage`. Flows `storage.md`.
