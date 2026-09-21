---
stream: classroom
---

# Stream: classroom

**Goal.** A course taught live, week by week, works on Qori: each live
Episode is one card with one Qori link that a Peer follows before and after
class, offers Join when the session is scheduled, keeps the recording on the
same card afterwards, carries the lesson's materials and homework, and tells
every Peer with access once when the recording is there. A Peer fifteen hours
from the creator sees every time in their own zone and catches up from the
same link the creator shared in the class chat.

**Done when.** A creator with a ten-week Zoom course adds each session with
its time and length, pastes the join link, and after class pastes the
recording link; a Peer in another timezone who missed the class receives one
email, opens the Episode card, and finds the recording, the slides and the
homework with its due date in their own zone; a Peer who is there on time
joins from the card without a Zoom account; nothing on the public page or in
a preview exposes a join link, a recording or a material; and the walk in
`T-145` passes in a clean browser at mobile and desktop widths with the Peer's
timezone at least eight hours from the Group's.

**All seven providers stay in beta** (`D-018`). This stream is sequencing,
not scope: the pasted-link tier it ships stands in beside `D-016`'s per-Peer
grants until each provider's task in `storage` lands (`D-025`), and automatic
Zoom recording detection follows on `T-044`'s contract the sprint after the
manual checkpoint (`D-031`).

## Why this is its own stream

Two proposals for the next sprint were written independently on 17 September
2026, one by the owner and one by Claude, and merged the same day into
`D-024` to `D-031`. Both put the same person's course at the centre and both
reached the same cut: ship the card, the pasted recording, the materials and
the email now; find the recording automatically later. The work has its own
tables (`episode_recordings`, `materials`, `series_chats`, `session_notices`,
`access_opens`), its own components and lang files, and its own scheduled
command, all disjoint from `storage`'s `series_containers`, `vendor_grants`
and the Integrations page. Where it meets `storage` on a shared file, the
dependency rule applies: `T-125` waits on `T-089` for the Open route,
`T-141` and `T-142` wait on `T-044` for the Zoom connection, and `T-122`
shares `T-099`'s Zoom account and fixture layout.

## Tasks, in order

The first line of work is the manual-replay checkpoint the owner named
(`D-031`): everything a Peer needs from a class Qori cannot yet watch for
itself. The second line is what Qori does on its own once a Zoom connection
exists. Four tasks in the same sequence belong to other streams and are
listed there: the spike `T-122` runs first, in week 1, in `storage` beside
`T-099`, so `T-142` can be specified against real payloads; `T-141` (the
Zoom connection on `T-044`'s contract) and `T-142` (`FindsRecordings` and the
Zoom folder) are `storage`'s and come before `T-143`; `T-145`, the browser
walk, is `workflow`'s on `T-120`'s pattern and is the beta-gate evidence.

1. `T-123` — A live Episode has an end and one start: `ends_at`, a length
   field, the `records` switch, `EpisodeProvider::Link` for Meet and any other
   host, `starts_at` out of `content`, and every `qori.live`, `qori.materials`
   and `qori.chats` number this stream reads declared once in `config/qori.php`
2. `T-124` — A creator corrects a live Episode's link, time and length:
   the edit form, so a class already held can take its recording without
   delete-and-re-add losing Peers' progress ids; creates `LiveSessionService`
   with the row lock every later write to a live Episode's `content` uses
3. `T-125` — A Peer joins a live Episode from the Series page, in their own
   time: the computed session state and its honest copy, Join through
   `T-089`'s route, the stable `shared.episodes.show` address every email
   and calendar file is minted against, the `access_opens` log
4. `T-126` — A creator adds a recording link to a live Episode, and Peers
   watch it from the same card: `episode_recordings`, published on paste
5. `T-127` — A recording can be hidden, added to, or declared not recorded,
   and an overdue session says so: the rest of the card's states
6. `T-128` — Every Peer with access hears once when a recording is
   published: the `session_notices` ledger as an outbox, `recording_ready`,
   `qori:sessions:notify`; its mail names the after-session materials, so it
   follows `T-130`
7. `T-129` — The creator is told when a recording is missing, and sees
   whether the recording email went: `creator_recording_needed` and the
   ledger read back on the card
8. `T-130` — An Episode holds several materials a creator adds, uploaded to
   Qori or linked: the `materials` table, the link tier, homework's brief and
   due date, removal that cleans Qori's storage
9. `T-131` — A Peer opens materials before and after the session, and sees
   homework due in their own time: `shared.materials.open`, the signing
   contract, the release gate on Qori-hosted files, the list on the card
