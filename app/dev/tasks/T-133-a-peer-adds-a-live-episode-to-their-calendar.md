---
id: T-133
title: A Peer adds a live Episode to their calendar
stream: classroom
status: draft
owner: unassigned
estimate: S
depends: T-127
blocks: T-138
---

# T-133 — A Peer adds a live Episode to their calendar

> **Draft.** Not specified to the last name yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). Written on 18 September 2026 from `D-024`,
> `D-026` and `D-028`, beside `T-125` to `T-127`, whose finished specs it
> reads; what has to be confirmed before it is `ready` is listed at the
> bottom.

## Why

A live Episode's time is on the Peer's page and nowhere the Peer keeps. The
row renders it once through `SessionTime`
(`resources/js/pages/shared/Show.vue:205-210`), and `T-125`'s card adds the
Group's zone beside it and Join when the window opens; nothing on the page
survives closing the tab. A Peer fifteen hours from the creator who wants to
be there on time copies the instant by hand into their own calendar, in the
right zone, and copies it again when the creator moves the session (`T-124`).
Reminder email is Start and above (`communications-policy.md:55-59`,
`D-028`), so on the Free plan the Peer's own calendar is the only reminder
there is, and on every plan it is the one the Peer controls.

Afterwards an `upcoming` card carries "Add to calendar", which downloads an
RFC 5545 file: one event whose `UID` is the Episode's id, whose start and end
are the two columns in UTC so the calendar shows them in its own zone, whose
`URL` and description point at `shared.episodes.show` and never at the meeting
link (`D-024`), and whose `SEQUENCE` is the Episode's `schedule_version`
(`D-026`), so a file downloaded again after a move updates the entry the
calendar already holds rather than adding a second. The same string is what
`T-138` attaches to the day-before reminder, and a session `T-134` cancels
reads `STATUS:CANCELLED` from the same method.

## Decisions taken to make this specifiable

**The file is built by `App\Support\CalendarInvite::for(Episode, Series): string`, a static helper under `app/Support`.**
RFC 5545 is an open standard, not a vendor, so `D-022` puts nothing under
`app/Integrations`; the helper knows no vendor and calls no HTTP. It takes the
Series as well as the Episode because the Series' title goes in the summary
and its Group's words go in the description, and the Peer surface has no
current Group to read either from (`routes/shared.php:13-15`). A static
method rather than a service, because it holds no state and its two callers
— this route and `T-138`'s notification — each have the two models in hand.

