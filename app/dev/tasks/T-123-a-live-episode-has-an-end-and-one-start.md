---
id: T-123
title: A live Episode has an end and one start
stream: classroom
status: done
owner: wayne
estimate: M
depends: none
blocks: T-124, T-125, T-130, T-152
---

# T-123 — A live Episode has an end and one start

## Why

A live Episode has a start and nothing else. `episodes` carries `starts_at`
and no end (`database/migrations/2026_09_08_000000_create_qori_schema.php:103-118`),
so nothing can say when a session is scheduled to end, and the start is written
twice: `StoreEpisodeRequest::content()` copies it into the jsonb payload
(`app/Http/Requests/Share/StoreEpisodeRequest.php:190-195`) and
`EpisodeService::add()` reads it back out of `$content['starts_at']` into the
column (`app/Services/EpisodeService.php:46`, `:60`). A live Episode may only
be Zoom or Teams (`app/Enums/EpisodeType.php:35`), so a Meet link — or any
other host — has nowhere to go. The creator's page holds the live fields
inline in the Episode form (`resources/js/pages/share/series/Show.vue:604-619`),
and every number the classroom stream reads — how long before a start Join
opens, how long a session waits for its recording — is declared nowhere.
`docs/flows/series.md:125-129` still says accesses, progress, playback tickets
and uploads are unbuilt; all four are built and documented in
`docs/flows/accesses.md` and `docs/flows/storage.md`.

`D-026` fixes the shape: `ends_at` beside `starts_at`, entered as a length in
minutes (default 60, at most twelve hours), backfilled an hour after the start
on every existing live row, with the start living in the column alone and the
live `content` keeping `join_url` and a `records` switch. `D-025` adds
`EpisodeProvider::Link` for a pasted link from any host, with no connection
behind it.

Afterwards a creator adds a live Episode with a start, a length and "Recorded"
or "Live only", from Zoom, Teams or another meeting link, and the row on their
Series page reads the start and the end in the Group's zone with the zone
named. Every live Episode that already exists has an end. `config('qori.live')`,
`qori.materials`, `qori.chats`, `qori.limits.text.material_note` and the two
new `live_prefix` entries exist with a comment each, so no later task in the
stream edits `config/qori.php`. `LiveSessionPanel.vue` exists for `T-124`,
`T-126`, `T-127`, `T-129`, `T-134`, `T-135` and `T-144` to edit, and
`docs/flows/series.md` says what is built.

## Decisions taken to make this specifiable

**The length is entered, the end is stored, and the length is derived back.**
A creator thinks in "90 minutes"; a stored instant is what `T-125`'s state
and `T-133`'s calendar file need. `Episode::lengthMinutes()` computes the one
from the two columns, so nothing stores the same fact twice (`D-026`).

**`add()` takes the start and the length as typed parameters, never through
`$content`.** The column is the one authority (`D-026`). A `starts_at` key in
`$content` is refused with an `InvalidArgumentException`: the callers still on
the old shape are all in this repository and all edited here (the tinker
recipe, two tests), and silently dropping the key would hide one that was
missed. The guard's `mixed $startsAt` becomes `?CarbonImmutable`.

**The service keeps accepting a live Episode with no start; the Form Request
is the wall.** `D-026` puts the requirement on the Form Request, and
`tests/Feature/Share/EpisodeServiceTest.php:120-142` adds a live Episode with
no start to prove the jsonb column is queryable. `ends_at` is null exactly when
`starts_at` is. `length_minutes` is `nullable` in the request because
`starts_at` is `required` for `type = live` and the service fills the default
length, so every live Episode the form creates has `ends_at` set — which is
what `D-026` means by the end being required by the Form Request. The
past-start refusal stays in the service and gains a `creating` flag so `T-124`
can pass `false` on edit, where a past start is the point (`D-026`).

**`starts_at` and `ends_at` are written only for a live Episode; a start passed
for any other kind is dropped.** That is today's behaviour on the HTTP path —
`content()` has no arm that carries it for a file — but not the service's:
`add()` writes `$content['starts_at'] ?? null` for any kind
(`app/Services/EpisodeService.php:60`), so a service caller could store a start
on a File Episode, and stops. Stated once in the service rather than left to
each caller. A PDF does not start.

**The default and the maximum length are read from `config('qori.live')` in
the service and the request; the migration's backfill writes 60 as a literal.**
A migration records what happened to the data on one day. Reading config there
would let a later change to `default_length_minutes` rewrite what a fresh
checkout does to old rows. A comment in the migration says so.

**A length under one minute is a programmer error.** The Form Request's `min:1`
is the user-facing wall; no person can reach the service with 0, so the
service throws `InvalidArgumentException` rather than growing a lang key
(`CLAUDE.md`, errors).

**`records` lives in `content`, defaults to true, and both the migration and
`add()` write it.** `D-026` names it. True by default because a course that
records is the common case and "Live only" is the deliberate choice; `add()`
merges `['records' => true]` under whatever it was given, so a service caller
that says nothing gets the same default the migration wrote, and the request's
`records()` answers true when the field is absent.

**A live join link is validated as the pasted tier: `https`, at most 2048
characters (`D-025`).** Today `reference` is `max:500` for every kind
(`StoreEpisodeRequest.php:99`); a live Episode's reference is a URL Qori will
hand to Peers (`T-125`), so it takes the tier's rule — `url:https`, which
`Str::isUrl()` checks against that one scheme — and only for `type = live`;
every other kind keeps `max:500`. The link stays optional, as it is today
(`:147-152`): `T-125`'s card says when there is none.

**`Link` is a provider of the live kind only.** `EpisodeType::Live` allows
`[Zoom, Teams, Link]`; File, Video and Audio are unchanged. `connection()`
answers null and `isQoriHosted()` false. `T-130` reuses the same case for a
materials row with `provider = link` (`D-030`), which is why the case is on
the shared enum and not a live-only flag.

**The whole config block lands here, keys later tasks read included.** The
stream file orders `config/qori.php` "`T-123` only; it declares every key the
stream reads". Every key carries a comment naming the task that reads it.
`storage.series_total_mb` is not declared — its Free figure is the owner's
(`T-139`) — and `T-138`'s per-plan reminder key is that task's own declared
exception.

**`LiveSessionPanel.vue` has two modes, `form` and `row`, and takes every
sentence as a prop.** One component because the stream orders its edits by
file; two modes because the same four facts — link, start, length, recorded —
are entered in the Episode form and read on each live row, and `T-124`'s edit
form sits in the row. The copy comes from `lang/en/series.php` through
`SeriesController::show()`; no new inline English in Vue.

**The Recorded switch is a hidden `records=0` followed by a checkbox
`records=1`, in this form and in `T-124`'s edit form alike.** An unticked
checkbox posts nothing, and the hidden field is the standard way to post the
off state; PHP keeps the last of two fields with one name, so a ticked box
arrives as `1` and an unticked one as `0`. `T-124` already specifies the pair
for its edit form, and one switch in one component takes one shape.

**The `starts_at` block and the live arms of `referenceLabel` and
`referencePlaceholder` move into the panel; the timezone notice stays on the
page.** The notice at `Show.vue:627-632` is existing inline English; moving it
into a new component would be new inline English in that component. It stays
where it is, above the panel.

