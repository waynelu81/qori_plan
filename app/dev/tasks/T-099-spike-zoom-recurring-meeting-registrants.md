---
id: T-099
title: Spike: Zoom recurring-meeting registrants
stream: storage
status: draft
owner: unassigned
estimate: S
depends: none
blocks: T-100
---

# T-099 — Spike: Zoom recurring-meeting registrants

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016`, the owner's BYO blueprint and a developer's review of the plan the
> same day, and revised on 17 September 2026 from `D-018`,
> which puts Zoom in the beta release.

## Why

`D-016` gives live sessions a container: one recurring fixed-time meeting per
Series, one registrant per Peer added with the creator's token, so a session
added later needs no new grant. Nobody at Qori has seen one of those responses.
`ConnectionProvider::Zoom` (`app/Enums/ConnectionProvider.php:18`),
`EpisodeProvider::Zoom` (`app/Enums/EpisodeProvider.php:23`) and
`EpisodeType::Live`, which allows Zoom and Teams
(`app/Enums/EpisodeType.php:35`), are the only mentions of Zoom under `app/`:
there is no `app/Integrations/Zoom`, the tag line at
`app/Providers/IntegrationServiceProvider.php:35` carries three media providers
and no Zoom class, `docs/flows/storage.md:98-104` lists Zoom join links under
"Not built yet", and `tests/Fixtures/` holds `google/` — `T-093`'s 66 bodies
and two header captures — beside `planning/` and `reachability/`, and nothing
from Zoom. `PROCESS.md` says a spec naming a vendor payload cites an observed
response or a committed fixture, so `T-100` cannot be `ready` until this runs.
Zoom ships in the beta release (`D-018`, 17 September 2026), so `T-100` is
release work and this spike sits on the path to it.

Four questions change `T-100`'s design rather than its wording. No primary
source says whether a registrant on a "register once, attend any occurrence"
meeting is carried into occurrences added **later** — if not, one grant per
Series does not hold and every new session is another add call against a cap of
three a day per Peer. Staff answers and forum threads disagree on whether the
returned `join_url` admits the Peer or sends them to the registration page.
Manual approval can leave the add-registrant response with no join URL at all,
so the approval mode is part of the promise. And the API spec puts the 4,999
registrant limit "per meeting" where the help centre says "per occurrence",
with error `3043` firing at "maximum attendee capacity" — which may mean room
size, 100 on Pro. Afterwards each is a fixture under `tests/Fixtures/zoom/` and
a dated answer struck into `T-100`.

## Decisions taken to make this specifiable

**Zoom is in the beta release, so this spike is scheduled rather than
conditional** (`D-018`, 17 September 2026). All seven providers ship before
beta, and that record amends `PLAN.md`'s rule 5 and its settled Zoom/Teams
line, so nothing here waits on a go-ahead and the Marketplace review sits on
the release path — which is why the scope list under Code is frozen before the
app is submitted, and why step 20 and question 21 record what the console asks
and what lead time it states.

**Every Zoom tier a creator can bring is offered with its limits stated, so
Basic is observed rather than quoted** (`D-018`). A tier is explained, never
refused: `T-100`'s tier entry has to say what a Basic account cannot do and
what Qori recommends instead, and step 15 makes that refusal a fixture in
Zoom's own status, code and message rather than a line taken from the help
centre. The room-size ceiling (step 14) and the registrant emails Zoom sends
anyway (steps 4 and 13) are the same kind of sentence, and each is owed an
observation.

**The spike calls the API from a shell and commits nothing under `app/`.** What
`T-100` needs is observed bodies; a class written before them would be written
twice.

**A private development app inside the spiker's own Pro account, with the
Marketplace question answered on paper.** A private app is authorised only by
members of the developer's own account, so a creator elsewhere needs a
published or unlisted app and a security review
([sharing private and beta apps](https://developers.zoom.us/docs/distribute/sharing-private-and-beta-apps/),
[review process](https://developers.zoom.us/docs/distribute/app-review-process/)).
The experiment does not need that; `T-100`'s launch does. So the spike freezes
the scope list in the report and records what the console asks, because adding
a scope later "will qualify for a complete security review"
([KB0058021](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0058021))
and Zoom publishes a 72-hour first-response SLA and no total timeline
([app review time](https://developers.zoom.us/blog/how-long-does-app-review-take/)).

**Automatic approval (`approval_type` 0) is the mode the spike proves; manual
approval is observed once, as a failure.** Priority 1 is working access right
after signing up, and Zoom's default is `approval_type` 2, no registration at
all ([api-hub](https://developers.zoom.us/api-hub/meetings/methods/endpoints.json)).
Manual approval leaves the registrant pending until the creator acts and is
reported to return no join URL, so it maps to `needs_creator` — the developer
review's ask, answered by choosing one mode and observing the other.

**The container is a recurring meeting with a fixed time (`type` 8) and
`registration_type` 1, and the later-occurrence question is this spike's reason
to exist.** Staff said in 2020 that an API registrant on a "register once"
meeting is added to all occurrences
([thread](https://devforum.zoom.us/t/recurring-meeting-registration/31395));
nothing covers occurrences added afterwards.

**`granted` means a Peer's clean browser reaching the session, never the
success status on Add registrant.** `T-091` makes every provider task say when
its grant is `granted`, and the review asks for API acceptance and usable
access to be told apart (the storage review of 20 September 2026; its findings
file is gone, and `docs/planning/reviews/README.md` says what became of it). So
the spike records the creator-token read that distinguishes them —
`GET /meetings/{id}/registrants`, whose `status` filter defaults to `approved`,
so a pending registrant is invisible to a naive lookup — beside the Peer's own
browser result for the same link.

**That same read is timed as the re-check of a `granted` row, and every call
is recorded as answering with a result or with a job to poll.** `T-091`
re-checks `granted` rows on a longer cadence (`checked_at`, provisional) and
Open reads the stored grant before trusting one, so current access is what is
verified rather than only first access — both need an observed call and its
seconds. The review also asks that asynchronous vendor operations be handled
where they exist; the spec shows none for these endpoints, so a fixture is
what says so.

**One recurring meeting per Series, and never the same meeting for two.** A
Zoom registrant belongs to the meeting rather than to an occurrence, so two
Series pointed at one meeting would let each Series' Peers into the other's
sessions and a single cancel would revoke both; step 8's registrant list is
what shows the list is meeting-wide. That matches `T-091`'s one grant row per
(Access, container). The sentence a creator reads when picking — that everyone
with access to the Series can join every session on that meeting, whether or
not it is an Episode — is `T-100`'s lang key, not this task's.

**Never re-add blind: every grant step is a list, then an add.** Add-registrant
is capped at three calls a UTC day per registrant per meeting, counted per call
and not per occurrence, and the next returns a 429 that locks that Peer out of
that meeting until 00:00 GMT
([rate limits](https://developers.zoom.us/docs/api/rate-limits/),
[staff thread](https://devforum.zoom.us/t/meeting-registration-cap-of-3-per-day-applies-even-with-different-occurrences/111827)).
`T-091`'s ensure step runs on every Series-page load, so a connector that
re-adds each pass would lock a Peer out by the third reload. The cap is
therefore measured deliberately, on a throwaway address.

**Registration capacity and simultaneous attendance are two questions, and only
the first is testable here.** Capacity is a scripted loop to room size plus one
(100 on Pro,
[KB0068002](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0068002));
whether `3043` fires there or at 4,999 decides whether a Series using Zoom needs
a Peer ceiling checked before checkout. Attendance is a hundred people in one
room at once, which no spike can stage: it stays a line in the tier copy.

**Recordings are their own link case.** The recording-registrant call takes a
meeting id and reaches only the latest instance; covering older ones by
instance UUID is a staff workaround the spec does not document. The spike makes
both calls and records which recording each returned `share_url` opens. It does
not choose between a stored link shown to Peers with access and one registrant
per recording per Peer — that is the owner's, in `T-100`.

**Zoom needs no Peer vendor identity, and the spike proves it rather than
assuming it.** Staff said a registrant may join with or without a Zoom account
unless the meeting requires authentication
([thread](https://devforum.zoom.us/t/you-can-add-any-email-if-using-add-meeting-registrants-api-even-only-authenticated-users-can-join-is-selected/23813)),
so `T-092` is not a dependency of `T-100` and a Zoom grant never answers
`awaitingIdentity()`. Every Peer here is a plain mailbox with no Zoom account,
and `meeting_authentication` is read and reported because turning it on
reverses that.

**The reconciliation triggers are observed as facts, not designed here.**
`T-091` re-runs grants when the creator reconnects the same account, marks
containers for a new pick when a different account is connected, and re-grants
when a container is replaced. What Zoom does in each is a fixture: a re-linked
token reaching the same meeting id; a second account's token reading it; a
cancelled registrant re-added.

**Every call is timed, and `start_url` is deleted rather than redacted.** The
wall time is what `VendorAccessService::REQUEST_TIMEOUT_SECONDS` (`T-091`,
provisional 5) is checked against. `start_url` starts the meeting as host, so
it is removed with a `"start_url": "REMOVED"` marker rather than given a
placeholder that invites a reader to look for the real one.

**One fixture per call and case, the raw body, named
`<group>/<call>.<case>.<status>.json`** (provisional — see below), with
status-only captures as `.txt`. `T-093` and `T-097` name flat files under the
vendor directory; `T-095` names this shape. Whichever spike lands first sets the
convention and the others rename, which is a wording change.

**Answers go into `T-100`, not `decisions.md`.** A spike learns facts. The one
thing facts cannot settle — the recordings departure from `D-016`'s step 3 — is
a bullet for the owner in `T-100` and in the report, tagged `→ T-100`. Whether
Zoom ships at all is not among them any more (`D-018`).

## Preconditions

`T-100` is a drafted task file whose "Before this can be ready" bullets already
name the questions below and mark them `T-099`'s; the answers are struck into
those bullets. Nothing else in the repository is needed, and nothing else in it
changes.

**Data this task verifies against:** nothing in Qori's database. Everything is
in Zoom: one recurring weekly meeting with three occurrences in the Pro
account, its first occurrence at least a day out so steps 6 and 7 run before it
starts; one throwaway meeting in the same account for the capacity loop; one
meeting in the Basic account for the refusal; one in a second Zoom account for
the different-account read.

**Equipment** (provisional — the licences are the owner's to approve, see
below):

- A **Zoom Workplace Pro** licensed host. Basic cannot register at all, which
  is the limit the Basic tier entry states and step 15's fixture observes.
- A **Basic** account for the `3161` refusal and, if available, a **Business**
  account with more than one user for the admin pre-approval screen, on by
  default on multi-user accounts
  ([KB0062300](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0062300)).
- A **user-managed General app** in the Pro account's own Marketplace, in
  development, with the scopes listed under Code and a redirect URI the spiker
  can read (`http://localhost` is enough for a hand-made code exchange).
