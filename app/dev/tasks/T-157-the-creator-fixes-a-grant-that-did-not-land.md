---
id: T-157
title: The creator fixes a grant that did not land
stream: storage
status: draft
owner: unassigned
estimate: M
depends: T-091
blocks: T-100, T-101
---

# T-157 — The creator fixes a grant that did not land

> **Cut out of `T-091` on 20 September 2026**, which was `L` at about 35 paths
> and 64 cases and named this as part (b) of its own split under "Before this
> can be ready": "the creator's surfaces on top of it — Try again now, the
> grants and repick lists on the Integrations page, and the container-change
> dialog". The stream owner took that recommendation the same day, and also
> settled part (c) against this file: the meeting half stays with `T-100` and
> `T-101`, so nothing this task builds ever produces a `meeting` container.
> Almost none of this is new — the decisions are `D-021`, `D-039` and `D-040`,
> and the copy, the code and the test cases are `T-091`'s, moved whole. Where
> the cut forced a change it is under **Decisions**, and every test case keeps
> the number `T-091` gave it, because other drafts cite those numbers.
>
> It is `M` rather than `L` because the split is the whole point: no schema, no
> vendor call, no new service class, and every shape it builds was written out
> in the task it came from.

## Why

`T-091` makes a grant when a Peer presses Open and records what the vendor said
as one of eight states (`D-040`, and `attempting` from `F01`). Two of those
states are the creator's to resolve, and neither of them reaches the creator. A
`needs_creator` row sits in `vendor_grants` where nothing displays it. A
`revoke_failed` row is a permission still standing in the creator's own account
— somebody refunded or removed who can still open the file — with no list naming
them. A container marked `repick` after a different account reconnects is a
third thing only the creator can fix: a Series nobody can open, and no page says
which Series. Under `D-040` nothing retries any of them on its own, so a row the
creator cannot see is a row that stays exactly as it is for ever.

The creator's Series page has the matching gap in the other direction: replacing
or removing a container moves every Peer and can strand every Episode on it, and
today the creator would find that out afterwards.

Afterwards each provider section on the Integrations page carries three lists —
who could not be let in, who could not be taken off, and which Series need
picking again. The first two name a reason beside each row and carry a button
that calls the vendor again at once; the third links each Series to the page
where it is picked again. The Series' own Peer list marks anybody a grant never
reached, and the Series page says what a container change will do to the Peers
and the Episodes before it is posted.

## Decisions taken to make this specifiable

**The cut follows the surfaces, so `T-091` keeps everything a Peer touches.**
The line is who is looking at the screen, not which layer the code is in. This
task takes two creator-facing pages and the three `VendorAccessService` methods
only those pages call. `T-091` keeps the grant itself and everything a provider
task calls into: the ensure step, `verify()`, the revokes, `attach()`,
`reconnected()`, `stateFor()`, `grantFor()`, `providersNeededBy()`, `handles()`
and `checkEpisode()`.

**`checkNow()` and the Peer's Check again are gone, and the argument this task
had about them is spent.** The first reading of the split put Check again here,
as a creator surface. This file argued the other way on 20 September 2026 — that
the button is a Peer's, because it lives inside the notice on
`resources/js/pages/shared/Show.vue`, posts `shared.access.check` through
`AccessCheckController` and reads `lang/en/shared.php` — and so left it in
`T-091`. The stream owner's answer the same day was that it is neither task's,
because it should not exist: `D-040` made Open the way a grant is retried, and
Check again was a second mechanism for the same thing. `checkNow()`,
`PEER_CHECK_SECONDS`, `scopeRecheckable()`, `AccessCheckController`, the
`shared.access.check` route, the `shared.vendor_notice.opened` key with its
three Check-again siblings, the four `shared.vendor_notice.next_attempt.*` lines
and `T-091`'s cases 25 and 42 to 45 were deleted rather than moved. Nothing
arrives here from that argument, and nothing anywhere in this file assumes
`checkNow()` exists.

**`impactOf()` comes here, so `T-091`'s `attach()` must stop calling it.** This
is the one change the cut forces in the task above, and it is not optional:
`T-091`'s replace branch reads `impactOf($old)` to learn which Episodes to check
inline, and this task depends on `T-091`, so a call the other way round is a
cycle. What `attach()` actually needs is the Episode list — the Series'
Episodes whose `provider->connection()` is the container's provider — which is a
query, not a Data shape, and `attach()` can read it directly. The creator-facing
counts and the dialog's copy are what `ContainerChangeImpact` exists for, and
nothing in `attach()` reads either.

**`ContainerChangeImpact` is `T-091`'s class, cited here and not re-declared.**
It is declared once, in `T-091`, which instantiates it nowhere; this task is its
first caller. Its `kind()` answers `'meeting'` for Zoom and Teams and `'folder'`
for every other container provider, and the controller builds the dialog's copy
from `series.container_change.{kind}.*`. Every container this task produces an
impact for is a folder — `D-024` holds the live-session containers until they
fit a per-Episode join link, so the eight `series.container_change.meeting.*`
lines and `T-091`'s case 60 go to `T-100` and `T-101` — so `folder` is the only
value that reaches this task's props, its dialog and its tests. **That is a fact
about what this task produces, not a limit on what the method answers**, and
writing `folder` into the key at the call site instead of calling `kind()` would
turn the one into the other and make `T-100` edit this dialog. The two must not
be conflated anywhere in this file.

**`MANUAL_RETRY_SECONDS` is declared here; `MANUAL_RETRY_LIMIT` stays in
`T-091`.** The throttle has exactly one caller, `IntegrationsController::retry()`,
which is this task's. The limit no longer bounds Try again now at all: `F08`
made every entry point spend `REQUEST_DEADLINE_SECONDS`, and what
`MANUAL_RETRY_LIMIT` bounds now is the inline Episode checks `attach()` runs
after a replace, which is `T-091`'s. Both constants sit on `VendorAccessService`,
which `T-091` creates and this task edits, so nothing moves file.

**Try again now spends the deadline and counts nothing.** It is bounded by
`REQUEST_DEADLINE_SECONDS` (`F08`), not by `MANUAL_RETRY_LIMIT`, and it reaches
a `needs_creator` row whatever its target — an item grant with no container
included, which is what `F10` found the older wording excluded. `T-091` said
both things two ways when this task was cut out of it: its Decisions and
Acceptance bound the work by the deadline, its `retryNeedingCreator()` docblock
still bounded it by `MANUAL_RETRY_LIMIT` and still required "an active Access
with a container". This task takes the Decisions and Acceptance, which are the
later text and the ones `F08` and `F10` were written into, and the docblock
reproduced under **Code** below is written that way. Whether `T-091`'s own copy
of it still disagrees is listed under **Before this can be ready**, dated, so
nobody resolves it by guessing.

**No vendor is called to draw the Integrations page, including for a row the
creator is about to retry.** The page already refuses to let a vendor take it
down — no section calls its provider to render (`R-004`) — and the same rule
holds for the three lists: they are reads of `vendor_grants` and
`series_containers`. A page that quietly retried on load would also make the
counts untrue by the time the creator finished reading them. Retrying is a POST
the creator presses, and `D-040`'s rule that nothing retries on its own is not
weakened by the page that lists what needs retrying.

**An `attempting` row is on none of these lists and marks nothing.** `F01` added
the eighth state for a create whose answer never arrived, so the vendor may hold
a permission Qori cannot name. It is not a state the creator can act on: there
is no setting to fix and no reason to show, and the row resolves itself the next
time that Peer presses Open, where `checkGrant()` asks the vendor what it
actually has. Listing it would put a row on a page headed "could not let in"
that the creator can do nothing about and that may already be granted. So the
grants list is `needs_creator` alone, the removals list is `revoke_failed`
alone, and the Peer-list marker is set for `needs_creator` alone. This is
written out beside each list rather than left to be inferred from the enum.

