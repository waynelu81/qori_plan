---
id: T-203
title: A test request starts with no current group
stream: workflow
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-203 — A test request starts with no current group

## Why

`CurrentGroup` is bound `scoped()` (`app/Providers/AppServiceProvider.php:31`)
and `SetCurrentGroup` fills it with a bare `set()`
(`app/Http/Middleware/SetCurrentGroup.php:46`). A real request starts in a
fresh container, but one test's requests share one application, so a Peer
request made after a creator request in the same test runs with the
creator's Group still current. That hides exactly the bug the Peer surface
is most exposed to — a group-scoped read with no `CurrentGroup::runFor()` —
because the leftover Group answers it. `T-126`'s and `T-127`'s tests work
round it by hand (`RecordingTest`'s `paste()` through `runFor()`,
`RecordingStateTest`'s `asPeer()` calling `forget()`); afterwards every test
request starts with no current Group, as a real one does, and those
workarounds can go (found by `T-127`'s test writer, 26 September 2026).

## Decisions taken to make this specifiable

Brought to ready on 27 September 2026, from the code and a full run.

**The reset lives in `Tests\TestCase`, around each request: `call()` forgets
the container's scoped instances first.** Every test request — `get()`,
`post()`, `json()` — goes through `MakesHttpRequests::call()`, and
`forgetScopedInstances()` is what the framework does between requests where
one process serves many. It is the test harness that differs from
production, so the fix is in the harness: nothing changes in
`SetCurrentGroup`, whose request already ends with its process.

**`Terminology` is reset with it.** The other `scoped()` binding memoises
each Group's vocabulary, and a memo carried between requests would hide a
vocabulary change the same way.

**`artisan()` is reset too.** A command runs in a process of its own, and
tests that call a command after setting a Group do the same `forget()` by
hand today.

**Nothing leaned on the leak.** The full suite, 1449 cases, passed with the
reset in place before anything else changed: the tasks that met the leak had
already worked round it. So the proof that the reset works is a test of its
own, which fails without it.

**The workarounds that precede a request or a command go; the rest stay.**
A `forget()` before a Peer's request (`asPeer()` in `RecordingStateTest`,
`OpenChatTest`, `OpenMaterialTest` and `CalendarInviteTest`, `peerPage()` and
two inline calls in `CancelLiveEpisodeTest`, one in `PeerNoteTest`), one
before `qori:series:purge` in `SeriesChatTest`, and `CalendarInviteTest`'s
`Terminology::forget()` before a download are the harness's job now.
`QuietReminderTest`'s, at the end of a test, never did anything. A `forget()`
before a service is called directly, outside any request or command
(`RefreshConnectionsCommandTest`'s two, `MaterialsTest`'s, `OpenMaterialTest`'s
second), stays: no harness sees that call. So do `RecordingTest`'s `paste()`
and `hide()`, which call a service inside `runFor()` — the right way to give a
direct call its Group in any case.

**Only the start of a request is reset.** What the test does after a request
still sees the Group that request set, which is how a test's assertions read
the rows the request wrote.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- `Tests\TestCase::call()` and `artisan()`.
- `tests/Feature/TestHarnessTest.php`.
- Removing the redundant `forget()` calls.

**Out:**

- Anything in `app/`.
- A `forget()` before a direct service call, which no harness can see.

## Files

| Path                                             | Change | Notes                             |
| ------------------------------------------------ | ------ | --------------------------------- |
| `tests/TestCase.php`                             | edit   | `call()` and `artisan()` reset    |
| `tests/Feature/TestHarnessTest.php`              | new    | 4 cases                           |
| `tests/Feature/Series/RecordingStateTest.php`    | edit   | `asPeer()` drops its `forget()`   |
| `tests/Feature/Shared/OpenChatTest.php`          | edit   | the same                          |
| `tests/Feature/Shared/OpenMaterialTest.php`      | edit   | the same, in `asPeer()` only      |
| `tests/Feature/Shared/CalendarInviteTest.php`    | edit   | the same, and a `Terminology` one |
| `tests/Feature/Series/CancelLiveEpisodeTest.php` | edit   | `peerPage()` and two inline calls |
| `tests/Feature/Share/PeerNoteTest.php`           | edit   | one before a request              |
| `tests/Feature/Series/SeriesChatTest.php`        | edit   | one before a command              |
| `tests/Feature/Series/QuietReminderTest.php`     | edit   | one at the end of a test          |

## Database

None.

## Code

```php
// Tests\TestCase
public function call($method, $uri, $parameters = [], $cookies = [], $files = [], $server = [], $content = null): TestResponse;
// $this->app->forgetScopedInstances(); return parent::call(...)

public function artisan($command, $parameters = []): PendingCommand|int;
// $this->app->forgetScopedInstances(); return parent::artisan(...)
```

## Copy

None.

## Routes

None: the harness test registers its probes at runtime, as
`ReachabilityTest` does.

## Tests

**New: `tests/Feature/TestHarnessTest.php` — 4 cases**

1. `test_a_request_starts_with_no_current_group` — a Group set in the test;
   a probe route answers that none is current.
2. `test_a_creators_group_does_not_carry_into_the_next_request` — the
   creator's Series page, then the probe.
3. `test_the_vocabulary_is_read_afresh_for_each_request` — the Group's words
   memoised in the test, then changed; the probe reads the new ones.
4. `test_a_command_starts_with_no_current_group` — a Group set; a probe
   command reports none.

**Changed:** the eight files above lose their workarounds; every case passes
as before.

## Acceptance

- [x] A test request and a test command start with no current Group and no
      remembered vocabulary
- [x] The harness test fails without the reset
- [x] The workarounds before a request or a command are gone
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Where the reset lives: a hook in `Tests\TestCase` around each request
  (Laravel's `beforeApplicationDestroyed()` is per test, not per request),
  or a terminating callback in `SetCurrentGroup`, or forgetting scoped
  instances between requests the way Octane does — anyone's, from the code.~~
  **Answered from the code, 27 September 2026:** `Tests\TestCase::call()`,
  forgetting the scoped instances the way a server between requests does
  (Decisions).
- ~~Which existing tests lean on the leak today and start failing once it is
  gone — anyone's: run the suite with the reset in place and list them.~~
  **Answered 27 September 2026:** none; 1449 passed with the reset in place
  (Decisions).

## Re-scope log

None.

## Notes

None.
