---
id: T-091
title: Every Peer with access is granted at the vendor
stream: storage
status: draft
owner: unassigned
estimate: L
depends: T-044, T-089, T-093, T-151, T-156
blocks: T-092, T-094, T-096, T-098, T-100, T-101, T-103, T-157
---

# T-091 — Every Peer with access is granted at the vendor

> **Draft**, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016` and the owner's BYO blueprint; reviewed the same day against the
> developer's review of the plan that day, whose asks for this task —
> short timeouts, a state that says who resolves it, re-checks of granted
> rows, reconciliation on identity, reconnect and container change, and
> replayable payment recovery — are folded in below. Revised on 17 September
> 2026 for `D-020` and `D-021`, after a designer's review of the storage
> drafts that day: a blocked Open lands on the Series page, a wait somebody can
> end has a button, and changing a container shows what it touches first.
> Amended on 18 September 2026 by the classroom decisions. `D-025` settles the
> two container questions: a Series may mix providers, one container each, and
> a container serves one Series. `D-024` holds this draft's live-session
> containers until they fit a per-Episode join link, so the meeting half of the
> impact dialog — `ContainerChangeImpact::kind()` answering `meeting`, the
> `series.container_change.meeting.*` lines and case 60 — waits, still written
> here, on the stream owner's answer below. `D-030` gives the item check a
> materials branch, which is `T-094`'s with `T-130` rather than this task's
> (Notes). Revised on 19 September 2026 to agree with the drafts around it:
> every vendor call renews the token through `T-044`'s
> `ConnectionService::fresh()` first and a refused token marks the connection
> for reconnect; `T-044`'s `ConnectionReconnected` reaches `reconnected()`
> through a listener here; the container lock is `T-044`'s `AdvisoryLock`; the
> identity shape is `GrantIdentity`; `GrantResult` and `ItemCheck` carry what
> `T-094` and `T-098` need; a replace checks at most `MANUAL_RETRY_LIMIT`
> Episodes inline; the grant is attempted before a restored Peer's email; and
> every timeout is a budget the vendor's client may only shorten (`D-034`).
>
> **Re-drafted again on 20 September 2026 on `D-040`**, which is the larger
> of that day's two changes. A grant is made when a Peer presses Open, for
> the one item they are opening, and at no other time: there is no scheduled
> sweep, nothing is granted ahead of use, and a purchase makes no vendor call
> at all. Revocation keeps its inline attempt and gains a visible end — a
> failed revoke is listed for the creator rather than retried for ever. The
> storage review of the same day
> ([`../reviews/storage-2026-09-20.md`](../reviews/storage-2026-09-20.md)) is
> folded in with it: the principal each grant was made to is stored (`F04`),
> a permission two purchases share is not revoked by either alone (`F02`),
> the identity a Series needs is read from its targets rather than its
> containers (`F03`), a person's request has a deadline and not only a
> per-call budget (`F08`), and the queries that assumed a container are named
> (`F10`). Where the two re-drafts disagree, `D-040` is the later.
>
> **Re-drafted on 20 September 2026 on `D-036`**, after `T-093`'s report
> ([`reports/T-093-2026-09-20-wayne.md`](reports/T-093-2026-09-20-wayne.md)):
> a grant is on a **target**, which is a container for the providers that
> share one and an **item** — one Episode's file — for Google Drive, whose
> narrow scope refuses every sharing change on a folder while anything
> beneath it is unpicked. The container half below is unchanged; what is new
> is the second target, the columns that carry it, `grantsOn()` and
> `revokeItem()`. (`ensureItem()` and the bound on how many grants one request
> may make were part of this paragraph until `D-040`, which arrived the same
> day and made both unnecessary — nothing is granted ahead of use, so there is
> no fan-out to bound.) The file name still
> says "on the Series container": it is kept so the drafts and reports that
> link to it keep working, and the title in the front matter is the one to
> read.
>
> **Cut in two on 20 September 2026**, by the stream owner, because
> `PROCESS.md` asks a ready `L` task to name its split and `blocks:` listed
> what builds on this rather than pieces it was cut into. What stays here is
> the **grant core**: the two tables, the contract, the ensure step, the
> target lock, revoke, attach, reconnected, and the Peer's path through Open.
> What left is the **creator's surfaces** —
> the grants and removals lists, Try again now, the container-change
> dialog — which is `T-157`, drafted the same day and due before `T-094`
> brings the Integrations section back into view. The **meeting half** went
> to `T-100` and `T-101`, the only tasks that would use it (`D-024` still
> holds it, so it arrives there held). Both halves remain vertical slices,
> for different people: this one is finished when a Peer presses Open and
> the file opens, `T-157` when the creator can fix it if it does not.
>
> **Consolidated on 20 September 2026**, after a three-lens read-through of
> the cut found about a hundred items and the answer that it had not been
> clean. Everything on that list is worked through — the record is at the
> bottom, under "Read-through and consolidation" — and what it turned on is
> worth knowing before reading the rest: the cut's lists were reliable and
> its prose was not, so the Decisions section was still building another
> task's screens two hundred lines after the Scope section gave them away.
> Four things were wrong in a way that would have built the wrong thing, one
> of them a correctness hole: `attempting`, added that morning, was read by
> nothing, so a permission Qori created would never have been revoked.

## Why

`D-016` grants each Peer on one container per Series — a folder or a recurring
meeting — with the creator's token, and nothing in the code can hold that fact.
`Series` has no provider or container (`app/Models/Series.php`), `Access` has
nowhere to keep a vendor permission id, and the only path into an access,
`AccessService::grant()` (`app/Services/AccessService.php:47-107`), writes the
row and sends the email with no vendor step anywhere. The queue is `deferred`
and cannot retry (`config/queue.php:16-39`), so a vendor call that fails in the
request is simply lost, and `CheckoutService::fulfil()` catches only
`AppException` (`app/Services/CheckoutService.php:113-140`) with no transaction
around `grant()`, so a vendor failure raised as an `AppException` on the paid
path would record a `Failed` fulfilment beside a live Access, and any other
exception would leave a live Access with no fulfilment row and the webhook
failing.

Afterwards there are two tables, one contract every per-Peer provider
implements, and one idempotent "make sure the grant exists" step that never
throws. A grant is on whatever the provider shares: a container, for a
provider that shares a folder or a meeting, or one Episode's file, for a
provider whose scope only reaches what the creator picked (`D-036`, Google
Drive). **The step runs when a Peer presses Open, and nowhere else**
(`D-040`): a purchase writes the Access and calls no vendor, attaching a
container calls no vendor for a grant, and nothing is scheduled. The Peer who
wants an Episode is the one who pays for the call that grants it — two to
three seconds at a click, and no work at all for the nineteen Episodes they
never open. Every grant row is in one of eight states, and each that is not
`granted` says who can resolve it: a Peer whose Open could not be completed
reads which, and presses Open again where pressing it can help. Where the
answer is the creator — an account that refused a grant, a removal that
failed, a container to pick again — this task writes the state and `T-157`
is what shows it to them; the Peer's side is finished when Open works, and
the creator's when they can fix it if it does not. No vendor is implemented here — the provider
tasks (`T-094`, `T-096`, `T-098`, `T-100`, `T-101`) bind their integrations
to the contract this task defines, and the tests here use a fake.

## Decisions taken to make this specifiable

**A grant is a row in `vendor_grants`, not a column on `accesses`.** One column
would fit one container per Access (accesses are unique per Group, Series and
user, `database/migrations/2026_09_08_000000_create_qori_schema.php:159`), but
a grant carries a status, an attempt count, a next-attempt time and a provider,
and a Series may hold more than one container. Rows are kept on revoke, as
`accesses` are (`AccessService.php:120-134`).

**One grant row per (Access, target), where a target is a container or one
Episode's item.** The draft before `D-036` had one row per (Access,
container) and said that a provider needing per-item grants would be a change
to this Database section; `T-093` is the spike that said so, and the owner
chose per-file grants for Google Drive on 20 September 2026. So a row carries
`target` (`container` or `item`), the container it belongs to or the Episode
it belongs to, and `external_target_id`, the vendor's id for whichever of the
two it was granted on. One row per (Access, container) and one per (Access,
Episode) are each unique, and no row carries both. This is still one grant
model: the states, the retry rule, the re-check, the revoke and the copy are
the same, and only what the grant is made on differs.

**A provider says which target it grants on, and `grant()` takes the row.**
`GrantsPeerAccess::grantsOn()` answers `GrantTarget::Container` or
`GrantTarget::Item`, which is how this service knows whether a Series needs
one row per container or one per Episode, and which of the two a page is
looking at. `grant()`, `checkGrant()` and `revoke()` take the `VendorGrant`
row itself rather than a `SeriesContainer`, because the row already carries
`provider`, `external_target_id`, its container and its Episode, and because
one signature then serves both models. An integration reading a Model is what
`CLAUDE.md` asks of one.

**A container is dedicated to one Series (`D-025`).**
`(group_id, provider, external_id)` is unique on `series_containers`, so one
folder or meeting can never serve two Series, and removing a Peer from one
Series can never cut off access they hold through another. `attach()` refuses a
container another Series holds with a readable error in front of the
constraint. Each provider task's picker carries the sentence that sharing the
container shares everything inside it, Episodes or not; this task has no
picker.

**The container is per Series and per provider, and a Series may mix
providers (`D-025`).** `(group_id, series_id, provider)` is unique on
`series_containers`: one container per provider, as many providers as the
creator connects. Setup recommends one connected storage provider per Series
and does not enforce it, because each connected provider costs each Peer one
more vendor sign-in (`T-092`); that sentence is `T-044`'s and the provider
tasks', not this task's.

**`provider` on both tables is `ConnectionProvider`, not `EpisodeProvider`.** A
container lives in a connected account, and the contract's `provider()` answers
for the account it needs. `EpisodeProvider::connection()`
(`app/Enums/EpisodeProvider.php:42-51`) is the one crossing from an Episode to
its container.

**Eight states, and each one that is not `granted` names who resolves it.**
`awaiting_identity`: the Peer has not confirmed the vendor account the Series
needs — the Peer resolves, by signing in with the vendor (`T-092`).
`awaiting_acceptance`: the vendor accepted the grant but the Peer still has a
step — a Dropbox Join, a OneDrive invite to take up — the Peer resolves.
`pending`: nothing has been sent to the vendor for this row, or the last send
failed with a timeout, a rate limit, a transient error, or an integration that
is missing or threw — the next Open sends it, and nobody else needs to act.
`attempting`: a create went out and its answer never arrived, so the vendor may
be holding a permission Qori cannot name — the next Open reconciles it, and
nobody needs to act (`F01`). `needs_creator`:
the creator must act — reconnect, an admin policy, a plan that cannot share, a
cap reached, a container Qori can no longer find. `revoke_failed`: the creator
must act, and it is the only state where what is owed is a removal rather than
a grant (`D-040`). `granted` and `revoked`. The
Peer-facing sentence for each says so, and "nothing more is needed from you"
is said for `pending` and `needs_creator`, the two states the Peer cannot act
on (`D-020`). `attempting` has no sentence of its own: `stateFor()` answers
`Pending` for it, because what the Peer should do is identical and a second
sentence would be a distinction drawn for Qori's benefit. `revoke_failed` and
`revoked` never reach the notice, since neither blocks an Open.

**A row becomes `granted` only when the provider has evidence the Peer can
open the container now.** `record()` sets `granted` from a
`GrantResult::granted()` or from a `checkGrant()` that answers `granted`, and
from nothing else. An API call the vendor accepted while the Peer still has a
step is `awaitingAcceptance()`, with the vendor's id stored so the row can be
re-read. Every provider task states, from its spike's fixture, exactly when
its grant is `granted` and which of its failures map to which state; the fake
here answers whatever a test tells it to.

**The ensure step never throws, and Open is the only thing that calls it**
(`D-040`). It runs from `T-089`'s Open route, for the one Episode being
opened, and from the three reconciliations —
`T-092` calls it when a Peer confirms or changes an identity, `T-044`'s
`ConnectionReconnected` reaches `reconnected()` through this task's listener
when the creator reconnects, and `attach()` calls it when a container is
replaced. None of those three grants anything by itself: each one clears
what was blocking, and the next Open makes the call. Nothing runs from
`AccessService::grant()`, from `SharedController::show()` or from a schedule.
Every vendor answer is a typed `GrantResult` recorded on
the row; a `Throwable` from anywhere inside the step — the integration, the
lock, the row write — is caught, logged with the Access id and swallowed. A
row that could not be saved is created by the next trigger.

**A purchase calls no vendor, and `AccessService::grant()` is left alone**
(`D-040`). The earlier draft attempted the grant between the Access write and
`announce()` (`AccessService.php:115-118`), so a slow vendor delayed the
access email and a Series of twenty Episodes spent twenty calls nobody had
asked for. Now `grant()` writes the Access, sends the email and calls
nothing: no grant row is created either, because a row records an attempt and
no attempt has been made. The email's link lands on `/shared/{id}`
(`app/Notifications/SeriesAccessNotification.php:62`) and every Episode on it
offers Open, which is where the first vendor call of that Peer's life
happens. `CheckoutService::fulfil()` therefore has nothing new that can fail
inside it, which is the cheapest possible answer to `PLAN.md`'s rule that
fulfilment is never refused after payment.

**A vendor call made inside a web request has a short budget, and a timeout
leaves the row `pending`.** `VendorAccessService::REQUEST_TIMEOUT_SECONDS`
(**6**, set from `T-093`'s measurements on 20 September 2026 and no longer
provisional) bounds the wait a Peer or a creator can be made to pay
for one vendor call. `T-093` found a create at 1.68 to 2.44 seconds alone and
3.76 contended, and a read at 0.52 to 0.84, so 5 left 1.24 seconds before a
call that would have worked became a false timeout
(`D-034`). The value is a parameter on every
contract method that can call the vendor, because an integration may not
import `app/Services` (`tests/Feature/ArchitectureTest.php:139-147`), and it is
a budget, not an order: each vendor's client sets its own timeout on its
`Http::` chain and uses whichever is shorter, its own or the budget, so it may
shorten the wait and never lengthen it (`D-034`). The same budget goes to
`T-044`'s `ConnectionService::fresh()`, so a token renewed first adds at most
one more budget, and only when it is within `T-044`'s `REFRESH_MARGIN_MINUTES`
of expiring. The integration answers a timeout with `pending(ERROR_TIMEOUT)`; the Peer
lands back on the Series page with the pending sentence and presses Open
again.

**A request has a deadline, not only a per-call budget** (`F08`, the review
of 20 September 2026). `D-034` bounds one call, and Open makes as many as
three — a token renewal, a read and a create — before it answers, each with
its own budget, so the caller's real worst case was never stated.
`REQUEST_DEADLINE_SECONDS` (**12**, kept on 20 September 2026 against
`T-093`'s timings, which confirmed the guess rather than moved it) is set when the entry point calls
in, and every step afterwards is given whatever is left of it rather than a
fresh budget: the renewal through `ConnectionService::fresh()`, the advisory
lock's acquisition, and the vendor call itself. A step with nothing left does
not run — the row is left as it stands and the Peer reads the pending
sentence — so no request can outlive the deadline whatever the vendor does.
Try again now and a replace's Episode checks carry their own deadline for the
same reason, and the number is what bounds them rather than a count of rows.

**Every vendor call takes the connection through `T-044`'s
`ConnectionService::fresh()` first, and a vendor 401 marks it for
reconnect.** Google's access token lasts about an hour, and `T-044`'s daily
`qori:connections:refresh` keeps the refresh token alive rather than every
access token fresh, so `grant()`, `checkGrant()`, `revoke()`,
`checkContainer()` and `checkItem()` — every call this class makes, from
`attempt()`, `verify()`, a revoke, `attach()` and `checkEpisode()`, and from
the methods `T-094` adds to it, `describeItem()` and `checkItems()` — first read
the Group's connection through `freshConnectionFor()`: a connection that
`isLive()` is passed to `fresh()` with the caller's budget, before any
container lock is taken, so the lock never waits on a refresh and `T-044`'s
`'connection'` lock and this task's never nest. After it, a row that is no
longer `isLive()` (the refresh found the token revoked, and `T-044` marked it)
is the unusable-connection case below, and a row whose token has still expired
(the refresh timed out or the vendor errored) calls nothing and leaves a grant
`pending` with `ERROR_TOKEN_EXPIRED`, for the next trigger to renew. An
integration answers a 401 — the creator's token refused — with
`ERROR_CONNECTION_UNUSABLE`, and never marks anything itself, since it may not
import `app/Services`; the service then calls
`ConnectionService::markForReconnect($connection, 'unauthorized')`, which is the
`reconnect_reason` `T-044` leaves to this task, and which emails the owner once,
as `T-044` does for any token that stops working. The grant being attempted goes
`needs_creator` with `ERROR_CONNECTION_UNUSABLE`, the code a disconnected
provider already gives it, and the connection waits on a reconnect like any
other. A 401 on a re-check marks the connection and leaves the row as it was,
as `verify()` does for any connection that is not live, because a refused
token says nothing about the Peer's permission; on a revoke it is a failed try
with `connection_unusable`, and on an item check it answers `NeedsCreator`.

**One retry rule everywhere: an attempt runs when `next_attempt_at` is null
or past, and the person pressing Open is what retries** (`D-040`). Nothing
retries on its own any more, so the rule's job is narrower and more
important: it stops a Peer pressing Open repeatedly from hammering a vendor
that has just asked for a pause, and it makes a `Retry-After` binding on
every caller. A `pending` failure sets `next_attempt_at` by
`BACKOFF_MINUTES`, whose last value — fifteen minutes — repeats; a vendor
`Retry-After` replaces the
backoff. The first failure costs nothing, because a backoff protects a vendor
from a loop and the thing retrying here is a person pressing a button. A
`needs_creator` row keeps the last backoff value, and is cleared
at once when the creator reconnects or presses Try again now. An Open that
arrives before the row is due makes no call and answers the pending sentence
with the time in it, so the Peer is told to come back rather than left to
guess.

**Current access is re-checked, not only first access.** `awaiting_acceptance`
rows and `granted` rows are re-read from the vendor through `checkGrant()`,
which reads the stored permission: on Open, for an accepted invitation the Peer may just have taken up and
before a `granted` row is trusted, at Open and nowhere else. `checked_at` throttles
it by `RECHECK_MINUTES` (**15**, kept on 20 September 2026), so pressing Open twice does not
call the vendor twice. Nothing re-reads a `granted` row on a schedule any
more (`D-040`): a permission that disappears is found the next time the Peer
opens that Episode, which is the only moment it matters. A permission the
vendor no longer has
is `pending(ERROR_PERMISSION_GONE)`, which every provider's `checkGrant()`
answers for it; it sets the row `pending` and the same run grants it again.
`T-093`'s step 14 is the observed case this has to catch.

**One grant at a time per target, by `T-044`'s `AdvisoryLock`, keyed on the
provider and the target's external id.** `attempt()` and `verify()` run their
vendor call and row write inside
`AdvisoryLock::run('container', $provider->value.':'.$externalTargetId, …)`,
with the row's own `provider` and `external_target_id` — the container's
values for a container grant, the file's for an item grant, and the row's
copies once its container row is gone; `attach()`'s write takes the same lock
for the container it writes. `T-093` watched Google apply concurrent
permission changes on one file about half a second apart, so the lock on an
item is the same guard for the same reason. The local cache is `array`/`file`, whose
locks are per process, and Neon's pooler is PgBouncer in transaction mode, where
a session-level `pg_advisory_lock` is not guaranteed to be released on the
connection that took it. `pg_advisory_xact_lock` inside `DB::transaction()`,
which is what `AdvisoryLock::run()` takes, is the one primitive that behaves the
same in tests, locally and in production. `T-044` builds it for its
per-connection refresh, keyed `'connection'`, and this task calls it rather
than keeping a second class around the same statement. The lock covers only
the vendor call and the row write, so a grant that fails there rolls back its
own row and nothing else.

**There is no scheduled anything in this task** (`D-040`). No
`qori:access:reconcile`, no command, no schedule line, no Group loop, no
`SWEEP_TIMEOUT_SECONDS`. The eager model needed one because grants were made
before anybody wanted them and something had to finish the ones that failed;
demand-driven grants have a retrier already, and it is the person pressing
Open. What the sweep would have cost is what decided it: one call per Peer
per Episode whether or not it was opened — twelve thousand calls for a Series
of twenty Episodes and three hundred Peers, and 220 to 328 minutes of them —
against a fair, bounded, non-overlapping scheduler that Qori would have had
to build and operate first. `ConsoleAccessTest`'s allow-list is untouched,
because no new `acrossAllGroups()` caller exists to add.

**No grant row exists until an attempt has been made** (`D-040`). A row
records what happened when Qori asked a vendor, so there is nothing to record
before it asked. Attaching a container writes no rows, adding an Episode
writes no rows and `ensureItem()` is gone, a purchase writes no rows, and a
Series with a hundred Peers and no opens has a hundred Accesses and zero
grants. The first Open on an Episode creates its row and attempts it in the
same request. This is also what makes the Series page cheap: it reads rows
that exist and assumes nothing about the ones that do not.

**Open grants exactly the item it is opening.** One Episode, one target, one
call. There is no `INLINE_GRANT_LIMIT` and nothing to bound, because the work
a request does no longer scales with the size of the Series: a container
provider grants its one container, an item provider grants the one file. The
Peer waits a create — 1.68 to 2.44 seconds at `T-093`'s measurement — and
then the redirect happens. The page has to show that wait: Open is a form
that disables itself and says so, never a link that appears to do nothing.

**The identity a Series needs is read from its targets, not its containers**
(`F03`, the review of 20 September 2026). `VendorIdentityService::neededFor()`
was specified over the Series' active `SeriesContainer` rows, and `D-036`
left Google Drive with none, so a Drive-only Series told a buyer it needed no
Google account, showed none of the before-buying lines and never released its
`awaiting_identity` rows. The providers a Series needs are therefore derived
the way the grants are: every container on the Series, plus the
`connection()` of every Episode whose provider grants on an item. `T-092`
owns the method; this task owns the helper it reads,
`providersNeededBy(Series $series)`, so one definition serves checkout, the
Series page and the ensure step and they cannot drift apart. Under `D-040`
this matters more, not less: with no rows written ahead of use, the Series'
targets are the only thing that knows what a Peer will be asked for.

**The principal a grant was made to is stored on the row** (`F04`). A grant
carries `principal` — the address or subject the vendor was actually given —
written when the attempt is made and never overwritten in place. Without it,
a Peer who changes their vendor account leaves a permission on the old one
that nothing can name, and a check of that old permission still answers
`granted` while the new account cannot open a thing. When a confirmed
identity no longer matches the row's `principal`, the row is not reused: its
old permission becomes a revoke of its own, and a new row is written for the
new principal. Removing an identity and confirming another goes down the same
path, which is the case the review found `$replaced` missing entirely.

**A permission two purchases share is not revoked by either alone** (`F02`).
Uniqueness on `vendor_grants` is `(access_id, target)`, which is Qori's
bookkeeping; the vendor has one permission per
`(provider, external_target_id, principal)`, and one file in two Series, two
Episodes on one file, or two Qori people who confirmed the same vendor
account all produce two rows over one permission — `permissions-create-repeat.json`
shows Google returning the identical id. So a revoke first counts the other
rows on the same triple inside the Group that `entitles()` — `granted`,
`awaiting_acceptance` **or `attempting`** — under the same target lock; if any
remain, the row is marked
`revoked` locally and no vendor call is made, and the log says which rows
held it. Only the last one calls the vendor. **`attempting` is in the count
because it is the state that would otherwise break it**: a create went out
and its answer was lost, so the vendor may be holding a permission for that
row, and a count that cannot see it lets a different row look like the last
entitlement and revoke access somebody is still owed. `revoke_failed` is
**not** in the count, and that is the same reasoning read the other way: its
entitlement has ended and only the removal failed, so counting it would leave
the permission standing for ever. Adoption of a permission Qori
did not create follows the same rule, and each provider task states what its
`grant()` does when the vendor returns a role wider than reader —
`permissions-create-repeat-over-writer.json` is the observed case.

**Replacing a container deletes the old row and queues its grants for
revoke.** A Series already holding a container for that provider gets the new
one in the same `attach()` call: the old `series_containers` row is deleted —
which is why every grant carries its own copy of `provider` and
`external_target_id` — its `granted` and `awaiting_acceptance` rows become
revokable, its other rows are set `revoked` with `revoked_at` (nothing was
granted there to take back, and a `needs_creator` row with no container would
otherwise stay on `T-157`'s list for good), and **no row of any kind is
written on the new container** (`D-040`): the Peer's next Open on an Episode
creates its row and grants it in that request, as it does on a Series that
has never had a container. A `revoke_failed` row of the old container is left
alone, because something is still out there and the creator owns it. Once that write has committed, `attach()` checks the affected
Episodes against the new container, at most `MANUAL_RETRY_LIMIT` of them
(below).

**Reconnecting the same account retries at once; connecting a different one
marks every container for a new pick.** `T-044` dispatches
`App\Events\ConnectionReconnected` with `connection`, `sameAccount` and
`previousExternalId`, and registers no listener. This task's
`App\Listeners\ResumeGrantsAfterReconnect` hands the three to
`reconnected()`, which runs inside `CurrentGroup::runFor()` for the
connection's Group, because `T-044`'s landing sits under `/u`, where no Group is
current. The listener is found by Laravel's event discovery, which is on
(`bootstrap/app.php` leaves the `withEvents()` that `Application::configure()`
calls as it is), and is not also registered with `Event::listen()`:
a second registration runs a listener twice for one event, as
`CreateGroupForNewUser` ran until `T-147` removed its hand registration from
`AppServiceProvider::boot()`, and `ListenerRegistrationTest` fails on one. Same account (tokens
refreshed): every `needs_creator` row of that provider in the Group goes back
to `pending` with `next_attempt_at` null, so the Peer's next Open grants it,
and every `revoke_failed` row whose last try failed with
`connection_unusable` is retried once inline, so a Peer removed while the
account was disconnected comes off as soon as it is back, and whatever still
fails stays on the creator's list. Different account: the
stored folder and meeting ids may be unusable, so every container of that
provider becomes `repick`, its non-granted rows become `needs_creator` with
`ERROR_CONTAINER_REPICK`, granted rows are left alone because the old grant
may still work, `Log::info` names the connection, `previousExternalId` and the
containers marked, and the Integrations page tells the creator which Series to
pick again. For an item provider there is no container to mark: its
non-granted rows become `needs_creator` with `ERROR_ITEM_REPICK`, which the
Integrations page reads like any other reason, and the creator picks each
Episode's file again on the Series page — `T-093` confirmed a different
account's token gets a 404 on a file it never picked, and `T-094`'s item
check is what flags each Episode there.

**While a provider is disconnected, the step calls that vendor for nothing and
takes nobody out.** `T-044`'s disconnect keeps the `connections` row and drops
its tokens, and its dialog says what that does to people already let in
(`D-021`), so this task states it. With the Group's connection for the
provider missing or not `isLive()` (`T-044`; disconnected, or waiting on a
reconnect, which a vendor 401 also leaves it): a due row becomes
`needs_creator` with `ERROR_CONNECTION_UNUSABLE` and no call, as below;
`verify()` makes no call
and leaves an `awaiting_acceptance` or `granted` row, and its `checked_at`, as
they are; a revoke makes no call and counts as a failed try with the same
code. Open on a `granted` row still answers the provider's `openLink()`,
passed the kept row, because every provider draft's `openLink()` reads what
Qori stored and makes no call (`T-094`, `T-096`, `T-098`, `T-100`, `T-101`).
So, while disconnected: people already let in keep opening, nobody new is let
in, and a Peer removed meanwhile stays in the vendor account: their row is
`revoke_failed` on the creator's list from the moment the removal was tried,
with the line saying the account has to come back (`D-039`), and the
reconnect above is what takes them out.

**Replacing or removing a container shows its impact before it is posted
(`D-021`), and this task declares the shape of that answer and nothing else.**
`App\Data\ContainerChangeImpact` is created here — the provider, the count of
active Accesses and the Series' Episodes on that provider, with a `kind()`
saying which set of sentences applies — because four tasks build one and none
of them should declare it. `T-157` produces it, from local reads alone, and
renders it in `ContainerChangeDialog.vue`; `T-100` builds `kind()`'s `meeting`
arm and the meeting copy, and `T-101` reads them from `T-100`; the replace and
remove controls that open the dialog are the provider tasks' own panels and
pages. **Nothing in this task constructs one**, which is the whole of the
arrangement: structure in the foundation, meaning in the task that means it,
exactly as `GrantResult::ERROR_PERMISSION_GONE` is declared once here for
`T-094` and `T-098` to share.

An item provider has no such change to show at all. Changing one Episode's
file touches that Episode and no other, so its provider's page says what it
does in its own copy (`T-094`) and opens no dialog; a container is the only
target whose replacement moves everybody at once, which is why it is the only
one that has to be described before it is posted.

**A replace checks the affected Episodes from `attach()`, at most
`MANUAL_RETRY_LIMIT` of them inline, and `checkEpisode()` is declared here
rather than in `T-094`.** So the flags are on the page the creator lands on,
`attach()`'s replace branch reads the Series' Episodes on that provider
directly — **not** through `impactOf()`, which went to `T-157` and would be a
call into the task that depends on this one — and, once the write has
committed and outside the container lock,
calls `checkEpisode($episode, REQUEST_TIMEOUT_SECONDS)` for the first
`MANUAL_RETRY_LIMIT` of its Episodes, in the Series' order — the cap Try again
now has, so a Series of forty file Episodes on a slow vendor cannot hold the
request for minutes. The rest wait for `T-094`'s daily `qori:episodes:check`,
whose pass calls the same `checkEpisode()`, and the dialog's Episodes sentence
promises a check "at once" only for a single Episode. The limit stays
set from `T-093`'s measured 0.85s per check on 20 September 2026, at twelve. The call sits in
`attach()` because every container provider replaces through it — `T-094`'s
`SeriesContainerController`, which `T-096` and `T-098` extend, `T-100`'s
`SeriesMeetingService` (its `LiveSessionService` until `D-026` gave that name
to `T-125`'s state), `T-101`'s `TeamsMeetingController` — and the method is
declared here because `attach()` is this task's and this is the one task all of
them depend on: `T-096`, `T-098` and `T-100` depend on `T-094`, but `T-101`
does not, and its replace goes through the same `attach()`. `checkEpisode()`
re-reads the Series' container for the Episode's provider unless its
`checked_at` is under `RECHECK_MINUTES` old (a container `attach()` just
checked is not read again), sets its `checked_at` when it is there, sets it
`missing` and flags the Episode when it is gone, and otherwise calls the
provider's `checkItem()` and records the answer in the Episode's `content`
under the two keys `T-094`, `T-096` and `T-098` already read: `checked_at` and
`missing_since`. On an item provider there is no container in the way: the
check is `checkItem()` alone, and `ItemCheck::$insideContainer` is null and
read by nobody. `T-094`'s `checkItems()` is the Group-wide loop over it — each
`Active` container read once, then `checkEpisode()` on each of its Episodes,
which finds the container freshly checked — and the container arm of
`EpisodeCheckController`, which `T-094` builds and `T-090` extends with its
Vimeo and YouTube arm, calls it for Check now. That arm first asks
`handles($episode->provider)` whether a `grant-providers` integration is bound
for the Episode's provider, because `providerFor()` is private and a Vimeo
Episode, whose `connection()` is not null, has no grant provider and is a 404
there until `T-090` adds its arm.

**`checkEpisode()` answers what it found, as `App\Enums\EpisodeCheckOutcome`**
(gatekeeper, 17 September 2026). `Clear`: the file is there and inside the
container, and `missing_since` is now null. `Flagged`: the file is missing or
outside the container, or the container is gone — read as gone just now, or
already marked `missing` — and the Episode now carries `missing_since`, kept
from an earlier flag or set now. `NeedsCreator`: Qori cannot ask until the
creator acts — no usable connection (none, not `isLive()`, or refused just now
with a 401, which marks it for reconnect), or, on a container provider, no
container for the provider on the Series or one marked `repick` — so nothing
is written and the page's own reconnect or pick-again note is what to follow. `Unreadable`: the vendor did
not answer in time or errored — a `ContainerCheck` or `ItemCheck` carrying any
other `errorCode`, a token `fresh()` could not renew, or a `Throwable` — or no
grant provider is bound, which Check now never reaches, because
`EpisodeCheckController` asks `handles()` first. Neither writes anything, and
any earlier flag stays: a failed read is not evidence the file moved, and
"couldn't reach Google Drive" would be untrue of a disconnected account.
`EpisodeCheckController`'s container arm flashes `series.episode_check.clear`,
`.still`, `.needs_creator` or `.unreadable` from it (`T-094`); `attach()`'s
replace and `T-094`'s daily pass ignore the value, because the flags they leave
in `content` are what the page shows.

**Awaiting identity is a status the provider returns, not a check the service
makes.** `grant()` always receives `?GrantIdentity`; this task always passes
`null`, and a provider that needs one answers `GrantResult::awaitingIdentity()`
without a vendor call. The contract stays uniform for link-only providers,
and `T-092` fills `identityFor()` without touching the contract.

**`GrantIdentity` is an `app/Data` value object, not `T-092`'s model.**
`T-092`'s `App\Models\VendorIdentity` hands it over through
`toGrantIdentity()`, so the contract can be written and tested before that row
exists, and its name is not the model's, so no file has to import two classes
called `VendorIdentity`. `CLAUDE.md` names Models, Enums and scalars as what an
integration takes in, so a Data shape going in departs from that sentence,
though not from `ArchitectureTest`, which forbids only `app/Services` and
`app/Http` (`tests/Feature/ArchitectureTest.php:139-147`); passing `T-092`'s
model instead would follow the sentence and tie the contract to a table this
task does not create.

**A blocked Open lands on the Series page, at its notice (`D-020`).** There is
no `shared/OpenBlocked` page. When the grant is not `granted`, `open()` returns
`VendorLink::blocked($state->value, $episode->provider)` and `T-089`'s
`shared.episodes.open` controller turns it into a redirect to
`route('shared.show', $seriesId).'#access'` with the toast
`shared.vendor_notice.redirected`, which is `T-089`'s key. The four non-granted
states are four sentences under `shared.vendor_notice.reasons.*`, read by the
Series page's notice alone, so each state has one sentence in one place; the
notice carries `id="access"` so the fragment lands on it. **Open is enabled wherever pressing it can help, which under `D-040` is most
of the time**: an Episode with no grant row at all, a `pending` row that is
due, and an `awaiting_acceptance` row all show a live Open control, because
pressing it is what makes the grant. Only three states disable it, each with
`shared.vendor_notice.open_disabled` beside it — `awaiting_identity`, where
`T-092`'s prompt is the action; `needs_creator`, where the creator is; and a
`pending` row not yet due, where the notice carries the time. So the
redirect catches a page rendered before the state changed, a saved link, or
Open's own re-check finding a permission gone. `T-089` builds the
Open control; this task disables it, because this task has the state.

**One deadline, spent down by every step inside the request (`F08`).** The
entry points — `ensureOpen()`, `revokeFor()`, `revokeItem()` and `attach()` —
each take `$deadlineSeconds`, defaulting to `REQUEST_DEADLINE_SECONDS`, and
that number is a remaining budget rather than a limit each step gets in full.
Every step reads what is left before it starts and is skipped when there is
not enough for it to finish usefully; nothing inside is given the whole of it.
In order, one Open spends it on:

1. **The lock.** `AdvisoryLock::run(…, $waitSeconds)` is passed what is left,
   capped at its own `WAIT_SECONDS`, not left on the default. It answers
   `false` when the lock was not taken and the callback never ran, so the
   caller branches on the return rather than assuming the work happened, and
   a row whose lock it could not take is left exactly as it was found.
2. **The renewal.** `ConnectionService::fresh()` is given
   `min($remaining, REQUEST_TIMEOUT_SECONDS)`.
3. **The read**, where a `granted` row is older than `RECHECK_MINUTES` or a
   row is `attempting`, at the same cap.
4. **The create**, at the same cap.

A step reached with too little left does not run and does not fail: the row
keeps the status it had, the request returns, and the Peer's next Open
carries a fresh budget. This is why `attempting` matters — a create skipped
for want of budget leaves `pending`, which is a different instruction from a
create that went out and was not answered.

**The row is written before the call, and `pending` no longer means two
things (`F01`).** A row created and then granted in one step cannot tell the
difference between a create that was never sent and a create whose response
was lost, and those are opposite instructions: the first wants sending, the
second wants looking for a permission that may already exist. So the write
comes first and commits on its own — `pending`, with `principal`,
`external_target_id` and `provider` filled in, which is the revocation intent
`F01` asks to outlive the content. The status moves to `attempting`
immediately before the vendor call and to its answer immediately after. A row
found in `attempting` by a later Open is never re-created: it is read with
`checkGrant()` first, because the vendor may already hold the permission, and
only a confirmed absence sends a second create. That is the one place Qori
pays a read to avoid a duplicate, and `D-041` is why it matters — two
permissions over one target and principal are exactly what the last-entitlement
rule cannot count.

A crash between the write and the call therefore leaves a `pending` row that
the next Open sends, and a crash after the call leaves an `attempting` row the
next Open reconciles. Neither is lost, and neither is guessed at.

**Reconciling an `attempting` row means `checkGrant()` has to work without a
`vendor_ref`**, which is the contract change the state forces and which the
read-through of 20 September 2026 found nothing had stated. The whole point of
the state is that Qori never learned the permission's id, so a `checkGrant()`
specified as "read the stored `vendor_ref`" has nothing to read and the state
is unreconcilable. The contract therefore reads: the permission is found **by
`vendor_ref` when the row has one, and otherwise by the row's
`external_target_id` and `principal`** — the triple `D-041` already keys on,
which is why `principal` being written before the call rather than after it
(`F04`) is what makes this possible at all. Each provider task says which call
it uses for the lookup; on Google Drive it is a `permissions.list` on the file
matched by address, which `T-093` already exercised. The same fallback serves
a revoke: an entitling row with no `vendor_ref` is read before it is revoked,
because a revoke by reference cannot be made without one.

**One predicate answers "is this row a live entitlement", and three callers
read it.** `VendorGrantStatus::entitles()` is true for `Attempting`,
`AwaitingAcceptance` and `Granted`: the row's holder is owed the permission
right now. `scopeRevokable()`, `revokeFor()` and `D-041`'s last-entitlement
count all read it, rather than each enumerating states of its own — which is
exactly how `attempting` came to be declared on 20 September 2026 and handled
by none of the three, so that a permission Qori created would never have been
revoked on refund and would have been invisible to the count. A predicate with
three callers cannot drift the way three lists can. It replaces
`mayHoldPermission()`, drafted the same day and never called: that predicate
also counted `revoke_failed`, which reads correctly as "the vendor may still
be holding this" and incorrectly as "somebody is still entitled to it", and
the second is the question all three callers are actually asking.

**The notice explains, and Open is the only thing to press (`D-020`,
`D-040`).** Rewritten on 20 September 2026, when the stream owner dropped
`checkNow()`: `D-040`'s case for granting at Open was "one way in … with no
second mechanism to understand", and a Check again button beside it was that
second mechanism. A notice names the state and who resolves it, and nothing
more. `awaiting_acceptance` tells the Peer to accept at the vendor and open
the Episode again, and each provider's own step for that state (`T-096`'s
Join panel, `T-098`'s invitation line) opens in a new tab so the Series page
stays in reach. `needs_creator` offers the Peer nothing to press, and
`awaiting_identity` is `T-092`'s prompt. No next-try sentence and no timer:
nothing tries on its own, so there is nothing to count down to.

What this costs, accepted with the decision: a Peer who accepts an invitation
at the vendor and comes back sees the old notice until they press Open, where
a Check again would have refreshed the page in place. `D-040` already accepted
that the page does not poll, and one stale sentence a press away is a smaller
thing than a second mechanism with its own route, throttle and vocabulary.

An Inertia request redirected to a URL with a fragment is answered 409
and followed by the client as a visit, and the toast is reflashed across it
(`vendor/inertiajs/inertia-laravel/src/Middleware.php:150-152`, `:172-174`,
`:210-215`), so the fragment and the toast both survive the POST.

**This task writes six Peer-facing lines and one refusal, and nothing else.**
They go in `lang/en/shared.php`, which `T-089` creates as the Peer surface's
file and which exists when this starts, except the one refusal, which goes in
`errors.php`. After the cut of 20 September 2026 this task writes nothing into
`connections.php` or `series.php`: the creator's sentences went to `T-157`
with the lists they sit under, and the impact dialog's went to `T-157` and
`T-100`. That is the whole of the copy, and it is worth stating plainly,
because a foundation task that writes seven sentences and a task that writes
seventy are different things to review.

**A revoke is tried once, inline, and a failure is listed for the creator**
(`D-040`, and `F01`). Grants can be lazy because somebody eventually opens
the file; nobody ever opens anything in order to be removed, so cleanup is
the one thing that cannot be demand-driven. `revokeFor()` and `revokeItem()`
make their attempt in the request that caused them — a refund, a removal, a
replaced file, a deleted Episode — and a failure does not retry: the row
becomes `revoke_failed`, keeping `vendor_ref`, `principal`,
`external_target_id` and `provider`, and `T-157`'s list shows it. That list is the durable revocation intent the review asks for
under `F01`, which is why **`episode_id` is null on delete rather than
cascade**: a row whose Episode has been deleted is exactly the row that still
has a permission to remove, and the old schema destroyed it.

**Both paths that delete an Episode revoke before they delete, and this task
owns those two edits** — `EpisodeService::remove()`
(`app/Services/EpisodeService.php:301`) and `SeriesService::purge()`
(`app/Services/SeriesService.php:279`, one per Episode), each calling
`revokeItem($episode)` above the delete, so the attempt is made while the row
still points at something and a `revoke_failed` row outlives both. Under
`D-036` this is no longer theoretical: an item grant is on the Episode's own
file, so deleting the Episode is deleting the only thing that names the
permission. **The Notes below said these two paths "touch no grant", and that
was true only while grants were per-container** — the blueprint's per-item
columns had been dropped and `D-036` brought them back. It is corrected there.

**`T-156` edits the same two methods, and this task depends on it** (the
stream owner, 20 September 2026). `T-156` stops an unrelated leak in the same
place — a deleted Episode leaves its file in R2 and its `media_assets` row
behind — and it is `S`, unblocked and fixes something already happening, so it
lands first and this task's one-line revoke goes on top of it. That is
`PROCESS.md`'s usual arbitration for two tasks wanting one file, and it also
keeps the checker honest: two tasks `doing` against one file is a gate
failure, and the dependency is what makes the order explicit rather than
lucky.

**What the creator does about all of this is `T-157`'s, and this task's job
is to leave it enough to read** (`D-040`). Three lists live there — the grants
that need the creator, the people Qori could not remove, and the containers to
pick again — each with a Try again the creator presses, in the provider
sections `T-044` built. None of it is specified here. What is specified here
is the state each list selects on and every column it reads, which is why
`revoke_failed` keeps `vendor_ref`, `principal`, `external_target_id` and
`provider` when its call fails, and why `last_error_code` holds a slug a
sentence can be keyed from. A `pending` or `attempting` row is on none of the
three: the Peer's own next Open handles both, and a list of rows nobody needs
to act on is a list that teaches a creator to ignore it.

The dependency runs one way only. `T-157` reads the states this task writes,
so it depends on this task and this task calls nothing of its — which is also
why `attach()`'s replace reads the Series' Episodes directly rather than
through `impactOf()`, the one place the two nearly crossed.

**Every query that reads a grant reads both targets** (`F10`). The review
found four consumers still shaped for a container after `D-036` moved the
target: Try again now's query requiring an active Access "with a container",
its creator list eager-loading `container.series`, the Peer notice taking its
provider and URL from a container, and `checkEpisode()`'s contract demanding
an `insideContainer` truth that an item result sets null. **The cut of
20 September 2026 split them two and two**: the Peer notice and
`checkEpisode()` are this task's and are answered below; the two queries went
to `T-157` with Try again now, and that task carries them. The rule that
covers all four is stated here anyway, because this task owns the model and a
rule kept in the task that reads it is a rule the next reader has to
rediscover: a query selects on
`(group_id, status)` and reads the row's own `provider` and
`external_target_id`; the Peer notice reads the row, never the container; and
`insideContainer` is nullable on `ItemCheck` and read only where a container
exists, which `checkEpisode()`'s contract now says by branching on
`grantsOn()` rather than assuming one — the last of the four, written in on
20 September 2026. A grant's Series is reached through its Access, which both targets
have, rather than through a container only one of them has.

**Payment recovery is never blocked or undone by a grant.** `grant()` returns
its Access whatever the vendor or the grant row did, so
`CheckoutService::fulfil()` records `Granted`; a webhook replay (`T-102`)
takes the existing-access branch and runs the step again, which creates the
row that failed to save or retries the one that is due. Nothing here reads a
grant to decide whether an Access exists.

## Preconditions

`T-044` done, so `lang/en/connections.php`, the provider sections, reconnect
with its `ConnectionReconnected` event, `ConnectionService::fresh()` and
`markForReconnect()`, and `AdvisoryLock` exist, and its migration
`2026_09_20_000000` has run before this task's `2026_09_20_000100`; `T-089`
done, so Open is a server route with `VendorLink`, a blocked
link redirects to `shared.show#access`, and `lang/en/shared.php` exists;
`T-093` done: it found that a folder grant under the narrow scope does not
hold while anything beneath the folder is unpicked, and `D-036` answered it
with per-file grants for Google Drive, which is the second target below;
`T-156` done, because it edits `EpisodeService::remove()` and
`SeriesService::purge()` for the storage leak and this task adds one line
above each of the same two deletes (the stream owner, 20 September 2026).
Tests run on the local Postgres (`_testing`), which the
advisory lock needs.

