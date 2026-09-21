---
id: T-023
title: Fixed-value attributes become PHP enums
stream: reachability
status: done
owner: claude
estimate: L
depends: none
blocks: none
---

# T-023 — Fixed-value attributes become PHP enums

## Why

Fifty-six string constants across fifteen models describe attributes with a
closed set of values — `Series::STATUS_DRAFT`, `Episode::TYPE_VIDEO`,
`Collaborator::ROLE_OWNER` and so on — and every one of them is a bare string
by the time it reaches the database, a comparison or a Vue prop. Three
consequences, all of which have already happened here:

- **Nothing enumerates them.** `Series::STATUS_ARCHIVED` was declared in the
  schema migration and read by nothing for a month; a `cases()` call would have
  shown a value with no behaviour behind it the day it was added.
- **Nothing checks a comparison.** `$series->status === 'pubished'` is valid
  PHP and silently false forever. PHPStan cannot help with a `string`.
- **Every consumer re-derives the mapping.** The Series list held its own
  `statusLabel()` until `T-001` moved it into a component, and printed the raw
  column before that — which is how "PUBLISHED" in capitals reached a product
  whose word for that state is "Ready to share".

Qori already has three enums — `App\Admin\StaffRole`, `StaffAbility` and
`App\Exceptions\ErrorCode` — and they are the good examples. This applies the
same treatment to the model attributes.

## Scope

**In:**

- Backed string enums for every closed-value attribute on a model.
- `$casts` entries so Eloquent hydrates and persists them.
- Converting comparison sites to enum comparisons.
- Keeping the existing `STATUS_*` constants as deprecated aliases **only** where
  removing them in one pass would be unreviewable — and saying which, and why.

**Out:**

- Anything whose values come from a vendor. `groups.subscription_status` is
  Stripe's word, not Qori's, and enumerating it would make Qori's copy of
  Stripe's state machine authoritative. Leave it a string.
- Database-level enum types. Postgres has them; a string column plus a PHP enum
  keeps migrations cheap and is what Laravel expects.
- New behaviour. A label that today lives in a Vue component may move onto its
  enum, but nothing new gets a rule it did not have.
- `ErrorCode`, `StaffRole`, `StaffAbility` — already done, and the pattern.

## Preconditions

None beyond a clean checkout.

## Files

Placed under `app/Models/Enums/` — inside the Models folder as asked, in a
subfolder because `CLAUDE.md` says `app/Models` holds Eloquent models only and
fifteen enums beside fifteen models makes neither easy to find. If that reading
is wrong, moving them is one `git mv` and a namespace change.

| Path                                      | Change | Notes                                                 |
| ----------------------------------------- | ------ | ----------------------------------------------------- |
| `app/Models/Enums/SeriesStatus.php`       | new    | draft, published, archived, purged                    |
| `app/Models/Enums/GroupStatus.php`        | new    | active, hibernated, archived                          |
| `app/Models/Enums/AccessStatus.php`       | new    | active, revoked                                       |
| `app/Models/Enums/CollaboratorRole.php`   | new    | owner, admin                                          |
| `app/Models/Enums/EpisodeType.php`        | new    | file, video, audio, live                              |
| `app/Models/Enums/EpisodeProvider.php`    | new    | qori_s3, dropbox, vimeo, zoom, teams                  |
| `app/Models/Enums/ConnectionProvider.php` | new    | dropbox, vimeo, zoom, teams                           |
| `app/Models/Enums/MediaAssetStatus.php`   | new    | pending, stored                                       |
| `app/Models/Enums/MediaAssetPurpose.php`  | new    | episode                                               |
| `app/Models/Enums/CampaignType.php`       | new    | launch, new_episode, stalled                          |
| `app/Models/Enums/CampaignStatus.php`     | new    | draft, sending, sent                                  |
| `app/Models/Enums/RecipientStatus.php`    | new    | pending, sent, failed, skipped, bounced, complained   |
| `app/Models/Enums/SuppressionScope.php`   | new    | all, marketing                                        |
| `app/Models/Enums/SuppressionReason.php`  | new    | bounce, complaint, manual                             |
| `app/Models/Enums/FulfilmentStatus.php`   | new    | granted, failed                                       |
| `app/Models/Enums/SignupIntent.php`       | new    | share, learn                                          |
| `app/Models/*.php`                        | edit   | 15 models: casts, and constants removed or aliased    |
| _call sites_                              | edit   | ~167 comparisons across `app/`, `tests/`, `database/` |
| `tests/Feature/Enums/ModelEnumTest.php`   | new    | 8 cases                                               |