**`SessionTime.vue` gains an optional `endsAt`, rendered as one range through
`Intl.DateTimeFormat.prototype.formatRange()`.** So the creator's row reads the
date once, both times and the zone — "1 Oct 2026, 9:00 – 10:30 am AEST" in an
`en-AU` browser — from the one component every surface uses for a time (its
docblock, `resources/js/components/series/SessionTime.vue:2-15`).
`formatRange()` collapses whatever the two instants share and names both dates
when a session crosses midnight, so no hand-written same-day check is needed.
`T-125` adds only `groupTimezone` beside it, on the same call, and cites this
rule rather than restating it.

**The creator's page carries `joinUrl`; the public and Peer pages get nothing
new.** The creator pasted it. `D-024` forbids the public page from carrying a
join link, and `PublicSeriesController::show()` lists title, type, preview and
start only (`app/Http/Controllers/PublicSeriesController.php:88-93`); a case
here holds that line. `T-125` decides what a Peer with access sees.

**The toast stays `series.session_scheduled`.** The end is on the row a
creator lands back on; a second sentence in a toast is a second copy of it.

**Content on create is exactly `join_url` and `records`.** `schedule_version`,
`cancelled_at`, `not_recorded_at`, `meeting_id` and `occurrence_id` are absent
until the task that writes each (`T-124`, `T-134`, `T-127`, `T-142`, `T-100`);
`Episode::isCancelled()` reads a key nothing writes yet, so `T-134` has a
reader on day one. A row written before this task keeps whatever else it had.

**The migration case runs the migration's own `down()` and `up()` around a
hand-inserted row.** `RefreshDatabase` has already migrated; `require` on the
file returns the anonymous migration; Postgres DDL is transactional, so the
case rolls back with the test and nothing else in the suite sees it.

## Preconditions

**Data this task verifies against:** a clean database. Every case builds its
own Group with `timezone` set, as `tests/Feature/Series/LiveSessionTest.php:41-60`
does, because a live Episode is refused without one. For the browser check,
the design-review world (`php artisan qori:reset full --force`,
`docs/tinker/design-review.md`): its one live Episode is the seeder's live
clinic (`database/seeders/DesignReviewSeeder.php:356`), written straight to
the table, and its Group has no `timezone` chosen — set one on the Group page
before adding a live Episode by hand, or the form's notice says why it refuses.

**Equipment:** a browser, to see the row and the form. No vendor call, no
mailbox, no credentials.

**Spike:** none owed. Nothing here reads a vendor payload; the join link is a
string Qori stores and never follows (`D-025`).

## Scope

**In:**

- `episodes.ends_at`, the migration that adds it, backfills every live row an
  hour after its start, drops `starts_at` from every `content`, sets
  `records` true on every live row that lacks it, and adds the partial index.
- `EpisodeProvider::Link`, its `connection()` arm, and `EpisodeType::Live`
  allowing it.
- `Episode`: `ends_at` fillable and cast, `isCancelled()`, `lengthMinutes()`.
- `EpisodeService::add()` with `$startsAt` and `$lengthMinutes`;
  `guardLiveSessionTime()` typed and flagged `creating`; `lengthOrDefault()`;
  the `records` default; the refusal of `starts_at` inside `$content`.
- `StoreEpisodeRequest`: `length_minutes`, `records`, the live `reference`
  rule, `messages()`, `startsAt()`, `lengthMinutes()`, `records()`, the
  `Link` arm of `content()` and the Zoom/Teams arm without `starts_at`.
- `EpisodeController::store()` passing the two new parameters.
- `SeriesController::show()`: `endsAt`, `lengthMinutes`, `records` and
  `joinUrl` per Episode, and the `live` prop carrying defaults and copy.
- `LiveSessionPanel.vue` in both modes, mounted from `share/series/Show.vue`;
  `SessionTime.vue` with `endsAt`; `link` in the form's provider list.
- `config/qori.php`: `live`, `materials`, `chats`,
  `limits.text.material_note`, and `storage.live_prefix` gaining `material`
  and `chat_code`.
- `lang/en/series.php` `providers.link` and `live.*`; `lang/en/errors.php`
  `series.length_too_long`.
- The design-review seeder, the tinker recipe, `docs/flows/series.md`.

**Out:**

- Editing a live Episode's link, time, length or switch; `UpdateEpisodeRequest`
  and `EpisodeService::update()` are untouched; `schedule_version` (`T-124`).
- `LiveState`, `LiveSessionService::stateFor()`, the Peer's card, Join,
  `lang/en/live.php`, `docs/flows/live-sessions.md`, `docs/tinker/live-sessions.md`
  and anything on `shared/Show.vue` or `SharedController` (`T-125`).
- Recordings and `episode_recordings` (`T-126`, `T-127`).
- Cancel, undo and "Add the next session"; nothing writes `cancelled_at`
  (`T-134`).
- The `materials` and `series_chats` tables and every consumer of the
  `qori.materials` and `qori.chats` keys declared here (`T-130`, `T-132`).
- `storage.series_total_mb` (`T-139`) and a per-plan reminder key (`T-138`).
- `T-044`'s `guardProviderConnected()` and its exemption for a pasted
  `join_url` (`D-025`); this task adds no connection check anywhere.
- The next session's time on the public page (`T-135`); the public page's
  Episode entries are unchanged.
- `docs/flows/storage.md:98-104`, which still lists "Zoom/Teams join links"
  as unbuilt; `T-125` creates the live-sessions flow doc and corrects it.

## Files

| Path                                                                    | Change | Notes                                                                                          |
| ----------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| `database/migrations/2026_09_18_000000_add_session_end_to_episodes.php` | new    | `ends_at`; backfill; content clean-up; partial index                                           |
| `app/Enums/EpisodeProvider.php`                                         | edit   | `Link`; the `connection()` arm; a sentence in the class docblock                               |
| `app/Enums/EpisodeType.php`                                             | edit   | `Live` allows `Link`; its docblock                                                             |
| `app/Models/Episode.php`                                                | edit   | `ends_at` fillable and cast; `isCancelled()`, `lengthMinutes()`                                |
| `app/Services/EpisodeService.php`                                       | edit   | `add()` signature; `guardLiveSessionTime()`; `lengthOrDefault()`                               |
| `app/Http/Requests/Share/StoreEpisodeRequest.php`                       | edit   | `length_minutes`, `records`, live `reference`; `messages()`; three accessors; `content()`      |
| `app/Http/Controllers/Share/EpisodeController.php`                      | edit   | `store()` passes the start and the length                                                      |
| `app/Http/Controllers/Share/SeriesController.php`                       | edit   | per-Episode `endsAt`, `lengthMinutes`, `records`, `joinUrl`; the `live` prop                   |
| `config/qori.php`                                                       | edit   | `live`, `materials`, `chats`, `limits.text.material_note`, two `live_prefix` entries           |
| `lang/en/series.php`                                                    | edit   | `providers.link`, `live.*`                                                                     |
| `lang/en/errors.php`                                                    | edit   | `series.length_too_long`                                                                       |
| `resources/js/components/series/LiveSessionPanel.vue`                   | new    | `form` and `row` modes; copy as props                                                          |
| `resources/js/components/series/SessionTime.vue`                        | edit   | optional `endsAt`, rendered through `formatRange()`                                            |
| `resources/js/pages/share/series/Show.vue`                              | edit   | mounts the panel twice; `link` in `allowed`; reference block hidden for live; `EpisodeSummary` |
| `database/seeders/DesignReviewSeeder.php`                               | edit   | `:356` content; `:433` `ends_at`                                                               |
| `docs/flows/series.md`                                                  | edit   | shape, provider table, a live subsection, "Not built yet"                                      |
| `docs/tinker/series.md`                                                 | edit   | the live recipe at `:48-52`                                                                    |
| `tests/Feature/Series/LiveEpisodeEndTest.php`                           | new    | 15 cases                                                                                       |
| `tests/Feature/Series/LiveSessionTest.php`                              | edit   | 1 case: the service call passes `startsAt:`; `scene()` freezes the clock                       |
| `tests/Feature/Share/EpisodeServiceTest.php`                            | edit   | 1 case: the same                                                                               |
| `tests/Feature/Series/EpisodeRoutesTest.php`                            | edit   | 1 case gains two assertions; a docblock                                                        |

