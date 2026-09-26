---
id: T-125
title: A Peer joins a live Episode from the Series page, in their own time
stream: classroom
status: doing
owner: claude
estimate: M
depends: T-089, T-123, T-124
blocks: T-126, T-131
---

# T-125 — A Peer joins a live Episode from the Series page, in their own time

> **Draft.** Specified on 17 September 2026 from `D-024`, `D-025` and
> `D-026`, and not to be started — see [`../PROCESS.md`](../PROCESS.md). It
> waits on `T-089` becoming `ready`, because it builds on names that draft
> holds; what has to happen before it can be marked `ready` is listed at the
> bottom.

## Why

A live Episode is a dead end for a Peer. The row on the Peer's page
(`resources/js/pages/shared/Show.vue:195-229`) is a button that calls
`openEpisode()` (`:82-113`), which fetches the JSON play route and reaches
`PlaybackTicketService::resolve()`, and that throws
`errors.playback.unsupported_provider` for any provider without a resolver
(`app/Services/PlaybackTicketService.php:85-89`) — which is every live one.
`T-089` replaces the button with a link for Episodes that open in a tab and
renders no control at all for a live Episode, on purpose, because nothing on
the Peer surface reads the `join_url` that `StoreEpisodeRequest::content()`
stores. The row shows `starts_at` alone, through `SessionTime.vue` in the
reader's own zone with nothing to say whose 9am the creator meant; `T-123`
adds `ends_at` and nothing yet shows it. And there is no address for one
Episode: the access email links `url('/shared/'.$id)`
(`app/Notifications/SeriesAccessNotification.php:62`) and every later email,
calendar file and copied message would have to do the same and leave the
Peer scrolling.

Afterwards a live Episode row on `/shared/{seriesId}` carries a card. The card
shows the start and the end in the device's zone with the Group's zone beside
it when the two differ, says "Recorded" or "Live only" from the creator's
switch, and offers Join — a plain `<a target="_blank">` to `T-089`'s
`shared.episodes.open` — from `qori.live.join_opens_minutes` before the start
until `join_closes_after_minutes` after the scheduled end, then a secondary
"Still in the session? Join again" until `join_grace_after_minutes`. What the
card says in each state is computed by
`App\Services\LiveSessionService::stateFor()` from the two columns, the clock
and `content`, never stored, and never claims a fact Qori has not observed
(`D-026`). Every Join marks the Episode opened, as `/play` does, and writes one
row to a new `access_opens` table. `GET /shared/{seriesId}/episodes/{episodeId}`
(`shared.episodes.show`) passes the Series page's access gate and answers 302
to `#episode-{id}` on that page, so every email and calendar file from `T-128`
and `T-133` onwards is minted against one address that a page of its own can
replace later without breaking a link already sent (`D-024`). A Peer who has
never saved a timezone is offered their device's zone on the page, so the
emails that follow (`D-028`) use it too.

## Decisions taken to make this specifiable

**State is computed by `LiveSessionService::stateFor(Episode, CarbonImmutable): LiveState` and never stored (`D-026`).**
Its arms in this task: `cancelled` when `content['cancelled_at']` is set;
`upcoming` before the join window opens; `open` until it closes;
`not_recorded` after that when `content['records']` is `false` or
`content['not_recorded_at']` is set; `waiting` until `ends_at` plus
`qori.live.recording_wait_hours`; `overdue` after. `LiveState` carries all
eight cases the stream shares, but `ready` and `review` are never returned
here: `ready` needs `episode_recordings` (`T-126`) and `review` the finder
(`T-143`), and each of those tasks inserts its arm between `not_recorded` and
`waiting`. Nothing writes `cancelled_at` or `not_recorded_at` before `T-134`
and `T-127`; the arms exist now so the tests pin the boundaries once and
those tasks add writers, not rules.

**The clock is a parameter.** `stateFor()` and `joinAllowed()` take a
`CarbonImmutable $now` and the controller passes `CarbonImmutable::now()`
(`Date::use(CarbonImmutable::class)`, `app/Providers/AppServiceProvider.php:102`).
Every boundary is then a plain call with a chosen instant, and no test sets
the application clock to prove one. The application clock is still pinned
once, in each test file's `setUp()`, before the scene is built: the scene
adds its Episode through `EpisodeService::add()`, whose
`guardLiveSessionTime(creating: true)` refuses a start behind the real
clock (`errors.series.starts_in_past`, `T-123`), so a fixed October 2026
start would fail at setup from 7 October 2026 without the pin. Laravel's
test case clears it after every test
(`Illuminate\Foundation\Testing\Concerns\InteractsWithTestCaseLifecycle:163-167`).

**The join window is one value, `App\Data\JoinWindow`, and the route admits the whole span.**
`opensAt = starts_at − join_opens_minutes`, `closesAt = ends_at + join_closes_after_minutes`,
`graceUntil = ends_at + join_grace_after_minutes`. `admits($now)` is
`opensAt ≤ now < graceUntil`; the state is `open` only until `closesAt`, and
the card renders the primary Join in `open` and the secondary "Join again" in
`waiting` and in `not_recorded` while `inGrace($now)` — a "Live only" session
is `not_recorded` from `closesAt`, and a class that runs over still needs a
way back in. Both controls are the same `<a>` to the same
route, because the route decides on the click and the card only decides what
to call it. A multi-field shape between layers is a `Data` class
(`CLAUDE.md`), not an array.

**The live arm is in `PlaybackTicketService::open()`, before any resolver, and answers a `VendorLink`.**
A pasted `join_url` is a URL Qori does not interpret (`D-025`), so it needs
no `ResolvesMedia` implementation and no vendor folder — `EpisodeProvider::Link`
has none. The arm runs after `admit()` and `ProgressService::opened()`, in
the slot `T-089` reserves for `T-091`'s ensure step, and returns
`new VendorLink($url, $episode->provider)` when `joinAllowed()`; otherwise
`VendorLink::blocked(LiveSessionService::BLOCKED_NOT_OPEN, …)`, or
`BLOCKED_NO_LINK` when `content['join_url']` is empty. The two states are
constants on the service, not `VendorGrantStatus` values, because no grant
exists on this path; `T-089`'s `blocked()` already takes a string for that
reason. A Join outside the window still counts as an open, exactly as
`T-089`'s blocked branch does: the gate was passed and the Episode reached.

**`OpenEpisodeController` chooses the destination by the blocked state.**
The two live states go to `route('shared.show', $seriesId).'#episode-'.$episodeId`
with `live.join.not_open` or `live.join.no_link` as an `info` toast; every
other state keeps `T-089`'s `#access` and `shared.vendor_notice.redirected`.
One `match`, three arms, in the controller `T-089` writes, because it is
the one place a blocked link becomes a redirect (`D-020`).

**One `access_opens` row per redirect that carries a URL; `issue()` writes none.**
`open()` records `OpenTarget::Join` on the live arm and `OpenTarget::Episode`
after `resolve()` succeeds on every other; a blocked link and a thrown
resolver write nothing, because the table answers "who followed it" and
`opened_episode_ids` already answers "who reached it". The JSON play route
is `T-090`'s to delete and gets no row. `AccessOpen::record()` sets
`group_id` from the Access explicitly, because the Peer surface has no
current Group and `BelongsToGroup`'s creating hook would call
`CurrentGroup::idOrFail()` (`app/Concerns/BelongsToGroup.php:25-29`).
Reads of `access_opens` from the Peer surface, when a later task needs one,
go through `forGroup($series->group)`; this task adds no `acrossAllGroups()`
caller, so the allow-list in `tests/Feature/Admin/ConsoleAccessTest.php`
is unchanged.