**A failed removal is retried one row at a time; a refused grant is retried a
provider at a time.** The grants list is one fault — a policy, an expired token,
a folder that moved — applied to many Peers, so one button fixes all of them
once the creator has changed the thing. A failed removal is one permission on
one file with its own reason, and the creator may want one gone and not another;
it is also the only action on this page that takes something away from somebody,
which is not a thing to do twenty at a time behind one click. So Try again now
takes `{provider}` and Try again on a removal takes `{grantId}` — ids are for
acting (`CLAUDE.md`).

**The removals list reuses `connections.grants.reasons.*`.** One `ErrorCode`
can serve many lang keys, and `connection_unusable` reads the same whether Qori
could not add somebody or could not take them off. One line is added rather than
reused: a revoke the deadline never reached carries `ERROR_TIMEOUT`, and
`reasons.other` ("the account refused the request") would be a lie about it, so
`reasons.timeout` says Qori did not get an answer and does not know.

**The three lists are three flat props keyed by the provider's stored value.**
`Integrations.vue` renders one `ProviderSection` per entry of `providers`, keyed
by the stored value (`google_drive`), and passes each list into that section's
`#grants` slot. Three maps read at the call site are cheaper than teaching
`App\Support\ProviderSections` about grants, which would put a `vendor_grants`
query inside a support class that today reads `connections` alone and is also
used by setup.

**Every URL in those props is built server-side**, as `beginUrl` already is
(`app/Support/ProviderSections.php:212`). The entry's key is the stored value and
the route takes `ConnectionProvider::slug()`, so a URL assembled in Vue from the
key is a 404 (`D-033`). The repick list's URL is the **Qori Series page**, not
`series_containers.url`: its copy says "Open each one and pick again", and the
place to pick again is the Series, not the folder in the creator's account.

**Two of `T-091`'s lines are re-written, because `D-040` made them untrue.**
`connections.grants.intro` and `connections.grants.retried` both promise that
Qori keeps trying on its own. Nothing does any more. The replacements say what is
actually true — a reconnect retries at once, and otherwise the next Open by that
person is the retry — because a creator told "Qori keeps trying" who comes back
tomorrow to the same list has been lied to by the product.

**The dialog ships rendered by nothing, and that is a deliberate exception to
`PLAN.md`'s first execution rule.** Every control that opens
`ContainerChangeDialog` belongs to a provider task — `T-094`'s folder panel,
which `T-096` and `T-098` extend, `T-100`'s `PickMeeting`, `T-101`'s
`TeamsMeeting` — and five tasks open the same dialog. Building it inside
whichever provider lands first would make the other four depend on that
provider; building it here makes them depend on this. What is tested here is the
prop and the copy, and the first walked journey through the dialog is `T-094`'s.

## Preconditions

`T-091` done, so `series_containers` and `vendor_grants` exist with their
models, `VendorGrantStatus` (eight cases since `F01` added `attempting`, with
`needs_creator` and `revoke_failed` among them), `SeriesContainerStatus::Repick`,
`GrantTarget`, `App\Data\ContainerChangeImpact`,
`VendorAccessService` with `REQUEST_TIMEOUT_SECONDS = 6`,
`REQUEST_DEADLINE_SECONDS = 12`, `MANUAL_RETRY_LIMIT = 12`, `attempt()`,
`freshConnectionFor()` and `revokeFor()`, the `GrantsPeerAccess` contract, the
two factories and the fake `tests/Doubles/GrantsEveryPeer.php`.

`T-044` is already done, so `lang/en/connections.php`,
`connections.providers.<provider>.name` keyed by the **stored value** (not the
slug), the `{provider}` slug binder and `ProviderSection.vue`'s `#grants` slot
(`resources/js/components/share/ProviderSection.vue:421`) are in the tree.

`php artisan wayfinder:generate --with-form` before anything reads
`resources/js/routes`: it is generated and gitignored, and `Integrations.vue`
posts through it.

**Data this task verifies against:** a clean database. Every case builds its own
Group, Series, Access, container and grant rows through `T-091`'s factories; the
three lists, the Peer-list marker and the impact are local reads, so no state
has to be reached through a vendor.

**Equipment:** none. Everything here is verified from the terminal against the
fake.

**Spike:** none owed. No vendor payload is named: `last_error_code` is opaque to
this task, and each provider task adds its own
`connections.grants.reasons.<vendor slug>` lines from its own fixture under
`tests/Fixtures/<vendor>/`.

## Scope

**In:**

- The three lists inside each provider section on the Integrations page: the
  grants that need the creator (`needs_creator` rows), the people Qori could not
  remove (`revoke_failed` rows, `D-040`), and the containers to pick again
  (`repick` containers). An `attempting` row is on none of the three — see
  Decisions.
- Try again now, per provider and throttled (`D-021`); Try again on one failed
  removal, per row.
- `VendorAccessService::retryNeedingCreator()`, `retryRemoval()` and
  `impactOf()`, and the `MANUAL_RETRY_SECONDS` throttle.
- `App\Data\GrantRetryTally`, new here, and the first calls to
  `App\Data\ContainerChangeImpact`, which `T-091` declares. Every impact this
  task produces is a folder; the class is not re-declared or edited here.
- **A Peer whose grant never landed is marked on the Series' Peer list too**,
  settled by the owner on 20 September 2026 in answer to `T-091`'s open
  question "should grants needing the creator also appear on the Series' Peer
  list, or is the Integrations page enough?" — both, and it is this task's to
  build. The Integrations page stays where it is fixed; the Series page is
  where a creator notices it, because that is the page they open to see who has
  access. One more field, `grantNeedsYou`, on each row of
  `SeriesController::peers()`
  (`app/Http/Controllers/Share/SeriesController.php:418`), whose shape today is
  `id`, `name`, `email`, `grantedAt`, `wasPaid`. It is the resolved
  `series.peers.grant_needs_you` line when any grant on that Access is
  `needs_creator`, and null otherwise — including for an `attempting`,
  `pending` or `awaiting_*` row, which nobody needs to act on, and for a Series
  whose Episodes need no grant at all. A `revoke_failed` row never marks
  anything here, because `peers()` reads active Accesses alone and a removal
  that failed is a removal whose Access is already gone.
- The marker's one line on the Peer list row in
  `resources/js/pages/share/series/Show.vue` (`:786-802`), and the field on its
  `PeerSummary` interface (`:84-90`).
- The `containerImpact` prop on the creator's Series page and
  `ContainerChangeDialog.vue`, which this task builds and does not render.
- The creator-facing copy for all of it, in `lang/en/connections.php` and
  `lang/en/series.php`.
- `docs/flows/vendor-access.md` and a `docs/tinker/connections.md` recipe.

**Out:**

- Everything a Peer sees: the `vendor` prop and its notice,
  `lang/en/shared.php`, the disabled Open control and `VendorLink::blocked()` —
  all `T-091`'s. **Check again, `checkNow()`, `AccessCheckController`,
  `PEER_CHECK_SECONDS`, `scopeRecheckable()` and `shared.access.check` are not
  merely out of scope but gone**, dropped by the stream owner on 20 September
  2026: `D-040`'s case for granting at Open was one way in with no second
  mechanism, and Check again was the second mechanism. Nothing in this file
  names them as live; where they appear it is as history, dated, under
  Decisions and Notes.
- The grant itself and everything under it: the two tables, the enums, the
  `GrantsPeerAccess` contract, the ensure step, `verify()`, `record()`,
  `revokeFor()`, `revokeItem()`, `attach()`, `reconnected()`,
  `ResumeGrantsAfterReconnect`, `checkEpisode()` and `MANUAL_RETRY_LIMIT` —
  `T-091`.
