---
id: T-048
title: The way into sharing offers a school, and lowercases a product noun
stream: language
status: doing
owner: claude
estimate: S
depends: none
blocks: T-197
---

# T-048 — The way into sharing offers a school, and lowercases a product noun

## Why

The receiving home shows one panel to anybody who signed up to learn, and it is
the only route from receiving into sharing. It reads:

> Set up your own **school** and publish **series** to the people you already know.

Two defects in one sentence, on the screen that decides whether somebody becomes
a creator.

**"School" is not a Qori word.** `PLAN.md`'s north star says Qori "is not a
school, marketplace, social feed or collection of integrations", and the thing
being offered is a Group. A person who reads this and expects a school gets
something else.

**"series" is a hardcoded, lowercased product noun.** `CLAUDE.md` says never
hardcode Series and never change its casing, because it is configurable per
Group on a higher tier and may be a word the customer chose. The same file
already imports `useTerminology` and uses `plural('series')` twelve lines away,
so this is not a page that lacks the tools.

Found on 11 September 2026 while signed in to check `T-038`'s sidebar lockup.

## Decisions taken to make this specifiable

**The noun is Group, resolved through the vocabulary.** Not "workspace", not
"space", not a school. The panel offers exactly the thing `start-sharing`
creates, and that is a Group.

**The line stays inline English.** Every other string on this page is, and
converting Vue templates to lang keys is `T-006`'s whole job. Adding one lang
key here would leave the panel half-converted, which is worse to finish later
than a panel that is consistently one thing.

**No new copy beyond fixing the two words.** The sentence's shape is fine and
its promise is accurate. Rewriting it invites a second opinion on a line nobody
is complaining about.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- The one sentence in the "Want to share?" panel.
- A test that no Vue file hardcodes a lowercase product noun in prose.

**Out:**

- Converting this page to lang keys. That is `T-006`.
- The panel's title, its button, or when it is shown.
- Auditing every other inline string in Vue for tone. If the new test finds
  more instances, fix the ones it names and no more.

## Files

| Path                                        | Change | Notes        |
| ------------------------------------------- | ------ | ------------ |
| `resources/js/pages/Dashboard.vue`          | edit   | One sentence |
| `tests/Feature/Design/ProductNounsTest.php` | new    | 2 cases      |

## Database

None.

## Code

```vue
Set up your own {{ noun('group') }} and publish {{ plural('series') }} to the
people you already know.
```

`noun` has to be added to the existing `useTerminology()` destructure, which
currently takes `plural` and `forCount` only.

**Check the article.** `CLAUDE.md` forbids "a" or "an" immediately before a
product noun, because the noun may start with a vowel and nothing warns you.
"your own :group" is safe because the possessive carries no article; do not
rewrite it into one that does.

## Copy

None as lang keys — see the decisions above. The English changes from "school"
to the Group noun and from "series" to the Series noun.

## Routes

None.

## Tests

**New: `tests/Feature/Design/ProductNounsTest.php` — 2 cases**

Read from the files, as `TabIndexTest` and `HeadingsTest` do.

1. `test_no_vue_file_hardcodes_a_lowercase_product_noun` — walks
   `resources/js`, fails on `series`, `episode`, `peer` or `group` appearing as
   a bare word in template text rather than through `noun`, `plural` or
   `forCount`. **This is the defect, asserted directly.** Expect it to name more
   than one file on the first run; the Scope says fix what it names.
2. `test_no_vue_file_calls_the_group_a_school` — the word, and the other names
   this product has been called in drafts. Cheap, and it is the one a reviewer
   cannot see in a diff of unrelated work.

Test 1 has to exclude imports, route names, CSS classes and prop names, all of
which legitimately contain these words in lowercase. If the exclusions cannot be
made to hold, narrow it to prose between tags rather than shipping a test
somebody has to silence.

## Acceptance

- [ ] The panel offers a Group, resolved through the vocabulary
- [ ] The Series noun comes from `plural('series')`, with its casing intact
- [ ] No article sits immediately before either noun
- [ ] The new test fails before the fix and passes after
- [ ] Every file the test names is fixed, and nothing beyond them is touched
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

**2026-09-24 — claimed, and three things the 11 September spec could not
know.**

- **Acceptance used the old process.** "Board regenerated (`php artisan
  qori:tasks`)" became `bin/tasks --check` in `qori-plan` when the plan moved
  (21 September); the closing lines are now the current ones.
- **"School" has two legitimate uses in `resources/js`, so test 2 carries an
  allow-list, each entry a file, the phrase on the matching line, and a
  reason.** `Welcome.vue` says Qori is "not a school" (`T-190`), which is the
  north star, not a name for the Group. `Register.vue`'s share hint, "Set up a
  school and publish series.", is `T-108`'s: it moves both hints to lang and
  its copy waits on the owner, so fixing it inline here would pre-empt that
  and be rewritten. The entry names `T-108`, which deletes it. This settles
  `T-108`'s open bullet on the order: this task lands first. "Workspace", the
  Group's code name until 9 September, is checked beside "school"; "Google
  Workspace" is a vendor's product and is not.
- **Test 1 walks every page but the staff console.** A first pass names 14
  phrases in 8 files, 5 of them in `resources/js/pages/admin/`. The console
  reads across Groups for Qori's own staff, so no Group's vocabulary applies
  there (`docs/architecture/admin-console.md`); it is excluded with that
  reason. The other four files it names are fixed, under **Added during
  execution**.

## Added during execution

| Path | Change | Notes |
| --- | --- | --- |
| `resources/js/pages/public/Certificate.vue` | edit | "this series", "this peer", "their series" |
| `resources/js/pages/share/series/Index.vue` | edit | "your peers", twice; a fixup line |
| `resources/js/pages/share/series/Show.vue` | edit | "this episode"; a fixup line |
| `resources/js/pages/share/settings/Integrations.vue` | edit | "your series", twice |

## Notes

This panel is the counterpart to `CreateGroupForNewUser` skipping people who
signed up to learn: not asking for a Group at signup must not mean never being
able to have one. That makes it the single door between the two halves of the
product, and the copy on it has never been read by anyone deciding vocabulary.
