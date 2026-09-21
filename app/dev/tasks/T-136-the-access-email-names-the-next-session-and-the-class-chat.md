---
id: T-136
title: The access email names the next session and the class chat
stream: classroom
status: ready
owner: unassigned
estimate: S
depends: T-128, T-132
blocks: none
---

# T-136 — The access email names the next session and the class chat

> **Draft.** Written on 18 September 2026 from `D-028`, `D-029`, `D-024` and
> the classroom brief; not to be started — see
> [`../PROCESS.md`](../PROCESS.md). It waits on `T-128`, whose
> `App\Support\ZonedTime` writes every date, and on `T-132`, whose chat rows
> it reads; what has to happen before it can be marked `ready` is listed at
> the bottom.

## Why

The "You're in" email is the first thing a Peer reads after getting access,
and it says who gave them access, whether they paid, and where the Series is
(`app/Notifications/SeriesAccessNotification.php:47-64`): a subject, a
greeting, an intro naming the creator, a paid-or-free line, the "Start the
series" button to `/shared/{seriesId}` and an outro
(`lang/en/accesses.php:21-29`). For a course taught live it leaves out the two
things a Peer needs first: when the next class is, and where the class talks.
After `T-125` the Series page carries each live Episode's card with its time
in the Peer's zone, and after `T-132` the chat invite sits on the same page
behind access — but nothing tells the Peer that, and a Peer fifteen hours from
the creator who reads the email on a phone has to open the page to learn
whether the class is tonight or tomorrow (`docs/planning/course-classroom.md`).

`D-028` fixes how a date is written in mail — the recipient's `users.timezone`,
else the Group's, the zone named, the Group's zone beside it when different —
and `T-128` states that rule once in `App\Support\ZonedTime`. `D-029` fixes
where an email may point for the chat: the Series page, never the invite
itself, so a replaced link strands nobody. `D-024` fixes the Peer's one
destination as that page.

Afterwards the same email, sent from the same place (`AccessService::grant()`
→ `announce()`, `app/Services/AccessService.php:115-118`), carries up to two
more lines between the paid-or-free line and the button: the next live
Episode ahead, with its start in the Peer's own zone and the Group's zone
beside it, and — when the Series holds a chat invite that has not expired — a
line saying the class chat is on the Series page. A Series with no live
Episode ahead and no chat sends exactly today's message.

## Decisions taken to make this specifiable

**The notification reads the rows; `grant()` passes nothing new.**
`SeriesAccessNotification`'s constructor stays `(Access, Series, string $creator)`
(`app/Notifications/SeriesAccessNotification.php:28-32`), and `toMail()` reads
`$this->series->nextLiveEpisode($now)` (`T-135`'s method on
`app/Models/Series.php`, over `orderedEpisodes()`, `:131-136`) and the
Series' chat rows itself. `AccessService::grant()` is `T-091`'s to edit, and
the brief says this task never touches it; the fallback of ordering this task
after `T-091` so the next session could be passed in from `grant()` is not
needed, because nothing is passed in.

**"Next" is `Series::nextLiveEpisode()`, declared once by `T-135` and
reused here.** The rule — among the Series' live Episodes with a `starts_at`
after now and no `cancelled_at` (`Episode::isCancelled()`, `T-123`), the one
with the earliest `starts_at`, not the first live row by position; a tie
falls to the lower position, because `orderedEpisodes()` is already in
position order and `sortBy()` is stable — lives on the model, where `T-135`'s
public page reads it for the same sentence, so both name the same session.
This task declares no filter of its own: whichever of `T-135` and this task
lands first writes the method on `app/Models/Series.php`, and the other's
Files row is a no-op. A creator who adds a make-up class out of order still
gets the right one named. A session already under way — `starts_at` at or
before now — is not named: the line says "starts", which would be false, and
the button lands on the page where Join is.

**The chat line goes only for an invite that is current, and
`SeriesChat::isExpired()` is the one place that says what current is.** A
`series_chats` row for the Series that `isExpired($now)` (`T-132`: expired
from the first midnight after `expires_on` in the Group's zone; never for a
null `expires_on`) does not call expired. This task restates none of that
rule in SQL or otherwise: the rows are read with `forGroup()` and the method
is asked, so the page and the email cannot drift apart. `D-029` hides the
code on the card after `expires_on` and tells the creator to replace it, so
pointing a Peer at an expired code is a promise the page cannot keep; the
replacement appears on the page without another email, which is why the line
names the page and not the invite.