**Times are UTC instants, and the file carries no `VTIMEZONE`.** `DTSTART`
and `DTEND` are written in the `20261006T230000Z` form from `starts_at` and
`ends_at` (`T-123`'s columns). A calendar renders a UTC instant in its own
zone, which is the Peer's, and a `VTIMEZONE` block is the part of the
standard importers most often get wrong. The Group's zone is on the card and
in the reminder (`D-028`); the calendar file needs neither zone named.

**`UID` is `{episodeId}@useqori.com`, with the domain a constant on the class.**
A `UID` is an identity, not a link: the same Episode has to produce the same
`UID` every time, or a re-download after a move becomes a second event
instead of an update. `config('app.url')` is per-environment and has already
changed once (`.env.example:5-6`), so the domain is
`CalendarInvite::UID_DOMAIN` and not derived from it. Kept open below in case
the owner prefers the host of `APP_URL`.

**`SEQUENCE` is `Episode::scheduleVersion()`.** `T-124` defines it as
`(int) ($this->content['schedule_version'] ?? 1)`, bumped once per save in
which `starts_at` or `ends_at` changes. So the first file a Peer downloads
says `SEQUENCE:1` and the file after one move says `SEQUENCE:2`; a calendar
compares the numbers and never counts from zero, so starting at 1 is
harmless. Nothing here writes `schedule_version`.

**`STATUS` is `CANCELLED` when `Episode::isCancelled()`, else `CONFIRMED`.**
`T-123` defines `isCancelled()` as `isset($this->content['cancelled_at'])`
and nothing writes that key before `T-134`; the branch exists now so `T-134`
adds a writer, not a rule, and its test writes the key directly on the row as
`T-125`'s case 7 does. A cancelled event keeps its `DTSTART`, because a
calendar needs the same `UID` and a later `SEQUENCE` or `CANCELLED` status to
find the entry it holds; the card no longer offers the file in that state,
but `T-138`'s cancellation mail may attach it.

**The `URL` and the description point at `shared.episodes.show`, and the join link never enters the file (`D-024`).**
`route('shared.episodes.show', [$seriesId, $episodeId])` is the address every
email, calendar file and copied message is minted against, so a link already
in somebody's calendar keeps working when the creator corrects the join link
or a page of its own replaces the redirect. The meeting link is the one thing
owner scenario 14 forbids in anything sent, and a test pins its absence.

**`METHOD:PUBLISH`, `PRODID:-//Qori//Qori//EN`, `CALSCALE:GREGORIAN`, `DTSTAMP` now, and no `VALARM`.**
`PUBLISH` is the method for a file a person adds to their own calendar;
`REQUEST` would ask for an RSVP nobody reads. `DTSTAMP` is
`CarbonImmutable::now()` in UTC, so the test sets the clock. No `VALARM`:
Google Calendar ignores one on import and applies the account's default,
Apple Calendar honours it and Outlook sometimes does, so an alarm here would
be one more thing that differs by importer; the Peer's calendar applies its
own reminder, which is what "the one self-serve reminder every plan has"
means. Kept open below for the owner.

**Text is escaped and lines are folded as the standard says, in two private methods.**
RFC 5545 §3.3.11: backslash, semicolon, comma and newline are escaped, in
that order so the backslash is done first. §3.1: a content line is at most
75 octets, folded with CRLF followed by one space, and the cut is on a UTF-8
boundary through `mb_strcut()` so a title in Chinese or an emoji is never
split mid-character. Every line ends in CRLF, the file included. A test
unfolds the body and reads the title back.

**`SUMMARY` is the Episode's title and the Series' title; `DESCRIPTION` is one sentence and the address.**
A calendar's month view shows the summary alone, and "Week 3" without the
course it belongs to is not an appointment. The summary line is
`live.calendar.summary` with `:title` for the Episode and `:series_title` for
the Series — a caller replacement, so it does not collide with the vocabulary's
`:series`, and `strtr()` matches the longer key first. The description is
`live.calendar.description`, read through `Terminology::line()` with the
Series' Group so `:episode` is that Group's word, and ends with the address,
because some importers show the description and drop the `URL` property. It
names no materials: the Peer's material list is `T-131`'s, which is not in
this task's chain (`T-127` → `T-126` → `T-125`), and a file downloaded the
day this lands must not promise what the page does not show.

**The route is `GET /shared/{seriesId}/episodes/{episodeId}/calendar`, `shared.episodes.calendar`, on a new invokable `CalendarInviteController`.**
Ids, because every Peer route takes ids (`routes/shared.php:21-25`); a
sibling of `T-125`'s anchor route and `T-089`'s open route, in the same
`auth`, `verified`, `shared.` group (`:31-34`). Its own controller rather than
an action on `SharedController`, because the response is a file, not a page.

**The gate is the Series page's, written in the controller, and the Episode is looked up as `PlaybackTicketService::issue()` looks one up.**
`CurrentUser::orFail()`, `Access::forUser($peer)->where('series_id', …)->first()`
— which is `->active()` (`app/Models/Access.php:253-259`), so a revoked
access is absent — and 403 `errors.access.not_granted` when absent: the
lines `SharedController::show()` carries at `:86-90`, `:97` and `:114-118`,
and `T-125`'s `EpisodeAnchorController` repeats. The Confirming branch
between them (`:98-112`, a payment in flight) is left out, as
`EpisodeAnchorController` leaves it out: a calendar link is only ever
offered to somebody who already has access. Then `$access->grantedSeries()`
and `orderedEpisodes()->first(…)` by id
(`app/Services/PlaybackTicketService.php:58-64`). The Series is read through
the Access row just checked rather than through
`Series::findForPeer($seriesId)`, because the row is the proof of access and
`grantedSeries()` cannot name a Series the row does not; it is what
`SharedController::show()` (`:123`) and `T-131`'s `MaterialService::open()`
do, while `T-132` reads through `findForPeer()`, and `T-131` names both as
the sanctioned crossings — neither adds an `acrossAllGroups()` caller.
`orderedEpisodes()` needs no `forGroup()`, because `Episode` carries no
group scope (`app/Models/Episode.php` has no `BelongsToGroup`). `T-089`'s
`admit()` is private to that service and would have to become public for
one caller outside it; the gate is short and the Peer surface already
writes it per controller.

**A missing Episode and a non-live Episode both answer 404 with one new line, `errors.live.no_calendar`.**
Neither address is ever offered: the control renders only on a live card, so
both are typed or stale URLs. `errors.playback.missing_content` says "still
uploading", which is wrong here, and `T-126`'s `errors.live.not_live` is the
creator's 422; one Peer-facing line with no resolution says what is true of
both — nothing at that address can go in a calendar — and it is final.

**Downloading records nothing.** No `ProgressService::opened()` and no
`access_opens` row: the file is a reminder about the lesson, not the lesson,
and `OpenTarget` has no case for it on purpose. `opened_episode_ids` is
"who reached it" and `access_opens` is "who followed it"; a calendar file is
neither.

**The card's href comes from the server inside `live`, not from the page through Wayfinder.**
`SharedController::liveCard()` adds `calendarUrl` built with
`route('shared.episodes.calendar', …)` and `copy.addToCalendar`, so
`LiveSessionCard.vue` reads both from the `live` prop it already has and
`shared/Show.vue` changes only its `LiveCard` type. Both edits are in the
stream's claim order (`streams/classroom.md`, "Claim order"):
`app/Http/Controllers/Shared/SharedController.php` — `T-089`, `T-125`,
`T-131`, `T-132`, `T-133`, `T-134`; `resources/js/pages/shared/Show.vue` —
`T-089` first, then `T-125`, `T-131`, `T-132`, `T-133` (a type only); and
the lines for `LiveSessionCard.vue` and `routes/shared.php` list this task
too. A type-only edit is the least the page edit can be. `qori:reachability`
sees the route by name through the controller, because its haystack includes
PHP files (`app/Support/Reachability.php:194-200`, `:162-171`), so no
allow-list row is needed. `joinHref` stays as `T-125` built it.

**"Add to calendar" renders in `upcoming` only, as a plain `<a download>`.**
The brief puts it there; by `open` the Peer is joining, and after the end
there is nothing to attend. The anchor carries `download` so the click saves
the file on every desktop browser without leaving the page, and the server's
`Content-Disposition: attachment` covers the rest; on a phone the file lands
where the share sheet offers Calendar. Kept open below whether `open` should
carry it too.

**The download is named after the Episode.** `CalendarInvite::filenameFor()`
is `Str::slug($episode->title)` with `.ics`, or `session.ics` when the title
slugs to nothing (a title in a non-Latin script), built through Symfony's
`HeaderUtils::makeDisposition()` so a quote in a title cannot break the
header. A slug is ASCII, so no fallback filename is needed for the header.

**The fallback name `session` is a constant, not copy, and that is deliberate.**
A download's name is a filesystem name the `Content-Disposition` header
carries, not a sentence a person is addressed with: `makeDisposition()`
requires ASCII for its plain `filename`, which is why the whole name is built
from `Str::slug()`, and a word read from `lang/en/live.php` — which a second
locale may make non-ASCII — would need an ASCII fallback of its own, which is
this constant again. `CLAUDE.md`'s inline-copy rule is about strings a person
reads as Qori speaking to them, and
`ArchitectureTest::test_no_user_facing_string_is_inline()` looks for a
sentence passed to `__()`; a reviewer reading `FILENAME_FALLBACK` should know
the choice was made, not missed.

**No copy is added to Vue.** The one label is the lang key
`live.calendar.add`, resolved in `SharedController::liveCard()` like every
other line on the card, and it reaches the card as the prop
`live.copy.addToCalendar` — a prop path, not a second lang key.

**`config/qori.php` is not edited.** This task reads no number.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests build
their own scene — a Group in `Australia/Brisbane` on the `start` plan with a
live Zoom Episode on 7 October 2026 at 09:00 for 60 minutes through
`EpisodeService::add()` with `startsAt:` and `lengthMinutes:` (`T-123`),
published, with an Access through `AccessService::grant()`. The zone, the
plan, the instants, the length and the `join_url` follow the scene of
`tests/Feature/Shared/LiveSessionCardTest.php` (`T-125`), so the two files
agree on every instant; the two titles — the Episode "Week 1", the Series
"Piano" — are this task's own, because `T-125` fixes no titles and this
file's download name and `SUMMARY` assertions read them.

**Equipment:** one calendar application to import the file into by hand —
Apple Calendar, Google Calendar's import, or Outlook, and each of the three
where the tester has it — and to import it into again after moving the
session, to see the entry update rather than double. Nothing else; there is
no vendor call.

**Spike:** none owed. The file is Qori's own output against an open standard
(RFC 5545, `https://www.rfc-editor.org/rfc/rfc5545`); no vendor payload is
read or guessed.

## Scope

**In:**

- `App\Support\CalendarInvite` with `for()` and `filenameFor()`: the fields
  above, escaping, folding, CRLF, the constants.
- `shared.episodes.calendar`, `CalendarInviteController`: the gate, the
  Episode lookup, the `text/calendar` response with an attachment
  disposition.
- `SharedController::liveCard()`: `calendarUrl` and `copy.addToCalendar`;
  the `LiveCard` type on `shared/Show.vue`; the control on
  `LiveSessionCard.vue` in `upcoming`.
- `lang/en/live.php` `calendar.*`; `lang/en/errors.php` `live.no_calendar`.
- `docs/flows/live-sessions.md` and `docs/tinker/live-sessions.md`.
- The tests.

**Out:**

- Attaching the file to the day-before reminder and to the cancellation
  mail, and the reminders themselves (`T-138`), which call `for()` and
  `filenameFor()` and add nothing here.
- Cancelling a session and writing `cancelled_at` (`T-134`); this task only
  reads it.
- The creator's own calendar; the creator's page has the time and their
  meeting tool has the event.
- A calendar feed a Peer subscribes to, a file holding every session of a
  Series, custom reminder offsets, recurrence rules, a `VALARM`.
- The control in any state but `upcoming`, and any change to
  `SessionTime.vue`.
- The public page and previews: a calendar file is never minted for
  somebody without an active Access (`D-024`).
- Any `access_opens` row or `opened_episode_ids` change for a download.

## Files

| Path                                                       | Change | Notes                                                                                          |
| ---------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| `app/Support/CalendarInvite.php`                           | new    | `for()`, `filenameFor()`; `escape()`, `fold()`, `utc()`; the five constants                    |
| `app/Http/Controllers/Shared/CalendarInviteController.php` | new    | the gate, the Episode lookup, the `text/calendar` attachment                                   |
| `routes/shared.php`                                        | edit   | `shared.episodes.calendar`, after `shared.episodes.open`                                       |
| `app/Http/Controllers/Shared/SharedController.php`         | edit   | `liveCard()`: `calendarUrl`, `copy.addToCalendar`                                              |
| `resources/js/pages/shared/Show.vue`                       | edit   | `LiveCard` gains `calendarUrl` and `copy.addToCalendar` — type only, no template change        |
| `resources/js/components/series/LiveSessionCard.vue`       | edit   | the `<a download>` in `upcoming`                                                               |
| `lang/en/live.php`                                         | edit   | `calendar.add`, `calendar.summary`, `calendar.description`                                     |
| `lang/en/errors.php`                                       | edit   | `live.no_calendar` in the `live` group `T-126` creates                                         |
| `docs/flows/live-sessions.md`                              | edit   | "Adding a session to a calendar": the chain and the fields; "Not built yet" loses the calendar |
| `docs/tinker/live-sessions.md`                             | edit   | minting the file and its name in tinker                                                        |
| `tests/Feature/Shared/CalendarInviteTest.php`              | new    | 16 cases                                                                                       |

No migration, no factory and no seeder change: the file is computed from
columns and content `T-123` and `T-124` already write, and the design-review
seeder's live Episode (`database/seeders/DesignReviewSeeder.php:352-356`, as
`T-123` leaves it) already renders an `upcoming` card. No `config/qori.php`
row: the route is linked by name from `SharedController::liveCard()`, which
`qori:reachability` reads (`app/Support/Reachability.php:194-200`).

