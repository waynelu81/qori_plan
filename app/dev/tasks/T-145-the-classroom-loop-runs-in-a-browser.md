---
id: T-145
title: The classroom loop runs in a browser: a far-timezone Peer misses a class and finds the recording
stream: workflow
status: draft
owner: unassigned
estimate: M
depends: T-120, T-128, T-131
blocks: none
---

# T-145 — The classroom loop runs in a browser: a far-timezone Peer misses a class and finds the recording

> **Draft.** Written on 18 September 2026 on `T-120`'s pattern, from `D-031`
> and the classroom brief; not to be started — see
> [`../PROCESS.md`](../PROCESS.md). It waits on the classroom checkpoint
> landing, because every selector below is a promise in a draft until then;
> what has to be true before it can be marked `ready` is listed at the bottom.

## Why

`php artisan qori:e2e` walks three journeys, and every Episode any of them
opens is a Vimeo reference (`tests/e2e/support/creator.ts:109-116`). Nothing
drives a live Episode, a pasted recording, a material, or an email that a
scheduled command sends rather than a request. The command hands Playwright
five `E2E_*` variables and nothing of the run's own environment
(`app/Console/Commands/EndToEndCommand.php:332-338`), so a journey cannot run
an artisan command against the run's database at all — and `recording_ready`
leaves only through `qori:sessions:notify` (`T-128`, `D-028`). The classroom
stream's exit condition names this walk: a Peer in another timezone who
missed the class receives one email, opens the Episode card and finds the
recording and the slides, at mobile and desktop widths, with the Peer's zone
at least eight hours from the Group's (`docs/planning/streams/classroom.md:16-24`).
`D-031` calls `T-145` the beta-gate evidence. The classroom tasks' own suites
pin every boundary at prop level and leave rendering to this walk: `T-125`
asserts the instants of a Brisbane session for New York and London and says
"the rendering is `T-145`'s"; a `datetime-local` typed in the Group's zone,
two zones on one card and a `<time>` element a browser formats are things
PHPUnit cannot see.

Afterwards `qori:e2e` runs a fourth journey. A creator whose Group keeps
Brisbane time schedules a live Zoom session ten minutes ahead and attaches
slides as a link; a Peer whose browser is in New York comes in through the
Series link and a code, saves New York as their timezone from the card's
prompt, sees the session in their own time with Brisbane beside it, and
follows Join — a 302 to the creator's link, asserted and not followed. The
creator pastes the recording link; the journey runs `qori:sessions:notify`
in the run's environment; the Peer's email names the session in both zones
and lands on the Episode's card, where Open on the slides answers a 302 to
the slides, and — once the run's clock is past the join window, the one thing
this draft still owes — Watch answers a 302 to the recording.
`--only=classroom` runs it alone,
`--viewport=mobile` runs it narrow, and the run's evidence goes to
`walkthroughs.md`.

## Decisions taken to make this specifiable

**The journey starts from `signUpCreator()` and `makeSeriesReady()` and adds
the live Episode to the Series after it is published.** `EpisodeService::add()`
guards the over-cap lock, the type, the limit and the live time
(`app/Services/EpisodeService.php:43-46`), never the status, and
`SeriesService::publish()` wants one Episode (`app/Services/SeriesService.php:157-162`),
which the helper's Vimeo Episode is. So the Vimeo Episode stays at position 1
and the live one lands at position 2. Every Peer-side selector is scoped by
`#episode-{id}` (`D-024`), so the position never appears in the journey, and
`makeSeriesReady()` is untouched.

**The Group's timezone is chosen explicitly, through a new option on
`signUpCreator()`.** `GroupNameForm.vue` carries `#group-timezone`
(`resources/js/components/share/GroupNameForm.vue:64-72`), pre-filled from
the browser only while nobody has answered, and `GroupController::update()`
saves it with the name (`app/Http/Controllers/Share/GroupController.php:36-48`).
`signUpCreator(page, project, { groupTimezone })` selects it in the "name the
Group" step when given; the other journeys pass nothing and behave as they
do today. The choice is explicit because `EpisodeService::guardLiveSessionTime()`
refuses a live Episode until the Group's _own_ zone is set
(`app/Services/EpisodeService.php:89-97`), and a journey that relied on the
pre-fill would depend on the browser's zone being in the option list.

**Each person's browser context carries their zone, and both pin `en-US`.**
`test.use({ timezoneId: 'Australia/Brisbane', locale: 'en-US' })` for the
creator's page; `browser.newContext({ timezoneId: 'America/New_York', locale: 'en-US' })`
for the Peer, the second context being the second person as `T-120` decided.
Brisbane is UTC+10 all year and New York UTC−4 or −5, fourteen or fifteen
hours apart — the stream's "at least eight". The locale is pinned because
Playwright's device descriptors set none (`devices['Desktop Chrome'].locale`
and `devices['Pixel 7'].locale` are both undefined in 1.63.0), so the browser
would take the machine's, and the abbreviation the card prints for Brisbane is
`GMT+10` under `en-US` and `AEST` under `en-AU`. Under `en-US`, Chromium's
`timeZoneName: 'short'` gives `EDT` or `EST` for New York and `GMT+10` for
Brisbane.