**Dates follow `T-128`'s zone rule and its helper.**
`ZonedTime::zoneFor($notifiable, $group)` — the recipient's raw
`users.timezone`, else `Group::timezone()` (`app/Models/Group.php:221-232`),
never `User::timezone()`'s UTC fallback (`app/Models/User.php:84-89`) — and
`ZonedTime::describe($startsAt, $zone, $group->timezone())`, which names the
zone and adds the Group's when the identifiers differ. This task restates none
of it and writes no format of its own; `T-128` is in `depends:` so the helper
exists before this is claimed.

**Each line links to the anchor its decision names, and the button is
unchanged.** The next-session line's title is a markdown link to
`route('shared.episodes.show', [$seriesId, $episodeId])` — `D-024`: every
email is minted against that route so a page of its own can replace the 302
later without breaking a link already sent; `T-125` mints it. The chat line's
"page" is a markdown link to `route('shared.show', $seriesId).'#chat'` —
`D-029`: emails point at the Series page's `#chat`, never at the invite. A
markdown link and not a bare URL, because Laravel's mail markdown registers
only the CommonMark core and table extensions
(`vendor/laravel/framework/src/Illuminate/Mail/Markdown.php:197-198`), so a
bare URL is not a link in the HTML part; the text part renders the same
`{{ $line }}`
(`vendor/laravel/framework/src/Illuminate/Notifications/resources/views/email.blade.php:14-17`)
through the text components, so the line arrives verbatim there, URL
included. The URL is a `:url` placeholder in the lang line, never a fragment
joined on. "Start the series" still goes to the Series page
(`app/Notifications/SeriesAccessNotification.php:62`), where the card
(`T-125`) and the chat card (`T-132`) are, because `D-024` fixes the Peer's
one destination as that page and the two lines are the pointers inside it.

**The two lines sit between the paid-or-free line and the button.** So the
order reads: who gave access, what was paid, what is next, where the chat is,
then the button. `MailMessage::line()` before `action()` appends to
`introLines` (`vendor/laravel/framework/src/Illuminate/Notifications/Messages/SimpleMessage.php:218`),
which is what the existing test reads
(`tests/Feature/Access/AccessServiceTest.php:275`), so the new tests assert
the body with the same `implode(' ', $mail->introLines)`.

**Both new lines go through `Terminology::line($key, $replace, $group)` with
the Group passed explicitly** (`app/Support/Terminology.php:89-97`), because a
notification cannot rely on a current Group. `next_session` names the noun
(`:episode`), so a Group that calls its Episodes "Classes" reads "Your next
Class"; `:title` is the title the line is about — the Episode's in
`next_session`, the Series' in `chat` — the brief's rule for a title, and
never a noun placeholder (`T-128`'s `:series_title` is for a line that
carries both titles at once, which neither line here does). The
existing lines keep `__()` and their `:series`-is-the-title replacement
(`app/Notifications/SeriesAccessNotification.php:49-53`); converting them is
`T-005`'s, and the brief says so.

**No vendor name and no join link reach the email.** `D-025` allows the
meeting vendor's name on Join and Watch and the chat platforms' names in the
picker and on the card; an email needs neither. The line says "class chat",
not WhatsApp or WeChat, and the next-session line carries the title and the
time, never `content['join_url']`, a recording or a passcode.

**The clock is `CarbonImmutable::now()` inside `toMail()`, and tests move it
with `travelTo()`.** The constructor cannot take a clock without changing
`grant()`'s call. `Date::use(CarbonImmutable::class)`
(`app/Providers/AppServiceProvider.php:102`) already makes `starts_at`
immutable.

**Subject unchanged; `Queueable` stays; nothing is `ShouldQueue`.** The
subject already names the Series. The trait is on the class today and
`tests/Feature/ArchitectureTest.php:123-130` checks only `ShouldQueue`.

