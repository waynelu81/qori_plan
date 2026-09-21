---
id: T-135
title: A buyer sees the next session before paying, and the creator can copy a message for the chat
stream: classroom
status: draft
owner: unassigned
estimate: S
depends: T-134
blocks: none
---

# T-135 — A buyer sees the next session before paying, and the creator can copy a message for the chat

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 18 September 2026 from
> `D-024`, `D-025`, `D-026` and `D-028`, and the owner's scenarios 2, 11 and
> 14 in `docs/planning/course-classroom.md`.

## Why

The public page lists each Episode's title, type, preview flag and start
(`app/Http/Controllers/PublicSeriesController.php:88-93`) and renders a live
Episode's start through `SessionTime` in the viewer's own zone with no other
zone beside it (`resources/js/pages/public/Series.vue:418-423`). Nothing on
the page says whether a session is recorded — `records` has lived in the live
`content` since `T-123` and reaches the creator's page and the Peer's card
(`T-125`) and never the public one — so a buyer fifteen hours from the creator
has to work out for themselves whether they can be there, and nothing tells
them what happens if they cannot. Someone deciding whether to pay reads the
price and the count of Episodes, and not the one fact a live course turns on.

On the creator's side the only thing that can be copied is the public link
(`resources/js/components/series/ShareLink.vue`, mounted at
`resources/js/pages/share/series/Show.vue:792-796`). A creator announcing a
class in the WhatsApp or WeChat group types the time by hand and pastes the
meeting link — the stale live destination the owner's scenario 14 forbids, and
the one address `D-024` says a copied message must never be minted against.
Free gets no reminder (`D-028`), so on that plan the message in the chat is
the only nudge a Peer gets before a session.

Afterwards the public page carries a "Next live session" block above the buy
controls: the title, the start and end in the viewer's zone with the Group's
zone beside it, and "Recorded — …" or "Live only — …" from the creator's
switch, never a join link (`D-024`); every session row on the page shows both
zones. On the creator's Series page a live row in `upcoming`, `open`, `ready`
or `cancelled` offers **Copy message for your chat**: the session's title, its
time in the Group's zone with the zone named, the line that the reader's own
time is on the Series page, and the `shared.episodes.show` address
(`D-024`, `D-026`).

## Decisions taken to make this specifiable

**The next session is the soonest live Episode still ahead and not cancelled,
chosen on the model, with the clock passed in.**
`Series::nextLiveEpisode(CarbonInterface $now): ?Episode` — the brief's shared
declaration, with no default — takes the live Episodes of `orderedEpisodes()`
(`app/Models/Series.php:131-136`) with a `starts_at` after `$now` and not
`isCancelled()` (`T-123`'s reader, written by `T-134`), and answers the one
with the earliest start — not the lowest position, because a creator may
reorder, and "next" is a question about the clock. `starts_at > $now` is the
rule `T-136`'s access email uses for the same sentence, so both name the same
session; at 9:10 the block moves to the following week's and the rows below
still show today's. A read with nothing to orchestrate goes on the model
("Query on the model or inside a Service", `CLAUDE.md`). The caller passes
the clock — `CarbonImmutable::now()` in `PublicSeriesController::nextSession()`
and in the tinker recipe, and in `T-136` the `$now` its `toMail()` already
holds — the explicit-clock rule `T-125` and `T-136` follow, so nothing on the
model reads the real clock and a test hands in an instant. Null when nothing
is ahead, and then nothing renders.

**The block shows for every viewer, granted or not, because it describes the
Series and not the viewer** — the reasoning `T-092` gives its requirements
list. It sits above the buy controls beside the deletion notice, for the
reason written there: "Above the buttons, not below them. Somebody deciding
whether to pay for this needs the date before they decide"
(`resources/js/pages/public/Series.vue:161-171`).

**`records` becomes one sentence chosen on the server; the switch never
reaches the page.** `live.before_buying.recorded` or
`live.before_buying.live_only`, chosen from `content['records']` in the
controller, so `T-123`'s case 15 (no `records` key on the public Episode
entries) stays true. The sentence states the creator's switch, which is the
one thing Qori knows before the session (`D-026`): "won't be recorded" and
"watch later" are what the switch means, and `T-127`'s `not_recorded` state
is where a promise that turns out otherwise is corrected.