**Data this task verifies against:** a clean database.

**Equipment:** none — no vendor is called, and nothing here is scheduled, so
the Scheduler question this task used to carry belongs to whichever task
next adds a command (`D-040`).

**Spike:** none owed by this task. No vendor payload is named here; the columns
that hold vendor ids are opaque to this task, and each provider task says what
it stores in them from its own fixture under `tests/Fixtures/<vendor>/`.

## Scope

**In:**

- `series_containers` and `vendor_grants`, their models, enums and factories,
  with a grant on a container or on one Episode's item (`D-036`).
- The `GrantsPeerAccess` contract with `grantsOn()`, `GrantTarget`, the four
  `app/Data` results and `GrantIdentity`, tagged `grant-providers` in
  `IntegrationServiceProvider`.
- `VendorAccessService`: ensure, for the one target a Peer is opening;
  verify, revoke and its unresolved rows, attach and replace, reconnected,
  state, `providersNeededBy()`, and the target lock on `T-044`'s
  `AdvisoryLock`; a token renewed through `T-044`'s
  `ConnectionService::fresh()` before every vendor call, and a connection
  marked for reconnect on a vendor 401; `handles()` and the
  single-Episode item check a replace runs within `REQUEST_DEADLINE_SECONDS`,
  with `EpisodeCheckOutcome` for what it found — the check `T-094`'s Check now
  button and daily pass both call, not the deleted `checkNow()`. Every entry point carries a
  request deadline that the steps inside it spend down (`F08`). The three
  methods that serve only the creator's surfaces — retry needing the
  creator, retry a failed removal and `impactOf()` — are `T-157`'s.
