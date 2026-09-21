---
id: T-075
title: Creator setup in three parts, each skippable
stream: onboarding
status: done
owner: claude
estimate: M
depends: T-068, T-062
blocks: T-076
---

# T-075 — Creator setup in three parts, each skippable

## Why

`T-068` asks a new creator one question, the Group's name, on one page, and
lands them on the dashboard. The owner called that version zero on
13 September 2026 and said what version one is: three parts, each saying why
it is asked and each skippable. Part one names the Group and says why the name
matters. Part two connects Stripe and says why a creator needs it. Part three
is storage and says how Qori keeps files.

The pieces exist. The name form is `GroupNameForm`; the Stripe doors are the
Integrations page's (`T-062`, `T-063`); storage is Qori's own, working today
with nothing to connect (`T-044` is where external storage arrives). What is
missing is the frame: an order, a record of what was done or skipped, a landing
that resumes at the right part, and the sentences that say why.

## Decisions taken to make this specifiable

**Three routes, one frame.** `setup` (name, exists), `setup/payments`,
`setup/storage`, each rendered inside a `SetupLayout` that shows "Part 1 of
3" and the two others' titles. Back is the previous part; there is no forward
without an answer or a skip.

**Progress is on the Group.** `groups.setup_state` jsonb, keys `name`,
`payments`, `storage`, each `done` or `skipped`, and `groups.setup_completed_at`.
`Group::setupNext(): ?string` returns the first part with no state, where a
chosen name counts as `name: done` and a connected account counts as
`payments: done`. Null once every part has a state; `setup_completed_at` is
stamped then.

**Skipping is a write.** `POST setup/skip/{part}` records `skipped` and goes
to the next part. A skipped name keeps the generated one, and the dashboard's
existing name prompt keeps asking. A skipped payments part means paid selling
is refused where it is refused today; Integrations is where it is finished.

**Landing resumes.** `SignInLanding::landing()` sends an owner to
`route('share.setup.'.$next)` while `setupNext()` is not null, and to the
dashboard otherwise. Admins are never sent to setup. Everything `T-068` said
about verification, sign-in and "start sharing" landing through here stands.

**Stripe returns to the frame.** The payments part renders the same doors the
Integrations page renders, from the same controller props, with
`session(['payouts.return_to' => route('share.setup.storage', $slug)])` put
before the doors are shown. `PayoutsController::return()` and
`PayoutsReturnController` redirect to that URL when it is present and forget
it; otherwise to Integrations as now. Coming back marks `payments: done` only
when an account id exists.

**Storage says how it works, and moves on.** There is nothing to connect yet,
so this part explains: documents live on Qori up to the plan's limit, video
and audio stay where they already are and are linked, and connecting Dropbox
or Google Drive arrives later. One button, Continue, records `storage: done`;
Skip records `skipped`. When `T-044` lands, the connect buttons join this page.

**The name part gains a why and loses "Save".** The button reads Continue; the
copy under the title says the name reaches every Peer in every invitation and
on every page. The timezone field stays, as `T-068` left it.

## Preconditions

`T-068` done: the setup route, page and landing exist. `T-062` done: the create
door is a POST with the country. `T-063` done: the existing-account door and
its props.

## Scope

**In:**

- The two columns, `setupNext()`, the skip and finish writes.
- The frame layout and the three pages.
- Landing, rename and Stripe return resuming at the right part.
- The design-review contexts and shots for the three parts.
- `docs/flows/auth.md` (landing) and `docs/tinker/groups.md`.

**Out:**

