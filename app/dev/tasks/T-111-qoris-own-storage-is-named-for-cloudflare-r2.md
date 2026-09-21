---
id: T-111
title: Qori's own storage is named for Cloudflare R2
stream: storage
status: done
owner: claude
estimate: M
depends: none
blocks: none
---

# T-111 — Qori's own storage is named for Cloudflare R2

## Why

The storage Qori itself provides is called `Qori` in code: the provider is
`EpisodeProvider::QoriS3` (`qori_s3`, stored on every Episode that uses it,
`app/Enums/EpisodeProvider.php:17`), and its classes are
`App\Integrations\Qori\QoriStorage` and `QoriUploads`. The bucket is Cloudflare
R2, not S3, and `Qori` names Qori rather than the vendor behind it, so a second
storage vendor would have no name. `D-022` puts each vendor's code in a folder
named for the vendor service.

Afterwards the offering is `EpisodeProvider::CloudflareR2` (`cloudflare_r2`),
its code is `app/Integrations/CloudflareR2`, and every stored `qori_s3` has
been migrated. A creator still reads "Qori storage".

## Decisions taken to make this specifiable

**The stored value changes, with a data migration, not only the case name.**
A case called `CloudflareR2` holding `qori_s3` would keep the wrong name in the
database, in props and in every log line. `episodes.provider` is the only
column that holds it: a plain string with no check constraint, enum type,
default or index (`database/migrations/2026_09_08_000000_create_qori_schema.php:109`).

**Case `CloudflareR2`, value `cloudflare_r2`, folder `CloudflareR2`, classes
`CloudflareR2Storage` and `CloudflareR2Uploads`.** The owner's names (`D-022`),
with the values in the snake case the other providers use, and the classes in
the `DropboxStorage` / `VimeoVideos` pattern. A later AWS offering would be
`AWSS3`; nothing for it is built here.

**One deploy, not expand and contract.** Nothing is sold to real customers yet
(`PLAN.md`), so the moment between `migrate --force` and the new code serving
is accepted. The migration is idempotent, so running it again after traffic has
switched converts any row an old instance wrote in between.

**The migration uses literal strings and `DB::table`, never the enum or the
model.** The old case will not exist when it runs, and `down()` must still
restore `qori_s3`.

**`isQoriHosted()` keeps its name and `Episode::isSelfHosted()` delegates to
it.** Both answered the same question and only `isSelfHosted()` had callers,
so a second Qori-hosted offering would have had to be added in two places.

**The creator-facing label stays "Qori storage".** Only the key in `Show.vue`'s
label map changes; public copy names no vendor.

**Environment and disk names stay.** The `r2` disk and the `R2_*` variables
already name the vendor, and `QORI_STORAGE_DISK` is a neutral selector set in
Laravel Cloud; renaming it would need a dashboard change for nothing.

## Preconditions

**Data this task verifies against:** a clean database for the tests. The
migration test inserts raw `qori_s3` rows itself, because `RefreshDatabase`
never runs a data step against existing rows.

**Equipment:** a browser for the creator Series page. The development database
holds the owner's rows with `qori_s3`; an agent must not run `migrate` against
it, so the owner runs `php artisan migrate` after merging, and until then those
Series pages fail to load their Episodes.

## Scope

**In:**

- The enum case and value, the two classes' folder, namespace and names, and
  every PHP, Vue, factory, seeder and test reference.
- A reversible, idempotent data migration for `episodes.provider`.
- The live docs that name the old value or classes, and a `DocumentationTest`
  reversed claim so they cannot come back.

**Out:**

- A disk per offering, and a contract for uploads so `UploadService` stops
  importing a vendor class. Both belong to whichever task adds `AWSS3`.
- `errors.series.provider_not_allowed` interpolating the raw enum value. It
  reads `cloudflare_r2` instead of `qori_s3`, and the form never offers a
  provider a type cannot use, so only a crafted request or tinker sees it.
- The storage-stream drafts (`T-089`, `T-094`, `T-096`, `T-097`, `T-098`) that
  cite `qori_s3` or `QoriStorage`. They are drafts, re-cited when specified.
- Records: `decisions.md`, `status-history.md`, `walkthroughs.md`, the archive,
  done tasks and reports keep the old names.

## Files

