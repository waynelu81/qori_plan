---
id: T-120
title: The Peer half of the loop runs in a browser
stream: workflow
status: done
owner: claude
estimate: M
depends: T-119
blocks: T-121, T-145
---

# T-120 — The Peer half of the loop runs in a browser

## Why

`T-119` drives the creator half of the core loop through a browser and stops
at "Ready to share". `PLAN.md`'s loop goes on: share or invite → get access →
continue → finish. Both ways in exist — a stranger with the Series link gets
access with a six-digit code without leaving the page (`T-073`, `T-074`), and
a creator gives an existing account access by email — and neither has been
walked by anything but a person since it was built.

Also from the owner, watching `T-119`'s headed run: `--slow` pauses before
every action, so the screen a step leaves is visible for one pause before the
next fill starts. Too fast to see. A pause _after each step_ is the missing
control.

Afterwards `php artisan qori:e2e` runs three journeys: the creator half as
before; a stranger who follows a Series link, gets a code, opens the Episode,
marks it done and reaches their certificate; and a learner who registers, is
given access by the creator, and follows the "You're in" email to the Series.
`--pause=3000` holds every screen for three seconds.

## Decisions taken to make this specifiable

**The sign-up and the Series become helpers.** Every Peer journey needs a
creator with a ready Series first, so those steps move from
`core-loop.spec.ts` into `tests/e2e/support/creator.ts` as
`signUpCreator(page, project)` and `makeSeriesReady(page, creator)`. The
core-loop journey becomes those two calls, and stays: it is the shortest
proof and the one to run while working on the creator pages.

**The Series id is read from the publish form's action.** Peer routes address
a Series by id (`/shared/{seriesId}`, `/s/{seriesId}/access`), the creator's
page loads by slug, and the page shows the id nowhere a person reads it. The
`#publish` form posts to `/g/{group}/series/{id}/publish`, so the helper reads
its `action` attribute before submitting it. The public page is
`/s/{group}/{seriesSlug}`, both slugs already known.

**A second browser context is the second person.** Playwright's
`browser.newContext()` shares no cookies with the creator's page, which is
exactly a Peer on their own device. Two contexts in one test, not two tests,
because the Peer's steps depend on the creator's Series existing.

**`--pause` is a wait after each step, done by a wrapper.**
`tests/e2e/support/steps.ts` exports `step(name, body)`: `test.step()` and
then a wait of `E2E_STEP_PAUSE` milliseconds, which the command sets from
`--pause=`. Every journey and helper uses `step()` rather than `test.step()`,
so the option holds every screen, not only the ones somebody remembered.
`--slow` stays as it is; they compose.

**The code is read from the subject.** `LoginCodeNotification` puts it there
on purpose ("Your Qori code is :code"), so `codeIn(message)` takes six digits
from the subject and never parses a body. It is typed into the one real input
`vue-input-otp` renders (`input[data-input-otp]`), which carries the value the
hidden `code` field posts.

**Messages are matched on subject as well as recipient.** A Peer receives a
code and then a "You're in" email at the same address within a few seconds;
`waitForMessage(to, { subject })` says which one is wanted. The recipient
alone would have returned the newest, which is a race.

**Text is matched only where Qori owns the words.** The Episode row is found
by its own title with an anchored regex (`^1\. <title>`), because the
"Continue — 1. <title>" control on the same page contains the title too. The
creator's "now has access" toast is matched on those three words, which are
`accesses.added` and not vocabulary. Every other selector is an id or a form
action, as in `T-119`.

**The learner's dashboard is not driven.** After verifying, a learner lands on
`/dashboard` with nothing shared yet; the journey asserts that and then goes
where the "You're in" email points, because following the email is the point.
Finding the Series on the dashboard afterwards is a page a design pass owns.

**The certificate is asserted, not read.** Marking the only Episode done
completes the Series and mints `certificate_code` (`ProgressService`), so the
public-link journey follows the "View your certificate" link and asserts the
URL and the Series title. What the certificate says is `§12`'s job and
`Certificate.vue`'s test.

**No new PHPUnit case.** `--pause` is an integer handed to Playwright in the
environment, past the point the four refusal cases can reach; the journeys
are its verification, and they ran with it.

## Preconditions

**Data this task verifies against:** the databases the command creates and
rebuilds itself.

**Equipment:** as `T-119` — Docker with Postgres and Mailpit up, Playwright's
Chromium, `npm run dev` or `npm run build`. Outbound access to
`player.vimeo.com`, which the opened Episode's iframe loads; the assertion is
on the iframe's `src`, so a blocked load still passes.

## Scope

**In:**

- `--pause=<ms>` on `qori:e2e`, and `step()` in every journey.
- `signUpCreator()` and `makeSeriesReady()`, and `core-loop.spec.ts` reduced
  to them.