**A new test file under `tests/Feature/Mail/`.** `MailContentTest` is about
`App\Support\MailContent` and deliberately touches no rows;
`AccessServiceTest` is about the service's writes. What the message says is
its own file, `SeriesAccessMailTest.php`, beside `T-128`'s
`RecordingReadyTest.php`.

**`qori:mail:check` is not extended here.** Its scratch Series holds one File
Episode (`app/Console/Commands/MailCheckCommand.php:194-201`), so neither new
line renders in the check; `T-128` gives that Series a zoned Group and a live
Episode. Whether the next-session line then renders depends on that Episode's
start being ahead of the run, and nothing here depends on it.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests
build their own rows: a Group with an owner and a `timezone`, the way
`tests/Feature/Series/LiveSessionTest.php:41-60` builds one but on the
factory's default `free` plan (`database/factories/GroupFactory.php:26`, not
that helper's `'plan' => 'start'`), because nothing here reads a plan limit
and case 11's entitlement is set on `qori.plans.free`, which is what
`Group::allows()` reads for a `free` Group (`app/Models/Group.php:156-159`);
a Series through
`Series::factory()`; live Episodes through `$series->episodes()->create([...])`
with `type`, `provider`, `content` (`join_url`, `records`), `starts_at`,
`ends_at` and `position`, because there is no `EpisodeFactory`; an Access
through `Access::factory()->forSeries($series)->forUser($user)`; and a chat row
through `SeriesChat::query()->create([...])` with `group_id` set explicitly,
because a test that constructs the notification by hand runs in no Group.

**Equipment:** none. Reading the rendered message in an inbox is optional and
needs Docker's Mailpit and `php artisan qori:mail:check`
(`docs/tinker/mail.md`), with the caveat in the last decision above.

**Spike:** none owed; no vendor is called.

## Scope

**In:**

- `SeriesAccessNotification::toMail()`: the next-session line and the chat
  line, each conditional, each through `Terminology::line()`, each a markdown
  link to its anchor (`shared.episodes.show`; `shared.show` + `#chat`); the
  private `hasCurrentChat()` that decides the second, and
  `Series::nextLiveEpisode()` reused for the first.
- `Series::nextLiveEpisode()` on `app/Models/Series.php`, only if `T-135` has
  not landed it first.
- `accesses.mail.next_session` and `accesses.mail.chat` in
  `lang/en/accesses.php`.
- `tests/Feature/Mail/SeriesAccessMailTest.php`, including the owner's
  scenario 2 in `docs/planning/course-classroom.md` — a Brisbane creator, a
  London Peer and a New York Peer across 1 November 2026 — as rendered-line
  assertions.

**Out:**

- `AccessService::grant()` and `announce()`: untouched, and `T-091`'s to edit.
- The rest of this email's vocabulary — `:series` and `:creator` as titles,
  `__()` on the existing lines, the subject — `T-005`.
- `App\Support\ZonedTime` and `live.mail.when` / `live.mail.when_both`:
  `T-128`'s, used here.
- A materials line or a homework due date in this email; `T-128`'s recording
  email carries those for one Episode.
- `recording_ready`, `day_before` and `session_cancelled` notices: `T-128`,
  `T-138`.
- A changed button: "Start the series" still goes to the Series page.
- The chat platform's name, the code image or the invite link in the email
  (`D-029`).
- The buyer's before-paying schedule and the creator's copyable chat message:
  `T-135`.
- `qori:mail:check`'s scratch data: `T-128`.
- `docs/flows/accesses.md`, `docs/tinker/accesses.md` and
  `docs/tinker/mail.md`: the chain, the recipe and the check's output are
  unchanged.

## Files

| Path                                             | Change | Notes                                                                   |
| ------------------------------------------------ | ------ | ----------------------------------------------------------------------- |
| `app/Notifications/SeriesAccessNotification.php` | edit   | two conditional lines, each linked; `hasCurrentChat()`                  |
| `app/Models/Series.php`                          | edit   | `nextLiveEpisode()` — `T-135`'s declaration; a no-op if it landed first |
| `lang/en/accesses.php`                           | edit   | `mail.next_session`, `mail.chat`                                        |
| `tests/Feature/Mail/SeriesAccessMailTest.php`    | new    | 14 cases                                                                |