**The time is rendered by `SessionTime.vue` in the browser; no lang line
carries a time.** The prop is the ISO instant, `Intl` gives the viewer's
zone, and `T-125`'s `groupTimezone` prop renders the Group's zone after " · "
when it differs. `T-123`'s `endsAt` renders the range, so the block says how
long the session is without a sentence. The Group's resolved zone is sent once
as `series.timezone` and used by the block and by every row. Owner scenario 2
is asserted at the instant level: a Brisbane 9:00 on 2 November 2026 is
`2026-11-01T23:00:00+00:00`, which London reads as 23:00 GMT on 1 November
and New York as 18:00 EST the same evening, both zones having left summer
time by then; the display is `Intl`'s, and the browser check in Acceptance is
where the two words are read.

**A new `NextSessionNotice.vue`, mounted from the page, with every sentence as
a prop.** `D-024`: each new card is its own component under
`resources/js/components/series/`, so a page edit is a mount. The page's
existing inline sentences (`Series.vue:402`, `:430`, `:116-121`) are §13's
unwired i18n and stay.

**The chat message is minted on the server in `App\Support\SessionChatMessage`,
and the panel only copies it.** Three of its facts are the server's: every
sentence is lang, the time is the Group's zone (a `setTimezone()`, as
`EpisodeController::store()` does at
`app/Http/Controllers/Share/EpisodeController.php:65-67`), and the address is
`route('shared.episodes.show', …)` (`D-024`). A static `for()` in
`app/Support`, on `DeletionDate::for()`'s pattern
(`app/Support/DeletionDate.php`): a private method on `SeriesController` would
be a second place the format lived, and the tinker recipe needs to call it.

**One lang key per state, chosen from `LiveState`; four states have a
message and four have none.** `upcoming` and `open` share
`live.chat_message.upcoming`, because the message states the schedule
("Starts …"), which is as true ten minutes into the session as an hour
before, and `D-026` forbids "live now". `ready` and `cancelled` have their
own. `waiting` and `overdue` have nothing to announce yet; `not_recorded` is a
fact the Peer's card already states and one a creator says better in their
own words; `review` is the creator's alone. In those four the control is
absent, not disabled: nothing to say is not a locked control.

**The message is one lang value per state, its lines separated by `\n`.** A
whole message in one line so a locale can reorder it (`CLAUDE.md`: sentences
are authored whole). The newlines survive `Lang::get()` and
`navigator.clipboard.writeText()`, and WhatsApp and WeChat keep them.

**`:title` is the session's title, `:series_title` the Series' title, `:when`
the start in the Group's zone with the zone named, `:url` the address.**
`strtr()` replaces the longest key first, so `:series_title` never collides
with the `:series` noun — `:series_plural` already relies on the same fact
(`app/Support/Terminology.php:89-97`). No line carries a noun placeholder, so
the lines are read with `__()`; the Series' title is the one word a Group has
already chosen.

**The time format is `SessionChatMessage::FORMAT = 'j M Y, g:ia T'`, the
shape `series.session_scheduled` already says the hour back in.** The same
literal at `EpisodeController.php:67` is left as it is — a file `T-124` and
`T-126` edit, and reading the constant there is a wording-tier change for
whoever next opens it (Notes).

**The panel copies with the clipboard and shows the message in a readonly
textarea on request or on failure**, on `ShareLink.vue`'s pattern (`:30-53`):
`navigator.clipboard` is unavailable on an insecure origin and can be refused,
and a person who cannot copy has to be able to read and select. The textarea
is hidden until **Show the message** is pressed or a copy fails. The control
is not disabled by the over-cap lock, because it writes nothing.

**The message rides in `live.chatMessage` per Episode and its labels once in
`livePanel.chat`; neither page is edited.** The stream's claim order gives
`share/series/Show.vue` to `T-123`, `T-130`, `T-132` and `T-137`, and
`T-127` established that the panel receives the whole `live` object and the
whole `livePanel` copy object so a new key reaches it without a page edit.
`SeriesController::show()` already computes `stateFor()` per live Episode for
`T-127`'s `state`; this task hoists that value and hands it to
`SessionChatMessage::for()`, so the state is computed once.

**Somebody who follows the address signed out meets sign-in, then the
anchor.** `shared.episodes.show` sits behind `auth` (`T-125`), the framework
stores a guest's GET as `url.intended`, and `T-084` keeps a stale one from
another person. Somebody with no access at all meets
`errors.access.not_granted` after signing in — the message is for the class
chat, whose members have access, and the public link has its own panel
(`share-link`); whether the message should carry both is at the bottom.

**Tests go through the two pages' props, not the components**, as `T-125`
and `T-127` test theirs: the controller is where the state, the zone and the
address are decided, and a prop assertion pins each.

## Preconditions