| Path                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Change | Notes                                                                                             |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------- |
| `app/Enums/EpisodeProvider.php`                                                                                                                                                                                                                                                                                                                                                                                                                                       | edit   | `case CloudflareR2 = 'cloudflare_r2';` and its docblock; `isQoriHosted()` and `connection()` arms |
| `app/Integrations/Qori/QoriStorage.php`                                                                                                                                                                                                                                                                                                                                                                                                                               | delete | moved                                                                                             |
| `app/Integrations/Qori/QoriUploads.php`                                                                                                                                                                                                                                                                                                                                                                                                                               | delete | moved                                                                                             |
| `app/Integrations/CloudflareR2/CloudflareR2Storage.php`                                                                                                                                                                                                                                                                                                                                                                                                               | new    | `git mv` of `QoriStorage`; namespace, class, `provider()`, docblock                               |
| `app/Integrations/CloudflareR2/CloudflareR2Uploads.php`                                                                                                                                                                                                                                                                                                                                                                                                               | new    | `git mv` of `QoriUploads`; namespace, class, docblock reference to the reader                     |
| `app/Providers/IntegrationServiceProvider.php`                                                                                                                                                                                                                                                                                                                                                                                                                        | edit   | import and `media-providers` tag                                                                  |
| `app/Providers/AppServiceProvider.php`                                                                                                                                                                                                                                                                                                                                                                                                                                | edit   | docblock names the uploads class                                                                  |
| `app/Services/UploadService.php`                                                                                                                                                                                                                                                                                                                                                                                                                                      | edit   | import and constructor type                                                                       |
| `app/Models/Episode.php`                                                                                                                                                                                                                                                                                                                                                                                                                                              | edit   | `isSelfHosted()` returns `$this->provider->isQoriHosted()`                                        |
| `app/Enums/EpisodeType.php`                                                                                                                                                                                                                                                                                                                                                                                                                                           | edit   | file arm of `allowedProviders()`                                                                  |
| `app/Enums/ConnectionProvider.php`                                                                                                                                                                                                                                                                                                                                                                                                                                    | edit   | docblock                                                                                          |
| `app/Data/MediaLink.php`                                                                                                                                                                                                                                                                                                                                                                                                                                              | edit   | docblock                                                                                          |
| `app/Http/Controllers/Share/EpisodeController.php`                                                                                                                                                                                                                                                                                                                                                                                                                    | edit   | fallback provider                                                                                 |
| `app/Console/Commands/MailCheckCommand.php`                                                                                                                                                                                                                                                                                                                                                                                                                           | edit   | the seeded file Episode                                                                           |
| `database/migrations/2026_09_17_000000_rename_qori_s3_provider_to_cloudflare_r2.php`                                                                                                                                                                                                                                                                                                                                                                                  | new    | data migration                                                                                    |
| `database/factories/SeriesFactory.php`                                                                                                                                                                                                                                                                                                                                                                                                                                | edit   | `withEpisodes()`                                                                                  |
| `database/seeders/DesignReviewSeeder.php`                                                                                                                                                                                                                                                                                                                                                                                                                             | edit   | the file Episodes' provider, line for line                                                        |
| `resources/js/pages/share/series/Show.vue`                                                                                                                                                                                                                                                                                                                                                                                                                            | edit   | the value at the allowed map, default, reference label and uploads switch; the label map key      |
| `tests/Feature/Storage/CloudflareR2ProviderMigrationTest.php`                                                                                                                                                                                                                                                                                                                                                                                                         | new    | 3 cases                                                                                           |
| `tests/Feature/Access/AccessServiceTest.php`, `tests/Feature/Access/ShareAccessRoutesTest.php`, `tests/Feature/Access/SharedRoutesTest.php`, `tests/Feature/Admin/ConsolePagesTest.php`, `tests/Feature/Checkout/BuyButtonTest.php`, `tests/Feature/Checkout/CheckoutTest.php`, `tests/Feature/Checkout/StripeWebhookTest.php`                                                                                                                                        | edit   | `EpisodeProvider::CloudflareR2`                                                                   |
| `tests/Feature/Series/ArchiveSeriesTest.php`, `tests/Feature/Series/DeleteSeriesTest.php`, `tests/Feature/Series/EpisodeOrderTest.php`, `tests/Feature/Series/EpisodeRoutesTest.php`, `tests/Feature/Series/LiveSessionTest.php`, `tests/Feature/Series/OverCapLockTest.php`, `tests/Feature/Series/SeriesIdentityTest.php`, `tests/Feature/Series/SeriesServiceTest.php`, `tests/Feature/Series/ShareLinkTest.php`, `tests/Feature/Series/ShareSeriesRoutesTest.php` | edit   | `EpisodeProvider::CloudflareR2`                                                                   |
| `tests/Feature/Share/EpisodeServiceTest.php`, `tests/Feature/ShareDigestTest.php`, `tests/Feature/Shared/CertificateTest.php`, `tests/Feature/Shared/ProgressTest.php`, `tests/Feature/Storage/MediaLifetimeTest.php`, `tests/Feature/Storage/PlaybackTest.php`                                                                                                                                                                                                       | edit   | `EpisodeProvider::CloudflareR2`                                                                   |
| `tests/Feature/ProductionDatabaseGuardTest.php`                                                                                                                                                                                                                                                                                                                                                                                                                       | edit   | docblock names the uploads class                                                                  |
| `tests/Feature/DocumentationTest.php`                                                                                                                                                                                                                                                                                                                                                                                                                                 | edit   | one reversed claim                                                                                |
| `docs/flows/storage.md`                                                                                                                                                                                                                                                                                                                                                                                                                                               | edit   | value and class names                                                                             |
| `docs/flows/series.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                | edit   | value in the provider list, table and rule                                                        |
| `docs/tinker/series.md`                                                                                                                                                                                                                                                                                                                                                                                                                                               | edit   | recipe calls and the expected error text                                                          |
| `docs/tinker/accesses.md`                                                                                                                                                                                                                                                                                                                                                                                                                                             | edit   | recipe call                                                                                       |
| `docs/tinker/uploads.md`                                                                                                                                                                                                                                                                                                                                                                                                                                              | edit   | value and recipe call                                                                             |
| `docs/planning/engineering-runbook.md`                                                                                                                                                                                                                                                                                                                                                                                                                                | edit   | the uploads class name                                                                            |

Flows: `docs/flows/storage.md` and `docs/flows/series.md` are the flow rows
above.

## Database

No schema change. A data migration only:

| Table      | Column     | Type               | Null | Default | Index / constraint |
| ---------- | ---------- | ------------------ | ---- | ------- | ------------------ |
| `episodes` | `provider` | string (unchanged) | no   | none    | none               |

Migration: `database/migrations/2026_09_17_000000_rename_qori_s3_provider_to_cloudflare_r2.php`

```php
return new class extends Migration
{
    public function up(): void
    {
        DB::table('episodes')->where('provider', 'qori_s3')->update(['provider' => 'cloudflare_r2']);
    }

    public function down(): void
    {
        DB::table('episodes')->where('provider', 'cloudflare_r2')->update(['provider' => 'qori_s3']);
    }
};
```

## Code

```php
namespace App\Enums;

