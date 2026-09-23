---
id: T-026
title: A new creator's first screen makes their first Series
stream: onboarding
status: ready
owner: unassigned
estimate: M
depends: T-068, T-024
blocks: T-195
---

# T-026 — A new creator's first screen makes their first Series

## Why

A new creator meets about ten screens before a share link: register, verify,
three setup parts (name, get paid, where files live), the first-Series action,
the Series form, the Episode form, make ready, the link. The owner, 23
September 2026: onboarding "is not quite there yet, it need to be simple
streamline no brainer, a couple of clicks" (`D-056`).

Afterwards a verified owner whose Group has no Series lands on one screen,
"What will you share first?": a title, three shapes, one button. It creates
the Series and lands on its Episode form already set up for the shape, so the
next click is choosing the file or the time. The Group keeps its generated
name, Stripe is asked where a price is typed and Google Drive where a file is
chosen, as the Series page already does.

## Decisions taken to make this specifiable

**The screen lives at the setup URL, `GET g/{group}/setup`, route
`share.setup`.** Every landing already sends an unfinished owner there
(`SignInLanding`, `HomeController::index()`, `DashboardController::show()`),
`OneGroupPerPersonTest` asserts it, and the design review shoots it. Only who
is sent and what renders change. Parts two and three stay until `T-195`.

**Who is sent: `User::needsFirstSeries(Group)`** — the owner, `onboarded_at`
null, and no Series in the Group (`Series::query()->forGroup($group)`, the
query `GroupService::nameInSetup()` uses, because a sign-in has no
`CurrentGroup`). An owner who already has a Series is past it whatever their
setup record says; `UserFactory` stamps `onboarded_at` by default, so the
suite's owners are not redirected.

**No empty Episodes are made** (`D-056`). The shape decides the first
Episode's form: `FirstSeriesShape::episodeType()` gives its kind, and the
title comes from `lang/en/onboarding.php` with the number interpolated. The
redirect carries both as query keys, `kind` and `title`, to
`share.series.show` at `#new-episode`, where the form already is.

**The form opens as the last Episode did.** With no query, `Show.vue` starts
the form on the last Episode's kind when it is still offered, and suggests the
next title when the last one ends in a number ("Part 1" → "Part 2"). The query
wins only while the Series has no Episodes, so a reload after the first save
does not suggest "Part 1" again. This is the outline Kajabi's blueprints give,
without an Episode existing before it has something in it.

**The timezone is asked only for the weekly shape, and only when the Group has
none.** A live session is refused without it
(`EpisodeService::guardLiveSessionTime()`). It is saved with
`GroupService::setTimezone()` before the Series is created, through the
`TimezoneField` the name card uses, validated as `UpdateGroupRequest` validates
it.

**Creating the Series ends onboarding; so does "I'll look around first".**
Both call `OnboardingService::finish()`, which stamps `onboarded_at` and never
unstamps it, so neither person is sent back. The name record in
`onboarding_state` is untouched: the dashboard's name card keeps asking until
the Group is renamed.

**The toast is `series.created`**, the line the Series form's own create
already says. No new one.

**Owner only.** An admin is sent to the dashboard from the page and refused on
both writes with `errors.group.owner_only_setup`, as the setup frame does.

## Preconditions

**Data this task verifies against:** a fresh registration, choosing to share,
verified. `php artisan qori:reset basic` for the rest of the world.

**Equipment:** a browser at 390px and 1440px, and Mailpit for the
verification link.

## Scope

**In:**

- The screen, its two writes, and `FirstSeriesShape`.
- Who lands there: the three home routes and `SignInLanding`.
- The Episode form opening from the query, then from the last Episode.
- `docs/flows/onboarding.md`, `docs/flows/auth.md` and the two tinker recipes
  that walk setup; the design-review context `691`.

**Out:**

- Removing parts two and three, `SetupSteps`, the frame, and the `setup` flag
  on `GroupController` (`T-195`).
- Coming back to the Series after connecting Stripe or Google Drive from it
  (`T-028`).
- Anything a Series-link recipient sees (`D-001` stands; `T-027`).
- The words of the dashboard's next actions (`T-191`).

## Files