**Data this task verifies against:** a clean database. Every case builds its
own Group with `timezone` set, as `tests/Feature/Series/LiveSessionTest.php:41-60`
does, adds a live Episode through
`EpisodeService::add(…, startsAt:, lengthMinutes:)` (`T-123`), publishes with
`SeriesService::publish()`, and moves the clock with `$this->travelTo()`; a
`ready` row comes from `RecordingService::paste()` (`T-126`), a `cancelled`
one from `LiveSessionService::cancel()` (`T-134`). For the browser check, the
design-review world (`php artisan qori:reset full --force`,
`docs/tinker/design-review.md`): its live clinic starts eleven days ahead
(`database/seeders/DesignReviewSeeder.php:433`), so its public page shows the
block and its creator page offers the message.

**Equipment:** a browser on a secure origin — `localhost` counts — so the
clipboard is available, with its zone changed once (the operating system's
zone, or DevTools → Sensors) to read a Brisbane time as London and New York.
A phone with WhatsApp or WeChat to see the pasted message keep its line
breaks, if one is to hand; a text editor shows the same.

**Spike:** none owed. Nothing here reads a vendor payload; the message carries
a Qori address and never the meeting link.

## Scope

**In:**

- `Series::nextLiveEpisode()`.
- `PublicSeriesController::show()`: `series.timezone` and `nextSession`.
- `NextSessionNotice.vue`, mounted from `public/Series.vue` above the buy
  controls; `group-timezone` on every row's `SessionTime`.
- `App\Support\SessionChatMessage` with `for()` and `FORMAT`.
- `SeriesController::show()`: `live.chatMessage` per live Episode and
  `livePanel.chat`.
- **Copy message for your chat** on `LiveSessionPanel.vue`, with the
  readonly textarea.
- `lang/en/live.php`: `before_buying.*` and `chat_message.*`.
- `docs/flows/series.md`, `docs/flows/live-sessions.md`,
  `docs/tinker/live-sessions.md`.

**Out:**

- `T-092`'s `BuyerRequirements` list and its `identities.requirements.title`
  (`D-021`, part 1); the block here is its own component, and whether it later
  becomes that list's first line is at the bottom.
- The access email's next-session line (`T-136`), which reads the same model
  method.
- A "moved" or "cancelled" email (`D-028`: none this sprint) and the day-before
  reminder (`T-138`); until those land the message here is how a creator tells
  the chat, which `T-124`'s edit form already says.
- The chat card, `series_chats` and `shared.chats.open` (`T-132`); this task
  copies text and stores nothing about a chat.
- Sending anything anywhere: no chat vendor is called (`D-029`), and nothing
  here writes a row.
- A "next session" on the Peer's Series page; every session is a card there
  (`T-125`).
- Cancel, Undo and **Add the next session**, beside which the control sits
  (`T-134`).
- The `recording_ready` re-send (`T-140`); the `ready` message here is a
  copy for the chat, not a notice.

## Files

| Path                                                   | Change | Notes                                                                                    |
| ------------------------------------------------------ | ------ | ---------------------------------------------------------------------------------------- |
| `app/Models/Series.php`                                | edit   | `nextLiveEpisode()`                                                                      |
| `app/Support/SessionChatMessage.php`                   | new    | `for()`, `FORMAT`                                                                        |
| `app/Http/Controllers/PublicSeriesController.php`      | edit   | `series.timezone`, `nextSession`; `nextSession()` private                                |
| `app/Http/Controllers/Share/SeriesController.php`      | edit   | `live.chatMessage` per live Episode; `livePanel.chat`                                    |
| `lang/en/live.php`                                     | edit   | `before_buying.*`, `chat_message.*`                                                      |
| `resources/js/components/series/NextSessionNotice.vue` | new    | the block; copy as props                                                                 |
| `resources/js/pages/public/Series.vue`                 | edit   | mounts the block; `timezone` on `PublicSeries`; `group-timezone` on every row            |
| `resources/js/components/series/LiveSessionPanel.vue`  | edit   | the copy control, the textarea, `chatMessage` on `LiveEpisode`, `chat` on the panel copy |
| `docs/flows/series.md`                                 | edit   | "The public series page": the next-session read and what never travels                   |
| `docs/flows/live-sessions.md`                          | edit   | the chat-message chain, beside the Join chain                                            |
| `docs/tinker/live-sessions.md`                         | edit   | `nextLiveEpisode()` and a message minted by hand                                         |
| `tests/Feature/Series/NextSessionBeforeBuyingTest.php` | new    | 5 cases                                                                                  |
| `tests/Feature/Series/SessionChatMessageTest.php`      | new    | 6 cases                                                                                  |

No route changes, so nothing under `resources/js/routes` moves and
`qori:reachability` is unaffected. No factory or seeder row: the seeder's live
Episode already carries `join_url`, `records` and a start eleven days ahead
(`T-123`). No new flow file: both chains belong to files that exist, so
`docs/flows/README.md` and `docs/tinker/README.md` do not change.

