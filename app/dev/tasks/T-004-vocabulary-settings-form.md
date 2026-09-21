---
id: T-004
title: Vocabulary settings form behind the entitlement
stream: language
status: done
owner: claude
estimate: M
depends: none
blocks: T-005
---

# T-004 — Vocabulary settings form behind the entitlement

## Why

`App\Support\Terminology` resolves a complete `Vocabulary` per Group, falls back
atomically, and is read by every screen. What it cannot do is find a custom
vocabulary, because nothing writes one: `groups.settings.vocabulary` is a shape
with no form behind it, and `custom_vocabulary` is false on every plan.

This is the way in. It is presentation data — a Group calling its Peers
"Ruffies" has renamed a label, not granted a permission — so nothing here may
be read by an authorisation check.

## Scope

**In:**

- A Group settings page with five singular/plural pairs and a live preview.
- Validation, reset-to-defaults, and the entitlement gate.
- Cache invalidation on write.

**Out:**

- Choosing which paid tier sets `custom_vocabulary`. **Answered on 9 September
  2026: Pro and above.** Already set in `config/qori.php`, so this task's tests
  can use a Pro Group rather than overriding config — though overriding is
  still fine and keeps the test independent of a pricing decision.
- Downgrade behaviour (keep read-only vs revert) — **still undecided**, see
  `../terminology-refactor.md`. Until it is, a Group that loses the entitlement
  falls back to defaults and its stored labels are left untouched, which is
  what `Terminology::resolve()` already does. That is a defensible default and
  not a decision: it means a Group that lapses from Pro and returns finds its
  words where it left them.
- Applying the vocabulary to mail and PDFs — that is `T-005`.
- Custom verbs. Not in v1, ever, per the spec.

## Files

| Path                                                  | Change | Notes                                  |
| ----------------------------------------------------- | ------ | -------------------------------------- |
| `app/Http/Controllers/Share/VocabularyController.php` | new    | `edit`, `update`, `destroy`            |
| `app/Http/Requests/Share/UpdateVocabularyRequest.php` | new    | 10 fields                              |
| `app/Services/GroupService.php`                       | edit   | `setVocabulary()`, `clearVocabulary()` |
| `app/Support/Terminology.php`                         | edit   | Call `forget()` after a write          |
| `routes/share.php`                                    | edit   | 3 routes                               |
| `lang/en/groups.php`                                  | edit   | 3 keys                                 |
| `resources/js/pages/share/Vocabulary.vue`             | new    | The form and preview                   |
| `resources/js/components/AppSidebar.vue`              | edit   | A "Settings" nav item, owner only      |
| `tests/Feature/Share/VocabularySettingsTest.php`      | new    | 11 cases                               |

**Collision note:** `AppSidebar.vue` is also touched by design-stream tasks.
Check the board before claiming.

## Database

None. Storage is the existing `groups.settings` jsonb column, under the key
`Terminology::SETTINGS_KEY` (`'vocabulary'`), in the shape
`Vocabulary::fromLabels()` already reads:

```php
['group' => ['singular' => 'Pack', 'plural' => 'Packs'], 'creator' => [...], 'series' => [...], 'episode' => [...], 'peer' => [...]]
```

Do not add a column. The shape is already parsed and its fallback is already
tested.

## Code

```php
// App\Services\GroupService
/**
 * @param  array<string, array{singular: string, plural: string}>  $labels
 */
public function setVocabulary(Group $group, array $labels): Group;
public function clearVocabulary(Group $group): Group;
```

Both write `settings` and then call `app(Terminology::class)->forget($group)` —
the registry memoises per group id per request, and a write inside the same
request would otherwise serve the old words back to the page that just saved
them.

`setVocabulary()` stores **all five** nouns or none. Partial input is a
validation failure, not a partial write: `Vocabulary::fromLabels()` falls back
atomically, so a half-saved set would silently render defaults and look like
the save failed.

```php
// App\Http\Controllers\Share\VocabularyController
public function edit(CurrentGroup $current, Terminology $terminology): Response;
public function update(UpdateVocabularyRequest $request, CurrentGroup $current, GroupService $groups, Terminology $terminology): RedirectResponse;
public function destroy(CurrentGroup $current, GroupService $groups, Terminology $terminology): RedirectResponse;
```

`edit()` must refuse when `! $group->allows(Terminology::ENTITLEMENT)`, with
`AppException::planLimitReached('errors.group.vocabulary_not_included')`. Refuse
in `update()` too — a form that is merely hidden is not a rule.

## Copy