## Database

None. `schedule_version` and `cancelled_at` live inside `episodes.content`
(`D-026`) and are written by `T-124` and `T-134`; `starts_at` and `ends_at`
are `T-123`'s columns. This task reads all four and writes none.

## Code

```php
namespace App\Support;

use App\Models\Episode;
use App\Models\Series;
use Carbon\CarbonImmutable;
use Carbon\CarbonInterface;
use Illuminate\Support\Str;
use InvalidArgumentException;

/**
 * A live Episode as an RFC 5545 calendar file (D-026).
 *
 * An open standard, not a vendor, so it lives here and not under
 * app/Integrations. The two instants are UTC — the reader's calendar shows
 * them in its own zone, and no VTIMEZONE is written — and the file points at
 * the Episode's Qori address, never at the meeting link (D-024). SEQUENCE is
 * the Episode's schedule_version, so a file downloaded again after a move
 * updates the entry a calendar already holds. T-138 attaches the same string
 * to the day-before reminder.
 */
class CalendarInvite
{
    /**
     * The domain part of every UID. A constant on purpose: a UID is an
     * identity, not a link, and must not follow APP_URL between environments.
     */
    public const UID_DOMAIN = 'useqori.com';

    public const PRODID = '-//Qori//Qori//EN';

    /**
     * The media type of the file: the response's Content-Type here and the
     * attachment's mime in T-138. Declared once, read from both.
     */
    public const MIME = 'text/calendar';

    /** RFC 5545 §3.1: a content line is at most this many octets before it is folded. */
    public const LINE_OCTETS = 75;

    /** The download's name when the title slugs to nothing. */
    public const FILENAME_FALLBACK = 'session';

    /**
     * The whole file, CRLF-terminated, escaped and folded.
     *
     * Throws InvalidArgumentException for an Episode that is not live or has
     * no starts_at/ends_at — a programmer error, since T-123 requires both on
     * every live row and the controller has already checked isLive().
     */
    public static function for(Episode $episode, Series $series): string;
    // if (! $episode->isLive() || $episode->starts_at === null || $episode->ends_at === null) {
    //     throw new InvalidArgumentException("Episode {$episode->getKey()} is not a live Episode with a start and an end.");
    // }
    //
    // $url = route('shared.episodes.show', [$series->getKey(), $episode->getKey()]);
    // $terminology = app(Terminology::class);
    //
    // $lines = [
    //     'BEGIN:VCALENDAR',
    //     'VERSION:2.0',
    //     'PRODID:'.self::PRODID,
    //     'CALSCALE:GREGORIAN',
    //     'METHOD:PUBLISH',
    //     'BEGIN:VEVENT',
    //     'UID:'.$episode->getKey().'@'.self::UID_DOMAIN,
    //     'DTSTAMP:'.self::utc(CarbonImmutable::now()),
    //     'DTSTART:'.self::utc($episode->starts_at),
    //     'DTEND:'.self::utc($episode->ends_at),
    //     'SEQUENCE:'.$episode->scheduleVersion(),                       // T-124
    //     'STATUS:'.($episode->isCancelled() ? 'CANCELLED' : 'CONFIRMED'), // T-123's accessor; T-134 writes the key
    //     'SUMMARY:'.self::escape(__('live.calendar.summary', ['title' => $episode->title, 'series_title' => $series->title])),
    //     'DESCRIPTION:'.self::escape($terminology->line('live.calendar.description', ['url' => $url], $series->group)),
    //     'URL:'.$url,
    //     'END:VEVENT',
    //     'END:VCALENDAR',
    // ];
    //
    // return implode("\r\n", array_map(self::fold(...), $lines))."\r\n";

    /** "<slug of the title>.ics", or "session.ics" when the slug is empty. */
    public static function filenameFor(Episode $episode): string;
    // (Str::slug($episode->title) ?: self::FILENAME_FALLBACK).'.ics'

    /** RFC 5545 §3.3.11, backslash first: \ → \\, ; → \;, , → \,, newline → \n. */
    private static function escape(string $text): string;

    /**
     * RFC 5545 §3.1: at most LINE_OCTETS octets per line, continued with CRLF
     * and one space; the first line takes LINE_OCTETS, each continuation one
     * fewer for the space, cut on UTF-8 boundaries with mb_strcut().
     */
    private static function fold(string $line): string;

    /** 20261006T230000Z — the instant in UTC, whatever zone it was read in. */
    private static function utc(CarbonInterface $at): string;
    // $at->toImmutable()->utc()->format('Ymd\THis\Z')
}
```