**`shared.episodes.show` is a gate and a 302, never a page (`D-024`).**
A new invokable `EpisodeAnchorController` does what
`SharedController::show()` does at `:86-118` — `CurrentUser::orFail()`,
`Access::forUser($peer)->where('series_id', …)->first()`, 403
`errors.access.not_granted` when absent — and redirects to the anchor. It
looks the Episode up nowhere: the Series page is the destination whatever
the Episode's fate, a removed Episode's anchor lands at the top of the same
page, and the page already holds every sentence (`D-020`). The Confirming
branch for a payment in flight stays the Series page's; a link to one
Episode is only ever sent to somebody who already has access.

**Every time on the card is formatted in the browser, and no lang line carries a clock time.**
The server cannot know the device's zone, and a sentence rendered in one
zone beside a time rendered in another is the confusion the card exists to
end. So the copy says the schedule in the config's numbers —
"Join opens :minutes minutes before the start" — and the instants travel
as ISO strings for `SessionTime.vue`, which has `endsAt` from `T-123` and
gains `groupTimezone` here (the start and the end again, in `T-123`'s
formatting, in the Group's zone, after " · ", only when that zone is not
the display zone). The card's zone is the device's, as `SessionTime`
already does for a Peer; the stored `users.timezone` governs emails
(`D-028`) and is what the prompt below saves.

**`LiveSessionCard.vue` takes its copy as props and picks among `upcoming`, `open` and `waiting` on a 30-second tick.**
`SharedController::show()` resolves every line the card can need through
`Terminology::line($key, $replace, $series->group)`, so `:episode` is the
Group's word and no English is added to Vue. The server's `state` is
authoritative, but a Peer who opens the page twenty minutes early is the
person Join exists for, so when the server says `upcoming`, `open` or
`waiting` the card re-derives which of the three to show from
`joinOpensAt` and `joinClosesAt` against `Date.now()` every 30 seconds, and
shows `not_recorded` instead of `waiting` when `records` is false. The
other states never move inside one page view that matters; a reload is the
refresh, and the Join route re-checks the clock on the click, so a stale
card can never send anybody early. `copy.states` is keyed by the `LiveState`
value, each entry `{ message, resolution? }`, so a later task adds a state
by adding one key in `liveCard()` and one arm in the card and never a second
prop; `join`, `joinAgain`, `noLink` and `records` are the controls' lines.

**`overdue` and `not_recorded` get a message line now, with no resolution; `cancelled` gets none.**
Both are reachable the day this lands — 48 hours after any session, and
the moment a "Live only" session ends — so the card cannot render nothing.
`T-127` adds `live.state.overdue.resolution` once `T-129` guarantees the
email it promises, and the creator's controls. `cancelled` has no writer
until `T-134`, which owns its line; for a state it has no copy for the card
renders the time and nothing else.

**The timezone prompt is once per page, above the list, and posts to the existing route.**
`SharedController::show()` sends `timezonePrompt` only when
`$peer->getAttributeValue('timezone')` is null and the Series has a live
Episode; the page shows it only when the browser names a zone in the
options that differs from the resolved value. The form is
`TimezoneController.update.form()` with `TimezoneField.vue`, exactly as
`resources/js/pages/settings/Profile.vue:172-190` mounts it, and the route is
`profile.timezone.update` (`routes/settings.php:49-50`). That controller
answers `to_route('profile.edit')` today
(`app/Http/Controllers/Settings/TimezoneController.php:32`), which would
strand the Peer on their profile; it becomes
`redirect()->back(fallback: route('profile.edit'))`, so the profile page
behaves as before (no referer in `TimezoneTest`, so the fallback) and the
Series page reloads in place with its toast. The label is
`profile.timezone.label`, reused; the two new lines are `live.timezone.*`.

**Vendor names appear on Join and nowhere else (`D-025`).**
`live.join.by_provider.zoom`, `.teams` and `.link` are the button's words,
chosen by `$episode->provider->value` in the controller. Nothing else on the
card names a vendor.

**The public page is not touched, and a test pins it.**
`PublicSeriesController::show()` already sends titles, types, preview flags
and `starts_at` only (`app/Http/Controllers/PublicSeriesController.php:88-93`).
One case asserts the response never contains the join link, and one asserts
the Peer page never carries it as a prop either — `joinUrlPresent` is a
boolean — so the only way to the URL is the gated route (owner scenario 11).

**Continue points at the card for a live next Episode.** `T-089` gives the
Continue control the row's three-way rule, which leaves a live Episode with
no control. Here it becomes an `<a :href="'#episode-' + id">`, because the
card is where that Episode is continued.

**No factory for `access_opens`.** Every row is written by `open()`, and the
tests read what it wrote through `AccessOpen::query()->forGroup($group)`.
The design-review seeder writes none: nothing in a screenshot reads them
until `T-129`'s "who opened".

**`config/qori.php` is not edited.** Every number this task reads —
`join_opens_minutes`, `join_closes_after_minutes`, `join_grace_after_minutes`,
`recording_wait_hours` — is declared by `T-123`, once, for the stream.

## Preconditions

**Data this task verifies against:** a clean database. The tests build a
Group with a chosen `timezone` (`Australia/Brisbane`), a Series through
`SeriesService::create()`, a live Episode through `T-123`'s
`EpisodeService::add(…, startsAt: …, lengthMinutes: …)` with
`['join_url' => 'https://zoom.us/j/91827405566', 'records' => true]`, and an
Access through `AccessService::grant()`, as
`tests/Feature/Storage/PlaybackTest.php:42-49` and
`tests/Feature/Series/LiveSessionTest.php:41-60` do. Locally,
`php artisan qori:reset full` gives the design-review Series its one live
Zoom Episode with the content `T-123` writes.

**Equipment:** a visible browser whose device zone differs from the Group's,
to see the two zones on one card and the Join tab open; PHPUnit cannot
render `Intl`. Nothing else: no vendor is called, and the join link is a
URL Qori never follows.

**Spike:** none owed. This task introduces no vendor payload (`D-025`).

## Scope

**In:**

- `LiveState`, `OpenTarget`, `JoinWindow`, `AccessOpen` and the
  `access_opens` migration.
- `LiveSessionService::stateFor()`, `joinWindow()`, `joinAllowed()` and the
  two blocked-state constants, on the class `T-124` creates.
- The live arm in `PlaybackTicketService::open()`, the `access_opens` row on
  both branches, and the redirect destination by blocked state in
  `OpenEpisodeController`.
- `shared.episodes.show` and `EpisodeAnchorController`.
- `SharedController::show()`: the `live` prop per Episode and
  `timezonePrompt`.
- `LiveSessionCard.vue`; `SessionTime.vue`'s `groupTimezone`;
  `shared/Show.vue`'s anchors, card mount, prompt and Continue link.
- `TimezoneController::update()` answering `back()`.
- `lang/en/live.php` with the Peer lines for `upcoming`, `open`, `waiting`,
  `overdue`, `not_recorded`, Join and the prompt; the `live` group in
  `lang/en/errors.php`, declared with no key of this task's own.
- `docs/flows/live-sessions.md` and `docs/tinker/live-sessions.md`, with
  their README rows; the stale line in `docs/flows/storage.md`.

**Out:**

- Recordings: the table, paste, Watch, `?recording=` on the Open route, the
  `ready` arm (`T-126`); hide, "There's no recording", the `overdue`
  resolution line and the creator's controls (`T-127`); the `review` arm
  (`T-143`).
- Cancel, undo and "Add the next session", and the `cancelled` copy
  (`T-134`).
