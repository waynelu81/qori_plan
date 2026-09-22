---
id: T-097
title: Spike: OneDrive silent invites and moved files
stream: storage
status: ready
owner: claude
estimate: S
depends: none
blocks: T-098
---

# T-097 — Spike: OneDrive silent invites and moved files

> **Ready, 22 September 2026**, brought there under `D-043` by resolving the
> seven open bullets at the bottom from the code, Microsoft's own pages and
> the equipment list; none needed the owner. Step 0 gained an invite on one
> file the same day, because `T-160` had shipped an item-only grant contract
> that a OneDrive grant on a file could reuse. **Running it needs the
> Equipment under Preconditions**, which is the owner's to supply, starting
> with a work tenant by whichever free route they have. Written on 16
> September 2026 from
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
was observed, and `T-098` ~~— the bare template today — carries a Notes line
naming that report until it is specified from it~~ carries the answers as
struck bullets, being no longer the bare template this said (22 September
2026). `T-092` puts the Peer's
Microsoft id-token fixture on this spike (`T-092`, Preconditions), so the
Peer's sign-in is captured here as well.

~~Nothing under `app/` mentions Microsoft today. `app/Integrations/` holds
Dropbox, Qori, Stripe and Vimeo; `App\Enums\ConnectionProvider` and
`App\Enums\EpisodeProvider` have no OneDrive case; the only trace is the
comment at `app/Providers/IntegrationServiceProvider.php:33-34` saying OneDrive
is "a class and a line here". That is `T-098`'s to change, not this task's.
Nor does `T-091`'s machinery exist: `vendor_grants`, `VendorGrantStatus`,
`VendorAccessService` and `qori:access:reconcile` are that draft's names, and
every one this file borrows is a spec's name rather than a class on disk.~~
**Re-read against the code on 22 September 2026.** There is still no
Microsoft integration. `app/Integrations/` holds Cloudflare, CloudflareR2,
Contracts, Dropbox, EuropeanCentralBank, Google, Stripe and Vimeo, and
neither `App\Enums\ConnectionProvider` nor `App\Enums\EpisodeProvider` has a
OneDrive case (`app/Enums/EpisodeProvider.php:75` says `T-098` adds it).
Microsoft is named only in comments and as Teams' vendor
(`app/Enums/ConnectionProvider.php:87`), and the comment saying OneDrive is
"a class and a line here" is now at
`app/Providers/IntegrationServiceProvider.php:50-52`. That is still
`T-098`'s to change. The last sentence is what no longer holds. `T-160`
built three of those four names on 21 September: the `vendor_grants` table
(`database/migrations/2026_09_21_000000_create_vendor_grants_table.php`),
`app/Enums/VendorGrantStatus.php` and `app/Services/VendorAccessService.php`,
on the item-only contract described under Decisions. The fourth,
`qori:access:reconcile`, will never be built, because `D-040` removed the
sweep it was for.

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
keeps that honest. **22 September 2026:** read "where no sandbox can be had"
as "where neither free route is open". `D-042`'s own correction of the same
day put a vendor's trial, cancelled before it bills, after the developer
programme, so Equipment and step 0 fall back to a Microsoft 365 Business
one-month trial when the sandbox's eligibility fails, and the work half stops
as this paragraph says only when neither route is open.

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
it. ~~Per-item is a change to `T-091`'s one grant row per (Access, container),
recorded there and never hidden in the connector.~~ **22 September 2026:**
per-item is no longer a change to `T-091`, nor only a fallback. `T-160` has
built an item-only contract, and step 0 now measures a grant on one file on
its own terms, before the folder's; the next paragraphs say why and in which
order. The permission listing on `new-web.pdf`, which is no Episode, is also
what proves the picker copy's line that sharing the folder shares everything
inside it.

**Step 0 asks about one file as well as the folder, because a grant on a
file is now the cheap model** (22 September 2026). This spike was drafted
when `D-016` meant one shared folder per Series and `T-091` was the only
foundation a OneDrive grant could stand on. On 21 September `T-160` shipped
Google Drive's grant at Open without waiting for `T-091`, on an **item-only**
contract:
`GrantsItemAccess::grantReader(Connection $connection, string $itemId, string $email, int $timeoutSeconds): GrantResult`
(`app/Integrations/Contracts/GrantsItemAccess.php:16-26`), called from
`VendorAccessService::ensureGrant()`
(`app/Services/VendorAccessService.php:48-95`), which keeps one `VendorGrant`
row per Access and Episode with `GrantTarget::Item` (`app/Models/VendorGrant.php`,
`app/Enums/GrantTarget.php`). A provider that can grant on a single file
implements that contract, joins the `item-granters` tag as one more class
(`app/Providers/IntegrationServiceProvider.php:59-65`), and needs none of
`T-091`'s container machinery. Graph's invite takes any driveItem, a file as
well as a folder (the invite page in the sources table under Code), so the
same body answers both models for one more call.

**That is worth a lot, because `T-091` is the stream's largest draft and is
out of step with what `T-160` built.** It is an `L` of 2,612 lines. Its
draft sets `REQUEST_TIMEOUT_SECONDS` to 6 (`T-091:1164`) where the code has 8
(`app/Services/VendorAccessService.php:34`); it re-reads a `granted` row
through `checkGrant()` at Open (`T-091:324-333`) where `ensureGrant()` trusts
one with no vendor call (`app/Services/VendorAccessService.php:71-73`); and
its table has `attempts`, `next_attempt_at`, `checked_at` and `revoked_at`
(`T-091:971-975`), none of which `vendor_grants` has
(`database/migrations/2026_09_21_000000_create_vendor_grants_table.php:21-41`).
A `T-098` on files would not wait for that to be reconciled. It would drop
its own `depends: T-091`, though not every path to it: `T-092` and `T-094`,
which `T-098` also depends on, both depend on `T-091`, and whether the file
route needs them is `T-098`'s to settle. `T-160` grants to the Peer's Qori
address without `T-092` (`app/Services/VendorAccessService.php:66-67`).

**The file goes first, and the order is the measurement.** `episode.pdf` sits
inside `Series spike/`, and what is inside a shared folder inherits its
permission (`inheritedFrom`, in the sources table). Invited on the file after
the folder, P3 would already reach it: the invite would meet the case the
Microsoft Q&A thread under "Revoke is checked" reports answering 200 with no
new permission, and P3's open could not be told from the folder's. So step 0
invites P3 on the file, reads that permission, has P3 open the file and reads
it again, and only then invites P3 on the folder. Two consequences follow,
and the README states both. P3's first sign-in to the tenant is on the file,
so Q8's row for P3 is step 0's. And `invite-work-200.json` is a folder
invite to an address the tenant already holds as a guest, while step 7's
invites of P1 and P4 are the folder invites to new addresses, and are named
for them.

**"Works" means P3 got in, not only that the invite answered 200, and for the
file that decides whether the contract can be reused as it stands.**
`T-160`'s Open sends a Peer on to the vendor only when the row is `granted`.
Every other state sends them back to the Series with a notice
(`app/Services/PlaybackTicketService.php:74-81`,
`app/Http/Controllers/Shared/OpenEpisodeController.php:40-53`), and
`shared.vendor_notice` has lines for `awaiting_identity`, `needs_creator` and
`pending` only (`lang/en/shared.php:28-30`). If a silent file invite leaves P3
a step to take at Microsoft, its 200 is `awaiting_acceptance`, Open would
never send P3 to take that step, and `T-098` would have to change Open as
well as add a granter.