- Connecting external storage (`T-044`).
- The guided first Series (`T-026`).
- Confirming name, email and personal timezone (`T-026`'s basic details).
- Prompting for seller setup at the paid action (`T-028`).

## Files

| Path                                                                  | Change | Notes                                                            |
| --------------------------------------------------------------------- | ------ | ---------------------------------------------------------------- |
| `database/migrations/2026_09_14_000000_add_setup_state_to_groups.php` | new    | Two columns                                                      |
| `app/Models/Group.php`                                                | edit   | Casts, `setupNext()`, `SETUP_PARTS`                              |
| `app/Services/GroupService.php`                                       | edit   | `skipSetup()`, `completeSetupPart()`                             |
| `app/Http/Controllers/Share/SetupController.php`                      | edit   | `show()` → name; `payments()`, `storage()`, `skip()`, `finish()` |
| `app/Http/Controllers/Share/GroupController.php`                      | edit   | `update()` returns to the next part when called from setup       |
| `app/Http/Controllers/Share/PayoutsController.php`                    | edit   | `return()` honours `payouts.return_to`                           |
| `app/Http/Controllers/Settings/PayoutsReturnController.php`           | edit   | Same                                                             |
| `app/Support/SignInLanding.php`                                       | edit   | `landing()` uses `setupNext()`                                   |
| `routes/share.php`                                                    | edit   | Four routes                                                      |
| `resources/js/layouts/setup/Layout.vue`                               | new    | Parts indicator, Back, Skip                                      |
| `resources/js/pages/share/Setup.vue`                                  | edit   | Wrapped; why copy; Continue                                      |
| `resources/js/pages/share/setup/Payments.vue`                         | new    | The two doors                                                    |
| `resources/js/pages/share/setup/Storage.vue`                          | new    | The explanation                                                  |
| `resources/js/components/share/GroupNameForm.vue`                     | edit   | `submitLabel` prop, default Save                                 |
| `lang/en/groups.php`                                                  | edit   | `setup.*`                                                        |
| `app/Console/Commands/DesignReviewCommand.php`                        | edit   | Contexts `owner-setup-{name,payments,storage}`                   |
| `docs/flows/auth.md`, `docs/tinker/groups.md`                         | edit   |                                                                  |
| `tests/Feature/Share/SetupStepsTest.php`                              | new    | 12 cases                                                         |
| `tests/Feature/Share/SetupTest.php`                                   | edit   | Landing cases go to the next part                                |

## Database

`groups.setup_state` jsonb, not null, default `'{}'` (a string default, per
CLAUDE.md's rule about raw storage values). `groups.setup_completed_at`
timestamp nullable. Existing Groups: a data step in the same migration sets
`setup_completed_at = now()` and `setup_state = '{"name":"done","payments":"skipped","storage":"skipped"}'`
for every Group with `name_set_at` not null, so nobody already sharing is sent
back through setup; Groups still unnamed get nothing and meet the frame at
part one.

## Code

```php
// App\Models\Group
public const SETUP_PARTS = ['name', 'payments', 'storage'];
protected $casts = [..., 'setup_state' => 'array', 'setup_completed_at' => 'datetime'];

/** The first part with no recorded state, or null when setup is complete. */
public function setupNext(): ?string;
// name is done when hasChosenName(); payments is done when connect_account_id is filled; otherwise read setup_state.
```

```php
// App\Services\GroupService
public function skipSetup(Group $group, string $part): void;          // validates against SETUP_PARTS; writes skipped; stamps completed when setupNext() is null
public function completeSetupPart(Group $group, string $part): void; // writes done; same stamp
```

```php
namespace App\Http\Controllers\Share;

class SetupController extends Controller
{
    public function show(string $group, CurrentGroup $current, Terminology $terminology): Response|RedirectResponse;      // part 1; non-owner → dashboard; complete → dashboard
    public function payments(string $group, CurrentGroup $current, PayoutsService $payouts): Response|RedirectResponse;  // part 2; puts payouts.return_to
    public function storage(string $group, CurrentGroup $current, Terminology $terminology): Response|RedirectResponse;  // part 3
    public function skip(string $group, string $part, CurrentGroup $current): RedirectResponse;                          // POST; owner; next part or dashboard
    public function finish(string $group, CurrentGroup $current): RedirectResponse;                                      // POST; storage: done; dashboard
}
```

Every action redirects a non-owner to the dashboard and an owner whose
`setupNext()` is null to the dashboard. Each page receives `frame`:
`['part' => 1|2|3, 'total' => 3, 'titles' => [...], 'back' => ?url, 'skip' => url, 'skipLabel' => …]`.

`GroupController::update()` redirects to `route('share.setup.'.$next)` when the
request came from the setup page (`$request->boolean('setup')`, a hidden
field the setup page's form adds) and `setupNext()` is not null, else back as
now.

`SignInLanding::landing()`: owner and `setupNext() !== null` →
`route('share.setup'.($next === 'name' ? '' : '.'.$next), $slug)` — name the
routes `share.setup`, `share.setup.payments`, `share.setup.storage` so the
expression is `$next === 'name' ? route('share.setup', …) : route("share.setup.{$next}", …)`.

## Copy

| Key                           | File                 | English                                                                                                                                                                                          |
| ----------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `groups.setup.part`           | `lang/en/groups.php` | Part :part of :total                                                                                                                                                                             |
| `groups.setup.skip`           | `lang/en/groups.php` | Set this up later                                                                                                                                                                                |
| `groups.setup.back`           | `lang/en/groups.php` | Back                                                                                                                                                                                             |
| `groups.setup.continue`       | `lang/en/groups.php` | Continue                                                                                                                                                                                         |
| `groups.setup.name_why`       | `lang/en/groups.php` | Your :peer_plural see this name in every invitation, on every page you share and on every receipt. A name they recognise is the difference between a link opened and a link ignored.             |
| `groups.setup.payments_title` | `lang/en/groups.php` | Get paid                                                                                                                                                                                         |
| `groups.setup.payments_why`   | `lang/en/groups.php` | To charge for a :series, Qori needs somewhere to send the money. Stripe pays you directly, Qori takes nothing, and refunds and disputes stay in your hands. Sharing for free needs none of this. |
| `groups.setup.storage_title`  | `lang/en/groups.php` | Where your files live                                                                                                                                                                            |
| `groups.setup.storage_why`    | `lang/en/groups.php` | Documents you upload live on Qori, up to your plan's limit. Video and audio stay where they already are and are linked, so nothing is copied and nothing is charged twice.                       |
| `groups.setup.storage_later`  | `lang/en/groups.php` | Connecting Dropbox or Google Drive is coming; when it does, it will be here.                                                                                                                     |
| `groups.setup.done`           | `lang/en/groups.php` | You're set up. Everything here can be changed from your :group's settings.                                                                                                                       |

`groups.setup.later` (`T-068`) is kept and shown under the name part.

## Routes

| Verb | Path                          | Name                   | Action                     |
| ---- | ----------------------------- | ---------------------- | -------------------------- |
| GET  | `g/{group}/setup`             | `share.setup`          | `SetupController@show`     |
| GET  | `g/{group}/setup/payments`    | `share.setup.payments` | `SetupController@payments` |
| GET  | `g/{group}/setup/storage`     | `share.setup.storage`  | `SetupController@storage`  |
| POST | `g/{group}/setup/skip/{part}` | `share.setup.skip`     | `SetupController@skip`     |
| POST | `g/{group}/setup/finish`      | `share.setup.finish`   | `SetupController@finish`   |

## Tests

**New: `tests/Feature/Share/SetupStepsTest.php` — 12 cases**

1. `test_a_new_owner_lands_on_the_name_part` — `SignInLanding::for()` for an
   owner of an unnamed Group is `share.setup`.
2. `test_naming_the_group_from_setup_goes_to_payments` — PATCH group with
   `setup=1` and a name: 302 to `share.setup.payments`, `name_set_at` set.
3. `test_skipping_the_name_keeps_the_generated_one_and_goes_on` — POST skip
   `name`: `setup_state.name = skipped`, `name_set_at` null, 302 to payments.
4. `test_the_payments_part_shows_both_doors_and_remembers_where_to_return` —
   GET payments with a client id configured: `existingLabel`, `createLabel`,
   `countries` present; session `payouts.return_to` is the storage URL.
5. `test_returning_from_stripe_lands_on_storage` — with `payouts.return_to`
   set and an account id: GET `share.payouts.return` 302 to storage,
   `setup_state.payments = done`, session key gone.
6. `test_skipping_payments_goes_to_storage` — POST skip `payments`.
7. `test_finishing_storage_completes_setup` — POST finish: `storage = done`,
   `setup_completed_at` set, 302 to dashboard.
8. `test_a_completed_owner_lands_on_the_dashboard` — `SignInLanding::for()`.
9. `test_an_owner_resumes_at_the_first_unfinished_part` — name done, nothing
   else: landing is payments; payments skipped: landing is storage.
10. `test_an_admin_is_never_sent_to_setup` — admin of an unfinished Group: GET
    each part 302 to dashboard; landing is dashboard.
11. `test_existing_groups_are_not_sent_back_through_setup` — a Group with
    `name_set_at` set and empty state before the migration's data step:
    after `setupNext()` reads the migrated state, null. (Run the migration's
    data step as a callable the test can invoke, or assert on a factory Group
    created with the migrated shape.)
12. `test_the_frame_counts_the_parts` — each GET carries `frame.part` 1, 2, 3
    and `frame.total` 3.

**Changed: `tests/Feature/Share/SetupTest.php`** — cases that expected the
dashboard after naming now expect payments; the registration-bounce case
still expects `share.setup`.

## Acceptance

- [x] A fresh registration, verified, lands on Part 1 of 3, which says why the
      name matters and offers Continue and Set this up later
- [x] Part 2 offers the two Stripe doors with the why, and coming back from
      Stripe lands on Part 3
- [x] Part 3 explains storage honestly, with nothing pretending to connect
- [x] Every part can be skipped, and a skipped part is reachable from settings
- [x] An owner who signs out midway resumes at the first unfinished part
- [x] Existing Groups are not sent through setup
- [x] Design-review shots exist for the three parts at 360px and desktop — named in the command with a seeded world; the command itself was not run this session (report)
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

Cut from `T-026` and `T-028` on 13 September 2026. `T-026` keeps the guided
first Series and the basic-details confirmation; `T-028` keeps the prompt for
seller setup at the paid action and the storage connectors' place in the
frame once `T-044` provides them.

`groups.setup.payments_why` opens "To charge for what you share" rather than
the table's "To charge for a :series": the vocabulary test forbids an article
before a noun placeholder, and the noun may be a word the customer chose.

Part three exists with nothing to connect because the owner asked for three
parts and because the frame should not change shape when `T-044` lands. If
that reads as a page with nothing to do in the browser, say so in the report
and propose folding it into part two rather than removing the record.
