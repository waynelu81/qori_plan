---
id: T-031
title: A Series can be changed after it is created
stream: recovery
status: done
owner: claude
estimate: M
depends: T-030
blocks: none
---

# T-031 — A Series can be changed after it is created

## Why

**There is no route that updates a Series.** `share.series.*` registers index,
store, show, publish, archive and unarchive, and nothing else;
`SeriesService` has `create`, the episode methods and the lifecycle methods, and
no `update`. A title, a summary and an hours figure are written once at creation
and are then permanent.

So a typo in a title is permanent, a summary written before the Series existed
can never be revised, and the only escape is to build the whole thing again
under a new slug. That is a dead end reached by ordinary use, which is what the
`recovery` stream exists to close.

It also makes `T-030` half a fix on its own: a textarea helps the person writing
a summary for the first time and does nothing for the one who has already
written it badly.

## Decisions taken to make this specifiable

**The slug never moves.** Exactly the rule `GroupService::rename()` already
keeps, and for the same reason: the slug is in every link a creator has sent, in
the access emails already delivered and on the public page. §21.3 says a slug is
for reading and an id is permanent, so nothing durable may depend on one — and a
rename that reassigned it would break every link to fix a display name.

**The form edits what the create form collects, and nothing more.** Title,
summary and hours. Not price: `SeriesService::create()` accepts `price_cents`
and `currency` and no form has ever sent them, so pricing a Series has no way in
at all. Adding repricing here would smuggle in a new capability and a real
product question — what happens to somebody who has already paid — under the
heading of a bug fix. That belongs in its own task with its own decision.

**It lives on the Series page, in a panel.** Not a separate `/edit` page. The
Series page is already where a creator works on a Series, and the pattern is the
one `GroupNameForm` uses on Share home. A `PATCH` takes the id, per §21.3.

**Editing is blocked by the same lock as everything else.**
`guardSeriesUnlocked()` already gates adding, editing and removing an Episode.
Changing the Series' own fields is editing it, so it takes the same guard: a
Group over its plan cap has read-only Series, and that has to mean all of it.

## Preconditions

`T-030` shipped, so `TextareaField` exists and the summary limit is in config.

## Scope

**In:**

- `PATCH /g/{group}/series/{seriesId}` with a Form Request.
- `SeriesService::update()`, keeping the slug.
- An edit panel on the Series page.
- The over-cap guard, and an archived Series being refused.

**Out:**

- Price and currency. See the decision above.
- Renaming the slug, or a slug field of any kind.
- Editing Episodes. `EpisodeController::update()` already exists, and what it
  cannot change is its own task.
- Rich text. `T-030` settles that.

## Files

| Path                                              | Change | Notes                                 |
| ------------------------------------------------- | ------ | ------------------------------------- |
| `routes/share.php`                                | edit   | One route                             |
| `app/Http/Requests/Share/UpdateSeriesRequest.php` | new    | Three fields                          |
| `app/Http/Controllers/Share/SeriesController.php` | edit   | `update()`; `show()` sends the limits |
| `app/Services/SeriesService.php`                  | edit   | `update()`                            |
| `resources/js/components/series/SeriesForm.vue`   | new    | The panel's form                      |
| `resources/js/pages/share/series/Show.vue`        | edit   | The panel                             |
| `lang/en/series.php`                              | edit   | 1 key                                 |
| `tests/Feature/Series/EditSeriesTest.php`         | new    | 9 cases                               |

**Collision note:** `SeriesController.php` and `share/series/Show.vue` are also
`T-030`'s neighbours. That is why this depends on it rather than running beside
it.

## Database

None.

## Code

```php
// App\Services\SeriesService
/**
 * Change a Series' own details, keeping its slug.
 *
 * @param  array{title?: string, summary?: ?string, hours?: ?float}  $attributes
 */
public function update(Series $series, array $attributes): Series;
```