## Database

None.

## Code

```php
// app/Models/Series.php

use Carbon\CarbonInterface;

/**
 * The live Episode a person is about to be told about: the soonest start
 * still ahead, skipping cancelled sessions. Null when nothing is ahead, and
 * then the public page's block and the access email's line render nothing
 * (T-135, T-136).
 *
 * Soonest, not lowest position: a creator may reorder, and "next" is a
 * question about the clock — and the clock is the caller's: no default, so
 * a test hands in an instant and nothing here reads now() (T-125's rule).
 */
public function nextLiveEpisode(CarbonInterface $now): ?Episode;
// return $this->orderedEpisodes()
//     ->filter(fn (Episode $episode): bool => $episode->isLive()
//         && $episode->starts_at !== null
//         && ! $episode->isCancelled()
//         && $episode->starts_at->greaterThan($now))
//     ->sortBy(fn (Episode $episode): int => $episode->starts_at->getTimestamp())
//     ->first();
```

```php
namespace App\Support;

use App\Enums\LiveState;
use App\Models\Episode;
use App\Models\Series;

/**
 * The message a creator pastes into the class chat (D-024, D-026).
 *
 * Minted here and not in the browser because its three facts are the
 * server's: every sentence is lang, the time is the Group's zone, and the
 * address is shared.episodes.show — never the meeting link, so nothing a
 * creator pastes goes stale when a link is corrected (owner scenario 14).
 *
 * One key per state. upcoming and open share a message that states the
 * schedule; waiting, review, overdue and not_recorded have nothing to
 * announce and answer null, and the panel shows no control.
 */
class SessionChatMessage
{
    /** The shape series.session_scheduled already says the hour back in (EpisodeController::store()). */
    public const FORMAT = 'j M Y, g:ia T';

    public static function for(Series $series, Episode $episode, LiveState $state): ?string;
    // $key = match ($state) {
    //     LiveState::Upcoming, LiveState::Open => 'live.chat_message.upcoming',
    //     LiveState::Ready => 'live.chat_message.ready',
    //     LiveState::Cancelled => 'live.chat_message.cancelled',
    //     LiveState::Waiting, LiveState::Review, LiveState::Overdue, LiveState::NotRecorded => null,
    // };
    //
    // if ($key === null || $episode->starts_at === null) {
    //     return null;
    // }
    //
    // return __($key, [
    //     'title' => $episode->title,
    //     'series_title' => $series->title,
    //     'when' => $episode->starts_at
    //         ->setTimezone($series->group?->timezone() ?? Timezones::fallback())
    //         ->format(self::FORMAT),
    //     'url' => route('shared.episodes.show', [
    //         'seriesId' => (string) $series->getKey(),
    //         'episodeId' => (string) $episode->getKey(),
    //     ]),
    // ]);
}
```

```php
// App\Http\Controllers\PublicSeriesController::show() — inside 'series' (:78-94), one more key:
// The Group's zone, resolved, so every session time on the page can show it
// beside the viewer's own (D-026). Never null: timezone() falls back.
'timezone' => $model->group?->timezone() ?? Timezones::fallback(),

// and one more top-level prop, beside 'deletionNotice' (:146-152):
// What a buyer needs before paying for a live course (T-135): the soonest
// session ahead, and whether it is recorded. Null when nothing is ahead. The
// join link never travels (D-024).
'nextSession' => $this->nextSession($model),

/**
 * @return ?array{heading: string, title: string, startsAt: string, endsAt: ?string, line: string}
 */
private function nextSession(Series $series): ?array;
// $next = $series->nextLiveEpisode(CarbonImmutable::now());   // the explicit clock T-125's controller passes; `use Carbon\CarbonImmutable;` joins the imports
//
// if (! $next instanceof Episode) {
//     return null;
// }
//
// return [
//     'heading' => __('live.before_buying.heading'),
//     'title' => $next->title,
//     'startsAt' => (string) $next->starts_at?->toIso8601String(),   // non-null by nextLiveEpisode()'s filter
//     'endsAt' => $next->ends_at?->toIso8601String(),
//     // The creator's switch as a sentence, chosen here so the switch itself
//     // stays off the page (T-123's case 15).
//     'line' => __(($next->content['records'] ?? true) !== false
//         ? 'live.before_buying.recorded'
//         : 'live.before_buying.live_only'),
// ];
```