```php
namespace App\Http\Controllers\Shared;

use App\Exceptions\AppException;
use App\Http\Controllers\Controller;
use App\Models\Access;
use App\Models\Episode;
use App\Models\Series;
use App\Support\CalendarInvite;
use App\Support\CurrentUser;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Symfony\Component\HttpFoundation\HeaderUtils;

/**
 * One live Episode as a calendar file, behind the Series page's gate (D-024).
 *
 * The gate is the one SharedController::show() and EpisodeAnchorController
 * pass; the Episode is then found as PlaybackTicketService::issue() finds
 * one. Nothing is marked opened and no access_opens row is written: the
 * file is a reminder about the lesson, not the lesson.
 */
class CalendarInviteController extends Controller
{
    public function __invoke(Request $request, string $seriesId, string $episodeId): Response;
    // $peer = CurrentUser::orFail($request);
    // $access = Access::forUser($peer)->where('series_id', $seriesId)->first();
    //
    // if ($access === null) {
    //     throw AppException::forbidden(
    //         'errors.access.not_granted',
    //         devMessage: "User {$peer->getKey()} has no active access in series {$seriesId}.",
    //     );
    // }
    //
    // $series = $access->grantedSeries();
    // $episode = $series?->orderedEpisodes()
    //     ->first(fn (Episode $candidate): bool => (string) $candidate->getKey() === $episodeId);
    //
    // if (! $series instanceof Series || ! $episode instanceof Episode || ! $episode->isLive()) {
    //     throw AppException::notFound(
    //         'errors.live.no_calendar',
    //         devMessage: "Episode {$episodeId} is not a live Episode of series {$seriesId}.",
    //     );
    // }
    //
    // return response(CalendarInvite::for($episode, $series), 200, [
    //     'Content-Type' => CalendarInvite::MIME.'; charset=utf-8',
    //     'Content-Disposition' => HeaderUtils::makeDisposition(
    //         HeaderUtils::DISPOSITION_ATTACHMENT,
    //         CalendarInvite::filenameFor($episode),
    //     ),
    // ]);
}
```

