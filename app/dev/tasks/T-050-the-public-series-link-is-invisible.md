---
id: T-050
title: A creator cannot find the link to their own public page
stream: selling
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-050 — A creator cannot find the link to their own public page

## Why

**The public selling page is built.** `GET /s/{group}/{series}` renders a
Series' title, summary, price, episode count and episode titles to anybody
signed in or not, offers `POST /checkout/{series}` for a paid one and
`POST /s/{seriesId}/grant` for a free one, and already knows whether the reader
has access. Payment happens on that page today.

**Nothing in the product links to it.** No Vue file references the route. The
generated route helper `series.publicMethod` exists and has no importer. There
is no clipboard copy anywhere in the application. A creator who has just made a
Series ready has no way to discover the URL of their own page short of guessing
the slug pattern.

So the funnel the public page was built for has never been usable. That is a
copy-to-clipboard button and a sentence, not a feature.

## Decisions taken to make this specifiable

**The Series page is where it goes, not the list.** The link belongs to one
Series and the page about that Series is where somebody goes when they are ready
to share it. Putting it on every row of the index would make the list about
distribution rather than about the work.

**Only when published, and say why when not.** `Series::findPublic()` resolves a
**published** Series only, so the link 404s for a draft. Showing a dead URL is
worse than showing none. A draft gets the same block with one line saying the
link goes live when the Series is made ready.

**A field showing the URL, with a copy button — not a bare button.** People paste
links into places a clipboard write cannot reach, and a URL somebody can read is
also a URL they can check. The copy button is the convenience, not the feature.

**No share-to-network buttons.** A social button is a per-network integration
with its own markup, its own tracking and its own decay. The URL is what the
creator asked for and it works in every one of those places.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The public URL, shown on the Series builder page, with a copy control.
- The unpublished state, saying when the link starts working.
- One test that the URL shown is the URL that resolves.

**Out:**

- Per-network share buttons, previews, or open-graph tags. Worth doing and not
  this; open graph in particular is its own task with its own image question.
- Changing anything on the public page itself.
- A short link or any redirect. The URL is already legible, which was the point
  of addressing pages by slug.
- Analytics on the link.

## Files

| Path                                              | Change | Notes                                     |
| ------------------------------------------------- | ------ | ----------------------------------------- |
| `resources/js/components/series/ShareLink.vue`    | new    | The URL, the copy control, the two states |
| `resources/js/pages/share/series/Show.vue`        | edit   | Place it                                  |
| `app/Http/Controllers/Share/SeriesController.php` | edit   | Send the absolute URL as a prop           |
| `lang/en/series.php`                              | edit   | 3 keys                                    |
| `tests/Feature/Series/ShareLinkTest.php`          | new    | 4 cases                                   |

## Database

None.

## Code

```php
// App\Http\Controllers\Share\SeriesController::show()
'publicUrl' => $series->isPublished()
    ? route('series.public', ['group' => $group->slug, 'series' => $series->slug])
    : null,
```

Built on the server with `route()`, not assembled in Vue from parts. A URL
composed in the front end is a second place the route shape lives, and it would
not follow a change to `config/fortify.php`-style path configuration or to the
route definition.

`null` rather than a URL plus a boolean: there is either a link or there is not,
and one value cannot then disagree with the other.

```vue
// resources/js/components/series/ShareLink.vue defineProps<{ url: string | null
}>();
```

The copy control uses `navigator.clipboard.writeText`, which is the first use of
it in this product. It is unavailable on an insecure origin and can be refused,
so the button must show that it failed rather than silently doing nothing — and
the URL is readable and selectable beside it either way, which is the fallback.

## Copy

| Key                        | File                 | English                                                                   |
| -------------------------- | -------------------- | ------------------------------------------------------------------------- |
| `series.share_link`        | `lang/en/series.php` | `Anyone with this link can read about this :series and get access to it.` |
| `series.share_link_draft`  | `lang/en/series.php` | `The link starts working when you make this :series ready to share.`      |
| `series.share_link_copied` | `lang/en/series.php` | `Link copied.`                                                            |

Through the vocabulary, because both lines name the Series noun. Button and
field labels stay inline like every other form (§13's unwired i18n, `T-006`).

## Routes

None. `series.public` already exists.

## Tests

**New: `tests/Feature/Series/ShareLinkTest.php` — 4 cases**

1. `test_a_published_series_sends_its_public_url` — the prop is present and
   absolute.
2. `test_the_url_that_is_shown_is_the_url_that_resolves` — take the prop, request
   it, assert 200 and that it renders the same Series. **This is the case worth
   having**: a link a creator hands out and that 404s is worse than no link, and
   only asking the router both questions catches a mismatch.
3. `test_a_draft_series_sends_no_public_url` — null, so the page shows the
   waiting state rather than a dead address.
4. `test_an_archived_series_sends_no_public_url` — archived is not published, and
   the public page will not resolve it either.

**Changed:** none expected.

## Acceptance

- [x] A published Series shows its public URL on its own page
- [x] The URL shown resolves to that Series
- [ ] Copying it to the clipboard works, and says so when it cannot — **half
      ticked on purpose.** The failure path is verified; the browser pane denies
      `clipboard-write`, so a successful copy is unproven here
- [x] A draft shows no URL and says when one will exist
- [x] The URL is readable and selectable without the copy button
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**This is the cheapest item on the board by value.** Everything behind the link
— the public page, checkout, free access, the access email, playback — was built
and tested, and none of it could be reached by anybody the creator had not added
by hand. The controller's own docblock says that was the gap the public page was
built to close. It closed half of it.

**The routing scan cannot find this, and the reason is worse than it looks.**
`qori:reachability` decides a route is linked if its **name** appears anywhere in
`app/`, `tests/` or `routes/`. `series.public` appears in nine test assertions,
in `DesignReviewCommand`, and in `routes/web.php` as `->name('series.public')` —
its own definition. Any one of those is enough. `T-051` covers that.