**The session starts ten minutes ahead, so Join is `open` the moment the Peer
arrives.** `T-125`: the window opens `qori.live.join_opens_minutes` (15)
before the start and closes `join_closes_after_minutes` (15) after the
scheduled end. The ten-minute lead is the one `T-125`'s Notes record for this
draft ("the journey either adds the session 10 minutes ahead or uses the
clock override"). The start is `Date.now() + 10 min` with seconds and
milliseconds cleared, typed into `#live-starts-at` as `YYYY-MM-DDTHH:mm` in
Brisbane (`StoreEpisodeRequest::prepareForValidation()` reads it in the
Group's zone). Steps 1 to 11 and step 13 need no clock: a paste is allowed
whatever the clock says (`T-126`); the email's recipients are decided at
publication and sent by the command whenever it runs (`T-128`); the slides
are `with_episode`, which is always released (`T-131`).

**Step 12 does need the clock moved, because the Peer's card offers Watch
only once the join window has closed.** `T-126` puts the `ready` arm _after_
`cancelled`, `upcoming` and `open` — "a recording pasted before or during the
session must not take Join off the Peer's card" — and renders the recording
block, with its `Passcode: …` line, only in state `ready`. A session ten
minutes ahead with a sixty-minute length is `open` until
`ends_at + 15 minutes`, so on today's clock the pasted recording sits on the
creator's page while the Peer's card still shows Join. Nothing in the product
brings `ready` forward: `EpisodeService::guardLiveSessionTime()`
(`app/Services/EpisodeService.php:107-112`) refuses a start behind now, so the
walk cannot schedule a session that is already over, and the recording's id
reaches no DOM the journey could address directly (`T-126` renders the
creator's list without it). The run therefore needs its clock moved past the
window between step 11 and step 12, and that mechanism is this draft's one
blocker — see "Before this can be ready". What is walked after the scheduled
end is step 12 and nothing else: the `waiting` line, an `after_session`
material's release and Join refused outside the window stay out.

**A redirect is asserted through the context's request API, never followed.**
`theirs.request.get(href, { maxRedirects: 0 })` uses the Peer's cookies and
`baseURL`, and returns the 302 with its `location` header. Three assertions
use it: Join to the Zoom-shaped link, Watch to the pasted recording, Open to
the slides. The run therefore needs no route to `zoom.us` or either
`example.test` host and opens no popup whose fate a blocked network would
decide. The GET still passes the gate, marks the Episode opened and writes
the `access_opens` row exactly as a click would; `T-125`, `T-126` and `T-131`
assert those rows, and this walk asserts what the browser is sent to.

**The notices are sent by running `qori:sessions:notify` from the journey, in
the run's environment.** Nothing else sends them: the paste queues and the
command sends inline (`D-028`). A new `tests/e2e/support/artisan.ts` spawns
`E2E_PHP` with `E2E_ARTISAN` and the process environment, and
`EndToEndCommand::playwright()` gives the Playwright process the same
`$environment` it gives `migrate:fresh` and the server
(`app/Console/Commands/EndToEndCommand.php:203-218`, `:244-256`, `:265-273`),
so the child artisan reads `DB_DATABASE`, `APP_URL`, `MAIL_MAILER=smtp` and
the rest from its environment, which wins over `.env` — the mechanism the
command's docblock already relies on (`:28-31`). The scheduler is not
involved: a run must not wait for a five-minute tick, and `withoutOverlapping()`
and `onOneServer()` sit on the schedule entry, not on the command.

**The time on the card is asserted by instant and by zone name, not by its
formatted text.** `SessionTime.vue` renders `<time :datetime="startsAt">`
(`resources/js/components/series/SessionTime.vue:66`) around text built with
`timeZoneName: 'short'` (`:34-42`); `T-125` adds the range and, after " · ",
the same range in the Group's zone. The journey asserts that the first
`time[datetime]` in the card parses to the instant it typed, and that the
card's text carries the New York abbreviation (`/E[DS]T/`) and Brisbane's
(`/GMT\+10/`) either side of " · ". Matching the whole string would pin ICU's
punctuation, which differs between Chromium and Node versions.

**The Peer's stored zone is saved from `T-125`'s prompt, not from the profile
page.** The prompt is the product's way of asking a Peer who has never
answered; the journey selects `America/New_York` in
`form[action$="/u/timezone"] select[name="timezone"]` (the route is
`profile.timezone.update`, `routes/settings.php:49-50`; `TimezoneField`'s
default `name` is `timezone`) and submits, and `TimezoneController::update()`
answers `back()` once `T-125` lands — still an open point of `T-125`'s,
carried under "Before this can be ready" — so the Peer stays on the Series
page. The
toast is `profile.timezone.saved` (`lang/en/profile.php:26`), matched on
"Times will show in America/New_York". `T-128`'s zone rule then renders the
email's session line in New York with Brisbane beside it, and the journey
asserts both identifiers in the message's text — the one email assertion
beyond the link.

**Text is matched only where Qori owns the words**, as `T-120`: the session
and material titles (anchored exact), the passcode, the zone identifiers in
the mail, "Recording added to" (the words of `series.recording_added` before
the vocabulary), the timezone toast. Every other selector is an id, a form
action or a route-shaped `href`: `#live-join-url`, `#live-starts-at`,
`#live-length`, `#live-records` (`T-123`); `#recording-url`,
`#recording-passcode`, `form[action$="/recordings"]` (`T-126`); the material
form's field names inside `form[action$="/episodes/{id}/materials"]`
(`T-130`); `#episode-{id} a[href$="/episodes/{id}/open"]` for Join,
`a[href*="?recording="]` for Watch, `a[href*="/materials/"]` for Open
(`T-125`, `T-126`, `T-131`). Join is scoped to the Episode route and never to
a bare `/open`, because the slides' Open control on the same row (`T-131`,
`/shared/{seriesId}/materials/{materialId}/open`) is also an `<a>` whose
`href` ends in `/open`, and a locator that resolves to two elements fails
under strict mode.

**The three code sign-in steps are copied from `public-link.spec.ts:28-55`
into this journey, not extracted into a helper.** `T-120` made helpers of
the steps every Peer journey needs — the sign-up and the ready Series — and
left each journey's own way in inline. The code is one of three ways in, and
only `public-link.spec.ts` shares it. Copying it here leaves that journey and
the other two untouched, as everything else in this task does, and keeps
`tests/e2e/public-link.spec.ts` out of the Files table. A
`tests/e2e/support/peer.ts` with `enterWithCode(page, series, peer)` is the
day a third journey needs the code, and that task edits
`public-link.spec.ts` to call it.

**The live Episode's id is read from the paste form's action**, as `T-120`
reads the Series id from the publish form: the creator's page shows the id
nowhere a person reads it, and `form[action$="/recordings"]` posts to
`…/episodes/{id}/recordings` (`T-126`) and is the only such form while the
Series has one live Episode without a recording.

**The material form lives inside a `<details>`, which the journey opens only
if it is closed.** `T-130` renders `MaterialList.vue` as a `<details>` with
the form at its foot. Playwright refuses to fill a hidden field, so the step
reads the element's `open` property and clicks its `summary` only when it is
false — a click that toggles would close one that was open.

**`newPerson()` gains `session` and `material`; the URLs are constants.** A
title needs the stamp so the desktop and mobile projects never share one;
the three URLs (`https://zoom.us/j/91827405566`, the eleven-digit placeholder
every classroom task uses; `https://recordings.example.test/clinic`;
`https://docs.example.test/clinic-slides`) need no stamp, because the
database is rebuilt each run and nothing is unique on them.

**Both widths, and the evidence in `walkthroughs.md`.** `--viewport=both`
walks the journey twice with two sets of people. The run's evidence is an
entry in `docs/planning/walkthroughs.md`, because it is evidence about the
product (`PROCESS.md`, "Finishing"), and the report says what the run could
not show.

**No new PHPUnit case.** As `T-120`: the change to the command is an
environment hand-off past the four refusals `EndToEndCommandTest` reaches
(`tests/Feature/Console/EndToEndCommandTest.php:17-53`); the journey is its
verification, and the report records the runs.

## Preconditions

**Data this task verifies against:** the databases the command creates and
rebuilds itself. The classroom checkpoint merged — `T-089`, `T-123` to
`T-128`, `T-130`, `T-131` — because the journey drives their pages and
routes as they land; nothing is seeded.

**Equipment:** as `T-119` and `T-120` — Docker with Postgres and Mailpit up,
Playwright's Chromium, `npm run dev` or `npm run build`. No outbound network:
the Vimeo iframe of the helper's Episode is never opened here, and every
vendor-shaped link is asserted as a 302 target. No Zoom account and no
storage bucket; the run serves with `QORI_STORAGE_DISK=local` and the slides
are a link.

**Spike:** none owed. The journey reads no vendor payload; the join link is a
URL Qori never follows (`D-025`).

## Scope

**In:**

- `tests/e2e/classroom.spec.ts`: the journey below, title containing
  `classroom`.
- `tests/e2e/support/artisan.ts` (`artisan()`), `tests/e2e/support/time.ts`
  (`minutesAhead()`, `localInput()`); `signUpCreator()`'s `groupTimezone`
  option; `session` and `material` on `Person`.
- `EndToEndCommand::playwright()` passing the run's environment, `E2E_PHP`
  and `E2E_ARTISAN`.
- Moving the run's clock past the join window before step 12, so the Peer's
  card reaches `ready`. The mechanism is the blocker below; its Files rows,
  its `Code` block and its `docs/tinker/e2e.md` paragraph land with it.
- `docs/tinker/e2e.md`: the fourth journey, the two helpers, the zones and
  the variables; `docs/planning/streams/workflow.md` task 8; the
  `walkthroughs.md` entry.

**Out:**

- Every state after the scheduled end except `ready`: the `waiting` line,
  `overdue`, an `after_session` material's release, Join refused outside the
  window, the "Join again" grace. `ready` is walked, because the recording is
  what the stream's exit condition is about; the clock mechanism that reaches
  it is the blocker below.
- Paying for the Series (`T-121`); the invited-learner way in (`T-120`'s
  journey covers it); `T-043`'s invitations.
- A Qori-hosted material (an upload) — the slides are a link; `T-130`'s
  suite covers the R2 path, and `T-119` decided the run touches no storage.
- The chat card (`T-132`), the calendar file (`T-133`), reminders and
  cancellation (`T-134`, `T-138`), Zoom detection (`T-141` to `T-144`).
- A Group vocabulary other than the default; the journey matches no noun.
- Confirmed delivery through Postmark (`T-032`); Mailpit is the inbox.
- A new refusal, option or PHPUnit case on `qori:e2e`.
- The daylight-saving boundary as a rendered assertion; the run uses today's
  clock, and `T-125` case 15 and `T-128` case 16 pin 1 November 2026.

## Files

| Path                                       | Change | Notes                                                                                      |
| ------------------------------------------ | ------ | ------------------------------------------------------------------------------------------ |
| `tests/e2e/classroom.spec.ts`              | new    | The journey                                                                                |
| `tests/e2e/support/artisan.ts`             | new    | `artisan()` — an artisan command in the run's environment                                  |
| `tests/e2e/support/time.ts`                | new    | `minutesAhead()`, `localInput()`                                                           |
| `tests/e2e/support/creator.ts`             | edit   | `signUpCreator()` gains `{ groupTimezone }`                                                |
| `tests/e2e/support/person.ts`              | edit   | `session`, `material`                                                                      |
| `app/Console/Commands/EndToEndCommand.php` | edit   | `playwright()` takes `$environment`; `E2E_PHP`, `E2E_ARTISAN`; the docblock                |
| `docs/tinker/e2e.md`                       | edit   | Four journeys, the row, the tree, "Zones and the clock", the variables Playwright now sees |
| `docs/planning/streams/workflow.md`        | edit   | Task 8                                                                                     |
| `docs/planning/walkthroughs.md`            | edit   | The run's entry, dated the day it ran                                                      |

Flows: none — the journey drives the live-session, recording, notice and
material flows as `docs/flows/live-sessions.md` and `docs/flows/materials.md`
describe them and rewires none of them; `app/Console/Commands/` is the only
application code touched.

No route, lang, config, factory or seeder row: the journey adds no page, no
sentence and no column. `tests/e2e/playwright.config.ts` is not edited — the
zones and the locale are set per journey, because the other three journeys
mean nothing by them.

## Database

None.

## Code

```php
// app/Console/Commands/EndToEndCommand.php

// handle(), line 111: the environment reaches Playwright too.
$exit = $this->playwright($baseUrl, $environment);

/**
 * The run's own values go to the Node side as well, so a journey that runs
 * an artisan command (tests/e2e/support/artisan.ts) reads the run's
 * database and sends through the run's mailer, as the migration and the
 * server do. The classroom journey (T-145) sends its notices that way.
 *
 * @param  array<string, string>  $environment
 */
private function playwright(string $baseUrl, array $environment): int;
// $process = new Process([$binary, ...$this->playwrightArguments()], base_path(), [
//     ...$environment,
//     'E2E_BASE_URL' => $baseUrl,
//     'E2E_MAILPIT_URL' => (string) config('qori.mail.mailpit_url'),
//     'E2E_SLOW_MO' => (string) max(0, (int) $this->option('slow')),
//     'E2E_STEP_PAUSE' => (string) max(0, (int) $this->option('pause')),
//     'E2E_OUTPUT' => storage_path('app/e2e'),
//     'E2E_PHP' => PHP_BINARY,
//     'E2E_ARTISAN' => base_path('artisan'),
// ], timeout: 900);
```

The class docblock (`:14-34`) gains one paragraph: the classroom journey runs
`qori:sessions:notify` from inside Playwright, which is why the same
environment is handed to the Node process. `$description` and the closing
`info` line are unchanged.

```ts
// tests/e2e/support/artisan.ts
import { execFileSync } from 'node:child_process';
import { dirname } from 'node:path';

/**
 * Run an artisan command in the run's environment (T-145).
 *
 * qori:e2e puts the run's DB_DATABASE, APP_URL and MAIL_MAILER into this
 * process's environment beside E2E_*, and a child inherits them, so the
 * command reads the run's database and mails the run's inbox — the same
 * mechanism as `DB_DATABASE=… php artisan test`. Throws with the output
 * when the command exits non-zero. Requires E2E_PHP and E2E_ARTISAN; by
 * hand, set them (`E2E_ARTISAN=$PWD/artisan E2E_PHP=php npx playwright …`).
 */
export function artisan(...args: string[]): string;
// const artisanPath = process.env.E2E_ARTISAN;
// const php = process.env.E2E_PHP;
// if (!artisanPath || !php) throw new Error('E2E_ARTISAN and E2E_PHP are not set; run through `php artisan qori:e2e`.');
// return execFileSync(php, [artisanPath, ...args], {
//     cwd: dirname(artisanPath),
//     env: process.env,
//     encoding: 'utf8',
//     timeout: 60_000,
// });

// tests/e2e/support/time.ts

/** Now plus `minutes`, seconds and milliseconds cleared: what is typed, what is stored and the ISO prop then agree to the second. */
export function minutesAhead(minutes: number): Date;
// const d = new Date(Date.now() + minutes * 60_000);
// d.setSeconds(0, 0); // both: `setSeconds(0)` alone leaves the milliseconds, and `Date.parse(datetime) === start.getTime()` fails
// return d;

/** `YYYY-MM-DDTHH:mm` for a `datetime-local` input — the instant as it reads in `zone`. */
export function localInput(instant: Date, zone: string): string;
// Intl.DateTimeFormat('en-CA', { timeZone: zone, year: 'numeric', month: '2-digit', day: '2-digit',
//     hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(instant), joined as
// `${year}-${month}-${day}T${hour}:${minute}`

// tests/e2e/support/person.ts — two fields
export type Person = {
    name: string;
    email: string;
    password: string;
    group: string;
    series: string;
    episode: string;
    /** The live Episode's title: `Live clinic <stamp>`. */
    session: string;
    /** The slides' title: `Clinic slides <stamp>`. */
    material: string;
};

// tests/e2e/support/creator.ts — one option
export async function signUpCreator(
    page: Page,
    project: string,
    options: { groupTimezone?: string } = {},
): Promise<Creator>;
// in 'name the Group', before the submit:
// if (options.groupTimezone) await page.selectOption('#group-timezone', options.groupTimezone);
```

```ts
// tests/e2e/classroom.spec.ts — the shape; every stage goes through step()

const GROUP_ZONE = 'Australia/Brisbane';
const PEER_ZONE = 'America/New_York';
const JOIN_URL = 'https://zoom.us/j/91827405566';
const RECORDING_URL = 'https://recordings.example.test/clinic';
const PASSCODE = 'clinic-1234';
const MATERIAL_URL = 'https://docs.example.test/clinic-slides';
/** Inside qori.live.join_opens_minutes (15), so the card offers Join on arrival. */
const LEAD_MINUTES = 10;
const LENGTH_MINUTES = 60;

test.use({ timezoneId: GROUP_ZONE, locale: 'en-US' });

test('a creator schedules a classroom session in Brisbane; a Peer in New York joins it, then finds the recording from the email', async ({
    page,
    browser,
}, testInfo) => {
    const creator = await signUpCreator(page, testInfo.project.name, {
        groupTimezone: GROUP_ZONE,
    });
    const series = await makeSeriesReady(page, creator);
    const peer = newPerson(testInfo.project.name, 'peer');
    const start = minutesAhead(LEAD_MINUTES);
    let episodeId = '';

    // 'schedule a live session ten minutes ahead'
    //   fill #episode-title = creator.person.session; selectOption #episode-type 'live';
    //   selectOption #episode-provider 'zoom'; fill #live-join-url JOIN_URL;
    //   fill #live-starts-at localInput(start, GROUP_ZONE); fill #live-length String(LENGTH_MINUTES);
    //   check #live-records; click form:has(#episode-title) button[type="submit"];
    //   expect getByText(session, { exact: true }) visible;
    //   episodeId = action of form[action$="/recordings"] matched on /\/episodes\/([^/]+)\/recordings$/, not ''.
    // 'add the slides as a link'
    //   form = page.locator(`form[action$="/episodes/${episodeId}/materials"]`);
    //   details = page.locator('details', { has: form }); open it if !(await details.evaluate(el => el.open));
    //   form [name="title"] = creator.person.material; select[name="role"] 'material';
    //   select[name="provider"] 'link'; [name="url"] MATERIAL_URL; select[name="release"] 'with_episode';
    //   click form button[type="submit"]; expect getByText(material, { exact: true }) visible.

    const context = await browser.newContext({
        timezoneId: PEER_ZONE,
        locale: 'en-US',
    });
    const theirs = await context.newPage();
    const card = theirs.locator(`#episode-${episodeId}`);

    // 'open the Series link as a stranger', 'ask for a code', 'type the code from the email'
    //   copied inline from public-link.spec.ts:28-55 — not extracted into a helper, and that
    //   file is not edited (see Decisions) — ending on /shared/{series.id}.
    // 'save their timezone from the prompt'
    //   prompt = theirs.locator('form[action$="/u/timezone"]'); expect visible;
    //   prompt select[name="timezone"] → PEER_ZONE; click prompt button[type="submit"];
    //   expect URL /\/shared\/{id}$/; expect getByText(/Times will show in America\/New_York/) visible;
    //   expect prompt toHaveCount(0).
    // 'see the session in their own time, with Brisbane beside it'
    //   datetime = await card.locator('time[datetime]').first().getAttribute('datetime');
    //   expect(Date.parse(datetime ?? '')).toBe(start.getTime());
    //   expect(card).toContainText(' · '); toContainText(/E[DS]T/); toContainText(/GMT\+10/).
    // 'join while the window is open'
    //   join = card.locator(`a[href$="/episodes/${episodeId}/open"]`); expect visible;
    //   (never a bare /open: the slides' Open on the same row ends in /open too, T-131)
    //   response = await theirs.request.get(await join.getAttribute('href') ?? '', { maxRedirects: 0 });
    //   expect(response.status()).toBe(302); expect(response.headers()['location']).toBe(JOIN_URL).
    // 'paste the recording link after the class'   (the creator's page)
    //   fill #recording-url RECORDING_URL; fill #recording-passcode PASSCODE;
    //   click form[action$="/recordings"] button[type="submit"];
    //   expect getByText(/Recording added to/) visible.
    // 'send the notices'
    //   artisan('qori:sessions:notify');   // throws on a non-zero exit; the email is the proof
    // 'follow the recording email'
    //   message = await waitForMessage(peer.email, { subject: 'recording' });
    //   expect(message.Text).toContain(`(${PEER_ZONE})`); toContain(`(${GROUP_ZONE})`);
    //   await theirs.goto(linkIn(message, `/shared/${series.id}/episodes/`));
    //   expect URL new RegExp(`/shared/${series.id}#episode-${episodeId}$`).
    // 'watch the recording from the same card'
    //   first the run's clock moves past ends_at + qori.live.join_closes_after_minutes and the
    //   Peer reloads, because T-126 renders the recording only in state 'ready' — the mechanism
    //   is this draft's blocker, and this line is written when it is decided;
    //   watch = card.locator('a[href*="?recording="]').first(); expect visible; expect(card).toContainText(PASSCODE);
    //   302 whose location is RECORDING_URL, as Join was asserted.
    // 'open the slides'
    //   expect(card).toContainText(creator.person.material);
    //   open = card.locator('a[href*="/materials/"]').first(); 302 whose location is MATERIAL_URL.

    await context.close();
});
```

Selectors the journey relies on, and which task makes each true:
`#group-timezone` (today, `GroupNameForm.vue:65`); `#episode-title`,
`#episode-type`, `#episode-provider` (today, `resources/js/pages/share/series/Show.vue`;
`#episode-provider` already accepts `zoom` for a live Episode, `Show.vue:202`,
and only the `#live-*` fields wait on `T-123`); `#live-join-url`,
`#live-starts-at`, `#live-length`, `#live-records` (`T-123`; the box is
`checked` in the markup and `check()` is idempotent, so the step states the
intent without toggling it);
`form[action$="/episodes/{id}/materials"]` and its `title`, `role`,
`provider`, `url`, `release` fields inside a `<details>` (`T-130`);
`#access-name`, `#access-email`, `form:has(#access-email) input[name="consent"]`,
`input[data-input-otp]`, `form[action$="/access/code"]` (today,
`public-link.spec.ts`);
`form[action$="/u/timezone"]` and `select[name="timezone"]` (`T-125`);
`#episode-{id}`, `time[datetime]` and `a[href$="/episodes/{id}/open"]`
(`T-125`; scoped to the Episode route because `T-131`'s material Open on the
same row also ends in `/open`);
`#recording-url`, `#recording-passcode`, `form[action$="/recordings"]` and
`a[href*="?recording="]` (`T-126`); `a[href*="/materials/"]` (`T-131`).