- **Peers with no Zoom account**: `peer-first` and `peer-second`, each a
  mailbox the spiker reads, plus a plus-addressed or catch-all domain for the
  cap and capacity loops (`spike+NNN@…`).
- A fresh browser profile per Peer, a phone with the Zoom app, a stopwatch,
  `curl` and `jq`.
- Optional, for step 18: a public HTTPS endpoint that can log a webhook.
  Without one that step is "not run" and `T-100` polls.

## Scope

**In:**

- Every call under Code, run as the account named, each body committed as a
  fixture with its status in the file name and its seconds in the README row.
- Every error met — `429` for the daily cap and for the plan limit, `3043`,
  `3161`, `1001`, `3000`, and a `401` on a revoked token — written beside the
  `VendorGrantStatus` it maps to and who resolves it.
- What a Basic host is refused, observed rather than quoted: Basic is offered
  with its limit stated before a creator connects (`D-018`), so step 15's
  `3161` is evidence for that tier entry as much as an error row.
- The creator-token evidence that tells an approved registrant from a pending
  one, beside the Peer's own browser result for the same link.
- The same read timed again as the re-check a `granted` row gets on `T-091`'s
  longer cadence, with whether it carries each registrant's `join_url` — which
  is what Open re-reads before it trusts a granted row.