```php
// App\Http\Controllers\Share\SeriesController::show() — inside the per-Episode
// `live` array T-127 shapes. T-127 computes stateFor() inline for 'state';
// hoist it to $state above the array and read it twice.
'live' => $episode->isLive() ? [
    // ...T-123's, T-126's and T-127's keys, with 'state' => $state->value...
    // The message for the class chat, or null when there is nothing to announce (T-135).
    'chatMessage' => SessionChatMessage::for($series, $episode, $state),
] : null,

// and inside T-127's top-level 'livePanel' prop, one more object. No noun, so __():
'chat' => [
    'button' => __('live.chat_message.button'),
    'show' => __('live.chat_message.show'),
    'hide' => __('live.chat_message.hide'),
    'copied' => __('live.chat_message.copied'),
    'failed' => __('live.chat_message.failed'),
],
```

```ts
// resources/js/components/series/NextSessionNotice.vue
import SessionTime from '@/components/series/SessionTime.vue';

defineProps<{
    /** "Next live session", from lang. */
    heading: string;
    title: string;
    /** ISO 8601 with an offset; the viewer's zone is Intl's business. */
    startsAt: string;
    endsAt: string | null;
    /** The Group's zone, shown after the viewer's when it differs (T-125). */
    groupTimezone: string;
    /** "Recorded — …" or "Live only — …", chosen on the server from the creator's switch. */
    line: string;
}>();
// <section class="bg-card flex flex-col gap-1 rounded-xl border p-4">
//   <p class="text-sm font-medium">{{ heading }}</p>
//   <p class="font-medium">{{ title }}</p>
//   <p class="text-muted-foreground text-sm">
//     <SessionTime :starts-at="startsAt" :ends-at="endsAt ?? undefined" :group-timezone="groupTimezone" />
//   </p>
//   <p class="text-muted-foreground text-sm">{{ line }}</p>
// </section>
// No other English.
```

```ts
// resources/js/pages/public/Series.vue
interface PublicSeries {
    // ...as today (:30-39)...
    /** The Group's resolved zone; every session time shows it beside the viewer's. */
    timezone: string;
}

const props = defineProps<{
    // ...as today (:41-72)...
    /** The soonest live session ahead, or null (T-135). */
    nextSession: {
        heading: string;
        title: string;
        startsAt: string;
        endsAt: string | null;
        line: string;
    } | null;
}>();
// Mounted between the deletion notice (:166-171) and the checkout notice (:178):
//   <NextSessionNotice v-if="nextSession" v-bind="nextSession" :group-timezone="series.timezone" />
// Every row's time (:422) becomes
//   <SessionTime :starts-at="episode.startsAt!" :group-timezone="series.timezone" />
```

```ts
// resources/js/components/series/LiveSessionPanel.vue — T-123's row type gains one
// key; T-127's panel copy gains one object; the row gains one control.
import { Check, Copy, X } from '@lucide/vue';

export interface LiveEpisode {
    // ...T-123's, T-124's, T-126's and T-127's keys...
    /** Minted on the server; null when there is nothing to announce, and then no control renders. */
    chatMessage: string | null;
}

interface LivePanelCopy {
    // ...T-127's keys...
    chat: {
        button: string;
        show: string;
        hide: string;
        copied: string;
        failed: string;
    };
}

type CopyResult = 'idle' | 'copied' | 'failed';
const chatResult = ref<CopyResult>('idle');
const chatShown = ref(false);
let chatTimer: ReturnType<typeof setTimeout> | undefined;

/** ShareLink.vue:35-53, with the message; a failure also reveals the textarea. */
async function copyChatMessage(): Promise<void>;
// if (!props.episode?.chatMessage) return;
// clearTimeout(chatTimer);
// try { await navigator.clipboard.writeText(props.episode.chatMessage); chatResult.value = 'copied'; }
// catch { chatResult.value = 'failed'; chatShown.value = true; }
// chatTimer = setTimeout(() => (chatResult.value = 'idle'), 2500);
```

In `row` mode, whenever `episode.chatMessage` is a string, the panel renders
under the state's own controls (`T-127`'s table; beside **Undo** in
`cancelled`, `T-134`): a `<Button type="button" variant="outline" size="sm" @click="copyChatMessage">`
carrying `Check`, `X` or `Copy` by `chatResult` and `livePanel.chat.button`;
a `<button type="button" class="underline underline-offset-4 text-sm">`
toggling `chatShown` and labelled `livePanel.chat.show` or
`livePanel.chat.hide`; a `<p class="text-muted-foreground text-sm" aria-live="polite">`
holding `livePanel.chat.copied` or `livePanel.chat.failed` while `chatResult`
is not `idle`; and, when `chatShown`,
`<textarea readonly rows="4" :value="episode.chatMessage" :aria-label="livePanel.chat.button" class="…font-mono text-xs" @focus="(e) => (e.target as HTMLTextAreaElement).select()">`.
Nothing here is disabled by `lock.active`. No other English.

