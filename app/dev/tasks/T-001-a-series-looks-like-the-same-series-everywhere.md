---
id: T-001
title: A Series looks like the same Series everywhere
stream: design
status: done
owner: claude
estimate: M
depends: none
blocks: T-003
---

# T-001 — A Series looks like the same Series everywhere

## Why

A Series is rendered on five surfaces — the Share list, the Series builder,
Shared with me, the Peer's own Series page and the public page — and each was
written separately. The same object shows a different status word, a different
progress treatment and no visual identity at all, so it reads as five things
rather than one. A creator who has just made something cannot recognise it on
the page they send to somebody else.

Day 4 of the redesign brief: share the Series' **identity**, not one whole card
component. Three compositions over shared parts, never one component with
`isPublic`, `isPeer` and `showProgress` flags.

## Decisions taken to make this specifiable

Both were listed as blocking when this was a draft. Recorded here rather than
in `decisions.md` because neither outlives the task.

**A Series cover is generated from its title, not uploaded.** There is no cover
column and this task does not add one. Reasons: Day 4 is about consistency, not
about adding a feature; an upload flow would push this from M to L inside the
week meant to finish the redesign; and a deterministic mark is identical on all
five surfaces with no data to keep in sync. It does not foreclose real covers —
a `SeriesCover` that falls back to a generated mark is exactly the shape wanted
when an image column arrives.

The mark is the title's initials, ink on the muted surface, with a gold
hairline. **No per-Series hue.** One gold is the brand rule, and a colour
derived from an id is the rainbow that rule exists to prevent. Two Series with
the same initials look alike; their titles are beside them.

**Status vocabulary is per-surface, and that is not an inconsistency.** A Peer
can never see a Draft or an Archived Series — only published ones are grantable
or public — so "Draft" is a word that cannot apply to them. Creator surfaces
show the Series' state (Draft / Ready to share / Archived); Peer surfaces show
the reader's own relationship to it (Not started / N of M / Finished); the
public page shows neither, because a stranger's question is what it costs and
how long it is.

## Preconditions

`php artisan wayfinder:generate --with-form`, and a browser. **There is no
JavaScript test runner in this project** — no vitest, no jest, and
`package.json` has no `test` script. Vue components cannot be unit-tested here,
which shapes the Tests section below: the server-side tests cover prop shape,
and the visual result is verified by eye or not at all.

## Scope

**In:**

- `SeriesCover`, `SeriesStatus` and `SeriesProgress` as shared parts.
- Applying them across all five surfaces.
- Making the four progress bars one.

**Out:**

- A cover image column, an upload, or any new Series data.
- A single card component for all five surfaces. The brief forbids it by name.
- Rewriting the public page's composition beyond adopting the shared parts.
- Renaming anything. `Series` is already the domain name.

## Files

| Path                                                | Change | Notes                                                           |
| --------------------------------------------------- | ------ | --------------------------------------------------------------- |
| `resources/js/components/series/SeriesCover.vue`    | new    | Initials mark, three sizes                                      |
| `resources/js/components/series/SeriesStatus.vue`   | new    | Creator-side state                                              |
| `resources/js/components/series/SeriesProgress.vue` | new    | Peer-side progress, replaces four copies                        |
| `resources/js/pages/share/series/Index.vue`         | edit   | Cover + `SeriesStatus`; drop `statusLabel()`                    |
| `resources/js/pages/share/series/Show.vue`          | edit   | Cover in the header; `SeriesStatus` in the action slot          |
| `resources/js/pages/shared/Index.vue`               | edit   | Cover + `SeriesProgress`                                        |
| `resources/js/pages/shared/Show.vue`                | edit   | Cover in the header; `SeriesProgress`                           |
| `resources/js/pages/Dashboard.vue`                  | edit   | `SeriesProgress` in "Pick up where you left off"                |
| `resources/js/pages/public/Series.vue`              | edit   | Cover beside the title                                          |
| `app/Http/Controllers/Share/SeriesController.php`   | edit   | `index()` sends `title` for the cover — confirm it already does |
| `tests/Feature/Series/SeriesIdentityTest.php`       | new    | 5 cases                                                         |