- Add to calendar (`T-133`); every email (`T-128`, `T-138`); the day-before
  reminder.
- Materials on the card (`T-130`, `T-131`) and the chat card (`T-132`).
- The creator's side of the card, `LiveSessionPanel.vue` (`T-123`, `T-124`).
- The next session on the public page before buying (`T-135`); the public
  page is only asserted, never edited.
- Any change to `ResolvesMedia`, the resolvers, `issue()`, the JSON play
  route or `MediaLink` (`T-090`); `T-091`'s ensure step and `series_containers`.
- Server-rendered dates in the recipient's zone (`T-025`); this task
  formats in the browser and saves a zone.
- A "who followed Join" read for the creator (`T-129`).
- A page of its own for one Episode; `D-024` chose the anchor.

## Files

| Path                                                            | Change | Notes                                                                                                    |
| --------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------- |
| `app/Enums/LiveState.php`                                       | new    | eight cases; `ready` and `review` documented as later arms                                               |
| `app/Enums/OpenTarget.php`                                      | new    | `episode`, `join`, `recording`, `material`, `chat`                                                       |
| `app/Data/JoinWindow.php`                                       | new    | `opensAt`, `closesAt`, `graceUntil`; `admits()`, `inGrace()`                                             |
| `app/Models/AccessOpen.php`                                     | new    | `BelongsToGroup`, `HasUlids`, no timestamps; `record()`                                                  |
| `app/Services/LiveSessionService.php`                           | edit   | `stateFor()`, `joinWindow()`, `joinAllowed()`, the two constants, beside `T-124`'s `withLockedContent()` |
| `app/Services/PlaybackTicketService.php`                        | edit   | the live arm in `open()`; `AccessOpen::record()` on both branches; `LiveSessionService` by constructor   |
| `app/Http/Controllers/Shared/OpenEpisodeController.php`         | edit   | destination and toast by blocked state                                                                   |
| `app/Http/Controllers/Shared/EpisodeAnchorController.php`       | new    | the gate, then 302 to `#episode-{id}`                                                                    |
| `app/Http/Controllers/Shared/SharedController.php`              | edit   | `live` per Episode, `timezonePrompt`; `LiveSessionService` and `Terminology` by method injection         |
| `app/Http/Controllers/Settings/TimezoneController.php`          | edit   | `back()` with `profile.edit` as the fallback                                                             |
| `routes/shared.php`                                             | edit   | `shared.episodes.show`                                                                                   |
| `database/migrations/2026_09_18_000100_create_access_opens.php` | new    | the table below                                                                                          |
| `lang/en/live.php`                                              | new    | the Peer lines; header in `accesses.php`'s style naming the `D-026` rule                                 |
| `lang/en/errors.php`                                            | edit   | the `live` group, empty, with a comment naming `T-126` and `T-127` as the tasks that fill it             |
| `resources/js/components/series/LiveSessionCard.vue`            | new    | the card; copy as props; the 30-second tick                                                              |
| `resources/js/components/series/SessionTime.vue`                | edit   | `groupTimezone`, beside `T-123`'s `endsAt`                                                               |
| `resources/js/pages/shared/Show.vue`                            | edit   | `id="episode-{id}"` on every row, the card on live rows, the prompt, Continue as an anchor               |
| `docs/flows/live-sessions.md`                                   | new    | the state table with its boundaries, the two chains, the open log, what is not built                     |
| `docs/flows/README.md`                                          | edit   | one row                                                                                                  |
| `docs/flows/storage.md`                                         | edit   | "Not built yet" (`:98-104`) loses join links and progress; the open chain gains the live arm             |
| `docs/tinker/live-sessions.md`                                  | new    | a live Episode, `stateFor()` at chosen clocks, a Peer's `open()`, the `access_opens` row, the anchor URL |
| `docs/tinker/README.md`                                         | edit   | one row                                                                                                  |
| `tests/Feature/Series/LiveSessionStateTest.php`                 | new    | 11 cases                                                                                                 |
| `tests/Feature/Shared/LiveSessionCardTest.php`                  | new    | 20 cases                                                                                                 |
| `tests/Feature/Storage/OpenEpisodeTest.php`                     | edit   | `T-089`'s case 8 removed, 1 case added                                                                   |
| `tests/Feature/Settings/TimezoneTest.php`                       | edit   | 1 case added                                                                                             |

`php artisan qori:reachability` (not part of `composer ci:check`, but the
audit the beta gate leans on) sees `shared.episodes.show` only once `T-128`
links to it from an email; until then it is reached by nothing on a page,
on purpose, and its name goes in `config('qori.reachability.allowed')` with
the reason "the address every session email and calendar file is minted
against (`D-024`); first linked by `T-128`" — one row in `config/qori.php`,
the one exception to "`T-123` only" in the stream's claim order, listed here
for the collision check and safe because `T-123` precedes this task.

| Path              | Change | Notes                                   |
| ----------------- | ------ | --------------------------------------- |
| `config/qori.php` | edit   | one `reachability.allowed` row, no more |

## Database

| Table          | Column       | Type      | Null | Default | Index / constraint                                    |
| -------------- | ------------ | --------- | ---- | ------- | ----------------------------------------------------- |
| `access_opens` | `id`         | ulid      | no   | —       | primary                                               |
| `access_opens` | `group_id`   | ulid      | no   | —       | FK `groups` cascade; first in the index               |
| `access_opens` | `access_id`  | ulid      | no   | —       | FK `accesses` cascade                                 |
| `access_opens` | `target`     | string    | no   | —       | an `OpenTarget` value                                 |
| `access_opens` | `episode_id` | ulid      | yes  | null    | FK `episodes` null on delete                          |
| `access_opens` | `subject_id` | string    | yes  | null    | a recording, material or chat id later; no FK         |
| `access_opens` | `opened_at`  | timestamp | no   | —       | index `(group_id, access_id, opened_at)` with the two |

No `created_at`/`updated_at`: a row is one event and `opened_at` is its time.

Migration: `database/migrations/2026_09_18_000100_create_access_opens.php`

```php
Schema::create('access_opens', function (Blueprint $table): void {
    $table->ulid('id')->primary();
    $table->foreignUlid('group_id')->constrained()->cascadeOnDelete();
    $table->foreignUlid('access_id')->constrained('accesses')->cascadeOnDelete();
    $table->string('target');
    $table->foreignUlid('episode_id')->nullable()->constrained()->nullOnDelete();
    $table->string('subject_id')->nullable();
    $table->timestamp('opened_at');
    $table->index(['group_id', 'access_id', 'opened_at']);
});
// down(): Schema::dropIfExists('access_opens');
```

## Code

```php
namespace App\Enums;

/**
 * Where a live Episode's card is in its life (D-026).
 *
 * Computed by LiveSessionService::stateFor() from starts_at, ends_at, the
 * clock and content, and never stored. The copy for each state says the
 * schedule and never a fact Qori has not observed.
 */
enum LiveState: string
{
    case Upcoming = 'upcoming';
    case Open = 'open';
    case Waiting = 'waiting';
    /** The creator's view of a found recording awaiting them; a Peer sees Waiting. Returned from T-143. */
    case Review = 'review';
    /** A published, unhidden recording exists. Returned from T-126. */
    case Ready = 'ready';
    case Overdue = 'overdue';
    case NotRecorded = 'not_recorded';
    case Cancelled = 'cancelled';
}
```

```php
namespace App\Enums;

/** What a Peer followed from the Series page — the `target` of an access_opens row. */
enum OpenTarget: string
{
    case Episode = 'episode';
    case Join = 'join';
    case Recording = 'recording';   // T-126
    case Material = 'material';     // T-131
    case Chat = 'chat';             // T-132
}
```