No route file changes: `share.series.episodes.store` takes two more fields on
the same path. Nothing under `resources/js/routes` moves, so Wayfinder and
`qori:reachability` are unaffected. `tests/Feature/DesignReviewFixtureTest.php`
reads nothing from the live Episode's content and does not change.

## Database

| Table      | Column    | Type      | Null | Default | Index / constraint                                                             |
| ---------- | --------- | --------- | ---- | ------- | ------------------------------------------------------------------------------ |
| `episodes` | `ends_at` | timestamp | yes  | null    | partial `episodes_live_ends_at_index` on `(ends_at) WHERE type = 'live'`       |
| `episodes` | `content` | jsonb     | —    | —       | data only: `starts_at` key removed from every row; `records` true on live rows |

Backfill, in the same migration: `ends_at = starts_at + interval '60 minutes'`
where `type = 'live'` and `starts_at` is not null. Sixty is a literal — see
the decision above.

Migration: `database/migrations/2026_09_18_000000_add_session_end_to_episodes.php`

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

/**
 * A live Episode has an end and one start (D-026, T-123).
 *
 * `?` in a raw statement is a PDO placeholder, so the jsonb checks below use
 * jsonb_exists() rather than the `?` operator.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('episodes', function (Blueprint $table): void {
            $table->timestamp('ends_at')->nullable();
        });

        // Sixty minutes as a literal: the default on the day this ran. A
        // migration is a record, and reading config here would let a later
        // change to qori.live.default_length_minutes rewrite what a fresh
        // checkout does to old rows.
        DB::statement("UPDATE episodes SET ends_at = starts_at + interval '60 minutes' WHERE type = 'live' AND starts_at IS NOT NULL");

        // The column is the only start from now on.
        DB::statement("UPDATE episodes SET content = content - 'starts_at' WHERE content IS NOT NULL AND jsonb_exists(content, 'starts_at')");

        // Every live row says whether it records; the default is yes.
        DB::statement("UPDATE episodes SET content = coalesce(content, '{}'::jsonb) || '{\"records\": true}'::jsonb WHERE type = 'live' AND NOT jsonb_exists(coalesce(content, '{}'::jsonb), 'records')");

        DB::statement("CREATE INDEX episodes_live_ends_at_index ON episodes (ends_at) WHERE type = 'live'");
    }

    public function down(): void
    {
        DB::statement('DROP INDEX IF EXISTS episodes_live_ends_at_index');

        Schema::table('episodes', function (Blueprint $table): void {
            $table->dropColumn('ends_at');
        });

        // The content keys are left as they are: nothing reads a start from
        // content any more, and a `records` key does no harm to old code.
    }
};
```

## Code

```php
// app/Enums/EpisodeProvider.php

// The class docblock (:5-13) gains one sentence after "may never have
// existed.": Link is the plainest case — a pasted URL from a host Qori has no
// connection for at all (D-025) — so the two enums stay apart.

/**
 * A pasted meeting link from a host Qori has no folder for (D-025): Meet, or
 * anything else. The unconnected tier; connection() answers null.
 */
case Link = 'link';

// connection(): one more arm in the exhaustive match (:44-50)
self::Link => null,
```

```php
// app/Enums/EpisodeType.php

// The docblock at :17 names Zoom and Teams alone; it becomes:
/** A scheduled meeting — Zoom, Teams or a pasted link from any host (§8.1, D-025). Qori integrates, never hosts. */
case Live = 'live';

// allowedProviders() (:31-36)
self::Live => [EpisodeProvider::Zoom, EpisodeProvider::Teams, EpisodeProvider::Link],
```

```php
// app/Models/Episode.php

/**
 * @property ?Carbon $starts_at
 * @property ?Carbon $ends_at
 */

/** @var list<string> */
protected $fillable = ['title', 'position', 'type', 'provider', 'content', 'starts_at', 'ends_at', 'is_preview'];

// casts(): beside 'starts_at' => 'datetime'
'ends_at' => 'datetime',

/** Whether a creator has cancelled this session. T-134 writes the key; nothing does yet. */
public function isCancelled(): bool;
// isset($this->content['cancelled_at'])

/**
 * The scheduled length, derived from the two columns so it is never stored
 * twice. Null unless both are set, which for a live Episode means "no start".
 */
public function lengthMinutes(): ?int;
// $this->starts_at === null || $this->ends_at === null ? null : (int) $this->starts_at->diffInMinutes($this->ends_at)
```

```php
// app/Services/EpisodeService.php

use InvalidArgumentException;

/**
 * Add an episode to the end of a series.
 *
 * A live Episode's start and length are parameters, not content: the column
 * is the one authority (D-026). Both are ignored for any other kind — a PDF
 * does not start.
 *
 * @param  array<string, mixed>  $content  never carries 'starts_at'
 */
public function add(
    Series $series,
    string $title,
    EpisodeType $type,
    EpisodeProvider $provider,
    array $content = [],
    bool $isPreview = false,
    ?CarbonImmutable $startsAt = null,
    ?int $lengthMinutes = null,
): Episode;
// if (array_key_exists('starts_at', $content)) {
//     throw new InvalidArgumentException('A live episode\'s start is the $startsAt parameter, never $content[\'starts_at\'] (T-123).');
// }
// $this->guardSeriesUnlocked($series->group, 'add an episode');
// $this->guardEpisodeType($type, $provider);
// $this->guardEpisodeLimit($series);
// $this->guardLiveSessionTime($series, $type, $startsAt, creating: true);
// $length = $this->lengthOrDefault($lengthMinutes);
// $live = $type === EpisodeType::Live;
// $existing = $series->episodes()->count();
// create([
//     'title' => trim($title),
//     'position' => $existing + 1,
//     'type' => $type,
//     'provider' => $provider,
//     'content' => $live ? array_merge(['records' => true], $content) : $content,
//     'starts_at' => $live ? $startsAt : null,
//     'ends_at' => $live ? $startsAt?->addMinutes($length) : null,
//     'is_preview' => $isPreview,
// ]);