- `public-link.spec.ts`: a stranger opens `/s/{group}/{series}`, asks for a
  code, types it from the email, lands on `/shared/{id}`, opens the Episode
  (the Vimeo iframe appears), marks it done, follows the certificate link.
- `invited-peer.spec.ts`: a learner registers with "I want to learn",
  verifies, lands on `/dashboard`; the creator gives their address access
  from the Series page; the learner follows the "You're in" email to
  `/shared/{id}` and sees the Episode.
- `waitForMessage()` gains a subject filter; `codeIn()` is added.
- `docs/tinker/e2e.md`: the option and the three journeys.

**Out:**

- Paying for a Series: `T-121`, blocked on a sandbox connected account.
- The code form's resend and start-over controls, a wrong code, an expired
  one.
- The Peer's password sign-in and magic link.
- EDM invitations to people without an account (`T-043`).
- The learner finding the Series on `/dashboard` or `/shared` by navigation.
- A File Episode and a download; the Episode stays a Vimeo reference.

## Files

| Path                                       | Change | Notes                                                    |
| ------------------------------------------ | ------ | -------------------------------------------------------- |
| `app/Console/Commands/EndToEndCommand.php` | edit   | `--pause=`, `E2E_STEP_PAUSE`                             |
| `tests/e2e/support/steps.ts`               | new    | `step()`                                                 |
| `tests/e2e/support/creator.ts`             | new    | `signUpCreator()`, `makeSeriesReady()`                   |
| `tests/e2e/support/mailpit.ts`             | edit   | `waitForMessage(to, { subject, timeoutMs })`, `codeIn()` |
| `tests/e2e/support/person.ts`              | edit   | `newPerson(project, role)`                               |
| `tests/e2e/core-loop.spec.ts`              | edit   | The two helper calls                                     |
| `tests/e2e/public-link.spec.ts`            | new    | The stranger's journey                                   |
| `tests/e2e/invited-peer.spec.ts`           | new    | The learner's journey                                    |
| `docs/tinker/e2e.md`                       | edit   | `--pause`, the journeys, the tree                        |
| `docs/planning/streams/workflow.md`        | edit   | Tasks 6 and 7                                            |

Flows: none — the journeys drive the code sign-in, access and progress flows
as they are and rewire none of them.

## Database

None.

## Code

```php
// app/Console/Commands/EndToEndCommand.php — one option and one variable
'{--pause=0 : Milliseconds to wait after each step, for watching}'
'E2E_STEP_PAUSE' => (string) max(0, (int) $this->option('pause')),
```

```ts
// tests/e2e/support/steps.ts
export async function step(
    name: string,
    body: () => Promise<void>,
): Promise<void>;

// tests/e2e/support/person.ts
export function newPerson(project: string, role = 'creator'): Person;
// name `E2E <role> <project> <stamp>`, email `e2e+<stamp>-<role>-<project>@example.test`

// tests/e2e/support/mailpit.ts
export async function waitForMessage(
    to: string,
    options?: { subject?: string; timeoutMs?: number },
): Promise<Message>;
export function linkIn(message: Message, pathContains: string): string;
export function codeIn(message: Message): string; // six digits from the subject

// tests/e2e/support/creator.ts
export type Creator = { person: Person; group: string };
export type ReadySeries = { id: string; slug: string; publicUrl: string };
export async function signUpCreator(
    page: Page,
    project: string,
): Promise<Creator>;
export async function makeSeriesReady(
    page: Page,
    creator: Creator,
): Promise<ReadySeries>;
```

Selectors the journeys rely on, all present today: `#access-name`,
`#access-email`, `form:has(#access-email) input[name="consent"]`,
`input[data-input-otp]`, `form[action$="/access/code"]`,
`form[action$="/complete"]`, `a[href^="/certificates/"]`, `#give-access #email`,
`#give-access input[name="consent"]`,
`label:has(input[name="signup_intent"][value="learn"])`.

## Copy

None.

## Routes

None.

## Tests

**New:** none in PHPUnit — see the last decision.

**Changed:** none.

## Acceptance

- [x] `php artisan qori:e2e` runs three journeys headless and exits `0`
- [x] `php artisan qori:e2e --headed --pause=2000` holds every screen for two
      seconds
- [x] `php artisan qori:e2e --viewport=mobile` passes all three
- [x] `--only=stranger` and `--only=learner` each run one journey
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Specified and approved on 17 September 2026, from the owner's three asks
after `T-119`'s first headed run: a pause between steps, the creator
publishing and a Peer registering and getting access, and payment. Payment
is `T-121`.

Closed the same day. Every journey passed on its first run; the only
surprise was the board, which wanted `T-119` to say `blocks: T-120` once
this task depended on it, and that line was fixed.
