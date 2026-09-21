---
id: T-097
title: Spike: OneDrive silent invites and moved files
stream: storage
status: draft
owner: unassigned
estimate: S
depends: none
blocks: T-098
---

# T-097 — Spike: OneDrive silent invites and moved files

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016` and the owner's BYO blueprint. Reworked on 21 September 2026 on
> `D-042`: nothing is bought to run it, a free Microsoft 365 E5 developer
> sandbox replaces the paid work tenant, step 0 settles that free path before
> any other fixture is gathered, and the personal half runs without waiting
> for it.

## Why

`D-016` grants each Peer on one container per Series with the vendor's
notification off, and `T-098` is OneDrive's version of it: one silent read
invite per Peer on a Series folder. Three things that spec has to state are
undocumented or contradicted by Microsoft's own pages, and `PROCESS.md`
refuses a spec that guesses a vendor payload. With `sendInvitation: false`
Microsoft documents no way for the Peer to take the grant up: the `permission`
resource says the grantee stays empty "until the invitation is redeemed" and
describes redemption as clicking the emailed link
([permission resource](https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0)),
so nobody knows whether an invite's 200 is `T-091`'s `granted` or its
`awaiting_acceptance`, or what a re-read of the stored permission shows once
the Peer has opened the folder. Microsoft's OneDrive support page says files
_moved_ into a shared folder need sharing again
([Share OneDrive files and folders](https://support.microsoft.com/en-us/office/share-onedrive-files-and-folders-9fcc2f7d-de0c-4cec-93b0-a82024800c07)),
and no primary source says a file _uploaded_ later reaches an existing viewer
on a personal account. And the invite response for an outside recipient is
reported to come back as a link-type permission on one call and a direct one
on the next (Microsoft Q&A,
<https://learn.microsoft.com/en-us/answers/questions/2147610/onedrive-sharing-and-graph-invite-endpoint-now-cre>),
which decides what `T-091`'s `vendor_grants.vendor_ref` can hold for OneDrive
and whether a revoke can delete it without cutting off somebody else.

Afterwards: every response `T-098` names is a committed fixture under
`tests/Fixtures/microsoft/`, a dated report answers each question with what
was observed, and `T-098` — the bare template today — carries a Notes line
naming that report until it is specified from it. `T-092` puts the Peer's
Microsoft id-token fixture on this spike (`T-092`, Preconditions), so the
Peer's sign-in is captured here as well.

Nothing under `app/` mentions Microsoft today. `app/Integrations/` holds
Dropbox, Qori, Stripe and Vimeo; `App\Enums\ConnectionProvider` and
`App\Enums\EpisodeProvider` have no OneDrive case; the only trace is the
comment at `app/Providers/IntegrationServiceProvider.php:33-34` saying OneDrive
is "a class and a line here". That is `T-098`'s to change, not this task's.
Nor does `T-091`'s machinery exist: `vendor_grants`, `VendorGrantStatus`,
`VendorAccessService` and `qori:access:reconcile` are that draft's names, and
every one this file borrows is a spec's name rather than a class on disk.

## Decisions taken to make this specifiable

**The free path is settled first, and the spike is two halves (`D-042`).**
Step 0 gets the work tenant for nothing — a Microsoft 365 E5 developer
sandbox — confirms the eligibility it rests on, and sends one invite from it
before any other work-tenant fixture is gathered, because every work-tenant
question below is unanswerable without a tenant and none of them is worth
answering about a path Qori may not build. The personal half is not held
behind that gate and starts the same day: a personal Microsoft account, an
outlook.com mailbox and a Gmail alias cost nothing and need no program, so
its free path was never in doubt, and `D-042`'s ordering applies to the half
whose free path is. Steps 1 to 6, step 8 and step 9's P1 round trip are the
personal half; step 7 and step 9's P4 round trip are the work half and wait
on step 0. Where no sandbox can be had, nothing is bought instead: the
personal half runs to the end and commits its fixtures, the work-tenant
questions are recorded unanswered with the reason, and the work-or-school
tier goes back to the owner to re-approach or drop. Acceptance already
refuses to let `T-098` advertise a family that was not walked, which is what
keeps that honest.

**The spike writes nothing under `app/`.** Calls are made from tinker with
`Http::withToken()` or from curl, and the output is evidence. Code written to
run a spike gets kept, and then it is code nobody specified.

**The folder grant is what is measured; per-item invites are measured beside
it as the fallback.** `D-016` chose the container, and the container rule
(provisional, the owner's question) is one dedicated folder per Series, never
shared between Series — so `Series spike/` holds this one Series and nothing
else. The spike's job is to find where the folder grant holds — uploads,
same-name replacements, moves — and what repairs it where it does not, so
`T-098` chooses between folder-only, folder plus re-share, and per-item from
observed behaviour rather than from the two research digests that disagree on
it. Per-item is a change to `T-091`'s one grant row per (Access, container),
recorded there and never hidden in the connector. The permission listing on
`new-web.pdf`, which is no Episode, is also what proves the picker copy's line
that sharing the folder shares everything inside it.

**Every question is asked in `T-091`'s six states, and the spike settles when
a OneDrive grant is `granted`.** `awaiting_identity` — the Peer has not
confirmed the Microsoft account the Series needs; the Peer resolves, by
signing in with Microsoft (`T-092`). `awaiting_acceptance` — the invite was
accepted but the Peer still has a step at Microsoft; the Peer resolves.
`pending` — Qori will retry: a timeout, a 429 or 503 with `Retry-After`, a
transient error; nobody needs to act. `needs_creator` — the creator must act:
reconnect, a tenant sharing level or guest-invite setting, a hard cap.
`granted` and `revoked`. An invite's 200 is not usable access until step 4
shows the Peer opening the folder; Q1 and Q11 decide what `T-098` may call
`granted` and what its `checkGrant()` reads, and Q7, Q9 and step 6's 401
decide which failures map to which state. Each non-granted state's Peer-facing
sentence has to name who resolves it, and only `pending` may tell a Peer that
nothing more is needed from them. The mapping and the sentences are `T-098`'s
to write, from these fixtures.

**The three reconciliation triggers each leave a fixture.** `T-091` routes a
Peer confirming or changing an identity, the creator reconnecting, and a
container being replaced through the same ensure step, and each needs a
OneDrive answer. Identity: step 9 captures what a confirmation carries, and
the invite that follows one is step 3's call unchanged. Reconnect, the same
account: step 1 refreshes twice and retries the replaced refresh token, and
step 6's 401 on an expired access token is the failure a refresh recovers
inside the request — as against a refresh that fails, which is
`needs_creator`. Connect a different account: step 8 reads C1's folder with
C3's token, which is what `checkContainer()` meets when the stored drive and
item ids belong to an account that is gone. Container replaced: step 6 deletes
one folder's permission and invites P1 on a second folder, so `T-098` knows
whether the old grant and the new one stand independently.

**Every invite sends `roles: ["read"]`, `requireSignIn: true`,
`sendInvitation: false` and nothing else.** `requireSignIn` and
`sendInvitation` cannot both be false (a 400) and `retainInheritedPermissions`
was reported to 404, both from one Microsoft Q&A answer that was tested with an
internal objectId on a SharePoint library only
(<https://learn.microsoft.com/en-gb/answers/questions/1336369/invalid-request-using-graph-invite-endpoint-requir>).
The 400 is recorded once as a fixture; `retainInheritedPermissions` is never
sent, because `T-098` will not send it either.

**The stored permission is re-read before and after each Peer's first open,
and again the next day.** `T-091` re-checks `awaiting_acceptance` and
`granted` rows through `checkGrant()` — on Open before a `granted` row is
trusted, and from `qori:access:reconcile`, which sweeps every few minutes
(provisional) and re-reads a `granted` row on a longer cadence (`checked_at`,
provisional interval) — so current access is verified, not only first
access. That only works if `GET …/permissions/{PERM_1}` looks different once
the Peer has taken the grant up. Q11 is that measurement.

**The invite call's own wall time is recorded beside the stopwatch.** `T-091`
grants inside the request that creates the Access, under
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` (provisional 5), and a timeout
leaves the row `pending` for the sweep. If an invite commonly takes longer
than that, priority 1 is served by the sweep and not by the request, and
`T-098` has to say so. Q12 is that measurement; the seconds go in the README
row beside each fixture.