/**
 * A live session needs a zone somebody chose, and — when it is being created —
 * a start still ahead. Editing may set a past start (D-026), so T-124 passes
 * creating: false. The body of today's :81-113 with the parameter typed.
 */
private function guardLiveSessionTime(Series $series, EpisodeType $type, ?CarbonImmutable $startsAt, bool $creating): void;
// return unless Live; timezone check as today (:87-97, errors.series.timezone_required);
// return if $startsAt === null;
// if ($creating && $startsAt->isPast()) → AppException::invalidRequest('errors.series.starts_in_past', devMessage: ...)

/**
 * The length a live Episode runs for: the configured default when none was
 * given, refused above the configured maximum. Under a minute is a programmer
 * error — the Form Request's min:1 is the wall a person meets.
 */
private function lengthOrDefault(?int $lengthMinutes): int;
// $max = (int) config('qori.live.max_length_minutes');
// $length = $lengthMinutes ?? (int) config('qori.live.default_length_minutes');
// if ($length < 1) throw new InvalidArgumentException("A live episode's length must be at least one minute; got {$length}.");
// if ($length > $max) throw AppException::invalidRequest(
//     'errors.series.length_too_long',
//     ['hours' => (string) intdiv($max, 60)],
//     devMessage: "Refused a live episode of {$length} minutes; the maximum is {$max}.",
// );
// return $length;
```

```php
// app/Http/Requests/Share/StoreEpisodeRequest.php

public function rules(): array
{
    $live = $this->episodeType() === EpisodeType::Live;

    return [
        'title' => ['required', 'string', 'max:200'],
        'type' => ['required', Rule::enum(EpisodeType::class)],
        'provider' => ['required', Rule::enum(EpisodeProvider::class)],
        'is_preview' => ['boolean'],
        // A live Episode's reference is a join link Qori hands to Peers: the
        // pasted tier, https and at most 2048 characters (D-025). Everything
        // else is a path or an id, as before.
        'reference' => $live
            ? ['nullable', 'string', 'url:https', 'max:2048']
            : ['nullable', 'string', 'max:500'],
        'starts_at' => $live ? ['required', 'date', 'after:now'] : ['nullable', 'date'],
        // Minutes. Absent means the configured default; the service fills it.
        'length_minutes' => $live
            ? ['nullable', 'integer', 'min:1', 'max:'.(int) config('qori.live.max_length_minutes')]
            : ['exclude'],
        // "Recorded" or "Live only" (D-026). Absent means recorded.
        'records' => $live ? ['nullable', 'boolean'] : ['exclude'],
    ];
}

/** @return array<string, string> */
public function messages(): array;
// 'length_minutes.max' => __('errors.series.length_too_long.message', [
//     'hours' => (string) intdiv((int) config('qori.live.max_length_minutes'), 60),
// ]),

/** The start as a UTC instant, or null. prepareForValidation() has already merged it as ISO 8601 with an offset. */
public function startsAt(): ?CarbonImmutable;
// $this->filled('starts_at') ? CarbonImmutable::parse((string) $this->input('starts_at'))->utc() : null

/** Null means "use the default"; EpisodeService fills it. */
public function lengthMinutes(): ?int;
// $this->filled('length_minutes') ? (int) $this->input('length_minutes') : null

/** Absent means recorded: the common case, and the one the migration wrote. */
public function records(): bool;
// $this->has('records') ? $this->boolean('records') : true

/** @return array<string, mixed> */
public function content(): array
{
    $reference = (string) $this->input('reference', '');

    return match ($this->episodeProvider()) {
        EpisodeProvider::Vimeo => ['vimeo_id' => $reference],
        // The start is the column's alone (D-026); the link is optional.
        EpisodeProvider::Zoom, EpisodeProvider::Teams, EpisodeProvider::Link => [
            ...array_filter(['join_url' => $reference !== '' ? $reference : null]),
            'records' => $this->records(),
        ],
        default => ['path' => $reference],
    };
}
```

The comment at `StoreEpisodeRequest.php:147-149` ("A live episode's join link
arrives from Zoom/Teams once that integration exists") is reworded: the link
is pasted, from any host, and stays optional.

```php
// app/Http/Controllers/Share/EpisodeController.php — store() (:43-53), two more arguments
$episode = $episodeService->add(
    $series,
    $request->string('title')->toString(),
    $request->episodeType() ?? EpisodeType::File,
    $request->episodeProvider() ?? EpisodeProvider::CloudflareR2,
    $request->content(),
    $request->boolean('is_preview'),
    $request->startsAt(),
    $request->lengthMinutes(),
);
// The toast (:55-69) is unchanged.
```

```php
// app/Http/Controllers/Share/SeriesController.php — show(): the Episode map (:158-166) gains four keys
'endsAt' => $episode->ends_at?->toIso8601String(),
'lengthMinutes' => $episode->lengthMinutes(),
// The switch is a live Episode's; every other kind answers null, as joinUrl does (and as T-124 declares the same line).
'records' => $episode->isLive() ? (bool) ($episode->content['records'] ?? true) : null,
// The creator pasted it. The public page never carries it (D-024).
'joinUrl' => $episode->isLive() ? ($episode->content['join_url'] ?? null) : null,

// and one more top-level prop, beside 'timezone' (:174-177)
'live' => [
    // The same numbers the validator and the service read (D-026).
    'defaults' => [
        'lengthMinutes' => (int) config('qori.live.default_length_minutes'),
        'maxLengthMinutes' => (int) config('qori.live.max_length_minutes'),
    ],
    'providerLabel' => __('series.providers.link'),
    // Every sentence the panel shows, so it holds no English of its own.
    'copy' => [
        'joinLink' => __('series.live.join_link'),
        'joinLinkHelp' => $terminology->line('series.live.join_link_help', [], $scope),
        'starts' => __('series.live.starts', ['zone' => $scope?->timezone() ?? Timezones::fallback()]),
        'startsHelp' => __('series.live.starts_help'),
        'length' => __('series.live.length'),
        'lengthHelp' => __('series.live.length_help', ['hours' => (string) intdiv((int) config('qori.live.max_length_minutes'), 60)]),
        'records' => __('series.live.records'),
        'recorded' => $terminology->line('series.live.recorded', [], $scope),
        'liveOnly' => __('series.live.live_only'),
        'recordedBadge' => __('series.live.recorded_badge'),
        'liveOnlyBadge' => __('series.live.live_only_badge'),
        'noLink' => __('series.live.no_link'),
    ],
],
```

```php
// config/qori.php — after 'limits' (:73-77): the block every classroom task reads, declared once (D-026, D-028, D-029, D-030).

/*
|--------------------------------------------------------------------------
| Live sessions
|--------------------------------------------------------------------------
|
| Every number the classroom stream reads, declared here by T-123 so no
| later task edits this file. Copy interpolates these and never restates
| them (D-026). Times are measured from the Episode's starts_at and ends_at.
|
*/

