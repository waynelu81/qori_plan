---
id: T-122
title: Spike: a Zoom cloud recording is found from a pasted join link and opens for someone outside the account
stream: storage
status: blocked
owner: unassigned
estimate: S
depends: none
blocks: T-141, T-142
---

# T-122 — Spike: a Zoom cloud recording is found from a pasted join link and opens for someone outside the account

## Why

Nobody at Qori has seen a Zoom recordings response. `app/Integrations/` holds
`CloudflareR2`, `Contracts`, `Dropbox`, `Stripe` and `Vimeo` and no Zoom
folder; `EpisodeProvider::Zoom` (`app/Enums/EpisodeProvider.php:23`), its
`connection()` arm (`:48`) and `EpisodeType::Live` allowing Zoom and Teams
(`app/Enums/EpisodeType.php:35`) are the only mentions under `app/`; the tag
line at `app/Providers/IntegrationServiceProvider.php:35` carries three media
providers and no Zoom class; `PlaybackTicketService::resolve()` throws
`errors.playback.unsupported_provider` for a live Episode
(`app/Services/PlaybackTicketService.php:85-89`); `docs/flows/storage.md:98-103`
lists Zoom join links under "Not built yet"; and `tests/Fixtures/` holds
`google/` — `T-093`'s 66 bodies and two header captures — beside `planning/`
and `reachability/`, and nothing from Zoom. `D-027` makes
recording detection a scheduled REST poll and calls its matching window
"provisional until `T-122`'s fixtures", `T-142` (`ZoomRecordings`,
`ZoomMeetingLink`) reads `GET /meetings/{meetingId}/recordings` and
`GET /past_meetings/{meetingId}/instances`, and `T-141` (`ZoomAccounts`) reads
`GET /users/me/settings` to tell a creator whether their plan keeps cloud
recordings. `PROCESS.md` says a spec that names a vendor payload cites an
observed response or a committed fixture, so neither can be `ready` until this
runs.

The facts the two specs rest on are all unobserved: which instance the
meeting-id call returns for a recurring meeting, and how far an instance's
`start_time` drifts from the schedule; which file `status` a recording still
being processed carries, when Zoom documents only `completed`; whether
`share_url` is in the REST response at all, when Zoom documents it only in the
`recording.completed` webhook payload; whether a person with no Zoom account
opens a recording signed out under each sharing mode, and whether the passcode
can ride in the URL (`D-027` leaves that to this spike); whether
`recording.cloud_recording` from `GET /users/me/settings` tells a Basic host
from a Pro host; and whether REST calls work from an install made through
Zoom's Request to Share (beta). Two planning documents also disagree about who
can install the app before Marketplace review: `docs/planning/vendor-accounts.md:966-967`
says review "is the gate on every creator outside Qori's own Zoom account" and
`:985-991` that the private-link route "cannot be used to onboard creators",
while the merged plan (`docs/planning/course-classroom.md`) planned this
spike's outside account and its beta creators on Request to Share (beta). One
of them is wrong, and the Marketplace submission `D-031` says to prepare this
sprint depends on which.

Afterwards every response `T-141` and `T-142` name is a redacted fixture under
`tests/Fixtures/zoom/recordings/`, with the date, the app, the scope list and
the seconds per call in `tests/Fixtures/zoom/README.md`; the Zoom scope list
is frozen once, as one union, in `vendor-accounts.md`, and its beta-share
paragraph says what was observed; the report's answer table has one row per
question; and one person with no Zoom account and no relation to Qori's Zoom
account has opened a recording, signed out, using only the link and passcode
Qori would store.

## Blocked on

What: a month of Zoom Workplace Pro on Qori's account, because cloud recording
needs Pro or above and a Basic account cannot produce the responses this spike
records (`docs/planning/course-classroom.md`, vendor facts); a user-managed
General app in development mode with its development credentials
(`docs/planning/vendor-accounts.md`, "What you open", steps 3 to 7); and a
Request to Share (beta) for one outside account, a Basic account preferred so
question 5 can be answered on it.

Who: wayne. Two of the three — the Pro month and the development app — are
`D-031`'s day-one items; the third, the beta share, is the `T-122` line under
"Open decisions" in `decisions.md`; `docs/planning/streams/classroom.md` says
the spike runs on day 1 by whoever holds the Zoom account.

## Decisions taken to make this specifiable

**This spike takes the recordings step from `T-099`, and `T-099` keeps
registrants.** `D-027`: "`T-099`'s recording step becomes `T-122`'s". The
classroom sprint needs the recording answers in week 1 so `T-142` can be
specified before the sprint after; the registrant model is the connected tier
(`D-026`) and is not on this sprint's path. The two spikes share the Zoom
account, the General app and the fixture README, and `T-099`'s step 17 and its
`recordings/` fixture row are struck (see Notes).