Flows: none — the call chain is unchanged: `AccessService::grant()` sends the
same notification from the same place (`docs/flows/accesses.md`, "Grantling"),
and only what the message says changes. No route changes, no config value, no
column, no factory and no seeder: the lines read rows `T-123`, `T-125` and
`T-132` create, link to routes `T-125` and `routes/shared.php:38` already
declare, and the format they need is `T-128`'s. No tinker recipe drives this
message by hand — `docs/tinker/mail.md` sends it through `qori:mail:check`,
whose output line for it ("You're in: Mail Check Series .. ok") is unchanged.

## Database

None.

## Code

```php
namespace App\Notifications;

use App\Models\Access;
use App\Models\Episode;
use App\Models\Series;
use App\Models\SeriesChat;
use App\Models\User;
use App\Support\Terminology;
use App\Support\ZonedTime;
use Carbon\CarbonImmutable;
use Illuminate\Bus\Queueable;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

/**
 * "You're in" — receipt and access, and since T-136 the next class and the
 * chat. Reads the Series' rows itself so AccessService::grant() passes
 * nothing new; the two lines appear only when there is something to say.
 */
class SeriesAccessNotification extends Notification
{
    use Queueable;

    // Unchanged: AccessService::announce() (app/Services/AccessService.php:115-118) constructs it exactly so.
    public function __construct(
        private Access $access,
        private Series $series,
        private string $creator,
    ) {}

    public function toMail(User $notifiable): MailMessage;
    // $now = CarbonImmutable::now();
    // $group = $this->series->group;
    // $terminology = app(Terminology::class);
    // $replace = ['series' => $this->series->title, 'creator' => $this->creator, 'name' => $notifiable->name];   // today's :49-53; T-005's to change
    //
    // $mail = (new MailMessage)
    //     ->subject(__('accesses.mail.subject', $replace))
    //     ->greeting(__('accesses.mail.greeting', $replace))
    //     ->line(__('accesses.mail.intro', $replace))
    //     ->line($this->access->wasPaid() ? __('accesses.mail.paid') : __('accesses.mail.free'));   // today's :55-61
    //
    // $next = $this->series->nextLiveEpisode($now);                                      // T-135's method, declared below
    //
    // if ($next instanceof Episode) {
    //     $mail->line($terminology->line('accesses.mail.next_session', [
    //         'title' => $next->title,
    //         'url' => route('shared.episodes.show', [$this->series->getKey(), $next->getKey()]),   // T-125's route (D-024)
    //         'when' => ZonedTime::describe($next->starts_at, ZonedTime::zoneFor($notifiable, $group), $group->timezone()),
    //     ], $group));
    // }
    //
    // if ($this->hasCurrentChat($now)) {
    //     $mail->line($terminology->line('accesses.mail.chat', [
    //         'title' => $this->series->title,
    //         'url' => route('shared.show', $this->series->getKey()).'#chat',                   // routes/shared.php:38; the anchor is T-132's (D-029)
    //     ], $group));
    // }
    //
    // return $mail
    //     ->action(__('accesses.mail.action'), url('/shared/'.$this->series->getKey()))   // today's :62
    //     ->line(__('accesses.mail.outro'));                                              // today's :63

    /**
     * A chat invite the page will still show (D-029): a series_chats row for
     * this Series that SeriesChat::isExpired() (T-132) does not call expired.
     * The rows are loaded and the model asked, so the expiry rule lives in one
     * place; qori.chats.per_series is 1, so this is at most one row.
     * forGroup(), because a notification runs in no Group.
     */
    private function hasCurrentChat(CarbonImmutable $now): bool;
    // return SeriesChat::query()
    //     ->forGroup($this->series->group)                                                 // app/Concerns/BelongsToGroup.php:52-57
    //     ->where('series_id', $this->series->getKey())
    //     ->get()
    //     ->contains(fn (SeriesChat $chat): bool => ! $chat->isExpired($now));
}
```