`docs/tinker/e2e.md`: the opening paragraph and "drives the three journeys"
say four; the journeys table gains
`classroom.spec.ts | classroom | All of the first, then a live Zoom session ten minutes ahead in a Brisbane Group with slides as a link; a Peer in New York comes in with a code, saves their zone, sees both zones on the card, Join answers a 302 to the link; the recording is pasted, qori:sessions:notify is run, the email lands on the card, Watch and Open answer 302s`;
the tree gains `classroom.spec.ts`, `support/artisan.ts` and
`support/time.ts` with one-line notes; a section "Zones and the clock" says
each journey sets its contexts' `timezoneId` and `locale`, that the classroom
session is ten minutes ahead so Join is open on arrival and nothing waits for
a window, how the run's clock is moved past that window for the recording
step, and that a vendor-shaped link is asserted as a 302 target with
`request.get()` and never opened; the isolation table gains a line saying the same variables now reach
Playwright, plus `E2E_PHP` and `E2E_ARTISAN`, so `artisan()` works; "Adding
a journey" names `artisan()` for a command a journey needs run.

`docs/planning/streams/workflow.md`, after task 7:
`8. T-145 — The classroom loop runs in a browser: a Brisbane creator schedules a live session and pastes its recording; a New York Peer joins from the card in their own time, and qori:sessions:notify's email brings them back to the recording and the slides — the classroom stream's beta-gate evidence`.