| Path                                                  | Change | Notes                                                                        |
| ----------------------------------------------------- | ------ | ---------------------------------------------------------------------------- |
| `app/Enums/FirstSeriesShape.php`                      | new    | Three cases and `episodeType()`                                              |
| `app/Http/Requests/Share/StartFirstSeriesRequest.php` | new    | `title`, `shape`, `timezone`                                                 |
| `app/Http/Controllers/Share/SetupController.php`      | edit   | `show()` renders the screen; `store()`, `later()`; parts two and three stay  |
| `routes/share/setup.php`                              | edit   | Two `POST`s                                                                  |
| `app/Models/User.php`                                 | edit   | `needsFirstSeries()`                                                         |
| `app/Services/OnboardingService.php`                  | edit   | `finish()`                                                                   |
| `app/Support/SignInLanding.php`                       | edit   | `landing()` reads `needsFirstSeries()`                                       |
| `app/Http/Controllers/HomeController.php`             | edit   | `index()` reads `needsFirstSeries()`                                         |
| `app/Http/Controllers/Share/DashboardController.php`  | edit   | `show()` reads `needsFirstSeries()`                                          |
| `resources/js/pages/share/Setup.vue`                  | edit   | Rewritten as the screen                                                      |
| `resources/js/pages/share/series/Show.vue`            | edit   | The Episode form's first kind and title                                      |
| `lang/en/onboarding.php`                              | new    | The screen's lines and the two numbered titles                               |
| `app/Console/Commands/DesignReviewCommand.php`        | edit   | `691-setup-name` becomes `691-first-series`, same URL                        |
| `docs/flows/onboarding.md`                            | edit   | The screen, the rule, and parts two and three as unreached until `T-195`     |
| `docs/flows/auth.md`                                  | edit   | The landing line                                                             |
| `docs/tinker/groups.md`, `docs/tinker/e2e-first-share.md` | edit | The setup steps in each recipe                                             |
| `tests/Feature/Share/FirstSeriesTest.php`             | new    | 10 cases                                                                     |
| `tests/Feature/Share/SetupTest.php`, `tests/Feature/Share/SetupStepsTest.php`, `tests/Feature/Share/OnboardingHomeTest.php` | edit | See Tests |

## Database

None. `users.onboarded_at` and `users.onboarding_state` exist.

## Code

```php
namespace App\Enums;

enum FirstSeriesShape: string
{
    case Files = 'files';
    case Weekly = 'weekly';
    case Single = 'single';

    /** The kind the first Episode's form opens on; null leaves the form's own default. */
    public function episodeType(): ?EpisodeType; // Files → File, Weekly → Live, Single → null
}
```

```php
namespace App\Models;

class User
{
    /** The owner, not onboarded, whose Group has never had a Series. */
    public function needsFirstSeries(Group $group): bool;
}
```

```php
namespace App\Services;

class OnboardingService
{
    /** Stamps onboarded_at if it is null, merged into the stored row as record() does. */
    public function finish(User $user): User;
}
```

```php
namespace App\Http\Controllers\Share;

class SetupController
{
    public function show(Request $request, string $group, CurrentGroup $current, Terminology $terminology): Response|RedirectResponse;

    public function store(StartFirstSeriesRequest $request, string $group, CurrentGroup $current, SeriesService $series, GroupService $groups, Terminology $terminology): RedirectResponse;

    public function later(Request $request, string $group, CurrentGroup $current): RedirectResponse;
}
```

`show()` sends anyone for whom `needsFirstSeries()` is false to
`share.dashboard`, and renders `share/Setup` with `shapes` (each `value`,
`label`, `detail`), `needsTimezone` (`! $group->hasChosenTimezone()`),
`timezones` (`Timezones::grouped()`) and `copy`, every line through
`Terminology::line()` with the Group. `payments()` and `storage()` keep
`away()` unchanged.

`store()` guards the owner, saves the timezone when the shape is weekly and
the Group has none, creates the Series with `SeriesService::create()`, calls
`finish()`, flashes `series.created`, and redirects to
`route('share.series.show', ['group' => …, 'series' => …, 'kind' => …, 'title' => …]).'#new-episode'`,
leaving `kind` out for `Single`. The title is
`onboarding.first.episode_title.files` or `.weekly` with `:number` 1, or the
Series' own title for `Single`.