- `ResumeGrantsAfterReconnect`, the listener that hands `T-044`'s
  `ConnectionReconnected` to `reconnected()`.
- Open as the one place a grant is made (`D-040`), the three reconciliation
  entry points, the Peer-facing notice on the Series page, and the blocked
  link on Open (`D-020`). The creator's two lists are `T-157`'s.
- **One way in, and only one.** Open is the whole of the Peer's mechanism
  (`D-040`); Check again and `checkNow()` are gone, and Try again now is the
  creator's and went to `T-157` with the list it sits under.
- **The shape a container change is described in, but not the describing.**
  `vendor_grants.join_url` is declared in this task's create migration
  because that is where the table is created, and `ContainerChangeImpact`
  declares a `kind()` this task never calls — structure in the
  foundation, meaning in the task that means it, as
  `GrantResult::ERROR_PERMISSION_GONE` is already declared once for `T-094`
  and `T-098` to share. `impactOf()`, the dialog, the `containerImpact` prop
  and the folder copy are `T-157`'s. `kind()`'s `meeting` arm, the four
  `series.container_change.meeting.replace.*` lines, case 60 and the Zoom half
  of case 28 are **`T-100`'s**, which `T-101` reads from it (the stream owner,
  20 September 2026); `D-024` still holds both. The four
  `series.container_change.meeting.remove.*` lines are written by nobody: no
  task in the plan builds a meeting remove, and four sentences describing an
  action nothing offers are four sentences to keep true for nothing.
- **The revoke call in the two paths that delete an Episode** —
  `EpisodeService::remove()` and `SeriesService::purge()`, one line each above
  the delete. `T-156` edits the same two methods for the storage leak and
  lands first (`depends:`).
- `docs/flows/vendor-access.md` (new), `accesses.md`, `storage.md`,
  `tenancy.md`, the flows index, the tinker recipe.

**Out:**

- Any vendor implementation, OAuth scope or picker, and the picker's sentence
  about what sharing a container shares — the provider tasks.
- The Peer's vendor identity, its `/u/*` page, the Series-page prompt, and the
  call to `ensureOpen()` when an identity is confirmed (`T-092`), and
  `neededFor()` itself, which reads this task's `providersNeededBy()` (`F03`);
  `identityFor()` returns null here.
- Reconnect itself and knowing whether the same account came back — `T-044`,
  which dispatches `ConnectionReconnected` and registers no listener; this
  task's listener calls `reconnected()`.
- The token refresh itself, `ConnectionService::fresh()`, `markForReconnect()`
  and the `AdvisoryLock` primitive — `T-044`; this task calls them.
- The materials arm of the item check and of a replacement's impact
  (`D-030`) — `T-094`, with `T-130`'s `materials` rows (Notes).
- Refusing a sale at a vendor's per-container cap — the provider tasks, which
  own `checkContainer()` callers.
- Revoke on refund (`T-103`), delayed payments (`T-102`), disconnect itself
  and its dialog (`T-044`); this task says only what the ensure step does
  while a provider is disconnected.
- The blocked link's redirect and its toast (`T-089`), and the Open control
  itself (`T-089`); this task disables it.
- The replace and remove controls and pickers that open
  `ContainerChangeDialog` (`T-094`, `T-096`, `T-098`, `T-100`, `T-101`), the
  flags they show beside an Episode, `qori:episodes:check` and the per-Episode
  Check now
  (`share.series.episodes.check`), which `T-094` builds and `T-090` extends.
- Any email to the creator about a failed grant.
- **Everything the creator does about a grant that did not land** — `T-157`:
  the grants-needing-the-creator list, the unresolved-removals list, the
  containers-to-repick list, Try again now and its removal twin,
  `impactOf()`, `ContainerChangeImpact`'s folder reading, `GrantRetryTally`,
  `ContainerChangeDialog.vue`, the `containerImpact` prop, the two routes
  under `share.settings.integrations.*` and the copy for all of it. The
  states this task writes are what that task reads, which is why it depends
  on this one and not the other way round.
- **The meeting reading of a container change** — `T-100` and `T-101`, which
  took it on 20 September 2026 with `D-024`'s hold intact.

## Files

| Path                                                                                                          | Change | Notes                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `database/migrations/2026_09_20_000100_create_series_containers_and_vendor_grants.php`                        | new    | Both tables; after `T-044`'s `2026_09_20_000000`                                                                                                                                 |
| `app/Models/SeriesContainer.php` `app/Models/VendorGrant.php`                                                 | new    | `BelongsToGroup`, `HasUlids`                                                                                                                                                     |
| `app/Enums/SeriesContainerStatus.php` `app/Enums/VendorGrantStatus.php` `app/Enums/GrantTarget.php`           | new    | `GrantTarget`: what a grant is made on, `container` or `item` (`D-036`)                                                                                                          |
| `app/Enums/EpisodeCheckOutcome.php`                                                                           | new    | What `checkEpisode()` found: `Clear`, `Flagged`, `NeedsCreator`, `Unreadable`                                                                                                    |
| `app/Integrations/Contracts/GrantsPeerAccess.php`                                                             | new    | The contract                                                                                                                                                                     |
| `app/Data/GrantResult.php` `app/Data/RevokeResult.php` `app/Data/ContainerCheck.php` `app/Data/ItemCheck.php` | new    | Results                                                                                                                                                                          |
| `app/Data/GrantIdentity.php`                                                                                  | new    | What `grant()` takes; `T-092`'s model builds it                                                                                                                                  |
| `app/Data/ContainerChangeImpact.php`                                                                          | new    | Declared here so `T-157` and `T-100`/`T-101` share one shape; nothing here produces it                                                                                           |
| `app/Services/VendorAccessService.php`                                                                        | new    | The ensure step, revoke, attach, reconnected, `handles()`, the single-Episode item check; `T-044`'s `ConnectionService` by constructor. `T-157` adds the creator's three methods |
| `app/Listeners/ResumeGrantsAfterReconnect.php`                                                                | new    | Hands `T-044`'s `ConnectionReconnected` to `reconnected()`                                                                                                                       |
| `app/Providers/IntegrationServiceProvider.php`                                                                | edit   | `grant-providers` tag beside `media-providers` (`:35-39`)                                                                                                                        |
| `app/Services/AccessService.php`                                                                              | edit   | Constructor dependency and the revoke hook only — `grant()` calls no vendor under `D-040`                                                                                        |
| `app/Services/EpisodeService.php` `app/Services/SeriesService.php`                                            | edit   | `revokeItem($episode)` above the delete in `remove()` and `purge()`; `T-156` edits the same two methods and lands first (`depends:`)                                             |
| `app/Services/PlaybackTicketService.php`                                                                      | edit   | `T-089`'s `open()`: ensure, verify, the grant's `openLink()` or `VendorLink::blocked()`                                                                                          |
| `app/Http/Controllers/Shared/SharedController.php`                                                            | edit   | `vendor` prop with the notice; no vendor call on `show()` (`D-040`)                                                                                                              |
| `resources/js/pages/shared/Show.vue`                                                                          | edit   | `InlineNotice` with `id="access"` from `vendor` — the target `OpenEpisodeController:43` already redirects to; Open disabled                                                      |
| `lang/en/shared.php` `lang/en/errors.php`                                                                     | edit   | Copy below; `shared.php` is `T-089`'s file. `connections.php` is not touched: every creator-facing line went to `T-157`, and no Peer-facing line names a vendor (`D-035`)        |
| `database/factories/SeriesContainerFactory.php` `database/factories/VendorGrantFactory.php`                   | new    |                                                                                                                                                                                  |
| `tests/Doubles/GrantsEveryPeer.php`                                                                           | new    | The fake, answering for the `ConnectionProvider` it is built with (`Dropbox` by default, so `T-092` can build it for `GoogleDrive`); records every call and its timeout          |
| `tests/Feature/Access/VendorAccessTest.php` `tests/Feature/Shared/VendorStateTest.php`                        | new    | 50 and 6 cases, counted from the sections; the first file's cases 61 to 81 are numbered after case 60, so the numbers other drafts cite stay put                                 |
| `docs/flows/vendor-access.md`                                                                                 | new    | The chain above with its token renewal, the reconnect listener and a replace's item check, when built                                                                            |
| `docs/flows/accesses.md` `docs/flows/storage.md` `docs/flows/README.md`                                       | edit   | Hook in the grant chain; the Open chain's vendor branch; index row                                                                                                               |
| `docs/architecture/tenancy.md` `docs/tinker/accesses.md`                                                      | edit   | Two group-owned tables; a recipe                                                                                                                                                 |

## Database

| Table               | Column                    | Type         | Null | Default     | Index / constraint                                                                                                                                                                                              |
| ------------------- | ------------------------- | ------------ | ---- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `series_containers` | `id`                      | ulid         | no   |             | primary                                                                                                                                                                                                         |
| `series_containers` | `group_id`                | ulid         | no   |             | FK `groups` cascade; first in every compound index                                                                                                                                                              |
| `series_containers` | `series_id`               | ulid         | no   |             | FK `series` cascade                                                                                                                                                                                             |
| `series_containers` | `provider`                | string       | no   |             | `ConnectionProvider` value; unique `(group_id, series_id, provider)`                                                                                                                                            |
| `series_containers` | `external_id`             | string       | no   |             | The vendor's id for the folder or meeting, opaque here; unique `(group_id, provider, external_id)`                                                                                                              |
| `series_containers` | `url`                     | string(2048) | yes  | null        |                                                                                                                                                                                                                 |
| `series_containers` | `settings`                | jsonb        | no   | `'[]'`      | `'array'` cast; the string default, never `[]`                                                                                                                                                                  |
| `series_containers` | `status`                  | string       | no   | `active`    | `SeriesContainerStatus`                                                                                                                                                                                         |
| `series_containers` | `checked_at`              | timestamp    | yes  | null        |                                                                                                                                                                                                                 |
| `series_containers` | `created_at` `updated_at` | timestamps   | yes  |             |                                                                                                                                                                                                                 |
| `vendor_grants`     | `id`                      | ulid         | no   |             | primary                                                                                                                                                                                                         |
| `vendor_grants`     | `group_id`                | ulid         | no   |             | FK `groups` cascade                                                                                                                                                                                             |
| `vendor_grants`     | `access_id`               | ulid         | no   |             | FK `accesses` cascade; unique `(group_id, access_id, series_container_id)` and `(group_id, access_id, episode_id)`, and Postgres counts nulls as distinct, so each pair binds only its own kind                 |
| `vendor_grants`     | `target`                  | string       | no   | `container` | `GrantTarget`: what the grant was made on (`D-036`)                                                                                                                                                             |
| `vendor_grants`     | `series_container_id`     | ulid         | yes  | null        | FK `series_containers` null on delete — a replaced container leaves its rows revokable; null on an item grant                                                                                                   |
| `vendor_grants`     | `episode_id`              | ulid         | yes  | null        | FK `episodes` **null on delete** — a deleted Episode's grant is the row that still has a permission to remove (`F01`); set on an item grant, null on a container grant                                          |
| `vendor_grants`     | `provider`                | string       | no   |             | copied from the container, or from the Episode's `provider->connection()`                                                                                                                                       |
| `vendor_grants`     | `external_target_id`      | string       | no   |             | the vendor's id for whichever target it was granted on: the container's `external_id`, or the item's id from the Episode's `content`                                                                            |
| `vendor_grants`     | `principal`               | string       | yes  | null        | The address or subject the vendor was actually given, written at the attempt and never overwritten (`F04`); index `(group_id, provider, external_target_id, principal)` for the shared-permission check (`F02`) |
| `vendor_grants`     | `vendor_ref`              | string       | yes  | null        | The vendor's id for this grant, opaque here; each provider task says what it holds                                                                                                                              |
| `vendor_grants`     | `join_url`                | string(2048) | yes  | null        | A per-Peer URL where a vendor issues one; `T-100` says whether Zoom does                                                                                                                                        |
| `vendor_grants`     | `status`                  | string       | no   | `pending`   | `VendorGrantStatus`, eight cases with `revoke_failed` (`D-040`) and `attempting` (`F01`); index `(group_id, status, next_attempt_at)`                                                                           |
| `vendor_grants`     | `last_error_code`         | string(100)  | yes  | null        | the vendor's own slug, or a `GrantResult::ERROR_*` value                                                                                                                                                        |
| `vendor_grants`     | `attempts`                | smallint     | no   | 0           |                                                                                                                                                                                                                 |
| `vendor_grants`     | `next_attempt_at`         | timestamp    | yes  | null        |                                                                                                                                                                                                                 |
| `vendor_grants`     | `granted_at`              | timestamp    | yes  | null        |                                                                                                                                                                                                                 |
| `vendor_grants`     | `checked_at`              | timestamp    | yes  | null        | last time the vendor confirmed the row's state; index `(group_id, status, checked_at)`                                                                                                                          |
| `vendor_grants`     | `revoked_at`              | timestamp    | yes  | null        |                                                                                                                                                                                                                 |
| `vendor_grants`     | `created_at` `updated_at` | timestamps   | yes  |             |                                                                                                                                                                                                                 |

Migration: `database/migrations/2026_09_20_000100_create_series_containers_and_vendor_grants.php`,
after `T-044`'s `2026_09_20_000000`.

## Code

```php
namespace App\Enums;

enum SeriesContainerStatus: string { case Active = 'active'; case Missing = 'missing'; case Repick = 'repick'; }

/** What a provider grants on (D-036). Container: a folder or a meeting the Series holds. Item: one Episode's own file. */
enum GrantTarget: string { case Container = 'container'; case Item = 'item'; }

enum VendorGrantStatus: string
{
    case AwaitingIdentity = 'awaiting_identity';     // the Peer resolves: confirm the vendor account (T-092)
    case AwaitingAcceptance = 'awaiting_acceptance'; // the Peer resolves: a step left at the vendor
    case Pending = 'pending';                        // nothing has been sent to the vendor for this row; the next Open sends it
    case Attempting = 'attempting';                  // a create was sent and its answer never arrived; the vendor may hold a permission (F01)
    case NeedsCreator = 'needs_creator';             // the creator resolves: reconnect, policy, plan, cap, container
    case Granted = 'granted';
    case Revoked = 'revoked';
    case RevokeFailed = 'revoke_failed';             // the creator resolves: Qori could not take this Peer off, and does not retry on its own (D-040)

    /**
     * A live entitlement to the permission: Attempting, AwaitingAcceptance or Granted. The row's holder is owed it now.
     * scopeRevokable(), revokeFor() and D-041's last-entitlement count all read this and never enumerate states of their
     * own, which is how attempting came to be declared on 20 September 2026 and handled by none of the three.
     * Revoked and RevokeFailed are not entitlements: the entitlement ended and, for the second, only the removal failed.
     */
    public function entitles(): bool;
}

/** What VendorAccessService::checkEpisode() found. Check now reads it; attach()'s replace and the daily pass ignore it. */
enum EpisodeCheckOutcome: string
{
    case Clear = 'clear';           // the file is there and inside the container; missing_since null
    case Flagged = 'flagged';       // missing, outside the container, or the container gone; the Episode carries missing_since
    case NeedsCreator = 'needs_creator'; // no usable connection, or no container for the provider or one marked repick; nothing written, any earlier flag stays
    case Unreadable = 'unreadable'; // the vendor did not answer in time or errored, or no grant provider is bound; nothing written, any earlier flag stays
}
```

```php
namespace App\Models;

class SeriesContainer extends Model   // BelongsToGroup, HasUlids, HasFactory
{
    protected $attributes = ['settings' => '[]'];
    // casts: provider => ConnectionProvider, status => SeriesContainerStatus, settings => 'array', checked_at => 'datetime'
    public function series(): BelongsTo;
    public function grants(): HasMany;    // VendorGrant, series_container_id; attach()'s replace reads it to dispose of the old container's rows
}

class VendorGrant extends Model         // BelongsToGroup, HasUlids, HasFactory
{
    // casts: provider => ConnectionProvider, status => VendorGrantStatus, attempts => 'integer',
    //        next_attempt_at, granted_at, checked_at, revoked_at => 'datetime'
    public function access(): BelongsTo;
    public function container(): BelongsTo;   // SeriesContainer, series_container_id; null on an item grant
    public function episode(): BelongsTo;     // Episode, episode_id; null on a container grant
    public function isGranted(): bool;
    /**
     * pending, attempting or needs_creator, next_attempt_at null or past, Access active — the one retry rule.
     * attempting is due like the others: a create whose answer was lost is work still owed, and a scope that cannot
     * see it is a row nothing ever reconciles.
     */
    public function scopeDue(Builder $query): Builder;
    // scopeRecheckable() is gone with checkNow(), its only caller: ensureOpen() re-verifies the one row it is opening
    // against RECHECK_MINUTES, which is a comparison on that row and never a query across the Access.
    /** status->entitles(), and the Access revoked or the target gone — the revoke pass. */
    public function scopeRevokable(Builder $query): Builder;
}
```