- The Peer journey walked again under exactly the scopes `T-100` will request:
  first access, a session added later, a repeated grant and one recoverable
  failure, each timed.
- The dated report with the answer table below, and each answered bullet in
  `T-100` struck with the date and the answer.

**Out:**

- Any code under `app/`, any `Http::fake()` test, any lang key. The tier copy
  and Peer-facing sentences are `T-100`'s, Open is `T-089`'s, connect and the
  token-refresh command are `T-044`'s.
- The grant model, the ensure step, the six states, the retry rule, the
  re-check cadence and `qori:access:reconcile` (`T-091`). The spike measures
  what those numbers must survive; it does not choose them.
- Teams (`T-101`), which stores a pasted link; the Webinars add-on, which
  mirrors these endpoints; Zoom Events and Webinars Plus, unassessed.
- The Peer's vendor identity (`T-092`): Zoom needs none, and step 6 proves it.
- The money path. A paid Series on Zoom waits on `T-102` and `T-103`, which
  keep fulfilment replayable when grant state cannot be saved; nothing here
  touches or tests it.
- Any decision. A fact that leaves a choice is a bullet for the owner in
  `T-100` — or for `T-091`'s owner where it changes the grant model.

## Files

| Path                                                                                                                                                                                                                                                                                                                                                                                                                                    | Change | Notes                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------- |
| `tests/Fixtures/zoom/README.md`                                                                                                                                                                                                                                                                                                                                                                                                         | new    | Date, app, scope list, account roster, redaction map; per file: call, status, seconds                   |
| `tests/Fixtures/zoom/oauth/token.authorization_code.200.json`, `tests/Fixtures/zoom/oauth/token.refresh.200.json`, `tests/Fixtures/zoom/oauth/token.refresh_reused.<status>.json`                                                                                                                                                                                                                                                       | new    | Tokens `REDACTED`; the third only if the old refresh token is refused                                   |
| `tests/Fixtures/zoom/meetings/create.recurring.<status>.json`, `tests/Fixtures/zoom/meetings/get.200.json`, `tests/Fixtures/zoom/meetings/list.200.json`                                                                                                                                                                                                                                                                                | new    | The container as created and read back; the list `T-100`'s picker reads                                 |
| `tests/Fixtures/zoom/meetings/patch.emails_off.<status>.txt`, `tests/Fixtures/zoom/meetings/get.emails_off.200.json`                                                                                                                                                                                                                                                                                                                    | new    | Status and headers of the empty PATCH, then whether each setting stuck                                  |
| `tests/Fixtures/zoom/meetings/patch.add_occurrence.<status>.txt`, `tests/Fixtures/zoom/meetings/get.four_occurrences.200.json`, `tests/Fixtures/zoom/meetings/patch.reschedule_occurrence.<status>.txt`                                                                                                                                                                                                                                 | new    | The later-occurrence question, and the reschedule community reports say breaks links                    |
| `tests/Fixtures/zoom/meetings/patch.required_question.<status>.txt`, `tests/Fixtures/zoom/meetings/patch.registration_off.<status>.txt`, `tests/Fixtures/zoom/meetings/get.after_breakers.200.json`, `tests/Fixtures/zoom/meetings/get.other_account.<status>.json`                                                                                                                                                                     | new    | The two documented breakers; and a second account's token on the stored meeting id                      |
| `tests/Fixtures/zoom/registrants/create.first.<status>.json`, `tests/Fixtures/zoom/registrants/create.second.<status>.json`, `tests/Fixtures/zoom/registrants/create.repeat.<status>.json`, `tests/Fixtures/zoom/registrants/create.after_cancel.<status>.json`                                                                                                                                                                         | new    | The grant, the mid-session grant, idempotency, and the restored-access case                             |
| `tests/Fixtures/zoom/registrants/create.rate_limited.429.json`, `tests/Fixtures/zoom/registrants/create.capacity.3043.<status>.json`, `tests/Fixtures/zoom/registrants/create.host_not_allowed.3161.<status>.json`, `tests/Fixtures/zoom/registrants/create.meeting_missing.1001.<status>.json`, `tests/Fixtures/zoom/registrants/create.no_access.3000.<status>.json`, `tests/Fixtures/zoom/registrants/create.invalid_token.401.json` | new    | Each exists only if that error was met; the README lists the gap                                        |
| `tests/Fixtures/zoom/registrants/list.approved.200.json`, `tests/Fixtures/zoom/registrants/list.pending.200.json`, `tests/Fixtures/zoom/registrants/list.denied.200.json`, `tests/Fixtures/zoom/registrants/list.occurrence.200.json`, `tests/Fixtures/zoom/registrants/list.after_cancel.200.json`                                                                                                                                     | new    | What `T-100`'s look-before-add and `checkGrant()` read                                                  |
| `tests/Fixtures/zoom/registrants/create.manual_approval.<status>.json`, `tests/Fixtures/zoom/registrants/status.approve.<status>.txt`, `tests/Fixtures/zoom/registrants/status.cancel.<status>.txt`, `tests/Fixtures/zoom/registrants/delete.<status>.txt`                                                                                                                                                                              | new    | The mode Qori does not use, observed once; and the two revoke shapes                                    |
| `tests/Fixtures/zoom/recordings/get_meeting.200.json`, `tests/Fixtures/zoom/recordings/list_user.200.json`, `tests/Fixtures/zoom/recordings/settings.get.200.json`, `tests/Fixtures/zoom/recordings/settings.patch.<status>.txt`, `tests/Fixtures/zoom/recordings/registrants.create.by_meeting_id.<status>.json`, `tests/Fixtures/zoom/recordings/registrants.create.by_uuid.<status>.json`                                            | new    | The recordings case; the two registrant calls are probes, not a design                                  |
| `tests/Fixtures/zoom/webhooks/meeting.updated.json`, `tests/Fixtures/zoom/webhooks/meeting.deleted.json`, `tests/Fixtures/zoom/webhooks/recording.completed.json`                                                                                                                                                                                                                                                                       | new    | Only with a public endpoint (step 18); otherwise the README records the gap                             |
| `docs/planning/tasks/reports/T-099-YYYY-MM-DD-<owner>.md`                                                                                                                                                                                                                                                                                                                                                                               | new    | The answer table and the states table, per [`reports/README.md`](reports/README.md)                     |
| `docs/planning/tasks/T-100-zoom-live-episodes-register-each-peer-once-per-series.md`                                                                                                                                                                                                                                                                                                                                                    | edit   | Strike each bullet marked `T-099`'s with the date and a one-line answer; a Notes line naming the report |