'live' => [
    // Join is offered from this many minutes before starts_at (T-125)...
    'join_opens_minutes' => 15,
    // ...until this many minutes after ends_at (T-125).
    'join_closes_after_minutes' => 15,
    // After that, "Still in the session? Join again" for this long past ends_at (T-125).
    'join_grace_after_minutes' => 120,
    // The length the form pre-fills and the service assumes, in minutes (T-123).
    'default_length_minutes' => 60,
    // The longest a session may be scheduled for: twelve hours. Refused above it (T-123).
    'max_length_minutes' => 720,
    // How long after ends_at a session waits for its recording before the card says it is overdue (T-127).
    'recording_wait_hours' => 48,
    // How long after ends_at the Group owner is told a recording is missing. Provisional (T-129).
    'creator_nudge_hours' => 12,
    // A recording published later than this after the session sends no email (T-128).
    'notice_window_days' => 7,
    // How many times a failed notice is retried before it is left for alerting (T-128).
    'notice_attempts' => 3,
    // At most this many notices leave in one run of qori:sessions:notify (T-128).
    'sends_per_run' => 200,
    // A found recording whose start is further than this from starts_at is held for review (T-143).
    'match_tolerance_minutes' => 30,
    // A found recording shorter than this is held for review (T-143).
    'min_recording_minutes' => 5,
    // How often qori:recordings:find looks again, by hours since ends_at (T-143).
    'check_backoff' => [
        ['until_hours' => 3, 'every_minutes' => 15],
        ['until_hours' => 24, 'every_minutes' => 60],
        ['until_hours' => 48, 'every_minutes' => 240],
    ],
    // The one reminder every plan above Free gets: a day before (T-138).
    'reminder_minutes_before' => 1440,
    // Check now and a deliberate re-send are throttled to one per this many seconds (T-140, T-144).
    'recheck_seconds' => 60,
],

/*
|--------------------------------------------------------------------------
| Materials and chats
|--------------------------------------------------------------------------
|
| Sanity caps on every plan, not tier levers (D-029, D-030). Provisional.
|
*/

'materials' => [
    // Rows per Episode and per Series; the refusal names the number (T-130, T-137).
    'per_episode' => 30,
    'per_series' => 30,
],

'chats' => [
    // One chat card per Series in v1; the column allows more (T-132).
    'per_series' => 1,
    // The largest QR image a creator may upload, in megabytes (T-132).
    'code_max_mb' => 2,
],

// 'limits' => ['text' => [...]] gains, beside 'series_summary' (:75):
'material_note' => 2000,   // a material's note, shared with its textarea (T-130)

// 'storage' => ['live_prefix' => [...]] (:141-143) gains two entries:
'material' => 'materials',      // a material uploaded to Qori (T-130)
'chat_code' => 'chat-codes',    // a chat's QR image (T-132)
```

```ts
// resources/js/components/series/LiveSessionPanel.vue

/** The live facts of one Episode row, as SeriesController::show() sends them. */
export interface LiveEpisode {
    startsAt: string | null;
    endsAt: string | null;
    lengthMinutes: number | null;
    /** Null off a live Episode; never null on one. */
    records: boolean | null;
    joinUrl: string | null;
}

/** Every sentence the panel shows, from lang/en/series.php through the controller. */
export interface LiveCopy {
    joinLink: string;
    joinLinkHelp: string;
    starts: string;
    startsHelp: string;
    length: string;
    lengthHelp: string;
    records: string;
    recorded: string;
    liveOnly: string;
    recordedBadge: string;
    liveOnlyBadge: string;
    noLink: string;
}

const props = defineProps<{
    /** `form`: the fields inside the New Episode form. `row`: the facts on one live row. */
    mode: 'form' | 'row';
    /** Required in `row` mode; ignored in `form` mode. */
    episode?: LiveEpisode | null;
    /** The Group's zone, resolved: what a typed time is read in and what a row is shown in. */
    timezone: string;
    defaults: { lengthMinutes: number; maxLengthMinutes: number };
    /** The parent Form's errors, in `form` mode. */
    errors?: Record<string, string | undefined>;
    copy: LiveCopy;
}>();
```

In `form` mode the panel renders, inside the parent `<Form>` (it adds no form
of its own): `<Input id="live-join-url" name="reference" type="url" />` under
`copy.joinLink` with `copy.joinLinkHelp` beneath and `errors.reference`;
`<Input id="live-starts-at" name="starts_at" type="datetime-local" required />`
under `copy.starts` with `copy.startsHelp` and `errors.starts_at` — the block
that leaves `Show.vue:604-619`; `<Input id="live-length" name="length_minutes"
type="number" min="1" :max="defaults.maxLengthMinutes"
:model-value="defaults.lengthMinutes" />` under `copy.length` with
`copy.lengthHelp` and `errors.length_minutes`; and the Recorded switch under
`copy.records`: a hidden `<input type="hidden" name="records" value="0" />`
followed by the checkbox
`<input id="live-records" type="checkbox" name="records" value="1" checked />`
labelled `copy.recorded`, with `copy.liveOnly` as the line beneath it saying
what unticking means, and `errors.records`. The hidden `0` is what an unticked
box posts, and the same two controls are `T-124`'s edit form in this
component, so one switch has one shape. In `row` mode it renders
`<SessionTime :starts-at="episode.startsAt" :ends-at="episode.endsAt" :timezone="timezone" />`
when `startsAt` is set, then `copy.recordedBadge` when `records` is true or
`copy.liveOnlyBadge` when it is false (never null on a live row) in the row's
small uppercase style (`Show.vue:426-430`), then `copy.noLink` when `joinUrl`
is null. No other English.

```ts
// resources/js/components/series/SessionTime.vue — one more prop
const props = defineProps<{
    startsAt: string;
    /** The scheduled end, ISO 8601 with an offset. When given, the two instants render as one range through Intl.DateTimeFormat.formatRange(). */
    endsAt?: string;
    timezone?: string;
}>();