```php
// App\Http\Controllers\Shared\SharedController::liveCard() — two keys added to
// T-125's array, nothing else in the method changes.

'calendarUrl' => route('shared.episodes.calendar', [$series->getKey(), $episode->getKey()]),
// inside 'copy', after 'records':
'addToCalendar' => $terminology->line('live.calendar.add', [], $group),
```

```ts
// resources/js/pages/shared/Show.vue — T-125's LiveCard, two keys, type only.
interface LiveCard {
    // …T-125's keys…
    calendarUrl: string;
    copy: {
        // …T-125's keys…
        addToCalendar: string;
    };
}

// resources/js/components/series/LiveSessionCard.vue — T-125's template, one
// line added under the `upcoming` paragraph. No other phase changes.
//   phase 'upcoming' → <p>{{ live.copy.upcoming }}</p>
//                      <a :href="live.calendarUrl" download>{{ live.copy.addToCalendar }}</a>
```

`lang/en/live.php` gains, under `T-125`'s header, a `calendar` group with a
comment naming the rule: the file is minted against the Episode's Qori
address and carries no meeting link (`D-024`). `lang/en/errors.php` gains
`no_calendar` inside the `live` group `T-126` creates (`not_live`,
`recording_unavailable`) and `T-127` extends (`has_recording`,
`recording_not_found`).