`StartFirstSeriesRequest`: `title` as `StoreSeriesRequest` has it; `shape`
required, `Rule::enum(FirstSeriesShape::class)`; `timezone` required when the
shape is weekly and the Group has no timezone, otherwise excluded, and
`Rule::in(Timezones::all())`.

`Show.vue`: the form's first `type` is the `kind` query when the Series has no
Episodes and `kind` is in `types`, else the last Episode's `type` when it is
in `types`, else today's default. The title input's first value is the `title`
query under the same condition, else the last Episode's title with its
trailing number plus one, else empty.

## Copy

All in `lang/en/onboarding.php`. The toast and the owner-only refusal reuse
`series.created` and `errors.group.owner_only_setup`.

| Key                                   | English                                                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `onboarding.first.heading`            | What will you share first?                                                                                   |
| `onboarding.first.lead`               | Give it a name and pick the shape closest to it. Everything can change later, and nothing is shared until you say so. |
| `onboarding.first.title_label`        | What is it called?                                                                                           |
| `onboarding.first.title_placeholder`  | The thing people keep asking you about                                                                       |
| `onboarding.first.shapes.files.label` | A course of files                                                                                            |
| `onboarding.first.shapes.files.detail` | Documents, slides or videos, one :episode at a time.                                                        |
| `onboarding.first.shapes.weekly.label` | A class, week by week                                                                                       |
| `onboarding.first.shapes.weekly.detail` | Live sessions on a schedule, each with its own time.                                                       |
| `onboarding.first.shapes.single.label` | One thing                                                                                                   |
| `onboarding.first.shapes.single.detail` | A single file, video or session. Add more whenever you like.                                               |
| `onboarding.first.timezone_label`     | Your sessions are scheduled in                                                                               |
| `onboarding.first.timezone_help`      | Everyone is shown the time in their own zone.                                                                |
| `onboarding.first.create`             | Create :series                                                                                               |
| `onboarding.first.later`              | I'll look around first                                                                                       |
| `onboarding.first.episode_title.files` | Part :number                                                                                                |
| `onboarding.first.episode_title.weekly` | Week :number                                                                                               |