// formatted (:44-62): the same computed, with formatRange() in place of toLocaleString()
// const start = new Date(props.startsAt);
// const end = props.endsAt ? new Date(props.endsAt) : null;
// if (Number.isNaN(start.getTime())) return '';
// const format = (options: Intl.DateTimeFormatOptions): string => {
//     const formatter = new Intl.DateTimeFormat(undefined, options);
//     return end && !Number.isNaN(end.getTime()) ? formatter.formatRange(start, end) : formatter.format(start);
// };
// try { return format({ ...parts, ...(props.timezone ? { timeZone: props.timezone } : {}) }); } catch { return format(parts); }
```

`formatRange()` collapses whatever the two instants share — on one day the
date and the zone, so the row reads the date once and then both times — and
names both dates when a session crosses midnight, with no hand-written day
comparison. The existing fallback (a zone this browser does not carry → the
reader's own zone) covers both calls. The template is unchanged: one
`<time :datetime="startsAt">` holding the range. `T-125` adds only
`groupTimezone` to this component, on the same `format()` call, and cites
this rule rather than restating it.

`resources/js/pages/share/series/Show.vue`:

- `EpisodeSummary` (`:33-41`) gains `endsAt: string | null`,
  `lengthMinutes: number | null`, `records: boolean | null`,
  `joinUrl: string | null`.
- The props (`:112-136`) gain
  `live: { defaults: { lengthMinutes: number; maxLengthMinutes: number }; providerLabel: string; copy: LiveCopy }`,
  importing `LiveCopy` from the panel.
- `allowed.live` (`:202`) becomes `['zoom', 'teams', 'link']`; the comment
  above it (`:194-196`) says "Mirrors Episode::allowedProviders()", a method
  that is on the enum, and is reworded to `EpisodeType::allowedProviders()`;
  `providerLabels` (`:290-296`) gains `link: props.live.providerLabel`.
- `referenceLabel` (`:236-244`) and `referencePlaceholder` (`:257-263`) lose
  their `zoom`/`teams` arms; the reference block (`:569-601`) takes
  `v-if="!isLive"`.
- The `starts_at` block (`:604-619`) is replaced by
  `<LiveSessionPanel v-if="isLive" mode="form" :timezone="timezone.name" :defaults="live.defaults" :errors="errors" :copy="live.copy" />`.
  The timezone notice (`:627-632`) stays.
- The row's `<template v-if="episode.startsAt">` with `SessionTime`
  (`:413-419`) is replaced by
  `<LiveSessionPanel v-if="episode.type === 'live'" mode="row" :episode="episode" :timezone="timezone.name" :defaults="live.defaults" :copy="live.copy" />`;
  the page's own `SessionTime` import goes if nothing else uses it.

`database/seeders/DesignReviewSeeder.php`: `:356` becomes
`['Live clinic: bring a room', EpisodeType::Live, EpisodeProvider::Zoom, ['join_url' => 'https://zoom.us/j/91827405566', 'records' => true], false]`;
`episodes()` (`:422-436`) writes `'ends_at' => $type === EpisodeType::Live ? Carbon::now()->addDays(11)->setTime(19, 30) : null`
beside `starts_at` (`:433`) — an hour, the same length the migration gives an
old row.

`docs/tinker/series.md:48-52` becomes:

```php
use Carbon\CarbonImmutable;

$episodes->add($series->fresh(), 'Live Q&A', EpisodeType::Live, EpisodeProvider::Zoom, [
    'join_url' => 'https://zoom.us/j/987654321',
], startsAt: CarbonImmutable::now()->addWeek(), lengthMinutes: 90);

// From Meet or any other host: the pasted tier, no connection behind it (D-025).
$episodes->add($series->fresh(), 'Office hours', EpisodeType::Live, EpisodeProvider::Link, [
    'join_url' => 'https://meet.google.com/abc-defg-hij',
], startsAt: CarbonImmutable::now()->addWeeks(2));