10. `T-132` — A Peer with access finds the class chat on the Series page:
    `series_chats`, a link or a QR image, expiry
11. `T-133` — A Peer adds a live Episode to their calendar: the RFC 5545 file
    with `SEQUENCE` from `schedule_version`, the one self-serve reminder
    every plan has
12. `T-134` — A creator can cancel a live Episode, undo it, and add the next
    session: first on the slip list, because a ten-week course is ten copies
13. `T-135` — A buyer sees the next session before paying, and the creator
    can copy a message for the chat
14. `T-136` — The access email names the next session and the class chat
15. `T-137` — A Series holds materials of its own, and materials can be
    reordered: only once the pilot shows material repeated across Episodes
16. `T-138` — Peers are reminded the day before a live Episode, and told when
    it is cancelled: `day_before` on Start and above, `session_cancelled` to
    whoever was reminded
17. `T-139` — Qori storage counts a Series' total, not only each file: the
    owner's 100 MB answer of 6 September 2026, once the Free figure is set
18. `T-140` — A creator can tell Peers about a corrected recording: the one
    deliberate re-send, keyed on `publication`
19. `T-143` — `qori:recordings:find` looks for recordings with backoff and
    lands them for review: the sweep, review-first, the ambiguity hold; after
    `storage`'s `T-141` and `T-142`
20. `T-144` — A creator publishes, rejects or picks the right recording, and
    Check now runs the search at once

**The cut** (`D-031`). The manual-replay checkpoint is `T-122` and tasks 1
to 11. Tasks 12 to 18 follow in that order when the checkpoint lands or
slips; the sprint after builds `T-141`, `T-142` and tasks 19 and 20 on
`T-044`'s contract with `T-122`'s fixtures already committed; `T-145` is the
evidence for the beta gate.

**Lanes.** Two developers: one takes the creator side first (`T-123`,
`T-124`, `T-130`), then the slip list (`T-134`, `T-137`, `T-139`); the other
the Peer side and the notices (`T-125` once `T-124` and `T-089` are in,
`T-126`, `T-127`, `T-128`, `T-129`, `T-131`, `T-132`, `T-133`). `T-122` runs on
day 1 by whoever holds the Zoom account.

## Claim order

**Claim in the order above.** The dependencies already serialise most of this;
where they do not, whoever claims second adds one rather than letting two
people meet in a merge (`PROCESS.md`). A task that jumps the queue checks the
board first, because two `doing` tasks claiming one file fail it.

These are the files more than three tasks touch, each with its claimants in
order. Every new card is its own component, so a page edit is a mount and the
page itself is claimed by as few tasks as possible.