- The meeting half: the eight `series.container_change.meeting.*` lines, the
  dialog's meeting copy and `T-091`'s case 60 — `T-100` and `T-101`, held by
  `D-024`. `kind()` already answers `meeting` for Zoom and Teams in `T-091`'s
  class and this task does not change that; no container it produces an impact
  for is one, so nothing it builds ever reads a meeting line.
- The controls that open `ContainerChangeDialog` and post the replace or the
  remove: the folder panel and its pickers (`T-094`, `T-096`, `T-098`), and the
  meeting pages (`T-100`, `T-101`).
- The per-provider `series.container.<provider>.change.replace` and `.remove`
  notes, which the dialog renders when `Lang::has()` finds them; each provider
  task writes its own.
- Any email about a refused grant or a failed removal. Nothing is emailed for
  either; the only mail in this area is `T-044`'s reconnect notification.
- Retrying a `revoke_failed` row automatically when the creator opens the page —
  see Decisions, and the open question below.
- Anything the marker on the Peer list might do beyond saying so: no button, no
  retry and no link out of the row. Try again now stays on the Integrations
  page, which is where the account it needs is connected.

## Files

| Path                                                      | Change | Notes                                                                                                                      |
| --------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| `app/Data/GrantRetryTally.php`                            | new    | What Try again now did                                                                                                     |
| `app/Services/VendorAccessService.php`                    | edit   | `retryNeedingCreator()`, `retryRemoval()`, `impactOf()` and `MANUAL_RETRY_SECONDS`; `T-091` creates the class              |
| `app/Http/Controllers/Share/IntegrationsController.php`   | edit   | Three props on `show()` (`:31-84`); `retry()` and `retryRemoval()`; `PaymentsService` stays the constructor dep (`:29`)    |
| `app/Http/Controllers/Share/SeriesController.php`         | edit   | `containerImpact` on `show()` (`:140`), by method injection as `ProgressService` is; `grantNeedsYou` on `peers()` (`:418`) |
| `routes/share/payments.php`                               | edit   | The two routes, beside `settings.integrations` (`:22-23`)                                                                  |
| `resources/js/pages/share/settings/Integrations.vue`      | edit   | The three lists in each section's `#grants` slot (`:277-283`); Try again now; Try again on a removal                       |
| `resources/js/pages/share/series/Show.vue`                | edit   | The marker on the Peer list row (`:786-802`) and its `PeerSummary` interface (`:84-90`)                                    |
| `resources/js/components/share/ContainerChangeDialog.vue` | new    | Renders one `containerImpact` entry before a replace or a remove; nothing opens it yet                                     |
| `lang/en/connections.php` `lang/en/series.php`            | edit   | Copy below; `connections.php` is `T-044`'s file                                                                            |
| `tests/Feature/Share/IntegrationsGrantsTest.php`          | new    | 8 cases: the three lists, Try again now, and a failed removal retried                                                      |
| `tests/Feature/Share/ContainerImpactTest.php`             | new    | 4 cases: the impact, the Series page's two props                                                                           |
| `docs/flows/vendor-access.md`                             | edit   | `T-091` writes it; the two creator actions and the impact read join it                                                     |
| `docs/tinker/connections.md`                              | edit   | A recipe beside "What the page would show" (`:357`): rows in each state, and the two retries                               |

`app/Data/ContainerChangeImpact.php` is deliberately not a row: `T-091` declares
it and this task is its first caller, so claiming the file here would be one
path claimed by two tasks for a change only one of them makes. Its shape is
reproduced under **Code** for the reader.

Flows: `docs/flows/vendor-access.md` above. It is `T-091`'s new file and this
task adds the creator's end of the same chain to it, rather than starting a
second document about one service.

## Database

None. Every column the three lists and the Peer-list marker read — `status`,
`last_error_code`, `next_attempt_at`, `principal`, `provider`,
`external_target_id`, `vendor_ref`, `access_id`, `episode_id`,
`series_container_id`, `updated_at` — is `T-091`'s, and `impactOf()` counts rows
that already exist.

"When it was tried" on the removals list is the row's `updated_at`: the only
writes a `revoke_failed` row ever takes are attempts at it, so the two mean the
same thing and a column of its own would only be a second copy to keep in step.

## Code

```php
namespace App\Data;

/** What Try again now did (D-021). */
class GrantRetryTally
{
    public function __construct(public int $letIn, public int $waiting) {}
}
```

`App\Data\ContainerChangeImpact` is `T-091`'s, declared there once and
instantiated nowhere in it; this task is its first caller and neither
re-declares nor edits it. Its shape, quoted from `T-091` so the calls below can
be read without opening it:

```php
namespace App\Data;

/**
 * What replacing or removing one container touches (D-021). Local reads only: no vendor
 * is called to draw a dialog, so a provider that is down cannot stop a creator changing
 * their own Series.
 */
class ContainerChangeImpact
{
    /** @param list<array{id: string, title: string}> $episodes the Series' Episodes on $provider, in the Series' order */
    public function __construct(
        public ConnectionProvider $provider,
        public int $peers,
        public array $episodes,
    ) {}

    /**
     * Which series.container_change.{kind}.* lines apply: 'meeting' for Zoom and Teams,
     * 'folder' for every other container provider.
     */
    public function kind(): string;
}
```

Every impact this task builds is a folder, so `folder` is the only value its
props, its dialog and its tests ever see. That is what this task produces, not
what the method answers: nothing here writes `folder` into the key at the call
site, and `T-100` and `T-101` add the `meeting` lang block and the journeys that
reach it without editing the class, the controller or the dialog.

```php
// App\Services\VendorAccessService — what this task adds to T-091's class.

/** A creator's Try again now waits this long between presses, per Group and provider. Provisional. */
public const MANUAL_RETRY_SECONDS = 60;

/**
 * Try again now (D-021), in the current Group. Selects on (group_id, status) and the row's own
 * provider, reading its own external_target_id: no container is joined and container.series is not
 * eager-loaded, because F10 found that requiring "an active Access with a container" excluded every
 * Google Drive item grant. A grant's Series is reached through its Access, which both target kinds
 * have. needs_creator rows only — an attempting row is left alone for the Peer's next Open (F01).
 * next_attempt_at now on every row it selects, then attempt() on the oldest by created_at until
 * REQUEST_DEADLINE_SECONDS is spent; MANUAL_RETRY_LIMIT does not bound this (F08). The rest are
 * left due, and the Peer's next Open takes them (D-040). letIn counts the rows now granted or
 * awaiting_acceptance: the vendor has taken them, whatever the Peer has left to do. waiting counts
 * every other row the press touched, attempted and unreached alike, because "still waiting" is true
 * of both. Never throws. The caller throttles by MANUAL_RETRY_SECONDS.
 */
public function retryNeedingCreator(ConnectionProvider $provider, int $deadlineSeconds = self::REQUEST_DEADLINE_SECONDS): GrantRetryTally;

/**
 * The creator's Try again on one failed removal (D-040): one more call, for that row alone. The
 * same path revokeFor() takes for a single row, so none of its rules is re-stated here — the
 * shared-permission count on (provider, external_target_id, principal) under the target lock (F02),
 * freshConnectionFor(), then revoke(). Success sets revoked and revoked_at; failure leaves the row
 * revoke_failed with a fresh last_error_code and updated_at, and nothing retries it afterwards.
 * A row that is not revoke_failed is left untouched and answers RevokeResult::revoked() when it is
 * already revoked. Never throws.
 */
public function retryRemoval(VendorGrant $grant, int $deadlineSeconds = self::REQUEST_DEADLINE_SECONDS): RevokeResult;

/**
 * Local reads only, no vendor call: the active Accesses on the container's Series, and that Series'
 * Episodes whose provider->connection() is the container's provider, in the Series' order.
 */
public function impactOf(SeriesContainer $container): ContainerChangeImpact;
```