What each outcome of step 0 means for `T-098` (Q14):

- **Both routes work.** `T-098` chooses, and the file route lets it reuse
  `GrantsItemAccess` and drop its own dependency on `T-091`, as above.
- **Only the folder works.** `T-098` stays on the container model and waits
  on `T-091`.
- **Only the file works.** The per-file route is the only one on this
  family, and step 7 runs on the file.
- **Neither works.** The work half stops, as step 0 always said.

**What step 0 does not settle is the personal family.** Step 0 runs in the
work tenant, and the personal half is asked of the folder alone, as before. A
file route for personal accounts would rest on no observation here, and the
report says so rather than carrying the work tenant's answer across. This
spike still does not choose `T-098`'s model; the report recommends one.

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
to write, from these fixtures. **Corrected 22 September 2026:** the states are
a class on disk now, `app/Enums/VendorGrantStatus.php`, with eight cases
rather than six. `T-160` took all of `T-091`'s, including `attempting`, a
create whose answer never came back (`T-091`'s `F01`), and `revoke_failed`, a
removal Qori could not make (`D-040`). Neither adds a question here: a
timed-out invite (Q12) is where `attempting` would come from, and a refused
`DELETE` in step 6 or 7 is where `revoke_failed` would. And since `D-040`,
`pending` is retried by the Peer's next Open, not by Qori on its own.

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
and again the next day.** ~~`T-091` re-checks `awaiting_acceptance` and
`granted` rows through `checkGrant()` — on Open before a `granted` row is
trusted, and from `qori:access:reconcile`, which sweeps every few minutes
(provisional) and re-reads a `granted` row on a longer cadence (`checked_at`,
provisional interval) — so current access is verified, not only first
access.~~ **Corrected 22 September 2026:** `D-040` removed the sweep.
`T-091`'s draft re-reads an `awaiting_acceptance` or `granted` row through
`checkGrant()` at Open and nowhere else (`T-091:324-333`), and `T-160`'s code
re-reads nothing: a `granted` row sends the Peer on with no vendor call
(`app/Services/VendorAccessService.php:71-73`). What the permission shows
once the Peer has taken the grant up is what either design would read,
`T-091`'s to promote an `awaiting_acceptance` row and a `T-098` on `T-160`'s
code to decide whether an invite's 200 may be written `granted` at all. That
only works if `GET …/permissions/{PERM_1}` looks different once the Peer has
taken the grant up. Q11 is that measurement, and step 0 takes it on the file
as well.

**The invite call's own wall time is recorded beside the stopwatch.** ~~`T-091`
grants inside the request that creates the Access, under
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` (provisional 5), and a timeout
leaves the row `pending` for the sweep. If an invite commonly takes longer
than that, priority 1 is served by the sweep and not by the request, and
`T-098` has to say so.~~ **Corrected 22 September 2026 (`D-040`, `T-160`):**
the grant is made when the Peer presses Open, inside that request, under
`VendorAccessService::REQUEST_TIMEOUT_SECONDS`, which is 8 on disk
(`app/Services/VendorAccessService.php:34`) where `T-091`'s draft says 6
(`T-091:1164`). A timeout leaves the row `pending`, and the Peer's next Open
sends the invite again, which is Q6's repeat. If an invite commonly takes
longer than the budget, a Peer's first Open fails, and `T-098` has to say so.
Q12 is that measurement; the seconds go in the README row beside each fixture.

**One repeated grant, one recoverable failure and one different-account read
are provoked on purpose.** The developer review of 16 September 2026 asks
every provider for a repeated grant and a recoverable failure on record. The
repeat is step 3's second invite of P1 (Q6). The recoverable failure is an
invite sent with step 1's first access token after it has expired — the 401 a
refresh recovers inside the same request, as opposed to the failed refresh
that is `needs_creator`. The different-account read is C3 fetching C1's
folder by id (step 8): what `checkContainer()` meets after the creator
connects another account, which `T-091` answers by marking containers for a
new pick. None of the three is a test; each is a fixture. **22 September
2026:** a fourth is provoked now, for `F11`: a permission two Peers share,
made from OneDrive's own Share dialog in steps 6 and 7 (Before this can be
ready).

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
day. **Kept on 22 September 2026** rather than dropped, for the reasons under
Before this can be ready.

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
the question. **22 September 2026:** or, where the sandbox's eligibility
fails, the one-month Business trial under Equipment, whose first user is its
Global Administrator too. The restriction on trial tenants cited above is
then exactly what step 0's two invites measure, on the tenant the spike
actually has.

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
holds a permission when it is sent. **22 September 2026 (`F11`):** where the
spike finds an id two Peers share, it sends the delete anyway: `T-098` would
skip it, and only a delete sent on the spike's own folder shows what that
skip protects. The spike also makes one such permission on purpose in steps
6 and 7 rather than waiting for an invite to return one. Taking one Peer off a
shared permission would need `revokeGrants`, which is beta, is not offered for
personal accounts at all
([revokeGrants](https://learn.microsoft.com/en-us/graph/api/permission-revokegrants?view=graph-rest-beta)),
and stays out of scope, so what is observed is what a `DELETE` does to
everyone on it.

**Fixtures are raw response bodies with ids swapped for fixed placeholders,
and one `README.md` beside them records the request, status, headers, seconds
and date per file.** ~~No `tests/Fixtures/<vendor>/` directory exists yet
(`tests/Fixtures/` holds `planning` and `reachability`), and every vendor test
today fakes with an inline `Http::response([...])`, so there is no loader to
fit.~~ A raw body is what `Http::response(file_get_contents(...), $status)`
takes; the status and any `Retry-After` live in the README row. ~~A `204` has
no body and gets no file, only a row.~~ (Both struck on 22 September 2026;
the next paragraph says what replaced them.) **Capture generously rather than
sparely, because the tenant will not be there when it is wanted:** `T-098` is
an `L` behind `T-044`, `T-091`, `T-092`, `T-094`, this spike and `T-152`,
while the sandbox lasts 90 days at a time and only renews on real
development activity — after it expires there are 30 days to take data out,
30 more where only the admin can sign in, and deletion on day 60
([FAQ](https://learn.microsoft.com/en-us/office/developer-program/microsoft-365-developer-program-faq)).
What these fixtures do not hold is what `T-098` cannot be specified from, and
re-observing it means a new tenant and another eligibility check.

**The fixture format is `T-093`'s, because it landed first** (22 September
2026, answering the bullet at the bottom). `tests/Fixtures/google/`, from
`T-093` on 20 September, and `tests/Fixtures/stripe/` after it hold flat files
beside one `README.md` whose rows give each file's call, date and what it
shows, and `T-160`'s test reads them with `file_get_contents()`
(`tests/Feature/Storage/OpenDriveEpisodeTest.php:70-72`). `T-095` adopted the
same on 22 September. This file already names successes by call and case in
that way, and two details change to match. **A failure carries its status and
Microsoft's word in its name**, as `errors-<call>-<status>-<code>.json`, where
`<code>` is Graph's `error.code`, or the token endpoint's `error`, as
observed, and a case word follows where two failures share a code. The Files
table below is written that way, and step 10 brings `T-098`'s citations of
the older names, such as `invite-400-both-false.json`, to the names
committed. **A response with no body is a `.txt`** holding its status line
and headers, as `tests/Fixtures/google/permissions-delete.txt` is, rather
than a README row alone. One thing stays different on purpose: `T-093` kept
its ids as observed, and this spike keeps the placeholder rule below, because
P1 and P2 need not be test accounts, which `T-093`'s README says its were,
and `T-098`'s tests read an id from the fixture rather than naming it
(`T-098:923`).

**Placeholders are fixed strings, never blanks:** `DRIVE_ID`, `FOLDER_ID`,
`FILE_PDF_ID`, `FILE_MP4_ID`, `UPLOADED_ID`, `MOVED_ID`, `PERM_1`, `PERM_2`,
`PERM_3`, `TENANT_ID`, `USER_OID`, `peer-1@example.com`, `peer-2@example.com`,
`peer-3@example.com`, `peer-4@example.com`, `ACCESS_TOKEN`, `REFRESH_TOKEN`,
`ID_TOKEN`. Every other field keeps its value and shape — `webUrl` included,
with only the id or account segment replaced — so `T-098`'s tests can assert
on a URL shape Microsoft actually returned. **22 September 2026:** three
more, `PERM_4` for P4's permission, `PERM_FILE` for step 0's permission on
the file, and `PERM_LINK` for the permission two Peers share in steps 6 and 7.

**The answers go into `T-098` as struck bullets with the date and the fixture
where it has bullets, and as one Notes line naming the report while it is the
bare template it is today.** `T-098` is a draft, so editing it is allowed; the
struck bullet is where the next reader looks first and the report is where the
observation lives. `T-093` does the same for `T-094`, and `T-092`'s one
bullet for this spike is struck the same way. **22 September 2026:** `T-098`
is no longer the bare template; it is a draft of 1,243 lines with bullets of
its own, so the first form applies, and step 10 also brings its citations of
this file's fixtures to the names committed.

**Timings are a stopwatch from the invite's 200 to the Peer's first
successful open**, written in the report. No source gives a figure, and one
measurement on the day is better than none.

**Publisher verification is measured, not started.** Whether a non-admin
member of the work tenant can consent to an unverified multi-tenant app asking
`Files.ReadWrite` is recorded — the AADSTS90094 refusal or a consent page.
Starting verification needs the owner's partner account and a custom
publisher domain
([Publisher verification](https://learn.microsoft.com/en-us/entra/identity-platform/publisher-verification-overview)),
which is `release-prerequisites.md:20`'s line to update. **22 September
2026:** that clause is at `release-prerequisites.md:29` now, and says work and
school creators cannot connect without verification; Q10 confirms or
corrects it.

## Preconditions

**Data this task verifies against:** none in Qori's database. The spike runs
no Qori code; a clean checkout is enough for committing the fixtures.

**Equipment.** Nothing below is bought (`D-042`): the work tenant is a free
developer sandbox or, where its eligibility fails, a one-month trial
cancelled before it bills (the fallback made explicit on 22 September
2026), every account is free to create, and an Entra app
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
      rules out, but ~~it is the owner's to approve — see below~~ it is the
      owner's billing identity, so linking it is their choice when step 0
      runs, and declining is simply the trial route below (22 September
      2026).
    - **How long it lasts.** Up to 90 days at a time, renewed on development
      activity; after expiry, 30 days to take data out, 30 more where only
      the admin can sign in, and deletion on day 60. Step 0 writes the
      dashboard's expiry date into the report, and the fixtures are committed
      as though the tenant will be gone by the time `T-098` starts, because
      it will be.
- An Entra app registration for "Accounts in any organizational directory and
  personal Microsoft accounts", one web redirect URI at a local address, a
  client secret, and `xms_edov` added as an optional id-token claim under
  its token configuration. It costs nothing and needs no paid tenant. ~~The
  registration is the owner's, because it is the one `T-098` and `T-092` ship
  with (provisional — see below); wherever it is created, it is not created
  inside the sandbox, because an app registration is a directory object and
  goes when its directory does.~~ **Rewritten 22 September 2026** (Before
  this can be ready): it lives in a directory that is **neither step 0's work
  tenant nor P4's home**. That was a matter of lifespan and is now also one of
  validity, because Microsoft's block on consent to an unverified
  multi-tenant app applies only to people in organisations other than the
  one that registered it (`vendor-accounts.md:588-593`), so a registration
  inside W1's tenant would never show Q10 the block. The owner's own
  registration, made the way `vendor-accounts.md:436-477` sets out, serves if
  it exists when the spike runs; otherwise the tester makes one in a
  directory of their own. The report says which it was, and whether it was
  publisher-verified when W1 met it.
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

    **22 September 2026:** which of the two routes a run uses is the owner's
    answer when it runs, not a question put in advance, and step 0 records
    it (Before this can be ready).

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
- Step 0's invite on one file and P3's open of it, which say whether `T-098`
  could grant per file on `T-160`'s contract rather than per folder on
  `T-091`'s (Q14, added 22 September 2026).
- The Peer journey walked with the scopes Qori will request: the creator's
  `Files.ReadWrite offline_access`, the Peer's `openid email`.
- The fixtures, their README, the report, the `T-098` and `T-092` edits and
  the one-line `release-prerequisites.md` update.

The questions, the step that answers each, and what each answer means for
`T-098`:

| #   | Question                                                                                                                                                                                                                                                                                         | Step    | If yes / observed                                                                                                                                                                                                          | If no                                                                                                                                                                                                                                               |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1  | With `sendInvitation: false`, can P1, P2 and P3 open the folder with no step beyond signing in, and did Microsoft email them anyway?                                                                                                                                                             | 3, 4    | The invite's 200 is `granted` for that family; the mailbox result decides whether the tier copy may say no email is sent                                                                                                   | A step exists: the row is `awaiting_acceptance` until it is done and the Peer-facing sentence names it. No way in at all: personal tiers are dead for `D-016`'s pattern and `T-098` becomes work-or-school only                                     |
| Q2  | How does the Peer find the folder: the creator's `webUrl` as returned, or only under Shared in their own OneDrive?                                                                                                                                                                               | 4       | `T-098` stores the URL that worked as the Open target and the fallback                                                                                                                                                     | —                                                                                                                                                                                                                                                   |
| Q3  | On personal OneDrive, does a file uploaded into the folder later reach P1 with no new invite?                                                                                                                                                                                                    | 5       | Folder-only; no re-share on new files                                                                                                                                                                                      | Folder plus re-share on every new child, or per-item — a change to `T-091`'s one-row-per-container model, recorded there                                                                                                                            |
| Q4  | Do files _moved_ into the folder need a new invite (Microsoft says yes), and what does the moved item's permission list show?                                                                                                                                                                    | 5       | Confirmed; `T-098` re-invites on the folder or on the item, whichever step 5 shows repairs it, and says how it notices a moved-in file — a listing of the folder's children, since retrying old failures discovers nothing | Microsoft's page is wrong for this case; folder-only stands                                                                                                                                                                                         |
| Q5  | Does a same-name upload (web Replace, and `PUT …/content`) keep the item id and P1's access?                                                                                                                                                                                                     | 5       | Replace-in-place is the tier copy's advice                                                                                                                                                                                 | Delete-and-re-upload semantics; the Episode needs re-picking and the copy says so                                                                                                                                                                   |
| Q6  | Is the invite response direct (`grantedToV2`) or a link (`link` + `grantedToIdentitiesV2`), and does a repeat, or a Peer who already has access, return that id?                                                                                                                                 | 3, 7    | `vendor_ref` holds a permission id; revoke may delete it                                                                                                                                                                   | Two Peers on one id: revoke skips link-type permissions and says so                                                                                                                                                                                 |
| Q7  | Work tenant: what does invite return when sharing is "Existing guests" and when guest invites are off?                                                                                                                                                                                           | 7       | The error body is a fixture; `T-098` maps it to `needs_creator` and the creator-facing sentence naming the admin setting                                                                                                   | —                                                                                                                                                                                                                                                   |
| Q8  | Work tenant: which sign-in does each Peer meet on the `webUrl`, and is a guest object created at once?                                                                                                                                                                                           | 0, 7    | The tier copy states the code-by-email path; `T-092`'s identity is confirmed before payment. P3's first sign-in is step 0's, on the file                                                                                   | —                                                                                                                                                                                                                                                   |
| Q9  | Free personal: how many invites before the daily cap, and what does the refusal look like?                                                                                                                                                                                                       | 8       | The number goes in the tier copy as `:people`; the refusal is a fixture, `pending` with `next_attempt_at` a day out if it names a reset, `needs_creator` if it does not                                                    | No cap reached at 100: the copy says only that Microsoft limits it                                                                                                                                                                                  |
| Q10 | Work tenant: can W1 consent to the unverified app, or is it AADSTS90094?                                                                                                                                                                                                                         | 7       | Publisher verification is a beta prerequisite with a lead time                                                                                                                                                             | User consent works; verification is still advised for step-up-consent tenants                                                                                                                                                                       |
| Q11 | Does `GET …/permissions/{PERM_1}` change once P1 has opened the folder — a grantee filled in where the invitation stood — and still show it on a re-read the next day? Step 0 asks the same of P3's permission on the file                                                                       | 0, 4, 7 | `checkGrant()` has a signal for `granted` on the stored `vendor_ref`, read at Open (`T-091`); until 22 September 2026 this column named the sweep `D-040` removed                                                          | `granted` rests on the Peer's first Open through Qori's route; a re-check can only confirm the permission still exists                                                                                                                              |
| Q12 | How long does one invite call take, from request to response, on each family?                                                                                                                                                                                                                    | 0, 3, 7 | Under `VendorAccessService::REQUEST_TIMEOUT_SECONDS`, 8 on disk (`app/Services/VendorAccessService.php:34`) and 6 in `T-091`'s draft: the grant made at Open lands inside the Peer's click                                 | Over it: that Open times out, the row stays `pending`, and the Peer's next Open sends the invite again, which is Q6's repeat; `T-098` says so, and the constant is questioned. Both columns rewritten on 22 September 2026 for `D-040`              |
| Q13 | Do `oid`, `tid`, `email` and `xms_edov` arrive in the id token for a personal account through `/common`, and for a work-tenant guest?                                                                                                                                                            | 9       | `T-092` keys OneDrive identities on `oid` + `tid` and requires `xms_edov`; the personal `tid` is recorded for `T-098`'s grant                                                                                              | `xms_edov` is missing on personal accounts: `T-092` stores it nullable and `T-098` says how a personal address is trusted                                                                                                                           |
| Q14 | Work tenant, step 0 (added 22 September 2026): does an invite on one file (`episode.pdf`) answer as the folder's does, and can P3, invited to that file alone with `sendInvitation: false`, open it with no step beyond signing in?                                                              | 0       | `T-098` may grant per file through `T-160`'s `GrantsItemAccess` on the work family, with no container and none of `T-091`'s machinery (Decisions)                                                                          | The file refused: the folder is the only route, and `T-098` stays on `T-091`'s container model. The file answered but P3 was left a step: its 200 is `awaiting_acceptance`, which `T-160`'s Open does not send on, so reuse means changing Open too |
| Q15 | Free personal, steps 2 to 4 (added 22 September 2026): the same as Q14 on the family most creators bring — does an invite on one file outside the folder (`Elsewhere/file-route.pdf`) answer as the folder's does, and can P2, invited to that file alone with `sendInvitation: false`, open it? | 2, 3, 4 | Whether `T-098`'s per-file route holds for personal OneDrive and not only for a work tenant; the two are different backends, and Q14 alone would let `T-098` choose its model on the family fewer creators use             | The personal file refused while the work file answered: `T-098` grants per file on work tenants and per folder on personal accounts, which is two models and a reason to prefer one                                                                 |

Steps. **Step 0 settles the free path before any other fixture is gathered
(`D-042`), and the ten steps after it keep the numbers they have**, because
`T-098` cites four of them by number — steps 3, 7 and 8 at
`T-098:164`, `T-098:255`, `T-098:333` and `T-098:685` — and a renumbering
would silently redirect every one. Steps 1 to 6, step 8 and step 9's P1
round trip are the personal half: they need only free accounts, so they
start on day one alongside step 0 rather than behind it. Step 7 and step 9's
P4 round trip are the work half and run only once step 0 has a tenant, the
sandbox or the trial.

0. **Settle the free path.** Check eligibility against the three qualifying
   paths in the developer program's FAQ (Equipment). **Where one holds**, set
   up the sandbox: link the billing account, record which path it came through
   and the expiry date the dashboard shows, and name the administrator
   account. **Where none holds — the likely case — or the owner declines to
   link a billing account, start a Microsoft 365 Business one-month trial
   instead** (Equipment), diarise its cancellation the same hour, and record
   the tenant, the admin account and the date the month ends; everything below
   then runs against the trial tenant and must finish inside it. Where neither
   route is open, stop here and report. Then the smallest set of calls that
   can say whether the tenant shares outside itself at all, **and on which of
   the two things `T-098` could grant on, a folder or one file** (rewritten 22
   September 2026; Decisions): as W2, connect with the same registration, make
   step 2's `Series spike/` in W2's OneDrive with `episode.pdf` in it,
   `GET /me/drive` and `GET …/children` on the folder for the ids and the
   file's `webUrl`, read the SharePoint admin centre's OneDrive sharing level
   and record it as found — step 7 restores that baseline later — and send two
   `POST …/invite` calls for P3's address, body exactly as step 3's, **the
   file first**:
    - (a) On `episode.pdf` (`FILE_PDF_ID`) → `invite-work-file-200.json`,
      with its seconds. `GET` the permission it returned →
      `permission-get-file-before-open-work.json`. Then P3, in a clean
      profile, opens the file's `webUrl`: record whether it opened with no
      step beyond signing in, the sign-in met, anything from Microsoft in
      P3's mailbox before P3 asked for a code, and the stopwatch time from the
      invite's 200. `GET` the permission again →
      `permission-get-file-after-open-work.json`.
    - (b) Then on the folder → `invite-work-200.json`, with its seconds. P3
      does not open the folder here; that is step 7's.

    The two answers are read apart (Q14):
    - **Both 200.** The free path works on both routes. Step 7 continues
      from this connection, this folder and this recorded baseline, and the
      file's answer is the report's for `T-098`.
    - **The folder 200, the file refused.** Step 7 continues as written, on
      the folder.
    - **The file 200, the folder refused.** The file is the only route on
      this family. Step 7 runs its per-Peer checks on `episode.pdf` wherever
      it says the folder, and marks step 5's upload and move checks, which
      only a folder grant raises, "not applicable: the file route has no
      folder".
    - **Both refused.** The work half's answer. Capture both bodies under
      the `errors-` form, name them in the README as where the work half
      stopped, and write in the report what that leaves unanswered.

    Either way nothing else happens here — no Peer but P3, no content set,
    no admin settings flipped — and either way nothing is bought.

1. **Connect C1.** Authorization code with `Files.ReadWrite offline_access`,
   exchange it, capture the token response and keep its access token aside
   for step 6. Refresh once, capture, and refresh again with the _old_
   refresh token; record whether the old one still works
   ([Refresh tokens](https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens)
   says it is replaced on every use but not revoked).
2. **Set up.** `GET /me/drive` for `DRIVE_ID`. In the web app make
   `Series spike/` — this one Series' folder and nobody else's — with
   `episode.pdf` and `episode.mp4` inside, and `Elsewhere/moved.pdf` outside
   it. Also `Elsewhere/file-route.pdf`, outside the folder too and kept apart
   from `moved.pdf`, which step 5 moves: it is the personal family's file for
   Q15, and it sits outside the folder because a file inside one inherits the
   folder's invitees, which would make a file-only invite indistinguishable
   from the folder's (added 22 September 2026). `GET …/children` on the folder. Make `Series spike 2/` beside it,
   empty, for step 6's container-replacement check.
3. **Invite.** P1, P2 and P3 in three separate calls; capture each status and
   body, and the seconds each call took. Wait ten minutes; check all three
   mailboxes for anything from Microsoft. Invite P1 again; compare ids. Send
   one call with `requireSignIn: false, sendInvitation: false`; capture the 400.
   Then invite P2 on `Elsewhere/file-route.pdf` alone, with P2's folder body
   → `invite-personal-file-200.json`, and its seconds (Q15, added
   22 September 2026).
4. **Take-up.** `GET …/permissions/{PERM_1}` before P1 has opened anything;
   capture. As P1 in a clean profile: open the folder's `webUrl` signed out,
   then signed in; open onedrive.live.com and look under Shared; record which
   of the three showed the folder, any step Microsoft put between sign-in and
   the folder, and the stopwatch time from step 3's 200 to the first open.
   `GET …/permissions/{PERM_1}` again; capture, and once more the next day.
   Open `episode.mp4` and `episode.pdf`; record the URL of each as opened.
   Open once in the phone app. Repeat as P2, and as P2 also open
   `Elsewhere/file-route.pdf` from its `webUrl`, signed out and then signed
   in, recording whether a Peer invited to that one file with
   `sendInvitation: false` reaches it and what stood in the way (Q15). As P3, create a Microsoft account
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
   P2's permission → `permissions-delete.txt`; confirm P1 still opens. If step
   3 found P1 and P2 on one id, send the `DELETE` anyway and record what P1 is
   left with: that is `F11`'s case, observed. Invite P1 on `Series spike 2/`,
   then `GET …/permissions` on both folders and confirm each grant stands on
   its own — what a replaced container leaves behind. **Then make a permission
   that covers two Peers rather than waiting for one** (added 22 September
   2026 for `F11`): share `Series spike 2/` from OneDrive's own Share dialog
   with P2 and P3 in one go, as specific people who can view, and
   `GET …/permissions` on it → `permissions-shared-link.json`. If one
   permission lists both, `DELETE` it and record which of P1, P2 and P3 can
   still open `Series spike 2/`; if the dialog made one permission each,
   record that and delete nothing. Then send step 3's P1 invite again with
   step 1's first access token, expired by now; capture the 401.
7. **Work tenant, from step 0's tenant**, the sandbox or the trial. As W1, run
   the consent screen for the same registration; capture the redirect's
   `error` and `error_description` or the consent page. As W2, on step 0's
   connection and folder, finish the content set as step 2 has it and invite
   P1 and P4 in separate calls → `invite-work-microsoft-account-200.json` and
   `invite-work-other-tenant-200.json`, with seconds; P3's folder invite is
   step 0's, and its seconds count as one of the three. In the Entra portal,
   record whether each appears under Users as a guest within a minute. Each
   Peer opens the folder's `webUrl`: record the sign-in met (work account,
   Microsoft account, one-time code), the consent page, and the time; re-read
   that Peer's permission before and after, as in step 4. P3 first signed in
   at step 0, on the file, so P3's open here is a returning guest's and Q8's
   row for P3 is step 0's. `GET …/permissions`; record direct or link and
   whether any two Peers share one id. Repeat step 5. `DELETE` P1's
   permission; confirm P3 still opens. If P1's id is another Peer's too, send
   the `DELETE` anyway and record who is left in (`F11`). If no two Peers
   shared an id, make the case as step 6 does: share the folder from the Share
   dialog with P1 and P4 in one go → `permissions-shared-link-work.json`, and
   if one permission lists both, `DELETE` it and record who can still open. In
   the SharePoint admin centre set OneDrive sharing to "Existing guests",
   invite a new address, capture; set it back and set Entra guest invite
   settings to "No one in the organization can invite guest users", invite,
   capture; restore both. Every README row for this step keeps the status, any
   `Retry-After` and any `RateLimit-*` header. The throttling page now says
   SharePoint Online neither returns nor supports the latter, while an older
   paragraph on it still advises reading them, so whether one arrives is
   itself recorded; a 429 or 503 is the throttle, recorded apart from a
   sharing refusal. On step 0's file-only outcome, every check here that names
   the folder runs on `episode.pdf`. (Fixture names, `F11`, the throttle and
   the file-only outcome added 22 September 2026.)
8. **Cap, and the other account's ids.** As C3,
   `GET /drives/{DRIVE_ID}/items/{FOLDER_ID}` with C1's ids; capture. Then on
   one folder of C3's own, invite `peer-cap+N@…` aliases of the P3 mailbox
   from N=1 until the first refusal or N=100; record N, the refusal body and
   headers. If step 3 showed personal drives refuse an address with no
   Microsoft account, invite P1 to N fresh folders instead. **Report the two
   limits apart** (22 September 2026): N is free personal OneDrive's daily
   sharing limit, and the report sets no SharePoint budget beside it; a 429
   or 503 met on the way is the throttle, recorded apart with its
   `Retry-After`, and the loop waits it out and carries on.
9. **Sign in.** As P1, then as P4, an authorization-code round trip against
   the same registration through `/common` with `scope=openid email`; capture
   the token response, decode the id token and capture its claims.
10. **Write it down.** Fixtures and README, the report, the `T-098` and
    `T-092` edits, the `release-prerequisites.md` line. `T-098`'s edit also
    brings its citations of this file's fixtures to the names committed,
    and `release-prerequisites.md`'s clause is at line 29 now (both 22
    September 2026).

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

| Path                                                                                                                                                                                                                                                                                                                                                                                                   | Change | Notes                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/Fixtures/microsoft/README.md`                                                                                                                                                                                                                                                                                                                                                                   | new    | One row per fixture: file, request, status, headers that matter, seconds, account family, date; laid out as `tests/Fixtures/google/README.md` is (22 September 2026)                                                                                                                    |
| `tests/Fixtures/microsoft/token-authorization-code.json` `tests/Fixtures/microsoft/token-refresh.json`                                                                                                                                                                                                                                                                                                 | new    | Step 1, tokens replaced                                                                                                                                                                                                                                                                 |
| `tests/Fixtures/microsoft/drive-me.json` `tests/Fixtures/microsoft/children-folder.json`                                                                                                                                                                                                                                                                                                               | new    | Steps 2 and 5; the children listing is the one taken after the upload and the move. Step 0's two reads take the `-work` suffix                                                                                                                                                          |
| `tests/Fixtures/microsoft/invite-work-file-200.json` `tests/Fixtures/microsoft/permission-get-file-before-open-work.json` `tests/Fixtures/microsoft/permission-get-file-after-open-work.json`                                                                                                                                                                                                          | new    | Step 0, added 22 September 2026: the invite on `episode.pdf`, and P3's permission on it either side of P3's open; a refusal takes the `errors-` form                                                                                                                                    |
| `tests/Fixtures/microsoft/invite-personal-200.json` `tests/Fixtures/microsoft/invite-personal-repeat.json` `tests/Fixtures/microsoft/invite-personal-no-account.json` `tests/Fixtures/microsoft/errors-invite-400-<code>-both-false.json`                                                                                                                                                              | new    | Step 3; `no-account` is P3's, under this name if it is a 200 and as `errors-invite-<status>-<code>-personal-no-account.json` if not; `repeat` is the repeated grant                                                                                                                     |
| `tests/Fixtures/microsoft/permission-get-before-open.json` `tests/Fixtures/microsoft/permission-get-after-open.json` `tests/Fixtures/microsoft/permission-get-next-day.json`                                                                                                                                                                                                                           | new    | Steps 4 and 7 (`-work` suffix); P1's permission re-read before the first open, after it, and the next day                                                                                                                                                                               |
| `tests/Fixtures/microsoft/invite-work-200.json` `tests/Fixtures/microsoft/invite-work-microsoft-account-200.json` `tests/Fixtures/microsoft/invite-work-other-tenant-200.json` `tests/Fixtures/microsoft/invite-work-207.json` `tests/Fixtures/microsoft/errors-invite-<status>-<code>-work-existing-guests.json` `tests/Fixtures/microsoft/errors-invite-<status>-<code>-work-guest-invites-off.json` | new    | Steps 0 and 7: `invite-work-200.json` is step 0's folder invite to P3, who had already signed in on the file; P1's and P4's are step 7's; `207` only if observed, and the README says so if it was not                                                                                  |
| `tests/Fixtures/microsoft/permissions-folder.json` `tests/Fixtures/microsoft/permissions-uploaded-item.json` `tests/Fixtures/microsoft/permissions-moved-item.json`                                                                                                                                                                                                                                    | new    | Step 5, personal; the work-tenant copies take a `-work` suffix                                                                                                                                                                                                                          |
| `tests/Fixtures/microsoft/item-replace-put-content.json`                                                                                                                                                                                                                                                                                                                                               | new    | Step 5, the driveItem returned by the `PUT`                                                                                                                                                                                                                                             |
| `tests/Fixtures/microsoft/errors-invite-401-<code>-expired-token.json` `tests/Fixtures/microsoft/permissions-second-folder.json` `tests/Fixtures/microsoft/permissions-delete.txt` `tests/Fixtures/microsoft/item-other-account.json`                                                                                                                                                                  | new    | Steps 6 and 8; the recoverable failure, the replaced container's own permission list, the `DELETE`'s 204 as its status line and headers (step 7's takes `-work`), and a container read with another account's token, as `errors-item-get-<status>-<code>-other-account.json` if refused |
| `tests/Fixtures/microsoft/permissions-shared-link.json` `tests/Fixtures/microsoft/permissions-shared-link-work.json`                                                                                                                                                                                                                                                                                   | new    | Steps 6 and 7, added 22 September 2026 for `F11`: a permission two Peers share, made from the Share dialog; the work one only if no invite produced a shared id first                                                                                                                   |
| `tests/Fixtures/microsoft/errors-invite-<status>-<code>-personal-cap.json` `tests/Fixtures/microsoft/errors-invite-429-<code>.json`                                                                                                                                                                                                                                                                    | new    | Steps 8 and any step; each only if reached, with `Retry-After` in the README row                                                                                                                                                                                                        |
| `tests/Fixtures/microsoft/oidc-token-personal.json` `tests/Fixtures/microsoft/oidc-claims-personal.json` `tests/Fixtures/microsoft/oidc-token-work.json` `tests/Fixtures/microsoft/oidc-claims-work.json`                                                                                                                                                                                              | new    | Step 9; the token response with tokens replaced, and the decoded id-token payload — `T-092`'s fixture, consumed by `T-098`                                                                                                                                                              |
| `tests/Fixtures/microsoft/consent-w1.txt`                                                                                                                                                                                                                                                                                                                                                              | new    | Step 7, the redirect query string as text, or one line saying consent was offered                                                                                                                                                                                                       |
| `app/dev/tasks/reports/T-097-YYYY-MM-DD-<owner>.md`                                                                                                                                                                                                                                                                                                                                                    | new    | In `qori-plan`, where planning moved on 21 September 2026; the four planning rows read `docs/planning/…` until then. The report; every question above answered by number, timings, and what could not be run                                                                            |
| `app/dev/tasks/T-098-onedrive-episodes-from-a-folder-shared-with-each-peer.md`                                                                                                                                                                                                                                                                                                                         | edit   | In `qori-plan`. Strike each bullet answered, with date and fixture, and bring its citations of this file's fixtures to the names committed                                                                                                                                              |
| `app/dev/tasks/T-092-a-peer-confirms-the-vendor-account-they-will-open-with.md`                                                                                                                                                                                                                                                                                                                        | edit   | In `qori-plan`. Strike its `xms_edov` bullet under "Before this can be ready" with the date and the claims fixture                                                                                                                                                                      |
| `app/dev/release-prerequisites.md`                                                                                                                                                                                                                                                                                                                                                                     | edit   | In `qori-plan`. Line 29's Microsoft clause (line 20 when this was drafted): confirmed or corrected from Q10, with what verification needs                                                                                                                                               |

Flows: none — no code changes; nothing under `app/` or `routes/` is touched.

## Database

None.

## Code

None under `app/`. The literal calls, so two testers capture the same
fixtures. Request and response field names below are as documented on the
pages cited, not observed; the fixture is what turns each into an observation.

```http
# Step 0 — as W2: step 1's authorize/token pair and step 2's two reads, then step 3's body, for P3, twice (22 September 2026)
POST https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FILE_PDF_ID}/invite
GET  https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FILE_PDF_ID}/permissions/{PERM_FILE}   # before and after P3 opens the file
POST https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FOLDER_ID}/invite                      # only then the folder

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

| Call                                          | Page                                                                                                                                                                     | Documented, not yet observed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST …/invite`                               | <https://learn.microsoft.com/en-us/graph/api/driveitem-invite?view=graph-rest-1.0>                                                                                       | 200 with `value[]` of permissions (`id`, `roles`, `grantedToV2`, `invitation.email`, `invitation.signInRequired`), or 207 partial; no permissions on a personal root. Any driveItem, a file as well as a folder, and `/me/drive/items/{item-id}/invite` names one without its drive; `sendInvitation: false` is documented as granting the permission directly, with no notification (22 September 2026)                                                                                                             |
| `GET …/permissions`, `GET …/permissions/{id}` | <https://learn.microsoft.com/en-us/graph/api/resources/permission?view=graph-rest-1.0>, <https://learn.microsoft.com/en-us/graph/api/permission-get?view=graph-rest-1.0> | `link` and `grantedToIdentitiesV2` on a link-type row; `inheritedFrom` on an inherited one; grantee empty until redeemed                                                                                                                                                                                                                                                                                                                                                                                             |
| `DELETE …/permissions`                        | <https://learn.microsoft.com/en-us/graph/api/permission-delete?view=graph-rest-1.0>                                                                                      | 204; only non-inherited permissions can be deleted                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `GET …/children`, drive, item                 | <https://learn.microsoft.com/en-us/graph/api/resources/driveitem?view=graph-rest-1.0>                                                                                    | `id` unique within the drive; `webUrl` is the only documented page a person opens; what another account's token gets for the id is not stated                                                                                                                                                                                                                                                                                                                                                                        |
| `PUT …/content`                               | <https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0>                                                                                  | Updates an existing item's bytes, up to 250 MB; whether the id survives is implied, not stated                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Token endpoint                                | <https://learn.microsoft.com/en-us/entra/identity-platform/refresh-tokens>                                                                                               | 90-day refresh token, replaced on every use; personal-account lifetimes not covered by that page; the 401 for an expired access token is not shown                                                                                                                                                                                                                                                                                                                                                                   |
| Id token claims                               | <https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference>                                                                                    | `email` may be wrong or change and must not authorise; `xms_edov` says whether it was verified; `oid` + `tid` identify the account                                                                                                                                                                                                                                                                                                                                                                                   |
| Throttling                                    | <https://learn.microsoft.com/en-us/sharepoint/dev/general-development/how-to-avoid-getting-throttled-or-blocked-in-sharepoint-online>                                    | 429 or 503 with `Retry-After`, and since August 2026 a section saying `RateLimit` headers are neither returned nor supported, though an older paragraph still advises them; 3,000 requests per 5 minutes per user, licence-dependent tenant budgets, five resource units per permission call, reads included, and per app per tenant 300 calls to unnamed "specific sharing APIs" every 5 minutes with no licence bound (the `RateLimit` and sharing-API facts read 22 September 2026; see Before this can be ready) |

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

- [ ] The report opens on step 0: the route the work tenant came through —
      the sandbox, with its eligibility path and the expiry date on the
      dashboard, or the one-month trial, with the date it ends and its
      cancellation diarised — the tenant's OneDrive sharing level as found,
      and both probe invites' status and seconds, the file's first; or, where
      neither route was open, the work-tenant questions that leaves
      unanswered, handed back to the owner under `D-042` rather than bought
      around
- [ ] The report says which of step 0's four outcomes it met, whether P3
      opened the file with no step beyond signing in, and which model it
      recommends `T-098` take, folder or file, with the reason; on a file it
      names `T-160`'s `GrantsItemAccess` as the contract `T-098` would reuse,
      and says the personal family was asked of the folder alone
- [ ] Q1 to Q15 each answered in the report by number, with the observed
      value, the account family, the date, and the stopwatch time and the
      call's seconds where one was asked for
- [ ] The report says, per account family, whether both first access and
      later content worked, so `T-098` can advertise only the families that
      were tested rather than "OneDrive"
- [ ] Every fixture in the Files table either committed with placeholders
      swapped, or named in the README as not reached and why — the repeated
      grant, the 401, the other-account read and the shared permission among
      them — and every failure named in the `errors-` form
- [ ] `tests/Fixtures/microsoft/README.md` has one row per fixture with the
      request, status, the headers that matter, the seconds and the date
- [ ] `T-098` carries the answers: struck bullets with the date and fixture
      where it has bullets, else a Notes line naming the report; `T-092`'s
      `xms_edov` bullet struck the same way
- [ ] `release-prerequisites.md:29`'s Microsoft clause, which says work and
      school creators cannot connect without publisher verification, is
      confirmed or corrected from Q10, with what verification needs (the
      clause was at line 20 when this was drafted)
- [ ] The report's "Could not verify" names every step skipped for want of
      equipment, C2 among them, which `D-042` does not provision
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan` (the board moved there with
      planning on 21 September 2026; `php artisan qori:tasks` is gone)
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Whether the Entra app registration is created now under the owner's
  account, so the redirect URIs, the `xms_edov` optional claim and the
  publisher domain are the ones `T-098` and `T-092` ship with, or under the
  tester's and re-created later — the owner's. Either way it is not
  registered inside the sandbox, which is deleted on a timer (Equipment).~~
  **Answered 22 September 2026: equipment for the spike and release setup for
  what ships, so neither is a question for this task.** What the spike needs
  is one registration with the settings under Preconditions, and
  `PROCESS.md` puts the equipment a task needs there; that line is rewritten
  to say where the registration may live. The registration Qori ships with
  is the one `vendor-accounts.md:436-477` has the owner make in Qori's own
  tenant, because Microsoft refuses publisher verification to an app a
  personal account registered and an app cannot change tenants. That
  registration, its redirect addresses and its verification are production
  configuration and a vendor's review, which `D-043` puts on `PLAN.md`'s
  release gate (`release-prerequisites.md:29`). Nothing captured here depends
  on which of the two the spike ran on, beyond the client id an id token
  carries as `aud`. What the old bullet's last sentence needed is now a
  stronger reason than a timer: Microsoft's block on unverified apps applies
  only to people outside the registering organisation
  (`vendor-accounts.md:588-593`), so a registration inside step 0's tenant
  would make Q10 unobservable, not merely short-lived.
- ~~**Which of the two free routes the owner has, which step 0 settles and
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
  `L` six tasks away and a renewable tenant outlives a trial — the owner's.~~
  **Answered 22 September 2026: equipment, not a design question, and not
  asked in advance.** Both routes are under Preconditions in the order step 0
  tries them: the E5 developer sandbox first, for this bullet's own reason,
  and the Microsoft 365 Business one-month trial as the fallback, with its
  cancellation diarised the hour it starts. Which one the owner holds, and
  whether they link their billing identity for the sandbox, is their answer
  when the spike runs; declining is simply the next route down, and step 0
  records the route used, with its eligibility path or its end date.
  `D-042` already made the one decision in this bullet, that neither route
  is a purchase.
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
- ~~Whether the fixture format (raw body plus a README row) is the one `T-093`
  and `T-095` also use, so the three vendor directories read the same way;
  `T-093` names files by call and case and `T-095` by
  `<namespace>/<route>.<case>.<status>.json`, and whichever spike lands first
  sets it — anyone's.~~ **Answered 22 September 2026: `T-093` landed first,
  so its format governs**, as `T-095` also settled that day. It was this
  file's already in the ways that matter, raw bodies beside one README and
  flat names by call and case. Two details change to match it: a failure
  carries its status and Microsoft's code in an `errors-` name, and a
  response with no body is a `.txt`. The placeholder rule stays, for the
  reason given. All three are under Decisions, the Files table is written in
  the new names, and step 10 brings `T-098`'s citations of the old ones
  along.
- ~~Whether step 8's cap count is worth a day of a throwaway account, or the
  copy says only that Microsoft limits daily sharing and a refused grant is
  retried tomorrow — the owner's.~~ **Answered 22 September 2026, decided
  rather than asked: it is worth it, and it stays, last, on C3.** Whether to
  measure something is not a product call, and the copy follows from Q9's
  answer either way, which is `T-098`'s to write. Two things have made the
  number worth more since the bullet was written. Under `D-040` a grant is
  made when a Peer presses Open, so a Series launching to many Peers at once
  is exactly when a daily cap bites, and `T-098` should meet it here rather
  than in production. And on step 0's file route a Peer costs one invite per
  Episode rather than one per Series, so the same cap is reached that many
  times sooner. The day it costs is C3's alone, which is what C3 is for, and
  `T-098` also owes a body for the personal-account gates the loop is the
  likeliest step to meet (`T-098:252-255`).
- ~~**From the storage review's rate-limit table (20 September 2026):** the
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
  anyone's.~~ **Answered 22 September 2026: done, and the correction above was
  half wrong.** Step 8 now reports the daily cap and the throttle apart and
  says its number is free personal OneDrive's, and step 7 keeps the status,
  any `Retry-After` and any `RateLimit-*` header on every row. Two things on
  the page are not as this bullet read it. **The 300 figure is there.** The
  page's per-app, per-tenant table lists "Specific Sharing APIs" at 300 every
  five minutes with no licence bound, and its source has carried that row
  since at least 28 May 2025: commit `d6363692a5` of `SharePoint/sp-dev-docs`,
  line 124 of the page then and line 132 now. What the page does not say is
  which sharing APIs those are, so the old row's "300 sharing calls" claimed
  more than the page does; the sources table now gives the figure the way the
  page does. **And `Retry-After` is the one throttling header the page still
  promises.** A change of 7 August 2026 added a section saying SharePoint
  Online neither returns nor supports the `RateLimit` headers, while an older
  paragraph on the same page still advises reading them; `Retry-After` comes
  with a 429 or 503. Step 7 keeps whatever arrives and records whether a
  `RateLimit` header ever did.
- ~~**From the storage review, F11 and its evidence table (20 September 2026):**
  the OneDrive row it owns asks that this spike run separately for personal and
  for work accounts — silent redemption, the permission's shape, removing one
  member of a shared link, the moved-in file's repair, the verified identity
  claims and the throttles — and that where one Peer cannot be taken off a
  shared permission, what Qori is left holding is observed rather than
  inferred. Q6 disposes of that case in a clause ("revoke skips link-type
  permissions and says so") and no such permission has been seen. What cannot
  safely be produced stays unobserved in the report with its reason, and an
  exception to the evidence rule is the owner's to record rather than the
  spike's to waive — the owner's, with step 8's bullet above.~~ **Answered 22
  September 2026, decided: the case is now produced and observed, so no
  exception is needed.** The rest of `F11`'s list already had a step in each
  family: silent take-up (Q1, Q8), the permission's shape (Q6), the moved-in
  file's repair (Q4), the identity claims (Q13) and the throttles (steps 7 and
  8). What had none was a permission covering two Peers, which the spike could
  only wait for. Step 6 now makes one from OneDrive's own Share dialog, as
  specific people who can view, and step 7 does the same in the work tenant
  unless an invite there has already produced one; each is captured, as
  `permissions-shared-link.json` and `permissions-shared-link-work.json`,
  deleted where it lists both, and followed by a record of who can still open.
  Where an invite itself returns an id two Peers share, the step's `DELETE` is
  sent anyway and what the other Peer is left with is recorded. It is the
  shape Q6 asks about, made on purpose; whether Qori's own invites ever
  produce it stays Q6's observation. Taking one Peer off such a permission
  needs `revokeGrants`, which is beta and not offered for personal accounts,
  so what is observed is what a `DELETE` does to everyone on it. If the Share
  dialog makes one permission per person, that is the observation, recorded as
  such, and nothing is waived.
- ~~**From the storage review, F10 (20 September 2026):** `D-036` moved Google
  Drive's grants onto files and decides nothing for OneDrive. Whether a
  OneDrive grant stands on the Series folder or on each item is this spike's,
  and Q3, Q4 and Q6 are where that answer comes from; `T-091`'s
  container-shaped queries and tests are not frozen until this spike and
  `T-095` have both answered — anyone's, with `T-091`.~~ **Answered 22
  September 2026: step 0 now asks it directly**, on one file and on the
  folder, before anything else in the work tenant (Q14). It matters more
  than when this bullet was written: `T-160` has since built the item
  contract, so a OneDrive grant on a file needs nothing from `T-091`. Q3, Q4
  and Q6 still answer the folder's side. What step 0 does not answer is the
  personal family, which is asked of the folder alone, and the per-file
  paragraph under Decisions says what that leaves `T-098`. For `T-091`,
  this spike's answer arrives with its report, and `T-091`'s
  container-shaped queries wait on it and on `T-095`'s as before.

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
claims fixture answer it. **22 September 2026:** `T-098` is no longer the
bare template; it says `depends: T-044, T-091, T-092, T-094, T-097, T-152`,
which is the edit this paragraph said was owed.

Fixture names are provisional until observed: `invite-work-207.json` and
`invite-429.json` exist only if reached, and `invite-personal-no-account`
may turn out to be a 200 rather than an error. The README row says which.
**22 September 2026:** in the names under Files, the second is
`errors-invite-429-<code>.json`, and the third keeps its name if it is a 200
and takes the `errors-` form if it is not.

`release-prerequisites.md:20` says the research "did not confirm" publisher
verification is required; the step-up-consent page above says unverified
multi-tenant apps are blocked for user consent by default. Q10 settles it.
**22 September 2026:** the clause is at `release-prerequisites.md:29` now and
no longer says "did not confirm"; it says work and school creators cannot
connect without verification. Q10 still settles it by observation.

Community reports describe invites whose permissions never took effect for
external users
(<https://learn.microsoft.com/en-us/answers/questions/1332382/microsoft-graph-api-drives-((drive-id))-items-((it>),
which is why step 4 waits and times rather than taking a 200 for access.

**22 September 2026, brought to ready.** Beyond the seven bullets struck
below Acceptance and the file invite added to step 0, the file was re-read
against the code, against `D-040` and against the move of planning to
`qori-plan`, and these changed openly where they stand: the Why section's
account of `app/`; the six states, the sweep and the provisional five-second
budget in Decisions, Q11 and Q12; the first Decisions paragraph, which had
not caught up with the trial fallback; step 7's title, which said sandbox
where it may be a trial; the four planning rows in Files, which named
`docs/planning/…` paths the code repository keeps only a signpost for; the
board command in Acceptance; the line number of the publisher-verification
clause; and the throttling row of the sources table. Q14 is new, and Q8, Q11
and Q12 name step 0 among their steps. Nothing here renumbers a step, so
`T-098:164`, `T-098:255`, `T-098:333` and `T-098:685` still point where they
did.