```php
namespace App\Data;

use Carbon\CarbonImmutable;

/** The span in which Join may be followed: qori.live's three numbers around the two columns (D-026). */
class JoinWindow
{
    public function __construct(
        /** starts_at − join_opens_minutes */
        public CarbonImmutable $opensAt,
        /** ends_at + join_closes_after_minutes — the state is `open` until here */
        public CarbonImmutable $closesAt,
        /** ends_at + join_grace_after_minutes — "Join again" until here */
        public CarbonImmutable $graceUntil,
    ) {}

    /** opensAt ≤ now < graceUntil */
    public function admits(CarbonImmutable $now): bool;

    /** closesAt ≤ now < graceUntil — the secondary control's span */
    public function inGrace(CarbonImmutable $now): bool;
}
```

```php
namespace App\Models;

use App\Concerns\BelongsToGroup;
use App\Enums\OpenTarget;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * One Peer following one thing from the Series page (D-024).
 *
 * Append-only. `opened_episode_ids` on the Access says an Episode was
 * reached; this says what was followed and when, and it is what T-129's
 * "who opened" reads.
 *
 * @property string $group_id
 * @property string $access_id
 * @property OpenTarget $target
 * @property ?string $episode_id
 * @property ?string $subject_id
 * @property \Illuminate\Support\Carbon $opened_at
 */
class AccessOpen extends Model
{
    use BelongsToGroup, HasUlids;

    public $timestamps = false;

    /** @var list<string> */
    protected $fillable = ['group_id', 'access_id', 'target', 'episode_id', 'subject_id', 'opened_at'];

    /** @return array<string, string> */
    protected function casts(): array;   // target => OpenTarget::class, opened_at => 'datetime'

    /** @return BelongsTo<Access, $this> */
    public function access(): BelongsTo;

    /** @return BelongsTo<Episode, $this> */
    public function episode(): BelongsTo;

    /**
     * One row per redirect. group_id is copied from the Access because the
     * Peer surface has no current Group and the creating hook would throw.
     */
    public static function record(Access $access, OpenTarget $target, ?string $episodeId = null, ?string $subjectId = null): self;
    // return static::create([
    //     'group_id' => $access->group_id,
    //     'access_id' => (string) $access->getKey(),
    //     'target' => $target,
    //     'episode_id' => $episodeId,
    //     'subject_id' => $subjectId,
    //     'opened_at' => now(),
    // ]);
}
```

```php
// App\Services\LiveSessionService — T-124's class, which holds
// withLockedContent(). Only what this task adds is shown; the `use` lines
// are the ones these members need. No vendor imports: the join link is a
// URL Qori never follows (D-025). T-134 adds cancel(), restore() and copy();
// T-143 attachFound().
namespace App\Services;

use App\Data\JoinWindow;
use App\Enums\LiveState;
use App\Models\Episode;
use Carbon\CarbonImmutable;
use InvalidArgumentException;

class LiveSessionService
{
    // withLockedContent(Episode $episode, Closure $callback): Episode — T-124's, unchanged.

    /** VendorLink::blocked() states on the live arm; not VendorGrantStatus values, because no grant exists here. */
    public const BLOCKED_NOT_OPEN = 'not_open';

    public const BLOCKED_NO_LINK = 'no_link';

    /**
     * Never stored. Throws InvalidArgumentException for an Episode that is
     * not live or has no starts_at/ends_at — a programmer error, since T-123
     * requires both on every live row.
     */
    public function stateFor(Episode $episode, CarbonImmutable $now): LiveState;
    // $content = (array) $episode->content;
    // $window = $this->joinWindow($episode);
    //
    // return match (true) {
    //     isset($content['cancelled_at']) => LiveState::Cancelled,
    //     $now < $window->opensAt => LiveState::Upcoming,
    //     $now < $window->closesAt => LiveState::Open,
    //     ($content['records'] ?? true) === false, isset($content['not_recorded_at']) => LiveState::NotRecorded,
    //     // T-126 inserts Ready here; T-143 inserts Review here.
    //     $now < $episode->ends_at->toImmutable()->addHours((int) config('qori.live.recording_wait_hours')) => LiveState::Waiting,
    //     default => LiveState::Overdue,
    // };

    public function joinWindow(Episode $episode): JoinWindow;
    // new JoinWindow(
    //     $episode->starts_at->toImmutable()->subMinutes((int) config('qori.live.join_opens_minutes')),
    //     $episode->ends_at->toImmutable()->addMinutes((int) config('qori.live.join_closes_after_minutes')),
    //     $episode->ends_at->toImmutable()->addMinutes((int) config('qori.live.join_grace_after_minutes')),
    // )

    /** The window admits and the session is not cancelled. */
    public function joinAllowed(Episode $episode, CarbonImmutable $now): bool;
}
```

```php
// App\Services\PlaybackTicketService — T-089's open(), with the live arm in
// the slot it left for T-091, and the open log on both branches.

public function __construct(
    private iterable $providers,
    private CurrentGroup $current,
    private ProgressService $progress,
    private LiveSessionService $live,
) {}

public function open(User $peer, string $seriesId, string $episodeId): MediaLink|VendorLink;
// [$access, $series, $episode] = $this->admit($peer, $seriesId, $episodeId);
// $this->progress->opened($access, $episodeId);
//
// if ($episode->isLive()) {
//     return $this->join($access, $episode);          // before any resolver; T-091's ensure step stays below this line
// }
//
// $link = $this->resolve($episode, $series);
// AccessOpen::record($access, OpenTarget::Episode, $episodeId);
//
// return $episode->provider->isQoriHosted() ? $link : VendorLink::fromMediaLink($link);

/** The live arm: the pasted link when the window admits, else why not. */
private function join(Access $access, Episode $episode): VendorLink;
// $url = $episode->content['join_url'] ?? null;
//
// if (! is_string($url) || $url === '') {
//     return VendorLink::blocked(LiveSessionService::BLOCKED_NO_LINK, $episode->provider);
// }
//
// if (! $this->live->joinAllowed($episode, CarbonImmutable::now())) {
//     return VendorLink::blocked(LiveSessionService::BLOCKED_NOT_OPEN, $episode->provider);
// }
//
// AccessOpen::record($access, OpenTarget::Join, (string) $episode->getKey());
//
// return new VendorLink($url, $episode->provider);
```

```php
// App\Http\Controllers\Shared\OpenEpisodeController::__invoke — T-089's blocked
// branch grows two arms. Nothing else in the method changes.

if ($link instanceof VendorLink && $link->isBlocked()) {
    [$key, $anchor] = match ($link->blockedState) {
        LiveSessionService::BLOCKED_NOT_OPEN => ['live.join.not_open', '#episode-'.$episodeId],
        LiveSessionService::BLOCKED_NO_LINK => ['live.join.no_link', '#episode-'.$episodeId],
        default => ['shared.vendor_notice.redirected', '#access'],
    };

    Inertia::flash('toast', [
        'type' => 'info',
        'message' => $terminology->line($key, [], Series::findForPeer($seriesId)?->group),
    ]);

    return redirect()->to(route('shared.show', $seriesId).$anchor);
}
```