- `app/Http/Controllers/Share/SeriesController.php` — `T-123`, `T-124`, `T-126`, `T-127`, `T-129`, `T-130`, `T-132`, `T-134`, `T-135`, `T-137`, `T-138`, `T-139`, `T-140`, `T-143`, `T-144`
- `docs/flows/live-sessions.md` — `T-125`, `T-126`, `T-127`, `T-128`, `T-129`, `T-133`, `T-134`, `T-135`, `T-138`, `T-140`, `T-143`, `T-144`
- `docs/tinker/live-sessions.md` — `T-125`, `T-126`, `T-127`, `T-128`, `T-129`, `T-133`, `T-134`, `T-135`, `T-138`, `T-140`, `T-143`, `T-144`
- `lang/en/errors.php` — `T-123`, `T-125`, `T-126`, `T-127`, `T-130`, `T-131`, `T-132`, `T-133`, `T-137`, `T-139`, `T-140`, `T-144`
- `lang/en/live.php` — `T-125`, `T-126`, `T-127`, `T-128`, `T-129`, `T-133`, `T-134`, `T-135`, `T-138`, `T-140`, `T-143`, `T-144`
- `lang/en/series.php` — `T-123`, `T-124`, `T-126`, `T-127`, `T-130`, `T-132`, `T-134`, `T-138`, `T-140`, `T-143`, `T-144`
- `resources/js/components/series/LiveSessionPanel.vue` — `T-123`, `T-124`, `T-126`, `T-127`, `T-129`, `T-134`, `T-135`, `T-140`, `T-143`, `T-144`
- `app/Http/Controllers/Shared/SharedController.php` — `T-125`, `T-126`, `T-127`, `T-131`, `T-132`, `T-133`, `T-134`, `T-137`, `T-138`
- `app/Services/LiveSessionService.php` — `T-124`, `T-125`, `T-126`, `T-127`, `T-134`, `T-138`, `T-143`, `T-144`
- `app/Models/Episode.php` — `T-123`, `T-124`, `T-126`, `T-127`, `T-140`, `T-143`
- `app/Services/RecordingService.php` — `T-126`, `T-127`, `T-128`, `T-140`, `T-143`, `T-144`
- `docs/flows/series.md` — `T-123`, `T-124`, `T-130`, `T-134`, `T-135`, `T-138`
- `resources/js/components/series/LiveSessionCard.vue` — `T-125`, `T-126`, `T-127`, `T-133`, `T-134`, `T-138`
- `resources/js/pages/shared/Show.vue` — `T-125`, `T-131`, `T-132`, `T-133`, `T-137`, `T-138`
- `routes/share/episodes.php` — `T-126`, `T-127`, `T-130`, `T-134`, `T-140`, `T-144`
- `app/Services/EpisodeService.php` — `T-123`, `T-124`, `T-130`, `T-138`, `T-143`
- `app/Services/SessionNoticeService.php` — `T-128`, `T-129`, `T-138`, `T-140`, `T-143`
- `config/qori.php` — `T-123`, `T-125`, `T-138`, `T-139`, `T-141`
- `docs/flows/README.md` — `T-125`, `T-128`, `T-130`, `T-132`, `T-143`
- `resources/js/pages/share/series/Show.vue` — `T-123`, `T-130`, `T-132`, `T-137`, `T-139`
- `app/Http/Controllers/Share/RecordingController.php` — `T-126`, `T-127`, `T-140`, `T-144`
- `app/Models/Series.php` — `T-135`, `T-136`, `T-139`, `T-143`
- `app/Providers/IntegrationServiceProvider.php` — `T-131`, `T-141`, `T-142`, `T-143`
- `app/Services/MaterialService.php` — `T-130`, `T-131`, `T-137`, `T-139`
- `database/seeders/DesignReviewSeeder.php` — `T-123`, `T-130`, `T-132`, `T-137`
- `docs/flows/materials.md` — `T-130`, `T-131`, `T-137`, `T-139`
- `docs/flows/storage.md` — `T-125`, `T-131`, `T-139`, `T-141`
- `docs/tinker/uploads.md` — `T-130`, `T-132`, `T-137`, `T-139`
- `lang/en/materials.php` — `T-130`, `T-131`, `T-137`, `T-139`
- `routes/shared.php` — `T-125`, `T-131`, `T-132`, `T-133`

Everything else is touched by one task, or by two the dependencies already
order.

## Where it touches other streams

`storage` owns the Open route (`T-089`), the connection page (`T-044`), the
grant foundation (`T-091`) and the Zoom registrant model (`T-099`, `T-100`);
`D-025` to `D-027` amend those drafts, and the amendment is written into
each. `delivery` owns proving mail arrives (`T-032`), which comes before
`recording_ready` reaches a real Peer. `onboarding` owns `T-025`, whose open
question `D-028` answers. `selling`'s `T-102` edits `SharedController` for
the Confirming page, and `T-043`'s invitations are not a prerequisite: the
public link and the code sign-in are how a new attendee gets in. `operations`
owns the worker (`T-018`) and the alerts (`T-019`); the notify command logs a
heartbeat for the second and sends inline because of the first.

## Notes

**Two proposals, one plan.** The owner's research proposal and Claude's
independent plan, both dated 17 September 2026, are merged in
[`../course-classroom.md`](../course-classroom.md), which keeps the story,
the competitor patterns, the vendor facts, the spike questions, the fourteen
acceptance scenarios and the measures. Where the two disagreed, the choice
and its reason are in `decisions.md` (`D-024` to `D-031`): one Peer
destination with a stable per-Episode address rather than a second page;
recordings in their own table; review-first publication with a hold on
ambiguous matches; the ledger as the outbox; one reminder kind; the calendar
file in the checkpoint; a Zoom connector task the plans had left out.

**Sizes are honest, not comfortable.** The checkpoint is twelve tasks, ten of
them `M`, on two developers over two weeks, and the two Vue pages serialise
most of them. If it slips, it slips in the order above; nothing in tasks 13
to 19 is promised for the sprint.

**Owner's day-one items** (`D-031`): a month of Zoom Workplace Pro and the
development app for `T-122`; answers to `T-089`'s three open questions so the
Peer lane can start (answered 19 September 2026: none is left, and since
`D-043` nothing waits on an approval); the schedule interval for `qori:sessions:notify` against
Laravel Cloud's sleep timeout, chosen with `T-091`'s.