| Key                                    | File                 | English                                 |
| -------------------------------------- | -------------------- | --------------------------------------- |
| `groups.vocabulary.saved`              | `lang/en/groups.php` | `Your :group speaks its own words now.` |
| `groups.vocabulary.reset`              | `lang/en/groups.php` | `Back to Qori's words.`                 |
| `errors.group.vocabulary_not_included` | `lang/en/errors.php` | message + resolution                    |

Vue copy for the form itself stays inline for now (§13's unwired i18n) —
**except** the preview sentences, which must come from lang so the preview shows
what the product will actually say.

Field labels are the _default_ nouns, never the custom ones: a form whose own
labels rename themselves as you type is unusable.

## Routes

| Verb   | Path                             | Name                       | Action                         |
| ------ | -------------------------------- | -------------------------- | ------------------------------ |
| GET    | `/g/{group}/settings/vocabulary` | `share.vocabulary.edit`    | `VocabularyController@edit`    |
| PATCH  | `/g/{group}/settings/vocabulary` | `share.vocabulary.update`  | `VocabularyController@update`  |
| DELETE | `/g/{group}/settings/vocabulary` | `share.vocabulary.destroy` | `VocabularyController@destroy` |

## Validation

Ten fields, `{noun}_singular` and `{noun}_plural` for each of
`Vocabulary::KEYS`. Every one:

- `required`, `string`, `min:1`, `max:40`
- `regex:/^[\p{L}\p{N} \-\'’]+$/u` — letters, digits, spaces, hyphen, apostrophe.
  No markup, no emoji, no newlines. Plain text only, escaped on output.
- Trimmed before storage; whitespace-only fails `min:1` after trimming, so
  apply `trim` in `prepareForValidation()`.

Casing is preserved exactly as typed. Nothing lowercases, title-cases or
pluralises a customer's word.

## Tests

**New: `tests/Feature/Share/VocabularySettingsTest.php` — 11 cases**

1. `test_an_entitled_group_can_set_its_own_words` — round-trip through
   `Terminology::for()`.
2. `test_the_words_reach_the_shared_inertia_prop` — `terminology.series.singular`.
3. `test_a_group_without_the_entitlement_cannot_open_the_form` — refused.
4. `test_a_group_without_the_entitlement_cannot_post_to_it` — refused; the
   hidden-form-is-not-a-rule case.
5. `test_a_missing_plural_is_rejected` — all five or none.
6. `test_markup_in_a_label_is_rejected` — `<b>Pack</b>`.
7. `test_a_whitespace_only_label_is_rejected`.
8. `test_casing_is_preserved_exactly` — `pack` stays lowercase.
9. `test_resetting_restores_the_defaults`.
10. `test_a_write_is_visible_in_the_same_request` — the memo-invalidation case.
11. `test_two_groups_render_different_words_for_the_same_series` — the
    acceptance criterion from `terminology-refactor.md`, written as a test.

**Changed:**

- `tests/Feature/TerminologyTest.php` — no changes expected. If it needs one,
  that is a signal the resolver's contract moved: stop and re-scope.

## Acceptance

- [x] An entitled Group can set, preview and reset its five noun pairs
- [x] An unentitled Group cannot, by form or by POST
- [x] All five or none; a partial submission is refused
- [x] Casing is preserved and markup is rejected
- [x] Two Groups render different words for the same underlying rows
- [x] `custom_vocabulary` is `true` on Pro and School and `false` below
- [x] No authorisation check anywhere reads a label
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)

## Re-scope log

None.

## Notes

**The nav item had to be plan-gated, not just owner-gated.** The Files table
says "a Settings nav item, owner only" — but the only thing behind Settings
today is custom vocabulary, so a free-plan owner was shown a link that answers 403. PLAN.md's beta gate forbids exactly that. `currentGroup` gained one
boolean, `canCustomiseVocabulary`. One boolean rather than a `features` map
because there is one gated nav item; the second one is the moment to
generalise.

**The preview substitutes in the browser, which the spec did not specify.** It
has to update as somebody types, before anything is saved, so the controller
sends the raw lang templates with their placeholders intact and the Vue fills
them. `Lang::get` without replacements is what returns a raw template — wanted
here and almost nowhere else. Longest placeholder first, exactly as Laravel's
translator does it: without that ordering `:series` matches inside
`:series_plural` and every plural in the preview becomes a singular followed by
a stray `_plural`.

The preview should use a real Series title from the Group where one exists.
"Create a new Trail" reads as a feature; "Create a new Trail — Watercolour for
Beginners" reads as their product.