`docs/flows/live-sessions.md` gains "Adding a session to a calendar": the
chain `GET …/calendar` → `CalendarInviteController` → the gate →
`CalendarInvite::for()` → `text/calendar`; the field table (`UID`, `DTSTART`,
`DTEND`, `SEQUENCE`, `STATUS`, `SUMMARY`, `DESCRIPTION`, `URL`) with where
each comes from; the two rules (UTC only, never the join link); and "Not
built yet" loses its calendar line. `docs/tinker/live-sessions.md` gains,
after `T-125`'s anchor URL:

```php
$episode = $series->orderedEpisodes()->first(fn ($episode) => $episode->isLive());
echo App\Support\CalendarInvite::for($episode, $series);
App\Support\CalendarInvite::filenameFor($episode);
route('shared.episodes.calendar', [$series->getKey(), $episode->getKey()]);
```

## Copy

| Key                               | File                 | English                                                            |
| --------------------------------- | -------------------- | ------------------------------------------------------------------ |
| `live.calendar.add`               | `lang/en/live.php`   | Add to calendar                                                    |
| `live.calendar.summary`           | `lang/en/live.php`   | :title — :series_title                                             |
| `live.calendar.description`       | `lang/en/live.php`   | Join from your :episode on Qori, where any recording is kept: :url |
| `errors.live.no_calendar.message` | `lang/en/errors.php` | There's no session to add to a calendar at that address.           |

`live.calendar.add` and `live.calendar.description` are read through
`Terminology::line()` with the Series' Group, the first in
`SharedController::liveCard()` beside the card's other lines and the second
in `CalendarInvite::for()`; `:episode` is that Group's word. `:title` is the
Episode's title and `:series_title` the Series' — a caller replacement,
distinct from the vocabulary's `:series` — so `live.calendar.summary` carries
no noun and is read with `__()`. `:url` is
`route('shared.episodes.show', …)`, never the join link.
`errors.live.no_calendar` carries no resolution on purpose: nothing at that
address can go in a calendar, and it is final. No line under `live.*` says
"live now", "has ended", "on its way" or "processing" (`D-026`) — "any
recording" says where one goes, not that one exists — and no article stands
before a noun placeholder.

## Routes

| Verb | Path                                               | Name                       | Action                                      |
| ---- | -------------------------------------------------- | -------------------------- | ------------------------------------------- |
| GET  | `/shared/{seriesId}/episodes/{episodeId}/calendar` | `shared.episodes.calendar` | `Shared\CalendarInviteController::__invoke` |

Inside the existing `auth`, `verified`, `shared.` group
(`routes/shared.php:31-34`), after `T-089`'s `shared.episodes.open`, taking
ids because every Peer route does (`:21-25`). No creator route changes.

## Tests

**New: `tests/Feature/Shared/CalendarInviteTest.php` — 16 cases**
(the scene of `tests/Feature/Shared/LiveSessionCardTest.php` (`T-125`) for
the zone, the plan, the instants, the length and the link: a Group in
`Australia/Brisbane` on the `start` plan, a live Zoom Episode on 2026-10-07
09:00 Brisbane for 60 minutes with `join_url`
`https://zoom.us/j/91827405566`, published, an Access through
`AccessService::grant()`; the two titles are this file's own, because
`T-125` fixes none — the Episode "Week 1", the Series "Piano" — so cases 1,
2 and 7 read them from here and a change to `T-125`'s scene cannot break
them; `Carbon::setTestNow(CarbonImmutable::parse('2026-09-18 10:00', 'UTC'))`
in `setUp` for `DTSTAMP`; the body read from `$response->getContent()`; a
private `unfold(string $body): string` helper that removes every CRLF-space
fold, and a private `event(string $body): array<string, string>` helper that
splits each unfolded line on its first colon)

1. `test_it_serves_the_session_as_a_calendar_file` — 200; `Content-Type`
   `text/calendar; charset=utf-8`; `Content-Disposition` is
   `attachment; filename=week-1.ics`; the body starts `BEGIN:VCALENDAR`,
   ends `END:VCALENDAR\r\n`, holds `VERSION:2.0`, `PRODID:-//Qori//Qori//EN`,
   `CALSCALE:GREGORIAN`, `METHOD:PUBLISH`, one `BEGIN:VEVENT`/`END:VEVENT`,
   and every line ends in CRLF.