**One repeated grant, one recoverable failure and one different-account read
are provoked on purpose.** The developer review of 16 September 2026 asks
every provider for a repeated grant and a recoverable failure on record. The
repeat is step 3's second invite of P1 (Q6). The recoverable failure is an
invite sent with step 1's first access token after it has expired — the 401 a
refresh recovers inside the same request, as opposed to the failed refresh
that is `needs_creator`. The different-account read is C3 fetching C1's
folder by id (step 8): what `checkContainer()` meets after the creator
connects another account, which `T-091` answers by marking containers for a
new pick. None of the three is a test; each is a fixture.

**The Peer's Microsoft sign-in is captured with `openid email` on both
families.** `T-092` keys a OneDrive identity on `oid` + `tid` and requires
`xms_edov`, and its Preconditions put the Microsoft id-token fixture on this
spike. One authorization-code round trip as P1 and one as P4 against the same
registration, through `/common`, with `xms_edov` added as an optional id-token
claim in the registration's token configuration, gives `T-092` the payload
and answers Q13. Building the sign-in stays `T-092`'s.

**Personal OneDrive is spiked on a free account; ~~Microsoft 365 Personal
only if a subscription is to hand (provisional — see below)~~ — C2 is not
provisioned (`D-042`, 21 September 2026).** The questions that can kill the
tier are the same on both; the daily cap is what differs, and it is measured
on free, the tighter of the two. One thing goes unanswered with C2: whether
a Microsoft 365 Personal or Family subscription lifts the cap Q9 counts, and
by how much. So the report says the number it measured is free OneDrive's,
`T-098` states that number and states none for the paid personal
subscriptions, and nobody buys one to find the other.