`docs/flows/series.md`, "The public series page" (`:133-179`): the read
`PublicSeriesController::show() → Series::nextLiveEpisode()` and the
`nextSession` prop; `series.timezone` beside every time; `records` reaching
the page as a sentence; the join link, a recording, a material and the chat
never reaching it (`D-024`). `docs/flows/live-sessions.md`: beside `T-125`'s
Join chain, "Copy message for your chat":
`SeriesController::show() → LiveSessionService::stateFor() → SessionChatMessage::for()`,
the four states that have a message, the address being
`shared.episodes.show`, and that the browser copies and the server sends
nothing. `docs/tinker/live-sessions.md`:
`$series->nextLiveEpisode(Carbon\CarbonImmutable::now())` — the argument is
the clock, so any instant may stand in for `now()` — then
`App\Support\SessionChatMessage::for($series, $episode, app(App\Services\LiveSessionService::class)->stateFor($episode, Carbon\CarbonImmutable::now()))`
inside the recipe's existing `CurrentGroup::runFor()`, and the message
printed with its line breaks.

## Copy

| Key                            | File               | English                                                                                                 |
| ------------------------------ | ------------------ | ------------------------------------------------------------------------------------------------------- |
| `live.before_buying.heading`   | `lang/en/live.php` | Next live session                                                                                       |
| `live.before_buying.recorded`  | `lang/en/live.php` | Recorded — watch later if you can't attend.                                                             |
| `live.before_buying.live_only` | `lang/en/live.php` | Live only — this session won't be recorded.                                                             |
| `live.chat_message.upcoming`   | `lang/en/live.php` | :title\nStarts :when.\nJoin from the :series_title page, where the time is shown in your own zone: :url |
| `live.chat_message.ready`      | `lang/en/live.php` | :title — the recording is ready.\nWatch it on the :series_title page: :url                              |
| `live.chat_message.cancelled`  | `lang/en/live.php` | Cancelled: :title (:when).\nThe :series_title page is here: :url                                        |
| `live.chat_message.button`     | `lang/en/live.php` | Copy message for your chat                                                                              |
| `live.chat_message.show`       | `lang/en/live.php` | Show the message                                                                                        |
| `live.chat_message.hide`       | `lang/en/live.php` | Hide the message                                                                                        |
| `live.chat_message.copied`     | `lang/en/live.php` | Message copied. Paste it into your chat.                                                                |
| `live.chat_message.failed`     | `lang/en/live.php` | Couldn't copy it. Select the message below and copy it yourself.                                        |

The three `chat_message` messages are double-quoted PHP strings and `\n` is a
real newline; `:when` is `SessionChatMessage::FORMAT` in the Group's zone
("1 Oct 2026, 9:00am AEST"), `:url` the `shared.episodes.show` address. Every
line is read with `__()`: none carries a noun placeholder, so none goes
through `Terminology::line()`, and none puts "a" or "an" before one. No line
under `live.*` says "live now", "has ended", "on its way" or "processing"
(`D-026`); `live_only` and `recorded` state the creator's switch, which is
what Qori knows before the session. No vendor is named (`D-025`), and no
number appears. `live.before_buying.*` and `live.chat_message.*` are new
groups in `T-125`'s file, beside the groups `T-125` creates (`state`, `join`,
`records`, `timezone`) and those the tasks between it and this one add.

## Routes

None. The message carries `shared.episodes.show` (`T-125`) and the block sits
on `series.public` (`routes/web.php:66-67`); both exist.

## Tests

**New: `tests/Feature/Series/NextSessionBeforeBuyingTest.php` — 5 cases**
(a `scene()` as `tests/Feature/Series/LiveSessionTest.php:41-60` with
`Australia/Brisbane`; `live(Series $series, CarbonImmutable $startsAt, bool $records = true): Episode`
through
`EpisodeService::add($series, $title, EpisodeType::Live, EpisodeProvider::Zoom, content: ['join_url' => 'https://zoom.us/j/91827405566', 'records' => $records], startsAt: $startsAt, lengthMinutes: 60)`
— the brief's placeholder meeting id, so a case asserting that the link never
travels has a link to miss; `SeriesService::publish()`; the page from
`route('series.public', ['group' => $group->slug, 'series' => $series->slug])`.
The clock: `EpisodeService::add()` refuses a past start on create (`T-123`),
so every case runs `$this->travelTo(CarbonImmutable::parse('2026-09-15T00:00:00Z'))`
before its `add()` calls and only then travels forward to the instant it
names; a "past" session is one added under the pinned clock and left behind,
and nothing relies on the real clock.)