2. `test_the_event_carries_the_episode_identity_and_its_instants_in_utc` —
   `UID` is `{episodeId}@useqori.com`; `DTSTAMP` `20260918T100000Z`;
   `DTSTART` `20261006T230000Z`; `DTEND` `20261007T000000Z`; `SEQUENCE` `1`;
   `STATUS` `CONFIRMED`; `SUMMARY` `Week 1 — Piano`; `URL` is
   `route('shared.episodes.show', [$seriesId, $episodeId])`; the body
   contains neither `TZID` nor `VTIMEZONE`.
3. `test_the_file_never_carries_the_join_link` —
   `assertStringNotContainsString('https://zoom.us/j/91827405566', $this->unfold($body))`,
   and the same for `zoom.us`, on the unfolded body and never the raw one,
   because a fold could split a leaked link into `zoom.` and ` us` and the
   raw body would pass with the defect present; `DESCRIPTION` ends with the
   anchor route's URL (`D-024`, owner scenario 14).
4. `test_the_sequence_and_the_instants_follow_a_reschedule` — the session is
   moved to 2026-10-14 09:00 Brisbane through `EpisodeService::update()`
   with a new `starts_at`, as `T-124`'s tests move one; the file now says
   `SEQUENCE:2`, `DTSTART:20261013T230000Z`, `DTEND:20261014T000000Z`, and
   the same `UID` as before (owner scenario 14).
5. `test_a_cancelled_session_is_marked_cancelled_under_the_same_uid` —
   `content.cancelled_at` written directly on the row, as `T-125`'s case 7
   writes it (`T-134` owns the writer): `STATUS:CANCELLED`, the `UID` and
   `DTSTART` unchanged.
6. `test_london_and_new_york_peers_get_the_same_instant_across_the_daylight_change`
   — a second live Episode on 2026-11-08 09:00 Brisbane; two Peers with
   `users.timezone` `Europe/London` and `America/New_York`, each with an
   Access: all four bodies carry `DTSTART:20261006T230000Z` and
   `DTSTART:20261107T230000Z` respectively, byte-identical between the two
   Peers, and no zone name anywhere (owner scenario 2: the calendar does the
   zone).
7. `test_text_is_escaped_and_long_lines_are_folded` — the Episode titled
   `Week 1, part A; the "basics" \ and more` in a Series whose title is 120
   characters: the raw body holds `\,`, `\;` and `\\`; no raw line exceeds
   75 octets; every continuation line begins with one space; the helper's
   unfolded `SUMMARY` reads the two titles back exactly.
8. `test_the_description_speaks_the_groups_words` —
   `config()->set('qori.plans.start.'.Terminology::ENTITLEMENT, true)`, then
   `$group->update(['settings' => [Terminology::SETTINGS_KEY => $labels]])`
   where `$labels` is the five-noun array `TerminologyTest::customLabels()`
   returns (`tests/Feature/TerminologyTest.php:36-45`), copied literally
   because that method is private and `Terminology::resolve()` falls back to
   every default on an incomplete set; then
   `app(Terminology::class)->forget($group)`, because the vocabulary is
   memoised per Group and the scene may already have resolved it:
   `DESCRIPTION` contains `Practice` and not `Episode`.
9. `test_downloading_records_no_open` — after the GET,
   `$access->fresh()->opened_episode_ids` is `[]`, `last_activity_at` is
   null, and `AccessOpen::query()->forGroup($group)->count()` is 0.
10. `test_it_refuses_someone_without_access` — a second User with no Access:
    403 with `errors.access.not_granted.message`; no file.
11. `test_it_refuses_a_revoked_access` — `AccessService::revoke()`, then 403.
12. `test_it_refuses_a_series_in_another_group` — a Peer with access to a
    Series in Group A asks for a live Series in Group B they have no access
    to: 403 (owner scenario 11).
13. `test_an_episode_of_another_series_is_not_found` — the Peer's own Series
    id with a live Episode id from another Series: 404 with
    `errors.live.no_calendar.message`.
14. `test_a_file_episode_has_no_calendar_file` — a File Episode in the
    Peer's Series: 404 with `errors.live.no_calendar.message`.
15. `test_a_guest_is_sent_to_sign_in` — signed out: a redirect to the
    sign-in page, no file.
16. `test_the_card_carries_the_calendar_url_and_its_label` —
    `assertInertia` on `shared.show`: `series.episodes.0.live.calendarUrl`
    is `route('shared.episodes.calendar', [$seriesId, $episodeId])` and
    `.copy.addToCalendar` is `Add to calendar`.

**Changed:**