**The daily-cap count runs last, on a throwaway creator account.** Microsoft
says sharing on basic OneDrive is limited and "limits reset after 24 hours"
([Unable to share OneDrive files](https://support.microsoft.com/en-us/office/unable-to-share-onedrive-files-18755580-24f3-408d-afda-bd8d0f7ed5a2));
hitting the cap on the main spike account would stop every other step for a
day.

~~**The work tenant is paid, not a trial, and the tester is its Global
Administrator.**~~ **Answered 21 September 2026 (`D-042`): the work tenant is
a free Microsoft 365 E5 developer sandbox**, whose administrator account is a
Global Administrator, so the sharing level and the guest-invite setting can
still be flipped and flipped back. The old bullet's reason stands and is why
step 0 exists rather than an assumption: trial tenants restrict external
sharing
([External sharing overview](https://learn.microsoft.com/en-us/sharepoint/external-sharing-overview)),
no Microsoft page says whether a developer sandbox is restricted the same
way, and one invite settles it where a purchase was being proposed to avoid
the question.

**Revoke is checked for whom it cuts off, not for how fast.** `D-016` makes
revocation best effort and rules airtight revocation out as a concern, so step
6 confirms P1 still opens after P2's permission is deleted and records nothing
about P2's open tab. What it does settle is Q6: whether one permission id
covers several Peers, which is the case where a delete must be skipped. The
same question has a second half. A Microsoft Q&A thread reports an invite to
somebody who already has access returning 200 with no new permission
(<https://learn.microsoft.com/en-us/answers/questions/1332382/microsoft-graph-api-drives-((drive-id))-items-((it>),
so the id `T-098` would store as `vendor_ref` may not be the one letting that
Peer in. Step 3's repeat invite of P1 is where that shows, because P1 already
holds a permission when it is sent.

**Fixtures are raw response bodies with ids swapped for fixed placeholders,
and one `README.md` beside them records the request, status, headers, seconds
and date per file.** No `tests/Fixtures/<vendor>/` directory exists yet
(`tests/Fixtures/` holds `planning` and `reachability`), and every vendor test
today fakes with an inline `Http::response([...])`, so there is no loader to
fit. A raw body is what `Http::response(file_get_contents(...), $status)`
takes; the status and any `Retry-After` live in the README row. A `204` has
no body and gets no file, only a row. **Capture generously rather than
sparely, because the tenant will not be there when it is wanted:** `T-098` is
an `L` behind `T-044`, `T-091`, `T-092`, `T-094`, this spike and `T-152`,
while the sandbox lasts 90 days at a time and only renews on real
development activity — after it expires there are 30 days to take data out,
30 more where only the admin can sign in, and deletion on day 60
([FAQ](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-faq)).
What these fixtures do not hold is what `T-098` cannot be specified from, and
re-observing it means a new tenant and another eligibility check.

**Placeholders are fixed strings, never blanks:** `DRIVE_ID`, `FOLDER_ID`,
`FILE_PDF_ID`, `FILE_MP4_ID`, `UPLOADED_ID`, `MOVED_ID`, `PERM_1`, `PERM_2`,
`PERM_3`, `TENANT_ID`, `USER_OID`, `peer-1@example.com`, `peer-2@example.com`,
`peer-3@example.com`, `peer-4@example.com`, `ACCESS_TOKEN`, `REFRESH_TOKEN`,
`ID_TOKEN`. Every other field keeps its value and shape — `webUrl` included,
with only the id or account segment replaced — so `T-098`'s tests can assert
on a URL shape Microsoft actually returned.

**The answers go into `T-098` as struck bullets with the date and the fixture
where it has bullets, and as one Notes line naming the report while it is the
bare template it is today.** `T-098` is a draft, so editing it is allowed; the
struck bullet is where the next reader looks first and the report is where the
observation lives. `T-093` does the same for `T-094`, and `T-092`'s one
bullet for this spike is struck the same way.

**Timings are a stopwatch from the invite's 200 to the Peer's first
successful open**, written in the report. No source gives a figure, and one
measurement on the day is better than none.

**Publisher verification is measured, not started.** Whether a non-admin
member of the work tenant can consent to an unverified multi-tenant app asking
`Files.ReadWrite` is recorded — the AADSTS90094 refusal or a consent page.
Starting verification needs the owner's partner account and a custom
publisher domain
([Publisher verification](https://learn.microsoft.com/en-us/entra/identity-platform/publisher-verification-overview)),
which is `release-prerequisites.md:20`'s line to update.

## Preconditions

**Data this task verifies against:** none in Qori's database. The spike runs
no Qori code; a clean checkout is enough for committing the fixtures.

**Equipment.** Nothing below is bought (`D-042`): the work tenant is a free
developer sandbox, every account is free to create, and an Entra app
registration costs nothing and needs no paid tenant or Azure subscription
behind it.

- **A Microsoft 365 E5 developer sandbox — the work-or-school tenant, free,
  and step 0's business.** The Microsoft 365 Developer Program gives an
  eligible member a Microsoft 365 E5 subscription with **25 user licences
  including the administrator**, good for up to 90 days and renewed on real
  development activity
  ([the program](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program),
  [setting one up](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-get-started),
  [FAQ](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-faq)).
  That covers everything the paid seat was for and more: the tenant, a Global
  Administrator, the non-admin member **W1** for the consent walk and the
  creator **W2**, who are two of the 24 non-admin accounts — 16 of them
  pre-created — rather than three jobs sharing one seat. One thing the swap
  costs: the tier facts below give B2B invitation caps of 10 or 100 a day for
  an unpaid tenant against 200 for a paid one under 30 days old, and no page
  says which a sandbox is, so step 7 records the tenant's age beside any
  refusal rather than reading a number off that table. Three things about the
  sandbox are checked at step 0 and not assumed:
    - **Eligibility, which is the whole question, and there is no open
      signup.** Read against the
      [FAQ](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-faq)
      on 21 September 2026, the qualifying paths are exactly three and the
      list is closed: an eligible Visual Studio Professional or Enterprise
      _standard_ subscription; the ISV Success Program or an eligible
      Microsoft AI Cloud Partner Program tier; or a Premier or Unified
      Support contract. **Nobody outside those three can obtain a sandbox at
      any price**, and an existing Microsoft 365 enterprise subscription does
      not qualify an account — the FAQ says so in its own question. A Visual
      Studio standard subscription is the surest path and renews the sandbox
      for as long as it is active
      ([Visual Studio subscribers](https://learn.microsoft.com/en-us/visualstudio/subscriptions/vs-m365));
      a monthly Visual Studio subscription is not on that renewing route.
      Microsoft may also ask for identity verification. Sign up with a work
      account, a Visual Studio ID or a Microsoft account, never a phone
      number or an `.onmicrosoft.com` address, both of which the program
      refuses.

        **This task was drafted on 21 September 2026 believing the sandbox was
        open to anyone who signed up. It is not**, and the correction matters
        more than the detail: the sandbox is a route this spike may simply not
        have, so step 0's first act is to find out, and the fallback below is
        what the spike actually runs on if the answer is no.

    - **A billing account, which is verification and not a purchase.** Setup
      requires one to be linked and cannot be bypassed: a Microsoft Customer
      Agreement billing account with an active Azure subscription under it.
      The sandbox stays free of charge, and a charge arrives only if somebody
      deliberately buys something. That is not the paid provisioning `D-042`
      rules out, but it is the owner's to approve — see below.
    - **How long it lasts.** Up to 90 days at a time, renewed on development
      activity; after expiry, 30 days to take data out, 30 more where only
      the admin can sign in, and deletion on day 60. Step 0 writes the
      dashboard's expiry date into the report, and the fixtures are committed
      as though the tenant will be gone by the time `T-098` starts, because
      it will be.
- An Entra app registration for "Accounts in any organizational directory and
  personal Microsoft accounts", one web redirect URI at a local address, a
  client secret, and `xms_edov` added as an optional id-token claim under
  its token configuration. It costs nothing and needs no paid tenant. The
  registration is the owner's, because it is the one `T-098` and `T-092` ship
  with (provisional — see below); wherever it is created, it is not created
  inside the sandbox, because an app registration is a directory object and
  goes when its directory does.
- ~~A paid work-or-school tenant (one Business Basic seat is enough) where
  the tester is Global Administrator, with a non-admin member **W1** for the
  consent walk and a creator **W2** (one person on two accounts is fine).~~
  **Answered 21 September 2026 (`D-042`), in two parts.** First choice: the
  E5 developer sandbox above, at no cost and with 25 licences rather than one
  seat. **If its eligibility check fails, which for anyone without a Visual
  Studio Professional or Enterprise standard subscription, ISV Success or
  MAICPP membership, or a Premier or Unified Support contract it will, the
  fallback is a [Microsoft 365 Business one-month trial](https://www.microsoft.com/en-us/microsoft-365/business/microsoft-365-business-standard-one-month-trial)** —
  a real work-or-school tenant with a Global Administrator, users and a
  domain, free for the month, cancelled before it bills by turning off
  recurring billing in the admin center
  ([how](https://learn.microsoft.com/en-us/microsoft-365/commerce/subscriptions/cancel-your-subscription)).
  It is the same answer `T-095` takes for its Plus tier and it is taken for
  the same reason: a cancelled trial costs nothing and observes the working
  path, which is what `PROCESS.md` needs and what `D-042` permits.

    Two things to hold to. **A card is required at signup**, so the
    cancellation is diarised the day the trial starts — an uncancelled trial is
    the purchase `D-042` says not to make, arriving by inattention. **One month
    is not ninety days**, so the work half's fixtures are captured inside it
    and captured generously; there is no coming back to re-observe without
    starting another trial. If neither route is open, the seat is still not
    bought: step 0 stops the work half, the report says which questions that
    leaves unanswered, and the work-or-school tier goes back to the owner, who
    re-approaches or drops it. The spike reports; it does not ask for a card.

- Creator **C1**: a free personal Microsoft account with OneDrive. ~~Creator
  **C2**: a Microsoft 365 Personal or Family account, if available.~~ **Not
  provisioned, 21 September 2026 (`D-042`)** — the personal-tier decision
  above says what that leaves unanswered. Creator **C3**: a second free
  account, throwaway, for the cap count.
- Peers, each with a mailbox the tester can read and a clean browser profile:
  **P1** an outlook.com account; **P2** a Microsoft account on a
  non-Microsoft address (Gmail); **P3** an address with no Microsoft account
  (a fresh Gmail alias never used with Microsoft); **P4** a member of a second
  work tenant ~~(a trial tenant is fine as a Peer's home)~~. P1, P2 and P3
  cost nothing and always did: an outlook.com mailbox, a Gmail alias and a
  Microsoft account on any address are all free. **P4's home is a second
  Microsoft Entra tenant, created free from the Entra admin centre, and not a
  second sandbox (21 September 2026):** a member holds one developer
  subscription and one program account per phone number, so there is no
  second sandbox to be had, while a tenant takes minutes and P4 needs nothing
  from home but a work identity with its own `tid` for Q13 and the guest
  redemption in step 7. Two things go with that choice. Tenant creation is
  refused to an account that is only a free or trial customer
  ([Create a tenant](https://learn.microsoft.com/en-us/entra/fundamentals/create-new-tenant)),
  and the Azure subscription the sandbox's billing step already wants is what
  makes the account a paid one, so step 0 records whether tenant creation is
  offered afterwards. And a bare Entra user has no mailbox, which this
  bullet's opening line assumes: the documented redemption order puts a
  managed tenant's own work account first, so a one-time code should not
  arise, and if one is sent anyway there is nothing to read — that Peer's
  open is recorded unobserved with its reason, or re-run with a Microsoft
  365 Business Basic trial as P4's home, which has a mailbox.
- A phone with the OneDrive app signed in as P1, for one open.
- A stopwatch, `jq` or tinker for pretty-printing, and an editor for the
  placeholder swap.

## Scope

**In:**

- The two account families, walked in the order below; every question in the
  table answered in the report with the observed value.
- The Peer journey walked with the scopes Qori will request: the creator's
  `Files.ReadWrite offline_access`, the Peer's `openid email`.
- The fixtures, their README, the report, the `T-098` and `T-092` edits and
  the one-line `release-prerequisites.md` update.

The questions, the step that answers each, and what each answer means for
`T-098`:

| #   | Question                                                                                                                                                               | Step | If yes / observed                                                                                                                                                                                                          | If no                                                                                                                                                                                                           |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1  | With `sendInvitation: false`, can P1, P2 and P3 open the folder with no step beyond signing in, and did Microsoft email them anyway?                                   | 3, 4 | The invite's 200 is `granted` for that family; the mailbox result decides whether the tier copy may say no email is sent                                                                                                   | A step exists: the row is `awaiting_acceptance` until it is done and the Peer-facing sentence names it. No way in at all: personal tiers are dead for `D-016`'s pattern and `T-098` becomes work-or-school only |
| Q2  | How does the Peer find the folder: the creator's `webUrl` as returned, or only under Shared in their own OneDrive?                                                     | 4    | `T-098` stores the URL that worked as the Open target and the fallback                                                                                                                                                     | —                                                                                                                                                                                                               |
| Q3  | On personal OneDrive, does a file uploaded into the folder later reach P1 with no new invite?                                                                          | 5    | Folder-only; no re-share on new files                                                                                                                                                                                      | Folder plus re-share on every new child, or per-item — a change to `T-091`'s one-row-per-container model, recorded there                                                                                        |
| Q4  | Do files _moved_ into the folder need a new invite (Microsoft says yes), and what does the moved item's permission list show?                                          | 5    | Confirmed; `T-098` re-invites on the folder or on the item, whichever step 5 shows repairs it, and says how it notices a moved-in file — a listing of the folder's children, since retrying old failures discovers nothing | Microsoft's page is wrong for this case; folder-only stands                                                                                                                                                     |
| Q5  | Does a same-name upload (web Replace, and `PUT …/content`) keep the item id and P1's access?                                                                           | 5    | Replace-in-place is the tier copy's advice                                                                                                                                                                                 | Delete-and-re-upload semantics; the Episode needs re-picking and the copy says so                                                                                                                               |
| Q6  | Is the invite response direct (`grantedToV2`) or a link (`link` + `grantedToIdentitiesV2`), and does a repeat, or a Peer who already has access, return that id?       | 3, 7 | `vendor_ref` holds a permission id; revoke may delete it                                                                                                                                                                   | Two Peers on one id: revoke skips link-type permissions and says so                                                                                                                                             |
| Q7  | Work tenant: what does invite return when sharing is "Existing guests" and when guest invites are off?                                                                 | 7    | The error body is a fixture; `T-098` maps it to `needs_creator` and the creator-facing sentence naming the admin setting                                                                                                   | —                                                                                                                                                                                                               |
| Q8  | Work tenant: which sign-in does each Peer meet on the `webUrl`, and is a guest object created at once?                                                                 | 7    | The tier copy states the code-by-email path; `T-092`'s identity is confirmed before payment                                                                                                                                | —                                                                                                                                                                                                               |
| Q9  | Free personal: how many invites before the daily cap, and what does the refusal look like?                                                                             | 8    | The number goes in the tier copy as `:people`; the refusal is a fixture, `pending` with `next_attempt_at` a day out if it names a reset, `needs_creator` if it does not                                                    | No cap reached at 100: the copy says only that Microsoft limits it                                                                                                                                              |
| Q10 | Work tenant: can W1 consent to the unverified app, or is it AADSTS90094?                                                                                               | 7    | Publisher verification is a beta prerequisite with a lead time                                                                                                                                                             | User consent works; verification is still advised for step-up-consent tenants                                                                                                                                   |
| Q11 | Does `GET …/permissions/{PERM_1}` change once P1 has opened the folder — a grantee filled in where the invitation stood — and still show it on a re-read the next day? | 4, 7 | `checkGrant()` has a signal for `granted` on the stored `vendor_ref`; the sweep's re-check of `granted` rows reads it                                                                                                      | `granted` rests on the Peer's first Open through Qori's route; a re-check can only confirm the permission still exists                                                                                          |
| Q12 | How long does one invite call take, from request to response, on each family?                                                                                          | 3, 7 | Under `VendorAccessService::REQUEST_TIMEOUT_SECONDS` (provisional 5): the in-request grant lands and the Peer waits for nobody                                                                                             | Over it: every in-request grant lands `pending` and the sweep is the real path; `T-098` says so, and `T-091`'s value is questioned                                                                              |
| Q13 | Do `oid`, `tid`, `email` and `xms_edov` arrive in the id token for a personal account through `/common`, and for a work-tenant guest?                                  | 9    | `T-092` keys OneDrive identities on `oid` + `tid` and requires `xms_edov`; the personal `tid` is recorded for `T-098`'s grant                                                                                              | `xms_edov` is missing on personal accounts: `T-092` stores it nullable and `T-098` says how a personal address is trusted                                                                                       |

Steps. **Step 0 settles the free path before any other fixture is gathered
(`D-042`), and the ten steps after it keep the numbers they have**, because
`T-098` cites four of them by number — steps 3, 7 and 8 at
`T-098:164`, `T-098:255`, `T-098:333` and `T-098:685` — and a renumbering
would silently redirect every one. Steps 1 to 6, step 8 and step 9's P1
round trip are the personal half: they need only free accounts, so they
start on day one alongside step 0 rather than behind it. Step 7 and step 9's
P4 round trip are the work half and run only once step 0 has a sandbox.

0. **Settle the free path.** Check eligibility against the three qualifying
   paths in the developer program's FAQ (Equipment). **Where one holds**,
   set up the sandbox: link the billing account, record which path it came
   through and the expiry date the dashboard shows, and name the
   administrator account. **Where none holds — the likely case — start a
   Microsoft 365 Business one-month trial instead** (Equipment), diarise its
   cancellation the same hour, and record the tenant, the admin account and
   the date the month ends; everything below then runs against the trial
   tenant and must finish inside it. Where neither route is open, stop here
   and report. Then the smallest set of calls that can say
   whether a sandbox shares outside itself at all: as W2, connect with the
   same registration, make step 2's `Series spike/` in W2's OneDrive with
   `episode.pdf` in it, read the SharePoint admin centre's OneDrive sharing
   level and record it as found — step 7 restores that baseline later — and
   send one `POST …/invite` for P3's address, body exactly as step 3's.
   A 200 is the free path working: capture it as `invite-work-200.json`
   with its seconds, and step 7 continues from this connection, this folder
   and this recorded baseline. A refusal is the work half's answer: capture
   the body, name it in the README as where the work half stopped, and write
   in the report what that leaves unanswered. Either way nothing else
   happens here — no Peers, no content set, no admin settings flipped — and
   either way nothing is bought.
1. **Connect C1.** Authorization code with `Files.ReadWrite offline_access`,
   exchange it, capture the token response and keep its access token aside
   for step 6. Refresh once, capture, and refresh again with the _old_
   refresh token; record whether the old one still works
   ([Refresh tokens](https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens)
   says it is replaced on every use but not revoked).
2. **Set up.** `GET /me/drive` for `DRIVE_ID`. In the web app make
   `Series spike/` — this one Series' folder and nobody else's — with
   `episode.pdf` and `episode.mp4` inside, and `Elsewhere/moved.pdf` outside
   it. `GET …/children` on the folder. Make `Series spike 2/` beside it,
   empty, for step 6's container-replacement check.
3. **Invite.** P1, P2 and P3 in three separate calls; capture each status and
   body, and the seconds each call took. Wait ten minutes; check all three
   mailboxes for anything from Microsoft. Invite P1 again; compare ids. Send
   one call with `requireSignIn: false, sendInvitation: false`; capture the 400.
4. **Take-up.** `GET …/permissions/{PERM_1}` before P1 has opened anything;
   capture. As P1 in a clean profile: open the folder's `webUrl` signed out,
   then signed in; open onedrive.live.com and look under Shared; record which
   of the three showed the folder, any step Microsoft put between sign-in and
   the folder, and the stopwatch time from step 3's 200 to the first open.
   `GET …/permissions/{PERM_1}` again; capture, and once more the next day.
   Open `episode.mp4` and `episode.pdf`; record the URL of each as opened.
   Open once in the phone app. Repeat as P2. As P3, create a Microsoft account
   on the invited address only now, then repeat; record whether the earlier
   grant is honoured without a new invite.
5. **Currency.** As C1: upload `new-web.pdf` through the web app; `PUT`
   `new-api.pdf` through the API; Replace `episode.pdf` through the web app
   with a same-name upload, then `PUT …/items/FILE_PDF_ID/content` with new
   bytes; Move `Elsewhere/moved.pdf` into the folder with the web app's Move
   to. After each, `GET …/permissions` on the item, `GET …/children` on the
   folder, and as P1 refresh the folder and open the item. If `moved.pdf` is
   not visible: invite P1 on the _folder_ again, recheck; if still not,
   invite P1 on `MOVED_ID` itself, recheck. Record which call repaired it.
6. **Revoke, the replaced container, and the recoverable failure.** `DELETE`
   P2's permission; confirm P1 still opens. Invite P1 on `Series spike 2/`,
   then `GET …/permissions` on both folders and confirm each grant stands on
   its own — what a replaced container leaves behind. Then send step 3's P1
   invite again with step 1's first access token, expired by now; capture the 401.
7. **Work tenant, from step 0's sandbox.** As W1, run the consent screen for
   the same registration; capture the redirect's `error` and
   `error_description` or the consent page. As W2, on step 0's connection
   and folder, finish the content set as step 2 has it and invite P1 and P4
   in separate calls; capture, with seconds — P3's invite is step 0's, and
   its seconds count as one of the three. In the Entra portal, record
   whether each appears under Users as a guest within a minute. Each Peer
   opens the folder's `webUrl`: record the sign-in met (work account,
   Microsoft account, one-time code), the consent page, and the time;
   re-read that Peer's permission before and after, as in step 4.
   `GET …/permissions`; record direct or link and whether any two Peers
   share one id. Repeat step 5. `DELETE` P1's permission; confirm P3 still
   opens. In the SharePoint admin centre set OneDrive sharing to
   "Existing guests", invite a new address, capture; set it back and set
   Entra guest invite settings to "No one in the organization can invite
   guest users", invite, capture; restore both.
8. **Cap, and the other account's ids.** As C3,
   `GET /drives/{DRIVE_ID}/items/{FOLDER_ID}` with C1's ids; capture. Then on
   one folder of C3's own, invite `peer-cap+N@…` aliases of the P3 mailbox
   from N=1 until the first refusal or N=100; record N, the refusal body and
   headers. If step 3 showed personal drives refuse an address with no
   Microsoft account, invite P1 to N fresh folders instead.
9. **Sign in.** As P1, then as P4, an authorization-code round trip against
   the same registration through `/common` with `scope=openid email`; capture
   the token response, decode the id token and capture its claims.
10. **Write it down.** Fixtures and README, the report, the `T-098` and
    `T-092` edits, the `release-prerequisites.md` line.

**Out:**

- Anything under `app/`, `routes/`, `lang/` or `resources/`; the OAuth
  connect step is `T-098`'s and the generic connect machinery `T-044`'s.
- Building Sign in with Microsoft (`T-092`): step 9 captures the token it
  will consume, and the spike reads each Peer's address from the mailbox it
  owns.
- The v8 File Picker and its SharePoint scopes; `T-098` lists through Graph.
- Download blocking, `createLink` and `revokeGrants` (both beta), and how
  fast a deleted permission ends an open session: downloads and airtight
  revocation are not concerns (`D-016`).
- `expirationDateTime`, `password`, Personal Vault, `Files.ReadWrite.All` and
  team sites.
- Teams, and moving a Teams recording into the folder (`T-101`).
- Deciding the state mapping and the tier copy. The observed bodies, numbers
  and paths feed `T-044` and `T-098`; the mapping and the sentences are
  theirs.
- The paid path. A delayed payment becoming access and a refund revoking the
  grant are `T-102` and `T-103`, which land before any paid Series uses a
  provider here; nothing in this spike is run against money.

## Files

| Path                                                                                                                                                                                                                        | Change | Notes                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/Fixtures/microsoft/README.md`                                                                                                                                                                                        | new    | One row per fixture: file, request, status, headers that matter, seconds, account family, date                                          |
| `tests/Fixtures/microsoft/token-authorization-code.json` `tests/Fixtures/microsoft/token-refresh.json`                                                                                                                      | new    | Step 1, tokens replaced                                                                                                                 |
| `tests/Fixtures/microsoft/drive-me.json` `tests/Fixtures/microsoft/children-folder.json`                                                                                                                                    | new    | Steps 2 and 5; the children listing is the one taken after the upload and the move                                                      |
| `tests/Fixtures/microsoft/invite-personal-200.json` `tests/Fixtures/microsoft/invite-personal-repeat.json` `tests/Fixtures/microsoft/invite-personal-no-account.json` `tests/Fixtures/microsoft/invite-400-both-false.json` | new    | Step 3; `no-account` is P3's, whatever status it is; `repeat` is the repeated grant                                                     |
| `tests/Fixtures/microsoft/permission-get-before-open.json` `tests/Fixtures/microsoft/permission-get-after-open.json` `tests/Fixtures/microsoft/permission-get-next-day.json`                                                | new    | Steps 4 and 7 (`-work` suffix); P1's permission re-read before the first open, after it, and the next day                               |
| `tests/Fixtures/microsoft/invite-work-200.json` `tests/Fixtures/microsoft/invite-work-207.json` `tests/Fixtures/microsoft/invite-work-existing-guests.json` `tests/Fixtures/microsoft/invite-work-guest-invites-off.json`   | new    | Step 7; `207` only if observed, and the README says so if it was not                                                                    |
| `tests/Fixtures/microsoft/permissions-folder.json` `tests/Fixtures/microsoft/permissions-uploaded-item.json` `tests/Fixtures/microsoft/permissions-moved-item.json`                                                         | new    | Step 5, personal; the work-tenant copies take a `-work` suffix                                                                          |
| `tests/Fixtures/microsoft/item-replace-put-content.json`                                                                                                                                                                    | new    | Step 5, the driveItem returned by the `PUT`                                                                                             |
| `tests/Fixtures/microsoft/invite-401-expired-token.json` `tests/Fixtures/microsoft/permissions-second-folder.json` `tests/Fixtures/microsoft/item-other-account.json`                                                       | new    | Steps 6 and 8; the recoverable failure, the replaced container's own permission list, and a container read with another account's token |
| `tests/Fixtures/microsoft/invite-personal-cap.json` `tests/Fixtures/microsoft/invite-429.json`                                                                                                                              | new    | Steps 8 and any step; each only if reached, with `Retry-After` in the README row                                                        |
| `tests/Fixtures/microsoft/oidc-token-personal.json` `tests/Fixtures/microsoft/oidc-claims-personal.json` `tests/Fixtures/microsoft/oidc-token-work.json` `tests/Fixtures/microsoft/oidc-claims-work.json`                   | new    | Step 9; the token response with tokens replaced, and the decoded id-token payload — `T-092`'s fixture, consumed by `T-098`              |
| `tests/Fixtures/microsoft/consent-w1.txt`                                                                                                                                                                                   | new    | Step 7, the redirect query string as text, or one line saying consent was offered                                                       |
| `docs/planning/tasks/reports/T-097-YYYY-MM-DD-<owner>.md`                                                                                                                                                                   | new    | The report; every question above answered by number, timings, and what could not be run                                                 |
| `docs/planning/tasks/T-098-onedrive-episodes-from-a-folder-shared-with-each-peer.md`                                                                                                                                        | edit   | Strike each bullet answered, with date and fixture; a Notes line naming the report while it is a bare template                          |
| `docs/planning/tasks/T-092-a-peer-confirms-the-vendor-account-they-will-open-with.md`                                                                                                                                       | edit   | Strike its `xms_edov` bullet under "Before this can be ready" with the date and the claims fixture                                      |
| `docs/planning/release-prerequisites.md`                                                                                                                                                                                    | edit   | Line 20: whether publisher verification is required, from Q10, and what it needs                                                        |

Flows: none — no code changes; nothing under `app/` or `routes/` is touched.

## Database

None.

## Code

None under `app/`. The literal calls, so two testers capture the same
fixtures. Request and response field names below are as documented on the
pages cited, not observed; the fixture is what turns each into an observation.

```http
# Step 0 — no call of its own: step 1's authorize/token pair as W2, then step 3's invite body once, for P3

# Step 1 — authority `common` serves both families; `consumers` if a personal account refuses it
GET  https://login.microsoftonline.com/common/oauth2/v2.0/authorize
     ?client_id=…&response_type=code&redirect_uri=…&response_mode=query
     &scope=Files.ReadWrite%20offline_access&state=spike
POST https://login.microsoftonline.com/common/oauth2/v2.0/token
     grant_type=authorization_code | grant_type=refresh_token

# Step 2
GET  https://graph.microsoft.com/v1.0/me/drive
GET  https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FOLDER_ID}/children

# Step 3 — one recipient per call; body exactly this
POST https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FOLDER_ID}/invite
     {"recipients":[{"email":"peer-1@example.com"}],"roles":["read"],"requireSignIn":true,"sendInvitation":false}

# Step 4 — before the first open, after it, and the next day
GET  https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FOLDER_ID}/permissions/{PERM_1}

# Step 5
PUT  https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FOLDER_ID}:/new-api.pdf:/content
PUT  https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FILE_PDF_ID}/content
GET  https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{MOVED_ID}/permissions

# Step 6
DELETE https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FOLDER_ID}/permissions/{PERM_2}
POST   …/invite as in step 3, with step 1's first access token — the 401

# Step 8 — C3's token, C1's ids
GET  https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FOLDER_ID}

# Step 9 — the Peer, same registration
GET  https://login.microsoftonline.com/common/oauth2/v2.0/authorize
     ?client_id=…&response_type=code&redirect_uri=…&response_mode=query
     &scope=openid%20email&state=spike-peer
POST https://login.microsoftonline.com/common/oauth2/v2.0/token
     grant_type=authorization_code
```

Sources for each call and the fields the fixture is expected to show:

| Call                                          | Page                                                                                                                                                                     | Documented, not yet observed                                                                                                                                         |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST …/invite`                               | <https://learn.microsoft.com/en-us/graph/api/driveitem-invite?view=graph-rest-1.0>                                                                                       | 200 with `value[]` of permissions (`id`, `roles`, `grantedToV2`, `invitation.email`, `invitation.signInRequired`), or 207 partial; no permissions on a personal root |
| `GET …/permissions`, `GET …/permissions/{id}` | <https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0>, <https://learn.microsoft.com/en-us/graph/api/permission-get?view=graph-rest-1.0> | `link` and `grantedToIdentitiesV2` on a link-type row; `inheritedFrom` on an inherited one; grantee empty until redeemed                                             |
| `DELETE …/permissions`                        | <https://learn.microsoft.com/en-us/graph/api/permission-delete?view=graph-rest-1.0>                                                                                      | 204; only non-inherited permissions can be deleted                                                                                                                   |
| `GET …/children`, drive, item                 | <https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0>                                                                                    | `id` unique within the drive; `webUrl` is the only documented page a person opens; what another account's token gets for the id is not stated                        |
| `PUT …/content`                               | <https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0>                                                                                  | Updates an existing item's bytes, up to 250 MB; whether the id survives is implied, not stated                                                                       |
| Token endpoint                                | <https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens>                                                                                               | 90-day refresh token, replaced on every use; personal-account lifetimes not covered by that page; the 401 for an expired access token is not shown                   |
| Id token claims                               | <https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference>                                                                                    | `email` may be wrong or change and must not authorise; `xms_edov` says whether it was verified; `oid` + `tid` identify the account                                   |
| Throttling                                    | <https://learn.microsoft.com/en-us/sharepoint/dev/general-development/how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online>                                    | 429 or 503 with `Retry-After`; 3,000 requests per 5 minutes per user, licence-dependent tenant budgets, and five resource units per permission call, reads included  |

Tier facts the report checks its observations against, so a surprise is
called one:

| Fact                                                                                                                                      | Page                                                                                                                                                 |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Personal accounts "can only choose people who also have Microsoft personal account"                                                       | <https://support.microsoft.com/en-us/office/external-or-guest-sharing-in-onedrive-sharepoint-and-lists-7aa070b8-d094-4921-9dd9-86392f2a79e7>         |
| From May 2026 every work-tenant share creates an Entra guest, no opt-out                                                                  | <https://learn.microsoft.com/en-us/sharepoint/sharepoint-azureb2b-integration>, <https://mc.merill.net/message/MC1243549>                            |
| Redemption order: work account, federation, Microsoft account, one-time code (30 min, 24 h session); an alias redeems only from the email | <https://learn.microsoft.com/en-us/entra/external-id/redemption-experience>, <https://learn.microsoft.com/en-us/entra/external-id/one-time-passcode> |
| Four sharing levels; OneDrive no looser than SharePoint                                                                                   | <https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off>                                                                       |
| Guest invite settings and domain lists                                                                                                    | <https://learn.microsoft.com/en-us/entra/external-id/external-collaboration-settings-configure>                                                      |
| B2B invitation caps: 10 or 100 a day unpaid, 200 a day for a paid tenant under 30 days old                                                | <https://learn.microsoft.com/en-us/entra/identity/users/directory-service-limits-restrictions>                                                       |
| Work or school: 50,000 unique permissions supported per library item, 5,000 recommended — one per Peer                                    | <https://learn.microsoft.com/en-us/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits>                     |
| `Files.ReadWrite` user-consentable under the managed policy; the `.All` scopes not                                                        | <https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/manage-app-consent-policies>                                                       |
| Step-up consent blocks unverified multi-tenant apps by default                                                                            | <https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-risk-based-step-up-consent>                                              |
| A same-name upload becomes the latest version in a versioned library                                                                      | <https://support.microsoft.com/en-us/office/upload-files-and-folders-to-a-library-da549fb1-1fcb-4167-87d0-4693e93cb7a0>                              |

## Copy

None. The tier sentences the answers feed belong to `T-044` and `T-098`.

## Routes

None.

## Tests

None. The spike adds no code; its fixtures are consumed by `T-098`'s tests,
which name them.

## Acceptance

- [ ] The report opens on step 0: the eligibility path the sandbox came
      through, the expiry date on the dashboard, the tenant's OneDrive
      sharing level as found, and the probe invite's status and seconds — or,
      where no sandbox could be had, the work-tenant questions that leaves
      unanswered, handed back to the owner under `D-042` rather than bought
      around
- [ ] Q1 to Q13 each answered in the report by number, with the observed
      value, the account family, the date, and the stopwatch time and the
      call's seconds where one was asked for
- [ ] The report says, per account family, whether both first access and
      later content worked, so `T-098` can advertise only the families that
      were tested rather than "OneDrive"
- [ ] Every fixture in the Files table either committed with placeholders
      swapped, or named in the README as not reached and why — the repeated
      grant, the 401 and the other-account read among them
- [ ] `tests/Fixtures/microsoft/README.md` has one row per fixture with the
      request, status, the headers that matter, the seconds and the date
- [ ] `T-098` carries the answers: struck bullets with the date and fixture
      where it has bullets, else a Notes line naming the report; `T-092`'s
      `xms_edov` bullet struck the same way
- [ ] `release-prerequisites.md:20` says whether publisher verification is
      required and what it needs, from Q10
- [ ] The report's "Could not verify" names every step skipped for want of
      equipment, C2 among them, which `D-042` does not provision
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Whether the Entra app registration is created now under the owner's
  account, so the redirect URIs, the `xms_edov` optional claim and the
  publisher domain are the ones `T-098` and `T-092` ship with, or under the
  tester's and re-created later — the owner's. Either way it is not
  registered inside the sandbox, which is deleted on a timer (Equipment).
- **Which of the two free routes the owner has, which step 0 settles and
  nobody else can.** The E5 developer sandbox needs one of three
  relationships — a Visual Studio Professional or Enterprise standard
  subscription, ISV Success or an eligible MAICPP tier, or a Premier or
  Unified Support contract — and there is no fourth. It also needs a
  Microsoft Customer Agreement billing account with an active Azure
  subscription linked, which cannot be bypassed; that is verification rather
  than a purchase, and nothing is charged, but it is the owner's billing
  identity and their call. The Microsoft 365 Business one-month trial needs
  none of that and does need a card at signup, cancelled before the month
  ends. **Ninety renewable days against thirty, versus a billing identity
  against a card** — the owner picks, and if they hold a qualifying Visual
  Studio subscription the sandbox is plainly better, because `T-098` is an
  `L` six tasks away and a renewable tenant outlives a trial — the owner's.
- ~~Whether a paid work-or-school tenant the tester administers exists or is
  bought for the spike (one Business Basic seat), since a trial tenant
  restricts external sharing and would make step 7 unrepresentative — the
  owner's.~~ **Answered 21 September 2026 (`D-042`):** neither. The tenant is
  the free E5 developer sandbox (Equipment), the trial-tenant worry is what
  step 0's probe invite now measures instead of assuming, and no seat is
  bought if the sandbox cannot be had.
- ~~Whether a Microsoft 365 Personal or Family subscription is available for
  C2, or the personal tier is spiked on free alone and Personal's cap stays
  "higher, unpublished" in the copy — the owner's.~~ **Answered 21 September
  2026 (`D-042`):** on free alone. C2 is not provisioned, Q9's number is free
  OneDrive's and is labelled as such, and `T-098` states no cap for the paid
  personal subscriptions rather than guessing one.
- Whether the fixture format (raw body plus a README row) is the one `T-093`
  and `T-095` also use, so the three vendor directories read the same way;
  `T-093` names files by call and case and `T-095` by
  `<namespace>/<route>.<case>.<status>.json`, and whichever spike lands first
  sets it — anyone's.
- Whether step 8's cap count is worth a day of a throwaway account, or the
  copy says only that Microsoft limits daily sharing and a refused grant is
  retried tomorrow — the owner's.
- **From the storage review's rate-limit table (20 September 2026):** the
  sources table's throttling row read "300 sharing calls per 5 minutes per app
  per tenant", a figure Microsoft's SharePoint throttling guidance (`V5`, the
  page that row already cites and the one Graph's service limits send a file
  caller to) does not give. **Corrected in place:** the row now says 3,000
  requests per five minutes per user, licence-dependent tenant budgets, and
  five resource units for every permission call, reads included. So a
  permission list spends the budget although it mutates nothing, and no
  SharePoint number may be carried across to consumer OneDrive unqualified:
  step 8's count and Q9's number say which family and which budget they
  measured, and step 7's captures keep the throttling headers that show it —
  anyone's.
- **From the storage review, F11 and its evidence table (20 September 2026):**
  the OneDrive row it owns asks that this spike run separately for personal and
  for work accounts — silent redemption, the permission's shape, removing one
  member of a shared link, the moved-in file's repair, the verified identity
  claims and the throttles — and that where one Peer cannot be taken off a
  shared permission, what Qori is left holding is observed rather than
  inferred. Q6 disposes of that case in a clause ("revoke skips link-type
  permissions and says so") and no such permission has been seen. What cannot
  safely be produced stays unobserved in the report with its reason, and an
  exception to the evidence rule is the owner's to record rather than the
  spike's to waive — the owner's, with step 8's bullet above.
- **From the storage review, F10 (20 September 2026):** `D-036` moved Google
  Drive's grants onto files and decides nothing for OneDrive. Whether a
  OneDrive grant stands on the Series folder or on each item is this spike's,
  and Q3, Q4 and Q6 are where that answer comes from; `T-091`'s
  container-shaped queries and tests are not frozen until this spike and
  `T-095` have both answered — anyone's, with `T-091`.

## Re-scope log

None.

## Notes

The spike runs in September 2026, inside the window where Microsoft's two
dates for retiring SharePoint's own verification codes disagree — July per
the FAQ, 1–31 October per MC1243549. A work-tenant Peer may meet either
sign-in; the report says which.

`T-098` is the bare template today, with `depends: none` and `blocks: none`,
while this file says `blocks: T-098`; the board's derivation check will want
`T-098` to say `depends: T-097` when it is specified, and that edit is
`T-098`'s. `T-092`'s "Before this can be ready" asks this spike whether
`xms_edov` arrives for personal accounts through `/common` and whether the
tenant matters for a personal-versus-work grant; Q13 and the `tid` in each
claims fixture answer it.

Fixture names are provisional until observed: `invite-work-207.json` and
`invite-429.json` exist only if reached, and `invite-personal-no-account`
may turn out to be a 200 rather than an error. The README row says which.

`release-prerequisites.md:20` says the research "did not confirm" publisher
verification is required; the step-up-consent page above says unverified
multi-tenant apps are blocked for user consent by default. Q10 settles it.

Community reports describe invites whose permissions never took effect for
external users
(<https://learn.microsoft.com/en-us/answers/questions/1332382/microsoft-graph-api-drives-((drive-id))-items-((it>),
which is why step 4 waits and times rather than taking a 200 for access.