1. `test_it_shows_the_next_live_session_before_buying` — sessions at 1
   October and 2 November 2026, 09:00 Brisbane, then `travelTo` 15 October
   2026: `nextSession.title` is the November session's, `.startsAt` is
   `2026-11-01T23:00:00+00:00`, `.endsAt` is `2026-11-02T00:00:00+00:00`,
   `.heading` is `Next live session`, `.line` is the recorded sentence, and
   `series.timezone` is `Australia/Brisbane` (owner scenario 2 at the instant
   level: London reads it 23:00 GMT on 1 November, New York 18:00 EST).
2. `test_it_names_the_soonest_session_ahead_and_skips_a_cancelled_one` — the
   later session added first, so it holds position 1: `nextSession.title` is
   the sooner one's; the sooner cancelled through
   `LiveSessionService::cancel()` (`T-134`): the later one is `nextSession`;
   both cancelled: `nextSession` is null.
3. `test_it_says_live_only_when_the_switch_is_off` — `records` false:
   `nextSession.line` is the live-only sentence; `nextSession` and
   `series.episodes.0` both `missing` a `records` key.
4. `test_it_shows_nothing_when_no_session_is_ahead` — a Series of File
   Episodes, and one whose only live session is past: `nextSession` is null
   on both, and `series.timezone` is still set.