`IntegrationsController::show()` adds three props, each keyed by the provider's
stored value so `Integrations.vue` can hand one entry to the matching section,
and each absent rather than empty when that provider has nothing (an entry is
written only when its rows are non-empty, except `grantsNeedingCreator`, which is
written for every connected provider so `none` and Try again now have somewhere
to live). Every sentence goes through `Terminology` against the current Group.

```php
'grantsNeedingCreator' => [
    'dropbox' => [
        'title' => '…',                                  // connections.grants.title
        'intro' => '…',                                  // connections.grants.intro
        'none' => '…',                                   // connections.grants.none, when rows is empty
        'retryLabel' => '…',                             // connections.grants.retry
        'retryUrl' => '/g/acme/settings/integrations/dropbox/retry',
        'rows' => [
            // VendorGrant::query()->where('status', NeedsCreator)->with(['access.peer', 'access.user', 'access.series', 'episode'])
            // ->orderBy('created_at'); the Access is the way to the Series, because only one target has a container (F10).
            // NeedsCreator alone: pending, attempting and the two awaiting_* states are nobody's to act on, and an
            // attempting row may already be granted vendor-side until the Peer's next Open settles it (F01).
            ['name' => 'Ada Lovelace', 'series' => 'Sourdough', 'reason' => '…', 'next' => 'today at 14:05'],
        ],
    ],
],
'removalsUnresolved' => [
    'dropbox' => [
        'title' => '…',                                  // connections.removals.title
        'intro' => '…',                                  // connections.removals.intro
        'disconnected' => '…',                           // connections.removals.disconnected, or null when the connection isLive() (D-039)
        'rows' => [
            // VendorGrant::query()->where('status', RevokeFailed)->with(['access.peer', 'access.user', 'access.series', 'episode'])
            // ->orderBy('updated_at'); id is the row's, for the per-row retry. RevokeFailed alone: attempting is a
            // create whose answer never came, not a removal that failed, and it is on neither list (F01).
            [
                'id' => '01J…',
                'name' => 'Ada Lovelace',                // the Peer's name, else their email, else principal
                'where' => 'Starter, day three',         // the Episode's title on an item grant, the Series' title on a container grant,
                                                         // else connections.removals.gone when the Episode has been deleted
                'reason' => '…',                         // connections.grants.reasons.{last_error_code}, falling back to reasons.other with :code
                'tried' => 'yesterday at 09:12',         // updated_at in the Group's timezone
                'retryLabel' => '…',                     // connections.removals.retry
                'retryUrl' => '/g/acme/settings/integrations/removals/01J…/retry',
            ],
        ],
    ],
],
'containersToRepick' => [
    'dropbox' => [
        'title' => '…',                                  // connections.containers.repick.title
        'body' => '…',                                   // connections.containers.repick.body
        'rows' => [
            // SeriesContainer::query()->where('status', Repick)->with('series'); the URL is the Qori Series page,
            // where picking again happens, never series_containers.url.
            ['series' => 'Sourdough', 'url' => '/g/acme/series/sourdough'],
        ],
    ],
],
```

```php
// App\Http\Controllers\Share\IntegrationsController — both actions method-inject, as CLAUDE.md
// asks of per-action dependencies; PaymentsService stays the constructor dependency (:29).

public function retry(string $group, ConnectionProvider $provider, VendorAccessService $vendorAccess, CurrentGroup $current, Terminology $terminology): RedirectResponse;
// {provider} carries ConnectionProvider::slug() and T-044's binder turns it back into the case this
// action takes (D-033): an unknown slug, or the stored value with its underscore, is a 404.
// $key = 'vendor-grants-retry:'.$current->get()->getKey().':'.$provider->value;
// RateLimiter::tooManyAttempts($key, 1) → $seconds = RateLimiter::availableIn($key);
//   toast info $terminology->choice('connections.grants.retry_wait', $seconds, ['seconds' => $seconds]); no call
// else RateLimiter::hit($key, VendorAccessService::MANUAL_RETRY_SECONDS); $tally = $vendorAccess->retryNeedingCreator($provider);
//   toast success connections.grants.retried, ['let_in' => $tally->letIn, 'waiting' => $tally->waiting,
//   'provider' => connections.providers.{provider->value}.name]
// return to_route('share.settings.integrations', ['group' => $current->get()->slug]);   // $current, not $group

public function retryRemoval(string $group, string $grantId, VendorAccessService $vendorAccess, CurrentGroup $current, Terminology $terminology): RedirectResponse;
// $grant = VendorGrant::query()->findOrFail($grantId);   // BelongsToGroup scopes it to the current Group, so
//   another Group's id is a 404 rather than a refusal that confirms the row exists.
// abort_if($grant->status !== VendorGrantStatus::RevokeFailed, 404);   // the only rows this page offers it on
// $result = $vendorAccess->retryRemoval($grant);
//   toast success connections.removals.retried when $result->revoked, else toast info
//   connections.removals.retry_failed, ['reason' => the same reasons.* line the row shows]
// return to_route('share.settings.integrations', ['group' => $current->get()->slug]);
// No RateLimiter: one row, one call, and a second press is one more vendor call on one permission.
// Toasts are Inertia::flash('toast', [...]) as everywhere (SeriesLifecycleController.php:51-54, :61).
```

`SeriesController::show()` (`app/Http/Controllers/Share/SeriesController.php:140`)
takes `VendorAccessService` by method injection, as it takes `ProgressService`,
and adds `'containerImpact'`: null when the Series has no `active` container,
else keyed by provider value, one entry per `active` container from `impactOf()`.
A `missing` or `repick` container gets no entry — it is being fixed rather than
changed, and its own panel says why. Each entry is:

```php
[
    'provider' => 'dropbox',
    'kind' => 'folder',
    'peers' => 2,
    'episodes' => [['id' => '01J…', 'title' => 'Starter, day three']],
    // The shape IntegrationsController::show() already gives Stripe's disconnect dialog (:76-83).
    'copy' => [
        'replace' => ['title' => '…', 'peers' => '…', 'episodes' => '…', 'note' => null, 'confirm' => '…'],
        'remove' => ['title' => '…', 'peers' => '…', 'episodes' => '…', 'note' => null, 'confirm' => '…'],
        'keep' => '…',
    ],
]
```

from `series.container_change.{kind}.*`. `title` and `confirm` go through
`Terminology::line()`; `peers` and `episodes` through `Terminology::choice()`
with the count of Peers or of Episodes, as `payments.disconnect_priced` is
(`IntegrationsController.php:80`); `:vendor` is
`connections.providers.{provider->value}.name`. `note` is
`series.container.{provider}.change.{action}` through `Terminology::line()` when
`Lang::has()` finds it, else null — so a fact true of one provider alone is that
provider task's line and no provider task edits the dialog.

`SeriesController::peers()` (`:418`) adds `'grantNeedsYou'` to each row it
builds, beside `wasPaid`. It is private and becomes
`peers(Series $series, Terminology $terminology): array` — `show()` already
injects `Terminology` (`:145`) and hands it down. No vendor is called and no
service is involved: this is a read of `vendor_grants` on the model, as
`CLAUDE.md` allows.