```php
namespace App\Integrations\Contracts;

/**
 * $timeoutSeconds, last on every method below, is a budget, never an order (D-034): the vendor's client in
 * app/Integrations/<Vendor> sets its own timeout on its Http:: chain and uses whichever is shorter, its own or the
 * budget, so it may shorten the wait and never lengthen it. Every caller passes what is left of its request's
 * REQUEST_DEADLINE_SECONDS, capped at REQUEST_TIMEOUT_SECONDS (F08); both were set from T-093's timings on
 * 20 September 2026 and are not provisional. A timeout is answered as pending(ERROR_TIMEOUT), never thrown.
 * Every $connection arrives through ConnectionService::fresh() (T-044), except openLink()'s: it is passed the kept row,
 * live or not, and makes no call (a disconnected provider, in the Decisions). A 401 — the creator's token refused — is
 * answered with GrantResult::ERROR_CONNECTION_UNUSABLE: needsCreator() from grant() and checkGrant(), RevokeResult::failed(),
 * the errorCode of a ContainerCheck or ItemCheck. The service marks the connection for reconnect on it; an integration
 * marks nothing, since it may not import app/Services.
 */
interface GrantsPeerAccess
{
    public function provider(): ConnectionProvider;
    /** What this provider grants on (D-036). A Container provider gets one row per Series container, an Item provider one per Episode. */
    public function grantsOn(): GrantTarget;
    /** Container providers only; an Item provider answers ContainerCheck(exists: false) and is never asked. */
    public function checkContainer(Connection $connection, string $externalId, int $timeoutSeconds): ContainerCheck;
    /** The row carries provider, external_target_id and whichever of container and episode its target is. A provider that needs an identity and is given null answers awaitingIdentity() with no vendor call. */
    public function grant(Connection $connection, VendorGrant $grant, ?GrantIdentity $identity, string $email, int $timeoutSeconds): GrantResult;
    /**
     * Reads the permission the row names on its target: granted, awaitingAcceptance, or pending(ERROR_PERMISSION_GONE)
     * when there is none. By vendor_ref when the row has one, and **otherwise by external_target_id and principal** —
     * an attempting row never learned its permission's id, and that lookup is the only way it can be reconciled (F01).
     * Each provider task says which call it uses for it; on Google Drive it is a permissions.list matched by address.
     */
    public function checkGrant(Connection $connection, VendorGrant $grant, int $timeoutSeconds): GrantResult;
    public function revoke(Connection $connection, VendorGrant $grant, int $timeoutSeconds): RevokeResult;
    public function openLink(Connection $connection, Episode $episode, ?VendorGrant $grant, int $timeoutSeconds): VendorLink;
    public function checkItem(Connection $connection, Episode $episode, int $timeoutSeconds): ItemCheck;
}
```

```php
namespace App\Data;

class GrantResult
{
    public const ERROR_CONNECTION_UNUSABLE = 'connection_unusable';   // needs_creator; also every integration's answer to a 401, which marks the connection
    public const ERROR_CONTAINER_MISSING = 'container_missing';       // needs_creator
    public const ERROR_CONTAINER_REPICK = 'container_repick';         // needs_creator
    public const ERROR_ITEM_MISSING = 'item_missing';                 // needs_creator; the vendor no longer returns the Episode's item
    public const ERROR_ITEM_REPICK = 'item_repick';                   // needs_creator; a different account reconnected, so the item has to be picked again (D-036)
    public const ERROR_NO_INTEGRATION = 'no_integration';             // pending, and Log::error — a deployment fault
    public const ERROR_PERMISSION_GONE = 'permission_gone';           // pending; every checkGrant()'s answer when the stored permission is gone — verify() falls through to attempt()
    public const ERROR_TIMEOUT = 'timeout';                           // pending
    public const ERROR_TOKEN_EXPIRED = 'token_expired';               // pending; fresh() could not renew an expired token, so nothing was called
    public const ERROR_UNEXPECTED = 'unexpected';                     // pending

    public function __construct(
        public VendorGrantStatus $status,           // never Revoked
        public ?string $vendorRef = null,
        public ?string $joinUrl = null,
        public ?string $errorCode = null,          // the vendor's own slug, or an ERROR_* value
        public ?int $retryAfterSeconds = null,     // from a Retry-After the vendor sent
        public ?string $upstream = null,           // raw vendor code or status; logs only
    ) {}

    public static function granted(string $vendorRef, ?string $joinUrl = null): self;
    public static function awaitingIdentity(): self;
    public static function awaitingAcceptance(string $vendorRef, ?string $joinUrl = null): self;
    public static function pending(string $errorCode, ?int $retryAfterSeconds = null, ?string $upstream = null): self;
    public static function needsCreator(string $errorCode, ?string $upstream = null): self;
}

class RevokeResult   { public function __construct(public bool $revoked, public ?string $errorCode = null, public ?int $retryAfterSeconds = null, public ?string $upstream = null) {} public static function revoked(): self; public static function failed(string $errorCode, ?int $retryAfterSeconds = null, ?string $upstream = null): self; }
/** url: the container's own vendor page, which attach() writes to series_containers.url when its caller passed none, and the Peer notice then reads. */
class ContainerCheck { public function __construct(public bool $exists, public ?string $url = null, public ?string $errorCode = null, public ?string $upstream = null) {} }
/** name, mimeType and url: the item as the vendor reports it, for T-094's describeItem(); checkEpisode() reads none of them. */
class ItemCheck      { public function __construct(public bool $exists, public ?bool $insideContainer = null, public ?string $name = null, public ?string $mimeType = null, public ?string $url = null, public ?string $errorCode = null, public ?string $upstream = null) {} }
/** What grant() takes; T-092's App\Models\VendorIdentity::toGrantIdentity() builds it. */
class GrantIdentity  { public function __construct(public ConnectionProvider $provider, public string $email, public ?string $subject = null) {} }

/** What replacing or removing one container touches (D-021); local reads only. */
class ContainerChangeImpact
{
    /** @param list<array{id: string, title: string}> $episodes the Series' Episodes on $provider, in the Series' order */
    public function __construct(
        public ConnectionProvider $provider,
        public int $peers,          // active Accesses on the Series
        public array $episodes,
    ) {}

    /**
     * 'meeting' for Zoom and Teams, 'folder' for every other container provider: which series.container_change.{kind}.*
     * lines apply. Declared here and implemented nowhere in this task, which constructs no ContainerChangeImpact at all:
     * T-157 produces the folder reading, T-100 builds the meeting arm and its copy, T-101 reads both from T-100.
     */
    public function kind(): string;
}

// App\Data\VendorLink is T-089's, blocked($state, $provider) and isBlocked() included; this task calls
// VendorLink::blocked($state->value, $episode->provider) from open() and adds nothing to the class. T-089's controller
// redirects a blocked link to shared.show#access (D-020), where shared.vendor_notice.reasons.{state} is the notice.
```

```php
namespace App\Services;

class VendorAccessService
{
    /**
     * The budget one vendor call is given, which the vendor's client may only shorten (D-034). Set from T-093's timings on
     * 20 September 2026: a create measured 1.68-2.44s alone and 3.76s contended, so 5 left 1.24s before a call that would
     * have worked became a false timeout. Two full-budget calls also fill REQUEST_DEADLINE_SECONDS exactly, which is what
     * one Open makes — a read and a create.
     */
    public const REQUEST_TIMEOUT_SECONDS = 6;
    /**
     * The whole of one entry point's vendor work, spent down across renewal, lock and call; a step with nothing left does
     * not run (F08). Kept at 12 on 20 September 2026 against T-093's timings, which confirmed the guess rather than moved
     * it: the worst realistic Open is a 3s lock, a renewal, a 0.85s read and a 2.44s create, about 7.3s.
     */
    public const REQUEST_DEADLINE_SECONDS = 12;
    /**
     * Minutes before Open will attempt a pending row again after the n-th failure; the last value repeats. Shortened on
     * 20 September 2026 from [1, 5, 30, 120, 1440], which was written for a sweep that retried on its own and, against
     * D-040's "retried by the person pressing Open again", locked that person out for a day. A backoff protects a vendor
     * from a loop and a human pressing a button is not a loop, so the first failure costs nothing and the fifth costs
     * fifteen minutes.
     */
    public const BACKOFF_MINUTES = [0, 1, 2, 5, 15];
    /**
     * A granted or accepted row is re-verified at Open when it was last checked longer ago than this. Kept at 15 on
     * 20 September 2026: one 0.85s read on the first Open of each quarter hour, and it is the only way Qori notices a
     * permission a creator removed by hand, which T-093 found reads as the same 404 as one Qori removed.
     */
    public const RECHECK_MINUTES = 15;
    // MANUAL_RETRY_SECONDS is T-157's: Try again now is its only caller. MANUAL_RETRY_LIMIT stays here, because it now
    // bounds a replace's inline Episode checks and attach() is this task's.
    /**
     * Episodes a replace checks inline before it stops; the rest wait for T-094's qori:episodes:check. A count as well as
     * the deadline, because each check is cheap and a Series of forty should not depend on how fast the vendor felt today.
     * Lowered from 20 on 20 September 2026: at T-093's measured 0.85s per files.get, twenty is 17s and the 12s deadline
     * always cut first, so the count was decoration. Twelve is 10.2s, inside the deadline, so the count is what binds.
     */
    public const MANUAL_RETRY_LIMIT = 12;

    /** @param iterable<GrantsPeerAccess> $providers */
    public function __construct(private iterable $providers, private CurrentGroup $current, private ConnectionService $connections) {}

    /**
     * The one grant path (D-040). Called by T-089's Open for the Episode being opened, and by nothing else: it finds or
     * creates that Episode's row — its container's row on a Container provider, its own on an Item provider — and attempts
     * it, verifying a granted row older than RECHECK_MINUTES before trusting it. One target, one call. Idempotent; skips an
     * inactive Access; catches every Throwable; never throws. $deadline is the request's remaining budget (F08).
     */
    public function ensureOpen(Access $access, Episode $episode, int $deadlineSeconds = self::REQUEST_DEADLINE_SECONDS): ?VendorGrant;
    /**
     * Best effort, one inline try inside the caller's deadline; a failure sets the row revoke_failed for T-157's list
     * rather than retrying (D-040, F01). Every row of the Access that entitles(), container and item alike — which is how
     * attempting is included without a fourth place enumerating states. A permission another entitling row of the Group
     * still holds on the same (provider, external_target_id, principal) is not called for at all (F02, D-041).
     */
    public function revokeFor(Access $access, int $deadlineSeconds = self::REQUEST_DEADLINE_SECONDS): void;
    /**
     * The same for one Episode's rows. Called by T-094 when a file is changed, and by EpisodeService::remove() and
     * SeriesService::purge() above their delete, so the attempt is made while the row still points at something (D-036, F01).
     */
    public function revokeItem(Episode $episode, int $deadlineSeconds = self::REQUEST_DEADLINE_SECONDS): void;
    // retryRemoval(), retryNeedingCreator() and impactOf() are T-157's: they serve the creator's surfaces alone.
    /** The providers a Series needs an identity for: every container's, plus the connection() of every Episode whose provider grants on an item (F03). T-092's neededFor() reads this. @return list<ConnectionProvider> */
    public function providersNeededBy(Series $series): array;
    /**
     * @param array<string, mixed> $settings — checkContainer first, which sets checked_at and fills url when the caller
     * passed none; refuses a container another Series holds (errors.container.in_use); replaces an existing container for
     * the provider. It writes no grant row of any kind and makes no grant call (D-040): the first Open creates the row.
     * Replace: the old row's entitling rows are left revokable, its revoke_failed rows are left alone and its others set revoked; then,
     * once the write has committed and outside the container lock, checkEpisode() on the first MANUAL_RETRY_LIMIT Episodes of
     * the Series whose provider->connection() is this provider, in the Series' order, with REQUEST_TIMEOUT_SECONDS; the rest
     * wait for T-094's qori:episodes:check. It reads that Episode list directly rather than through impactOf(), which moved to
     * T-157 on 20 September 2026: a task cannot call a method belonging to the task that depends on it, and what attach() needs
     * here is a query, not a Data shape a dialog is built from.
     */
    public function attach(Series $series, ConnectionProvider $provider, string $externalId, ?string $url = null, array $settings = []): SeriesContainer;
    /**
     * ResumeGrantsAfterReconnect calls this on T-044's ConnectionReconnected; it runs inside runFor($connection->group), since
     * T-044's landing has no Group current. Same account: needs_creator rows of the provider go pending, due now, and revokable
     * rows that failed with connection_unusable get attempts 0, due now. Different: its containers go repick, their non-granted
     * rows needs_creator with ERROR_CONTAINER_REPICK, and Log::info names the connection, $previousExternalId and the containers.
     * Sets values and increments none, so a second call for one event changes nothing.
     */
    public function reconnected(Connection $connection, bool $sameAccount, ?string $previousExternalId = null): void;
    // checkNow() is gone: see the Decisions. Open is the one way in, and PEER_CHECK_SECONDS went with it.
    /** Whether a grant-providers integration is bound for $provider->connection(); false when that is null. T-094's EpisodeCheckController asks it before its container arm. */
    public function handles(EpisodeProvider $provider): bool;
    /**
     * One Episode's item check, in the current Group, for a replace, T-094's checkItems() and Check now. No grant provider
     * for the Episode's provider: nothing written, Unreadable. No usable connection: nothing written, NeedsCreator.
     * It then branches on grantsOn(), which F10 says this contract did not and had to (20 September 2026): written for a
     * container, it asked every provider for an insideContainer truth that an item provider sets null, so an item Episode
     * that plainly exists came out neither Clear nor Flagged.
     *   Container provider — no container for it on the Series, or one marked repick: nothing written, NeedsCreator. A
     *   container marked missing: content missing_since kept, or now, no call, Flagged. Else, through freshConnectionFor(),
     *   re-reads the container through checkContainer() unless its checked_at is under RECHECK_MINUTES old (exists →
     *   checked_at now; exists false → status missing, content missing_since kept, or now, Flagged, and stop), then
     *   checkItem(): exists and insideContainer → content checked_at now, missing_since null, Clear; exists false or
     *   insideContainer false → content missing_since kept, or now, Flagged.
     *   Item provider — no container is expected and none is read. checkItem() alone, and insideContainer is null and
     *   ignored: exists → checked_at now, missing_since null, Clear; exists false → missing_since kept, or now, Flagged. A ContainerCheck or ItemCheck with ERROR_CONNECTION_UNUSABLE (a 401): the connection
     * marked for reconnect, nothing written, NeedsCreator. Any other errorCode, a token fresh() could not renew, or a Throwable:
     * nothing written, Unreadable. Never throws. attach() and T-094's checkItems() ignore the answer; EpisodeCheckController flashes from it.
     */
    public function checkEpisode(Episode $episode, int $timeoutSeconds): EpisodeCheckOutcome;
    /**
     * Null when the Series has no grant row; else the worst row of either kind: awaiting_identity, awaiting_acceptance,
     * needs_creator, pending, granted. It never answers attempting — that row reads as Pending, because what the Peer
     * should do about it is identical and shared.vendor_notice.reasons.* would otherwise need a key for a distinction
     * drawn for Qori's benefit. Nor revoked or revoke_failed, neither of which blocks an Open.
     */
    public function stateFor(Access $access): ?VendorGrantStatus;
    /**
     * The link for a granted row, for T-089's PlaybackTicketService::open(): resolves the bound integration, passes the
     * kept connections row without fresh() since openLink() makes no call, and answers null when nothing is bound.
     * It exists because providerFor() is private and open() must not take the grant-providers tag as a second iterable
     * of its own — settled on the consolidation pass, 20 September 2026, with the question the draft left open.
     */
    public function openLinkFor(VendorGrant $grant, Episode $episode, int $timeoutSeconds): ?VendorLink;
    /** Null in this task; T-092 reads the person's confirmed identity here. */
    protected function identityFor(User $user, ConnectionProvider $provider): ?GrantIdentity;
    private function providerFor(ConnectionProvider $provider): ?GrantsPeerAccess;
    private function connectionFor(ConnectionProvider $provider): ?Connection;   // Connection::query()->where('provider'), in Group context; the kept row, live or not
    /**
     * Where every vendor call reads its connection: connectionFor(), then, when it isLive(), $this->connections->fresh($connection,
     * $timeoutSeconds), before any container lock is taken. The row as it then stands, or null when the Group has none. The caller
     * reads it: null or ! isLive() → the unusable-connection answer, no call; hasExpired() → no call, pending(ERROR_TOKEN_EXPIRED).
     */
    private function freshConnectionFor(ConnectionProvider $provider, int $timeoutSeconds): ?Connection;
    private function attempt(VendorGrant $grant, User $user, int $timeoutSeconds): void;   // freshConnectionFor(), then grant() inside the target lock; the row carries its target
    private function verify(VendorGrant $grant, int $timeoutSeconds): void;   // freshConnectionFor(), then checkGrant() inside the container lock; a gone permission falls through to attempt(); no usable connection: no call, row untouched
    private function record(VendorGrant $grant, GrantResult $result): void;
}
// The container lock is T-044's: AdvisoryLock::run('container', $provider->value.':'.$externalId, fn () => …), with the
// row's own provider and external_target_id: the container's external_id, the item's id, or the copies kept after a container is gone.
// A vendor 401 (an answer carrying GrantResult::ERROR_CONNECTION_UNUSABLE): $this->connections->markForReconnect($connection, 'unauthorized').
```

`ensureOpen()` reads the Series through `$access->grantedSeries()` and runs
inside `$this->current->runFor($series->group, …)`, as
`PlaybackTicketService::connectionFor()` does
(`app/Services/PlaybackTicketService.php:135`). It resolves **one** target
from the Episode it was given: on a `Container` provider, the Series'
container for `$episode->provider->connection()`, and
`VendorGrant::firstOrCreate` on `(access_id, series_container_id)` with
`target` `container`, `provider` and `external_target_id` copied; on an
`Item` provider, `firstOrCreate` on `(access_id, episode_id)` with `target`
`item`, `provider` from `EpisodeProvider::connection()` and
`external_target_id` from the Episode's stored item id. An Episode with no
item id yet is not granted and answers `ERROR_ITEM_MISSING`. A new row is
written `pending` and attempted in the same call; a `revoked` row is treated
as `pending` (a restored Peer is the same Peer); a `revoke_failed` row is
left alone, because something is still out there and the creator owns it.
`principal` is written from the identity the attempt used (`F04`), and a row
whose `principal` no longer matches the confirmed identity is not reused: it
is queued for revoke and a new row takes its place. Then, by the row's
state:

| Row state                    | Open (`ensureOpen()`), which is the only caller                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------- |
| no row yet                   | create `pending`, commit, then `attempt()`                                                        |
| `pending`, due               | `attempt()`                                                                                       |
| `pending`, not yet due       | nothing; the notice carries the time, at most `BACKOFF_MINUTES`' last value away                  |
| `attempting`                 | `verify()` first, whatever `checked_at` says, and `attempt()` only on a confirmed absence (`F01`) |
| `needs_creator`, due         | `attempt()`                                                                                       |
| `needs_creator`, not yet due | nothing                                                                                           |
| `awaiting_identity`          | nothing — `T-092` prompts                                                                         |
| `awaiting_acceptance`        | `verify()` when `checked_at` is older than `RECHECK_MINUTES`                                      |
| `granted`                    | `verify()` when `checked_at` is older than `RECHECK_MINUTES`, else the link                       |
| `revoked`                    | treated as `pending`: a restored Peer is the same Peer                                            |
| `revoke_failed`              | nothing — `T-157`'s list owns it, and something is still out there                                |

`attempting` is the one state that reads before it looks at `checked_at`,
because there the read **is** the reconciliation and a throttle would leave the
row unreconcilable. It is also the one state expected to leave on the same
Open. The column for Try again now went with it to `T-157` on 20 September
2026; it had been leaving a cell behind on four rows, which read as Try again
now re-verifying `granted` rows.

Before `attempt()`: a container that is `missing` or `repick` → `needs_creator`
with `ERROR_CONTAINER_MISSING` or `ERROR_CONTAINER_REPICK`, no vendor call. An
item row whose Episode no longer carries an item id, or whose Episode is gone,
→ `needs_creator` with `ERROR_ITEM_MISSING`, no vendor call. No
integration bound for the provider → `pending`, `ERROR_NO_INTEGRATION`,
`Log::error`, no vendor call. Then `freshConnectionFor()`: connection missing
or `! isLive()`, before `fresh()` or after it — `T-044`'s `Connection::isLive()`,
which is `isUsable()` (`app/Models/Connection.php:118`) and not marked for
reconnect, so a disconnected provider, one waiting on a reconnect and one whose
refresh just found the token revoked are read alike → `needs_creator`,
`ERROR_CONNECTION_UNUSABLE`, no vendor call; live, but its token still expired
after `fresh()` → `pending`, `ERROR_TOKEN_EXPIRED`, no vendor call. Otherwise
`grant()` is called with the row `fresh()` returned, inside the container lock,
and a `GrantResult` carrying `ERROR_CONNECTION_UNUSABLE` — a 401 — first calls
`$this->connections->markForReconnect($connection, 'unauthorized')`, then is
recorded as any `needs_creator` answer is. Before `verify()`: the same reads,
and a connection missing, not `isLive()` or still expired → nothing, no vendor
call, the row and its `checked_at` as they were; a `checkGrant()` answering
`ERROR_CONNECTION_UNUSABLE` marks the connection the same way and records
nothing. `record()` maps the result:
`granted` sets `vendor_ref`, `join_url`, `granted_at`, `checked_at`, clears
`last_error_code` and `next_attempt_at`; `awaiting_acceptance` sets the status,
`vendor_ref`, `join_url` and `checked_at`; `awaiting_identity` sets the status
and touches nothing else; `pending` sets `last_error_code`, increments
`attempts`, and sets `next_attempt_at` to now plus `retryAfterSeconds` when
given, else `BACKOFF_MINUTES[min(attempts, count) − 1]`; `needs_creator` sets
`last_error_code`, increments `attempts`, and sets `next_attempt_at` to now
plus the last `BACKOFF_MINUTES` value. A `Throwable` from anywhere in the step
is `Log::error`ed with the Access id; one from the integration is also recorded
as `pending(ERROR_UNEXPECTED)` when the row can still be written.