```php
// app/Models/Series.php — T-135's declaration, written by whichever of T-135
// and this task lands first; the other finds it and its Files row is a no-op.

use Carbon\CarbonImmutable;

/**
 * The live Episode a person is about to be told about: the soonest start
 * still ahead, skipping cancelled sessions. Null when nothing is ahead, and
 * then the public page's block and the access email's line render nothing
 * (T-135, T-136).
 *
 * Soonest, not lowest position: a creator may reorder, and "next" is a
 * question about the clock.
 */
public function nextLiveEpisode(?CarbonImmutable $now = null): ?Episode;
// $now ??= CarbonImmutable::now();
//
// return $this->orderedEpisodes()
//     ->filter(fn (Episode $episode): bool => $episode->isLive()
//         && $episode->starts_at !== null
//         && ! $episode->isCancelled()
//         && $episode->starts_at->greaterThan($now))
//     ->sortBy(fn (Episode $episode): int => $episode->starts_at->getTimestamp())
//     ->first();
```

```php
// lang/en/accesses.php — inside 'mail' (:21-29), after 'free'.
//
// Two lines that appear only when there is something to say, read through
// Terminology::line() with the Group passed in — unlike their siblings, which
// T-005 converts. :episode is the Group's noun; :title the title the line is
// about (the Episode's, then the Series'); :url the anchor the line links to
// (shared.episodes.show, then shared.show#chat), as a markdown link because
// a bare URL is not one in Laravel's mail markdown; :when is
// ZonedTime::describe()'s fragment (T-128), which names the zone and the
// Group's zone beside it when different.
'next_session' => 'Your next :episode, [:title](:url), starts :when.',
'chat' => 'Join the class chat from the [:title page](:url).',
```

Names this task relies on and does not declare: `Episode::isCancelled()` and
`episodes.ends_at` (`T-123`); `App\Models\SeriesChat` with `BelongsToGroup`,
`series_id`, `platform`, `expires_on` cast `immutable_date` and
`SeriesChat::isExpired(CarbonImmutable $now): bool` (`T-132`, `D-029`);
`GET /shared/{seriesId}/episodes/{episodeId}` `shared.episodes.show` and the
`#chat` anchor on the Peer's Series page (`T-125`, `T-132`); `shared.show`
(`routes/shared.php:38`); `App\Support\ZonedTime::zoneFor(User, Group): string`
and
`ZonedTime::describe(CarbonInterface $at, string $zone, string $groupZone): string`
with `live.mail.when` and `live.mail.when_both` (`T-128`).
`Series::nextLiveEpisode()` is `T-135`'s declaration, reproduced above so both
tasks write the same one.

## Copy

| Key                          | File                   | English                                           |
| ---------------------------- | ---------------------- | ------------------------------------------------- |
| `accesses.mail.next_session` | `lang/en/accesses.php` | Your next :episode, [:title](:url), starts :when. |
| `accesses.mail.chat`         | `lang/en/accesses.php` | Join the class chat from the [:title page](:url). |

Both are read through `Terminology::line()` with the Series' Group, so
`:episode` is that Group's word. `[…](:url)` is a markdown link, filled with
`shared.episodes.show` for the Episode and `shared.show` + `#chat` for the
Series (`D-024`, `D-029`); the URL is interpolated, never written in lang.
Neither line is under `live.*`, and neither uses a word `D-026` forbids;
neither carries a number, a vendor name or an article before a noun
placeholder (`tests/Feature/TerminologyTest.php:218`). The zone name, the
Group's zone and the time format are `T-128`'s `live.mail.when` and
`live.mail.when_both`, not restated here.

## Routes

None.

## Tests

**New: `tests/Feature/Mail/SeriesAccessMailTest.php` — 14 cases**
(`RefreshDatabase`; `setUp` travels to `2026-10-30 12:00:00 UTC`. Helpers:
`scene(?string $peerZone = 'America/New_York', array $groupOverrides = []): array{User, Group, Series, Access}`
builds the Group in `Australia/Brisbane` on the factory's default `free` plan
with an owner, a published Series and the Peer's Access;
`liveEpisode(Series $series, string $title, string $brisbaneStart, int $position, array $content = []): Episode`
writes `type` Live, `provider` Link, `content` `['join_url' => 'https://meet.google.com/abc-defg-hij', 'records' => true, ...$content]`,
`starts_at` from the Brisbane wall time and `ends_at` an hour later;
`chat(Series $series, ?string $expiresOn = null): SeriesChat` writes a
WhatsApp row with a url and `group_id` set explicitly;
`body(User $user, Series $series, Access $access): string` is
`implode(' ', (new SeriesAccessNotification($access, $series, $series->group->name))->toMail($user)->introLines)`.
Brisbane keeps AEST, UTC+10, all year; London left BST on 25 October 2026;
New York leaves EDT on 1 November 2026. "Week 3" is Sunday 1 November 2026
at 09:00 in Brisbane, which is 31 October 23:00 UTC.)