**Fixtures follow `T-099`'s naming, and every one this spike writes sits under
one group, `recordings/`, with one exception for the OAuth pair.**
`<group>/<call>.<case>.<status>.json`, with a status-only capture as `.txt`;
the two `/users/me` reads sit under `recordings/` too, as `user_settings` and
`user_me`, so `T-141` and `T-142` read one directory and `T-099` keeps
`meetings/`, `registrants/` and `webhooks/`. `oauth/` is `T-099`'s group, but
its first two files — `oauth/token.authorization_code.200.json` and
`oauth/token.refresh.200.json`, which `T-141` reads — are captured by
whichever spike authorises the app first, on the way to its bearer token,
under `T-099`'s redaction map; the stream file runs this spike on day 1, so
the Files table carries them here, conditionally, and `T-099`'s refresh-reuse
probe stays its own. Whichever spike lands first creates
`tests/Fixtures/zoom/README.md` and the other adds its section: the file has
one `##` section per spike, `## T-099 — registrants` and
`## T-122 — recordings`, each with its own date, app name and mode, scope
list, roster, redaction map and per-file rows, so neither spike edits the
other's section, and `T-099`'s README row takes the same shape (Notes).

**The meeting id placeholder is `91827405566`.** `T-099` asks for one fixed
eleven-digit placeholder and does not choose it. This is the number the
design-review world already carries (`918 2740 5566`,
`database/seeders/DesignReviewSeeder.php:356`) and the join link `T-123` gives
that Episode (`https://zoom.us/j/91827405566`), so a fixture, the seeded world
and `ZoomMeetingLink`'s tests agree on one number.

**Redaction is `T-099`'s fixed map, extended for recordings.** `access_token`,
`refresh_token` and any `Authorization` header become `REDACTED`; `start_url`
becomes `REMOVED`; `host_id`, `host_email` and `account_id` keep their shape
and take a stable placeholder; the meeting id becomes `91827405566` everywhere;
`pwd` and `tk` query values in a `join_url` become `REDACTED` with the
parameter names kept; emails become the roster names at `example.test`. For
recordings: `recording_play_passcode`, `password` and `passcode` become
`REDACTED`; the token segment of `play_url`, `share_url` and `download_url`
becomes `RECORDING_TOKEN` with the host and path shape kept, and a
`download_url`'s `access_token` query value becomes `REDACTED`; each
instance's `uuid` and each `recording_files[].id` and `meeting_id` take a
stable placeholder per instance (`INSTANCE_1`, `INSTANCE_1_FILE_1`, …),
because `T-142` matches on them; `topic` becomes `Spike daily session`.
Everything else stays verbatim: every `status`, `recording_type`, `file_type`,
`file_extension`, `file_size`, `duration`, `start_time`, `recording_start`,
`recording_end`, `auto_delete_date`, `occurrence_id`, `code`, `message`, and
every `Retry-After` and `X-RateLimit-*` header. The map lives in the README as
placeholder → meaning.

**The recurring meeting is daily, not weekly, and the instance questions
are the same.** A fixed-time recurring meeting (Zoom type 8) with a daily
recurrence gives three held occurrences inside one working week; whether the
meeting-id call returns the latest instance, how `start_time` drifts and what
the instances list carries do not depend on the gap between occurrences. The
README says the meeting was daily.

**Every call is timed, and the two timeouts are checked against the
observation.** `curl -w time_total` on every call, recorded per fixture row.
`T-143`'s two constants on `LiveSessionService` — 30 seconds for the sweep,
5 for Check now (`T-144`) — are the sweep-and-request pair `T-091` set; the
README's seconds are what those numbers are checked against, and a call that
took longer than 5 seconds is a finding for `T-144`.

**Signed out means a clean browser profile, never a Zoom account of Qori's
signed in.** A Peer is somebody with no Zoom account at all; a Basic account
signed in would prove less than the case Qori has to serve. The outside
account's job is questions 5, 6, 7 and 10 — a Basic host's settings, another
host's meeting, REST from a beta install and what the console offers — not the
signed-out open.

**Sharing modes are switched in Zoom's web portal, as a creator would, and
read back by API.** `GET /meetings/{meetingId}/recordings/settings` is read
under each mode; nothing PATCHes the settings, because Qori never will
(`D-027`: only Check now and the sweep re-read the vendor, and neither writes).

**The webhook half of question 7 is observed and nothing is built.** This task
adds no endpoint. If a public HTTPS endpoint is at hand for `T-099`'s step 18,
whether `recording.completed` arrives for a recording on Qori's own account is
noted there and the payload goes in `T-099`'s `webhooks/` group; whether an
event subscription can be created for a user-managed General app before
publication is answered by attempting one call of Zoom's Marketplace event
subscription API and recording the status, with the exact path used written in
the README. A Basic outside account cannot cloud-record, so whether an event
reaches a beta install is "not observed" unless the share goes to a Pro
account, and the README says so.

