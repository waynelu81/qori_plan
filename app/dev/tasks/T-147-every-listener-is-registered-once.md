---
id: T-147
title: Every listener is registered once
stream: operations
status: done
owner: wayne
estimate: S
depends: none
blocks: none
---

# T-147 — Every listener is registered once

## Why

`php artisan event:list --event=Registered` lists
`App\Listeners\CreateGroupForNewUser` twice: once as
`App\Listeners\CreateGroupForNewUser`, from
`Event::listen(Registered::class, CreateGroupForNewUser::class)` in
`AppServiceProvider::boot()` (`app/Providers/AppServiceProvider.php:48`), and
once as `App\Listeners\CreateGroupForNewUser@handle`, from Laravel's event
discovery, which is on because `bootstrap/app.php` leaves the `withEvents()`
that `Application::configure()` calls as it is. Every sign-up runs the listener
twice.

Nothing breaks only because the second run returns early. The first has seated
the person as owner, and `CreateGroupForNewUser::handle()` stops when
`$user->collaborations()->exists()`
(`app/Listeners/CreateGroupForNewUser.php:45`). Without that line the second
run would reach `GroupService::createFor()`, whose one-Group guard throws a
`LogicException` (`app/Services/GroupService.php:37-41`), and every sign-up
would fail. A listener registered the same way without such a guard would act
twice for one event; `T-091`'s `ResumeGrantsAfterReconnect` is the next one
planned.

Afterwards discovery is the one way a listener is registered, each listener is
registered once for each event it handles, and a test fails the day that stops
being true.

## Decisions taken to make this specifiable

**Discovery stays and the hand registration goes**, rather than turning
discovery off and registering every listener by hand. Every class in
`app/Listeners` has a typed `handle()`, so discovery finds each one with no
configuration; `bootstrap/app.php` stays as the framework writes it; and
`T-091` already specifies its listener as found by event discovery and
registered nowhere else. A hand-kept list is one somebody has to remember to
extend, and a listener nobody registered never runs, silently.

**The check reads the dispatcher's listeners, not `event:list`'s output.**
`Event::getRawListeners()` is the array `event:list` prints from
(`EventListCommand::getListenersOnDispatcher()`), as data. The console table
changes shape with the terminal's width and the framework's version.

**A listener is compared as `Class@method`, the way the dispatcher calls it.**
A bare class means `handle()`, or `__invoke()` when the class has no
`handle()`, and a `[class, method]` array is the same pair
(`Dispatcher::createClassCallable()`). So `CreateGroupForNewUser` and
`CreateGroupForNewUser@handle` are one listener registered twice, which is the
defect, and not two listeners. Closures are left out: they carry no class to
compare, and every one registered today is the framework's or a package's.

**Every event is checked, not only Qori's listeners.**
`EventServiceProvider::configureEmailVerification()` registers
`SendEmailVerificationNotification` on `Registered` unless that provider's own
`$listen` names it, and it never asks the dispatcher. A provider that also
registered it by hand would mail two verification links per sign-up, and the
same case catches that.

**Each listener in `app/Listeners` is registered exactly once, not at most
once.** The expected set is what the framework's own
`DiscoverEvents::within(app_path('Listeners'), base_path())` finds there, so
the case holds no second copy of discovery's rules. Zero is as broken as two —
a sign-up with no Group — and zero is what turning discovery off without
registering by hand, or a stale `bootstrap/cache/events.php`, would produce.

**One case goes through the event and counts the calls.** `GroupService` is
replaced with `$this->mock()` expecting `createFor()` once, and one
`Registered` event is dispatched. The mock writes nothing, so the listener's
early return cannot hide a second run: the case fails today with two calls,
which is the defect as a person would describe it rather than as an array
shape.

**The rule is written once, in `CLAUDE.md`**, as one bullet under "Where code
lives". `T-091` and whatever follows it add listeners, and `T-091`'s author
found the double registration only by running `event:list`.

**The flow doc's stale reason goes with the stale registration.**
`docs/flows/auth.md` says the listener hangs off the event "because two
registration controllers exist in this codebase and only route ordering
decides which one runs". One exists (`POST /auth/register`, Fortify's
`RegisteredUserController`), and the listener's own docblock already gives the
reason that holds: the event is what every registration path emits, including
ones not built yet. The paragraph is rewritten whole rather than half.

**`CreateGroupForNewUser` is not touched.** Its early return stays right for a
replayed event — `docs/tinker/auth.md` fires `Registered` by hand — and for
anyone who already has a Group.