`docs/planning/walkthroughs.md`, appended under a heading
`## <date> — the classroom loop in a browser (T-145)`: the command lines
run and their timings; that the card showed the session at the New York hour
with the Brisbane hour after " · " at 1440 and at 390 px; that the email
named both zones; the three 302 targets; and what the run could not show —
no real meeting, no recording host, nothing past the scheduled end.

## Copy

None. The journey reads copy and adds none.

## Routes

None.

## Tests

**New: `tests/e2e/classroom.spec.ts` — one Playwright test.** Thirteen steps
of its own after `signUpCreator()`'s five and `makeSeriesReady()`'s three,
in this order, each a `step()`:

1. `schedule a live session ten minutes ahead` — the live Episode lands with
   its title on the page; the id is read from the paste form.
2. `add the slides as a link` — the material's title is on the page.
3. `open the Series link as a stranger` — `#access-email` visible.
4. `ask for a code` — the code form appears.
5. `type the code from the email` — `/shared/{id}`.
6. `save their timezone from the prompt` — the toast names New York; the
   prompt is gone; still on `/shared/{id}`.
7. `see the session in their own time, with Brisbane beside it` — the
   `<time>` instant equals the typed start; `E[DS]T`, `·`, `GMT+10`.
8. `join while the window is open` — Join is `a[href$="/episodes/{id}/open"]`
   inside the card, never a bare `/open`, which would also match the slides'
   Open; 302 to `JOIN_URL`.