$series->fresh()->orderedEpisodes()->first()->lengthMinutes();   // 90
```

`docs/flows/series.md`: the shape block (`:16-22`) gains `ends_at` ("live
episodes only; the scheduled end") and `link` in the provider line, and names
the live `content` keys `join_url` and `records`; the provider table (`:79-84`)
reads `live` → `zoom`, `teams`, `link`; `:87` names `Episode::allowedProviders()`,
which is `EpisodeType::allowedProviders()`; a new "Live Episodes" subsection after
"Adding episodes" says the start is typed in the Group's zone and converted by
`StoreEpisodeRequest::prepareForValidation()`, the length becomes `ends_at`,
`records` is the creator's switch, and a pasted link is stored and never
followed (`D-025`); "Not built yet" (`:125-129`) says instead that accesses,
progress, playback and uploads are built (`accesses.md`, `storage.md`), and
that for a live Episode nothing schedules the meeting, a Peer has no Join
yet (`T-125`) and no recording is kept (`T-126`).

## Copy

| Key                                        | File                 | English                                                                                                                                                        |
| ------------------------------------------ | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `series.providers.link`                    | `lang/en/series.php` | Another meeting link — Meet or anything else                                                                                                                   |
| `series.live.join_link`                    | `lang/en/series.php` | Join link                                                                                                                                                      |
| `series.live.join_link_help`               | `lang/en/series.php` | Paste the link your :peer_plural will follow. Check the meeting lets anyone with the link in, so nobody needs an account with the host. Qori never follows it. |
| `series.live.starts`                       | `lang/en/series.php` | Starts, in :zone                                                                                                                                               |
| `series.live.starts_help`                  | `lang/en/series.php` | Everyone is shown this time converted to their own, so enter it as it reads where you are.                                                                     |
| `series.live.length`                       | `lang/en/series.php` | Length, in minutes                                                                                                                                             |
| `series.live.length_help`                  | `lang/en/series.php` | Up to :hours hours. Qori uses it to say when the session is scheduled to end.                                                                                  |
| `series.live.records`                      | `lang/en/series.php` | Will this session be recorded?                                                                                                                                 |
| `series.live.recorded`                     | `lang/en/series.php` | Recorded — :peer_plural who miss it can watch it here afterwards                                                                                               |
| `series.live.live_only`                    | `lang/en/series.php` | Live only — there won't be a recording                                                                                                                         |
| `series.live.recorded_badge`               | `lang/en/series.php` | Recorded                                                                                                                                                       |
| `series.live.live_only_badge`              | `lang/en/series.php` | Live only                                                                                                                                                      |
| `series.live.no_link`                      | `lang/en/series.php` | No join link yet                                                                                                                                               |
| `errors.series.length_too_long.message`    | `lang/en/errors.php` | A live session can run for up to :hours hours.                                                                                                                 |
| `errors.series.length_too_long.resolution` | `lang/en/errors.php` | Split a longer day into more than one session.                                                                                                                 |

`:zone` is the Group's resolved zone (`Group::timezone()`,
`app/Models/Group.php:221-232`), interpolated by `SeriesController::show()`.
`:hours` is `intdiv(config('qori.live.max_length_minutes'), 60)` — twelve —
interpolated in three places (the request's `messages()`, the service's
exception, the controller's `lengthHelp`) and written in none.
`series.live.starts_help` is the sentence leaving `Show.vue:614-617`; the
inline label "Starts, in {{ timezone.name }}" (`:605-607`) becomes
`series.live.starts`. The two lines carrying `:peer_plural` go through
`Terminology::line()` with the Group; the rest through `__()`. "Meet" in the
provider label is `D-016`'s stated exception to the no-vendor-names rule —
vendor names may appear in provider-choice copy because the person is choosing
between those vendors — as `D-025` extends it to the pasted tier, and reaches
Vue as a prop. `series.session_scheduled` is unchanged.

## Routes

None. `POST /g/{group}/series/{seriesId}/episodes` (`share.series.episodes.store`,
`routes/share/episodes.php:19-20`) takes `length_minutes` and `records` on the
same path.

## Tests

**New: `tests/Feature/Series/LiveEpisodeEndTest.php` — 15 cases**
(`RefreshDatabase`; a private `scene()` as `LiveSessionTest.php:41-60` builds,
with the Group's `timezone` `Australia/Melbourne` and `plan` `start`, whose
first line is `CarbonImmutable::setTestNow('2026-09-01T00:00:00+00:00')`, so
the literal 1 October dates below stay ahead of "now" whatever day the suite
runs — Carbon 3 keeps one test clock for `Carbon` and `CarbonImmutable`
(`Test::setTestNow()` delegates to `FactoryImmutable::getDefaultInstance()`),
so the one call pins `now()`, `isPast()` and the validator's `after:now`, and
Laravel's test lifecycle clears it after every case; a private
`melbourne9am()` returning
`CarbonImmutable::parse('2026-10-01T09:00:00', 'Australia/Melbourne')->utc()`,
which is `2026-09-30T23:00:00+00:00` as `LiveSessionTest.php:112-134` proves;
a private `livePayload(array $overrides = []): array` mirroring
`LiveSessionTest.php:63-73` — `title` 'Live Q&A', `type` `live`, `provider`
`zoom`, `reference` 'https://zoom.us/j/123', `starts_at` '2026-10-01T09:00',
with `$overrides` spread last — for every POST to the store route; the store
URL as `LiveSessionTest.php:75-81`)

1. `test_the_end_is_the_start_plus_the_length` — `add()` with
   `startsAt: melbourne9am()`, `lengthMinutes: 90`; `ends_at` is
   `2026-10-01T00:30:00+00:00`, a literal; `lengthMinutes()` is 90.
2. `test_the_length_defaults_from_config` — `add()` with the start and no
   length; `ends_at` is `2026-10-01T00:00:00+00:00`; `lengthMinutes()` equals
   `config('qori.live.default_length_minutes')`.
3. `test_a_length_over_the_maximum_is_refused_with_the_hours_named` — `add()`
   with 721 throws `AppException` with `ErrorCode::InvalidRequest`, a message
   containing `12` and a non-null `resolution()`; then a POST of
   `livePayload(['length_minutes' => 721])` has errors on `length_minutes` and
   writes no Episode.
4. `test_a_length_under_a_minute_is_a_programmer_error` —
   `expectException(InvalidArgumentException::class)`; `add()` with
   `lengthMinutes: 0`.
5. `test_the_migration_gives_existing_live_rows_an_end_and_one_start` —
   `$migration = require database_path('migrations/2026_09_18_000000_add_session_end_to_episodes.php')`;
   `$migration->down()`; then `DB::table('episodes')->insert([...])` with
   exactly these two rows on `scene()`'s Series — the query builder bypasses
   `HasUlids` and every model default, so each column is supplied, the id in
   the lowercase form `HasUlids` writes (as `tests/Feature/Series/SeriesPriceTest.php:197`
   does):

    ```php
    [
        'id' => Str::lower((string) Str::ulid()),
        'series_id' => $series->getKey(),
        'title' => 'Old live clinic',
        'position' => 1,
        'type' => 'live',
        'provider' => 'zoom',
        'content' => '{"join_url":"https://zoom.us/j/1","starts_at":"2026-10-01T09:00:00+00:00"}',
        'starts_at' => '2026-10-01 09:00:00',
        'is_preview' => false,
        'created_at' => now(),
        'updated_at' => now(),
    ],
    [
        'id' => Str::lower((string) Str::ulid()),
        'series_id' => $series->getKey(),
        'title' => 'Old notes',
        'position' => 2,
        'type' => 'file',
        'provider' => 'cloudflare_r2',
        'content' => '{"path":"a.pdf"}',
        'starts_at' => null,
        'is_preview' => false,
        'created_at' => now(),
        'updated_at' => now(),
    ],
    ```

    then `$migration->up()`; the live row's `ends_at` is `2026-10-01 10:00:00`,
    its content decodes to exactly
    `['join_url' => 'https://zoom.us/j/1', 'records' => true]`; the file row's
    content still decodes to `['path' => 'a.pdf']` and its `ends_at` is null;
    `DB::select("SELECT 1 FROM pg_indexes WHERE indexname = 'episodes_live_ends_at_index'")`
    has one row.

6. `test_a_pasted_link_is_allowed_for_a_live_episode_and_refused_for_a_file` —
   `add()` Live + `Link` with `['join_url' => 'https://meet.google.com/abc-defg-hij']`
   stores `provider` `EpisodeProvider::Link`; File + `Link` throws
   `AppException` for `errors.series.provider_not_allowed`;
   `EpisodeType::Live->allowedProviders()` is `[Zoom, Teams, Link]`.
7. `test_a_pasted_link_needs_no_connection` — `EpisodeProvider::Link->connection()`
   is null; `isQoriHosted()` false.
8. `test_content_never_carries_a_start` — a POST of `livePayload()`, whose
   `starts_at` is '2026-10-01T09:00' and whose `reference` is set: the
   Episode's `content` keys are exactly `join_url` and `records`, and
   `starts_at` is `2026-09-30T23:00:00+00:00`;
   then `add()` given `['starts_at' => '2026-10-01T09:00:00+00:00']` in
   `$content` throws `InvalidArgumentException` and writes nothing.
9. `test_records_is_stored_and_defaults_to_true` — a POST of `livePayload()`,
   which carries no `records`, stores `content['records']` true; a POST of
   `livePayload(['records' => 0])` stores false;
   `add()` with content lacking the key stores true; `add()` with
   `['records' => false]` stores false.
10. `test_a_past_start_is_still_refused_on_create` — `add()` with
    `startsAt: CarbonImmutable::now()->subDay()` (31 August 2026 against the
    frozen clock) throws `AppException` for `errors.series.starts_in_past`;
    nothing written.
11. `test_a_live_join_link_must_be_https_and_may_be_long` — a POST of
    `livePayload(['reference' => 'http://zoom.us/j/1'])` has errors on
    `reference`; a POST of `livePayload(['reference' => $long])`, where
    `$long` is a 600-character `https://` link, has none and stores it in
    `content['join_url']`; a POST of
    `['title' => 'Notes', 'type' => 'file', 'provider' => 'cloudflare_r2', 'reference' => $long]`
    has errors on `reference` (`max:500` unchanged).
12. `test_length_minutes_and_is_cancelled_read_the_row` — after `add()` with
    90 minutes, `lengthMinutes()` is 90 and `isCancelled()` false; a File
    Episode answers null; after
    `$episode->update(['content' => [...$episode->content, 'cancelled_at' => now()->toIso8601String()]])`,
    `isCancelled()` is true.
13. `test_the_creator_page_carries_the_end_the_switch_and_the_link` — POST
    `livePayload()` (its `reference` is 'https://zoom.us/j/123'), then `add()`
    a File Episode ('Notes', `CloudflareR2`, `['path' => 'a.pdf']`), then GET
    `share.series.show` and `assertInertia`: `series.episodes.0.endsAt` is
    `2026-10-01T00:00:00+00:00`, `lengthMinutes` 60, `records` true, `joinUrl`
    `https://zoom.us/j/123`; `series.episodes.1.endsAt`, `lengthMinutes`,
    `records` and `joinUrl` are all null — the switch is a live Episode's;
    `live.defaults.lengthMinutes` and `maxLengthMinutes` equal config;
    `live.providerLabel` equals `__('series.providers.link')`;
    `live.copy.starts` contains `Australia/Melbourne`; `live.copy.lengthHelp`
    contains `12`.
14. `test_a_start_on_a_file_episode_is_dropped` — `add()` File + CloudflareR2
    with `startsAt: melbourne9am()`, `lengthMinutes: 90`: `starts_at` and
    `ends_at` both null.