1. `test_it_names_the_next_session_in_the_recipients_zone_with_the_groups_zone_beside` — the New York Peer's body contains "Week 3", "Sat 31 Oct 2026, 7:00 pm EDT" and "Sun 1 Nov 2026, 9:00 am AEST".
2. `test_it_shows_a_london_recipient_the_same_session_in_gmt` — `Europe/London`: "Sat 31 Oct 2026, 11:00 pm GMT" beside the Brisbane time.
3. `test_it_follows_the_recipients_clock_across_their_daylight_saving_change` — travel to 2 November 2026; "Week 4" at 8 November 09:00 Brisbane reads "Sat 7 Nov 2026, 6:00 pm EST": the same Brisbane hour, one hour earlier on the New York clock.
4. `test_it_falls_back_to_the_groups_zone_when_the_recipient_has_none` — `users.timezone` null: "Sun 1 Nov 2026, 9:00 am AEST" once, and no "UTC" anywhere in the body.
5. `test_it_names_the_earliest_session_ahead_not_the_first_by_position` — position 1 "Week 4" on 8 November, position 2 "Week 3" on 1 November: "Week 3" named, "Week 4" not.
6. `test_it_passes_over_a_session_under_way_and_a_cancelled_one` — "Week 2" started ten minutes ago, "Week 3" with `content.cancelled_at` set, "Week 4" ahead: only "Week 4".
7. `test_it_says_nothing_about_a_session_when_none_is_ahead` — a File Episode and a live one that ended yesterday: `introLines` has two entries, as today.
8. `test_it_points_at_the_chat_when_the_series_has_a_current_invite` — a WhatsApp row with no expiry: the body contains `'Join the class chat from the ['.$series->title.' page]('.route('shared.show', $series->getKey()).'#chat).'`, so the chat URL is asserted here.
9. `test_it_omits_the_chat_line_when_the_series_has_no_chat` — no row: no "class chat".
10. `test_it_judges_a_codes_expiry_on_the_groups_calendar` — `expires_on` 31 October 2026: at 31 October 12:00 UTC (22:00 in Brisbane) the line is there; at 31 October 20:00 UTC (06:00 on 1 November in Brisbane) it is gone.
11. `test_it_speaks_the_groups_own_nouns` — `config()->set('qori.plans.free.'.Terminology::ENTITLEMENT, true)` (the scene's Group is `free`, so `Group::allows()` reads that key) and `scene()` called with `['settings' => [Terminology::SETTINGS_KEY => $labels]]`, where `$labels` is a full custom vocabulary with `episode` "Class"/"Classes" in the shape of `tests/Feature/TerminologyTest.php:36-50`, attached the way `:87-90` attaches one: "Your next Class," and no "Episode".
12. `test_it_carries_no_join_link_and_names_no_meeting_vendor` — a Zoom Episode with `join_url` `https://zoom.us/j/91827405566`: subject and body contain neither the join link nor "zoom" in any case, and the subject is still "You're in: <Series title>".
13. `test_it_is_the_notification_grant_sends_with_nothing_passed_in` — `Notification::fake()`, `AccessService::grant()` inside `CurrentGroup::runFor()` on the published Series with "Week 3" ahead; `Notification::assertSentTo($user, SeriesAccessNotification::class, fn ($notification) => str_contains(implode(' ', $notification->toMail($user)->introLines), 'Week 3'))`.
14. `test_it_links_the_next_session_to_its_anchor_and_keeps_the_button_on_the_series_page` — "Week 3" ahead: the body contains `route('shared.episodes.show', [$series->getKey(), $next->getKey()])` inside `'['.$next->title.']('`; `toMail()`'s `actionUrl` is still `url('/shared/'.$series->getKey())` and `actionText` still `__('accesses.mail.action')`.

**Changed:** none. `tests/Feature/Access/AccessServiceTest.php:264-275` keeps
passing: its Series holds one File Episode and no chat, so neither line
renders. `MailContentTest::test_every_notification_class_is_covered_by_the_command`
is unaffected: no notification class is added.

## Acceptance

- [ ] A Peer given access to a Series with a live Episode ahead reads its
      title and start in their own zone, with the zone named and the Group's
      zone beside it when different, and the title links to that Episode's
      anchor (`shared.episodes.show`) — the owner's scenario 2 in
      `docs/planning/course-classroom.md`: a Brisbane creator, a London Peer
      and a New York Peer across 1 November 2026
- [ ] A Peer with no timezone reads the start in the Group's zone, never UTC
- [ ] A session already under way, a cancelled one and a past one are never
      named; with none ahead, the email is today's
- [ ] A Series with a current chat invite tells the Peer it is on the Series
      page, linking its `#chat`; an expired code or no chat says nothing, and
      no platform name, invite link or image reaches the email
- [ ] No join link, recording, passcode or meeting vendor name reaches the
      email
- [ ] The email still comes from `AccessService::grant()` alone, with the
      notification's constructor unchanged, and `php artisan qori:mail:check`
      still reports "You're in: Mail Check Series .. ok"
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-132` `ready`, so `SeriesChat`, its `BelongsToGroup`, `series_id`,
  `platform`, `expires_on` (`immutable_date` cast) and `isExpired()` are
  frozen names — the stream owner's, once `T-132`'s own chain (`T-130`,
  `T-131`, `T-125`, `T-123`) is.
- `T-128` `ready`, so `App\Support\ZonedTime::zoneFor()`, `describe()`,
  `live.mail.when` and `live.mail.when_both` are frozen names — the stream
  owner's.
- If `T-005` lands first and has converted this email's lines to
  `Terminology::line()`, the two lines here follow the shape it chose; check
  before claiming — anyone's.

## Re-scope log

None.

## Notes

- Specified on 18 September 2026 from `D-028`, `D-029`, `D-024` and the
  classroom brief. `docs/planning/course-classroom.md` holds the story this
  serves: a Peer fifteen hours behind the creator gets access, and the email
  names the next class in her zone and points at the chat card.
- `depends: T-128, T-132`, as the brief's table says, and `T-128`'s front
  matter carries `blocks: T-129, T-136, T-138, T-140, T-145`, so
  `php artisan qori:tasks --check` agrees; an earlier draft of this file
  named only `T-132` and carried a fallback in which this task would have
  declared `ZonedTime` itself, which the brief forbids.
- `Series::nextLiveEpisode()` is one declaration in two tasks: whichever of
  `T-135` and this task lands first writes it on `app/Models/Series.php`, and
  the other's Files row is a no-op. The signature followed is `T-135`'s on
  disk, `nextLiveEpisode(?CarbonImmutable $now = null): ?Episode`; the
  brief's shared names spelled it `CarbonInterface $now`, and one spelling
  wins, `T-135`'s.
- The chat line keeps the brief's `:title` for the Series' title; `T-128`'s
  `:series_title` is for a line that carries both titles at once, and no line
  here does. Both lines gained `:url` after the first draft, because `D-024`
  and `D-029` name an anchor for each and a line with no link departed from
  both silently.
- "The owner's scenario 2" is the numbering of the owner's acceptance list as
  folded into `docs/planning/course-classroom.md`; `T-135` cites scenarios
  the same way, so if the merged file renumbers them, both tasks are edited
  together.
- `T-005` owns the rest of this email's vocabulary and `T-091` edits
  `AccessService::grant()`; neither meets the four files here.
- `T-025`'s open question — a Peer's dates in their own zone or the Group's —
  is answered by `D-028` and applied here to the first email a Peer gets;
  its owner rewrites its Scope.
- `qori:mail:check` renders the next-session line only if `T-128`'s scratch
  live Episode starts after the run. To read it in an inbox, follow
  `docs/tinker/mail.md`'s "Sending one message by hand" with a Series that
  has a live Episode ahead and a chat row.