No "charge" anywhere (the owner's word, 23 September 2026). No article
immediately before a placeholder.

## Routes

| Verb   | Path                    | Name                | Action                     |
| ------ | ----------------------- | ------------------- | -------------------------- |
| `GET`  | `g/{group}/setup`       | `share.setup`       | `SetupController::show`    |
| `POST` | `g/{group}/setup`       | `share.setup.store` | `SetupController::store`   |
| `POST` | `g/{group}/setup/later` | `share.setup.later` | `SetupController::later`   |

The `GET` exists; its action's page changes.

## Tests

**New: `tests/Feature/Share/FirstSeriesTest.php` — 10 cases**

1. `test_a_verified_new_owner_lands_on_the_first_series_page` — register to
   share, verify, follow the redirects: `share.setup`, component `share/Setup`.
2. `test_the_page_offers_three_shapes_and_asks_the_timezone_only_when_missing`
   — `shapes` has three values; `needsTimezone` true, then false once the
   Group has one.
3. `test_a_course_of_files_creates_the_series_and_opens_a_file_form` — a draft
   Series, no Episode, `onboarded_at` set, the redirect's `kind=file` and
   `title=Part 1`.
4. `test_a_weekly_class_saves_the_timezone_and_opens_a_live_form` — the
   Group's timezone saved, `kind=live`, `title=Week 1`.
5. `test_a_weekly_class_without_a_timezone_is_refused_on_that_field` — no
   Series, an error on `timezone`.
6. `test_one_thing_titles_the_form_after_the_series` — no `kind`; `title` is
   the Series title.
7. `test_later_goes_to_the_dashboard_and_is_not_asked_again` — `onboarded_at`
   set; the next sign-in lands on `share.dashboard`.
8. `test_an_owner_whose_group_has_a_series_is_not_sent_there` — with
   `onboarded_at` null, `/dashboard` and a sign-in land on the Group's home.
9. `test_an_admin_is_not_sent_there_and_cannot_create_from_it` — the page
   redirects to the dashboard; `store` and `later` refuse with
   `errors.group.owner_only_setup`.
10. `test_a_series_page_the_person_was_bounced_from_still_wins` — an intended
    public Series URL beats the first-Series page, as `SignInLanding::isHome()`
    already rules.

**Changed:**

- `SetupTest` — the four "lands on setup" cases now arrange an owner with no
  Series rather than an unnamed Group; `test_a_named_group_signs_in_to_its_dashboard`
  becomes a Group with a Series; `test_the_setup_page_offers_the_name_form`
  moves to case 2 above. The naming cases stay until `T-195`.
- `SetupStepsTest` — `test_a_new_owner_lands_on_the_name_part`,
  `test_a_completed_owner_lands_on_the_dashboard` and
  `test_an_owner_resumes_at_the_first_unfinished_part` follow the new rule;
  the parts' own cases stay until `T-195`.
- `OnboardingHomeTest` — the three redirect cases arrange an owner with no
  Series.

The Episode form's first kind and title are client-side; the browser walk
checks them.

## Acceptance

- [ ] A fresh registration to share, verified, lands on "What will you share
      first?" at 390px and 1440px, and two clicks after typing a title reach
      the Episode form set up for the shape
- [ ] Each shape opens the form on the right kind and title; weekly asks the
      timezone only when the Group has none
- [ ] After the first Episode is saved, the form suggests the next title
- [ ] "I'll look around first" lands on the dashboard and is not asked again;
      an owner with a Series and an admin are never sent to the screen
- [ ] `docs/flows/onboarding.md`, `docs/flows/auth.md` and both tinker recipes
      describe the screen
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

**2026-09-11 — owner changed the target while this task was draft.** The prior
exclusion of any staged setup, the Series-first onboarding order and the
collapse-only checklist recommendation are superseded. Setup comes first;
storage, integrations and seller payments can be skipped. No implementation
attempt was started or stopped.

**2026-09-13 — the frame is cut out.** `T-075` builds the three-part skippable setup (name, Stripe, storage) with progress on the Group. What remains here is the basic-details confirmation and the guided first Series after it.

**2026-09-23 — re-scoped at the owner's word to one screen (`D-056`).** The
owner read the Kajabi note's blueprint proposal and said onboarding needs to
be "a couple of clicks", then "yes re-scope T-026 to that shape". Everything
above the log is rewritten: the staged frame, basic-details confirmation and
guided checklist are gone, and the task is the first-Series screen. The
proposal put to the owner laid out empty Episodes in advance; the code check
recorded in `D-056` replaced that with a form opened on the right kind and
title. Estimate L becomes M, with the retirement of the three parts cut out as
`T-195`. Brought to ready the same day.

## Notes

R-003's recorded path and working first-Series form remain valid historical
evidence. T-024 is completed work to reuse. The next-sprint creator-home
composition applies after setup and must be designed with this guide, not
implemented as a competing first-run page. Seller setup is prompted before
paid selling if it was skipped or remains incomplete; T-028 owns that rule.

**17 September 2026 — [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-9.** Fresh zero/one-Series home captures still prioritise meter layouts over a Series-shaped beginning or the one real object. The first action itself held up live: Fern's Create Series opens and focuses Title, then saves a private draft with a clear missing-Episode explanation. Do not report first-Series creation as absent. Keep object composition/guidance together in this draft; no competing meter-removal task was created. Upload and the complete ready/share loop were not verified because browser file-chooser tooling failed.

**23 September 2026 — the owner, reading the Kajabi note's blueprint
proposal:** onboarding "is not quite there yet; it needs to be simple,
streamlined, a no-brainer, a couple of clicks." Today a new creator meets
about ten screens before a share link: register, verify, three setup parts,
the first-Series action, the Series form, the Episode form, make ready, the
link. A streamlined shape was put to the owner the same day — one screen
asking what they will share first, with three shapes that create the Series
and its draft Episodes, the Group name defaulted, Stripe and storage asked
only when a price is set or a file chosen. If the owner takes it, this task is
re-scoped to that and the 11 September order (setup first) is superseded by a
decision record.
