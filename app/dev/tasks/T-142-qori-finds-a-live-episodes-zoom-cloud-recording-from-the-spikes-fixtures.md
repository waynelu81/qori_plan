---
id: T-142
title: Qori finds a live Episode's Zoom cloud recording from the spike's fixtures
stream: storage
status: draft
owner: unassigned
estimate: M
depends: T-122, T-141
blocks: T-143
---

# T-142 — Qori finds a live Episode's Zoom cloud recording from the spike's fixtures

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 18 September 2026 from
> `D-027`, `D-022` and `D-026`, on `T-141`'s `ZoomClient` and against the
> fixtures `T-122` commits under `tests/Fixtures/zoom/recordings/`, none of
> which exist yet. Every Zoom field named below is an expectation from Zoom's
> Meetings reference until its fixture is on disk.

## Why

Nothing in Qori can look for a recording. `app/Integrations/` holds
`CloudflareR2`, `Contracts`, `Dropbox`, `Stripe` and `Vimeo`; the one media
contract, `ResolvesMedia` (`app/Integrations/Contracts/ResolvesMedia.php:29-34`),
answers a play link for an Episode's own media and nothing else, and
`PlaybackTicketService::resolve()` throws `errors.playback.unsupported_provider`
for a live Episode (`app/Services/PlaybackTicketService.php:75-89`).
`app/Providers/IntegrationServiceProvider.php:35` tags three media providers and
knows no other kind. `T-100`'s draft put recordings on
`SchedulesMeetings::recordings()` returning a `MeetingRecording`, with its
HTTP client in `app/Integrations/Concerns/ZoomHttpClient.php` — a folder
`D-022` forbids and `ArchitectureTest::test_integrations_keep_no_shared_concerns_folder`
(`tests/Feature/ArchitectureTest.php:45`) refuses — and stored the result as a
new Video Episode, which `D-024` rules out. `D-027` replaces all of that with a
scheduled REST poll on the creator's own token: a `FindsRecordings` contract, a
`ZoomRecordings` finder beside `T-141`'s `ZoomClient`, and a recording as a row
of its own (`T-126`'s `episode_recordings`) holding the share link when the
vendor returns one, else the play link, never a download token, with only a
completed video file ever counting. `PROCESS.md` says a spec that names a
vendor payload cites an observed response, and `tests/Fixtures/` holds
`planning/` and `reachability/` and nothing from Zoom, which is why `T-122`
runs first and this task reads what it commits.

Afterwards the Zoom folder can answer one question for one live Episode: which
instances of its meeting were recorded inside the session's window, and where
each recording opens. `FindsRecordings` states that question in Qori's terms —
`handles()` for a link, `find()` for the recordings, `openUrl()` for the link a
Peer follows, `cloudRecording()` for whether the account keeps any —
`SessionRecording` carries each answer as a vendor-neutral shape, and
`ZoomMeetingLink` is the only place a Zoom host or path pattern appears.
`ZoomRecordings` is tagged `recording-finders` and reached by nothing until
`T-143`'s `qori:recordings:find` sweeps with it and `T-144`'s Check now runs
it at once; every test that calls Zoom fakes it with `T-122`'s fixture bodies,
and no test reaches the vendor.

## Decisions taken to make this specifiable

**The contract is `FindsRecordings` with the five methods the sprint brief
names, and it is a contract of its own rather than a method on
`ResolvesMedia`.** `ResolvesMedia::linkFor()` answers at play time for an
Episode's own media and takes no clock; finding a recording is a read of the
vendor's account after a session, keyed on a meeting the Episode only points
at, and it returns a list. Two jobs, two contracts, one binding each
(`app/Providers/IntegrationServiceProvider.php:29-30` already keeps
`SellsSeries` and `BillsGroups` apart for the same reason). The tag is
`recording-finders`; the `when()->needs('$finders')->giveTagged()` line for
whichever Service first takes the set is that Service's task (`T-143`), as
`PlaybackTicketService`'s line is here (`:37-39`).

**`find()` takes the Episode, the Connection and a timeout, and reads
everything else off the Episode.** The window comes from `starts_at` and
`ends_at` (`T-123`), the meeting from `content['meeting_id']` when the
connected tier has written it and from `content['join_url']` otherwise, and
`content['occurrence_id']` when `T-100` has stored one. The caller passes a
usable Connection it has refreshed — `T-141`'s Notes: a Zoom access token
lasts an hour, so `T-143` and `T-144` call `ConnectionService::fresh()` before
the finder — and a timeout in seconds per call, 30 from the sweep and 5 from
Check now, which are `T-143`'s constants on `LiveSessionService` rather than
this folder's, because an integration may not import `App\Services`
(`tests/Feature/ArchitectureTest.php:139`) and so cannot read a constant kept
there. **An Episode the finder cannot look for is a programmer error.** An
Episode with no meeting id — which, for one the connected tier has not stamped,
is exactly a `join_url` that `handles()` refuses — one that is not live or has
no `starts_at` or no `ends_at`, or a Connection that is not Zoom's or not
`isUsable()` (`app/Models/Connection.php:91-94`) throws
`InvalidArgumentException` and sends nothing, as `T-125`'s `stateFor()` does
for a non-live Episode: the sweep filters candidates with `handles()` first,
and a sweep that forgets to should fail in its tests rather than quietly find
nothing.

**The instances list is always read; the meeting-id read comes first and its
body is reused.** The brief and `D-027` describe `GET /meetings/{meetingId}/recordings`
as the first call — it returns the latest instance — with
`GET /past_meetings/{meetingId}/instances` as the fallback when that instance
is outside the window. A restarted meeting is two instances (owner acceptance
8, `T-122`'s `list_instances.restarted.200.json`), and the meeting-id read
returns one of them, so a finder that stops at the shortcut can never return
Part 1 when Part 2 exists: exactly the silent wrong attach the acceptance
forbids. So `find()` reads the latest instance, then the instances list (one
MEDIUM-tier call, `docs/planning/course-classroom.md`, vendor facts), keeps
every instance whose `start_time` falls inside the window, and reads
recordings by uuid for each of those except the one whose body it already
holds. A normal session costs two calls; a restart three. If the spike's
`restarted` fixtures show one instance per restart, the instances read can go
back to being the fallback and this is one line — see "Before this can be
ready".

**The window is `[starts_at − 60 min, ends_at + 120 min]`, as two public
constants on `ZoomRecordings`.** `D-027`'s numbers, provisional until `T-122`
question 1 says how far an instance's `start_time` drifts. Not in
`config('qori.live')`, because `config/qori.php` is `T-123`'s and frozen for
this stream (its stream file names the only two exceptions), and not on the
contract, because how far a vendor's instance drifts from a schedule is that
vendor's. Public so `T-143`'s tests can place an Episode against them. When
`content['occurrence_id']` is set and the instances list carries
`occurrence_id`, the instances with that id are the wanted set and the window
is not consulted (`D-027`: "matching on `occurrence_id` when stored"); the
key's presence in the list is question 1's.

**One `SessionRecording` per instance; `vendorRef` is the instance `uuid`.**
An instance is what Zoom records once and what `episode_recordings` keeps
unique on (`(episode_id, vendor_ref)`, `D-027`), so Part 1 and Part 2 of a
restarted meeting are two objects in `startedAt` order. A recording stopped
and started again inside one instance (`T-122`'s `get_meeting.paused.200.json`)
is one instance with several video files and stays one object: the share
page lists every segment, and with no share link the earliest video by
`recording_start` is the link. `startedAt` is the instance's `start_time`,
`durationMinutes` its `duration`.

**Only a `completed` file counts, only a video file is a recording, and
`isVideo` says whether the link has one behind it.** `D-027`: a transcript or
an audio-only file never is a recording. `find()` looks at
`recording_files[]` whose `status` is `completed` and picks the `MP4` whose
`recording_type` comes first in `VIDEO_TYPES`, then the earliest by
`recording_start`. When the instance has a share link, it is returned whether
or not a completed video exists yet — no completed file at all is the ordinary
still-processing case and still counts — with `isVideo` false in that case, so
`T-143` can tell "the instance exists and its video is not finished" from
"nothing found" and keep checking instead of declaring the session unrecorded;
`T-143` attaches only `isVideo` rows. When there is no share link and no
completed video, there is nothing a Peer could open, and the instance is left
out. So the one test is `$url`: a completed transcript, chat file or audio
file neither makes a recording nor suppresses one. Which `status` value a file still processing carries, or whether the
whole call answers 404 until then, is question 2's; both paths are specified.

**`url` is `share_url` when present, else the video's `play_url`, stored
bare; `passcode` is `recording_play_passcode`, else `password`; `openUrl()`
appends `pwd`.** `D-027`: the share link when the vendor returns one, else the
play link, never a download token (`download_url` carries an `access_token`
and is never read). `share_url` is documented only on the
`recording.completed` webhook and its presence in the REST body is question 9.
Zoom documents splicing `recording_play_passcode` into `play_url` or
`share_url` as `?pwd=`, which is why that field is the passcode, with the
human `password` as the fallback when the token is absent. `openUrl()` is a
string operation — `?pwd=` or `&pwd=` when the url already has a query,
`rawurlencode`d — and makes no vendor call, so Watch stays what `D-027` says
it is. Whether `?pwd=` opens signed out is question 3, and if it does not,
`openUrl()` has no link a Peer can follow and the owner decides the third
answer (`T-122`'s Notes) — see below.

**`availableUntil` comes from the payload's `auto_delete_date` alone.** `T-141`
also reads `recording.auto_delete_cmr_days` and offers it as a fallback; it
is not used, because a date computed from a days figure is a date Qori never
observed, and `D-027` shows `available_until` so an auto-delete is never a
surprise — a wrong date is a worse surprise than none. Null when the payload
carries no date. The format is question 9's (`get_meeting.auto_delete.200.json`).

**A 404 is an empty answer; every other failure throws through
`ZoomClient::unwrap()`; a transport failure is an upstream timeout.** No
recording yet, a recording in the trash, and a meeting that is not this
account's all answer `[]` and never an exception, because the sweep backs off
on nothing found and the creator is nudged at `recording_wait_hours` (`T-129`,
`T-143`), and `T-141`'s `limits.common.meeting_links` already told the creator
which links Qori cannot look for. Whether another host's meeting answers 404
or a 400 with a `code` is question 6's (`get_meeting.other_host.<status>.json`);
`NOT_THIS_ACCOUNT_CODES` carries whatever it recorded, empty until then. A 401,
403, 429 or 5xx reaches the caller as `AppException::upstreamUnavailable` with
`upstream` set to the status — `unwrap()`'s contract from `T-141` — and a
`ConnectionException` as `AppException::upstreamTimeout` with `upstream`
`timeout`. How many attempts it took is `T-141`'s: `api()` retries
`ZoomClient::READ_ATTEMPTS` (2) times and its `retryWhen()` retries a
`ConnectionException` or a 5xx only, so a 401, a 403 and a 429 are each one
call. **No lang key is passed.** Nothing here answers a person: the sweep
logs, and the one sentence a creator reads when Check now meets a failure is
`T-144`'s.

**`ZoomMeetingLink` is the one place a Zoom host or path pattern appears, and
a personal meeting id is told from a scheduled meeting's by its digits.** The
brief: PMI and vanity links yield null. A `zoom.us/my/{name}` link is a
personal room by shape. A `zoom.us/j/{id}` link is a personal room when the id
has fewer than eleven digits — Zoom has generated eleven-digit ids for
scheduled meetings since 2020 and personal meeting ids stay ten — which is a
rule from Zoom's help centre, unobserved, and `T-122`'s link-shape table
(question 6) confirms or corrects it. A regional host (`us02web.zoom.us`), a
`pwd` query and a fragment are accepted; another host, plain `http`, and a
host that merely contains `zoom.us` are not. `handles()` is exactly
`meetingId() !== null`.

**`content['meeting_id']` and `content['occurrence_id']` are read here and
written by nothing here.** `D-026` reserves `meeting_id` for "the Zoom folder
when a finder reads the link"; the same decision puts every write to a live
Episode's `content` under `LiveSessionService::withLockedContent()`, a Service
an integration may not import. This draft parses the link on every call and
stores nothing, which costs one regular expression per check; storing the id,
and which layer does it, is a bullet for the owner below.

**`cloudRecording()` is on the contract for `T-144`, and `T-143` never calls
it.** `T-141` reads `recording.cloud_recording` into
`connections.settings.cloud_recording` at connect and reconnect, and the sweep
reads that key. `T-141`'s Notes name Check now as the place a creator who
upgraded gets the setting re-read without reconnecting, and Check now holds
the finder, not the connector — so the finder carries the read. Best effort:
a failed call or an absent key is `null`, never an exception, as `T-141`'s
settings read is.

**Tests place the Episode around the fixture's `start_time`, writing the row
directly.** The fixtures carry the dates the spike recorded, all in the past
by the time a test runs, and `EpisodeService::add()` refuses a past start on
create (`guardLiveSessionTime`, `creating: true`). So a helper reads
`start_time` from the fixture, sets `starts_at` three minutes before it (a
host who started a little late, the common case) and `ends_at` ninety minutes
on, and writes the row with `$series->episodes()->create()`, the way
`database/factories/SeriesFactory.php:65` already writes one, and the way
`T-129` and `T-143` place their live Episodes.
Every case that reaches the client fakes Zoom with `Http::fake()` and a fixture
body, with `Http::preventStrayRequests()` in `setUp()` as `PlaybackTest.php:32-37`; a
case that needs a shape no fixture holds edits the fixture's array in the test
rather than adding a fixture nobody observed, as `T-141` does.

**The feature file is `tests/Feature/Integrations/Zoom/ZoomRecordingsTest.php`,
and the parser's cases are a unit file.** `T-141` creates that directory for
`ZoomAccountsTest.php` and its Files row says `T-142` "adds
`ZoomRecordingsTest.php` beside it", so the two Zoom test files already sit
together and nothing here chooses a home.
`ZoomMeetingLink::meetingId()` calls
nothing, so its cases extend bare `PHPUnit\Framework\TestCase` under
`tests/Unit/Integrations/Zoom/`, the way `T-089` puts `VendorLinkTest` under
`tests/Unit/Data/`; `tests/Unit/` is empty today.

**No copy, no route, no schema, no config.** Nothing here is read by a person;
the finder answers a Service. `T-123`'s `qori.live` block already holds every
number the sprint reads, `T-141`'s `services.zoom` and `qori.connections.zoom`
hold the client's, and the two window constants are the vendor's drift, kept
with the vendor. `episode_recordings` is `T-126`'s table and this task inserts
nothing into it.

## Preconditions

`T-141` done, so `app/Integrations/Zoom/ZoomClient.php` with `api()` and
`unwrap()`, `ZoomAccounts`, `config('services.zoom')`,
`Connection::factory()->zoom()` and `docs/tinker/connections.md`'s Zoom
paragraph exist. `T-123` done (it is `ready`), so `episodes.ends_at`,
`Episode::$fillable` with `ends_at`, and a live `content` of `join_url` and
`records` exist. `T-122` done, so `tests/Fixtures/zoom/README.md` and the
`recordings/*` fixtures exist.

**Data this task verifies against:** a clean database and the fixtures under
`tests/Fixtures/zoom/recordings/`. A test builds its own Group, Series,
Episode and Connection.

**Equipment:** none. Every check runs from the terminal against faked HTTP.
To run the finder against Zoom itself, the tinker paragraph below needs
`T-141`'s equipment: the General app in development mode on Qori's own Zoom
account, its credentials in `.env`, and a connection made through the
Integrations page.

**Spike:** `T-122` is the spike. This task cites, by name, the fixture each
field comes from; a fixture that `T-122`'s gap list says could not be produced
leaves the corresponding branch as an expectation from Zoom's reference, and
the case that reads it edits a fixture that does exist. Every field is listed
under "Before this can be ready" with the question that settles it.

## Scope

**In:**

- `App\Integrations\Contracts\FindsRecordings` and `App\Data\SessionRecording`.
- `App\Integrations\Zoom\ZoomMeetingLink` and `App\Integrations\Zoom\ZoomRecordings`,
  the latter tagged `recording-finders` in `IntegrationServiceProvider`.
- `find()` as `D-027` describes it: the meeting-id read, the instances list,
  the window (or the stored `occurrence_id`), recordings by uuid with
  double-encoding, completed video files only, the share link else the play
  link, the passcode, the start, the length, `auto_delete_date`.
- `openUrl()` appending the passcode; `cloudRecording()` reading
  `/users/me/settings`.
- A "find a recording against a fixture" paragraph in
  `docs/tinker/connections.md`.
- Twenty-four tests: every case that calls Zoom reads a fixture body or a body
  edited from one, and the rest (`openUrl()`, `handles()`, the parser) call
  nothing.

**Out:**

- The sweep: `qori:recordings:find`, its candidate filter, the backoff,
  `episodes.recording_checked_at`, `series.recording_publication`,
  `LiveSessionService::attachFound()`, the ambiguity hold, the creator's
  `review` copy and `creator_recording_needed` with detection (`T-143`).
- Publish, reject, picking among several held, Check now and its throttle,
  and the one line a creator reads when a check fails (`T-144`).
- The `source = zoom` arm of Watch in `PlaybackTicketService::watch()`:
  `T-126` wrote "`T-142` routes a zoom row through `FindsRecordings::openUrl()`
  here" (`:599`), but this task does not depend on `T-126` and the first task with
  both the finder and a `zoom` row is `T-143` — see Notes.
- Writing `content['meeting_id']` or `content['occurrence_id']`; inserting an
  `episode_recordings` row; any change to `LiveSessionService`.
- `GET /users/me/recordings?from=&to=`, the one-call alternative `T-122`
  question 1 compares; built only if the spike prefers it, as a re-scope of
  this draft.
- `GET /meetings/{meetingId}/recordings/settings`: read by the spike to
  answer question 3 and never by Qori (`D-027`: only Check now and the sweep
  re-read the vendor, and neither writes).
- Webhooks, `ZoomWebhook`, `recording.completed`, `app_deauthorized`.
- A Teams or Meet finder: a Teams recording sits in the organiser's OneDrive
  and a Meet recording in the organiser's Drive, both pasted (`D-025`);
  `EpisodeProvider::Link` never has a finder.
- Registrants, the meeting picker and the Series container (`T-099`,
  `T-100`); any change to `ZoomClient` or `ZoomAccounts` (`T-141`).
- The fixtures and the README (`T-122`); the frozen scope list
  (`vendor-accounts.md`).

## Files

| Path                                                     | Change | Notes                                                                                     |
| -------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------- |
| `app/Integrations/Contracts/FindsRecordings.php`         | new    | `provider()`, `handles()`, `find()`, `openUrl()`, `cloudRecording()`                      |
| `app/Data/SessionRecording.php`                          | new    | Seven properties, and the docblock mapping them to `episode_recordings`                   |
| `app/Integrations/Zoom/ZoomMeetingLink.php`              | new    | `meetingId()`; the only Zoom host and path pattern                                        |
| `app/Integrations/Zoom/ZoomRecordings.php`               | new    | `FindsRecordings`; the window constants; the file rules                                   |
| `app/Providers/IntegrationServiceProvider.php`           | edit   | `ZoomRecordings` tagged `recording-finders`                                               |
| `docs/tinker/connections.md`                             | edit   | "Find a recording against a fixture", under `T-141`'s Zoom paragraph (`T-044`'s new file) |
| `tests/Feature/Integrations/Zoom/ZoomRecordingsTest.php` | new    | 19 cases, beside `T-141`'s `ZoomAccountsTest.php` in the directory it creates             |
| `tests/Unit/Integrations/Zoom/ZoomMeetingLinkTest.php`   | new    | 5 cases; bare `PHPUnit\Framework\TestCase`; `tests/Unit/` is empty today                  |

The fixtures under `tests/Fixtures/zoom/recordings/` are read and never
written. No route: nothing here answers HTTP. No lang file: nothing here is
read by a person. No `config/qori.php` row: `T-123` declared the stream's
numbers and the two window constants are the vendor's. No factory or seeder:
no column is added. No flow file either: the finder is reached by nothing until
`T-143`, which adds the sweep's chain to `docs/flows/live-sessions.md`
(`T-125`'s file, and the task that rewrites `docs/flows/README.md:42-43`).
`docs/flows/storage.md`'s Connections section, which `T-141` edits, describes
connecting and not finding.
`tests/Feature/ArchitectureTest.php` is unchanged and its two integration
rules (`:45`, `:139`) now walk the Zoom folder.

Flows: none — the finder is reached by nothing until `T-143`'s sweep and
`T-144`'s Check now, and those tasks write the chain into
`docs/flows/live-sessions.md`.

## Database

None. The finder reads `episodes.starts_at`, `episodes.ends_at` (`T-123`) and
`episodes.content` (`join_url`, and `meeting_id` and `occurrence_id` when the
connected tier has written them), and `connections.access_token`; it writes
no row. Its answers become `episode_recordings` rows in `T-143`, by the
mapping `SessionRecording`'s docblock states.

## Code

```php
namespace App\Integrations\Contracts;

use App\Data\SessionRecording;
use App\Enums\EpisodeProvider;
use App\Exceptions\AppException;
use App\Models\Connection;
use App\Models\Episode;
use InvalidArgumentException;

/**
 * Finding the cloud recordings of a live Episode's meeting on the creator's own
 * account (D-027). A contract of its own beside ResolvesMedia: that one answers
 * a play link for an Episode's own media at play time; this one reads a vendor's
 * account after a session and returns a list, keyed on a meeting the Episode
 * only points at. Tagged `recording-finders`; qori:recordings:find (T-143) and
 * Check now (T-144) are the callers.
 */
interface FindsRecordings
{
    /** Which Episode provider this finder looks for. Zoom; Teams later; never Link. */
    public function provider(): EpisodeProvider;

    /** Whether this finder can look for the meeting behind a pasted join link at all. */
    public function handles(string $joinUrl): bool;

    /**
     * Every instance of the Episode's meeting recorded inside its window, in
     * start order. Empty when nothing is found yet, when the recording is gone,
     * and when the meeting is not this account's — the sweep backs off on an
     * empty answer. $timeoutSeconds bounds each call, not the whole search.
     *
     * @return list<SessionRecording>
     *
     * @throws InvalidArgumentException for an Episode handles() refuses, one that is not live or has no ends_at, or a Connection that is not usable or not this provider's — a programmer error, since the caller filters first
     * @throws AppException upstreamUnavailable for a refused token, a rate limit or a server error that outlived the retry; upstreamTimeout for a transport failure
     */
    public function find(Episode $episode, Connection $connection, int $timeoutSeconds): array;

    /** The link a Peer follows for a recording this finder found. A string operation: Watch makes no vendor call (D-027). */
    public function openUrl(SessionRecording $recording): string;

    /**
     * Whether the connected account keeps cloud recordings, read from the
     * vendor now. Null when it could not be read. For Check now (T-144); the
     * sweep reads connections.settings.cloud_recording, which T-141 stores.
     */
    public function cloudRecording(Connection $connection, int $timeoutSeconds): ?bool;
}
```

```php
namespace App\Data;

use Carbon\CarbonImmutable;

/**
 * One recorded instance of a live Episode's meeting, as a finder reports it
 * (D-027). Vendor-neutral: the finder maps the vendor's payload here, and
 * T-143 writes an episode_recordings row from it — vendorRef → vendor_ref,
 * url → url, passcode → passcode, startedAt → started_at,
 * durationMinutes → duration_minutes, availableUntil → available_until,
 * source from the finder's provider(). isVideo false never becomes a row.
 */
class SessionRecording
{
    public function __construct(
        /** The vendor's id for this instance of the meeting; unique per Episode in episode_recordings. */
        public string $vendorRef,
        /** The link Peers open, stored bare: no passcode in it, and never a download token. */
        public string $url,
        /** What openUrl() carries and the card shows; null when the vendor set none. */
        public ?string $passcode,
        /** When the instance started, UTC. */
        public CarbonImmutable $startedAt,
        public int $durationMinutes,
        /** The date the vendor will delete it, UTC midnight; null when it keeps it. */
        public ?CarbonImmutable $availableUntil,
        /** A completed video file is behind $url. False: the instance has a share link, and no completed video behind it yet. */
        public bool $isVideo,
    ) {}
}
```

```php
namespace App\Integrations\Zoom;

/**
 * Reads the meeting id out of a Zoom join link. The only place in Qori a Zoom
 * host or path pattern appears (D-022, D-027): the sweep, the Service and every
 * query ask handles() and never look at the URL.
 *
 * Provisional until T-122's link-shape table (question 6).
 */
class ZoomMeetingLink
{
    /**
     * https://zoom.us/j/{id} and https://{region}.zoom.us/j/{id}, with any query
     * (pwd=…) or fragment after it. Not http, not another host, not a host
     * that merely contains zoom.us, not /my/{name} (a personal room by shape).
     */
    public const PATTERN = '~^https://(?:[a-z0-9-]+\.)?zoom\.us/j/(\d+)(?:[/?#]|$)~i';

    /**
     * A scheduled meeting's id has eleven digits (Zoom, since 2020); a personal
     * meeting id has ten. Fewer than eleven is treated as a personal room and
     * yields null, so the sweep never looks for a PMI's recordings: D-027's
     * fourth hold reason ("a meeting id from a personal or vanity link") is
     * applied by never looking, and the creator pastes the link instead.
     */
    public const MEETING_ID_DIGITS = 11;

    /** The meeting id, or null for a link this folder will not look for. */
    public static function meetingId(string $joinUrl): ?string;
    // preg_match(self::PATTERN, trim($joinUrl), $m) === 1 && strlen($m[1]) === self::MEETING_ID_DIGITS ? $m[1] : null
}
```

```php
namespace App\Integrations\Zoom;

use App\Data\SessionRecording;
use App\Enums\ConnectionProvider;
use App\Enums\EpisodeProvider;
use App\Exceptions\AppException;
use App\Integrations\Contracts\FindsRecordings;
use App\Models\Connection;
use App\Models\Episode;
use Carbon\CarbonImmutable;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Support\Facades\Log;
use InvalidArgumentException;

/**
 * https://developers.zoom.us/docs/api/meetings/ — GET /meetings/{meetingId}/recordings
 * (LIGHT), GET /past_meetings/{meetingId}/instances (MEDIUM), GET /users/me/settings
 * (MEDIUM). Every field named here is an expectation until its fixture under
 * tests/Fixtures/zoom/recordings/ exists; the fixture is named beside each.
 */
class ZoomRecordings implements FindsRecordings
{
    /** D-027's window: an instance that started this long before starts_at is still this session's. Provisional (T-122 question 1). */
    public const WINDOW_BEFORE_MINUTES = 60;

    /** …and one that started this long after ends_at still is. Provisional (T-122 question 1). */
    public const WINDOW_AFTER_MINUTES = 120;

    /** recording_files[].status — the only documented value; what a file still processing carries is T-122 question 2's. */
    public const FILE_STATUS_COMPLETED = 'completed';

    /** recording_files[].file_type of a video. Never M4A, TRANSCRIPT, CHAT, CC or TIMELINE (D-027). */
    public const VIDEO_FILE_TYPE = 'MP4';

    /** recording_files[].recording_type preference for the play link when share_url is absent, best first. Provisional (fixtures). */
    public const VIDEO_TYPES = [
        'shared_screen_with_speaker_view',
        'speaker_view',
        'shared_screen_with_gallery_view',
        'gallery_view',
        'shared_screen',
        'active_speaker',
    ];

    /** The query parameter Zoom documents for splicing recording_play_passcode into play_url or share_url. */
    public const PASSCODE_PARAMETER = 'pwd';

    /**
     * Error codes a 400 carries for a meeting that is not this account's, from
     * get_meeting.other_host.<status>.json (T-122 question 6). Empty until the
     * fixture exists; a 404 needs no code.
     *
     * @var list<int>
     */
    public const NOT_THIS_ACCOUNT_CODES = [];

    public function __construct(private ZoomClient $client) {}

    public function provider(): EpisodeProvider;            // EpisodeProvider::Zoom

    public function handles(string $joinUrl): bool;          // ZoomMeetingLink::meetingId($joinUrl) !== null

    /**
     * 1. $meetingId = $this->meetingIdFor($episode) — InvalidArgumentException when null, when
     *    ! $episode->isLive(), when $episode->starts_at or $episode->ends_at is null, when
     *    $connection->provider !== ConnectionProvider::Zoom, or when ! $connection->isUsable().
     *    Nothing is sent.
     * 2. $from = $episode->starts_at->toImmutable()->subMinutes(self::WINDOW_BEFORE_MINUTES);
     *    $to = $episode->ends_at->toImmutable()->addMinutes(self::WINDOW_AFTER_MINUTES);
     * 3. $latest = $this->recordingsOf($connection, $meetingId, $timeoutSeconds);
     *    GET /meetings/{meetingId}/recordings → uuid, id, start_time, duration, share_url?,
     *    recording_play_passcode?, password?, auto_delete_date?, recording_files[]
     *    [get_meeting.latest.200.json]; null on a 404 [get_meeting.processing.<status>.json,
     *    get_meeting.deleted.<status>.json].
     * 4. $instances = $this->instancesOf($connection, $meetingId, $timeoutSeconds);
     *    GET /past_meetings/{meetingId}/instances → meetings[] of uuid, start_time, occurrence_id?
     *    [list_instances.daily.200.json]; [] on a 404.
     * 5. $occurrenceId = $episode->content['occurrence_id'] ?? null (a non-empty string, else null).
     *    $wanted is a list of uuids, in either the occurrence branch or the window branch and never both:
     *      - $occurrenceId !== null and at least one instance carries a non-empty 'occurrence_id':
     *        the uuids of the instances whose occurrence_id === $occurrenceId. $from and $to are not
     *        consulted and $latest is not added, whatever its start_time (D-027, "matching on
     *        occurrence_id when stored").
     *      - otherwise: the uuids of the instances whose start_time is within [$from, $to], plus
     *        $latest['uuid'] when $latest !== null, its start_time is within [$from, $to] and that
     *        uuid is not already in the list — which is what answers when the instances read 404s.
     *    Duplicates are dropped; the order does not matter, step 7 sorts.
     * 6. For each wanted uuid: $body = $latest !== null && $latest['uuid'] === $uuid
     *        ? $latest
     *        : $this->recordingsOf($connection, self::encode($uuid), $timeoutSeconds);   // [get_meeting.by_uuid.200.json]
     *    $recording = $body === null ? null : $this->recordingFrom($body); keep the non-null ones.
     * 7. Sort by startedAt ascending; return the list.
     *
     * @return list<SessionRecording>
     */
    public function find(Episode $episode, Connection $connection, int $timeoutSeconds): array;

    /** $recording->passcode === null ? $recording->url : $recording->url.(str_contains($recording->url, '?') ? '&' : '?').self::PASSCODE_PARAMETER.'='.rawurlencode($recording->passcode) */
    public function openUrl(SessionRecording $recording): string;

    /**
     * GET /users/me/settings → recording.cloud_recording [user_settings.pro.200.json,
     * user_settings.basic.<status>.json]. The value when it is a bool; null when the key is
     * absent, the call fails after the retry, or the transport fails — logged at warning,
     * never thrown. The same key T-141's ZoomAccounts::settingsFrom() maps at connect.
     */
    public function cloudRecording(Connection $connection, int $timeoutSeconds): ?bool;

    /** content['meeting_id'] when a non-empty string (the connected tier's, T-100), else ZoomMeetingLink::meetingId(content['join_url'] ?? ''). Never written back. */
    private function meetingIdFor(Episode $episode): ?string;

    /**
     * GET /meetings/{meetingIdOrEncodedUuid}/recordings through $this->client->api((string) $connection->access_token, $timeoutSeconds).
     * 404 → null. A 400 whose body `code` is in NOT_THIS_ACCOUNT_CODES → null. Every other status,
     * 2xx included, goes to $this->client->unwrap($response, "recordings of {$ref}"), which returns the
     * body of a 2xx and otherwise throws upstreamUnavailable with upstream = the status; no lang key is
     * passed. ConnectionException → AppException::upstreamTimeout(devMessage: "Zoom recordings of {$ref} timed out", upstream: 'timeout', previous: $e).
     *
     * @return ?array<string, mixed>
     */
    private function recordingsOf(Connection $connection, string $ref, int $timeoutSeconds): ?array;

    /**
     * GET /past_meetings/{meetingId}/instances, same client, same failure rules (a 2xx through
     * unwrap(), context "instances of {$meetingId}"); 404 → [].
     * Returns the body's `meetings` list, [] when absent.
     *
     * @return list<array<string, mixed>>
     */
    private function instancesOf(Connection $connection, string $meetingId, int $timeoutSeconds): array;

    /**
     * $files = recording_files[] whose status === FILE_STATUS_COMPLETED ([] when the key is absent).
     * $video = the $files entry with file_type === VIDEO_FILE_TYPE whose recording_type comes first in
     *          VIDEO_TYPES (an MP4 with a type not listed comes after every listed one), ties by the earliest
     *          recording_start [get_meeting.paused.200.json holds several]; null when none.
     * $url = share_url when a non-empty string [T-122 question 9], else $video['play_url'], else null.
     * Returns null when $url is null — the only test, so a completed transcript, chat or audio file
     * neither makes a recording nor suppresses one. Otherwise:
     *   vendorRef = (string) $body['uuid'],
     *   url = $url,
     *   passcode = recording_play_passcode when a non-empty string, else password when a non-empty string, else null,
     *   startedAt = CarbonImmutable::parse((string) $body['start_time'], 'UTC'),
     *   durationMinutes = (int) ($body['duration'] ?? 0),
     *   availableUntil = isset($body['auto_delete_date']) ? CarbonImmutable::parse((string) $body['auto_delete_date'], 'UTC')->startOfDay() : null   [get_meeting.auto_delete.200.json],
     *   isVideo = $video !== null.
     *
     * @param  array<string, mixed>  $body
     */
    private function recordingFrom(array $body): ?SessionRecording;

    /**
     * Zoom: a meeting UUID that begins with `/` or contains `//` must be double
     * URL-encoded in a path [get_meeting.by_uuid_encoded.<status>.json].
     */
    private static function encode(string $uuid): string;
    // str_starts_with($uuid, '/') || str_contains($uuid, '//') ? rawurlencode(rawurlencode($uuid)) : rawurlencode($uuid)
}
```

```php
// app/Providers/IntegrationServiceProvider.php — one tag beside media-providers (:35).
// The when()->needs('$finders')->giveTagged('recording-finders') line belongs to the first
// Service that takes the set (T-143), as PlaybackTicketService's does at :37-39.
$this->app->tag([ZoomRecordings::class], 'recording-finders');
```

Call budget, for `T-143`'s and `T-144`'s timeouts: a session with one
instance costs two calls (the meeting-id read and the instances list), a
restart three, and each further in-window instance one more, each bounded by
`$timeoutSeconds`. `GET /meetings/{id}/recordings` is in Zoom's LIGHT tier and
the other two reads are MEDIUM, all shared across every app on the account
(`docs/planning/course-classroom.md`, vendor facts).

`docs/tinker/connections.md`, under `T-141`'s Zoom paragraph, "Find a
recording against a fixture": `Http::fake()` with
`get_meeting.latest.200.json` and `list_instances.daily.200.json` keyed on
`https://api.zoom.us/v2/meetings/91827405566/recordings` and
`https://api.zoom.us/v2/past_meetings/91827405566/instances`; a live Episode
written around the fixture's `start_time`; `Connection::factory()->zoom()`
inside `CurrentGroup::runFor()`; then
`app(App\Integrations\Zoom\ZoomRecordings::class)->find($episode, $connection, 30)`
and `->openUrl($found[0])`. A second block without the fake, against the
development app, for whoever has `T-141`'s equipment.

## Copy

None. Nothing this task builds is read by a person: `find()` answers a
Service, its failures are logged by the sweep, and the one sentence a creator
reads when Check now meets one is `T-144`'s. `T-141`'s
`connections.providers.zoom.limits.common.meeting_links` already tells the
creator which links Qori cannot look for.

## Routes

None.

## Tests

Every case that reaches the client fakes Zoom with `Http::fake()` and a fixture
body under `tests/Fixtures/zoom/recordings/` (`T-122`'s), keyed on the full URL, the
meeting-id pattern before the `*` uuid pattern because Laravel takes the first
match; `Http::preventStrayRequests()` in `setUp()`. Private helpers:
`fixture(string $file): array` (decodes the file), `liveEpisode(array $fixture, array $content = ['join_url' => 'https://zoom.us/j/91827405566', 'records' => true]): Episode`
(a Group with a timezone, `SeriesService::create()`, then
`$series->episodes()->create()` with `type` Live, `provider` Zoom, `starts_at`
three minutes before the fixture's `start_time`, `ends_at` ninety minutes on),
`zoomConnection(Group $group): Connection`
(`Connection::factory()->zoom()->create(['group_id' => …])` inside
`CurrentGroup::runFor()`, as `PlaybackTest.php:112`), and
`finder(): ZoomRecordings` (`app(ZoomRecordings::class)`).

**New: `tests/Feature/Integrations/Zoom/ZoomRecordingsTest.php` — 19 cases**

1. `test_it_handles_a_zoom_join_link_and_nothing_else` — `handles()` true for `https://zoom.us/j/91827405566` and `https://us02web.zoom.us/j/91827405566?pwd=REDACTED`; false for `https://zoom.us/my/spike`, a Teams `meetup-join` link and a Meet link; nothing sent.
2. `test_the_latest_instance_inside_the_window_is_the_recording` — `get_meeting.latest.200.json` and `list_instances.daily.200.json`: one `SessionRecording`; `vendorRef` is the body's `uuid`, `url` is `share_url` (or the MP4's `play_url` when the fixture has none), `passcode` is `recording_play_passcode` (or `password`), `startedAt` equals `start_time`, `durationMinutes` equals `duration`, `isVideo` true; `Http::assertSentCount(2)` and no uuid read.
3. `test_an_early_test_recording_outside_the_window_is_left_behind` — the meeting-id read answers `get_meeting.early_test.200.json` (the day before), `list_instances.early_test.200.json` holds both instances, the in-window uuid answers `get_meeting.by_uuid.200.json`: exactly one recording, its `vendorRef` the in-window uuid, the early test's absent (owner acceptance 8).
4. `test_a_restarted_meeting_is_two_recordings_in_start_order` — `list_instances.restarted.200.json`; the meeting-id read answers `get_meeting.restarted.200.json`, the other uuid its own body: two recordings ordered by `startedAt`, distinct `vendorRef`s, the latest body reused so `Http::assertSentCount(3)` (owner acceptance 8).
5. `test_a_stopped_and_restarted_recording_in_one_instance_is_one_recording` — `get_meeting.paused.200.json`: one recording; with `share_url` absent, `url` is the earliest completed MP4's `play_url` by `recording_start`; `durationMinutes` is the instance's `duration`.
6. `test_a_uuid_that_needs_it_is_double_encoded` — an instance uuid `/abc//def==` edited into the instances fixture (or `get_meeting.by_uuid_encoded.<status>.json` once it exists): `Http::assertSent()` sees the path containing `rawurlencode(rawurlencode('/abc//def=='))`, and a plain uuid is single-encoded.
7. `test_only_a_completed_video_file_is_a_recording` — the `latest` body edited so the MP4's `status` is not `completed` and the M4A's is, and again so the only completed files are TRANSCRIPT and CHAT, and again with no `recording_files` at all: each comes back with `isVideo` false while `share_url` is present, and each is absent from the list once `share_url` is stripped too.
8. `test_a_recording_still_processing_or_deleted_answers_nothing` — `get_meeting.processing.<status>.json` and `get_meeting.deleted.<status>.json` as the meeting-id answer, with the instances read answering 404: `[]` and no exception in both.
9. `test_another_hosts_meeting_answers_nothing` — `get_meeting.other_host.<status>.json` and a 404 instances read: `[]`; the case asserts a 404, and when the fixture recorded a 400 its `code` joins `NOT_THIS_ACCOUNT_CODES` and the case asserts `[]` through it.
10. `test_a_stored_meeting_id_wins_over_the_link` — content `meeting_id` `91827405566` with `join_url` `https://zoom.us/j/99999999999`: every request path carries the stored id.
11. `test_a_stored_occurrence_id_picks_that_instance_whatever_the_window` — content `occurrence_id` equal to one entry's `occurrence_id` in `list_instances.daily.200.json`, the Episode placed so that no instance's `start_time` falls inside the window: that instance alone is read and returned. Dropped, with the branch, if the fixture carries no `occurrence_id`.
12. `test_a_link_the_finder_does_not_handle_is_a_programmer_error` — content `join_url` `https://zoom.us/my/spike`: `InvalidArgumentException`; a revoked Connection (`Connection::factory()->zoom()->revoked()`): the same; `Http::assertNothingSent()`.
13. `test_a_token_refusal_is_an_upstream_exception_after_one_call` — the meeting-id read answering 401 `{"code": 124, "message": "Invalid access token"}`: `AppException` with `ErrorCode::UpstreamUnavailable` and `upstream` `401`; `Http::assertSentCount(1)`.
14. `test_a_server_error_is_retried_once_then_thrown` — 500 on every call: the exception, `upstream` `500`, `Http::assertSentCount(2)`.
15. `test_a_timeout_is_an_upstream_timeout` — `Http::fake()` throwing `ConnectionException`: `AppException` with `ErrorCode::UpstreamTimeout` and `upstream` `timeout`.
16. `test_open_url_carries_the_passcode` — `?pwd=` appended to a bare url, `&pwd=` to one with a query, the passcode `rawurlencode`d, and the url unchanged when `passcode` is null.
17. `test_available_until_reads_the_auto_delete_date` — `get_meeting.auto_delete.200.json`: `availableUntil` is that date at UTC midnight; `get_meeting.latest.200.json`: null.
18. `test_cloud_recording_reads_the_user_settings_and_never_throws` — `user_settings.pro.200.json` → true; `user_settings.basic.<status>.json` → false when it answered, null when it was refused; 500 on every call → null, no exception, `Http::assertSentCount(2)`.
19. `test_the_finder_is_tagged_and_names_its_provider` — `app()->tagged('recording-finders')` yields exactly one object, an instance of `FindsRecordings`, whose `provider()` is `EpisodeProvider::Zoom`.

**New: `tests/Unit/Integrations/Zoom/ZoomMeetingLinkTest.php` — 5 cases**
(bare `PHPUnit\Framework\TestCase`; the directory is new, `tests/Unit/` holding
only its `.gitkeep` today)

20. `test_it_reads_the_meeting_id_from_a_plain_link` — `https://zoom.us/j/91827405566` → `91827405566`.
21. `test_it_reads_the_meeting_id_from_a_regional_link_with_a_passcode` — `https://us02web.zoom.us/j/91827405566?pwd=REDACTED#success` and `https://zoom.us/j/91827405566/` → `91827405566`.
22. `test_a_personal_meeting_room_yields_nothing` — `https://zoom.us/my/spike` and the ten-digit `https://zoom.us/j/9182740556` → null.
23. `test_another_host_yields_nothing` — a Teams link, a Meet link, `http://zoom.us/j/91827405566` and `https://zoom.us.example.test/j/91827405566` → null.
24. `test_a_malformed_link_yields_nothing` — `''`, `'zoom'`, `https://zoom.us/j/` and `https://zoom.us/j/abc` → null.

**Changed:** none. `tests/Feature/ArchitectureTest.php` walks the new folder
with no edit; `tests/Feature/Admin/ConsoleAccessTest.php`'s allow-list is
unchanged because nothing here calls `acrossAllGroups()`.

Total: 24 new cases. No Peer-surface route and no notification is added, so
the wrong-tenant, revoked-Access and renamed-vocabulary rules have nothing to
attach to here; the finder never reads an Access and never renders a noun.

## Acceptance

- [ ] A live Zoom Episode placed around `get_meeting.latest.200.json` yields
      one `SessionRecording` carrying the instance's uuid, the share link or
      the video's play link, the passcode, the start, the length, the
      auto-delete date and `isVideo`, and every field is cited to a fixture
      under `tests/Fixtures/zoom/recordings/`
- [ ] An early test recording the day before is left behind, a restarted
      meeting comes back as two recordings in order, and a recording stopped
      and restarted inside one instance is one recording (owner acceptance 8:
      no early test, restart or extra segment can silently become the wrong
      replay)
- [ ] Nothing yet, a deleted recording and another host's meeting answer an
      empty list and never an exception; a refused token, a rate limit, a
      server error after two attempts and a timeout answer an `AppException`
      with `upstream` set, which the sweep can log (owner acceptance 9:
      truthful status for an expired or deleted recording)
- [ ] A personal meeting room by name or by ten-digit id, a Teams or Meet
      link, a plain-`http` link and a malformed one are refused by
      `handles()`, and `find()` on any of them is a programmer error that
      sends nothing; no Zoom host or path pattern appears outside
      `ZoomMeetingLink`
- [ ] Only a `completed` MP4 makes a recording; an instance with a share link
      and no completed video yet comes back with `isVideo` false; a
      transcript, a chat file or an audio-only file never becomes one
- [ ] `openUrl()` returns the stored link with the passcode spliced in and
      makes no call; `cloudRecording()` reads the account's setting and never
      throws
- [ ] `ZoomRecordings` is the one object under the `recording-finders` tag,
      `ArchitectureTest` passes unchanged, no test reaches Zoom, and the
      tinker paragraph runs against a fixture
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-122`'s fixtures on disk, and its answers to the questions this draft
  reads — the spike's:
    - question 1: whether the instances body is keyed `meetings` and carries
      `occurrence_id` (case 11 and the `occurrence_id` branch stand or fall on
      it); how far `start_time` drifts from the schedule, for
      `WINDOW_BEFORE_MINUTES` and `WINDOW_AFTER_MINUTES`; and whether a
      restart is two instances with the meeting-id read returning the latest
      (`list_instances.restarted.200.json`, `get_meeting.restarted.200.json`),
      which decides whether the instances read stays unconditional or goes
      back to being the fallback the brief describes;
    - question 2: what a file still processing carries — a `status` other
      than `completed`, or a 404 with a `code` — so case 8 asserts one shape;
    - question 6: the link-shape table for `ZoomMeetingLink::PATTERN` and the
      eleven-digit rule; the `code` a 400 carries for another host's meeting,
      for `NOT_THIS_ACCOUNT_CODES`; what a PMI and a no-fixed-time meeting
      answer;
    - question 9: whether `share_url` is in the REST body, the
      `auto_delete_date` format, and which of `recording_play_passcode` and
      `password` the body carries.
- Whether a link with `?pwd=` opens signed out under "Everyone with the
  recording link" (question 3). If it does not, `openUrl()` has no link a Peer
  can follow and `D-027`'s "share link else play link" needs a third answer
  (`T-122`'s Notes) — the owner's, after the spike.
- Whether the passcode a Peer is shown should be Zoom's human `password`
  rather than the `recording_play_passcode` this draft stores, in which case
  `SessionRecording` and `episode_recordings` need a second value — the
  spike's (question 3), then the owner's.
- `T-141` `ready`, so `ZoomClient::api()`'s retry, `unwrap()`'s signature and
  `Connection::factory()->zoom()` are frozen — the storage owner's.
- Whether `content['meeting_id']` is stored, and by which layer: `D-026`
  names the Zoom folder, the lock rule names a Service, and this draft
  parses on every call and writes nothing — the owner's (a decision).
- Whether `isVideo` false objects serve `T-143` as "keep checking" or should
  be dropped inside `find()` — anyone's, with `T-143`'s writer.
- Where the `source = zoom` arm of Watch is wired: `T-126` (`:599`, `:1028`)
  names this task; this task's dependencies do not include `T-126`, so this
  draft leaves it to `T-143` — anyone's, with `T-126`'s and `T-143`'s
  writers.
- `F08` in the storage review of 20 September 2026
  (`docs/planning/reviews/storage-2026-09-20-findings-codex.md`) does the
  arithmetic on the two-step read above. `T-141`'s `api()` retries a read once,
  so every call is two attempts at the same per-call timeout with a 200 ms delay
  between them, and `find()` normally makes two calls and three when a meeting
  was restarted. At a five-second budget, two timed-out reads alone cost about
  20.4 seconds before any token refresh, and the departure that makes the
  instances read unconditional puts a third call on that sum. `D-034` bounds one
  call and not the caller's whole request, so `find()`'s `$timeoutSeconds` is a
  per-call budget with nothing bounding the whole of it; the review asks for a
  total deadline that the remaining budget is passed through, and the Check-now
  constant `T-143` and `T-144` still spell two ways has to sit inside it — the
  storage owner's, with `T-143` and `T-144`.
  **That file no longer exists and cannot be recovered**, so these bullets are
  the review itself, to be read as the primary source and not as a summary of
  something a reader can go and check; `docs/planning/reviews/README.md` has the
  whole of it.
- No Zoom response fixture exists anywhere in the repository yet; the review of
  20 September 2026 checked and says so plainly. `tests/Fixtures/` holds
  `google/`, `planning/` and `reachability/` and nothing from Zoom, so every
  shape this draft maps — the instances body's key and its `occurrence_id`,
  a recording file's `status`, `share_url` and `play_url`,
  `recording_play_passcode` against `password`, the `auto_delete_date` format
  and the `code` another host's meeting answers with — is a hypothesis taken
  from Zoom's reference, as is `ZoomMeetingLink::MEETING_ID_DIGITS`, which
  encodes a help-centre rule nobody has observed. The questions above are
  where each is answered; this is why none of them is a wording question —
  the spike's.

## Re-scope log

None.

## Notes

Written 18 September 2026 from `D-027`, `D-022` and `D-026`, on `T-141`'s
`ZoomClient` and against `T-122`'s fixture names. The merged sprint reference
is `docs/planning/course-classroom.md`; its "How Qori detects the end and the
recording" section and its vendor facts are where the two-step read, the
double-encoding rule, the completed-file rule and the tier costs come from.

**One departure from the brief, made on purpose.** The brief reads
`GET /past_meetings/{meetingId}/instances` as the fallback when the latest
instance is outside the window; this draft reads it every time, because a
restarted meeting is two instances and the shortcut alone can never return
Part 1 (owner acceptance 8). It costs one MEDIUM-tier call per check and is
the first bullet above.

`T-126`'s draft is edited to: the `source = zoom` arm inside
`PlaybackTicketService::watch()` ("`T-142` routes a zoom row through
`FindsRecordings::openUrl()` here", `:599`, and the Notes line at `:1028`) is
`T-143`'s, the first task that has both the finder and a `zoom` row; this task
builds `openUrl()` and wires it to nothing.

`T-143`'s draft is edited to: take an empty `find()` answer as nothing yet and
back off; attach only `isVideo` objects, and read an `isVideo` false object as
an instance whose video is still processing; hold for review when two or more
objects come back (`D-027`); call `ConnectionService::fresh()` before the
finder (`T-141`'s Notes); resolve the set with
`when()->needs('$finders')->giveTagged('recording-finders')`; and add the
`source = zoom` Watch arm through `openUrl()`, building the `SessionRecording`
from the row's `vendor_ref`, `url`, `passcode`, `started_at`,
`duration_minutes` and `available_until`.

Nothing in `T-141` is edited. Its `ZoomAccountsTest` case 9 already counts
`Http::assertSentCount(3)` for one identity read plus
`ZoomClient::READ_ATTEMPTS` settings tries, because Laravel's `retry($times)`
is the total number of attempts and `retry(2, 200, throw: false)` makes two.
This draft's cases 14 and 18 count two attempts for the same reason, and case
13 counts one because `T-141`'s `retryWhen()` retries a `ConnectionException`
or a 5xx and never a 4xx.

`T-143` and `T-144` spell the Check-now timeout constant differently
(`LiveSessionService::CHECK_TIMEOUT_SECONDS` at `T-143`'s `:603`,
`CHECK_NOW_TIMEOUT_SECONDS` at `T-144`'s `:111`). This task names neither —
`find()` takes the seconds — so the two drafts can settle it between them.

`T-141`'s Notes offer `recording.auto_delete_cmr_days` as a fallback for
`availableUntil`; it is not used here (Decisions), and `T-141` stores it
nowhere, so nothing changes there.

`ZoomMeetingLink::MEETING_ID_DIGITS` encodes a rule from Zoom's help centre —
eleven digits for a scheduled meeting since 2020, ten for a personal meeting
id — that nobody at Qori has observed; it is the cheapest way to honour the
brief's "PMI → null" and `T-122`'s link-shape table replaces it if it is
wrong. `database/seeders/DesignReviewSeeder.php:356` carries `918 2740 5566`
today, the same eleven digits, and `T-123` rewrites that row to
`https://zoom.us/j/91827405566`, so the seeded world is one the finder handles.

This task adds no flow file: the finder is code with no chain through it until
`T-143`, whose flow file is `T-125`'s `docs/flows/live-sessions.md`.
`docs/flows/README.md:42-43` — the Zoom/Teams live-episode integration has no
flow file — is `T-125`'s to rewrite when it creates that file, not this task's,
and `T-143` says the same.