```php
// One more field on the row, from the grant states T-091 writes:
'grantNeedsYou' => $needsCreator->has((string) $access->getKey())
    ? $terminology->line('series.peers.grant_needs_you')
    : null,
// $needsCreator is one read for the whole page, taken before the map from the keys of the
// Accesses peers() has already loaded (:422-426), so the list costs one query however long it is:
// VendorGrant::query()->whereIn('access_id', $accessIds)->where('status', VendorGrantStatus::NeedsCreator)
//   ->pluck('access_id')->flip();
// NeedsCreator alone (F01): an attempting, pending or awaiting_* row marks nothing, because nobody
// can act on one and the Peer's next Open settles it. A revoke_failed row cannot appear here at all —
// peers() reads active Accesses (:422-425) and a failed removal's Access is already gone.
```

The field carries the resolved sentence rather than a boolean, because
`Show.vue` may not add English of its own (`CLAUDE.md`); the page renders it
when it is set and nothing when it is null. It is one line beneath the email
line, not another `·` fragment on it, because it is an instruction to the
creator and the rest of that line is facts about the Peer.

`ContainerChangeDialog.vue` takes one `containerImpact` entry and
`action: 'replace' | 'remove'`, with `open` as a model, and renders the `dialog`
primitives from `resources/js/components/ui/dialog` as the Series page's archive
dialog does (`resources/js/pages/share/series/Show.vue:938-963`): the title, the
Peers sentence, the Episodes sentence with the Episode titles listed beneath it
(nothing listed when there are none), the `note` when it is set, Confirm and
Keep. A `peers` or `episodes` sentence that is null is not rendered, which is
what lets `T-101` build an entry with no Episodes sentence. It emits `confirm`
and posts nothing itself; the panel that opened it posts the replace or the
remove.

## Copy

| Key                                               | File                      | English                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `connections.grants.title`                        | `lang/en/connections.php` | :peer_plural your account could not let in                                                                                                                                                                                                                                                                                                                                                                                        |
| `connections.grants.intro`                        | `lang/en/connections.php` | These :peer_plural have access to the :series, but your account could not add them. The reason is beside each name. Fix it, then try again now — Qori also tries again as soon as you reconnect the account, and the next time one of them opens it.                                                                                                                                                                              |
| `connections.grants.row`                          | `lang/en/connections.php` | :name on :series — :reason. Next try :next.                                                                                                                                                                                                                                                                                                                                                                                       |
| `connections.grants.reasons.connection_unusable`  | `lang/en/connections.php` | your account is disconnected or its access has expired; reconnect it                                                                                                                                                                                                                                                                                                                                                              |
| `connections.grants.reasons.container_missing`    | `lang/en/connections.php` | what this :series holds can no longer be found in your account; pick it again                                                                                                                                                                                                                                                                                                                                                     |
| `connections.grants.reasons.container_repick`     | `lang/en/connections.php` | what this :series holds was picked with the account you replaced; pick it again                                                                                                                                                                                                                                                                                                                                                   |
| `connections.grants.reasons.item_missing`         | `lang/en/connections.php` | the file this :episode uses can no longer be found in your account                                                                                                                                                                                                                                                                                                                                                                |
| `connections.grants.reasons.item_repick`          | `lang/en/connections.php` | the file this :episode uses belongs to the account you replaced; choose it again on the :series                                                                                                                                                                                                                                                                                                                                   |
| `connections.grants.reasons.timeout`              | `lang/en/connections.php` | your account did not answer in time, so Qori does not know whether it worked                                                                                                                                                                                                                                                                                                                                                      |
| `connections.grants.reasons.other`                | `lang/en/connections.php` | the account refused the request (:code)                                                                                                                                                                                                                                                                                                                                                                                           |
| `connections.grants.none`                         | `lang/en/connections.php` | Everyone with access has been let in.                                                                                                                                                                                                                                                                                                                                                                                             |
| `connections.grants.retry`                        | `lang/en/connections.php` | Try again now                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `connections.grants.retried`                      | `lang/en/connections.php` | Tried again just now: :let_in let in, :waiting still waiting. If you changed a setting in :provider, it can take a few hours to apply — try again then, and Qori also tries whenever one of them opens the :series.                                                                                                                                                                                                               |
| `connections.grants.retry_wait`                   | `lang/en/connections.php` | `{1} You tried a moment ago. You can try again in a second.\|[2,*] You tried a moment ago. You can try again in :seconds seconds.`                                                                                                                                                                                                                                                                                                |
| `connections.removals.title`                      | `lang/en/connections.php` | :peer_plural Qori could not take off                                                                                                                                                                                                                                                                                                                                                                                              |
| `connections.removals.intro`                      | `lang/en/connections.php` | These :peer_plural no longer have access in Qori, but your account would not let Qori remove what it had given them, so they can still open it. The reason is beside each name. Nothing happens on its own here: fix the reason, then try each one again.                                                                                                                                                                         |
| `connections.removals.row`                        | `lang/en/connections.php` | :name on :where — :reason. Last tried :tried.                                                                                                                                                                                                                                                                                                                                                                                     |
| `connections.removals.gone`                       | `lang/en/connections.php` | something you have since deleted                                                                                                                                                                                                                                                                                                                                                                                                  |
| `connections.removals.disconnected`               | `lang/en/connections.php` | Qori needs this account connected again before it can take anybody off. Nothing below can be tried until then.                                                                                                                                                                                                                                                                                                                    |
| `connections.removals.none`                       | `lang/en/connections.php` | Everyone Qori let in and then took off is off.                                                                                                                                                                                                                                                                                                                                                                                    |
| `connections.removals.retry`                      | `lang/en/connections.php` | Try again                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `connections.removals.retried`                    | `lang/en/connections.php` | Taken off. They can no longer open it from your account.                                                                                                                                                                                                                                                                                                                                                                          |
| `connections.removals.retry_failed`               | `lang/en/connections.php` | Still not taken off: :reason. They keep what your account gave them until this works.                                                                                                                                                                                                                                                                                                                                             |
| `connections.containers.repick.title`             | `lang/en/connections.php` | Pick again with the account now connected                                                                                                                                                                                                                                                                                                                                                                                         |
| `connections.containers.repick.body`              | `lang/en/connections.php` | What these :series_plural hold was picked with the account you replaced, so Qori can no longer reach it. Open each one and pick again.                                                                                                                                                                                                                                                                                            |
| `series.container_change.keep`                    | `lang/en/series.php`      | Keep it as it is                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `series.container_change.folder.replace.title`    | `lang/en/series.php`      | Switch this :series to a different folder?                                                                                                                                                                                                                                                                                                                                                                                        |
| `series.container_change.folder.replace.peers`    | `lang/en/series.php`      | `{0} Nobody has access yet, so nobody moves.\|{1} One :peer with access moves to the new folder and is taken off this one in your :vendor account.\|[2,*] :count :peer_plural with access move to the new folder and are taken off this one in your :vendor account.`                                                                                                                                                             |
| `series.container_change.folder.replace.episodes` | `lang/en/series.php`      | `{0} No :episode_plural use files from this folder yet.\|{1} This :episode uses a file from this folder. After the switch Qori checks it against the new folder at once, and if its file isn't inside that folder, you'll need to pick it again.\|[2,*] These :episode_plural use files from this folder. After the switch Qori checks each against the new folder, and you'll need to pick again any file that isn't inside it.` |
| `series.container_change.folder.replace.confirm`  | `lang/en/series.php`      | Switch folder                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `series.container_change.folder.remove.title`     | `lang/en/series.php`      | Stop using this folder?                                                                                                                                                                                                                                                                                                                                                                                                           |
| `series.container_change.folder.remove.peers`     | `lang/en/series.php`      | `{0} Nobody has access yet, so nobody is taken off it.\|{1} One :peer with access is taken off this folder in your :vendor account.\|[2,*] :count :peer_plural with access are taken off this folder in your :vendor account.`                                                                                                                                                                                                    |
| `series.container_change.folder.remove.episodes`  | `lang/en/series.php`      | `{0} Your files stay where they are.\|{1} Your files stay where they are. This :episode can't be opened until you choose a folder again.\|[2,*] Your files stay where they are. These :episode_plural can't be opened until you choose a folder again.`                                                                                                                                                                           |
| `series.container_change.folder.remove.confirm`   | `lang/en/series.php`      | Stop using it                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `series.peers.grant_needs_you`                    | `lang/en/series.php`      | Your account could not let them in — fix it under Integrations.                                                                                                                                                                                                                                                                                                                                                                   |

