---
id: T-029
title: A live session has a time, and it is the right one
stream: onboarding
status: done
owner: claude
estimate: M
depends: T-024
blocks: none
---

# T-029 — A live session has a time, and it is the right one

## Why

`episodes.starts_at` exists, is validated, is read by the controller, is
rendered by the Series builder and the Peer's page — and **there is no field
anywhere in the product that sets it.** The Episode form collects `title`,
`type`, `provider`, `reference` and `is_preview`. A creator can add a Zoom
session and cannot say when it is.

Worse than that, adding the field naively would be wrong. `config('app.timezone')`
is `'UTC'` and `starts_at` is validated with `['nullable', 'date']`, so a naive
string from a `datetime-local` input is parsed **as UTC**. A creator in
Melbourne typing 9am would schedule 9am UTC — 7pm their time, and their Peers
would be told the wrong hour with total confidence.

So the time has to be stored UTC and entered in a zone somebody chose. That is
what makes `T-024` a prerequisite rather than a nicety, and it is why a timezone
is **mandatory for a Series with a live Episode** and optional otherwise.

## Decisions taken to make this specifiable

**Stored in UTC, entered and shown in the Group's zone.** `T-024` settled that
the Group's zone is what a scheduled time _means_, because the person choosing
it is the creator. The input is interpreted in that zone on the way in; the
instant is stored UTC; every reader sees it converted to their own.

**A timezone is required before a live Episode can be added.** Every other
onboarding step is optional and this one is not, which is worth stating because
it is the single exception to that stream's thesis. The reason it earns the
exception: the alternative is not an unconfigured product, it is a confidently
wrong one. A missing storage connection stops a creator; a missing timezone
misinforms their Peers.

**No timezone column on the Episode.** A stored UTC instant plus the Group's
zone is enough unless the zone changes between scheduling and the session — a
DST rule change, or the creator moving the Group. Rare, recoverable by editing
the Episode, and a column per Episode is a cost paid on every session to
insure against an event most Groups never see. Named as a known limitation
below rather than designed around.

## Preconditions

`T-024` shipped, so a Group can hold a timezone.

## Scope

**In:**

- A date-and-time field on the Episode form, shown only for a live Episode.
- Interpreting it in the Group's zone; storing UTC.
- Requiring the Group to have a zone before a live Episode can be added.
- Showing the time with its zone named, everywhere it appears.

**Out:**

- Notifying Peers that a session is coming. It needs mail, which is the
  `delivery` stream and blocked on the owner. `starts_at` being correct is the
  prerequisite for that work, not part of it.
- Calendar invites, `.ics`, reminders. Later, and each its own task.
- Recurring sessions.
- A per-Episode timezone — see the decision above.

## Files

| Path                                              | Change | Notes                                           |
| ------------------------------------------------- | ------ | ----------------------------------------------- |
| `app/Http/Requests/Share/StoreEpisodeRequest.php` | edit   | Require for live; interpret in the Group's zone |
| `app/Services/SeriesService.php`                  | edit   | Guard: no live Episode without a Group timezone |
| `app/Http/Controllers/Share/SeriesController.php` | edit   | Send the Group's zone to the form               |
| `resources/js/pages/share/series/Show.vue`        | edit   | The field, shown for live only                  |
| `resources/js/pages/shared/Show.vue`              | edit   | Name the zone beside the time                   |
| `resources/js/pages/public/Series.vue`            | edit   | Same                                            |
| `resources/js/components/series/SessionTime.vue`  | new    | One formatting, three surfaces                  |
| `lang/en/series.php`                              | edit   | 1 key                                           |
| `lang/en/errors.php`                              | edit   | 2 keys                                          |
| `tests/Feature/Series/LiveSessionTest.php`        | new    | 10 cases                                        |

**Added during execution.** None changes what gets built — see the report:

| Path                                               | Change | Why it was missing                                 |
| -------------------------------------------------- | ------ | -------------------------------------------------- |
| `app/Http/Controllers/Share/EpisodeController.php` | edit   | `series.session_scheduled` needed a caller         |
| `tests/Feature/Series/SeriesServiceTest.php`       | edit   | Its Groups had no timezone; two live cases refused |
| `tests/Feature/Series/EpisodeRoutesTest.php`       | edit   | Same, plus a live post with no `starts_at`         |

## Database

None. `episodes.starts_at` is already `timestamp` nullable and already cast to
`datetime`, which Laravel reads and writes as `config('app.timezone')` — UTC.
The bug is not the column.

## Code