**The scope list is frozen as the union of every list written so far, recorded
once, and checked against the console's spelling.** Seventeen scopes (under
Scope). The two the merged plan marks optional —
`cloud_recording:read:recording_settings` and
`cloud_recording:read:list_user_recordings` — stay in, because `T-099` already
asks for both, dropping a scope before submission costs nothing and adding one
after publication brings a complete re-review (KB0058021, cited in `T-099`).
The three write scopes `T-099` asked for only for its step 17 —
`cloud_recording:update:recording_settings`,
`cloud_recording:write:recording_registrant` and
`cloud_recording:update:registrant_status` — stay in the union for the same
reason and are entered on the development app so the console's spelling of
each is read; nothing in this task or in `T-100`'s `ZoomAccounts::SCOPES`
calls what they permit, and Zoom's review may refuse a scope it thinks
unnecessary (`vendor-accounts.md`, step 6), so the report carries a "Found,
not fixed" bullet asking `T-099`'s owner to strike the three before
submission (`→ T-099`), and this task neither strikes them nor shortens
another task's list. Question 8 replaces any string here with the console's
exact spelling; the report lists the strings as the console shows them.

**Question 10 is decided by evidence, and this task corrects whichever
document is wrong.** `vendor-accounts.md` and the merged proposal cannot both
be right about Request to Share (beta). The report says what the console
offered, the turnaround it stated and whether the outside account could
install; the paragraph in `vendor-accounts.md` is rewritten to match. That is a
wording change to a planning document, not a decision: no choice is left once
the console has been looked at. If the beta share cannot admit an outside
creator, the outside-account half is "not observed" with that reason, and
`T-141`'s tier copy says Marketplace review gates every creator.

**Answers go into `T-141` and `T-142`, not `decisions.md`.** As `T-099` does
with `T-100`: each bullet in those drafts marked the spike's is struck with
the date and a one-line answer. A fact that leaves a choice is a bullet for
the owner in the task it affects, tagged `→ T-141` or `→ T-142` in the report.

**A PMI, a vanity link and a no-fixed-time meeting are each recorded once, on
Qori's account, and a vanity URL is expected to be "not observed".** A vanity
URL needs a Business account or above, which the owner has not bought; the
README's link-shape table records the shapes that were seen and names the
vanity shape from Zoom's documentation as unobserved.

**No app code and no test.** The fixtures are read by `T-141`'s and `T-142`'s
`Http::fake()` tests; this task writes none, so its test total is zero.

## Preconditions

**Data this task verifies against:** nothing in Qori's database. Everything is
in Zoom, on the accounts the roster names:

- `qori-pro` (Qori's Zoom Workplace Pro account): one fixed-time recurring
  meeting, daily, with at least three occurrences, of which two are held and
  cloud-recorded for longer than six minutes (above the five-minute floor
  `D-027` sets — `qori.live.min_recording_minutes`, declared by `T-123`) with
  the recording stopped and started again during one of them; a third occurrence held on the same meeting id,
  ended, and restarted within ten minutes; one short test meeting on the same
  id the day before the first occurrence, under five minutes; one PMI meeting
  recorded once; one recurring meeting with no fixed time (Zoom type 3)
  recorded once; auto-delete switched on in the account's recording settings
  for one of the recordings; one recording moved to trash after its fixture
  is taken.
- `outside-basic` (the outside account, once the beta share is granted): one
  meeting of its own, with cloud recording attempted and refused.
- `peer-signed-out`: no account; a clean browser profile.

**Equipment:** the Pro licence, the General app in development with the
seventeen scopes under Scope and a redirect URI the spiker can read
(`http://127.0.0.1` is enough for a hand-made code exchange —
`vendor-accounts.md`, step 5); the Basic outside account and its beta share; a
clean browser profile or private window with no Zoom sign-in, plus a phone
with no Zoom app for the same open on a second device; a stopwatch or the wall
clock for processing times; `curl` and `jq`. Optional: a public HTTPS endpoint
that can log a webhook, shared with `T-099`'s step 18.

**Spike:** this is the spike. It owes nothing and names no response field as
observed until its fixture exists.

## Scope

**In:**

Every call is run as the account named, with `T-099`'s helper
(`curl -sS -i -w '\ntime_total=%{time_total}\n'` on `https://api.zoom.us/v2`
with a bearer token), the status line and headers kept in the capture and the
body alone committed, redacted. Paths and field names below are the API spec's
([api-hub endpoints](https://developers.zoom.us/api-hub/meetings/methods/endpoints.json),
[Meetings API](https://developers.zoom.us/docs/api/meetings/)); no response
field is observed until its fixture exists.

The ten questions. The first nine are the merged plan's spike questions
(`docs/planning/course-classroom.md`), as written there, except that question
1's "weekly" is read as "daily" (Decisions):

1. **Instances.** For a weekly meeting, when does the latest-instance call
   suffice, and how far does an instance's `start_time` drift from schedule?
   Does the instances list's `occurrence_id` make time matching unnecessary?
   How does that compare with one `GET /users/me/recordings?from=&to=` call?
    - `GET /meetings/91827405566/recordings` after two recorded occurrences →
      `get_meeting.latest.200.json`; the README row says which occurrence came
      back.
    - `GET /past_meetings/91827405566/instances` →
      `list_instances.daily.200.json`; each instance's `uuid`, `start_time`
      and whether an `occurrence_id` is present, beside the scheduled time.
    - `GET /meetings/{uuid}/recordings` for the earlier instance →
      `get_meeting.by_uuid.200.json`; if a uuid starts with `/` or contains
      `//`, the same call double-encoded → `get_meeting.by_uuid_encoded.<status>.json`,
      else the README's gap list says no such uuid occurred.
    - `GET /users/me/recordings?from=<day 1>&to=<day 3>` →
      `list_user.window.200.json`.
    - The occurrence ended and restarted: `list_instances.restarted.200.json`
      and `get_meeting.restarted.200.json` — one instance or two, and which
      the meeting-id call returns (owner acceptance 8: a restarted meeting).
    - The occurrence whose recording was stopped and started again:
      `get_meeting.paused.200.json` — how many `recording_files` entries, and
      their `recording_start`/`recording_end` (owner acceptance 8: multiple
      segments).
    - The short test meeting the day before: `list_instances.early_test.200.json`
      and `get_meeting.early_test.200.json` — whether it is the instance the
      meeting-id call returns, and its `duration` (owner acceptance 8: an
      early test recording; `D-027`'s hold for a duration under five minutes
      and a start outside the window).
2. **Processing.** Which file `status` means still processing (only
   `completed` is documented), and how long did processing really take?
    - `GET /meetings/91827405566/recordings` within five minutes of an
      occurrence ending, repeated every five minutes for the first hour and
      hourly after that until a file is `completed`, with the interval in use
      written in the README → `get_meeting.processing.<status>.json` for the
      first answer (a body with a non-`completed` `status`, or a `404` with
      its `code`), and the README's processing-time table: minutes from the
      scheduled end to the first `completed` file, per occurrence, to the
      precision of the interval in use at the time.
    - After one recording is moved to trash →
      `get_meeting.deleted.<status>.json` (owner acceptance 9: an
      expired or deleted recording).
3. **Signed-out access.** Does the recording link with `?pwd=` open signed
   out under "Everyone with the recording link", "Sign in to Zoom" and
   on-demand registration? How do the results compare with
   `share_recording`, `recording_authentication` and `on_demand` from
   `GET /meetings/{meetingId}/recordings/settings`?
    - Under each mode, switched in the web portal:
      `GET /meetings/91827405566/recordings/settings` →
      `settings.everyone_with_link.200.json`, `settings.sign_in_to_zoom.200.json`,
      `settings.on_demand.200.json`.
    - Under each mode, in the clean profile and on the phone: open the link
      the fixture holds (`share_url` when present, else the video file's
      `play_url`), first bare — entering the passcode when asked — then with
      `?pwd=<recording_play_passcode>` appended. The report records, per
      mode and per link, whether it played, what Zoom asked for first, and
      whether `?pwd=` alone was enough. This is the signed-out open the title
      names, and the acceptance line below.
4. **Sharing changes.** Does switching a recording's sharing mode change its
   stored link?
    - After the three switches, `GET /meetings/91827405566/recordings` →
      `get_meeting.after_sharing_change.200.json`; the README row compares
      `share_url` and each `play_url` with `get_meeting.latest.200.json`.
5. **Plans.** Does `recording.cloud_recording` from `GET /users/me/settings`
   tell a Basic host from a Pro host? What is Basic's current meeting-length
   limit?
    - `GET /users/me/settings` as `qori-pro` → `user_settings.pro.200.json`
      and as `outside-basic` → `user_settings.basic.<status>.json`; the
      report reads `recording.cloud_recording`, `recording.auto_recording`,
      `recording.authenticated_view_cloud_recoding` (Zoom's spelling) and
      `recording.auto_delete_cmr_days` from each.
    - `GET /users/me` as each → `user_me.pro.200.json`,
      `user_me.basic.<status>.json`, for the `type` value and the display
      name `T-141` shows after connecting.
    - Basic's meeting-length wording, read from the outside account's own
      portal and Zoom's pricing page on the day, quoted in the report with
      the date.
6. **Other links.** What do PMI links, vanity links, meetings hosted by
   another user, and a recurring meeting with no fixed time return?
    - The PMI, recorded once: `GET /meetings/{pmi}/recordings` →
      `get_meeting.pmi.<status>.json`.
    - A vanity link: `get_meeting.vanity.<status>.json` only if a vanity URL
      exists on an account the spike can use; else the README's gap list
      says so and the link-shape table carries the documented shape as
      unobserved.
    - Another host: `qori-pro`'s token on `outside-basic`'s meeting id →
      `get_meeting.other_host.<status>.json` (the `code` — `3000`, `1001` or
      another — is what `T-142` maps to "not this account's meeting").
    - The no-fixed-time meeting, recorded once:
      `get_meeting.no_fixed_time.<status>.json` and
      `list_instances.no_fixed_time.<status>.json`.
    - The README's link-shape table: every join-link shape met on the way —
      `zoom.us/j/{id}`, a regional `{sub}.zoom.us/j/{id}?pwd=`, the PMI's
      `/j/{pmi}` and `/my/{name}`, the no-fixed-time meeting's link, and the
      outside account's — with the meeting id each yields or none. This is
      what `T-142`'s `ZoomMeetingLink::meetingId()` is written against.
7. **Beta installs.** Do REST calls work from the beta install? Does
   `recording.completed` reach it (observe only)? Is Zoom's event
   subscription API usable for a user-managed General app before
   publication?
    - `outside-basic` installs through the Request to Share URL and
      authorises; its token on its own meeting:
      `GET /meetings/{outside meeting}/recordings` →
      `get_meeting.beta_install.<status>.json`. A `404` with a "no
      recording" `code` is an authenticated answer and proves REST works; a
      `401` or a scope refusal is the finding.
    - `recording.completed`: observed only if `T-099`'s step 18 endpoint
      exists, for a recording on `qori-pro`; "not observed" otherwise, and
      "not observable on a Basic outside account" for the beta-install half.
    - One attempt to create an event subscription for the app through
      Zoom's Marketplace event subscription API →
      `event_subscriptions.create.<status>.json`, with the exact path used
      in the README; only if attempted, else the gap list says why.
8. **Scopes and licence.** What are the exact granular scope strings? Does
   Zoom's API licence (the clause `T-099` leaves open for `registrant_id`
   and `join_url`) also cover storing a recording's link and passcode?
    - The seventeen scopes below are entered on the app's Scopes page; the
      report lists them as the console spells them, and any string that
      differs is corrected in this task, in `T-099`, `T-100`, `T-141`,
      `T-142` and `vendor-accounts.md` in one commit.
    - The licence question is read, not called: the report cites the clause
      of Zoom's API licence and terms of use
      ([API terms](https://www.zoom.com/en/trust/legal/zoom-api-license-and-tou/))
      that governs storing a recording's link and passcode, with the section
      as rendered on the day, and says whether it is confirmed with Zoom at
      review, as `T-099` does for registrants.
9. **`share_url`.** Does `GET /meetings/{meetingId}/recordings` return
   `share_url` for a user-managed app, and when it does not, does
   `play_url?pwd=` open signed out?
    - Read from `get_meeting.latest.200.json`; the report's field table says
      which of `share_url`, `play_url`, `download_url`,
      `recording_play_passcode`, `password`, `auto_delete_date`, `duration`,
      `start_time`, `uuid`, `occurrence_id`, `recording_type`, `file_type` and
      `status` were present, with one example value each, redacted.
    - With auto-delete on: `get_meeting.auto_delete.200.json` — whether
      `auto_delete_date` appears and its format, which is `T-142`'s
      `availableUntil`.
    - The signed-out open of `play_url?pwd=` is question 3's second pass.
10. **Request to Share.** What does the Marketplace console offer for Request
    to Share on a user-managed General app in development, what turnaround
    does it state, and which is right: `vendor-accounts.md` (Marketplace
    review gates every outside creator; the private-link route cannot onboard
    creators) or the merged proposal (a beta share admits outside creators,
    up to 100 user-level additions, on a four-week URL extended twice)? The
    report says what the console offered, quotes its wording with the date,
    and corrects whichever document is wrong.

The scope list entered on the app, frozen as the union of every list written
so far (`vendor-accounts.md`'s six, `T-099`'s thirteen, `T-100`'s nine, and
the four this plan adds), seventeen user-level granular scopes:
`meeting:write:meeting`, `meeting:read:meeting`, `meeting:read:list_meetings`,
`meeting:update:meeting`, `meeting:write:registrant`,
`meeting:read:list_registrants`, `meeting:update:registrant_status`,
`meeting:delete:registrant`, `meeting:read:list_past_instances`,
`cloud_recording:read:list_recording_files`,
`cloud_recording:read:list_user_recordings`,
`cloud_recording:read:recording_settings`,
`cloud_recording:update:recording_settings`,
`cloud_recording:write:recording_registrant`,
`cloud_recording:update:registrant_status`, `user:read:user`,
`user:read:settings`. After question 8 the list is written once, in
`vendor-accounts.md`'s step 6, and every task cites it there.

Also in:

- `tests/Fixtures/zoom/README.md`: this spike's section — date, the app's
  name and mode, the scope list, the account roster, the redaction map, the
  link-shape table, the processing-time table, one row per fixture (call,
  case, status, seconds, and when the call was made relative to the
  occurrence's scheduled end), and the gap list.
- `docs/planning/vendor-accounts.md`: the `T-099` line at `:787` gains
  `T-122`, `T-141` and `T-142`; the table row at `:37` and step 6 (`:879-889`)
  carry the frozen list with a one-line reason per scope; "What has to be
  approved" (`:966-991`) says what question 10 observed.
- The dated report with the answer table (one row per question, each cell
  "observed" with its fixture or "not observed" with why), the field table
  from question 9, and each answered bullet in `T-141` and `T-142` struck
  with the date and the answer.

**Out:**

- Registrants, the recurring-meeting container, registrant emails, the
  capacity loop and the daily cap (`T-099`), and the two on-demand recording
  registrant probes `T-099`'s step 17 named: `D-027` settled recordings on
  "Everyone with the recording link" plus the passcode, and no per-Peer grant
  for a recording is designed.
- Webhooks beyond observing: no endpoint, no `ZoomWebhook`, no signature
  check, no handling code (`D-027`: after publication, and only as a
  speed-up).
- Any code under `app/`, any `Http::fake()` test, any lang key. `ZoomClient`
  and `ZoomAccounts` are `T-141`'s, `FindsRecordings`, `SessionRecording`,
  `ZoomRecordings` and `ZoomMeetingLink` are `T-142`'s, the sweep and its
  backoff are `T-143`'s, review and Check now are `T-144`'s.
- The matching window, the ambiguity rules and the hold (`D-027`, `T-143`).
  The spike measures what those must survive; it does not choose them.
- Teams and Meet recordings: pasted links (`D-025`), no vendor call.
- The Marketplace submission, domain verification and the Technical Design
  section (`vendor-accounts.md`, steps 8 to 12): the owner's, prepared this
  sprint per `D-031`, informed by question 10.
- Buying the licence or opening the outside account: **Blocked on**.
- Any decision. A fact that leaves a choice is a bullet for the owner in
  `T-141` or `T-142`.

## Files

| Path                                                                                                                                                                                                                                                                                                                                                            | Change | Notes                                                                                                                                                                                                                               |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/Fixtures/zoom/README.md`                                                                                                                                                                                                                                                                                                                                 | new    | Shared with `T-099`; whichever lands first creates it. This spike's section, `## T-122 — recordings`: date, app, scope list, roster, redaction map, link shapes, processing times, one row per fixture, gap list                    |
| `tests/Fixtures/zoom/oauth/token.authorization_code.200.json`, `tests/Fixtures/zoom/oauth/token.refresh.200.json`                                                                                                                                                                                                                                               | new    | Only if this spike authorises the app before `T-099` runs: captured on the way to the bearer token under `T-099`'s redaction map (tokens `REDACTED`); read by `T-141`; `T-099`'s `token.refresh_reused.<status>.json` stays its own |
| `tests/Fixtures/zoom/recordings/get_meeting.latest.200.json`, `tests/Fixtures/zoom/recordings/list_instances.daily.200.json`, `tests/Fixtures/zoom/recordings/get_meeting.by_uuid.200.json`, `tests/Fixtures/zoom/recordings/get_meeting.by_uuid_encoded.<status>.json`, `tests/Fixtures/zoom/recordings/list_user.window.200.json`                             | new    | Question 1: which instance the meeting-id call returns, the instances list, an earlier instance by uuid, the one-call alternative; the encoded case only if such a uuid occurred                                                    |
| `tests/Fixtures/zoom/recordings/list_instances.restarted.200.json`, `tests/Fixtures/zoom/recordings/get_meeting.restarted.200.json`, `tests/Fixtures/zoom/recordings/get_meeting.paused.200.json`, `tests/Fixtures/zoom/recordings/list_instances.early_test.200.json`, `tests/Fixtures/zoom/recordings/get_meeting.early_test.200.json`                        | new    | Question 1, owner acceptance 8: a restarted meeting, several segments, an early test recording                                                                                                                                      |
| `tests/Fixtures/zoom/recordings/get_meeting.processing.<status>.json`, `tests/Fixtures/zoom/recordings/get_meeting.deleted.<status>.json`                                                                                                                                                                                                                       | new    | Question 2: the first answer after the end, and a recording in the trash (owner acceptance 9)                                                                                                                                       |
| `tests/Fixtures/zoom/recordings/settings.everyone_with_link.200.json`, `tests/Fixtures/zoom/recordings/settings.sign_in_to_zoom.200.json`, `tests/Fixtures/zoom/recordings/settings.on_demand.200.json`                                                                                                                                                         | new    | Question 3: the recording settings under each sharing mode                                                                                                                                                                          |
| `tests/Fixtures/zoom/recordings/get_meeting.after_sharing_change.200.json`                                                                                                                                                                                                                                                                                      | new    | Question 4: the links after the mode was switched                                                                                                                                                                                   |
| `tests/Fixtures/zoom/recordings/user_settings.pro.200.json`, `tests/Fixtures/zoom/recordings/user_settings.basic.<status>.json`, `tests/Fixtures/zoom/recordings/user_me.pro.200.json`, `tests/Fixtures/zoom/recordings/user_me.basic.<status>.json`                                                                                                            | new    | Question 5, read by `T-141`: `recording.cloud_recording` and the account identity on each plan; the Basic pair only once the share is granted                                                                                       |
| `tests/Fixtures/zoom/recordings/get_meeting.pmi.<status>.json`, `tests/Fixtures/zoom/recordings/get_meeting.vanity.<status>.json`, `tests/Fixtures/zoom/recordings/get_meeting.other_host.<status>.json`, `tests/Fixtures/zoom/recordings/get_meeting.no_fixed_time.<status>.json`, `tests/Fixtures/zoom/recordings/list_instances.no_fixed_time.<status>.json` | new    | Question 6: the links `T-142` must refuse or hold; the vanity case only with a vanity URL                                                                                                                                           |
| `tests/Fixtures/zoom/recordings/get_meeting.beta_install.<status>.json`, `tests/Fixtures/zoom/recordings/event_subscriptions.create.<status>.json`                                                                                                                                                                                                              | new    | Question 7: REST from the beta install; the subscription attempt only if made                                                                                                                                                       |
| `tests/Fixtures/zoom/recordings/get_meeting.auto_delete.200.json`                                                                                                                                                                                                                                                                                               | new    | Question 9: `auto_delete_date` with auto-delete on                                                                                                                                                                                  |
| `docs/planning/vendor-accounts.md`                                                                                                                                                                                                                                                                                                                              | edit   | `:787` gains the three tasks; `:37` and step 6 carry the frozen scope union with a reason per scope; "What has to be approved" says what question 10 observed                                                                       |
| `docs/planning/tasks/reports/T-122-YYYY-MM-DD-<owner>.md`                                                                                                                                                                                                                                                                                                       | new    | The answer table, the field table, the signed-out results per mode, per [`reports/README.md`](reports/README.md)                                                                                                                    |
| `docs/planning/tasks/T-141-a-creator-connects-the-zoom-account-they-already-have.md`                                                                                                                                                                                                                                                                            | edit   | Strike each bullet marked the spike's with the date and a one-line answer; a Notes line naming the report                                                                                                                           |
| `docs/planning/tasks/T-142-qori-finds-a-live-episodes-zoom-cloud-recording-from-the-spikes-fixtures.md`                                                                                                                                                                                                                                                         | edit   | The same, for questions 1, 2, 3, 6 and 9                                                                                                                                                                                            |
| `docs/planning/tasks/T-099-spike-zoom-recurring-meeting-registrants.md`                                                                                                                                                                                                                                                                                         | edit   | Scope spellings after question 8; its step 17, its `recordings/` fixture row and its `D-016` recordings-departure bullet struck with the date, pointing here; its README row takes the one-section-per-spike shape (Notes)          |
| `docs/planning/tasks/T-100-zoom-live-episodes-register-each-peer-once-per-series.md`                                                                                                                                                                                                                                                                            | edit   | Scope spellings after question 8, in `ZoomAccounts::SCOPES`                                                                                                                                                                         |

Flows: none — a spike writes fixtures and a report, no code.

## Database

None.

## Code

None. No PHP is written; the literal calls are under Scope, one per fixture,
so two people running the spike make the same ones.

## Copy

None.

## Routes

None.

## Tests

None — 0 cases. The fixtures are read by `T-141`'s tests
(`user_settings.*`, `user_me.*`) and `T-142`'s (`tests/Feature/Integrations/Zoom/ZoomRecordingsTest.php`,
every `get_meeting.*`, `list_instances.*` and `list_user.*` file); this task
writes no test.

**Changed:** none.

## Acceptance

- [ ] Every one of the ten questions has a row in the report's answer table,
      each "observed" with its fixture or "not observed" with why
- [ ] A person with no Zoom account and no relation to Qori's Zoom account, in
      a clean browser profile and on a phone with no Zoom app, opens a
      recording of the daily meeting signed out under "Everyone with the
      recording link", using only the link and passcode a fixture holds; the
      report says whether `?pwd=` alone did it, and what "Sign in to Zoom" and
      on-demand registration showed instead
- [ ] Every fixture in the Files table exists, or the README's gap list says
      why not; each is redacted by the map with `start_url` removed and the
      meeting id `91827405566`; the README states the date, the app, the scope
      list, the roster, and per file the call, the case, the status and the
      seconds
- [ ] The README's link-shape table lists every join-link shape met, with the
      meeting id each yields or none, and the processing-time table gives the
      minutes from scheduled end to the first `completed` file per occurrence
- [ ] The fixtures cover an early test recording, a restarted meeting and a
      recording in several segments (owner acceptance 8) and a deleted
      recording (owner acceptance 9), or the gap list says which could not be
      produced
- [ ] `vendor-accounts.md` carries the scope list once, in the console's exact
      spelling, and its "What has to be approved" section says what question
      10 observed about Request to Share (beta)
- [ ] Every bullet in `T-141` and `T-142` marked the spike's is struck with
      the date and a one-line answer
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The three items under **Blocked on**: the Pro month, the General app in
  development, and the beta share for one outside account — the owner's.
- Whether the outside-account half (questions 5 on Basic, 6's other host, 7
  and 10) runs inside the sprint on the beta share's stated turnaround, or as
  a second `S` spike once the share is granted, with the `qori-pro` half
  landing first — the owner's.
- Zoom's documented limits are plan- and account-wide and shared by every app
  installed on the account, which the storage review of 20 September 2026
  (`docs/planning/reviews/storage-2026-09-20-findings-codex.md`) read off Zoom's
  published API rate limits: on Pro, 30 requests a second for the light calls
  and 20 for the medium ones, with the heavy, resource-intensive calls drawing
  on one allowance of 30,000 a day. `T-142` costs its two-step read at "one
  MEDIUM-tier call" on no evidence, and this spike's README records the seconds
  per call and no tier, so the review asks that the tier Zoom gives
  `GET /meetings/{meetingId}/recordings`,
  `GET /past_meetings/{meetingId}/instances` and `GET /users/me/settings`, and
  the `Retry-After` and `X-RateLimit-*` headers each of them returns, be
  captured here rather than inferred — anyone's.
  **That file no longer exists and cannot be recovered**, so these bullets are
  the review itself, to be read as the primary source and not as a summary of
  something a reader can go and check; `docs/planning/reviews/README.md` has the
  whole of it.
- The same review's evidence table puts the REST `share_url`, the passcode and
  the expiry, the restarted session, the UUID encoding and personal-room
  detection on this spike, and states plainly that no Zoom response fixture
  exists anywhere in the repository, so every downstream mapping in `T-141` and
  `T-142` is a hypothesis until this runs (20 September 2026). The Why
  section's "`tests/Fixtures/` holds `planning/` and `reachability/` and
  nothing from any vendor" was true when it was written and is not now —
  `T-093` committed the Google bodies — so it is corrected in place to name
  `google/` and to say that what is missing is Zoom's — anyone's.

## Re-scope log

None.

## Notes

Written 17 September 2026 from `D-027` and `D-031`, beside `T-099`, which
keeps the registrant half of the Zoom account and the app this spike shares.

`T-099`'s draft is edited to strike its step 17 (recordings) and the
`tests/Fixtures/zoom/recordings/…` row in its Files table with today's date,
pointing here, to strike its "recordings departure from `D-016`" bullet as
answered by `D-027` (a stored link and passcode shown to every Peer with
access, no per-Peer grant), and to give its `tests/Fixtures/zoom/README.md`
row the shape the naming decision above fixes — one `##` section per spike,
`## T-099 — registrants` and `## T-122 — recordings`, each with its own date,
app, scope list, roster, redaction map and per-file rows — so the two spikes
write one file the same way whichever lands first. Its step 18 keeps the
`recording.completed` payload, because the endpoint is its. Those strikes and
the scope spellings question 8 corrects are why `T-099` and `T-100` are `edit`
rows in the Files table.

`T-141` and `T-142` are drafts written on 18 September 2026; each carries the
bullets this spike answers under "Before this can be ready", marked the
spike's. `T-142` reads questions 1, 2, 3, 6 and 9; `T-141` reads questions 5,
8 and 10, the `user_settings.*` and `user_me.*` fixtures and, if this spike
authorises the app first, the two `oauth/` fixtures.

Two things the spike may find that change a spec rather than a wording, each
a bullet for the owner in the task named: if `share_url` is absent and
`play_url?pwd=` does not open signed out, `T-142`'s `openUrl()` has no link a
Peer can follow and `D-027`'s "share link else play link" needs a third
answer (`→ T-142`); if the beta share cannot admit an outside creator,
`T-141`'s connect screen says review gates every creator, and the beta
creators the merged plan counted on for detection wait for publication
(`→ T-141`).

Zoom processes a recording in "approximately twice the recorded duration" and
"occasionally … up to 24 hours" (`docs/planning/course-classroom.md`, vendor
facts), so question 2's hourly polling can run into the next day for an
occurrence and the spike spans a working week of wall clock, most of it
waiting; the calls themselves are an afternoon.
