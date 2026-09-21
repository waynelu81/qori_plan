---
id: T-069
title: One command resets the development database to one of three states
stream: operations
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-069 — One command resets the development database to one of three states

## Why

Resetting the development database has been a hand-run `migrate:fresh` plus,
sometimes, `db:seed --class=DesignReviewSeeder`, and the owner has asked for
it three times today in three different shapes: empty, empty with plans, and
the full cast. The plans live inside the design-review seeder, so "empty with
plans" had no command at all, and an empty database leaves the billing and
pricing pages listing nothing.

Afterwards: `php artisan qori:reset` asks which of three states the database
should be in, or takes it as an argument, refuses anywhere but a local
database, and prints what it left behind.

## Decisions taken to make this specifiable

**Three states, one argument.** `clear` is an empty migrated schema. `basic`
adds the plans and the coupon. `full` adds the design-review cast, which
includes the plans. Missing the argument asks.

**The plans get their own seeder.** `PricingSeeder` holds what
`DesignReviewSeeder::pricing()` held, keyed by the same ids so the
design-review wipe still finds them, and idempotent so it can be run on a
database that already has them. `DesignReviewSeeder` calls it.

**Local only, and it means the database, not the flag.** The environment must
be `local` (or `testing`, for the suite) and the connection's host must be
loopback. `--force` skips the confirmation and nothing else.

**Files are not touched.** R2 objects referenced by dropped rows are
orphaned, not deleted; the command says so. Clearing storage is a separate
decision each time.

## Preconditions

None beyond a clean checkout and the local database.

## Scope

**In:**

- The command, the pricing seeder, the design-review seeder calling it.
- A tinker recipe and a row in the recipe index.
- Tests.

**Out:**

- Clearing R2.
- Any change to what the design-review seeder builds.

## Files

| Path                                                 | Change | Notes                             |
| ---------------------------------------------------- | ------ | --------------------------------- |
| `app/Console/Commands/ResetDatabaseCommand.php`      | new    | `qori:reset`                      |
| `database/seeders/PricingSeeder.php`                 | new    | Plans and coupon, idempotent      |
| `database/seeders/DesignReviewSeeder.php`            | edit   | `pricing()` calls `PricingSeeder` |
| `docs/tinker/reset.md`                               | new    | Recipe                            |
| `docs/tinker/README.md`                              | edit   | Index row                         |
| `docs/tinker/design-review.md`                       | edit   | Points at `qori:reset full`       |
| `tests/Feature/Console/ResetDatabaseCommandTest.php` | new    | 6 cases                           |

## Database

None.

## Code

```php
namespace App\Console\Commands;

class ResetDatabaseCommand extends Command
{
    protected $signature = 'qori:reset
                            {state? : clear, basic or full}
                            {--force : Skip the confirmation}';

    public const STATES = ['clear', 'basic', 'full'];

    public function handle(Application $app): int;
    // refuse unless $app->environment(['local', 'testing']) and the connection host is loopback
    // choice() when state is missing; confirm() unless --force
    // migrate:fresh --force; then db:seed PricingSeeder (basic) or DesignReviewSeeder (full)
    // print a table: users, groups, series, subscription_prices; one line saying storage was not touched
}
```

```php
namespace Database\Seeders;

class PricingSeeder extends Seeder
{
    public function run(): void;   // Model::unguarded; SubscriptionPrice::updateOrCreate(['id' => DesignReviewSeeder::id('PR1CE00n')], [...]) ×3; SubscriptionCoupon likewise
}
```

## Copy

None. Console output aimed at a developer.

## Routes

None.

## Tests

**New: `tests/Feature/Console/ResetDatabaseCommandTest.php` — 6 cases**, no
`RefreshDatabase`: the command drops the schema itself, and `tearDown()` leaves
it empty for whatever runs next.

1. `test_it_refuses_outside_a_local_environment` — env set to `production`:
   exit code 1 and a row created beforehand survives.
2. `test_clear_leaves_an_empty_schema` — a user exists; `clear --force`
   leaves zero users and zero prices.
3. `test_basic_seeds_the_plans_and_nothing_else` — three prices, one coupon,
   zero users.
4. `test_full_seeds_the_design_review_cast` — five Groups, three prices,
   users present.
5. `test_the_pricing_seed_runs_twice_without_duplicating` — `basic` then the
   seeder again: still three prices.
6. `test_it_asks_which_state_when_none_is_given` — `expectsChoice`.

## Acceptance

- [x] `php artisan qori:reset` offers the three states and does what each says
- [x] It refuses a non-local environment or a non-loopback database host
- [x] `basic` gives the billing and pricing pages their plans on an empty database
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

None.