```php
namespace App\Http\Controllers\Shared;

use App\Exceptions\AppException;
use App\Http\Controllers\Controller;
use App\Models\Access;
use App\Support\CurrentUser;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

/**
 * The stable address of one Episode on the Peer surface (D-024).
 *
 * Every email, calendar file and copied message is minted against this
 * route, and it answers with the Series page at that Episode's anchor, so a
 * page of its own can replace the redirect later without breaking a link
 * already sent. The gate is the Series page's; the Episode is not looked
 * up, because the page holds every sentence whatever became of it (D-020).
 */
class EpisodeAnchorController extends Controller
{
    public function __invoke(Request $request, string $seriesId, string $episodeId): RedirectResponse;
    // $peer = CurrentUser::orFail($request);
    //
    // if (Access::forUser($peer)->where('series_id', $seriesId)->first() === null) {
    //     throw AppException::forbidden(
    //         'errors.access.not_granted',
    //         devMessage: "User {$peer->getKey()} has no active access in series {$seriesId}.",
    //     );
    // }
    //
    // return redirect()->to(route('shared.show', $seriesId).'#episode-'.$episodeId);
}
```

```php
// App\Http\Controllers\Shared\SharedController::show(), with two services by
// method injection — the constructor stays empty for T-131 and T-132.

public function show(Request $request, string $series, LiveSessionService $live, Terminology $terminology): Response;

// Each Episode (:134-142) gains one key; T-089's `opens` stays null for a live one:
'live' => $episode->isLive() ? $this->liveCard($episode, $model, $live, $terminology) : null,

// Two page-level keys beside `deletion` and `progress`:
'timezonePrompt' => $this->timezonePrompt($peer, $model),

/**
 * What the card needs and nothing it must not have: the join link never
 * travels, only whether one exists.
 *
 * @return array<string, mixed>
 */
private function liveCard(Episode $episode, Series $series, LiveSessionService $live, Terminology $terminology): array;
// $now = CarbonImmutable::now();
// $window = $live->joinWindow($episode);
// $content = (array) $episode->content;
// $group = $series->group;
// $records = ($content['records'] ?? true) !== false;
//
// return [
//     'state' => $live->stateFor($episode, $now)->value,
//     'startsAt' => $episode->starts_at?->toIso8601String(),
//     'endsAt' => $episode->ends_at?->toIso8601String(),
//     'joinOpensAt' => $window->opensAt->toIso8601String(),
//     'joinClosesAt' => $window->closesAt->toIso8601String(),
//     'joinAgainUntil' => $window->graceUntil->toIso8601String(),
//     'groupTimezone' => $group?->timezone() ?? Timezones::fallback(),
//     'joinUrlPresent' => is_string($content['join_url'] ?? null) && $content['join_url'] !== '',
//     'records' => $records,
//     'copy' => [
//         // Keyed by the LiveState value, one {message, resolution?} each. T-126 adds
//         // 'ready', T-127 'resolution' under 'overdue', T-134 'cancelled' — here, never a second prop.
//         'states' => [
//             'upcoming' => ['message' => $terminology->line('live.state.upcoming.message', ['minutes' => (int) config('qori.live.join_opens_minutes')], $group)],
//             'open' => ['message' => $terminology->line('live.state.open.message', ['minutes' => (int) config('qori.live.join_closes_after_minutes')], $group)],
//             'waiting' => ['message' => $terminology->line('live.state.waiting.message', [], $group)],
//             'overdue' => ['message' => $terminology->line('live.state.overdue.message', [], $group)],
//             'not_recorded' => ['message' => $terminology->line('live.state.not_recorded.message', [], $group)],
//         ],
//         'join' => $terminology->line('live.join.by_provider.'.$episode->provider->value, [], $group),
//         'joinAgain' => $terminology->line('live.join.again', [], $group),
//         'noLink' => $terminology->line('live.join.no_link_yet', [], $group),
//         'records' => $terminology->line($records ? 'live.records.recorded' : 'live.records.live_only', [], $group),
//     ],
// ];

/**
 * Offered only to somebody who has never answered, and only where a session
 * makes the answer matter. The browser decides whether its own zone differs.
 *
 * @return ?array{options: array<string, list<string>>, value: string, label: string, description: string, save: string}
 */
private function timezonePrompt(User $peer, Series $series): ?array;
// if ($peer->getAttributeValue('timezone') !== null) return null;
// if (! $series->orderedEpisodes()->contains(fn (Episode $episode): bool => $episode->isLive())) return null;
//
// return [
//     'options' => Timezones::grouped(),
//     'value' => $peer->timezone(),
//     'label' => __('profile.timezone.label'),
//     'description' => __('live.timezone.why'),
//     'save' => __('live.timezone.save'),
// ];
```

```php
// App\Http\Controllers\Settings\TimezoneController::update() — the last line only.
return redirect()->back(fallback: route('profile.edit'));
```

```ts
// resources/js/pages/shared/Show.vue — the shapes the page and the card share.

/** LiveState's values as the page can receive them. `review` is the creator's and is never sent here: a Peer sees `waiting` (D-026). */
type LiveState =
    | 'upcoming'
    | 'open'
    | 'waiting'
    | 'ready'
    | 'overdue'
    | 'not_recorded'
    | 'cancelled';

interface LiveCard {
    state: LiveState;
    startsAt: string;
    endsAt: string;
    joinOpensAt: string;
    joinClosesAt: string;
    joinAgainUntil: string;
    groupTimezone: string;
    joinUrlPresent: boolean;
    records: boolean;
    copy: {
        /** Keyed by the LiveState value; this task fills five. T-127 adds `resolution` under `overdue`; T-126 and T-134 add their keys. */
        states: Partial<
            Record<LiveState, { message: string; resolution?: string }>
        >;
        join: string;
        joinAgain: string;
        noLink: string;
        records: string;
    };
}

interface GrantedEpisode {
    // …T-089's fields…
    live: LiveCard | null;
}

interface TimezonePrompt {
    options: Record<string, string[]>;
    value: string;
    label: string;
    description: string;
    save: string;
}
// props gain: timezonePrompt: TimezonePrompt | null

// resources/js/components/series/LiveSessionCard.vue
const props = defineProps<{
    live: LiveCard;
    /** openRoute.url([seriesId, episodeId]) — T-089's `shared.episodes.open` */
    joinHref: string;
}>();
// const now = ref(Date.now()); a setInterval of 30_000 in onMounted, cleared in onUnmounted.
// const phase = computed<LiveState>(() => {
//     if (!['upcoming', 'open', 'waiting'].includes(props.live.state)) return props.live.state;
//     if (now.value < Date.parse(props.live.joinOpensAt)) return 'upcoming';
//     if (now.value < Date.parse(props.live.joinClosesAt)) return 'open';
//     return props.live.records ? 'waiting' : 'not_recorded';
// });
// const line = computed(() => props.live.copy.states[phase.value]);   // undefined for a state this task has no copy for
// const joinAgain = computed(
//     () => (phase.value === 'waiting' || phase.value === 'not_recorded') && now.value < Date.parse(props.live.joinAgainUntil),
// );
//
// Template, top to bottom:
//   <SessionTime :starts-at="live.startsAt" :ends-at="live.endsAt" :group-timezone="live.groupTimezone" />
//   <span>{{ live.copy.records }}</span>
//   line                 → <p>{{ line.message }}</p>, then <p v-if="line.resolution">{{ line.resolution }}</p> (first filled by T-127)
//   phase 'upcoming'     → !live.joinUrlPresent → <p>{{ live.copy.noLink }}</p>
//   phase 'open'         → live.joinUrlPresent ? <a :href="joinHref" target="_blank" rel="noopener">{{ live.copy.join }}</a>
//                                              : <p>{{ live.copy.noLink }}</p>
//   phase 'waiting' or 'not_recorded'
//                        → joinAgain && live.joinUrlPresent → a secondary <a :href="joinHref" target="_blank" rel="noopener">{{ live.copy.joinAgain }}</a>
//                          (in `not_recorded` too: a "Live only" class that runs over needs a way back in, and the route admits the whole grace)
//   anything else        → the time alone
// No inline English anywhere in the file.

// resources/js/components/series/SessionTime.vue — one prop added beside T-123's endsAt
const props = defineProps<{
    startsAt: string;
    /** T-123's; its rendering is T-123's and does not change here. */
    endsAt?: string;
    timezone?: string;
    /** The Group's zone; the start and the end again, in T-123's formatting, after " · " — only when it is not the display zone. */
    groupTimezone?: string;
}>();
// displayZone = props.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone (in the existing try/catch)
// second = props.groupTimezone && props.groupTimezone !== displayZone ? the same computed as `formatted`, with timeZone: props.groupTimezone : ''
// T-123's element, then <span v-if="second"> · {{ second }}</span>
// The existing fallback (a zone this browser does not carry → the reader's own zone) covers both calls.
```

