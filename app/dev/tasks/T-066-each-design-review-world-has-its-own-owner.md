---
id: T-066
title: Each design-review world has its own owner
stream: design
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-066 — Each design-review world has its own owner

## Why

`DesignReviewSeeder` gives Rita five Groups so that one sign-in reaches every
state the contact sheet photographs. Under the rule recorded on 2026-09-13
(`decisions.md`, one Group per person) that fixture describes a product that
does not exist, and it is what put a five-entry switcher in front of the owner
while they were testing the one account the product actually gives.

Afterwards: each world has its own owner, Rita owns Harbour Lane Studio and
nothing else, and the screenshot run signs in as each owner for that owner's
world. Ada is still an admin on Harbour Lane who does not own it.

## Preconditions

`php artisan qori:design-review` needs the browser the command drives; the
report says whether it was run.

## Scope

**In:**

- Four owners in the seeder, one per world, with hand-written ULIDs like the
  rest of the cast.
- Four sign-in contexts in the command, and the world screens using them.
- The wipe list.
- One fixture test.
- The cast table and "The five worlds" in `docs/tinker/design-review.md`.

**Out:**

- Any change to what each world contains.
- Peers, Ada, Theo, Noor and staff.

## Files

| Path                                           | Change | Notes                        |
| ---------------------------------------------- | ------ | ---------------------------- |
| `database/seeders/DesignReviewSeeder.php`      | edit   | Four owners; wipe list       |
| `app/Console/Commands/DesignReviewCommand.php` | edit   | Four contexts; world screens |
| `tests/Feature/DesignReviewFixtureTest.php`    | edit   | 1 new case                   |
| `docs/tinker/design-review.md`                 | edit   | Cast; five worlds            |

## Database

None.

## Code

```php
// Database\Seeders\DesignReviewSeeder
public const OWNER_EMPTY_EMAIL = 'fern@design-review.qori.test';    // Fern Okoye, Fresh Start
public const OWNER_ONE_EMAIL = 'omar@design-review.qori.test';      // Omar Reyes, Solo Practice
public const OWNER_MANY_EMAIL = 'lena@design-review.qori.test';     // Lena Novak, The Long Names Collective
public const OWNER_CAPPED_EMAIL = 'kai@design-review.qori.test';    // Kai Tanaka, Capped Co

private function owner(string $tail, string $name, string $email): User;   // ids PER50N07..PER50N10
```

`emptyGroup()`, `oneItemGroup()`, `crowdedGroup()` and `cappedGroup()` are
called with the matching owner instead of `$creator`. `wipe()` deletes the
four addresses too.

```php
// App\Console\Commands\DesignReviewCommand::contexts() — four more:
['name' => 'owner-empty', 'url' => $this->magicLinkFor(DesignReviewSeeder::OWNER_EMPTY_EMAIL), 'steps' => []],
['name' => 'owner-one', ...], ['name' => 'owner-many', ...], ['name' => 'owner-capped', ...],
```

The `600`–`695` screens in `stateScreens()` use those contexts instead of
`creator`.

## Copy

None.

## Routes

None.

## Tests

**Changed: `tests/Feature/DesignReviewFixtureTest.php` — 1 new case**

1. `test_every_world_has_its_own_owner` — the five fixture Groups have five
   distinct `owner_user_id`s, Rita owns exactly one, and each owner holds the
   Owner collaborator row on their Group.

## Acceptance

- [x] Seeding gives five Groups with five owners; Rita owns one
- [x] The screenshot run's world screens sign in as that world's owner
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

None.