5. `test_it_never_carries_the_join_link` — signed out, and signed in as a
   Peer with access: `assertDontSee('zoom.us/j/')` on the response (the
   helper's link), `nextSession` `missing('joinUrl')`, `series.episodes.0`
   `missing('live')` (owner scenario 11).

**New: `tests/Feature/Series/SessionChatMessageTest.php` — 6 cases**
(a Melbourne scene built the same way — `scene()` with `Australia/Melbourne`,
the same `live()` helper with its `zoom.us` link, and the same pinned clock
before every `add()`; the creator's page through
`route('share.series.show', …)` as `tests/Feature/Series/ShareLinkTest.php:54-60`;
the message read from `series.episodes.0.live.chatMessage`)

1. `test_it_mints_the_upcoming_message_in_the_groups_zone` — a session at
   `2026-10-01T09:00` Melbourne, stored 23:00 UTC on 30 September (Melbourne
   is on AEST until 4 October 2026): the message is the `upcoming` line with
   the title, `1 Oct 2026, 9:00am AEST`, the Series title and the address,
   newlines included; `livePanel.chat.button` is `Copy message for your chat`.
2. `test_it_mints_the_ready_message_once_a_recording_is_published` — a past
   session, `RecordingService::paste()` (`T-126`): the `ready` line with the
   address.
3. `test_it_mints_the_cancelled_message_for_a_cancelled_session` —
   `LiveSessionService::cancel()` (`T-134`): the `cancelled` line with
   `:when` filled.
4. `test_it_gives_only_four_states_a_message` — `SessionChatMessage::for()`
   called once per `LiveState` case: `Upcoming` and `Open` give the
   `upcoming` line, `Ready` and `Cancelled` theirs, and `Waiting`, `Review`,
   `Overdue` and `NotRecorded` give null; on the page, `travelTo` ten minutes
   after the start (`open`) still reads the `upcoming` message, and a session
   in `waiting` carries `chatMessage` null.
5. `test_it_carries_the_qori_address_and_never_the_join_link` — the message
   contains `route('shared.episodes.show', [...])` and not `zoom.us` (the
   helper's link); a Peer with access who `GET`s that address is redirected
   to `route('shared.show', $series->getKey()).'#episode-'.$episode->getKey()`
   (`T-125`'s anchor) — the address that is shown is the address that
   resolves (`ShareLinkTest.php:85-104`'s reason; owner scenario 14).
6. `test_it_gives_a_file_episode_no_message` — `series.episodes.0.live` is
   null and nothing on the page is named `chatMessage`.

**Changed:** none. `tests/Feature/PublicSeriesTest.php` asserts by key and
gains two props it does not name; `T-123`'s case 15 and `T-125`'s case 17
assert the public Episode entries, which are unchanged, and stay green.

## Acceptance

- [ ] The public page of a published Series with a live session ahead shows
      "Next live session" above the buy controls — the title, the start and
      end in the viewer's zone with the Group's zone beside it when it
      differs, and "Recorded — …" or "Live only — …" — and a Series with none
      ahead shows nothing there
- [ ] Every session row on the public page shows the Group's zone beside the
      viewer's own
- [ ] A Brisbane creator's 9:00 on 2 November 2026 reads 23:00 GMT on 1
      November in a browser set to London and 18:00 EST on 1 November in one
      set to New York (owner scenario 2)
- [ ] Nothing on the public page carries a join link, signed out or signed in
      (owner scenario 11)
- [ ] On the creator's Series page a live row in `upcoming`, `open`, `ready`
      or `cancelled` offers Copy message for your chat; pressing it puts the
      message on the clipboard and says so; pasted into a chat or an editor
      the message keeps its line breaks; a row in `waiting`, `overdue` or
      `not_recorded` offers nothing
- [ ] The message names the session, its start in the Group's zone with the
      zone named, the Series page, and a `/shared/{seriesId}/episodes/{episodeId}`
      address, and never a meeting link (owner scenario 14)
- [ ] A Peer with access who follows the address lands on the Series page at
      that Episode; where the clipboard is refused the creator can read and
      select the message
- [ ] `docs/flows/series.md` and `docs/flows/live-sessions.md` describe the
      two reads, and `docs/tinker/live-sessions.md` mints a message by hand
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-134` `ready` and landed, so `LiveSessionService::cancel()`'s signature,
  the writer of `content['cancelled_at']` and the `cancelled` row of the
  panel (where this control sits beside **Undo**) are frozen. `T-134`'s
  draft declares `cancel(Series $series, string $episodeId): Episode`; this
  draft uses it as read, and the bullet closes when `T-134` is `ready` —
  anyone's.
- Whether the block later becomes the first line of `T-092`'s
  `BuyerRequirements` list (`D-021`, part 1) or stays its own block above it
  — the storage stream owner's, with `T-092`; noted, not blocking: the block
  is a component, and moving it is a mount.
- Whether the message should also carry the public link (`series.public`)
  for someone in the chat who has not got access yet — the owner's; this
  draft says no, because `D-024` mints every copied message against
  `shared.episodes.show` and the public link has its own panel; not
  blocking.
- How `T-127`'s `LiveSessionPanel.vue` takes its row and its copy: the whole
  `live` object and the whole `livePanel` object (`T-127`'s decision, and
  this draft's assumption, so neither page changes) — anyone's; if either
  arrives field by field, the one line on `share/series/Show.vue` is a
  departure under **Added during execution**, made only while `T-130`,
  `T-132` and `T-137` are not `doing` on the page.

## Re-scope log

None.

## Notes

Written on 18 September 2026 from `D-024` (the per-Episode address and what
the public page never carries), `D-025` (the pasted link never travels and no
vendor is named), `D-026` (the state and the copy rule) and `D-028` (Free
gets no reminder, so the chat is the nudge); the owner's scenarios 2, 11 and
14 are folded into Acceptance.

`T-136`'s draft must be edited — an implied draft edit, not yet made. As
written it declares a private `nextSession(CarbonImmutable $now): ?Episode` on
`SeriesAccessNotification` that filters `orderedEpisodes()` itself, and its
Files table does not list the model. The edit: drop that method, call
`$this->series->nextLiveEpisode($now)` with the `CarbonImmutable::now()` its
`toMail()` already holds, and list `app/Models/Series.php` as `edit`. Until it
is made the same read is declared twice in two spellings, and the brief's
shared declaration — `nextLiveEpisode(CarbonInterface $now): ?Episode`, as the
Code section here has it — is the one both follow. Either task may land
first: whichever of `T-135` and `T-136` lands first declares the method on
`app/Models/Series.php`, and the other's row becomes a no-op, said so in its
report.

`T-124`'s edit form tells a creator that no email goes when a session moves
and to tell the chat (`series.live.edit.no_email`); once this task lands the
control it points at exists on the same row. Nothing here changes `T-124`.

`EpisodeController::store()` formats the scheduled hour with the literal
`'j M Y, g:ia T'` (`app/Http/Controllers/Share/EpisodeController.php:67`),
which `SessionChatMessage::FORMAT` now also holds. Reading the constant there
is a wording-tier change for whoever next edits that file; this task's Files
table leaves it alone because `T-124` and `T-126` edit it and nothing here
needs to.

`SessionTime.vue` prints the Group's zone only when it differs from the
display zone (`T-125`), so a viewer in the Group's own zone sees one time and
not the same time twice. The public page has shown a live Episode's start in
the reader's zone since `T-029`; this task adds the second zone and the
recorded line to the rows and nothing else.

The design-review seeder's live clinic (`DesignReviewSeeder.php:433`) starts
eleven days ahead, so `php artisan qori:reset full --force` gives the browser
check a public page with the block and a creator page with the message,
without adding a seeder row.