9. `paste the recording link after the class` — "Recording added to".
10. `send the notices` — `artisan('qori:sessions:notify')` exits 0.
11. `follow the recording email` — both zone identifiers in the text; the
    link lands on `/shared/{id}#episode-{episodeId}`.
12. `watch the recording from the same card` — the run's clock past
    `ends_at + join_closes_after_minutes` so the card is `ready` (`T-126`);
    the passcode on the card; 302 to `RECORDING_URL`.
13. `open the slides` — the title on the card; 302 to `MATERIAL_URL`.

**New in PHPUnit:** none — see the last decision. **Changed:** none;
`EndToEndCommandTest`'s four refusals stop before `playwright()` is reached,
and the three existing journeys are unchanged by the option and the fields
added to the helpers.

Total: one Playwright test and no new PHPUnit case.

## Acceptance

- [ ] `php artisan qori:e2e` runs four journeys headless and exits `0`;
      `--only=classroom` runs one
- [ ] A creator whose Group keeps Brisbane time schedules a live Zoom session
      ten minutes ahead, and a Peer in New York who came in through the
      Series link and a code — never through creator setup — sees it on the
      card in their own time with Brisbane beside it (owner acceptance 1 and
      2 at the browser; the daylight-saving boundary is `T-125`'s and
      `T-128`'s prop-level cases)
- [ ] Join on the card answers a 302 to the creator's link while the window
      is open, and the slides are on the same card before and after (owner
      acceptance 3)
- [ ] After the creator pastes the recording link and `qori:sessions:notify`
      runs, the Peer receives one email that names the session in New York
      and Brisbane and lands on the Episode's card, where Open on the slides
      answers a 302 to their link (owner acceptance 4)
- [ ] With the run's clock past the join window the same card is `ready`, and
      Watch answers a 302 to the pasted link with the passcode beside it
      (owner acceptance 4; `T-126` keeps Join in front of `ready` until the
      window closes)
- [ ] Nothing in the run reaches `zoom.us` or either `example.test` host, and
      no vendor account is needed
- [ ] `php artisan qori:e2e --viewport=mobile` passes all four;
      `--viewport=both` passes eight; `--headed --pause=2000` holds every
      screen of the new journey
- [ ] `docs/tinker/e2e.md` describes the fourth journey, `artisan()`, the
      zones and the variables; `docs/planning/streams/workflow.md` lists
      task 8; `docs/planning/walkthroughs.md` carries the run's entry
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-128` and `T-131` `done`, which carries the chain beneath them
  (`T-089`, `T-123` to `T-127`, `T-130`), so every selector named under
  Code is code and not a draft's promise; whoever sets this `ready` re-reads
  the selectors against the merged pages, and a renamed id is a wording fix
  here, not a re-scope — anyone's.
- `T-125`'s open point on `TimezoneController::update()` answering
  `redirect()->back(fallback: route('profile.edit'))` rather than today's
  `to_route('profile.edit')`
  (`app/Http/Controllers/Settings/TimezoneController.php:32`) is settled,
  because step 6 asserts the Peer is still on `/shared/{id}` and that the
  prompt is gone. If it stays `to_route('profile.edit')`, step 6 does
  `theirs.goto(`/shared/${series.id}`)` after the submit and before its URL
  and prompt assertions, and the decision above is reworded — anyone's, with
  `T-125`'s owner told.
- **A way to move the run's clock past the join window**, decided and
  specified, because step 12 cannot run without one. `T-126` renders the
  recording only in state `ready`, which begins at
  `ends_at + join_closes_after_minutes`, and a live Episode's start can never
  be typed into the past, so no arrangement of the journey reaches `ready` on
  today's clock. Two shapes are on the table: an `E2E_NOW` variable in the
  run's environment, read as `qori.e2e.now` in `config/qori.php` (`env()`
  only there, `CLAUDE.md`) and honoured by a provider under `local` only
  through `CarbonImmutable::setTestNow()`, which moves every state at once
  without touching a service; or a per-run `qori.live.*` window short enough
  to wait through. Only the server's clock has to move: the card re-derives
  client-side only among `upcoming`, `open` and `waiting` and renders a
  server `ready` as given (`T-125`), so the browser's own clock can stay
  real and the step is a reload. Whoever sets this `ready` picks one, and its
  Files rows, its `Code` block and its `docs/tinker/e2e.md` paragraph are
  written then — anyone's, with `T-119`'s command and `T-123`'s config both
  touched.
- Whether the same mechanism should also carry the walk across the states
  left out of Scope — the `waiting` line, an `after_session` material's
  release, Join refused after the window, the "Join again" grace. They are
  free once the clock moves, and each is one more assertion or one more
  reload. The owner's, as a second half of this journey or a fifth one.

## Re-scope log

None.

## Notes

Written on 18 September 2026 on `T-120`'s pattern, from `D-031` ("`T-145` is
the beta-gate evidence") and the classroom brief. The two source proposals are
folded into [`../course-classroom.md`](../course-classroom.md); the owner's
acceptance scenarios 1 to 4 are the ones this walk shows in a browser, and 11
to 13 are the tests in the classroom tasks.

`T-125`'s Notes already say this draft is edited to a ten-minute lead, and
this draft is written that way; `T-125`'s own note stands as the record of
why. No other draft is edited by this one. `T-120`'s front matter carries
`blocks: T-121, T-145`, which the amendments pass wrote.

The abbreviations the card prints depend on the browser's locale, not only on
its zone: `en-US` says `GMT+10` where `en-AU` says `AEST`. Both contexts pin
`en-US` for that reason, and the other three journeys are not touched by it.
Should the design stream ever pin a locale in `playwright.config.ts` for all
four, this journey's `test.use()` line becomes redundant and can go.

The one diagnostic the journey does not read is `qori:sessions:notify`'s
"Sent 1, 1 due." line — a developer's output that `T-128` may reword; the
email arriving is the proof and the exit code is the check.

The clock blocker is the one thing this draft owes, and it is owed to step 12
rather than to a nice-to-have: `T-126` decided that Join stays in front of
`ready` until the window closes, which is right for a Peer and means a walk
on today's clock can reach the pasted recording on the creator's page and
never on the Peer's. `LiveSessionService::stateFor()` takes the clock as a
parameter (`T-125`), so a `qori.e2e.now` config key — its `env()` read in
`config/qori.php`, because app code reads `config('qori.…')` and never
`env()` (`CLAUDE.md`, `ArchitectureTest`) — that a provider honours under
`local` through `CarbonImmutable::setTestNow()` moves every state at once
without touching a service. That is the shape to start from; the choice is
made where this can be marked `ready`, not here.