## Preconditions

The local Postgres container on port 5433 (`docker compose up -d`), with this
checkout's `_testing` database: `qori_testing`, or `qori_wtN_testing` in a
worktree (CLAUDE.md, Tests).

**Data this task verifies against:** A clean database. The cases make their own
user; the tinker recipe is run against a development database of the
developer's choosing, and in a worktree that is `qori_wtN`, never the shared
`qori`.

**Equipment:** None.

## Scope

**In:**

- Deleting the hand registration from `AppServiceProvider::boot()`, and the
  three imports only it used.
- `tests/Feature/ListenerRegistrationTest.php`: two cases over the
  dispatcher's listeners and one through the `Registered` event.
- The registration paragraph of `docs/flows/auth.md`, one bullet in
  `CLAUDE.md`, and the sentence in `T-091` that calls the double registration
  current.

**Out:**

- `bootstrap/app.php` and discovery's paths. `Application::configure()`
  already calls `withEvents()`, and nothing is added to say so again.
- Whether a deploy runs `php artisan event:cache` or `optimize`. The cache is
  built by the same discovery and holds the same set.
- `CreateGroupForNewUser` itself (Decisions), and `SeriesAccessController`
  not firing `Registered`, which `docs/flows/auth.md` records as deliberate.
- Closure listeners registered by the framework and packages.
- `docs/tinker/auth.md`. Its recipe fires `Registered` once and gets one
  Group, before and after this task; it is run, not edited.

## Files

| Path                                                                                     | Change | Notes                                              |
| ---------------------------------------------------------------------------------------- | ------ | -------------------------------------------------- |
| `app/Providers/AppServiceProvider.php`                                                   | edit   | `boot()` loses its last line; three imports go     |
| `tests/Feature/ListenerRegistrationTest.php`                                             | new    | 3 cases                                            |
| `docs/flows/auth.md`                                                                     | edit   | The paragraph under the Registration diagram       |
| `CLAUDE.md`                                                                              | edit   | One bullet under "Where code lives"                |
| `docs/planning/tasks/T-091-every-peer-with-access-is-granted-on-the-series-container.md` | edit   | Wording only: the double registration becomes past |

The flow file is `docs/flows/auth.md`. `docs/tinker/auth.md` is run to confirm
its registration recipe still gives one Group, and is not changed.

## Database

None.

## Code

```php
// App\Providers\AppServiceProvider — boot() without its last line. The imports
// only that line used go with it: App\Listeners\CreateGroupForNewUser,
// Illuminate\Auth\Events\Registered and Illuminate\Support\Facades\Event.
public function boot(): void
{
    $this->configureDefaults();
    $this->guardProductionDatabase();
    $this->configureRateLimiting();
    $this->configurePasskeys();
}
```

```php
namespace Tests\Feature;

use App\Listeners\CreateGroupForNewUser;
use App\Models\Group;
use App\Models\User;
use App\Services\GroupService;
use Illuminate\Auth\Events\Registered;
use Illuminate\Foundation\Events\DiscoverEvents;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Str;
use Mockery\MockInterface;
use Tests\TestCase;

/**
 * Every listener is registered once for each event it handles (T-147): the
 * Why of the task in a paragraph, naming discovery, the hand registration it
 * doubled, and the early return that hid it.
 */
class ListenerRegistrationTest extends TestCase
{
    use RefreshDatabase;

    public function test_no_listener_is_registered_twice_for_one_event(): void;
    // For each event in registered(), array_count_values() of its listeners;
    // every count above 1 is an offender, written
    // "<listener> is registered <n> times for <event>".
    // assertSame([], $offenders, 'A listener registered twice runs twice for one event. Event discovery already registers every class in app/Listeners; delete the Event::listen() that registers it again.')

    public function test_every_listener_in_app_listeners_is_registered_once_for_its_event(): void;
    // $discovered = DiscoverEvents::within(app_path('Listeners'), base_path());
    // First assertContains(CreateGroupForNewUser::class.'@handle', $discovered[Registered::class] ?? []),
    // so a walk that found nothing cannot pass.
    // Then for each event and each listener discovery found for it, its count
    // in registered()[$event] ?? []; every count other than 1 is an offender,
    // in the same words as above.
    // assertSame([], $offenders, 'Each class in app/Listeners is registered once, by event discovery. None means discovery is off or bootstrap/cache/events.php is stale (php artisan event:clear); two means an Event::listen() registers it again.')

    public function test_one_registered_event_asks_for_one_group(): void;
    // $user = User::factory()->create();
    // $this->mock(GroupService::class, fn (MockInterface $mock) => $mock->shouldReceive('createFor')->once()->andReturn(new Group));
    // event(new Registered($user));

    /**
     * Each event's class listeners as Class@method, the way the dispatcher
     * calls them: a bare class means handle(), or __invoke() when the class has
     * no handle(), and a [class, method] array is the same pair
     * (Dispatcher::createClassCallable()). A closure has no class to compare
     * and is left out. Str::parseCallback($listener, 'handle') splits a string.
     *
     * @return array<string, list<string>>
     */
    private function registered(): array;
}
```