Every line above is `T-091`'s except `connections.removals.*`,
`connections.grants.reasons.timeout`, the re-written `grants.intro` and
`grants.retried` — see Decisions for why those two changed — and
`series.peers.grant_needs_you`, which is new with the marker the owner settled
on 20 September 2026. The marker names no vendor: an Access can hold grants on
more than one provider, and the page that names the account is the one the line
sends the creator to.

`:vendor` and `:provider` are `connections.providers.<provider>.name`, keyed by
the **stored value** (`google_drive`, with the underscore), not by `slug()`.
`:seconds` is `RateLimiter::availableIn()`, never a restated constant.
`:next` and `:tried` are in the Group's timezone. The `{0}`/`{1}`/`[2,*]` lines
go through `Terminology::choice()`, counting Peers, Episodes or seconds, as
`series.archive_confirm` does (`lang/en/series.php:108`). The removals copy
names what Qori changes and never claims to touch the creator's file: it is
permissions Qori created, and only those (`D-038`).

Provider tasks add `connections.grants.reasons.<vendor slug>` lines for the codes
they observe, and `series.container.<provider>.change.replace` or `.remove` for a
fact that is theirs alone, which the dialog shows as its note.

## Routes

| Verb | Path                                                        | Name                                        | Action                                       |
| ---- | ----------------------------------------------------------- | ------------------------------------------- | -------------------------------------------- |
| POST | `/g/{group}/settings/integrations/{provider}/retry`         | `share.settings.integrations.retry`         | `Share\IntegrationsController::retry`        |
| POST | `/g/{group}/settings/integrations/removals/{grantId}/retry` | `share.settings.integrations.retry-removal` | `Share\IntegrationsController::retryRemoval` |

Both sit beside `settings.integrations` in `routes/share/payments.php:22-23`,
inside the sharing group. `{provider}` carries `ConnectionProvider::slug()`, so
Google Drive's retry posts to `…/integrations/google-drive/retry`, and `T-044`'s
binder turns the slug back into the case the action takes (`D-033`); an unknown
slug, or the stored value with its underscore, is a 404. `{grantId}` is the
grant's ULID, because a `POST` takes the model id and the page submitting
already holds it. The path stays lowercase and hyphen-free (`D-033`); the route
**name** keeps its hyphen, which is the codebase's own habit for a two-word
segment (`magic-link.store`, `series.sign-in`, `two-factor.setup`).

The creator's Series page is `share.series.show`
(`routes/share/series.php:26`) and gains a prop, not a route.

## Tests

Both files bind `T-091`'s fake with
`$this->app->when(VendorAccessService::class)->needs('$providers')->give(fn () => [$this->fake])`
and call `Http::fake()`; the fake makes no HTTP call and records each call with
the timeout and the connection it was given. Every case acts as the Group's
owner through the sharing routes.

**The case numbers are `T-091`'s and none is renumbered** — other drafts cite
them. `T-091` numbers every case in every one of its files from one sequence,
1 to 80; 46 to 51 are retired, and 25 and 42 to 45 went with Check again on
20 September 2026 and are not reused. The numbers below are this task's share of
that sequence — 52 to 59, and 76 and 77 — so they are not contiguous and are
written beside each case rather than as list markers. One case is genuinely new
here and takes **82**, one past `T-091`'s highest, which its own consolidation pass took to 81.

**New: `tests/Feature/Share/IntegrationsGrantsTest.php` — 8 cases**

- **52** `test_the_integrations_page_lists_grants_needing_the_creator_under_their_provider`
  — a `pending` row is not listed, and neither is an `attempting` one (`F01`);
  `retryLabel` is `connections.grants.retry` and `retryUrl` carries the
  provider's slug, not its stored value.
- **53** `test_the_integrations_page_lists_containers_to_pick_again` — the
  entry's `url` is the Qori Series page, never `series_containers.url`.
- **54** `test_another_groups_rows_are_not_shown` — grants, removals and repick
  containers alike.
- **55** `test_try_again_now_retries_the_providers_rows_and_reports_the_counts`
  — two `needs_creator` Dropbox rows, the fake grants one and refuses the other;
  POST `share.settings.integrations.retry` with `dropbox`; redirect to
  `share.settings.integrations`; toast `connections.grants.retried` with
  `:let_in` 1 and `:waiting` 1. A third row on an **item** target with no
  container is attempted too — `F10`'s query would have excluded it.
- **56** `test_a_second_try_inside_the_throttle_calls_nothing_and_says_when` —
  two POSTs: the fake's calls do not grow; the second toast is
  `connections.grants.retry_wait`; the throttle is per provider, so a POST for
  another provider still runs.
- **57** `test_try_again_now_leaves_another_groups_rows_alone` — a
  `needs_creator` row in a second Group keeps its `next_attempt_at` and sees no
  call.
- **76** `test_the_integrations_page_lists_the_people_qori_could_not_remove` —
  new: a `revoke_failed` row shows the Peer, the Episode title, the reason and
  when it was last tried; a row whose Episode has been deleted shows
  `connections.removals.gone`; `disconnected` is set when the provider's
  connection is not `isLive()` and null when it is (`D-039`); a `revoked` row is
  absent, and so is an `attempting` one (`F01`).
- **77** `test_try_again_on_a_failed_removal_calls_the_vendor_once_more` — new:
  POST `share.settings.integrations.retry-removal` with the grant's id; the
  fake's `revoke()` is called once, the row is `revoked` with `revoked_at`, and
  the toast is `connections.removals.retried`. Then a row the fake refuses:
  still `revoke_failed`, a fresh `updated_at`, toast
  `connections.removals.retry_failed`, and nothing retries it afterwards. Then a
  `granted` row's id and another Group's row's id: 404 each, zero calls.

`T-091` says this file has eight cases and numbers six of them, 52 to 57. The
two it never wrote are the removals list and its retry, which `D-040` added to
the heading line and nowhere else; they take 76 and 77 rather than a guess at
which numbers were meant, because 58 and 59 are already `ContainerImpactTest`'s.

**New: `tests/Feature/Share/ContainerImpactTest.php` — 4 cases**

- **28** `test_impact_counts_active_peers_and_lists_the_episodes_on_the_containers_provider`
  — `T-091`'s case 28, which travels with `impactOf()` from
  `tests/Feature/Access/VendorAccessTest.php` to this file, **minus its Zoom
  half**: two active Accesses and one revoked gives `peers` 2; the Dropbox
  Episodes in the Series' order with `id` and `title`, the Qori-hosted one
  absent; `kind()` is `folder`; zero vendor calls.
- **58** `test_the_series_page_sends_the_impact_of_changing_its_container` — a
  Dropbox container, two active Accesses, two Dropbox Episodes:
  `containerImpact.dropbox` has `kind` `folder`, `peers` 2, the two Episodes,
  and `copy.replace.peers` is the `[2,*]` branch of
  `series.container_change.folder.replace.peers` with `:vendor` filled;
  `copy.remove` and `copy.keep` present; `copy.replace.note` null, and set once
  a `series.container.dropbox.change.replace` line is registered with
  `addLines()`.