**Added during execution.** None changes what gets built — the Scope says
"every closed-value model attribute", and these are the ones the table missed
plus the files the Code section's label move actually needs:

| Path                                               | Change | Why it was missing                                        |
| -------------------------------------------------- | ------ | --------------------------------------------------------- |
| `app/Models/Enums/PeerStatus.php`                  | new    | `Peer::STATUS_*` — Qori's own, not in the table           |
| `app/Models/Enums/ConsentSource.php`               | new    | `Peer::CONSENT_*` — same                                  |
| `app/Integrations/Contracts/ResolvesMedia.php`     | edit   | `provider()` returned a string and was compared to a cast |
| `app/Data/MediaLink.php`                           | edit   | Same value, carried across the boundary                   |
| `app/Support/UploadKey.php`                        | edit   | `live()` took the purpose as a string                     |
| `app/Http/Controllers/Share/SeriesController.php`  | edit   | Sends `statusLabel`, per the Code section                 |
| `resources/js/components/series/SeriesStatus.vue`  | edit   | Stops mapping; renders the label it is given              |
| `resources/js/pages/share/series/{Index,Show}.vue` | edit   | Pass the new prop                                         |

**Collision warning.** This touches almost every model, so it collides with
anything else in flight. Check the board before claiming, and prefer to run it
when nothing else is `doing`.

## Database

None. The columns stay `string`; the enum is a PHP-side cast. A Postgres enum
type would make every added value a migration, which is the wrong trade for
values that change with the product.

Confirm no migration constrains any of these columns to a check or enum type
before starting. If one does, that is a re-scope.

## Code

House style is `App\Admin\StaffRole`: a backed string enum, `PascalCase` cases,
a docblock per case where the value is not self-evident, and behaviour on the
enum rather than in a `match` at the call site.

```php
namespace App\Models\Enums;

enum SeriesStatus: string
{
    /** Being made. Nobody outside the Group can reach it. */
    case Draft = 'draft';

    /** Ready to share — the word the product uses (§terminology). */
    case Published = 'published';

    /** Out of circulation; every Peer with access keeps it (T-009). */
    case Archived = 'archived';

    /** Its material has been deleted; the record stays (T-010). */
    case Purged = 'purged';

    /** What a creator is shown. Peers never see these — see SeriesStatus's docblock. */
    public function label(): string;

    /** Counts against the plan cap. */
    public function isLive(): bool;
}
```

Cast in the model:

```php
protected function casts(): array
{
    return ['status' => SeriesStatus::class, /* … */];
}
```

**Where a label already exists in Vue, move it and leave the Vue reading a
prop.** `SeriesStatus::label()` should return what `SeriesStatus.vue` returns
today; the component then renders `series.statusLabel` rather than mapping it
again. Two mappings that must agree is the problem being solved.

**Do not delete a constant and its every use in one commit for all fifteen
models.** Work model by model. `Series` and `Group` first — they have the most
call sites and set the pattern.

## Copy

None. Labels that move onto an enum keep their existing wording; the
terminology rules still apply (`docs/planning/terminology-refactor.md`), so a
label naming a product noun resolves through `Terminology` rather than being
written into the enum.

## Routes

None.

## Tests

**New: `tests/Feature/Enums/ModelEnumTest.php` — 8 cases**

