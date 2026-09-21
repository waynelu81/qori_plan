---
id: T-068
title: A new creator is asked to name their Group before anything else
stream: onboarding
status: done
owner: claude
estimate: S
depends: none
blocks: T-026, T-075
---

# T-068 — A new creator is asked to name their Group before anything else

## Why

The owner registered fresh on 13 September 2026, confirmed the address, and
landed on the dashboard. Nothing asked them anything. Registration names the
Group from the person's first name, verification sends everyone to the home
route, and the one place that asks for a name is a dashboard card keyed to the
next-action logic, which for a brand-new Group is "make your first Series". So
the moment the owner described — "once Rita registered she is asked to name
her group" — never happens.

The onboarding journey is designed (`ui-onboarding.md`) and split into three
`draft` tasks nobody could start, in a stream `PLAN.md` did not list. This is
the first slice of `T-026`, cut small enough to be ready: one question, asked
once, before anything else.

Afterwards: confirming the address, signing in, and choosing to start sharing
all land an owner whose Group has no chosen name on a page that asks for it,
and nowhere else. Naming it goes to the Group's home. Everything else the
journey wants — storage, integrations, payments, the guided first Series —
stays where it is and is asked later or not at all.

## Decisions taken to make this specifiable

**A landing, not a wall.** The gate lives in `SignInLanding`, which every
sign-in already goes through, and which verification and "start sharing" now
go through too. It is not middleware on the sharing surface: a person who
navigates away from the page is not trapped, and the dashboard's own name card
still catches them later. Asked once, at the front, is what the owner wants.

**Owners only.** An admin on an unnamed Group is never sent to name somebody
else's Group; they land on its dashboard as today.

**Reuse the form and the write.** `GroupNameForm` and `PATCH /g/{group}`
already exist and already stamp `name_set_at`. The setup page renders that
form; the update returns `back()` to the setup page, which sees the name is
chosen and goes on to the dashboard. No second write path.

**No app shell.** The page is the first thing a new creator sees, and a
sidebar of Series, Peers and Settings around one question reads as a product
they have not been introduced to. It uses the auth shell, like sign-in, and
the layout resolver names it as such.

**The factory now makes named Groups.** `Group::factory()` left `name_set_at`
null, so every test's Group was unnamed by accident; with this gate every
owner sign-in in the suite would land on setup. The factory default becomes
named, with an `unnamed()` state for the tests that mean it, which is what
`GroupService::createFor()` produces anyway.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The route, the controller, the page, the landing changes, the factory, the
  copy, the layout resolver case, `docs/flows/auth.md`.
- Adding the onboarding stream to `PLAN.md`'s table, and narrowing `T-026` to
  the guided first Series.

**Out:**

- Timezone, profile, storage, integrations, payments: `T-026`, `T-028`,
  `T-067`'s page.
- The dashboard's name card and the next-action logic.
- Arrival from a Series link (`T-027`).

## Files

| Path                                             | Change | Notes                                    |
| ------------------------------------------------ | ------ | ---------------------------------------- |
| `routes/share.php`                               | edit   | `GET setup`                              |
| `app/Http/Controllers/Share/SetupController.php` | new    | `show()`                                 |
| `app/Support/SignInLanding.php`                  | edit   | Owner of an unnamed Group lands on setup |
| `app/Http/Responses/VerifyEmailResponse.php`     | edit   | Lands through `SignInLanding`            |
| `app/Http/Controllers/HomeController.php`        | edit   | `startSharing()` lands through it too    |
| `database/factories/GroupFactory.php`            | edit   | `name_set_at`; `unnamed()`               |
| `resources/js/app.ts`                            | edit   | `share/Setup` takes the auth shell       |
| `resources/js/pages/share/Setup.vue`             | new    | The page                                 |
| `lang/en/groups.php`                             | edit   | `setup.lead`, `setup.later`              |
| `docs/flows/auth.md`                             | edit   | Where verification lands                 |
| `tests/Feature/Share/SetupTest.php`              | new    | 8 cases                                  |

## Database

None.

## Code

```php
// App\Support\SignInLanding
public static function for(User $user): string;   // unchanged signature; both Group branches go through:
private static function landing(User $user, Group $group): string;
// route('share.setup', $slug) when $group->owner_user_id === $user->getKey() && ! $group->hasChosenName()
// else route('share.dashboard', $slug)
```