- **59** `test_the_series_page_sends_no_impact_without_an_active_container` — no
  container gives null; a `repick` container gives null; a `missing` container
  gives null.
- **82** `test_the_series_peer_list_marks_a_peer_whose_grant_needs_the_creator`
  — new with the owner's ruling of 20 September 2026: an Access with a
  `needs_creator` grant carries `grantNeedsYou` as the resolved
  `series.peers.grant_needs_you` line; an Access whose grants are all `granted`
  carries null, and so do Accesses whose grants are `attempting`, `pending` or
  `awaiting_acceptance` (`F01`), and a Series needing no grant at all; the rest
  of the row — `id`, `name`, `email`, `grantedAt`, `wasPaid` — is unchanged;
  zero vendor calls. It sits here rather than in a file of its own because this
  file is where the Series page's vendor-access props are asserted.

`T-091`'s case 60, `test_a_meeting_container_takes_the_meeting_lines`, is **not**
here: it goes to `T-100` with the `meeting` lang block (`D-024`), which is also
why case 28 sheds its Zoom assertion on the way. `kind()` is `T-091`'s and
already answers `meeting`; what `T-100` proves is that the dialog reads the
meeting lines, and no case here produces a meeting container to read them with.

Total: 12.

**Changed:**

- None expected. `IntegrationsController::show()` and `SeriesController::show()`
  gain props that existing assertions do not name, the Peer row gains a field
  rather than changing one, and both new actions are method-injected, so no test
  constructs either controller by hand. Nothing under `tests/Feature/Series/`
  asserts the Series page's `peers` prop today (checked 20 September 2026);
  `tests/Feature/Share/PeersPageTest.php` reads `share.peers.index`, a different
  page and a different shape. Confirm rather than assume for
  `tests/Feature/Share/IntegrationsPageTest.php` and
  `tests/Feature/Share/IntegrationsProvidersTest.php`.

## Acceptance

- [ ] Each provider section on the Integrations page lists this Group's grants
      needing the creator, the people Qori could not remove, and the containers
      to pick again — and nobody else's Group's; an `attempting` row is on none
      of the three, because nobody can act on one (`F01`)
- [ ] Every row names who, where and why, and a removal also names when it was
      last tried; a removal whose Episode has been deleted still appears, and
      says so
- [ ] Drawing the page calls no vendor and retries nothing (`R-004`, `D-040`)
- [ ] Try again now retries that provider's grants needing the creator whatever
      their target (`F10`), spends `REQUEST_DEADLINE_SECONDS`, leaves the rest
      due, is throttled per Group and provider, and reports the counts without
      promising that anything keeps trying (`D-021`, `D-040`)
- [ ] Try again on one failed removal calls the vendor once for that row alone,
      says whether the person is off, and never retries itself; a row that is
      not `revoke_failed`, or is another Group's, is a 404
- [ ] While the provider is disconnected the removals list says the account has
      to come back before anybody can be taken off (`D-039`)
- [ ] The creator's Series page sends `containerImpact` for each `active`
      container and nothing for a `missing` or `repick` one, and
      `ContainerChangeDialog` renders one entry — the Peers sentence, the
      Episodes sentence with the titles, the provider's note when it exists,
      Confirm and Keep (`D-021`)
- [ ] The Series' Peer list marks a Peer whose grant is `needs_creator` and
      marks nobody else, the mark says what to do about it, and the rest of the
      row is unchanged (the owner, 20 September 2026)
- [ ] Nothing this task builds produces a meeting: every impact it sends carries
      `kind()` `folder`, and the `meeting` lang block and `T-091`'s case 60 are
      left for `T-100` and `T-101`, which do not edit the class, the controller
      or the dialog to add them (`D-024`)
- [ ] `docs/flows/vendor-access.md` and the `docs/tinker/connections.md` recipe
      describe what was built
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **This cannot be `ready` before `T-091` is.** It consumes `T-091`'s states,
  columns, service, factories and fake, and `T-091` is a draft carrying its own
  re-draft on `D-040` plus a dozen open bullets. Nothing below can be settled
  ahead of it — the stream owner's, and it is the first of these.
- **`T-091` has to say one thing in one place about `retryNeedingCreator()`.**
  Read on 20 September 2026, before `T-091`'s own consolidation pass, its
  docblock required "an active Access with a container" — which `F10` found
  excludes every Google Drive item grant, the rows `D-036` created — and bounded
  the work by `MANUAL_RETRY_LIMIT`, where `F08` bounds it by
  `REQUEST_DEADLINE_SECONDS`; its Decisions and Acceptance said the opposite of
  both. This task's copy of the docblock, under **Code**, is written the later
  way. Check `T-091`'s against it once that pass has landed: if the pass
  corrected it, this bullet is spent — anyone's.
- **`T-091`'s `attach()` has to stop calling `impactOf()`.** See Decisions: the
  method comes here, this task depends on `T-091`, and a call the other way is a
  cycle. `attach()` needs the Episode list, not the Data shape. It is a
  three-line change in a task nobody has started — the stream owner's, in the
  same re-draft.
- **Five tasks depend on this one and three of them do not say so.** `T-094`,
  `T-096`, `T-098`, `T-100` and `T-101` each open `ContainerChangeDialog` and
  read `containerImpact`, and each cites both as `T-091`'s; `T-094` also cites
  `share.settings.integrations.retry` in its case 32. `blocks:` names `T-100`
  and `T-101`, whose `depends:` were re-pointed here with the cut. `T-094`,
  `T-096` and `T-098` still depend on `T-091` alone, and re-pointing them also
  decides whether this task or `T-091` is the one they wait on for the folder
  panel. The stream owner's.
- **What the removals list says when the permission was on an Episode that has
  since been deleted.** `T-091` left this open with a designer, and it is real:
  `episode_id` is `nullOnDelete` precisely so the row survives, and Qori is then
  holding a principal and a vendor id with no title to show. The provisional line
  is `connections.removals.gone` above — "something you have since deleted" —
  which is honest and slightly bleak. Anyone's, with a designer.
- **Whether a `revoke_failed` row should be retried when the creator opens the
  Integrations page**, which is demand-driven in the same sense Open is. This
  task says no and gives its reason under Decisions, but `T-091` raised it as an
  open question and the reversal is cheap — the owner's.
- **`connections.grants.row` still promises a time nothing keeps.** It ends
  "Next try :next", filled from `next_attempt_at`, and under `D-040` nothing
  tries at that time: the next attempt is that Peer's next Open, the creator's
  Try again now, or a reconnect. The column is still a real gate — an Open
  before the row is due does not attempt — so what is true is "not before", not
  "next try", and `connections.grants.intro` was re-written for exactly this
  reason and already says what does the retrying. Found on the consolidation
  pass of 20 September 2026 and left rather than reworded on the spot: it is a
  third `T-091` line `D-040` made untrue, and the two before it were re-written
  under Decisions with their reason rather than quietly. Anyone's, with a
  designer.
- **`MANUAL_RETRY_SECONDS` is provisional at 60.** With `T-093`'s timings — a
  permission create at 1.68 to 2.44 s and a delete at 1.14 to 1.74 s — a Try
  again now that spends twelve seconds fits comfortably, so the throttle is not
  protecting the request; it is protecting the vendor from a creator clicking
  while nothing appears to change. Whether a minute is the right wait to put in
  front of somebody who has just fixed a setting is a judgement nobody has made
  against real use — anyone's.