1. `test_a_status_round_trips_through_the_database` — save a model with an enum,
   reload, assert the instance not the string.
2. `test_every_enum_case_is_reachable_from_its_model` — each enum's `cases()`
   against what the model's scopes and methods can produce. **This is the case
   that would have caught `STATUS_ARCHIVED` sitting unused for a month**; where
   a case is deliberately unreachable, say so in the test.
3. `test_a_series_status_knows_whether_it_counts_against_the_cap`
4. `test_a_label_matches_what_the_interface_shows` — the moved Vue mapping.
5. `test_an_unknown_value_in_the_database_fails_loudly` — write a bad string
   with the query builder, assert hydration throws rather than yielding null.
6. `test_no_model_still_declares_a_converted_constant` — greps `app/Models` for
   `public const STATUS_`, so the refactor cannot be half-done and forgotten.
7. `test_no_call_site_compares_a_status_to_a_string_literal` — greps `app/` for
   `status === '` and its relatives.
8. `test_every_enum_lives_in_the_models_enums_namespace`.

**Changed:** expect wide, shallow changes across the existing suite wherever a
test asserts a raw string. Assert the enum instead. Count them in the report —
if the number is small, that is itself a finding about how little the current
values were being checked.

## Acceptance

- [x] Every closed-value model attribute is a backed enum under
      `app/Models/Enums/`
- [x] Models cast them; nothing compares a status to a string literal in `app/`
- [x] Vendor-owned values (`subscription_status`) are deliberately left alone
- [x] A label that existed in two places now exists in one
- [x] An unknown value from the database fails loudly rather than silently
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**The reachability test found ten orphans on its first run, not one.** The Why
cites `STATUS_ARCHIVED` sitting unused for a month as the motivating example.
`test_every_enum_case_is_reachable_from_its_model` found ten more values that
nothing in `app/` or `database/` can produce — two campaign types, a Group
status, four recipient statuses, a suppression reason, plus the two known
placeholders. Each is listed in the test with the task that will produce it, so
the exemption is a sentence somebody wrote and the list shrinking is how it
gets finished.

**Two attributes were missing from the Files table and are Qori's own.**
`Peer::STATUS_*` and `Peer::CONSENT_*`. Added, because Scope says "every".
`SubscriptionPrice::INTERVAL_*` and `SubscriptionCoupon::DURATION_*` are also
absent from the table and stay strings — those are Stripe's words, which the
Out section already excludes.

**Two enums looked like one and are not.** `EpisodeProvider` and
`ConnectionProvider` share four spellings, and the playback path was comparing a
`Connection` constant against an `Episode` column — correct only by coincidence.
`EpisodeProvider::connection()` is now the single explicit crossing, and Qori's
own storage is the case that proves they are different types: it has a media
resolver and no connection at all.

**The seeder was writing values no constant declared.** `consent_source` held
`invite_form` and `checkout` in the design-review fixture; the product only ever
writes `peer` or `creator`. The cast refused them, which is the whole point.

**Deleting a string parameter deleted an error.**
`errors.series.unknown_episode_type` and `errors.campaign.unknown_type` both
existed to catch a value nothing recognised. With `EpisodeType` and
`CampaignType` in the signature, PHP refuses the call before the body runs, so
both branches were unreachable and both lang keys had no thrower. Removed.

**PHPStan cannot see through `mixed`.** It caught the enum-versus-string
comparisons in `withValidator()`, where the type was known, and missed the same
mistake three lines away in `rules()`, where the value came from
`$request->input()`. The suite caught that one. Worth knowing: the analyser is
the net for typed code and the tests are still the net for request input.

Enums cross into Vue as plain strings — a cast serialises to its `value`, so
props are unchanged and no frontend type has to move. Where a component maps a
status to a label today, send the label as its own prop instead and let the
enum own the mapping.

The Vue-side type could become a union (`'draft' | 'published' | …`) to get the
same protection in TypeScript. Worth doing and not in this task's scope; note
it in the report if it looks cheap.