enum EpisodeProvider: string
{
    /** Qori-hosted files on Cloudflare R2. Only ever for files (§8). */
    case CloudflareR2 = 'cloudflare_r2';
    // Dropbox, Vimeo, Zoom, Teams unchanged

    public function isQoriHosted(): bool; // $this === self::CloudflareR2
    public function connection(): ?ConnectionProvider; // self::CloudflareR2 => null
}

namespace App\Integrations\CloudflareR2;

class CloudflareR2Storage implements ResolvesMedia
{
    public function provider(): EpisodeProvider; // EpisodeProvider::CloudflareR2
    // linkFor() and the rest unchanged
}

class CloudflareR2Uploads
{
    // sign(), verify(), promote(), filesystem() unchanged
}

namespace App\Models;

class Episode
{
    public function isSelfHosted(): bool; // return $this->provider->isQoriHosted();
}
```

`Show.vue`: `'qori_s3'` becomes `'cloudflare_r2'` everywhere, and the label map
entry becomes `cloudflare_r2: 'Qori storage'`.

`DocumentationTest::reversedClaims()` gains
`'/\bQoriS3\b|\bqori_s3\b|QoriStorage|QoriUploads|Integrations\/Qori\b/'` with
the reason "Qori's own storage is `CloudflareR2` (`cloudflare_r2`) in
`app/Integrations/CloudflareR2` (`D-022`)."

## Copy

None. "Qori storage" stays as the creator's label.

## Routes

None.

## Tests

**New: `tests/Feature/Storage/CloudflareR2ProviderMigrationTest.php` — 3 cases**

1. `test_it_renames_every_qori_s3_episode_to_cloudflare_r2` — raw `qori_s3`
   rows inserted with `DB::table`, the migration's `up()` run, every row reads
   `cloudflare_r2` and hydrates as `EpisodeProvider::CloudflareR2`.
2. `test_it_leaves_other_providers_alone` — a `vimeo` and a `dropbox` row keep
   their values.
3. `test_rolling_back_restores_qori_s3` — `down()` after `up()` restores the
   raw value.

**Changed:**

- The 23 test files in the Files table replace `EpisodeProvider::QoriS3` with
  `EpisodeProvider::CloudflareR2`. Test names that describe the concept
  (`test_a_qori_hosted_file_resolves_to_a_link`) stay.
- `tests/Feature/DocumentationTest.php` gains the reversed claim; its test count
  is unchanged.

Total new: 3.

## Acceptance

- [x] No `QoriS3`, `qori_s3`, `QoriStorage`, `QoriUploads` or `Integrations\Qori` remains in `app/`, `database/factories`, `database/seeders`, `resources/js`, `tests/` or the live docs
- [x] The migration converts existing rows and rolls back
- [x] A creator's Series page offers "Qori storage" for a file Episode, and an Episode added with it is stored as `cloudflare_r2`
- [x] The report tells the owner to run `php artisan migrate` on the development database
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Wording, found in execution (17 September 2026): the first Acceptance line
holds outside the migration, its test and the `DocumentationTest` pattern,
which need the old names; "running it again after traffic has switched" under
**One deploy** means running the update by hand, because `migrate` will not
run a recorded migration twice. The third Acceptance line was checked with an
Episode stored through `EpisodeService::add()`, not an upload, which would
write to the real bucket. See the report.

Written from the owner's instruction of 17 September 2026 ("name Qori storage
… CloudflareR2, if Qori do provide AWS S3 it will be having one more file call
AWSS3"), which the owner, as the stream's owner, gave as approval to build.