- None. `tests/Feature/Shared/LiveSessionCardTest.php` (`T-125`) asserts
  named keys, and two more keys on the `live` prop break nothing.
  `tests/Feature/TerminologyTest.php` walks `lang/en/live.php` on its own for
  articles before nouns. `tests/Feature/Admin/ConsoleAccessTest.php` is
  unchanged: no `acrossAllGroups()` caller is added, the route reads through
  `Access::forUser()` and `grantedSeries()` as the Series page does.

Total: 16 new cases in one file.

## Acceptance

- [ ] On an `upcoming` card a Peer with access sees "Add to calendar", and the
      file imports into a calendar application as one event at the session's
      time in the calendar's own zone, titled with the Episode and the Series,
      linking to the Episode's Qori address, with no meeting link anywhere in
      it — tried by hand in Apple Calendar, Google Calendar and Outlook, each
      where the tester has it, and the report names which
- [ ] After the creator moves the session (`T-124`), downloading again updates
      the entry the calendar already holds instead of adding a second (owner
      scenario 14)
- [ ] A Peer in London and one in New York import the same instant on either
      side of 1 November 2026 and each sees their own local time (owner
      scenario 2)
- [ ] No access, a revoked access, another Group's Series, another Series'
      Episode, a File Episode and a guest each meet the refusal the tests
      name, and never a file (owner scenario 11)
- [ ] Downloading marks nothing opened and writes no `access_opens` row
- [ ] A session with `cancelled_at` set produces `STATUS:CANCELLED` under the
      same `UID`, ready for `T-134` and `T-138` without a change here
- [ ] `docs/flows/live-sessions.md` describes the chain and the fields, and no
      longer lists the calendar file as unbuilt
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-127` `ready`, and with it `T-125` and `T-126`, so the `live` prop and
  its `copy` shape on `LiveSessionCard.vue` and `lang/en/live.php` (`T-125`)
  are frozen, and the `errors.live` group is frozen once `T-126`, which
  creates it with `not_live` and `recording_unavailable`, is `ready` — the
  names above are theirs — anyone's.
- Whether the estimate stays `S` with the 16 cases below, or becomes `M` —
  the stream owner's, when setting it `ready`; see Notes.
- Whether `UID`'s domain is the constant `useqori.com` this draft uses, or
  the host of `config('app.url')` — anyone's; the draft's reason is above.
- Whether the file carries a `VALARM` — the owner's; this draft writes none,
  so each calendar applies its own reminder.
- Whether "Add to calendar" also shows in `open`, for the Peer who arrives
  during the window and wants the next one in their calendar — anyone's;
  this draft follows the brief and renders it in `upcoming` only.

## Re-scope log

None.

## Notes

Written 18 September 2026 from `D-024`, `D-026` and `D-028` and the finished
drafts of `T-125` (the card, the `live` prop, `lang/en/live.php`), `T-124`
(`Episode::scheduleVersion()`, absent reads 1), `T-126` (the `errors.live`
group, with `not_live` and `recording_unavailable`) and `T-127`
(`has_recording` and `recording_not_found` in it).
`docs/planning/course-classroom.md` was written after this draft, so the
decisions are cited directly here rather than through it; its "The lifecycle
of a live Episode" section is the same shape, and acceptance scenario 14 is
the one this task carries with `T-138`.

`T-134`'s draft, when it is written, needs nothing for the calendar:
`CalendarInvite::for()` reads `cancelled_at` through `Episode::isCancelled()`,
and case 5 above already pins `STATUS:CANCELLED`. `T-138`'s draft is edited
to attach `CalendarInvite::for($episode, $series)` as
`CalendarInvite::filenameFor($episode)` on the day-before reminder and, if it
chooses, on the cancellation mail, and to add no calendar code of its own.
Its draft declares `SessionReminderNotification::CALENDAR_MIME = 'text/calendar'`;
that value is `CalendarInvite::MIME` here, and `T-138` reads the constant
rather than declaring its own — its owner's edit, so the one value is
declared once across the stream.

The type-only edit to `resources/js/pages/shared/Show.vue` exists because
`T-125` declares `LiveCard` on the page; if that interface moves into the
card, the page row above goes, and the stream's claim order loses this task
on that line.

The brief sized this task `S` with about six tests. Written out, it carries
RFC 5545 escaping and folding on UTF-8 boundaries, a controller, a header,
two docs edits and 16 cases, which is a day rather than under half of one.
The 16 stay, because each pins a rule a calendar would otherwise break
silently — the fold, the join link's absence, the identity across a move,
the refusals; the front matter keeps the brief's `S`, and the stream owner is
asked to size it `M` when setting it `ready`, or to name the cases to cut.

`SEQUENCE` starts at 1, not 0, because `scheduleVersion()` reads an absent
key as 1 (`T-124`). Calendars compare the number against the one they hold
and never count from zero, so nothing depends on the start.