- ~~**Whether grants needing the creator should also appear on the Series' Peer
  list**, or the Integrations page is enough. `T-091`'s open question, inherited
  whole: if the answer is yes, this is the task that grows, and the Peer list
  page and its controller join the Files table — the owner's.~~ **Answered
  20 September 2026:** both, and this is the task that grows. The Integrations
  page stays where a grant is fixed; the Series page is where the creator
  notices it. `SeriesController::peers()`, `resources/js/pages/share/series/Show.vue`
  and `series.peers.grant_needs_you` are in the Files table, the Copy table and
  case 82.
- **How the marker reads, and where it sits in the row.** The line is
  `series.peers.grant_needs_you` — "Your account could not let them in — fix it
  under Integrations." — rendered beneath the email line rather than appended to
  the `·` list beside it. A designer may want a shorter badge, or the mark
  carried by the row's styling instead; the field is one nullable string either
  way, so the change would be to `Show.vue` and one lang line. Anyone's, with a
  designer.
- **Whether `removalsUnresolved` needs a count in the section heading.** `D-040`
  says "a count in the section's heading" for the new list, and
  `ProviderSection.vue` renders the heading, not the slot — so a count there is
  a change to `T-044`'s component rather than to the slot content, and it would
  put this task's data into a prop shape `ProviderSections::props()` builds. This
  task puts the count in the list's own intro instead and leaves the component
  alone; confirm that is enough, or accept a `ProviderSection.vue` row in the
  Files table — anyone's, with a designer.

## Read-through, 20 September 2026

A three-lens read of `T-091` before it was to be frozen found the cut of that
day was not clean, and some of what it found is this task's. The list is in
`T-091` under "Read-through, 20 September 2026 — what the cut left behind".
This task's share was worked through the same day, in this file:

- **`ContainerChangeImpact` was declared twice.** It is `T-091`'s, declared
  once there; the Files table no longer claims the path, Decisions and Code
  cite the class instead of re-declaring it, and the `kind()` docblock quoted
  under Code is `T-091`'s — `meeting` for Zoom and Teams, `folder` otherwise.
  What this task produces and what the method answers are now stated as two
  different things wherever both appear (Scope, Code, Acceptance).
- **The Series' Peer-list marker is settled and specified.** Scope "In", Scope
  "Out" and the open question said three different things; the owner's ruling
  of 20 September is that the grant is marked there and this task builds it.
  Scope "In" names the field `grantNeedsYou`, Scope "Out" now excludes only
  what the marker does _not_ do, the open question is struck with its answer,
  the Files row for `SeriesController` names `peers()` (`:418`) beside
  `show()`, and `resources/js/pages/share/series/Show.vue`,
  `series.peers.grant_needs_you` and case 82 are new with it.
- **`checkNow()` and Check again are recorded as deleted, not moved.** The
  Decisions passage keeps the argument this task had on 20 September and ends
  with the owner's answer; nothing in the file claims either still exists.
- **The eighth state is written into the lists.** `VendorGrantStatus` has eight
  cases since `F01`, and an `attempting` row is on none of the three lists and
  marks nothing on the Peer list, because nobody can act on one and the Peer's
  next Open reconciles it with `checkGrant()`. Said in Decisions, Scope, both
  list queries, cases 52, 76 and 82, and Acceptance.
- **`F10`'s residue is gone from `retryNeedingCreator()`.** The docblock now
  says what the query selects on — `(group_id, status)`, the row's own
  `provider` and `external_target_id` — and that no container is joined and
  `container.series` is not eager-loaded, with the Series reached through the
  Access that both target kinds have.
- **The counts were recounted from the numbered cases.** `IntegrationsGrantsTest`
  has 8 (52 to 57, 76, 77) and its stated total was right; `ContainerImpactTest`
  had 3 (28, 58, 59) and has 4 with case 82; the total is 12, not 11. `T-091`'s
  sequence runs to 80, not 75, so 76 and 77 are this task's share of it rather
  than "one past the highest". `T-091`'s own consolidation pass added its case 81 the same day, so this one is 82.
- Stale citations corrected on the same pass: `VendorGrantStatus`'s case count
  in Preconditions, the constants `T-091` has settled, the `blocks: none` line
  when the front matter says `T-100, T-101`, and
  `tests/Feature/Share/IntegrationsTest.php`, which does not exist — the files
  are `IntegrationsPageTest.php` and `IntegrationsProvidersTest.php`.

Left, and each carries its own bullet under **Before this can be ready**:
`connections.grants.row` still reads "Next try :next" when `D-040` means "not
before"; how the marker reads and where it sits in the row; and whether
`T-091`'s own `retryNeedingCreator()` docblock still disagrees with its
Decisions once its consolidation pass lands.

## Re-scope log

None.

## Notes

**Citations re-read against the code on 20 September 2026.** `T-091` was written
over several days and some of the lines it cites have moved; these are the
current ones, and the ones the sections above use:

- `IntegrationsController::__construct()` is `:29` (`T-091` says `:27`), `show()`
  is `:31`, and Stripe's disconnect copy array is `:76-83` with its `choice()`
  call at `:80`. `T-091` cites `:67-74` and `:71`, and names the key
  `payouts.disconnect_priced`; it is `payments.disconnect_priced`.
- `SeriesController::show()` starts at `:140` (`T-091` says `:137-143`) and
  already injects `Terminology` at `:145`. `peers()` is private at `:418`, reads
  active Accesses at `:422-425`, and builds the row `id`, `name`, `email`,
  `grantedAt`, `wasPaid` at `:427-433`.
- The Peer list on the Series page renders at
  `resources/js/pages/share/series/Show.vue:786-802`, from the `PeerSummary`
  interface at `:84-90`; the `·` line under the name carries the email, when
  they joined and whether they paid.
- `routes/share/payments.php`'s `settings.integrations` is `:22-23` (`T-091` says
  `:20-21`); `share.series.show` is `routes/share/series.php:26`.
- `series.archive_confirm` is `lang/en/series.php:108` (`T-091` says `:57`), and
  the Series page's archive dialog is
  `resources/js/pages/share/series/Show.vue:938-963` (`T-091` says `:888`).
- `ProviderSection.vue`'s `#grants` slot is `:421`, and the comment `T-044` left
  above it at `:420` reads "T-091 fills this with the container and the grants
  that need the creator." After the cut that is this task, and the comment is a
  one-word correction in a file nothing else here touches — so
  `resources/js/components/share/ProviderSection.vue` is **not** in the Files
  table, and the line is a departure to add if the developer thinks it worth
  the row. Noted so it is a choice rather than an oversight.
- `Integrations.vue` renders its sections at `:277-283`, keyed by the provider's
  stored value, and `beginUrl` is built server-side at
  `app/Support/ProviderSections.php:212` — the precedent every URL here follows.

**Naming the vendor in this copy is `T-044`'s precedent, not a new decision.**
`D-035` asks for the owner's confirmation before a vendor is named in public
copy, and lists Stripe alone. Every line here is creator-facing on a page whose
sections already say "Connect Dropbox" and name the account the creator
connected themselves; the test `D-035` sets — what naming the vendor gives away
about Qori's stack — is already answered on that page. Worth knowing rather than
worth re-deciding, and it does not extend to anything a Peer reads.

**What `T-091` was ambiguous about, and how this task read it.** Four places, all
recorded above where they bite: whether `checkNow()` was a creator surface
(moot — the owner deleted it on 20 September 2026, and Decisions keeps the
argument and its answer); whether `impactOf()` can stay callable from `attach()`
(it cannot — Decisions); whether `containersToRepick`'s `url` is the container's
vendor page or the Qori Series page (the Series page, because the copy says to
open it and pick again); and how many cases `IntegrationsGrantsTest` really has
(`T-091` says eight and numbers six). None of them changes what gets built; all
four would have been resolved differently by different developers, which is the
test `PROCESS.md` sets.