`shared/Show.vue`: every row wrapper becomes
`<div :id="`episode-${episode.id}`" class="scroll-mt-4">`; a row whose
`episode.live` is set mounts `<LiveSessionCard :live="episode.live" :join-href="openRoute.url([series.id, episode.id])" />`
under the title and keeps `T-089`'s rule of no row-level Open control;
the Continue control for a live `nextEpisode` is
`<a :href="`#episode-${nextEpisode.id}`">`; above the `<Panel>` of
Episodes, when `timezonePrompt` is set and the browser's zone (read as
`TimezoneField.vue:39-45` reads it) is in the options and differs from
`timezonePrompt.value`, a `<Panel>` holding
`<Form v-bind="TimezoneController.update.form()">` with
`<TimezoneField :options :value :chosen="false" :label :description />`
and a submit button reading `timezonePrompt.save`, imported as
`resources/js/pages/settings/Profile.vue:8` imports the action.

`docs/flows/live-sessions.md`: the state table with each boundary as an
expression over the two columns and the four config keys; the Join chain
(`GET …/open` → `open()` → `admit()` → `opened()` → `join()` →
`AccessOpen::record()` → 302, and the two blocked states' redirects); the
anchor chain; the copy rule from `D-026` stated once; "Not built yet":
recordings, cancel, calendar, notices, each with its task id.
`docs/flows/README.md` gains the row
`[live-sessions.md](live-sessions.md) | A live Episode's computed state, Join, the per-Episode address, the open log`.
`docs/tinker/live-sessions.md`: setup as `docs/tinker/accesses.md:8-33`;
a live Episode through `EpisodeService::add(…, startsAt: CarbonImmutable::parse('2026-10-07 09:00', 'Australia/Brisbane'), lengthMinutes: 60)`;
`stateFor()` at five chosen clocks; `joinWindow()`; a Peer's `open()`
answering a `VendorLink`; `AccessOpen::query()->forGroup($group)->get()`;
`route('shared.episodes.show', [$series->getKey(), $episode->getKey()])`.
`docs/tinker/README.md` gains the row
`[live-sessions.md](live-sessions.md) | A live Episode's state at chosen clocks, Join, the open log`.

## Copy

| Key                               | File               | English                                                                                                                                       |
| --------------------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `live.state.upcoming.message`     | `lang/en/live.php` | Join opens :minutes minutes before the start.                                                                                                 |
| `live.state.open.message`         | `lang/en/live.php` | Join is open. It closes :minutes minutes after the scheduled end.                                                                             |
| `live.state.waiting.message`      | `lang/en/live.php` | This session was scheduled to end at the time shown. If it was recorded, the recording will be added here and you'll get an email when it is. |
| `live.state.overdue.message`      | `lang/en/live.php` | No recording has been added for this session yet.                                                                                             |
| `live.state.not_recorded.message` | `lang/en/live.php` | This session wasn't recorded.                                                                                                                 |
| `live.join.by_provider.zoom`      | `lang/en/live.php` | Join on Zoom                                                                                                                                  |
| `live.join.by_provider.teams`     | `lang/en/live.php` | Join on Teams                                                                                                                                 |
| `live.join.by_provider.link`      | `lang/en/live.php` | Join the session                                                                                                                              |
| `live.join.again`                 | `lang/en/live.php` | Still in the session? Join again                                                                                                              |
| `live.join.no_link_yet`           | `lang/en/live.php` | No join link has been added for this session yet.                                                                                             |
| `live.join.not_open`              | `lang/en/live.php` | Join isn't open for that :episode right now. The card shows when it is.                                                                       |
| `live.join.no_link`               | `lang/en/live.php` | That :episode has no join link yet.                                                                                                           |
| `live.records.recorded`           | `lang/en/live.php` | Recorded                                                                                                                                      |
| `live.records.live_only`          | `lang/en/live.php` | Live only                                                                                                                                     |
| `live.timezone.why`               | `lang/en/live.php` | Times on this page follow your device. Save your timezone so emails about sessions use it too.                                                |
| `live.timezone.save`              | `lang/en/live.php` | Save timezone                                                                                                                                 |

`:minutes` is `config('qori.live.join_opens_minutes')` on the first line and
`join_closes_after_minutes` on the second, interpolated in
`SharedController::liveCard()` and never restated. Every line is read
through `Terminology::line()` with the Series' Group, except the two
`live.timezone.*` lines, which carry no noun and are read with `__()`. No
line under `live.*` says "live now", "has ended", "on its way" or
"processing" (`D-026`); `live_only` is the creator's switch, not a claim
about the session. `live.state.overdue.resolution` is `T-127`'s;
`live.state.cancelled.message` is `T-134`'s; the `ready` lines are
`T-126`'s. The `profile.timezone.label` line ("Your timezone") is reused
for the prompt's label. `live.join.no_link_yet` states what Qori can see —
no link on the row — and is shown in `upcoming` and `open` alike, because
whether the creator will add one is not Qori's to promise (`D-026`). This
task throws no error of its own — the anchor route reuses
`errors.access.not_granted` — but the classroom brief settles that the
`live` group in `lang/en/errors.php` is declared here and filled by later
tasks, so `errors.php` gains an empty `'live' => []` with a comment naming
`T-126` (`recording_unavailable`, `not_live`) and `T-127` (`has_recording`,
`recording_not_found`) as the tasks that add its keys, and a lang walk finds
nothing under it to check.

## Routes

| Verb  | Path                                           | Name                      | Action                                                               |
| ----- | ---------------------------------------------- | ------------------------- | -------------------------------------------------------------------- |
| GET   | `/shared/{seriesId}/episodes/{episodeId}`      | `shared.episodes.show`    | `Shared\EpisodeAnchorController::__invoke` (new)                     |
| GET   | `/shared/{seriesId}/episodes/{episodeId}/open` | `shared.episodes.open`    | `Shared\OpenEpisodeController::__invoke` (`T-089`'s; the live arm)   |
| PATCH | `/u/timezone`                                  | `profile.timezone.update` | `Settings\TimezoneController::update` (exists; the redirect changes) |

The new route sits in `routes/shared.php` inside the existing
`auth`, `verified`, `shared.` group (`:31-34`), after `record` (`:37`) as
the file's own comment requires, and takes ids because every Peer route
does (`:21-25`). No creator route changes.

## Tests

**New: `tests/Feature/Series/LiveSessionStateTest.php` — 11 cases**
(a Group with `timezone` `Australia/Brisbane` on the `start` plan as
`LiveSessionTest.php:41-60` builds one; `setUp()` pins the application
clock with `Carbon::setTestNow(CarbonImmutable::parse('2026-10-01 09:00', 'Australia/Brisbane'))`
before the scene, so `EpisodeService::add()`'s past-start guard accepts the
fixed start whatever the real date, and Laravel's test case clears the pin
after each test; a live Zoom Episode starting 2026-10-07 09:00 Brisbane for
60 minutes through `EpisodeService::add()` with `startsAt:` and
`lengthMinutes:`; every clock a boundary is asserted at is a
`CarbonImmutable` passed into `stateFor()`, `joinWindow()` or
`joinAllowed()`, never the pinned one)

1. `test_it_is_upcoming_until_join_opens_minutes_before_the_start` — `Upcoming`
   at 08:44:59 Brisbane, `Open` at 08:45:00.
2. `test_it_is_open_from_join_opens_until_join_closes_after_the_end` — `Open`
   at 10:14:59, `Waiting` at 10:15:00.
3. `test_it_is_waiting_after_join_closes_until_recording_wait_hours` —
   `Waiting` at 10:15:00 and at 47 hours 59 minutes past 10:00.
4. `test_it_is_overdue_once_recording_wait_hours_have_passed` — `Overdue` at
   48 hours past 10:00.
5. `test_it_is_not_recorded_after_the_window_when_the_creator_chose_live_only`
   — `records => false`: `Open` at 09:30, `NotRecorded` at 10:15:00, still
   `NotRecorded` at 48 hours.
6. `test_it_is_not_recorded_when_not_recorded_at_is_set` — the content key
   written directly on the row; `NotRecorded` at 10:15:00.
7. `test_it_is_cancelled_whenever_cancelled_at_is_set` — the content key
   written directly; `Cancelled` at 08:00, 09:30 and 48 hours later.
8. `test_the_join_window_admits_from_opening_to_the_end_of_the_grace` —
   `admits()` false at 08:44:59, true at 08:45:00, true at 10:14:59, true at
   11:59:59, false at 12:00:00; `inGrace()` false at 10:14:59, true at
   10:15:00, false at 12:00:00.
9. `test_join_is_not_allowed_for_a_cancelled_session_inside_its_window` —
   `joinAllowed()` false at 09:30 with `cancelled_at` set.
10. `test_the_edges_come_from_config_and_nowhere_else` —
    `config()->set('qori.live.join_opens_minutes', 30)`: `opensAt` is 08:30.
11. `test_it_refuses_an_episode_that_is_not_live` — a File Episode:
    `InvalidArgumentException` from `stateFor()` and from `joinWindow()`.

**New: `tests/Feature/Shared/LiveSessionCardTest.php` — 20 cases**
(the same scene, published, with an Access through `AccessService::grant()`;
the same `setUp()` pin at 2026-10-01 09:00 Brisbane before the scene is
built — case 15's November Episodes included — and `Carbon::setTestNow()`
then moves the clock to each route case's instant; the flash toast is read
as `tests/Feature/Access/SeriesAccessCodeTest.php:87-89` reads one;
`Http::preventStrayRequests()` in `setUp`)

1. `test_join_redirects_to_the_join_link_inside_the_window` — at 09:30 the
   GET on `shared.episodes.open` is a 302 to `https://zoom.us/j/91827405566`.
2. `test_join_still_works_in_the_grace_after_the_window_closes` — at 11:00,
   the same 302.
3. `test_join_outside_the_window_returns_to_the_card_with_the_not_open_line`
   — at 08:00 and at 12:30: 302 to `route('shared.show', $seriesId).'#episode-'.$episodeId`;
   an `info` toast whose message is `live.join.not_open` with the Group's
   `:episode`.
4. `test_join_with_no_link_returns_to_the_card_with_the_no_link_line` —
   content without `join_url`, at 09:30: the same anchor; `live.join.no_link`.
5. `test_join_writes_an_access_open_row_carrying_the_access_group` — after
   case 1's GET, `AccessOpen::query()->forGroup($group)` holds one row:
   `access_id`, `target` `join`, `episode_id`, `opened_at` set,
   `subject_id` null.
6. `test_a_join_that_was_turned_back_writes_no_access_open_row` — after case
   3's GET, no row.
7. `test_join_marks_the_episode_opened` — `$access->fresh()->hasOpened($episodeId)`
   after case 1, and after case 3 too.
8. `test_join_refuses_a_revoked_access` — `AccessService::revoke()`, then
   403 with `errors.access.not_granted.message`.
9. `test_join_refuses_a_series_in_another_group` — a Peer with access to a
   Series in Group A, a live Series in Group B they have no access to: 403.
10. `test_the_anchor_route_redirects_to_the_episode_anchor` — 302 to
    `route('shared.show', $seriesId).'#episode-'.$episodeId`; nothing is
    marked opened and no `access_opens` row is written.
11. `test_the_anchor_route_refuses_someone_without_access` — 403.
12. `test_the_anchor_route_refuses_a_revoked_access` — 403.
13. `test_the_anchor_route_refuses_a_series_in_another_group` — 403.
14. `test_the_page_carries_the_card_with_the_group_zone_beside_the_instant`
    — `assertInertia`: `series.episodes.0.live.state` is `upcoming`,
    `.groupTimezone` is `Australia/Brisbane`, `.startsAt` is
    `2026-10-06T23:00:00+00:00`, `.endsAt` is `2026-10-07T00:00:00+00:00`,
    `.joinOpensAt` is `2026-10-06T22:45:00+00:00`, `.copy.join` is
    `Join on Zoom`, `.copy.records` is `Recorded`.
15. `test_a_brisbane_session_is_one_instant_for_london_and_new_york_across_the_daylight_change`
    — two live Episodes, 1 and 8 November 2026 at 09:00 Brisbane, for a
    Peer whose `users.timezone` is `America/New_York`: the `startsAt` props
    are `2026-10-31T23:00:00+00:00` and `2026-11-07T23:00:00+00:00`;
    read back through `CarbonImmutable::parse()->setTimezone()`, London
    shows 23:00 on both, New York 19:00 then 18:00, Brisbane 09:00 on both
    (owner scenario 2 at prop level; the rendering is `T-145`'s).
16. `test_the_join_link_is_never_a_page_prop` — `joinUrlPresent` is true,
    `assertDontSee('zoom.us/j/91827405566')` on the response, and no
    `joinUrl` key anywhere under `series.episodes.0.live`.
17. `test_the_public_page_carries_no_join_link` — `GET` the public page from
    `route('series.public', …)` signed out and signed in as the Peer: the
    response never contains the link and `series.episodes.0` has no `live`
    key (owner scenario 11).
18. `test_a_file_episode_has_no_card` — `series.episodes.0.live` is null.
19. `test_the_timezone_prompt_is_offered_only_to_someone_who_has_not_chosen_a_zone`
    — `timezonePrompt` is null for a Peer with `timezone` set; for one
    with null it carries `options`, `value` `UTC`, `label`
    `Your timezone`, `save`; null again for a Series with no live Episode.
20. `test_a_live_only_session_offers_join_again_in_the_grace` — `records => false`,
    at 10:30: `series.episodes.0.live.state` is `not_recorded`,
    `.joinAgainUntil` is `2026-10-07T02:00:00+00:00`, and the GET on
    `shared.episodes.open` is a 302 to the join link, because the route
    admits the whole grace and the card's secondary is the same `<a>`; at
    12:30 the same GET turns back to the anchor with `live.join.not_open`.

**Changed:**

- `tests/Feature/Storage/OpenEpisodeTest.php` (`T-089`'s) — case 8,
  `test_a_live_episode_cannot_be_opened`, is deleted, because this task
  reverses it and the file above holds the live cases; one case is added,
  `test_an_open_writes_an_access_open_row_for_the_episode`: after the
  Qori-hosted 302, one row with `target` `episode`. Case 10's `opens` of
  `null` for a Zoom session stays true.
- `tests/Feature/Settings/TimezoneTest.php` — one case added,
  `test_saving_returns_to_the_page_it_was_posted_from`: with a `Referer`
  of `route('shared.show', $seriesId)` the PATCH redirects there; the
  existing `test_a_user_can_set_their_timezone` (`:54-63`) sends no referer
  and keeps asserting `profile.edit`.
- `tests/Feature/TerminologyTest.php` — unchanged; its article walk covers
  `lang/en/live.php` on its own. `tests/Feature/Admin/ConsoleAccessTest.php`
  — unchanged; no `acrossAllGroups()` is added.

Total: 31 new cases in two files, 2 added to existing files, 1 removed.

## Acceptance

- [ ] A Peer with access sees each live Episode as a card with the start and
      end in the device's zone, the Group's zone beside it when different,
      and "Recorded" or "Live only" from the creator's switch
- [ ] From 15 minutes before the start until 15 minutes after the scheduled
      end, Join opens the creator's link in a new tab; for two hours after
      that a secondary "Still in the session? Join again" does the same, for
      a "Live only" session too; before and after, the card says what comes
      next in the schedule's
      words, and no line says "live now", "has ended", "on its way" or
      "processing"
- [ ] A saved Join link followed outside the window returns to the card with
      one line, never to a page of its own
- [ ] `GET /shared/{seriesId}/episodes/{episodeId}` lands on the card after
      the access gate — the address every later email and calendar file
      is minted against
- [ ] Owner scenario 2: a Brisbane creator's 1 and 8 November 2026 sessions
      are the right instants for London and New York at prop level; the
      browser rendering is walked in `T-145`
- [ ] Owner scenario 11: a revoked Peer and a wrong-tenant request are
      refused on both routes; the public page never carries a join link,
      and neither does the Peer page as a prop
- [ ] Every Join is one `access_opens` row with the Access's `group_id` and
      marks the Episode opened
- [ ] A Peer with no timezone saved is offered their device's zone on the
      page and comes back to the same page after saving
- [ ] `docs/flows/live-sessions.md` and `docs/tinker/live-sessions.md`
      describe what runs, with their README rows, and `docs/flows/storage.md`
      no longer lists join links or progress as unbuilt
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~`T-089`'s three open questions answered and `T-089` set `ready`, so
  `shared.episodes.open`, `OpenEpisodeController`,
  `PlaybackTicketService::open()` and `admit()`, `VendorLink::blocked()`
  and `lang/en/shared.php` are frozen names this spec builds on — the
  owner's.~~ **Answered 21 September 2026:** `T-089` is `done`, and each name
  it freezes was read back from the code the same day —
  `shared.episodes.open` (`routes/shared.php:49`), `OpenEpisodeController`
  (`app/Http/Controllers/Shared/OpenEpisodeController.php`),
  `PlaybackTicketService::open()` (`:67`) and `admit()` (`:86`),
  `VendorLink::blocked()` (`app/Data/VendorLink.php:35`) and
  `lang/en/shared.php`.
- ~~The route name for the profile timezone form to post to~~ — read on
  17 September 2026: `profile.timezone.update`, `routes/settings.php:49-50`.
  ~~What remains is whether `TimezoneController::update()` may answer
  `back()` with `profile.edit` as the fallback, which this spec assumes and
  `T-025` (onboarding) may also want — anyone's, with `T-025`'s owner told.~~
  **Answered 21 September 2026:** yes. The method returns
  `to_route('profile.edit')` unconditionally today
  (`app/Http/Controllers/Settings/TimezoneController.php`), so naming
  `profile.edit` as the fallback keeps exactly today's behaviour for anyone
  who arrived from the profile page, and `back()` is what returns a Peer to
  the Series page the prompt was shown on. `T-025` wants the same shape and
  inherits it.
- ~~`app/Services/LiveSessionService.php` is also `T-124`'s
  (`withLockedContent()`), `T-124` is `ready`, and neither task depends on
  the other~~ — settled 18 September 2026: this task depends on `T-124`
  (front matter), `T-124` creates the file and this task edits it, and the
  `classroom` stream's claim order lists it (`T-124`, then `T-125`,
  `T-127`, `T-134`, `T-143`).

## Re-scope log

None.

## Notes

Specified on 17 September 2026 from the merged decisions and the classroom
brief; the two source proposals are folded into
[`../course-classroom.md`](../course-classroom.md).

Edits to other drafts this spec implies:

- `T-089`'s draft is edited to: "`T-091` is the first caller of
  `VendorLink::blocked()`" becomes "`T-125` or `T-091`, whichever lands
  first; on the live arm the state is a `LiveSessionService` constant, not
  a `VendorGrantStatus` value", and its test 8 (`test_a_live_episode_cannot_be_opened`)
  is noted as one `T-125` removes.
- `T-127`'s draft is edited — **for the amendments agent; not made as of
  18 September 2026** — so that: its Files row for
  `app/Services/LiveSessionService.php` reads "`liveEpisodeOf()`,
  `declareNotRecorded()`, `declareRecorded()`; `ready` narrowed to visible
  rows" and no longer claims the `not_recorded` arm, which `stateFor()`
  carries from here (declared, or `records` false, once Join has closed),
  and its Scope bullet on `stateFor()` says the same; its `lang/en/live.php`
  row reads "`state.overdue.resolution`, `panel.*`" and its Copy table drops
  `live.state.overdue.message` and `live.state.not_recorded.message`, which
  exist from here with the English above; its `LiveSessionCard.vue` row and
  its Decisions lose "the grace secondary in `not_recorded`", which this
  task renders; its `lang/en/errors.php` row reads "three keys in the `live`
  group `T-125` declares"; and its "Before this can be ready" bullets on the
  `copy` prop shape (it is `copy.states.<state>.message`, as that draft
  assumed) and on whether `live.php` already carries the two lines are
  struck as answered. `T-127` keeps `live.state.overdue.resolution`, the
  creator's three controls, the `not_recorded_at` writer and its test cases.
- `T-126`'s draft is edited to: `open()` already writes an `access_opens`
  row per redirect; Watch adds `OpenTarget::Recording` with `subject_id`
  set to the recording id, and inserts the `ready` arm between
  `not_recorded` and `waiting` in `stateFor()`; its `lang/en/errors.php`
  row adds `live.recording_unavailable` and `live.not_live` to the group
  this task declares, so its "whichever lands first" sentence goes.
- `T-134`'s draft is edited to: `stateFor()`'s `cancelled` arm and
  `joinAllowed()`'s refusal exist from `T-125`; `T-134` adds the writers,
  `live.state.cancelled.message` and the card's rendering of it.
- `T-145`'s draft is edited to: Join admits only from 15 minutes before the
  start, so a session added 30 minutes ahead is `upcoming` when the Peer
  arrives; the journey either adds the session 10 minutes ahead or uses the
  clock override that draft already lists as its open point.

`live.state.waiting.message` promises an email that `T-128` sends. `D-026`
fixes that sentence and `D-031` puts `T-128` inside the same checkpoint; if
the checkpoint ships without `T-128`, the report says so and the sentence
loses its second half in a wording change.

`Illuminate\Database\Schema\Blueprint::constrained()` on `access_id` would
guess `accesses` from the column name, and the migration names the table
anyway so nobody has to check.