Calls `guardSeriesUnlocked($series->group, 'edit a series')` first, and refuses
an archived Series with `AppException::invalidRequest('errors.series.is_archived')`
— the key already exists and already says to bring it back first.

Writes only the keys present, so a partial submission does not blank a field
nobody sent. `title` is trimmed; an empty string is a validation failure rather
than a blank title.

```php
// App\Http\Controllers\Share\SeriesController
public function update(
    string $group,
    string $seriesId,
    UpdateSeriesRequest $request,
    SeriesService $seriesService,
    Terminology $terminology,
): RedirectResponse;
```

Route parameters arrive positionally in URI order, so `$group` is declared even
though the middleware supplies the context — trap 5, the same as every other
action in this controller.

```vue
// resources/js/components/series/SeriesForm.vue defineProps<{ seriesId: string;
groupSlug: string; title: string; summary: string | null; hours: number | null;
summaryMaxlength: number; disabled?: boolean; // the over-cap lock, said before
the refusal }>();
```

## Copy

| Key              | File                 | English         |
| ---------------- | -------------------- | --------------- |
| `series.updated` | `lang/en/series.php` | `:title saved.` |

Names the title back, because a rename is the change most worth confirming and
the one a creator is most likely to have fat-fingered.

## Routes

| Verb  | Path                           | Name                  | Action                    |
| ----- | ------------------------------ | --------------------- | ------------------------- |
| PATCH | `/g/{group}/series/{seriesId}` | `share.series.update` | `SeriesController@update` |

`{seriesId}`, not `{series}`: this mutates, so it takes an id (§21.3). The page
submitting already holds it.

## Tests

**New: `tests/Feature/Series/EditSeriesTest.php` — 9 cases**

1. `test_a_creator_can_change_the_title` — the capability that did not exist.
2. `test_the_slug_does_not_move_when_the_title_does` — the rule that matters
   most, and the one a careless implementation breaks.
3. `test_a_creator_can_change_the_summary` — including a multi-line value.
4. `test_a_summary_over_the_limit_is_refused` — the same config-driven limit as
   `T-030`, on the other form.
5. `test_hours_can_be_cleared` — null is a legitimate value here, and
   distinguishing "sent empty" from "not sent" is where a partial write goes
   wrong.
6. `test_an_omitted_field_is_left_alone` — send only the title; the summary
   survives.
7. `test_an_empty_title_is_refused`.
8. `test_an_archived_series_cannot_be_edited` — refused, naming the archive.
9. `test_a_group_over_its_cap_cannot_edit` — the read-only lock covers the
   Series' own fields, not only its Episodes.

**Changed:** none expected.

## Acceptance

- [x] A creator can change a Series' title, summary and hours after creating it
- [x] The slug never moves
- [x] An omitted field is left alone rather than blanked
- [x] An archived Series and an over-cap Group are both refused, in the service
- [x] Price is untouched and unreachable, exactly as before
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**A refusal on a `PATCH` is a toast, not a validation error.**
`AppException::render()` only builds an error page for a failed `GET`; anything
else flashes an error toast and redirects back. So a route-level test can only
show that nothing changed, which would also pass if the request were silently
ignored. Both refusal tests therefore assert twice: the route leaves the row
alone, and the service throws with the right `ErrorCode`.

**PHPStan caught dead code in the first draft of `update()`.** It had an
`=== ''` arm for a cleared hours field. `ConvertEmptyStringsToNull` has already
turned that into null before validation runs, so the branch could never be
taken. Removed rather than silenced.

**The Series page needed two props it did not have.** `hours` was not in
`summarise()` and the summary limit was not sent at all, so the form had nothing
to fill itself in with. `hours` went into `summarise()` rather than into a second
shape, so the list and the page cannot disagree about what a Series is.

`series.title` is 255 characters and stays an `<Input>`. It is a name, not
prose, and `T-030`'s rule is about long-form text rather than about long
columns.