Flows: none — nothing under `app/` or `routes/` changes; `T-091` writes
`docs/flows/vendor-access.md` and `T-100` edits it.

## Database

None.

## Code

No PHP. The literal calls, so two people running the spike make the same ones.
Paths and field names are the API spec's
([api-hub endpoints](https://developers.zoom.us/api-hub/meetings/methods/endpoints.json),
[Meetings API](https://developers.zoom.us/docs/api/meetings/)); **no response
field named below is observed until its fixture exists**, and the status and
the body around an error code are what the fixture records, not what this task
states.

Scopes requested, user-level granular, frozen before the app is submitted
([granular scopes](https://developers.zoom.us/docs/integrations/oauth-scopes-granular/)):
`meeting:read:list_meetings`, `meeting:read:meeting`, `meeting:update:meeting`,
`meeting:write:registrant`, `meeting:read:list_registrants`,
`meeting:update:registrant_status`, `meeting:delete:registrant`,
`cloud_recording:read:list_user_recordings`,
`cloud_recording:read:list_recording_files`,
`cloud_recording:read:recording_settings`,
`cloud_recording:update:recording_settings`,
`cloud_recording:write:recording_registrant`,
`cloud_recording:update:registrant_status`.

Redaction is a fixed map, not judgement: `access_token`, `refresh_token` and any
`Authorization` header become `REDACTED`; `start_url` becomes `REMOVED`;
`host_id`, `host_email`, `account_id` and `uuid` keep their shape and take a
stable placeholder; the meeting id becomes one fixed 11-digit placeholder used
everywhere; `pwd` and `tk` query values inside a `join_url` or `share_url`
become `REDACTED` with the parameter names kept; Peer emails become the role
names above at `example.test`. Everything else — every `code`, `message`,
`status`, `registrant_id`, `occurrence_id`, `Retry-After` and `X-RateLimit-*`
header — stays verbatim. The map lives in the fixture README as placeholder →
role.

```bash
API=https://api.zoom.us/v2
# $T is the access token of the account each step names. -i keeps the status
# line and headers (Retry-After, X-RateLimit-*) in the capture; -w appends the
# wall time for the README row. The fixture is the body alone, redacted.
z() { curl -sS -i -w '\ntime_total=%{time_total}\n' -X "$1" "$API$2" \
  -H "Authorization: Bearer $T" -H 'Content-Type: application/json' ${3:+-d "$3"}; }
```

1. **Token, Pro account.** Authorise at
   `https://zoom.us/oauth/authorize?response_type=code&client_id=$ZOOM_CLIENT_ID&redirect_uri=$REDIRECT`,
   exchange the code at `POST https://zoom.us/oauth/token` with
   `grant_type=authorization_code` → `oauth/token.authorization_code.200.json`.
   Record `expires_in`, whether a `refresh_token` and `scope` come back, and
   that there is no separate offline scope
   ([OAuth](https://developers.zoom.us/docs/integrations/oauth/)).
2. **Refresh twice, reuse the old one.** `grant_type=refresh_token` twice →
   `oauth/token.refresh.200.json`, then retry the first refresh token →
   `oauth/token.refresh_reused.<status>.json`. Whether it is refused decides
   whether `T-044`'s `qori:connections:refresh` needs a per-connection lock.
3. **Create the container.** `z POST /users/me/meetings` with `"type": 8`, a
   weekly `recurrence` of three occurrences and `"settings": {"approval_type":
0, "registration_type": 1, "waiting_room": true, "join_before_host": false}`
   → `meetings/create.recurring.<status>.json`. Record the status, `id`, every
   `occurrences[].occurrence_id`, `registration_url`, and the returned
   `settings` including `meeting_authentication`,
   `registrants_confirmation_email` and `registrants_email_notification`.
4. **Emails off.** `z PATCH /meetings/{id}` with those two `false` →
   `meetings/patch.emails_off.<status>.txt`, then `z GET /meetings/{id}` →
   `meetings/get.emails_off.200.json`. A 2020 thread says the confirmation
   email cannot be set false at creation while the notification switch
   suppresses it
   ([thread](https://devforum.zoom.us/t/registrants-confirmation-email-vs-registrants-email-notification/12113));
   record which stuck.
5. **The picker's list.** `z GET '/users/me/meetings?type=scheduled&page_size=30'`
   → `meetings/list.200.json`. Record which fields the list carries and which
   need a per-meeting `GET`: `T-100`'s picker must check `type`,
   `approval_type`, `registration_type`, the occurrence count and the required
   questions before a creator can choose a meeting.
6. **Grant, `peer-first`.** `z POST /meetings/{id}/registrants` with
   `{"email": "peer-first@example.test", "first_name": "Peer", "last_name":
"One"}` and no `occurrence_ids` → `registrants/create.first.<status>.json`.
   Record the status, `registrant_id`, `join_url`, `start_time`, `topic` and
   the seconds. Start the stopwatch.
7. **Open the join link.** A fresh browser profile, not signed in to Zoom:
   open `join_url` before the first occurrence, then while it is live; stop the
   stopwatch at the first successful entry. Record whether it admits directly,
   lands on the registration page or asks for a Zoom sign-in, with the waiting
   room on and then PATCHed off, and repeat once on the phone. Then add
   `peer-second` mid-session → `registrants/create.second.<status>.json` and
   open theirs. This is what the `tk`-token threads leave open
   ([join_url](https://devforum.zoom.us/t/zoom-registration-and-registrant-join-url/53163),
   [registration page](https://devforum.zoom.us/t/zoom-join-url-sends-registrant-to-registration-url/16645)).
8. **The list, each status.** `z GET '/meetings/{id}/registrants?status=approved&page_size=300'`,
   the same for `pending` and `denied`, then `?occurrence_id=<first>` → four
   fixtures. Record that the filter defaults to `approved`, the trap a
   look-before-add has to avoid. Time the call twice — once as that lookup and
   once as the re-check a `granted` row gets on `T-091`'s longer cadence — and
   record whether the list carries each registrant's `join_url`, whether it
   holds every Series' Peers on that meeting, and whether any call here answers
   with a job to poll rather than a result.
9. **The cap, on a throwaway address.** Add `spike+cap@…`, then twice more,
   then once past it → `registrants/create.repeat.<status>.json` for the second
   (same `registrant_id` and link, or an error) and
   `registrants/create.rate_limited.429.json` for the refusal. Record the
   message, any `Retry-After`, and — probing hourly with one call — when it
   resets against the documented 00:00 GMT.
10. **Later occurrences.** `z PATCH /meetings/{id}` extending `recurrence` to
    four → `meetings/patch.add_occurrence.<status>.txt`, `z GET /meetings/{id}`
    → `meetings/get.four_occurrences.200.json`, then `?occurrence_id=<fourth>`
    on the registrant list, and open `peer-first`'s step 6 `join_url` for
    occurrence 4. **This decides whether one grant per Series holds for Zoom.**
11. **Reschedule.** `z PATCH '/meetings/{id}?occurrence_id=<second>'` with a new
    `start_time` → `meetings/patch.reschedule_occurrence.<status>.txt`, then
    change the whole series' time. Re-open `peer-first`'s link after each and
    re-list. Only community reports say this breaks links
    ([thread](https://community.zoom.com/meetings-2/meeting-url-not-working-when-rescheduling-occurrence-of-a-repeating-meeting-35706)).
12. **Breakers.** Make one registration question required, re-open the link and
    re-list → `meetings/patch.required_question.<status>.txt`. Then set
    `approval_type` to 2, re-open, set it back to 0 and re-list →
    `meetings/patch.registration_off.<status>.txt` and
    `meetings/get.after_breakers.200.json`: is the registrant list restored
    ([KB0065026](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065026),
    [KB0065196](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065196))?
13. **Manual approval, once.** PATCH `approval_type` to 1, add a fresh address →
    `registrants/create.manual_approval.<status>.json`: is a `join_url` present,
    and what does it do in a browser? List `status=pending`, then
    `z PUT /meetings/{id}/registrants/status` with `{"action": "approve",
"registrants": [{"id": "…", "email": "…"}]}` →
    `registrants/status.approve.<status>.txt`, and record whether Zoom emailed
    the registrant. Set `approval_type` back to 0.
14. **Capacity.** On the throwaway meeting, script adds of `spike+NNN@…`, one
    address per call, at most two a second (Pro's Medium label allows 20/s), to
    room size plus one — 101 on Pro. Record whether `3043` fires at 100 →
    `registrants/create.capacity.3043.<status>.json`, or whether 101 succeed and
    the ceiling is the spec's 4,999.
15. **The refusals Qori must map.** As the Basic host, create a meeting with
    registration and add a registrant → expect `3161`. Add against a deleted
    meeting id → `1001`. Revoke the token (`POST https://zoom.us/oauth/revoke`)
    and add again → the `401`. With a second Zoom account's token,
    `z GET /meetings/{id}` on the Pro account's meeting →
    `meetings/get.other_account.<status>.json` (`3000` or `1001`), which is what
    `T-091` sees when a creator connects a different account.
16. **Revoke.** With `peer-first` in a live occurrence,
    `z PUT /meetings/{id}/registrants/status` with `{"action": "cancel", …}` →
    `registrants/status.cancel.<status>.txt`: are they dropped, and what does
    the link do in a fresh browser? Then
    `z DELETE /meetings/{id}/registrants/{registrantId}` on `peer-second` →
    `registrants/delete.<status>.txt`, re-list →
    `registrants/list.after_cancel.200.json`, and re-add `peer-first` →
    `registrants/create.after_cancel.<status>.json`. Reports say a status change
    can answer 204 and leave the status unchanged
    ([thread](https://devforum.zoom.us/t/update-meeting-registrant-not-actually-cancelling/12770)),
    so the list is the evidence, not the status code.
17. **Recordings.** Cloud-record two occurrences.
    `z GET /meetings/{id}/recordings` → `recordings/get_meeting.200.json`
    (does only the latest instance come back?) and
    `z GET '/users/me/recordings?from=…'` → `recordings/list_user.200.json`,
    with each instance's `uuid`, `share_url` and passcode.
    `z GET /meetings/{id}/recordings/settings` and a PATCH with
    `{"on_demand": true, "approval_type": 0}` → two fixtures. Then
    `z POST /meetings/{id}/recordings/registrants` once by meeting id and once
    by instance UUID → two fixtures; open each returned `share_url` in a clean
    browser and record which recording it opens. Trim one recording and confirm
    its link is unchanged
    ([KB0067514](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0067514),
    [KB0065362](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065362),
    [KB0067567](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0067567)).
18. **Webhooks, only with a public endpoint.** Subscribe the development app to
    `meeting.updated`, `meeting.deleted` and `recording.completed`, repeat a
    PATCH, delete the throwaway meeting and finish a recording → three payload
    fixtures. Record whether `recording.completed` carries `share_url` and the
    passcode per instance. Without an endpoint this is "not run" and `T-100`
    polls.
19. **The walkthrough under `T-100`'s scopes.** Re-authorise with exactly the
    scope list above and nothing wider, then, each timed: (a) list, then add a
    fresh Peer; (b) that Peer opens the session in a clean browser with no Zoom
    account; (c) the creator adds a fifth occurrence and the same Peer opens it;
    (d) the grant repeated as `T-091`'s ensure step would repeat it — list
    first, add only if absent — confirming no add call was spent; (e) the
    recoverable failure: revoke the token, attempt the grant, re-link the same
    account, repeat the grant on the same meeting id and record that it
    succeeds. A step that only a wider scope got through is a finding.
20. **Admin pre-approval, only with a Business account.** Attempt the authorise
    as a member of the multi-user account and record the exact screen and
    wording, and whether an admin can approve an app still in development.

The report's **Outcome** is this table, one row per question, each cell
"observed" with its fixture or "not observed" with why:

| #   | Question                                                                            | Decides in `T-100`                                                   |
| --- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1   | Does a registrant carry into an occurrence added later, and does the old link work? | One grant per Series, or one per occurrence                          |
| 2   | Does the returned `join_url` admit a Peer with no Zoom account, before and during?  | When a grant is `granted`, and what Open redirects to                |
| 3   | The same for a Peer added mid-session                                               | Whether priority 1 holds for a late buyer                            |
| 4   | Does a repeat add return the same id and link, and does it spend one of the three?  | Whether the ensure step must list before every add                   |
| 5   | The cap: the 429 body, any `Retry-After`, the observed reset                        | Zoom's retry rule against `next_attempt_at`                          |
| 6   | Manual approval: is a `join_url` returned, and where does the Peer land?            | The `needs_creator` row for a meeting Qori cannot fix                |
| 7   | Do the two registrant email settings stick, and when?                               | Whether `D-016`'s "notification off" holds for Zoom                  |
| 8   | Rescheduling one occurrence, and changing the series time                           | What the creator is told never to do                                 |
| 9   | A required question, and registration off then on: is the list restored?            | The breakers in the tier copy, and what the scheduled check watches  |
| 10  | Does `3043` fire at room size or at 4,999?                                          | Whether a Zoom Series needs a Peer ceiling checked before payment    |
| 11  | `3161`, `1001`, `3000`, `401`: status, code and message for each                    | The error-to-state mapping and the creator's sentence                |
| 12  | A second account's token reading the stored meeting id                              | `T-091`'s "connected a different account" trigger                    |
| 13  | Cancel and delete: the running session, the link afterwards, the two lists          | What `revoked` is checked against, and which call revoke uses        |
| 14  | Re-adding a cancelled registrant                                                    | The restored-access path                                             |
| 15  | Meeting recordings versus user recordings, per instance                             | Whether recordings list without polling per instance                 |
| 16  | The two recording-registrant calls: which recording each `share_url` opens          | Whether recordings keep a per-Peer grant at all                      |
| 17  | Does `recording.completed` carry `share_url` and passcode per instance?             | Webhook or scheduled poll                                            |
| 18  | Is the old refresh token refused after a refresh?                                   | Whether the refresh command needs a per-connection lock              |
| 19  | Which fields the meeting list returns, and what PICK needs a second call for        | The picker's check, and how many calls it costs                      |
| 20  | Seconds per call, and the stopwatch from grant to first join                        | `REQUEST_TIMEOUT_SECONDS` against Zoom, and when to say `pending`    |
| 21  | The Marketplace console: what review asks, any lead time, the admin-approval screen | `release-prerequisites.md:20`, and whether Business creators connect |
| 22  | The walkthrough: first access, a later session, a repeat, a recovery                | The release check `T-100` cites                                      |
| 23  | What a re-check of a `granted` row reads, and whether the list carries `join_url`   | The `checked_at` cadence, and what Open re-reads before trusting     |
| 24  | Does any call answer with a job to poll rather than a result?                       | Whether a Zoom grant is ever asynchronous                            |
| 25  | What a Basic host is refused, in Zoom's own words                                   | The Basic tier entry's stated limit, and its recommendation          |

The report's **States** table reads the same rows the other way: each outcome,
its fixture, the `VendorGrantStatus` it maps to and who resolves it. The mapping
below is the candidate, in `T-091`'s vocabulary; a fixture confirms or corrects
each line and `T-100` states the final one.

| Outcome                                                                  | Candidate state       | Resolves                                         |
| ------------------------------------------------------------------------ | --------------------- | ------------------------------------------------ |
| Add succeeds under `approval_type` 0 and the link admits a clean browser | `granted`             | —                                                |
| Add succeeds but the link lands on the registration page                 | `awaiting_acceptance` | The Peer, by registering — and `T-100` changes   |
| `429` daily cap for that registrant                                      | `pending`             | Nobody; the next trigger retries after 00:00 GMT |
| `429` plan rate limit, a timeout, or a 5xx                               | `pending`             | Nobody; `Retry-After` where sent                 |
| `3043` capacity                                                          | `needs_creator`       | The creator, by a bigger plan or another meeting |
| `3161` host not licensed (a plan dropped to Basic)                       | `needs_creator`       | The creator, by restoring the licence            |
| `1001` meeting does not exist, `3000` cannot access meeting info         | `needs_creator`       | The creator, by picking the meeting again        |
| `401` on the creator's token                                             | `needs_creator`       | The creator, by reconnecting                     |
| Registration turned off, or a question made required                     | `needs_creator`       | The creator, by restoring the setting            |
| A re-check finds a `granted` registrant gone from every list             | `pending`             | Nobody; the next ensure re-adds, inside the cap  |
| Cancel or delete confirmed by the registrant list                        | `revoked`             | —                                                |

`awaiting_identity` has no Zoom row: a registrant needs only an email, so a Zoom
grant never waits on `T-092`. If `meeting_authentication` is on, that is a
`needs_creator` row rather than a Peer step, because Qori can read the setting
and the Peer cannot change it.

## Copy

None. This spike ships no string. The facts feed `T-100`'s tier bullets, its
picker sentence and its Peer-facing state sentences, and that task owns every
lang key and the file it goes in. `D-018` makes those tier bullets state each
tier's limits and what Qori recommends beside them, so the spike owes `T-100`
the observation behind each one — what a Basic host is refused (step 15), where
registration stops (step 14), and which emails Zoom sends anyway (steps 4 and 13) — while defining no key and writing no sentence itself. It owes them the
States table too: each non-granted state names who can resolve it, and because
only `pending` may be described as needing nothing from the person, an outcome
the Peer or the creator has to act on is never recorded as `pending` here.

## Routes

None.

## Tests

None. The fixtures are read by `T-100`'s tests; this task writes no test.

## Acceptance

- [ ] Every fixture in the Files table exists, or the README's gap list says
      which case was not met and why; each body is verbatim under the redaction
      map, with `start_url` removed, and the README states the date, the app,
      the scope list, the account role, the status and the seconds per file
- [ ] Every row of the answer table is "observed" with its fixture or "not
      observed" with the reason, and every row of the States table names the
      fixture that confirms or corrects its candidate state
- [ ] Question 1 is answered either way in the report — a registrant carried
      into a later occurrence, or not — because `T-100`'s container rests on it
- [ ] The report says what a Basic host is refused, with its fixture, what the
      capacity loop stopped at, and which registrant emails Zoom sent anyway,
      so `T-100`'s tier entries can state each limit and its recommendation
- [ ] The walkthrough (step 19) is in the report with its seconds, and any step
      that only a wider scope got through is a finding
- [ ] The report records what the Marketplace console asks of a user-managed
      General app with these scopes, any lead time it states, and the
      multi-user admin-approval screen
- [ ] Every bullet in `T-100`'s "Before this can be ready" marked `T-099`'s is
      struck with the date and a one-line answer, and a Notes line there names
      the report; any choice the facts leave the owner is written there as a
      bullet for the owner, and a change to the grant model as a bullet for
      `T-091`'s
- [ ] Every "Found, not fixed" bullet in the report ends in a disposition
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Whether Zoom enters before beta at all. `PLAN.md` rule 5 and its settled
  line defer broad Zoom/Teams work, and the open decision in `decisions.md`
  recommends Zoom after beta unless a representative creator runs live
  sessions; until it is taken this spike is worth running early only for the
  Marketplace lead time — the owner's.~~ **Answered 17 September 2026
  (`D-018`):** Zoom is in the beta release with the other six providers, and
  that record amends `PLAN.md`'s rule 5 and its Zoom/Teams line. The spike runs
  in the `storage` stream's order, and the Marketplace lead time is now
  something the release date has to absorb rather than the only reason to run
  this early.
- Whether to pay for a Zoom Workplace Pro licence, and on whose card; and
  whether a Business account with more than one user is available for step 20,
  or that step is "not run" — the owner's.
- Whether the spike may open the Marketplace submission now. The scope list must
  be final first, because adding one later triggers a complete re-review, and
  the total review time is unpublished — the owner's.
- Whether storing `registrant_id` and `join_url` per Peer is allowed under
  Zoom's API terms, which forbid building databases or copies of API data; the
  section number is unsettled (the owner cites §3.4; fetches rendered 3.4,
  3.7(m) and 3.2.7.13) and the answer is confirmed with Zoom at review
  ([API terms](https://www.zoom.com/en/trust/legal/zoom-api-license-and-tou/))
  — the owner's.
- Whether the owner accepts the recordings departure from `D-016`'s step 3 — a
  stored `share_url` and passcode shown to Peers with access, no per-Peer grant
  — if step 17 shows the per-instance call is undocumented or unreliable.
  Carried into `T-100` either way — the owner's.
- Whether the capacity loop (step 14, about 101 add calls) and the cap-reset
  probe (step 9, up to 24 hours of wall clock) stay in an `S`, or move to
  `T-100`'s first week on a throwaway account — anyone's.
- Whether step 18 is in scope, which needs a public HTTPS endpoint to point Zoom
  at, or whether webhooks wait for `T-100` — anyone's.
- The fixture naming convention: `T-093` and `T-097` name flat files under the
  vendor directory, this draft and `T-095` name
  `<group>/<call>.<case>.<status>.json`; whichever spike lands first sets it and
  the others rename — anyone's.
- Whether the Webinars add-on gets its own spike: it mirrors these endpoints
  with the same caps, but a one-off webinar's id stops working at its scheduled
  end, so a Peer who gets access afterwards has no link — the owner's.
- Zoom's documented limits are plan- and account-wide and shared by every app
  installed on the account, which the storage review of 20 September 2026
  (`docs/planning/reviews/storage-2026-09-20-findings-codex.md`) read off Zoom's
  published API rate limits: on Pro, 30 requests a second for the light calls
  and 20 for the medium ones, with the heavy calls drawing on one allowance of
  30,000 a day, and registration limited separately to three requests per
  registrant per meeting per UTC day and ten for a status change. Step 9
  measures the three. The ten allowed for a status change is a second cap that
  steps 13 and 16 spend against and that this task records nowhere, and the
  review asks that the tier Zoom labels each endpoint with, and the real
  `Retry-After` and `X-RateLimit-*` headers, be captured here rather than taken
  from the documentation — anyone's.
  **That file no longer exists and cannot be recovered**, so these bullets are
  the review itself, to be read as the primary source and not as a summary of
  something a reader can go and check; `docs/planning/reviews/README.md` has the
  whole of it.
- The scan before an add is not one call. The same review notes that the
  expensive read is every registrant page and every status, so step 8's timing
  has to cover the approved, pending and denied reads together, with whatever
  pagination a meeting near its ceiling forces, rather than one
  `page_size=300` read reported as the whole cost of the look-before-add rule
  `T-100` rests on (20 September 2026) — anyone's.
- The same review's evidence table puts future occurrences, the returned join
  links, the caps, cancellation and OAuth rotation on this spike and `T-122`,
  and states plainly that no Zoom response fixture exists anywhere in the
  repository, so every mapping `T-100`, `T-141` and `T-142` take from Zoom's
  reference is a hypothesis until both have run (20 September 2026). The Why
  section's "`tests/Fixtures/` holds `planning/` and `reachability/` and
  nothing from any vendor" was true when it was written and is not now —
  `T-093` committed the Google bodies — so it is corrected in place to name
  `google/` and to say that what is missing is Zoom's — anyone's.

## Re-scope log

None.

## Notes

The two research digests disagree on the unit of a Zoom grant: one registers per
scheduled meeting, the other uses one recurring meeting per Series with
"register once, attend any occurrence". `D-016` took the container and this
spike tests it. If question 1 comes back negative, Zoom needs one add call per
Peer per occurrence against a cap of three a day, which is a bullet for
`T-091`'s owner about the grant model as much as a change to `T-100`.

Two limits shape a Series before any code does, and `T-100`'s tier copy states
both: a recurring meeting holds at most 60 occurrences, and a meeting id expires
365 days after an occurrence was last started
([KB0064248](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0064248),
[KB0065196](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065196)).
A weekly Series past about sixty weeks needs a new meeting and every Peer
re-registered. Neither is spiked — both are read from the help centre — but they
are why the scheduled check `T-100` adds reads the occurrence count and the last
start. A creator whose plan drops to Basic loses the grant silently, and their
cloud recordings become inaccessible and are deleted after 30 days
([KB0063923](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0063923)),
so step 15's `3161` fixture is what the connector has to recognise.

Zoom's own emails to registrants cannot be suppressed for a meeting update: the
settings are meeting-wide rather than per call, and the claim rests on a 2019
staff answer. `T-100`'s tier copy says so rather than promising silence.

`CLAUDE.md` still says integrations expose `name()` and are bound in
`AppServiceProvider`; the code says `provider()`
(`app/Integrations/Contracts/ResolvesMedia.php:29`) and
`app/Providers/IntegrationServiceProvider.php`. Nothing here binds anything, but
`T-100` follows the code.

**18 September 2026 (`D-027`).** Step 17, the recording observations, is carved
out into `T-122`, so the classroom stream can specify detection against real
payloads without waiting for the registrant questions. The two spikes share the
month of Zoom Workplace Pro, the development app and the `tests/Fixtures/zoom/`
layout and its `README.md` — whichever runs first creates the README, and the
other adds to it. The scope union both spikes authorise is frozen once, in
`T-122`'s report, so neither task records a list of its own. The eleven-digit
placeholder meeting id is `91827405566` in both, and in the seeder.