## Database

None. Deliberately — see the decision above.

## Code

```vue
// resources/js/components/series/SeriesCover.vue defineProps<{ title: string;
size?: 'sm' | 'md' | 'lg'; // 40px / 56px / 80px, default 'md' }>();
```

Initials: first letter of the first two words that start with a letter or
digit, uppercased, at most two characters. A single-word title gives one
letter. An empty or symbol-only title gives an empty mark rather than a crash —
`useInitials` already solves this shape for people and its `getInitials` may be
reused directly if it behaves; check before duplicating it.

`aria-hidden="true"`: the title is always beside it, and a screen reader
announcing "W B" before the title is noise.

```vue
// resources/js/components/series/SeriesStatus.vue defineProps<{ status: string
}>(); // 'draft' | 'published' | 'archived'
```

Owns the mapping that `share/series/Index.vue` currently holds in a local
`statusLabel()` function: `published` → "Ready to share" (success tone),
`archived` → "Archived", anything else → "Draft" (muted). Never prints the raw
column value. Unknown statuses fall to "Draft" rather than throwing — a status
added to the model must not blank a list.

```vue
// resources/js/components/series/SeriesProgress.vue defineProps<{ percent:
number; isComplete: boolean; done?: number; // when given, renders "3 of 6"
beside the bar total?: number; }>();
```

Replaces four hand-rolled bars. The complete state uses `bg-success`, otherwise
`bg-foreground/60` — both already in use, and the point is that they stop being
in use in four places.

## Copy

| Key | File | English                                                                                                                                                          |
| --- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| —   | —    | **None.** Every string here already exists: "Ready to share", "Archived", "Draft" move out of a Vue file into a component, and the progress figures are numbers. |

Vue templates keep their inline English (§13's unwired i18n). Do not add more.

## Routes

None.

## Tests

**There is no JavaScript test runner**, so none of these components can be unit
tested. Say so in the report rather than implying coverage that does not exist.
What can be tested is the risk that actually bites: five controllers sending
five different shapes for the same object.

**New: `tests/Feature/Series/SeriesIdentityTest.php` — 5 cases**

1. `test_the_share_list_sends_what_a_cover_needs` — `series.0.title` present.
2. `test_the_series_builder_sends_what_a_cover_needs` — `series.title`.
3. `test_the_peer_list_sends_title_and_progress` — `title`, `progressPercent`,
   `isComplete`.
4. `test_the_peer_series_page_sends_title_and_progress`.
5. `test_the_public_page_sends_title_and_episode_count` — and **not**
   `status`, which a stranger has no use for and which would leak whether a
   Series was ever a draft.

**Changed:** none expected.

## Acceptance

- [x] The same Series is recognisable on all five surfaces
- [x] One cover component, generated from the title, with no new data
- [x] Creator surfaces show Series state; Peer surfaces show the reader's
      progress; the public page shows neither
- [x] The four progress bars are one component
- [x] No component takes an `isPublic`, `isPeer` or `showProgress` flag
- [x] Checked in a browser, both themes, on every one of the five surfaces
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**The initials rule in the Code section was wrong and `getInitials` was right.**
The spec said "first two words"; `useInitials` takes first and _last_, which is
better for a title — "Watercolour for Beginners" gives WB rather than WF,
because English puts a stop word in second position more often than in last.
Reused rather than duplicated, as the spec itself said to check.

**Three progress bars, not four.** The fourth the spec counted is the creator's
per-Episode distribution in the progress panel — a different measurement (where
a room of Peers stops) wearing the same shape, and it carries no label. Left
alone.

`PageHeader` gained a `#before` slot rather than a `cover` prop, so it never has
to know what a Series is.