```php
// App\Http\Requests\Share\StoreEpisodeRequest
/**
 * The naive input, read in the Group's zone and returned as UTC.
 *
 * `['date']` alone parses "2026-10-01T09:00" as UTC, so a creator in
 * Melbourne scheduling 9am would schedule their Peers' 7pm. The zone has to
 * be applied here, at the only point where the string is still known to be
 * local.
 */
private function startsAtUtc(): ?CarbonImmutable;
```

Validation: `starts_at` becomes `required` when `type === Episode::TYPE_LIVE`,
and `after:now` — a session scheduled in the past is a typo every time.

```php
// App\Services\SeriesService — in addEpisode(), beside the §8 provider rules
if ($type === Episode::TYPE_LIVE && $series->group?->timezone === null) {
    throw AppException::invalidRequest('errors.series.timezone_required');
}
```

Guarded in the service and not only the request, for the same reason every
other §8 rule is: the request is one caller.

```vue
// resources/js/components/series/SessionTime.vue defineProps<{ startsAt:
string; // ISO 8601 with offset, as the controllers already send timezone?:
string; // the Group's, for the "9am AEST" suffix }>();
```

Renders the viewer's local time **and names the zone**. An absolute time a
person has to show up for is the one case where "3pm" alone is not enough.

## Copy

| Key                               | File                 | English                                                                                                                                |
| --------------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `series.session_scheduled`        | `lang/en/series.php` | `:title starts :when.`                                                                                                                 |
| `errors.series.timezone_required` | `lang/en/errors.php` | message: `Set your :group's timezone before scheduling a live session.` resolution: `It decides what time your :peer_plural are told.` |
| `errors.series.starts_in_past`    | `lang/en/errors.php` | message + resolution                                                                                                                   |

## Routes

None. The field rides on the existing `share.series.episodes.store`.

## Tests

**New: `tests/Feature/Series/LiveSessionTest.php` — 10 cases**

1. `test_a_live_episode_requires_a_start_time` — the rule that does not exist
   today.
2. `test_a_file_episode_does_not` — the conditional half.
3. `test_a_time_is_read_in_the_groups_zone_and_stored_as_utc` — the core:
   Group in `Australia/Melbourne`, post `2026-10-01T09:00`, assert the stored
   value is `2026-09-30T23:00:00Z`. **This fails today.**
4. `test_a_group_in_utc_stores_what_was_typed` — the case that hides the bug.
5. `test_a_live_episode_is_refused_without_a_group_timezone`
6. `test_the_guard_is_in_the_service_not_only_the_request`
7. `test_a_session_in_the_past_is_refused`
8. `test_the_stored_instant_is_the_same_whichever_zone_entered_it` — two Groups
   in different zones scheduling the same real moment produce the same UTC.
9. `test_a_peer_sees_the_session_with_a_zone_named`
10. `test_editing_an_episode_keeps_the_time_it_had` — the round trip that
    naive parsing breaks on every save.

## Acceptance

- [x] A live Episode can be given a time through the interface
- [x] The time is entered in the Group's zone and stored in UTC
- [x] A live Episode is refused when the Group has no timezone, in the service
- [x] A session in the past is refused
- [x] Every surface showing a session time names the zone
- [x] Editing an Episode does not shift its time
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**Known limitation, accepted:** the stored instant is fixed at scheduling. If
the Group's zone changes afterwards — a DST rule change, or the creator moving
the Group — the session stays at the same real moment and its local time
appears to shift. Correct for anyone travelling to it, surprising for the
creator. The fix, if it ever matters, is a zone column on the Episode; not
worth a column on every session for an event most Groups never see.

**`dateStyle`/`timeStyle` cannot be combined with `timeZoneName`.** ECMA-402
throws `TypeError: Invalid option : option` for that pair, and because the
component formats during hydration the throw took the **whole page** down —
a blank screen, not a missing line. All three surfaces this replaces used the
shorthand pair, which is exactly why none of them named a zone: the obvious way
to add one does not work. `SessionTime` sets the components explicitly instead.
Caught in a browser; there is no JavaScript test runner here, so nothing else
would have caught it.

**`after:now` had to move behind the conversion.** Left on the raw input it
compares a naive local string against a UTC instant, so a creator west of
Greenwich would be refused a perfectly good future time. Converting in
`prepareForValidation()` rather than after validation fixes the rule and the
storage together, and is the only point where the string is still known to be
local.

**The guard reads the Group's own zone, not its resolved one.** `Group::timezone()`
falls back to the owner's zone and then to UTC, which is right for reading a
date and wrong for writing one. `hasChosenTimezone()` is what the guard asks.

**This is a capability `qori:reachability` cannot find.** The column, the
validation and the render all exist; only the input is missing, and the
command looks at routes and service methods rather than form fields. Worth
adding to `docs/planning/reachability.md` as an example of what a clean run
does not cover.