15. `test_the_public_page_lists_no_link_and_no_switch` — add the live
    Episode, `SeriesService::publish()`, GET `route('series.public', …)` and
    `assertInertia`: `series.episodes.0` has `startsAt` and no `joinUrl`, no
    `records`, no `endsAt` key (`D-024`; `T-135` adds the next session on
    purpose).

**Changed:**

- `tests/Feature/Series/LiveSessionTest.php` —
  `test_the_guard_is_in_the_service_not_only_the_request` (`:180-186`) passes
  `['join_url' => 'https://zoom.us/j/123']` and
  `startsAt: CarbonImmutable::parse('2026-10-01T09:00:00+00:00')`; the
  assertion is unchanged. `scene()` (`:41-60`) gains
  `CarbonImmutable::setTestNow('2026-09-01T00:00:00+00:00')` as its first
  line, for the same reason as above: its `liveEpisodePayload()` posts
  1 October 2026 as a literal and nothing pins "now", so every case that
  creates a live Episode would start failing with `starts_in_past` on that
  day. `test_a_session_in_the_past_is_refused` (`:198-212`) still refuses,
  because `Carbon::now()->subDay()` reads the frozen clock. The eight other
  cases pass as written: `liveEpisodePayload()` sends an `https` link and no
  length, so the default applies.
- `tests/Feature/Share/EpisodeServiceTest.php` —
  `test_a_live_episode_records_its_provider_and_start` (`:100-115`) passes
  `startsAt: CarbonImmutable::now()->addWeek()` and content
  `['meeting_id' => '123456789', 'join_url' => 'https://zoom.us/j/123']`, and
  gains `assertNotNull($episode->ends_at)`.
  `test_episode_content_is_stored_as_a_queryable_document` (`:120-142`) is
  unchanged: a live Episode with no start is still accepted by the service.
- `tests/Feature/Series/EpisodeRoutesTest.php` —
  `test_a_reference_is_required_except_for_live_episodes` (`:133-153`) asserts
  the live Episode's `content` has `records` true and no `starts_at`, and
  first freezes the clock the same way, since it posts the same literal
  1 October start (`:148`); its docblock (`:129-132`) says the link is pasted
  from any host rather than arriving from Zoom or Teams.

Total: 15 new cases; 3 existing cases change, and one existing helper
(`LiveSessionTest::scene()`) freezes the clock.

## Acceptance

- [x] A creator adds a live Episode with a start, a length of 90 minutes and
      "Recorded", and the row reads the start and the end in the Group's zone
      with the zone named, with "Recorded" beside it
- [x] A creator picks "Another meeting link — Meet or anything else", pastes a
      Meet link, and the Episode is stored `provider = link` with the link in
      `content.join_url` and nothing asking for a connection
- [x] Every live Episode that existed before the migration has `ends_at` an
      hour after its start, `records` true and no `starts_at` in its
      `content`; after `php artisan qori:reset full --force` the design-review
      live clinic shows its end
- [x] A length over twelve hours is refused on the field with the hours named,
      and no Episode is written
- [x] The `docs/tinker/series.md` recipe runs as written, with the start and
      the length as parameters
- [x] `docs/flows/series.md` describes `ends_at`, `link` and the live
      `content` keys, and no longer claims accesses, progress, playback or
      uploads are unbuilt
- [x] The public page's Episode entries carry no link and no switch
- [x] Every key in `config('qori.live')`, `qori.materials`, `qori.chats`,
      `qori.limits.text.material_note` and the two new `live_prefix` entries
      exists with a comment, and no number from them is written into a
      sentence
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Added during execution

| Path                                        | Change | Reason                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/Feature/Storage/OpenEpisodeTest.php` | edit   | `T-089` landed on `main` first, and its two live cases passed the start inside `content`, which `add()` now refuses. As both tasks' Notes ask of whichever lands second, they pass it as `add(..., startsAt:)` with the content `['join_url' => 'https://zoom.us/j/91827405566', 'records' => true]`. Made in the merge into `main`, the first tree that holds both |

## Re-scope log

None.

## Notes

Specified on 17 September 2026 from `D-025` and `D-026` and the classroom
brief; the first task in the creator lane, with no dependency, so it can be
claimed on day one.

`?` in a raw Postgres statement is a PDO placeholder, and `DB::statement()`
with no bindings fails on it. The migration uses `jsonb_exists()` for the two
key checks rather than the `?` operator.

`T-089`'s draft case 8 (`test_a_live_episode_cannot_be_opened`) cites
`LiveSessionTest.php:185` for a live Episode's content, which after this task
carries no `starts_at`. `T-089`'s draft is edited to build its live Episode
through `add()` with `startsAt:`, and the content it then reads is
`['join_url' => …, 'records' => true]`.

For `T-124`: content on create has no `schedule_version`; a missing key reads
as 1 through `Episode::scheduleVersion()` and the first change writes 2
(`T-124`), so this migration has nothing to backfill;
`UpdateEpisodeRequest` should validate `join_url` exactly as `reference` is
validated here for a live Episode (`url:https`, `max:2048`), so the two
requests cannot disagree about the tier.

For `T-125`: `stateFor()` can meet a live Episode whose `starts_at` and
`ends_at` are null, from a service caller — the form never produces one. What
the state is then is `T-125`'s to say.

`docs/flows/storage.md:98-104` lists "Zoom/Teams join links" as unbuilt; a
pasted link has been stored since `StoreEpisodeRequest::content()` wrote it.
That file is `storage`'s and `T-125` creates the live-sessions flow doc, so
the line is left for it.

The brief's estimate is `M`; the stub said `S`. The migration, the request,
the service, the controller, the page, a new component and fifteen cases are
a day, not half of one.

**Executed 19 September 2026 — wording-tier fixes** (`reports/T-123-2026-09-19-wayne.md`):

- The recipe's `orderedEpisodes()->first()->lengthMinutes()   // 90` reads the
  File Episode the same recipe adds first, so it answers null. It is
  `firstWhere('title', 'Live Q&A')`. The recipe also gains one line setting a
  zone when the Group has none: Setup takes `Group::first()`, and on the
  design-review world that can be a Group with no timezone chosen, which
  `add()` refuses for a live Episode.
- `add()` writes `$startsAt?->utc()`, not `$startsAt`. The column is a
  `timestamp` with no zone, and Eloquent writes a zoned Carbon as its own
  wall-clock time, so a caller passing a Melbourne instant would have stored
  it ten or eleven hours out. Every caller in the Code section already passes
  UTC; this makes it true for the ones that do not.
- The New Episode `<Form>` captures its fields' defaults when it mounts, while
  the kind is still a file, so the panel's fields had none: `reset-on-success`
  emptied the length, unticked Recorded and blanked the hidden `0`, and the
  next session saved as "Live only" without anybody choosing it. Seen in the
  browser after the first add. `Show.vue` re-mounts the panel on the form's
  `reset` event (`livePanelKey`), which puts its own defaults back.
- `StoreEpisodeRequest` said `SeriesService` twice where `T-083` made it
  `EpisodeService`.