```php
namespace App\Listeners;

/** T-044's reconnect, handed to the grants it held up. Found by event discovery and registered nowhere else, so it runs once. */
class ResumeGrantsAfterReconnect
{
    public function __construct(private VendorAccessService $vendorAccess) {}

    public function handle(ConnectionReconnected $event): void;
    // $this->vendorAccess->reconnected($event->connection, $event->sameAccount, $event->previousExternalId);
}

```

```php
// App\Services\AccessService — the hooks
public function __construct(private CurrentGroup $current, private VendorAccessService $vendorAccess) {}

// grant(), existing branch (:74-88), reshaped so the step runs once the Access is active and before anything is announced.
// The restore block's comment (:75-77) stays above $restored.
if ($existing !== null) {
    $restored = ! $existing->isActive();

    if ($restored) {
        $existing->update(['status' => AccessStatus::Active, 'revoked_at' => null]);
    }

    // No vendor call on either branch under D-040: the Access is written, the email is sent, and the Peer's first
    // Open is what grants. The restore block is left exactly as it stands (:74-88).
    if ($restored) {
        $this->announce($existing, $series, $user, $group);
    }

    return $existing;
}

// grant(), new branch: unchanged — nothing is added between promoteTo() (:101) and announce() (:103)
// revoke(): after the update, the one hook this task adds to AccessService
$this->vendorAccess->revokeFor($access);
```

`revokeFor()` takes every row of the Access whose status `entitles()` —
`granted`, `awaiting_acceptance` or `attempting` — and tries each once inside
the caller's deadline; `revokeItem()` does
the same for one Episode's rows across every active Access. Before each call,
under the target lock, it counts the Group's other rows that `entitles()`
on the same `(provider, external_target_id, principal)`:
if any remain, the permission belongs to an entitlement that is still live, so the
row is set `revoked` with `revoked_at` and **no vendor call is made** (`F02`,
`D-041`),
and `Log::info` names the rows that held it. Otherwise the vendor is called —
and an `attempting` row, which has no `vendor_ref` to call against, is read
with `checkGrant()` first so the revoke goes out against what that found.
Success sets `revoked` and `revoked_at`; **failure sets `revoke_failed`**,
keeps every column the retry will need, logs a warning with the grant id, and
puts the row on `T-157`'s list (`D-040`). Nothing retries it on its own.
Where the deadline runs out before a row is reached, that row is
`revoke_failed` with `ERROR_TIMEOUT` and nothing was called, which is the
honest record: Qori does not know whether it would have worked. A revoke try
reads its connection through `freshConnectionFor()`, as `attempt()` does; a
connection missing or unusable makes no call and is `revoke_failed` with
`connection_unusable`, and so is a `RevokeResult::failed()` carrying
`ERROR_CONNECTION_UNUSABLE` — a 401, which also marks the connection for
reconnect. `reconnected(sameAccount: true)` retries those rows once.

`SharedController::show()` takes `VendorAccessService` by constructor, calls
**no vendor method at all** (`D-040`) — it reads the rows that exist — and
adds one prop:
`'vendor' => null` when `stateFor()` is null or `granted`, else, every string
through `$terminology->line(…, …, $access->group)`:

```php
[
    'state' => $state->value,
    'provider' => $grant->provider->value,       // the row's own provider, never a container's (F10); T-096 and T-098 pick their own panel by it
    'url' => $grant->container?->url,             // a container's vendor page where there is one, null on an item grant (F10)
    'title' => 'shared.vendor_notice.title',
    'message' => 'shared.vendor_notice.reasons.'.$state->value,   // ['creator' => $access->group?->name]
    // No next-attempt keys: D-040 left nothing to schedule, so there is no next try to name and the four
    // shared.vendor_notice.next_attempt.* lines are gone with the sweep that was going to make them true.
    'openDisabled' => 'shared.vendor_notice.open_disabled',
    // Episodes whose provider->connection() has a grant row on this Access that is not granted, read from the
    // Access' rows once rather than a lookup per Episode.
    'episodeIds' => ['01J…'],
]
```

`Show.vue` renders an `InlineNotice` with `id="access"` (tone `info` for
`pending`, `warning` otherwise) above the Episode list when `vendor` is set,
beside the deletion notice (`resources/js/pages/shared/Show.vue:185-193`): the
title and the message, and no button of its own. There is no countdown and
no `setTimeout`: `D-040` left nothing running in the background to count down
to, and the one action that changes anything is the Episode's own Open
control. Every Episode in `episodeIds` renders `T-089`'s
Open control disabled, with `openDisabled` beside it. While `T-092`'s identity
prompt shows, the prompt stands in for this notice and carries `id="access"`
instead, so one element holds the id; `vendor` is still sent, so `episodeIds`
keeps those Open controls disabled (`T-092`).

`PlaybackTicketService::open()` (`T-089`'s method; the branch for an Episode
that is not Qori-hosted) takes `VendorAccessService` by constructor and, after
`admit()`, calls `ensureOpen($access, $episode)` — the one grant path there
is (`D-040`), which finds or creates that Episode's row, attempts it and
verifies a stale `granted` one, all inside the request's deadline. When the
row it answers is not `granted`, `open()` returns
`VendorLink::blocked($state->value, $episode->provider)` and `T-089`'s
controller redirects to `route('shared.show', $seriesId).'#access'` with the
toast `shared.vendor_notice.redirected` (`D-020`); when it is `granted`, it
returns `$this->vendorAccess->openLinkFor($grant, $episode, REQUEST_TIMEOUT_SECONDS)`,
which passes the kept `connections` row even when it is unusable (a disconnected
provider, above), with no `fresh()`, since `openLink()` makes no call; when no
`grant-providers` integration is bound for the provider —
`handles($episode->provider)` false, or `openLinkFor()` answering null —
`T-089`'s `fromMediaLink()` branch stays.

**`openLinkFor()` is the answer to the question this draft left open**, and it
was settled on the consolidation pass of 20 September 2026: `open()` was
written as calling `providerFor(...)->openLink(…)`, which cannot compile,
because `providerFor()` is private to `VendorAccessService` and no such method
exists anywhere else. Of the two ways out — a public method here, or handing
the `grant-providers` tag to `PlaybackTicketService` as well — the first wins
on the rule the rest of this task follows: the tagged iterable is resolved in
one class, `handles()` is already public for exactly this reason, and a second
holder of the tag is a second place to keep the binding right.

**Everything the creator sees is `T-157`'s**, and no controller prop of its is
specified here: `IntegrationsController::show()`'s two lists and their copy,
its `retry()` and `retryRemoval()` actions, `SeriesController`'s
`containerImpact` prop and its Peer-list marker, and `ContainerChangeDialog.vue`.
They were written out in full in this section until 20 September 2026, when the
cut moved them and the prose stayed — one paragraph of it ending "This task
builds the dialog and renders it nowhere". `ContainerChangeImpact` is still
declared here so those tasks share one class rather than three, and nothing in
this task constructs one.

## Copy

| Key                                                | File                 | English                                                                                                                                                                             |
| -------------------------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `shared.vendor_notice.title`                       | `lang/en/shared.php` | Before this :series opens                                                                                                                                                           |
| `shared.vendor_notice.reasons.pending`             | `lang/en/shared.php` | :creator's account didn't let you in that time. Open it again and Qori tries once more.                                                                                             |
| `shared.vendor_notice.reasons.needs_creator`       | `lang/en/shared.php` | :creator's account couldn't let you in. Qori has told :creator what needs to change on their side. Nothing more is needed from you, and this :series opens once they've changed it. |
| `shared.vendor_notice.reasons.awaiting_identity`   | `lang/en/shared.php` | This :series opens on another site, and Qori doesn't know yet which of your accounts to let in. Confirm it, and Qori lets you in.                                                   |
| `shared.vendor_notice.reasons.awaiting_acceptance` | `lang/en/shared.php` | The site this :series lives on has an invitation waiting for you. Accept it there, then open this :episode again.                                                                   |
| `shared.vendor_notice.open_disabled`               | `lang/en/shared.php` | Not open yet. The note above says why.                                                                                                                                              |
| `errors.container.in_use.message`                  | `lang/en/errors.php` | That already holds another :series.                                                                                                                                                 |
| `errors.container.in_use.resolution`               | `lang/en/errors.php` | Each :series needs its own folder or meeting. Pick one nothing else uses.                                                                                                           |

`shared.vendor_notice.reasons.awaiting_identity` is replaced on the page by
`T-092`'s prompt; it exists so every state renders a sentence.
`shared.vendor_notice.redirected`, the toast on a blocked Open, is `T-089`'s
key. A provider with a vendor step of its own for `awaiting_acceptance` —
`T-096`'s Join panel, `T-098`'s invitation line — renders it beside the notice
in a new tab, and decides whether its own sentence replaces this
one. Provider tasks add `connections.grants.reasons.<vendor slug>` lines for
the codes they observe, into `T-157`'s lists rather than this table.

Three placeholders are used above and no others: `:series` and `:episode` are
the Group's nouns through `Terminology`, and `:creator` is the Group's name,
as `accesses.consent.peer` uses it. **No line here names a vendor**, which is
`D-035` rather than an omission — the owner has confirmed Stripe and nothing
else, and a Peer being told a file lives on Google Drive learns something
about Qori's stack rather than about what to do next. The prop carries
`provider` so `T-096` and `T-098` can pick their own panel by it, and the
sentence stays vendor-neutral.

Nothing here is pluralised and nothing carries a time: no `Terminology::choice()`,
no `{0}`/`{1}`/`[2,*]` branches, no `:time`, `:date` or `:seconds`. The prose
explaining all four survived the cut of 20 September 2026 without a single key
left that used them — the counted sentences went to `T-157` with the impact
dialog, and the times went with the sweep (`D-040`), which is what there used
to be to count down to.

## Routes

None. `shared.access.check` went with `checkNow()` on 20 September 2026 and
`share.settings.integrations.retry` and `.retry-removal` went to `T-157` with
the surfaces that post to them, so this task registers no route at all: every
path into it is a method another task's controller calls.

Open is `T-089`'s `shared.episodes.open`; the Integrations page is
`share.settings.integrations`; the creator's Series page is
`share.series.show` (`routes/share/series.php:25`). Flows: this route is
written into `docs/flows/vendor-access.md` with the ensure step.

## Tests

Every case binds the fake with
`$this->app->when(VendorAccessService::class)->needs('$providers')->give(fn () => [$this->fake])`
and calls `Http::fake()`; the fake makes no HTTP call and records each call
with the timeout it was given, and the connection it was handed. `T-044`'s
`ConnectionService` is the real one except in case 61; a factory connection
carries no `expires_at`, so its `fresh()` renews nothing and calls no vendor.

**New: `tests/Feature/Access/VendorAccessTest.php` — 31 cases**

1. `test_it_records_nothing_for_a_series_with_no_container`
2. `test_a_new_access_writes_no_grant_row_and_calls_no_vendor` — `AccessService::grant()` on a Series with a container and three item Episodes: zero rows, zero calls (`D-040`).
3. `test_the_access_email_is_sent_with_no_vendor_call` — `Notification::fake()`; the notification was sent and the fake saw nothing.
4. `test_a_restored_access_calls_no_vendor_either` — the existing-access branch, a `revoked` row left as it is, zero calls; the Peer's next Open is what grants.
5. `test_a_replayed_grant_calls_no_vendor` — the shape `T-102`'s replay takes: the second `grant()` returns the Access and makes no call.
6. `test_a_vendor_exception_never_reaches_the_caller` — the fake throws; `grant()` returns the Access; row `pending`, `unexpected`.
7. `test_a_failed_row_write_never_reaches_the_caller` — `VendorGrant::saving()` throws inside `ensureOpen()`; Open answers blocked rather than erroring; no row; the next Open creates and grants it.
8. `test_a_web_request_passes_the_short_timeout` — the fake received `REQUEST_TIMEOUT_SECONDS`.
9. `test_a_timeout_stays_pending` — `pending(ERROR_TIMEOUT)`; row `pending`; `stateFor()` is `Pending`.
10. `test_a_transient_refusal_sets_the_backoff_and_counts_the_attempt` — `BACKOFF_MINUTES` is `[0, 1, 2, 5, 15]`, so the first failure leaves `next_attempt_at` due at once, the second ≈ +1 minute and the third ≈ +2; `attempts` counts each. The first value being zero is the point: a person pressing Open again is not a loop to back off from.
11. `test_a_retry_after_replaces_the_backoff` — `retryAfterSeconds` 3600 → ≈ +1 hour, over a backoff of zero.
12. `test_nothing_is_attempted_before_next_attempt_at` — a row already at its third failure, so `next_attempt_at` is two minutes out: `ensureOpen()` makes no call and answers the pending row with its time. (A row at its _first_ failure is due at once, which case 10 covers and which is the behaviour, not a bug.)
13. `test_an_unusable_connection_needs_the_creator_without_a_vendor_call` — revoked connection; `needs_creator`, `connection_unusable`; zero calls; `next_attempt_at` ≈ +15 minutes, `BACKOFF_MINUTES`' last value; the same for a connection `T-044` has marked for reconnect but not revoked, which `isUsable()` alone would pass.
14. `test_a_provider_needing_an_identity_waits_for_it` — `awaitingIdentity()`; `attempts` 0; not `due()`.
15. `test_an_accepted_invitation_is_not_yet_granted` — `awaitingAcceptance()`; row `awaiting_acceptance` with `vendor_ref`; `isGranted()` false.
16. `test_a_recheck_promotes_an_accepted_invitation` — an `awaiting_acceptance` row with an old `checked_at`; `checkGrant()` answers `granted`; row `granted`, `checked_at` now.
17. `test_open_rechecks_a_granted_row_and_regrants_a_lost_permission` — `ensureOpen()` on a row checked longer than `RECHECK_MINUTES` ago; `checkGrant()` answers `pending(ERROR_PERMISSION_GONE)`; `grant()` is called again and the row ends `granted`; a fresh `checked_at` makes no call.
18. `test_it_takes_the_container_lock_around_the_vendor_call` — `DB::listen` sees `pg_advisory_xact_lock` with the bindings `container` and `dropbox:` followed by the container's `external_id`, `T-044`'s `AdvisoryLock::run()` statement, before the call.
19. `test_reconnecting_the_same_account_retries_at_once` — `reconnected($connection, sameAccount: true)`; `needs_creator` rows are `pending` with `next_attempt_at` null; the next `ensureOpen()` grants; a `revoke_failed` row is retried once in the same call.
20. `test_connecting_a_different_account_marks_containers_for_a_new_pick` — `reconnected($connection, sameAccount: false)`; containers `repick`; pending rows `needs_creator`, `container_repick`; granted rows untouched; no vendor call.
21. `test_revoking_an_access_revokes_the_grant_and_keeps_the_row`
22. `test_a_failed_revoke_becomes_revoke_failed_for_the_creators_list` — the fake refuses; the row is `revoke_failed`, keeps `vendor_ref`, `principal` and `external_target_id`, a warning is logged, and nothing retries it (`D-040`, `F01`).
23. `test_attaching_a_container_writes_no_rows_and_calls_nothing` — three active Accesses; `attach()` writes **zero** grant rows and makes zero grant calls (`D-040`); `checkContainer` called once. The first Open on an Episode is what creates a row.
24. `test_attaching_refuses_a_container_another_series_holds_and_replaces_its_own` — a second Series with the same `external_id` throws `errors.container.in_use`; the same Series with a new `external_id` deletes the old row, leaves its granted rows `revokable()`, sets its `needs_creator` row `revoked` with `revoked_at`, leaves its `revoke_failed` row alone, and writes no row at all on the new one.
25. ~~`test_check_now_rechecks_accepted_and_granted_rows_inside_the_recheck_window`~~ — **retired 20 September 2026** with `checkNow()`. What it guarded, that a re-check does not create rows, is now true by construction: only `ensureOpen()` writes one.
26. `test_open_attempts_a_due_row_and_leaves_the_others_alone` — a `pending` row not yet due and an `awaiting_identity` row: no call; a due `needs_creator` row: one `grant()` call. (Was `test_check_now_attempts_only_due_rows`; the one retry rule outlived the button that used to exercise it, and Open exercises it now.)
27. ~~`test_retrying_rows_needing_the_creator_stops_at_the_limit_and_leaves_the_rest_due`~~ — **retired in place 20 September 2026**: Try again now, `retryNeedingCreator()`, `GrantRetryTally` and `MANUAL_RETRY_SECONDS` all went to `T-157` in that day's cut, and the case goes with them. `MANUAL_RETRY_LIMIT` stays here because it still bounds a replace's inline Episode checks, which case 32 covers.
28. ~~`test_impact_counts_active_peers_and_lists_the_episodes_on_the_containers_provider`~~ — **retired in place 20 September 2026**: `impactOf()` went to `T-157` and the Zoom half of this case to `T-100` with `kind()`'s `meeting` arm. Nothing in this task constructs a `ContainerChangeImpact`, so there is nothing here to assert about one.
29. `test_checking_an_episode_flags_a_file_outside_the_container_and_clears_it_again` — `checkItem()` answers `insideContainer` false: `content.missing_since` set and `Flagged` returned, and the same `missing_since` kept on a second such answer; then `exists` and inside: `missing_since` null, `checked_at` now, `Clear` returned.
30. `test_a_failed_item_read_records_nothing_and_answers_unreadable` — an Episode already carrying `missing_since`; an `ItemCheck` with `errorCode` `timeout`, then a thrown exception: `content` unchanged each time, the earlier `missing_since` kept, `Unreadable` returned, nothing reaches the caller; then a revoked connection, and a container marked `repick`: no call, `content` unchanged, `NeedsCreator` returned.
31. `test_checking_an_episode_whose_container_is_gone_flags_it_without_reading_the_file` — the container's `checked_at` older than `RECHECK_MINUTES`; `checkContainer()` answers `exists` false with no `errorCode`: container `missing`, `content.missing_since` set, `Flagged`, no `checkItem()` call; a second Episode on the now `missing` container: `missing_since` set, `Flagged`, zero calls.
32. `test_replacing_a_container_checks_the_affected_episodes_up_to_the_limit` — a Series with two Dropbox Episodes and a Qori-hosted one; `attach()` with a new `external_id`: `checkItem()` twice, with `REQUEST_TIMEOUT_SECONDS`, after the new container row is committed; `checkContainer()` once, `attach()`'s own; the Episode the fake reports outside has `missing_since` set when `attach()` returns. Then a Series with `MANUAL_RETRY_LIMIT` + 1 Dropbox Episodes: `checkItem()` `MANUAL_RETRY_LIMIT` times, in the Series' order, and the last Episode's `content` untouched.
33. `test_a_disconnected_provider_calls_nothing_and_leaves_people_already_let_in_alone` — revoked connection; a `granted` row checked longer than `RECHECK_MINUTES` ago and an `awaiting_acceptance` row: `ensureOpen()` makes no call and changes neither row; `PlaybackTicketService::open()` for the granted Peer returns the fake's `openLink()`.
34. `test_a_revoke_while_disconnected_is_listed_and_runs_on_reconnect` — revoked connection; `revokeFor()` makes no call and leaves the row `revoke_failed` with `connection_unusable`, on the creator's list; `reconnected(sameAccount: true)` retries it once and it is `revoked` (`D-039`, `D-040`).

**New: `tests/Feature/Shared/VendorStateTest.php` — 6 cases**

35. `test_the_series_page_sends_no_vendor_prop_without_a_container`
36. `test_the_series_page_calls_no_vendor` — a due `pending` row is still `pending` after the GET and the fake saw nothing (`D-040`); the prop carries its state.
37. `test_the_series_page_says_who_resolves_a_stalled_grant` — the fake answers `needsCreator()`; 200; state `needs_creator`; message is `shared.vendor_notice.reasons.needs_creator`; the prop carries no next-attempt key and no button key at all. (The `checkable` prop it used to assert went with `checkNow()` on 20 September 2026; the notice has no control of its own.)
38. `test_open_lands_on_the_series_notice_while_a_grant_is_pending` — GET `shared.episodes.open`; a redirect to `route('shared.show', $seriesId).'#access'`; toast `shared.vendor_notice.redirected`; names from `T-089`.
39. `test_the_paid_path_records_a_granted_fulfilment_and_calls_no_vendor` — `CheckoutService::fulfil()` on a Series with a container and three item Episodes: `payment_fulfilments.status` `granted`, **zero grant rows and zero vendor calls**, and a fake rigged to throw is never reached (`D-040`). It is the paid-path guarantee, and `D-040` made it a stronger one: fulfilment cannot be refused by a vendor that is never asked.
40. ~~`test_the_series_page_says_when_a_pending_grant_is_tried_next`~~ — **retired 20 September 2026 (`D-040`)**, with the four `shared.vendor_notice.next_attempt.*` lines it asserted. Nothing tries on its own any more, so there is no next try to name and no timezone rendering to check. The number is kept rather than reused, because other drafts cite the numbering of this file. What survives of its intent is case 41: `next_attempt_at` still gates whether Open attempts, and a row inside its backoff still disables Open.
41. `test_the_series_page_disables_open_only_where_pressing_it_cannot_help` — an Episode with no row and one with a due `pending` row keep a live Open; `awaiting_identity`, `needs_creator` and a `pending` row not yet due are disabled with `shared.vendor_notice.open_disabled`; with the row `granted`, `vendor` is null (`D-040`).