The assertion messages are diagnostics for a developer, not copy (CLAUDE.md,
Errors and user-facing copy).

**`CLAUDE.md`**, a new bullet under "Where code lives", directly after the one
that begins "Dependencies:":

```markdown
- `app/Listeners` — found by Laravel's event discovery through the event each `handle()` takes, and registered nowhere else: an `Event::listen()` for one as well runs it twice per event (`T-147`, `ListenerRegistrationTest`).
```

**`docs/flows/auth.md`**, the paragraph that begins "Group creation hangs off
the **event**", replaced whole:

```markdown
Group creation hangs off the **event**, not off `CreateNewUser`, because the
event is what every registration path emits, including ones not built yet such
as a social sign-in. Laravel's event discovery registers the listener, by the
event its `handle()` takes, and nothing registers it again, so it runs once per
sign-up (T-147). `php artisan event:list --event=Registered` shows it beside
the framework's `SendEmailVerificationNotification`, which mails the
verification link.
```

**`T-091`**, in its reconnect paragraph, the clause from "`php artisan
event:list` lists" to "twice for one event." becomes:

```markdown
a second registration runs a listener twice for one event, as
`CreateGroupForNewUser` ran until `T-147` removed its hand registration from
`AppServiceProvider::boot()`, and `ListenerRegistrationTest` fails on one.
```

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/ListenerRegistrationTest.php` — 3 cases**

1. `test_no_listener_is_registered_twice_for_one_event` — fails today:
   `App\Listeners\CreateGroupForNewUser@handle is registered 2 times for Illuminate\Auth\Events\Registered`.
2. `test_every_listener_in_app_listeners_is_registered_once_for_its_event` —
   fails today with the same line; afterwards `CreateGroupForNewUser@handle` is
   registered once for `Registered`.
3. `test_one_registered_event_asks_for_one_group` — fails today with
   `createFor()` called twice where once was expected.

Total: 3. Write the file and run it before editing `AppServiceProvider`, and
quote the three failures in the report: they are the evidence that the defect
was real and that the cases would catch it again.

**Changed:** none expected. `SignupIntentTest` and `RegistrationTest` register
through Fortify and assert one Group, which the second run never added, so
they pass unchanged.

## Acceptance

- [x] `php artisan event:list --event=Registered` lists
      `App\Listeners\CreateGroupForNewUser@handle` and
      `Illuminate\Auth\Listeners\SendEmailVerificationNotification`, each once,
      and nothing else
- [x] `AppServiceProvider` registers no listener, and `bootstrap/app.php` is
      unchanged
- [x] The three cases fail before the provider edit and pass after it, and the
      report quotes the failures
- [x] `docs/flows/auth.md` says discovery registers the listener and gives the
      reason that holds; `CLAUDE.md` states the rule; `T-091` no longer calls
      the double registration current
- [x] The `docs/tinker/auth.md` registration recipe still gives one Group
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Added during execution

| Path                                                           | Change | Notes                                                                                               |
| -------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------- |
| `docs/planning/tasks/T-044-nothing-can-create-a-connection.md` | edit   | Cited `AppServiceProvider::boot()` as `:41-49`; the deleted line moves it to `:38-44`. Wording only |

## Re-scope log

None.

## Notes

The order on `Registered` is unchanged where it matters: the Group is still
made before the verification mail is sent. Discovery registers in the event
provider's booting callback and `SendEmailVerificationNotification` in its
booted callback, so after this task the two run in that order, as the discovered
copy and the mail did before it.

**Preconditions, wording.** "In a worktree that is `qori_wtN`" named a
development database that does not exist for most worktrees:
`qori:testing-databases` creates only the `_testing` ones, and `qori_wt1` is
the only `qori_wtN` on this machine. The recipe ran against `qori_wt3_testing`,
which the next test run migrates fresh, so nothing new was created and the
shared `qori` was not touched (19 September 2026).