```php
// App\Http\Controllers\Share\SetupController
public function show(string $group, CurrentGroup $current, Terminology $terminology): Response|RedirectResponse;
// not the owner, or the name already chosen → to_route('share.dashboard', $slug)
// else Inertia::render('share/Setup', [
//     'group' => ['slug', 'name'], 'timezones' => Timezones::grouped(), 'timezone', 'timezoneChosen',  (as DashboardController passes them)
//     'copy' => ['title' => line('groups.name_prompt.label'), 'lead' => line('groups.name_prompt.message'),
//                'detail' => line('groups.name_prompt.detail', ['current' => $name]), 'later' => line('groups.setup.later')],
// ])
```

```php
// App\Http\Responses\VerifyEmailResponse::toResponse()
return redirect()->intended($destination['url'] ?? SignInLanding::for(CurrentUser::orFail($request)));
// The `?verified=1` that used to ride on the home URL is dropped: nothing reads it.

// App\Http\Controllers\HomeController::startSharing()
return redirect()->to(SignInLanding::for($user));   // after the create-if-none
```

```php
// Database\Factories\GroupFactory
'name_set_at' => now(),                          // in definition()
public function unnamed(): static;               // ['name_set_at' => null]
```

`resources/js/app.ts`: `case name === 'share/Setup': return null;` beside the
public pages, because the page brings its own shell. `Setup.vue` renders
`AuthSimpleLayout` itself with
`copy.title` and `copy.lead`, then `copy.detail`, `GroupNameForm` with the
same props the dashboard card passes, and `copy.later` in small print.

## Copy

| Key                  | File                 | English                                                  |
| -------------------- | -------------------- | -------------------------------------------------------- |
| `groups.setup.later` | `lang/en/groups.php` | You can change it any time from your :group's home page. |

Title, lead and detail reuse `groups.name_prompt.label`, `.message` and
`.detail`, which already say the right things.

## Routes

| Verb | Path              | Name          | Action                 |
| ---- | ----------------- | ------------- | ---------------------- |
| GET  | `g/{group}/setup` | `share.setup` | `SetupController@show` |

The form submits to the existing `PATCH g/{group}` (`share.group.update`).

## Tests

**New: `tests/Feature/Share/SetupTest.php` — 8 cases**

1. `test_signing_in_to_an_unnamed_group_lands_on_setup` — owner of a Group
   from `createFor()` signs in with a password: 302 to `share.setup`.
2. `test_confirming_the_address_lands_on_setup` — an unverified owner follows
   the signed verification link: 302 to `share.setup`.
3. `test_starting_to_share_lands_on_setup` — a learner with no Group posts
   `start-sharing`: a Group exists and the response is 302 to its setup.
4. `test_the_setup_page_offers_the_name_form` — GET setup as the owner
   renders `share/Setup` with the default name and the four copy lines.
5. `test_naming_the_group_from_setup_goes_to_the_dashboard` — PATCH the name
   from the setup page: back to setup, which is 302 to `share.dashboard`;
   `hasChosenName()` is true.
6. `test_a_named_group_signs_in_to_its_dashboard` — after `rename()`, sign-in
   is 302 to `share.dashboard`.
7. `test_an_admin_is_never_sent_to_setup` — an admin on an unnamed Group signs
   in to its dashboard, and GET setup as that admin is 302 to the dashboard.
8. `test_setup_for_a_named_group_goes_to_the_dashboard` — the owner opening
   setup once the name is chosen is 302 to the dashboard.

**Changed:** none expected. `SignInLandingTest`, `VerificationDetourTest` and
every test that signs an owner in keep passing because the factory now names
its Groups.

## Acceptance

- [x] A fresh registration, once the address is confirmed, lands on a page
      that asks for the Group's name and nothing else
- [x] Signing in and "Start sharing" land there too while the name is unchosen
- [x] Naming the Group goes to its home; an admin is never asked
- [x] The stream is in `PLAN.md`'s table and `T-026` no longer includes this
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**Found by the owner after close, same day.** A real registration still landed
on `/dashboard`. Fortify sends a new registration to the home route, the
`verified` wall bounces it to the notice and stores the home route as the
intended URL, and the verification landing honoured that above the fallback.
The spec's test list went straight to the verification link with nothing
stored, which is why eight cases passed and the owner's walk did not. Fixed:
an intended URL that is the home route is discarded before the landing is
chosen (`SignInLanding::isHome()`); a real page still wins. A ninth case walks
the registration path. See the second report.