**Retired: `tests/Feature/Shared/AccessCheckTest.php` — cases 42 to 45.**
Gone with `checkNow()` on 20 September 2026, along with case 25. All four
tested a button that no longer exists; nothing they asserted is true of
another path, because Open creates and grants where Check again only looked.
The numbers are not reused.

**New, continued: `tests/Feature/Access/VendorAccessTest.php` — 4 cases**

Numbered after case 60, so the numbers other drafts cite stay put.

61. `test_an_expiring_token_is_refreshed_before_the_grant_call` — a Dropbox connection whose `expires_at` falls inside `T-044`'s `ConnectionService::REFRESH_MARGIN_MINUTES`, and `ConnectionService` replaced with `$this->mock()`: `fresh()` is called once, with that connection and `REQUEST_TIMEOUT_SECONDS`, and the fake's `grant()` receives the row it returned, with a new `access_token` and `expires_at` an hour ahead; row `granted`. Then `fresh()` answering the row with its token still expired, as a refresh that timed out leaves it: no `grant()` call; row `pending`, `token_expired`.
62. `test_a_vendor_401_marks_the_connection_for_reconnect_and_waits_on_the_creator` — the fake's `grant()` answers `needsCreator(ERROR_CONNECTION_UNUSABLE)`, as an integration answers a 401: the connection's `reconnect_required_at` is set and its `reconnect_reason` is `unauthorized` (`T-044`'s columns); row `needs_creator`, `connection_unusable`; once the row is due, `ensureOpen()` makes no call. In a second Group, a `granted` row checked longer than `RECHECK_MINUTES` ago whose `checkGrant()` answers the same: that connection is marked the same way and the row stays `granted` with its `checked_at`.
63. `test_the_reconnect_event_moves_rows_waiting_on_the_creator_to_pending` — `event(new ConnectionReconnected($connection, true, null))` with no Group current, as `T-044`'s landing under `/u` dispatches it: the Group's `needs_creator` Dropbox rows are `pending` with `next_attempt_at` null, through `ResumeGrantsAfterReconnect`; a `needs_creator` row in another Group is untouched.
64. `test_it_says_which_episode_providers_have_a_grant_provider` — `handles()` is true for `EpisodeProvider::Dropbox`, which the fake answers for, and false for `Vimeo`, whose connection has no grant provider bound, and for `CloudflareR2`, which has no connection.

**New, continued: `tests/Feature/Access/VendorAccessTest.php` — 11 cases on an item provider (`D-036` and the review)**

The fake is built with `grantsOn()` answering `GrantTarget::Item` for these,
as `T-092` builds it for another provider; no Series container exists in any
of them.

65. `test_each_episode_opened_gets_its_own_item_row` — a Series with three Episodes on the item provider and one Qori-hosted; Open on each of the three in turn: three rows, each `target` `item` with its own Episode and that Episode's item id in `external_target_id`, all `granted`; three calls, each with the row whose Episode it was for; the Qori-hosted Episode is never granted and has no row. (Was `test_it_grants_a_new_access_on_every_episodes_item`, which fanned out at `AccessService::grant()` — the eager world `D-040` deleted, and directly against case 2. What it was really guarding is the row shape per Episode, which survives the change of trigger.)
66. `test_open_grants_one_item_and_touches_no_other_episode` — a Series of twenty item Episodes, Open on the fourteenth: exactly one call, one row, and the other nineteen Episodes have no row at all (`D-040`).
67. `test_open_grants_the_episode_it_is_opening_in_the_same_request` — no row beforehand: `ensureOpen()` creates it, grants it, and `PlaybackTicketService::open()` answers the fake's `openLink()` in that request.
68. `test_adding_an_episode_writes_no_rows_for_anybody` — a Series with three active Accesses and one revoked gains an Episode on the item provider: **zero** rows and zero calls, and the same after a second save (`D-040`). Then one Peer opens it: exactly one row, theirs. (Was `test_a_new_episode_pends_a_row_for_every_peer_and_calls_nothing`, which called `ensureItem()` — gone with the eager model. The guarantee worth keeping is that adding an Episode costs a Series of three hundred Peers nothing.)
69. `test_changing_an_episodes_file_revokes_the_readers_of_the_old_item` — `revokeItem()`: each granted row tried once, `revoked` with `revoked_at`; the rows the deadline did not reach are `revoke_failed` with `ERROR_TIMEOUT` and on the creator's list.
70. `test_a_different_account_leaves_item_grants_for_the_creator_to_pick_again` — `reconnected($connection, sameAccount: false)` with no container: the item rows are `needs_creator` with `ERROR_ITEM_REPICK` and granted rows are left alone. What lists them, and the `connections.grants.reasons.item_repick` sentence it reads, is `T-157`'s.
71. `test_a_permission_two_purchases_share_is_not_revoked_by_either_alone` — one file, two Series, one Peer with an Access on each and the same `principal`; revoking the first sets its row `revoked`, makes **no** vendor call, and logs the row that still holds it; revoking the second calls the vendor once (`F02`).
72. `test_the_principal_granted_is_stored_and_a_changed_identity_is_not_reused` — the row carries the address the fake was given; after the Peer confirms a different account, the old row is queued for revoke and a new row is written for the new principal rather than the old one being overwritten (`F04`).
73. `test_a_grant_row_survives_its_episode_being_deleted` — a `granted` item row whose Episode is deleted: `revokeItem()` runs first, and a row whose revoke failed is still there afterwards with its `vendor_ref` and `external_target_id`, `episode_id` null (`F01`).
74. `test_the_request_deadline_bounds_the_whole_of_one_open` — the fake sleeps to the per-call budget on each call; `ensureOpen()` returns within `REQUEST_DEADLINE_SECONDS` and the step it could not reach left its row untouched (`F08`).
75. `test_providers_needed_by_reads_items_as_well_as_containers` — a Series with no container and two Drive Episodes answers `[GoogleDrive]`, where the container-only reading answered `[]` (`F03`).

**New, continued: `tests/Feature/Access/VendorAccessTest.php` — 4 cases on
the split `pending` and the deadline (`F01`, `F08`)**

Numbered from 78, because `T-157` took 76 and 77.

78. `test_a_row_is_written_and_committed_before_the_vendor_is_called` — the fake's `grant()` asserts, when it is called, that a `vendor_grants` row for that Access and target already exists and reads `attempting`; after it answers, the row is `granted`. With the fake throwing instead, the row is still there afterwards with its `principal` and `external_target_id`, which is the revocation intent `F01` asks for.
79. `test_a_lost_create_is_reconciled_rather_than_sent_twice` — a row left `attempting` by an earlier request: the next `ensureOpen()` calls `checkGrant()` first and makes no second `grant()` call when it answers `granted`; when `checkGrant()` answers `pending(ERROR_PERMISSION_GONE)` it does call `grant()` once. The vendor never receives two creates for one target and principal (`F01`, `D-041`).
80. `test_the_lock_wait_is_the_remaining_budget_and_a_busy_lock_changes_nothing` — `AdvisoryLock` held by another transaction: `ensureOpen()` returns inside `REQUEST_DEADLINE_SECONDS`, the fake saw no call, and the row is exactly as it was found. The wait passed is what was left of the deadline, never `AdvisoryLock::WAIT_SECONDS` when less remains (`F08`).
81. `test_an_attempting_row_is_a_live_entitlement_and_is_revoked_like_one` — added 20 September 2026, for the hole the read-through found. One target and principal, two Accesses: row A `attempting`, row B `granted`. Revoking B makes **no** vendor call and logs A as still holding it (`entitles()` counts `attempting`, `D-041`). Then revoking A, the last one: because it has no `vendor_ref`, `checkGrant()` is called first and finds the permission by `external_target_id` and `principal`, and the revoke goes out against what it found. Last, a `revoke_failed` row beside a `granted` one on the same triple does **not** block that row's revoke, because its entitlement has ended and only its removal failed.

Total: 56, counted rather than stated.

Every stated total in this section has been wrong at least once, which is why
each is now recounted from the numbered cases rather than adjusted. Before the
cut of 20 September 2026: `VendorAccessTest` said 38 and numbered 34, the
item-provider block said 6 and numbered 11 (`D-036` added six, the review's
`F01`, `F02`, `F04`, `F08` and `F03` cases took it to eleven, and the heading
was never touched), and `IntegrationsGrantsTest` said 8 and numbered 6. After
the cut and before the consolidation, the Files table said 44 and 7 where the
sections numbered 51 and 6, and the split bullet said 59. `PROCESS.md` asks
for a total because a reviewer counts them; a total nobody has counted is
worse than none.

The numbers run 1 to 81 with 42 to 60 absent and 76 and 77 belonging to
`T-157`, and none will be reused. 42 to
45 went with `checkNow()`; 46 to 51 went with the sweep (`D-040`); 52 to 59
went to `T-157`; 60 went to `T-100`. Cases 25, 27, 28 and 40 are retired in
place — 25 and 40 with `checkNow()` and the sweep, 27 and 28 on the
consolidation pass, with Try again now and `impactOf()`. Case 81 is the only
one added since the cut. Other drafts cite these numbers, which is why the
gaps stay.

**Changed:** none expected. `AccessService`, `PlaybackTicketService`,
`SharedController`, `EpisodeService` and `SeriesService` gain constructor
dependencies the container resolves, as
`VendorAccessService` gains `T-044`'s `ConnectionService`; no test constructs
them by hand. `T-156`'s own cases over `EpisodeService::remove()` and
`SeriesService::purge()` land first and assert objects and rows, not grants,
so the revoke line added above each delete leaves them passing — confirm
rather than assume. `T-044`'s tests that
dispatch `ConnectionReconnected` without `Event::fake()` now run the listener,
which finds no grant rows there and changes nothing. `ConsoleAccessTest`'s
allow-list and `ArchitectureTest` are untouched.

## Acceptance

- [ ] A new, restored or replayed access writes no grant row and calls no
      vendor at all; the Peer's first Open on an Episode creates that row and
      attempts it in the same request, within `REQUEST_DEADLINE_SECONDS` for
      the whole of it, and a vendor failure of any kind is a row in one of
      the eight states, never an exception to the caller (`D-040`)
- [ ] Every vendor call renews an expiring token through `T-044`'s
      `ConnectionService::fresh()` first, and a vendor 401 marks the connection
      for reconnect and leaves the grant being attempted `needs_creator`
- [ ] The Series page calls no vendor; Open retries a due row and re-checks
      an accepted or granted one. While a row is not `granted` the Series
      page shows the sentence for its state at `#access`, naming who
      resolves it, and Open stays live wherever pressing it can help —
      disabled only for `awaiting_identity`, `needs_creator` and a row not
      yet due — with an Open that gets through landing there with a toast:
      never a refusal, never a page of its own (`D-020`, `D-040`)
- [ ] A `pending` notice names no next try, because nothing tries on its
      own (`D-040`), and offers no button of its own: Open is the whole of
      the Peer's mechanism, and an `awaiting_acceptance` notice sends them
      to the vendor and back to the same Open control (`D-020`)
- [ ] A replace checks up to `MANUAL_RETRY_LIMIT` affected Episodes before
      the response and leaves the rest to `qori:episodes:check` (`D-021`).
      Try again now and the impact dialog are `T-157`'s
- [ ] `checkEpisode()` answers `Clear`, `Flagged`, `NeedsCreator` or
      `Unreadable`; `Flagged` leaves `missing_since` on the Episode, and the
      other two write nothing and keep any earlier flag
- [ ] While a provider is disconnected no vendor is called, people already
      let in keep opening, and a Peer removed meanwhile sits on `T-157`'s
      unresolved list until the same account reconnects (`D-039`)
- [ ] Nothing in this task is scheduled, and no vendor call happens except
      in a request somebody is waiting on (`D-040`)
- [ ] A revoke is tried once inline; a failure is `revoke_failed` with every
      column its retry needs, survives its Episode being deleted (`F01`), and
      is left for `T-157`'s list to show and retry. A permission another
      live entitlement still holds is released locally and never called for,
      keyed by account, target and principal under the same lock (`F02`,
      `D-041`)
- [ ] `VendorGrantStatus::entitles()` is the one answer to "is somebody owed
      this permission", and `scopeRevokable()`, `revokeFor()` and `D-041`'s
      count all read it rather than listing states of their own — so an
      `attempting` row is revoked on refund like any other and can never be
      overlooked by the count, and a `revoke_failed` row never blocks
      somebody else's revoke (`F01`, `D-041`)
- [ ] An `attempting` row is reconcilable: `checkGrant()` finds the
      permission by `external_target_id` and `principal` when the row has no
      `vendor_ref`, which is every row in that state (`F01`)
- [ ] A grant row is written and committed before the vendor is called, so a
      crash between the two leaves `pending` for the next Open to send and a
      lost response leaves `attempting` for it to reconcile — never a row
      that cannot tell those apart, and never a second create for a target
      and principal the vendor may already hold (`F01`, `D-041`)
- [ ] One request spends one deadline across lock, renewal, read and create;
      a step with too little left does not run and leaves its row untouched,
      and a lock that was not taken is answered by `AdvisoryLock::run()`
      returning `false` rather than assumed (`F08`)
- [ ] `checkEpisode()` branches on `grantsOn()`: an item provider is never
      asked for a container, and an item that exists answers `Clear` (`F10`)
- [ ] Each row stores the `principal` it was granted to, and a confirmed
      identity that no longer matches it queues the old permission for revoke
      rather than overwriting the row (`F04`)
- [ ] `providersNeededBy()` answers from containers and item Episodes alike,
      so a Series with only item Episodes still asks its buyer for the
      identity it needs (`F03`)
- [ ] `T-044`'s `ConnectionReconnected` reaches `reconnected()` through
      `ResumeGrantsAfterReconnect`: reconnecting the same account retries
      `needs_creator` rows at once; connecting a different one marks its
      containers for a new pick and tells the creator; replacing a container
      queues the old grants for revoke and writes nothing on the new one,
      where the Peer's next Open is what grants (`D-040`)
- [ ] On a provider that grants on items (`D-036`), Open grants exactly the
      one file it is opening and touches no other Episode, a new Episode
      writes no rows and calls nothing, and changing an Episode's file takes
      the readers Qori added off the old one
- [ ] Two grants on one target never run at once
- [ ] `PlaybackTicketService::open()` reaches the bound integration through
      the public `openLinkFor()`, and no second holder of the
      `grant-providers` tag exists
- [ ] A row this Group cannot resolve carries every column `T-157`'s three
      lists read — provider, target, principal, `last_error_code` and
      `revoked_at` — and no row of another Group is ever reachable through
      them
- [ ] `docs/flows/vendor-access.md`, `accesses.md`, `storage.md`, `tenancy.md`,
      the flows index and the tinker recipe describe what was built
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~May one Series mix providers, one container each, or is it one provider
  per Series? The unique constraint allows mixing; the answer may tighten it
  — the owner's.~~ ~~A container dedicated to one Series, enforced by
  `(group_id, provider, external_id)`: confirm, or allow one folder to serve
  several Series, which changes what revoke may remove — the owner's.~~
  **Answered 18 September 2026 (`D-025`):** mixing allowed, one container per
  `(group_id, series_id, provider)`, dedicated to one Series; one connected
  provider recommended, not enforced, because each connected provider costs
  each Peer one more vendor sign-in.
- ~~Should grants needing the creator also appear on the Series' Peer list,
  or is the Integrations page enough?~~ **Answered 20 September 2026 by the
  owner: both.** A creator looking at who has access to one Series should see
  there that somebody was never let in, rather than learning it on a page
  about connections. The Integrations page stays the place it is fixed, and
  the Series page is where it is noticed. **It is `T-157`'s to build**, not
  this task's: `SeriesController::peers()`
  (`app/Http/Controllers/Share/SeriesController.php:418`) is already that
  task's file for the `containerImpact` prop, and the row shape it returns —
  `id`, `name`, `email`, `grantedAt`, `wasPaid` — takes one more field read
  from the states this task writes.
- ~~The provisional numbers: `REQUEST_TIMEOUT_SECONDS` 5 and
  `REQUEST_DEADLINE_SECONDS` 12, budgets the vendor's client may only shorten
  (`D-034`, `F08`), `RECHECK_MINUTES` 15, and whether Open re-checks a
  granted row on every click instead of once per `RECHECK_MINUTES`.~~
  **Answered 20 September 2026 by the stream owner**, in the bullet further
  down that sets all of them from the timings below; `RECHECK_MINUTES` stays
  15, so Open re-checks once a quarter hour rather than on every click. The
  reasoning here held and is kept for it: **the deadline is the number a
  Peer now feels**, because Open is where every vendor call happens
  (`D-040`): twelve seconds allows a renewal, a read and a create at the
  measured worst case, and anything less cuts one of them off. **`T-093`,
  20 September 2026:**
    - `permissions.create` took 1.68 to 2.44 s alone, and up to 3.76 s as the
      fifth of five at once on one folder, which Google appears to apply one
      after another.
    - `permissions.delete` took 1.14 to 1.74 s.
    - `files.get` and the permission reads stayed under 0.85 s.
- ~~**Grants on an item, which `D-036` now needs.** The Decisions above keep
  one row per (Access, container) and say that a provider needing per-item
  grants is a change to this task's Database section; `T-093` is the spike
  that said so, and the owner chose per-file grants for Google Drive on
  20 September 2026.~~ **Written in, 20 September 2026:** the Decisions,
  Database, Code, Tests and Acceptance above carry the second target —
  `GrantTarget`, `grantsOn()`, the `target`, `episode_id` and
  `external_target_id` columns, `revokeItem()`,
  `ERROR_ITEM_MISSING` and `ERROR_ITEM_REPICK`, the
  lock on the target, and six cases. The container half is unchanged.
  `ensureItem()` was in that list and is not in the document: `D-040`, later
  the same day, left nothing for it to do.
- ~~The value of `INLINE_GRANT_LIMIT`.~~ **Gone with `D-040`**: no request
  makes more than one grant, so there is nothing to bound.
- What the Peer sees on a Series where nothing has been granted yet, which
  under `D-040` is every Series until somebody opens something. There is no
  notice to show — no rows exist — so the page is simply a list of Episodes
  with live Open controls, and the two-to-three-second wait happens at the
  click. Whether that wants a word before the first Open ("the first time you
  open one, it takes a moment") or nothing at all is a designer's call —
  anyone's, with a designer.
- Whether `T-096`'s Dropbox and `T-098`'s OneDrive still grant on a container.
  `D-036` changed Google Drive alone, on `T-093`'s evidence; `T-095` and
  `T-097` are the spikes that answer it for the other two, and each may bring
  its own answer — the stream owner's, with those spikes.
- `T-093`'s answers for this task (`reports/T-093-2026-09-20-wayne.md`):
    - A Peer removed by hand in Drive reads the same 404 as one Qori removed
      (`errors-permissions-get-404-notFound-removed-by-hand.json`).
    - The same account reconnecting reaches the stored folder without a
      re-pick (`files-get-folder-after-reconnect.json`).
    - A different account's token gets 404 on it
      (`errors-files-get-folder-other-account-404-notFound.json`), so that
      reconnect marks the container for re-pick.
    - Under `drive.file`, one item beneath the folder that the creator has not
      picked blocks every grant and every removal on it, which `T-094`'s
      re-draft decides how to meet.

    Anyone's.

- **What `D-040` leaves for this re-draft to finish.** ~~whether `checkNow()`
  earns its place at all now that Open does the same work with a redirect at
  the end of it~~ — **answered 20 September 2026 by the stream owner: it does
  not, and it is gone**, with `PEER_CHECK_SECONDS`, `scopeRecheckable()`, the
  `shared.access.check` route, `AccessCheckController`, four lang keys and
  cases 25 and 42 to 45. The reasoning is in the Decisions. The other two went
  to `T-157` with the surfaces they belong to: whether a `revoke_failed` row
  should ever be retried automatically on the creator's next visit to the
  Integrations page, and what the unresolved-removals list says when the
  permission was on an Episode since deleted — `T-157`'s, with a designer for
  the second.

- ~~The sweep's interval.~~ **Moot under `D-040`**: nothing in this task is
  scheduled, so the Laravel Cloud sleep-timeout question it raised belongs to
  whichever task next adds a command.
- ~~Confirm the Scheduler is running in production (`routes/console.php:18-22`
  says no; `PLAN.md` says done 11 September 2026).~~ **Confirmed by the owner
  on 20 September 2026: it is on and running.** `routes/console.php` was the
  one that was wrong and its comment is corrected. Nothing in this task is
  scheduled anyway (`D-040`), so this mattered only to `T-094`'s
  `qori:episodes:check` and to `T-151`'s refresh, both of which can now count
  on it.
- ~~The new provisional numbers: `PEER_CHECK_SECONDS` 30,
  `MANUAL_RETRY_SECONDS` 60 and `MANUAL_RETRY_LIMIT` 20.~~ **Set from
  `T-093`'s measurements on 20 September 2026, by the stream owner**, and no
  longer provisional. `REQUEST_TIMEOUT_SECONDS` 5 → **6**, because the
  measured worst single call is a contended create at 3.76s and 5 left 1.24s
  before a call that would have worked became a false timeout; two full
  budgets also fill the deadline exactly, which is what one Open makes.
  `REQUEST_DEADLINE_SECONDS` **stays 12**: the worst realistic Open is a 3s
  lock, a renewal, a 0.85s read and a 2.44s create, about 7.3s.
  `MANUAL_RETRY_LIMIT` 20 → **12**, because twenty `files.get` at the
  measured 0.85s is 17s and the deadline always cut first, so the count was
  decoration; twelve is 10.2s and binds. `RECHECK_MINUTES` **stays 15**: one
  0.85s read on the first Open of each quarter hour, and it is the only way
  Qori notices a permission removed by hand, which `T-093` found reads as the
  same 404 as one Qori removed. `PEER_CHECK_SECONDS` went with `checkNow()`
  and `MANUAL_RETRY_SECONDS` went to `T-157`.
- **`BACKOFF_MINUTES` was a lockout, and is now a floor.** Not a question
  anyone had asked: `[1, 5, 30, 120, 1440]` was written for a sweep that
  retried on its own, and `D-040` made Open the only retry there is, so after
  five transient failures the person pressing Open again was refused for a
  day with the control greyed out — against `D-040`'s own "retried by the
  person pressing Open again". **Set to `[0, 1, 2, 5, 15]` on 20 September
  2026 by the stream owner**: the second press works at once, the fifth costs
  fifteen minutes, and a backoff protects a vendor from a loop rather than
  from a human.
- ~~A replace checks every affected Episode inline, one `checkItem()` each at
  `REQUEST_TIMEOUT_SECONDS`, so a Series of forty file Episodes on a slow
  vendor holds the request for minutes. Cap it as Try again now is capped and
  leave the rest to `qori:episodes:check`, or accept it — anyone's, with
  `T-094`'s observed timings.~~ **Answered 19 September 2026:** capped as Try
  again now is, at `MANUAL_RETRY_LIMIT`: the first Episodes in the Series'
  order, up to the limit, are checked before the response, the rest wait for
  `T-094`'s daily `qori:episodes:check`, and the `[2,*]` Episodes sentence no
  longer says "at once". ~~The limit stays provisional until `T-093`'s timings.~~
  **Set to 12 on 20 September 2026** by the bullet above.
- ~~`checkEpisode()` is declared here and not in `T-094`, and records into
  `content.checked_at` and `content.missing_since`, the keys `T-094`, `T-096`
  and `T-098` read; `T-094`'s `checkItems()` becomes the loop over it and the
  per-Episode Check now calls it. Confirm with `T-094`, whose draft may still
  declare it — anyone's.~~ **Settled 17 September 2026 (`D-021`):** declared
  here, because `attach()` calls it and every container provider depends on
  this task; `T-094`, `T-096`, `T-098` and `T-100` cite it, and `T-094`'s
  `checkItems()` loops over it. The gatekeeper settled the rest the same day:
  it returns `EpisodeCheckOutcome`, which `T-094`'s `EpisodeCheckController`
  flashes from, and `T-094` builds `qori:episodes:check`, that controller and
  `missingSince`. Whether `T-090` adopts these `content` keys or adds its own
  columns is `T-090`'s open question.
- ~~`D-024` holds the live-session containers until they fit a per-Episode
  join link (`D-026`), so this draft's meeting half waits:
  `ContainerChangeImpact::kind()` answering `meeting`, the eight
  `series.container_change.meeting.*` lines, case 60 and the Zoom half of
  case 28. Does it stay here, written and
  waiting, or move to `T-100` and `T-101`, the only tasks that would use
  it?~~ **Answered 20 September 2026 by the stream owner: it moves**, and
  both tasks took it as a dated amendment the same day, `D-024`'s hold
  intact. Two things stayed, to stop two tasks declaring one thing:
  `vendor_grants.join_url`, because this task's migration creates the table
  and an `ALTER` for a nullable string buys nothing, and
  `ContainerChangeImpact` itself, because `T-157`, `T-100` and `T-101` all
  build one. Structure here, meaning there. The Teams-container-with-no-
  connection question went with the move and is `T-101`'s to settle.
  **Found on the way, and answered on the consolidation pass, 20 September
  2026, by the stream owner.** Of the eight lines, the four
  `series.container_change.meeting.replace.*` are **`T-100`'s** to declare and
  `T-101` reads two of them from it, which is why `T-101` now carries
  `depends: T-100`. The four `series.container_change.meeting.remove.*` are
  **written by nobody and dropped**: `T-100` only ever replaces a meeting,
  `T-101` has no remove, and the only draft building a remove is `T-094`, for
  a Drive folder. Four sentences describing an action nothing offers are four
  sentences somebody has to keep true for nothing; whichever task first builds
  a meeting remove writes them then, against what that remove actually does.
- ~~Wherever the meeting half lands, its `meeting` lines of
  `series.container_change.*` are written from `T-100`'s and `T-101`'s
  drafts.~~ **It landed in `T-100`, 20 September 2026**, and the reasoning
  that decided it is why: Zoom cancels the old registrants, Teams
  tells Microsoft nothing, so the lines say what Qori stops doing and nothing
  about the vendor account; `T-100` adds Zoom's cancelled registrations as a
  `series.container.zoom.change.replace` note, and `T-101` builds its entry with
  its own Peers sentence and no Episodes sentence. Wording answerable to two
  vendors' behaviour could never have sat in a draft that can see neither,
  which is the whole reason it left this task.
- A `granted` Peer keeps opening while the provider is disconnected only
  because every provider draft's `openLink()` makes no call; a provider whose
  `openLink()` needs a live token would have to answer `blocked()` instead,
  and `T-044`'s disconnect dialog has to say the same as the paragraph above —
  anyone's, with `T-044`.
- `T-089`'s names — `shared.episodes.open`, `OpenEpisodeController`,
  `PlaybackTicketService::open()`, `VendorLink` with its
  `blocked($state, $provider)` and `isBlocked()`, the redirect to `shared.show#access` with `shared.vendor_notice.redirected`,
  `lang/en/shared.php` — were taken from its draft and `D-020`.
  **Checked 20 September 2026: `T-089` is `done`, and every name holds** —
  `routes/shared.php:49`, `OpenEpisodeController:27`,
  `PlaybackTicketService::open(User, string, string): MediaLink|VendorLink`
  at `:67`, `VendorLink::blocked(string $state, EpisodeProvider $provider)`
  at `app/Data/VendorLink.php:35`, `isBlocked()` at `:41`, and
  `shared.vendor_notice.redirected` at `lang/en/shared.php:16`. `$state` is
  a plain string whose docblock names a `VendorGrantStatus` value, so the
  enum is still this task's to create. **One gap worth knowing:**
  `OpenEpisodeController:43` already redirects to `shared.show#access`, and
  nothing in `resources/js/pages/shared/Show.vue` carries `id="access"`, so
  the anchor this task adds is a target something is already aiming at.
- ~~Whether `App\Data\VendorIdentity` is the shape `T-092`'s row hands to
  `grant()`, or that task prefers to pass its model — anyone's, with
  `T-092`.~~ **Answered 19 September 2026:** a Data shape, renamed
  `App\Data\GrantIdentity` so it no longer shares a basename with `T-092`'s
  `App\Models\VendorIdentity`, whose `toGrantIdentity()` builds it; `grant()`
  takes `?GrantIdentity` and `identityFor()` returns it. How that sits with
  `CLAUDE.md`'s sentence on what an integration takes in is under Decisions.
- ~~Whether `ContainerLock::run(ConnectionProvider, string, Closure)` becomes a
  call to `T-044`'s `AdvisoryLock::run(string, string, Closure)`, or both
  classes stay around one `pg_advisory_xact_lock` statement — the stream
  owner's, before either task is `ready` (`T-044`).~~ **Answered 19 September
  2026:** a call. `ContainerLock` is gone, and the container lock is
  `AdvisoryLock::run('container', $provider->value.':'.$externalId, …)`.
  **Corrected 20 September 2026 against the built class**
  (`app/Support/AdvisoryLock.php:56`), because this task cited it with three
  parameters and no return: the real signature is
  `run(string $namespace, string $key, Closure $callback, int $waitSeconds = self::WAIT_SECONDS): bool`,
  with `WAIT_SECONDS = 3` at `:35`. Two things follow that the sections above
  have to say. It **returns `false` when the lock was not taken and the
  callback did not run** (Postgres `55P03`), so every caller here branches on
  it rather than assuming the work happened; and a caller inside a Peer's
  request passes what is left of its deadline as `$waitSeconds` instead of
  taking the default, which is the acquisition budget `F08` says is missing.
  The callback is `Closure(): void`, so anything it produces comes back by
  reference.
- `T-044`'s names — `lang/en/connections.php`, `Connection::isLive()`,
  `ConnectionService::fresh()` with its `REFRESH_MARGIN_MINUTES`, and
  `markForReconnect()`, `AdvisoryLock::run()`,
  `App\Events\ConnectionReconnected` with `connection`, `sameAccount` and
  `previousExternalId`, the migration `2026_09_20_000000` this task's sorts
  after, the provider section component the two lists and Try again now slot
  into (`ProviderSection.vue`'s `#grants` slot), and
  `connections.providers.<provider>.name` for `:vendor` and `:provider` — are
  taken from its draft. **Checked 20 September 2026, with `T-044`, `T-151`
  and `T-152` merged: every name holds but one.** `ConnectionService::fresh()`
  is at `:403` and `REFRESH_MARGIN_MINUTES` at `:107`; the model's
  `markForReconnect()` at `Connection.php:165` writes the two columns while
  the service's at `ConnectionService.php:487` also notifies, so this task
  calls the service; `Connection::isLive()` at `:143`;
  `ConnectionReconnected` carries all three properties and names
  `ResumeGrantsAfterReconnect` in its own docblock; `ProviderSection.vue`'s
  `#grants` slot is at `:421`, in `resources/js/components/share/`; and
  `connections.providers.<provider>.name` is keyed by the
  **`ConnectionProvider` value** — `google_drive`, with an underscore — not
  by its `slug()`. The exception is `AdvisoryLock::run()`, corrected in the
  bullet above. One thing to know before the `grant-providers` tag is
  written: `account-connectors` is tagged with an **empty array**
  (`IntegrationServiceProvider.php:53`) until `T-094`, so the pattern to copy
  is `media-providers` at `:36`, not its neighbour.
- ~~`PlaybackTicketService::open()` is written as returning
  `providerFor(...)->openLink(…)`, but `providerFor()` is private to
  `VendorAccessService`, which is why `handles()` exists for `T-094`. `open()`
  needs a public way to the bound integration's `openLink()`: a method on
  `VendorAccessService` that answers it for a `granted` row, or the
  `grant-providers` tag handed to `PlaybackTicketService` as well.~~
  **Answered on the consolidation pass, 20 September 2026: a method here**,
  `openLinkFor(VendorGrant, Episode, int): ?VendorLink`, which the Code
  section now calls. The tagged iterable stays resolved in one class, as
  `handles()` already assumes; a second holder of the `grant-providers` tag
  would be a second place to keep the binding right. This one mattered more
  than an open question usually does, because the Code section was asserting
  the unanswered version as the implementation — a call to a private method on
  another class, which does not compile.
- What `attach()` does when its `checkContainer()` answers `exists` false or an
  `errorCode` — a 401 among them now, which marks the connection — is not
  specified: `T-094`'s `SeriesContainerController` relies on `attach()` to
  check the folder, while `T-100` checks the meeting itself first and throws
  its own `errors.meeting.*` — anyone's, with `T-094`.
- ~~Whether `T-093`'s report keeps one grant row per (Access, container) and
  the `checkGrant()` read of a stored permission, or changes the Database
  section — anyone's, when `T-093` reports.~~ **`T-093` reported on
  20 September 2026 and it changed the Database section**, which is `D-036`
  and the second target: one row per (Access, container) **or** per (Access,
  Episode). The `checkGrant()` read of a stored permission survived and grew
  a fallback, for the row that has no stored permission to read
  (`F01`, above). Struck on the consolidation pass, where it was still asking
  a question its own answer is written on top of.
- ~~**Split.** This is `L` (about 35 files and 64 cases), and `blocks:` lists
  the tasks that build on it, not pieces it was cut into, so `PROCESS.md`'s
  rule for a ready `L` task is not yet met.~~ **Answered 20 September 2026 by
  the stream owner: (a) as this task, (b) as its own draft after it.** (a) is
  the grant core and the Peer's path through Open; (b) is `T-157`, drafted
  the same day, which `blocks:` now names. (c), the meeting half, went to
  `T-100` and `T-101`. The estimate stays `L`: **36 files and 56 cases**,
  counted from the table and the sections on the consolidation pass rather
  than carried forward, is still two days, and what `PROCESS.md` asks of a
  ready `L` is that it names its split, which `blocks:` now does. The 22 and
  the 59 it said before were both guesses at a document that had just been cut
  three ways.

### `D-040` re-drafts this task, 20 September 2026

**Read this before the review's findings below.** The owner removed the
scheduled sweep the same day: a grant is made when a Peer presses Open, for
that one item, and at no other time (`D-040`). This task is written on the
opposite assumption throughout, so it needs a re-draft larger than `D-036`'s
before any of the bullets below can be read as still applying.

- The sweep goes whole: `qori:access:reconcile`, its command, its
  five-minute schedule, `SWEEP_TIMEOUT_SECONDS`, `scopeDue()`'s retry timing
  and every test of them. So does `INLINE_GRANT_LIMIT` and the fan-out bound
  `D-036` introduced, because nothing is granted ahead of use any more.
- **Open must grant.** The note struck above declining Open on a pending
  item is reversed by `D-040`, and for the reason it gave: it was declined
  because the sweep would arrive within minutes, and there is no sweep. Open
  on a not-yet-granted Episode is now the only path that exists.
- **A failed revoke is listed, not retried.** The inline attempt at refund
  and removal stays; when it fails the row is unresolved and the Integrations
  page shows the creator who could not be removed, from which file, with a
  Try again they press. That list is `F01`'s durable revocation intent by
  another name, and it is the one part of the review's first finding that
  this decision makes more important rather than less.
- The six states stay, and matter more: a Peer pressing Open against a
  creator's dead connection must meet `needs_creator` rather than a retry
  that can never work.
- `F07` dissolves with the scheduler. `F08` grows: Open now calls a vendor
  inside a person's request, so the total deadline is no longer optional.

### From the storage review, 20 September 2026

Each bullet is a finding of `reviews/storage-2026-09-20-findings-codex.md`,
accepted by the owner. **That file no longer exists and cannot be recovered.**
`reviews/README.md` has a findings file transferred into the plan and then
deleted, which is by design — but it also says to commit it first, because a
file git has never seen is destroyed by deleting it, and it names this as the
one that was lost that way on 20 September 2026. So the bullets below are not
a summary of something a reader can go and check: they **are** the surviving
record of that review, and they are to be read as the primary source.
(`reviews/storage-2026-09-20.md`, the brief that commissioned it, is still
there.) They are why this task must not be set `ready` as it
stands: the foundation is where seven of the twelve findings land.

- ~~**Revocation intent does not survive the thing it points at** (`F01`).~~ **Written in, 20 September 2026**, in four parts: the grounded section below establishes which deletion paths actually exist and settles that intent survives the content but not the account (`D-038`, `D-039`); `episode_id`, `series_container_id` and `access_id` are `nullOnDelete`, following `payment_fulfilments`' precedent; the row is written and committed before the vendor call, carrying `principal`, `external_target_id` and `provider`; and `pending` splits, with `attempting` meaning a create went out and was not answered. The finding, for the record:
  `vendor_grants.episode_id` is `FK episodes cascade`, so deleting an Episode
  with three hundred granted Peers destroys the two hundred and eighty
  permission ids `revokeItem()` had not reached, and the first twenty too if
  their calls failed. `SeriesService` purge deletes Episodes directly and
  never calls it at all. Replacement has the same shape: one row per
  `(access_id, episode_id)` still holds the old `external_target_id`,
  `firstOrCreate()` does not move it to the new file, and `scopeRevokable()`
  names a revoked Access or a missing container, never a replaced item under
  an active Access. Revocation intent has to be persisted with the account,
  target, principal and permission reference it needs, and outlive the
  content — and `pending` must stop meaning "nothing was created", because a
  create whose response was lost looks exactly the same — anyone's, and it is
  the first thing to specify.
- ~~**Two Qori grants can own one vendor permission** (`F02`). Uniqueness is
  `(group_id, access_id, episode_id)`, which is Qori's bookkeeping, not the
  vendor's. One file in two Series, two Episodes on one file, or two Qori
  people who confirmed the same Google account all produce two grants over
  one permission, and revoking either takes away access the other one paid
  for.~~ **Answered 20 September 2026 by the owner, as `D-041`:** the
  permission is keyed by (connected account, target, principal) and revoked
  only when the last entitlement over it ends, under the same lock.
  Restricting reuse was refused because the same file in two Series is
  something creators do. The Acceptance line and case 71 carry it; `T-092`
  inherits the case where two Qori people confirm one Google account.
- ~~**The principal actually granted is not stored** (`F04`), so an identity
  change whose revoke of the old account fails leaves a permission nothing
  can find again, and an identity removed and re-added leaves rows bound to
  the old account while Open sends the new one.~~ **Written in.** The
  `principal` column is written at the attempt and never overwritten, and it
  is the third part of `D-041`'s key, so a permission Qori cannot name the
  principal of is one it can neither find nor count. A confirmed identity
  that no longer matches queues the old permission for revoke and writes a
  new row rather than overwriting, which Acceptance and case 72 carry.
- **Disconnect throws away the only authority that could clean up** (`F05`),
  which `D-038` now contradicts. See `T-044`, where the decision belongs.
- ~~**The fan-out arithmetic in this draft is wrong, and the sweep is
  unbounded** (`F07`).~~ **Dissolved, 20 September 2026, and checked rather
  than assumed.** `D-040` removed the sweep, so the run limit, checkpoint,
  fairness rule and overlap guard have nothing to bound and the
  payment-to-first-item objective has nothing to measure: no request makes
  more than one grant. The wrong line the finding names at `:905` went with
  `INLINE_GRANT_LIMIT` in the same re-draft and is not in this document any
  more. The second half goes too — the Series page never learning the work
  finished was a problem because the work happened elsewhere; it now happens
  inside the Open the Peer pressed, which ends at the file. What replaced the
  arithmetic is the constants above, set from the same measurements the
  finding used. For the record, the finding's own numbers, which were
  right: A new grant is a list and a create, so six thousand
  grants is twelve thousand calls, not six thousand; at the seconds `T-093`
  actually measured — create 1.68 to 2.44, list 0.52 to 0.84 — that is 220
  to 328 minutes serial, one new Episode for three hundred Peers is 11 to 16
  minutes, and the daily recheck of six thousand rows is 52 to 84 minutes.
  The line at `:905` saying five inline grants are about ten seconds in the
  worst case is wrong on the same evidence: five are 11 to 16 seconds. The
  sweep itself has no run limit, checkpoint, fairness rule across Groups or
  overlap guard, and scans existing rows rather than reconstructing work
  from active Accesses and targets, so a swallowed write is never retried.
  It asked for a bounded processor with durable progress and a measured
  payment-to-first-item objective, called fairness the part that mattered
  most — round-robin across Groups, a run limit, an overlap guard, revocation
  before new grants — and noted that the Series page never learns the work
  finished, because it does not poll. Every line of that is a requirement on
  a sweep, and there is no sweep. It is quoted here and nowhere else in this
  document, because on the consolidation pass of 20 September 2026 it was
  still reading as live instruction under a struck heading.

    The only part that outlives `D-040` is the observation underneath it —
    that a grant is a read and a create, not a create — and that is now in
    `REQUEST_DEADLINE_SECONDS`, which budgets for both.

- ~~**A person's request has no total deadline** (`F08`).~~ **Written in, 20
  September 2026**, as the Decision "One deadline, spent down by every step
  inside the request": every entry point takes `$deadlineSeconds`, each step
  reads what is left before it starts, and a step with too little does not
  run and does not fail. The acquisition budget the finding calls out is the
  fourth parameter of `T-044`'s built `AdvisoryLock::run()`, which also
  returns `false` when the lock was not taken, so a caller branches on it
  instead of assuming. The finding, for the record: `D-034` bounds one
  call; a five-item ensure can spend fifty seconds of vendor calls, the
  twenty-row retry two hundred, and the advisory lock is specified as a
  blocking `pg_advisory_xact_lock` with no acquisition budget at all, so
  even a fast call can follow an unbounded wait. Needs a request deadline
  passed through refresh, lock, pagination, create and retry, with the rest
  converted to persisted intent before returning — anyone's.
- ~~**A due `pending` item could offer Open, and today nothing does**
  (`F07`).~~ **Declined on the morning of 20 September 2026 and granted in
  full by `D-040` the same day.** The review asked that a due `pending` item's
  Open control attempt that one item rather than stay disabled. It was
  declined on the arithmetic of the sweep — a Peer waits at most one five-minute
  tick plus their remaining grants, about six minutes, which the owner judged
  acceptable — and then `D-040` deleted the sweep and made Open the **only**
  way a grant is ever made. So the review was right and the refusal is void:
  what it asked for as an exception is now the whole mechanism, and the reason
  it was refused stopped existing hours later.

    This is the one finding whose disposition read backwards, and it is worth
    keeping visible rather than tidying away. The refusal turned on a number —
    six minutes of sweep latency — and the decision that followed removed the
    thing the number described. A disposition that cites an argument rather
    than a principle expires when the argument does, and nothing warns you.

- **The container-shaped consumers were not moved with the grant** (`F10`).
  Split by the cut of 20 September 2026, because the four consumers no longer
  sit in one task.
    - ~~**Here, and still open:** `checkEpisode()`'s contract requires
      `insideContainer` truth where an item result sets it null.~~ **Written
      in, 20 September 2026.** The contract branches on `grantsOn()`: a
      container provider reads its container and then the item, an item
      provider reads the item alone and ignores `insideContainer`. Before
      that branch an item Episode that plainly existed came out neither
      `Clear` nor `Flagged`, because `exists && insideContainer` and
      `insideContainer === false` are both false when the value is null. The
      Peer notice was answered earlier, reading `provider` from the row and
      `url` from `$grant->container?->url`.
    - **`T-157`'s:** the Try again now query requiring an active Access "with
      a container", which excludes every Drive item grant, and its creator
      list loading `container.series`. Both went with Try again now, and that
      task names the contradiction rather than inheriting it silently: its
      `retryNeedingCreator()` docblock still carried the container wording
      while the Decisions above it said "whatever their target".

## Amended 20 September 2026 — the column was renamed

`T-044`'s `needs_reconnect_at` became `reconnect_required_at` after that task
shipped, in
`database/migrations/2026_09_20_000300_rename_reconnect_column_and_google_personal_tier.php`.
Case 62 above cites the new name. Nothing else moved:
`Connection::markForReconnect()`, `ConnectionService::markForReconnect()`,
`needsReconnect()`, `ConnectionNeedsReconnectNotification` and
`reconnect_reason` are all unchanged, because the column names the event Qori
observed and those name the remedy, which did not.

## Grounded 20 September 2026 — what actually destroys a grant

`F01` says revocation intent must outlive the content, and names
`vendor_grants.episode_id`'s cascade and `SeriesService` purge. The code was
read to see whether that is the whole of it. It is not, and two of the
finding's assumptions do not hold.

**Every path that destroys an Episode row today.** Two in PHP, both hydrated
model deletes rather than bulk: `EpisodeService::remove()`
(`app/Services/EpisodeService.php:301`, its `$episode->delete()` at `:322`)
and `SeriesService::purge()` (`app/Services/SeriesService.php:279`, its delete
at `:307`, one per Episode, deliberately outside a transaction). Everything else is the database: `episodes.series_id`,
`series.group_id` and `groups.owner_user_id` are all `cascadeOnDelete`
(`2026_09_08_000000_create_qori_schema.php:105`, `:84`, `:58`).

**That chain has a live trigger this task has to answer for, and the finding
does not name it.** `ProfileController:128` is `$user->delete()` — a creator
deleting their own account. Every Series, Episode and Access in the Group they
own goes at the database level, in one statement, **with no PHP running at
all**. A second mass delete lives at `MailCheckCommand:287`
(`Series::query()->forGroup($group)->delete()`), the only query-builder mass
delete in the codebase.

**Nothing can be hung off a model event, because the application has none.** A
sweep of `app/` for `static::deleting`, observers or `ObservedBy` returns one
hit, `BelongsToGroup::creating` at `app/Concerns/BelongsToGroup.php:25`, which
stamps `group_id`. No model in Qori uses `SoftDeletes` and no migration
declares a `deleted_at`. So "outlive the content" cannot lean on a soft delete
or a deleting hook; it has to be the column shape.

**The finding's replacement case cannot happen the way it describes.** There
is no in-place replacement: `EpisodeService::update()` refuses a raw `content`
payload outright and its docblock says "Replacing the Episode is the honest
path", while `UpdateEpisodeRequest` accepts six keys, none of them `content`,
`provider` or `type`. A replacement is therefore a delete and a create with a
**new ULID**, so `firstOrCreate()` never meets a stale `external_target_id` on
a live row — it meets a row whose `episode_id` has gone null. The outcome
`F01` worries about is real; the mechanism is not.

**The one true in-place repoint is `join_url`** (`EpisodeService.php:219-227`,
written through `LiveSessionService::withLockedContent()`), where a creator
changes which meeting a live Episode points at and keeps the Episode id, with
nothing recording the URL that was there before. That is the meeting half, and
it goes to `T-100` and `T-101` with the rest of it — named here so it is not
lost on the way.

**The pattern to copy already exists.** `payment_fulfilments` is the record
that has to outlive what it points at, and it does it with nullable FKs:
`group_id`, `series_id`, `user_id` and `access_id` are each
`nullable()->nullOnDelete()`
(`2026_09_09_000000_create_payment_fulfilments_table.php:33-36`), with a
docblock saying "the case worth recording is the one where no access exists".
`vendor_grants` is the same kind of row and takes the same shape. There is a
second precedent for an id outliving its row, less deliberate:
`accesses.opened_episode_ids` is unconstrained `jsonb` and keeps the ids of
deleted Episodes for ever.

**Decision: intent survives the content, not the account.** `episode_id`,
`series_container_id` and `access_id` are `nullOnDelete`, so a grant holding a
`vendor_ref` is still there to be acted on when the Episode, the container or
the Access goes. `group_id` stays `cascade`, which means a creator deleting
their account takes every unrevoked grant with it and no permission is ever
removed. That is not a gap to close but the same answer `D-038` and `D-039`
already give: Qori removes only the permissions it created, and a disconnect
leaves every permission standing, because the authority to remove them was the
creator's and they have withdrawn it. Deleting the account withdraws it
completely. The Copy section says this where a creator can read it before they
act.

**`pending` still has to split**, and that part of `F01` stands untouched by
any of the above: a row that has made no vendor call and a row whose create
lost its response are the same value today and are opposite instructions. The
re-draft writes the intent before the call rather than after it.

## Read-through and consolidation, 20 September 2026

Three independent passes over this file before it was to be marked `ready`:
one on cross-section consistency, one hunting residue of the sweep `D-040`
deleted, one on the boundary between this task, `T-157`, `T-100` and `T-101`.
They found about a hundred items, which is the answer to whether the cut was
clean: it was not. **They were worked through the same day**, in a
consolidation pass across all four files at once, and this section is what
that pass did rather than what the read found.

**The shape of it, which is the part worth keeping.** Everything the cut
removed from **Scope, Files, Routes, Copy and Tests** went cleanly, because
those are lists and a list can be checked. Everything written as **prose in
Decisions** stayed, because prose has to be read to be found: the grep that
finds a table row does not find a paragraph meaning the same thing in other
words. Two whole decisions survived the cut still building `T-157`'s screens,
one of them ending "This task builds the dialog and renders it nowhere" —
directly against a Scope section two hundred lines above it. **A future split
starts from the Decisions section, not finishes there**, and is read across
every affected task at once, because three of the worst items below were
invisible from inside any single file.

### What would have built the wrong thing, and is fixed

- **`attempting` was declared and handled nowhere.** Added that morning for
  `F01`, wired into the enum, `mayHoldPermission()` and the Database note, and
  then read by nothing: `scopeRevokable()`, `revokeFor()` and `D-041`'s
  last-entitlement count each enumerated `granted or awaiting_acceptance` on
  their own. A permission Qori created would never have been revoked on
  refund, and would have been invisible to the count, so a different row could
  look like the last entitlement and strip access somebody still held. Fixed
  by `VendorGrantStatus::entitles()`, one predicate with three callers, which
  `mayHoldPermission()` — never called — is replaced by. Two things the state
  needed and nobody had written are now in the contract: `checkGrant()` finds
  a permission by `external_target_id` and `principal` when there is no
  `vendor_ref`, which is every `attempting` row, and `stateFor()` answers
  `Pending` for it so the notice needs no ninth sentence. Case 81 is new for
  it, and the row-state table has the row it was missing.
- **Three test cases asserted the world `D-040` deleted.** Case 65 had a new
  Access write three rows and make three calls where case 2 in the same file
  has it write none; case 68 called `ensureItem()`; case 39 expected a
  `pending` row from a failing vendor on a paid path that now calls no vendor
  at all. Each is rewritten to test what it was really guarding — the row
  shape per Episode, the cost of adding an Episode, the paid-path guarantee —
  under the trigger that exists.
- **`attach()`'s replace still fanned out** in five places, against a Decision
  three hundred lines above saying attaching writes no rows. Fixed in the
  Decisions, the `attach()` docblock, cases 23 and 24 and the Acceptance line.
- **The Decisions built `T-157`'s surfaces in full** — Try again now with its
  throttle and tally, the impact dialog, `IntegrationsController::show()`'s
  props, `ContainerChangeDialog.vue`. All four are now a pointer and a
  statement of what this task leaves them to read.
- **The Open path could not compile.** `open()` was written as
  `providerFor(...)->openLink(…)`, a call to a private method on another
  class, while an open question below asked how `open()` should reach the
  integration at all. Answered: the public `openLinkFor()`, because the
  tagged iterable stays resolved in one class.

### Cross-task, and settled by the stream owner

- **`EpisodeService::remove()` and `SeriesService::purge()`** were named by a
  Decision here, denied by the Notes here, and claimed by `T-156`. This task
  owns the revoke-before-delete edit and **depends on `T-156`**, which lands
  first: it is `S`, unblocked and stops a leak that is happening now. The
  Notes' denial is corrected in place — it was true until `D-036`.
- **The meeting half now has one owner.** `T-100` declares
  `ContainerChangeImpact::kind()`'s `meeting` arm and the four
  `series.container_change.meeting.replace.*` lines; `T-101` reads two of them
  and **depends on `T-100`**. `vendor_grants.join_url` stays declared once, in
  this task's create migration, and both meeting tasks drop the `ALTER` they
  were each proposing — the trap being that editing this task to match either
  of them would have deleted the column from the plan entirely. The four
  `series.container_change.meeting.remove.*` lines are **dropped**: no task
  builds a meeting remove, and four sentences describing an action nothing
  offers are four sentences to keep true for nothing.
- `T-157`'s three-way contradiction on the Series' Peer-list marker, its
  narrower `kind()` docblock, and both meeting tasks' citations of
  `shared.access.check` and `shared.vendor_notice.opened` are that task's and
  were worked through with it.

### Counts, numbers and copy

Every stated total was recounted from the thing it counts rather than
adjusted: the Files table (44 and 7 where the sections numbered 51 and 6), the
`estimate: L` bullet (22 files and 59 cases where the table holds 36 and the
sections number 56), and the state count, given as six, seven, seven and eight
in four places against an enum with eight. Three cases asserted the old
`BACKOFF_MINUTES`, whose first value is now `0` — one of them could not have
passed at all. Two Decisions still called the constants provisional at 5 and 12. The row-state table was malformed, four rows carrying a cell the header
lost when the Check again column went, so it read as Try again now
re-verifying `granted` rows. Copy's trailing prose explained `:time`, `:date`,
`:seconds` and four plural forms, none of which any surviving key uses, and
the Files table still claimed `lang/en/connections.php`, which this task no
longer writes a line into. Cases 27 and 28 are retired in place with Try again
now and `impactOf()`. `grantFor()` and `peerResolves()` were declared and
called by nothing and are gone; `SeriesContainer::grants()` and
`ContainerCheck::$url` were the same and instead have their caller named,
because both have one.

**`F07`'s disposition read backwards** and is the one item worth a second
look. The review asked that a due `pending` item offer Open; it was declined
that morning on the arithmetic of the sweep, and `D-040` deleted the sweep
that afternoon and made Open the only way a grant is ever made. The refusal
cited an argument rather than a principle, and expired when the argument did.

### What is left

Nothing on the list. What still stands between this task and `ready` is in
"Before this can be ready" above, and it is all owner's or spike's work
rather than consolidation: whether `T-096`'s Dropbox and `T-098`'s OneDrive
still grant on a container (`T-095` and `T-097` answer it), what `attach()`
does when `checkContainer()` refuses, and a designer's call on what a Peer
sees before the first Open of a Series.

## Verified 21 September 2026 — what the consolidation did not close

An independent read of the consolidated file, by someone who had not made the
cut. **The failure mode the consolidation predicted held, and caught the
consolidation too**: what survived is prose in Decisions, plus two Code
signatures and one Database line that the prose around them contradicts.
Thirteen items would build something wrong. They are additions to "Before this
can be ready", not part of it, and **this task is further from `ready` than
the consolidation record above implies**.

The counts, the `T-157`/`T-100`/`T-101` boundary, the constants, `entitles()`,
`openLinkFor()` and the removal of every deleted artefact were all checked in
both directions and are clean.

### The owner's, because a decision record says otherwise

- **`D-041`'s row key makes `F04`'s behaviour impossible.** The Database
  section and `D-041` both key the bookkeeping row
  `(group_id, access_id, episode_id)`. `F04` says a confirmed identity that no
  longer matches the row's `principal` is not reused — "a new row is written
  for the new principal" — and rows are kept on revoke, so the old row is
  still there and the insert violates the constraint. Case 72 asserts the new
  row; Acceptance asserts it; the key forbids it. Adding `principal` to the
  key would fix it and contradicts `D-041` in terms, so it is an amendment
  rather than an edit. A partial index excluding `revoked` does **not** work:
  the case `F04` describes is precisely the one where the old row is
  `revoke_failed`.

### Would build the wrong thing

- **Nothing revokes what a replace or an identity change queues, and
  `scopeRevokable()` has no caller.** Three places say the old rows "become
  revokable"; the scope that selects them is described as "the revoke pass",
  and there is no pass — the sweep was what consumed it. So after a container
  replace every Peer keeps their permission on the old folder for ever, and
  because the rows stay `granted` they never reach `T-157`'s list either. This
  is the largest piece of sweep residue left, and it is a hole in the product
  rather than in the prose.
- **The deadline's numbered step order puts the lock before the renewal**,
  against the Decision three hundred lines above that reads the connection
  "before any container lock is taken, so the lock never waits on a refresh
  and `T-044`'s `'connection'` lock and this task's never nest".
  `ConnectionService::fresh()` really does take `AdvisoryLock::run()`
  internally (`app/Services/ConnectionService.php:411`), so the numbered list
  nests two advisory locks in one transaction — the exact thing the Decision
  forbids. `attempt()`'s docblock agrees with the Decision, not the list.
- **`ensureOpen()`'s caller list contradicts itself, and one named caller
  cannot call it.** The Decisions name Open plus three reconciliations; the
  docblock and the row-state table both say Open and nothing else. `T-092`
  is named as calling it on identity confirmation, which the signature
  forbids — `ensureOpen(Access, Episode, int)` needs an Episode and an
  identity confirmation has none. Scope repeats the three entry points as
  this task's.
- **`SharedController`'s prop reads a `$grant` nothing produces, and `open()`
  reads an unbound `$state`.** The only method offered is
  `stateFor(Access): ?VendorGrantStatus`, which returns a status, not a row,
  while the prop block reads `$grant->provider` and `$grant->container?->url`.
  `open()` returns `VendorLink::blocked($state->value, …)` with `$state` never
  bound, and `ensureOpen()` may answer null. Same shape as the `providerFor()`
  defect the consolidation fixed: an implementation asserted against an API
  the file does not provide.
- **An item grant's `external_target_id` has no named source.** The Database
  says "the item's id from the Episode's `content`" and never names the key,
  which is vendor-specific in the live code — `content['file_id']` for Drive,
  `content['path']` for Dropbox, `content['vimeo_id']` for Vimeo. No contract
  method answers it, so `VendorAccessService` would have to read a vendor's
  payload key, which `CLAUDE.md`'s "Where code lives" forbids outright. The
  contract needs the method.
- **`attach()` is named as an entry point taking `$deadlineSeconds` and its
  signature has none**, and its twelve inline checks each get a fresh
  `REQUEST_TIMEOUT_SECONDS` — a worst case of 72 seconds in a request the
  same task bounds at 12. `SeriesService::purge()` has the same shape from the
  other side: one `revokeItem()` per Episode, each defaulting to a fresh
  12-second deadline, so a twenty-Episode purge is bounded at 240 seconds in
  one web request. Both are the hole `F08` exists to close, in a task that
  claims to have closed it.
- **`ensureOpen()` runs for every Episode that is not Qori-hosted**, including
  Vimeo and `Link`, which have no grant provider — `checkEpisode()` and
  `EpisodeCheckController` both guard with `handles()` and this path does not.
  Every Vimeo open writes a spurious `pending` row with `ERROR_NO_INTEGRATION`,
  which the file elsewhere calls a deployment fault worth `Log::error`.
- **The pending notice is promised a time no lang key can carry.** Three
  places say the notice carries the next-attempt time; four say it carries no
  time at all, and the Copy table's `reasons.pending` has no placeholder. A
  developer either invents a key or contradicts three Decisions.
- **Webhook replay is still described as running the grant step**, against
  case 5, `D-040` and the Decision on purchases.
- **Uniqueness is stated a third and wrong way** in the Decisions, as
  `(access_id, target)`, under which an Access could hold exactly one item
  grant in total.
- **Case 75 needs `EpisodeProvider::GoogleDrive`**, which `T-094` adds and
  this task does not edit; it should use the item-provider fake the
  surrounding cases use.

### Smaller, and recorded rather than argued

The `AccessService::grant()` code block shows a refactor of a method three
other places say is untouched. The `### D-040 re-drafts this task` heading
still reads as live instruction for a re-draft that happened, and carries a
fifth stale "six states" the consolidation's recount missed. The header and
Notes still say the meeting half is "still written here". `revoke_failed` has
no notice sentence but can reach the notice, landing the Peer on a page with
nothing to read. `identityFor()`, `scopeDue()`, `isGranted()`,
`SeriesContainer::series()`, `RevokeResult::$retryAfterSeconds` and
`series_containers.settings` are declared with no named reader — the same
standard the consolidation applied to `grantFor()` and `peerResolves()`.

**And the arithmetic nobody has written down:** at `T-093`'s measured 1.14 to
1.74 seconds per `permissions.delete`, a 12-second deadline reaches about
seven rows, so deleting one Episode from a three-hundred-Peer Series puts
roughly 290 rows on `T-157`'s unresolved list in a single action. The file
states the equivalent arithmetic for the sweep it deleted and not for the
revoke path it kept. **Revoke is now the one thing that still fans out per
Peer**, and `D-040` never costed it.

## Re-scope log

None.

## Notes

The blueprint's citations were written a day before this draft and some
moved: the existing-access branch is `AccessService.php:74-88`, not `:74-87`;
the free self-grant sits at `app/Http/Controllers/SeriesAccessController.php:146-150`.
~~The blueprint's per-item columns went with the one-row-per-container rule,
so Episode deletion touches no grant.~~ **Corrected on the consolidation pass,
20 September 2026: it was true for about four days and `D-036` ended it.**
With a grant on one Episode's own file, deleting the Episode destroys the only
thing that names the permission, so `EpisodeService::remove()`
(`app/Services/EpisodeService.php:301`) and `SeriesService::purge()`
(`app/Services/SeriesService.php:279`, one per Episode) each call
`revokeItem($episode)` above the delete — this task's edit, landing on top of
`T-156`'s, which touches the same two methods. The Decisions say it and case
73 tests it; this paragraph had been denying it since `D-036`, which is the
kind of contradiction only a read across the whole file finds. `docs/flows/accesses.md:77`, `:94` and `:103` still spell the sharing
route `/w/{group}` where `routes/share.php:25` has `g/{group}`; fix them in the
same edit.

Citations re-read against the code on 19 September 2026. Moved:
`ArchitectureTest`'s import rule is `test_integrations_import_no_app_layer` at
`:139-147`, since `T-112` added a test above it; Stripe's disconnect array is
`IntegrationsController.php:67-74`, with `payouts.disconnect_priced` at `:71`,
since `T-113`; `EpisodeService::remove()` starts at `:301`, not `:156` as this line said until 21 September 2026; the Inertia
middleware's reflash, fragment check and 409 are at `:150-152`, `:172-174` and
`:210-215`; `T-100`'s picker-and-attach service is `SeriesMeetingService` since
`D-026`. `CLAUDE.md` now says what the code does, `provider()` and
`IntegrationServiceProvider`, so the note that it did not is gone. Everything
else cited here still holds.

Nothing in this task calls `acrossAllGroups()`: there is no Group loop left
to add one (`D-040`), and `ensureOpen()` reaches the Series through
`Access::grantedSeries()`, which is already allow-listed. `VendorAccessService` calls contracts only, as
`tests/Feature/ArchitectureTest.php:30` requires.

**18 September 2026 (`D-030`, `D-024`).** `D-030` has this task's
`checkItem()` and the replacement impact grow a materials branch, so a
replaced folder flags picked materials as well as Episodes. That arm is
placed with `T-094`, which works it out with `T-130`'s `materials` rows and
records it as its own open question: `T-094` writes the picked Google Drive
items into those rows and depends on this task, so a branch here would wait
on its own dependant. This task's `checkItem()` contract and `checkEpisode()`
take Episodes only, and `impactOf()` lists Episodes only. `D-024`'s hold on the
live-session containers is in the header, Scope and the stream owner's bullet
above; none of the meeting half is deleted while it waits.

**19 September 2026.** `GrantResult::ERROR_PERMISSION_GONE` is shared, so
`T-094` and `T-098` drop the constant each declared on its own class, and
`T-096` answers it in place of its own `ERROR_MEMBER_GONE`. `ItemCheck`'s
`name`, `mimeType` and `url` answer `T-094`'s question about `describeItem()`,
and `handles()` its question about how `EpisodeCheckController` asks for a
bound grant provider.

**The 20 September 2026 re-draft (`D-036`).** `T-093` found that Google's
narrow scope refuses every sharing change on a folder while anything beneath
it is unpicked, so Google Drive grants per file and a Series has no Drive
folder. This task keeps the container model for the providers that still
share one and gains the item target beside it: one more column pair, one enum,
`grantsOn()` and `revokeItem()`. `T-094` is written against exactly this
shape, and nothing in it can be specified to the column until this task
carries it. `ensureItem()` and the fan-out bound were named here too and both
went with `D-040`, hours later.
