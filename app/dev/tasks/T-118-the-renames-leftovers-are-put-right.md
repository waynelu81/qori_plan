---
id: T-118
title: The words the renames mangled are put right
stream: operations
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-118 — The words the renames mangled are put right

## Why

The 9 September rename (`f74757a`, "Rename the domain all the way through")
replaced words inside other words. `T-116` fixed the one a password manager
reads, `enroll` turned into `grantl`. The rest are still there:

- **A sentence a buyer reads.** `lang/en/accesses.php:76`,
  `accesses.consent.required`, says "Please agree to be peered before
  granting." It was "Please agree to be contacted before enrolling." A buyer
  who leaves the email-consent box unticked sees it, through
  `StartSeriesAccessRequest` and `GrantInSeriesRequest`, and it now puts the
  creator's verb on the buyer.
- **A method name.** `AccessService::guardGrantlable()`
  (`app/Services/AccessService.php:52`, `:308`), which draft `T-094` names.
- **Comments and docs.** "grantlable" in `AccessService.php:190` and
  `SeriesService.php:139`, and in `docs/flows/series.md:73`, `:224` and
  `docs/tinker/accesses.md:123`; "Grantling" in `docs/flows/accesses.md:32`,
  `:39`, `:57`, `docs/flows/series.md:160`, `docs/tinker/README.md:11`, and
  `tests/Feature/Access/AccessServiceTest.php:65`, `:158`.

The route prefix moved from `/w/{group}` to `/g/{group}` and three flow docs
still say `/w/`: `docs/flows/groups.md:11`, `:78`, `:93`,
`docs/flows/storage.md:157`, `:169`, and `docs/flows/accesses.md:77`, `:94`,
`:103`. `T-116` corrected the one in `docs/flows/auth.md`. CLAUDE.md says the
flow docs describe what the code does today.

Afterwards no customer reads a mangled sentence, and no code or live document
names a word the renames made up.

## Decisions taken to make this specifiable

Brought to ready on 28 September 2026, from the code.

**The buyer's sentence is already gone.** `T-178` removed
`accesses.consent.required` with the rule that used it (`cfc6b8c`, 22 September
2026), so the one question that was the owner's has no sentence left to ask it
about.

**`guardGrantlable()` becomes `guardGrantable()`.** It answers whether a Series
can be granted in — a Group behind it, published, the Group active — and the
word the rename meant was "grantable". A longer name for what it checks would
be a second rename of a method `T-094`'s draft already names; that draft's two
mentions change with it.

**The words go everywhere the code and the live documents say them.**
"grantlable" becomes "grantable" and "Grantling" "Granting", in `app/`, `tests/`,
`docs/flows` and `docs/tinker`; every `/w/` path in `docs/flows` becomes `/g/`,
as the routes have been since the rename.

**`DocumentationTest` refuses them from now on.** One more reversed claim, for
the made-up words and a `/w/` path, so the next rename cannot leave them
standing in a live document. The planning history keeps them: it records what
was written on a day.

## Preconditions

None.

**Data this task verifies against:** None; no behaviour changes.

**Equipment:** None.

## Scope

**In:**

- The method's name, its caller and its comments.
- The words in comments, tests and the live documents.
- The `/w/` paths in `docs/flows`.
- The reversed claim, and `T-094`'s two mentions.

**Out:**

- The planning history and finished tasks' reports, which record the words.

## Files

| Path                                                                                           | Change | Notes                                     |
| ---------------------------------------------------------------------------------------------- | ------ | ----------------------------------------- |
| `app/Services/AccessService.php`                                                               | edit   | `guardGrantable()`, its caller, a comment |
| `app/Services/SeriesService.php`                                                               | edit   | a comment                                 |
| `tests/Feature/Access/AccessServiceTest.php`                                                   | edit   | a comment                                 |
| `tests/Feature/DocumentationTest.php`                                                          | edit   | the reversed claim                        |
| `docs/flows/accesses.md` `docs/flows/series.md` `docs/flows/groups.md` `docs/flows/storage.md` | edit   | the words, and `/w/`                      |
| `docs/tinker/README.md`                                                                        | edit   | "Granting"                                |

Flows: the four above, whose words change and whose call chains do not.

## Database

None.

## Code

```php
// App\Services\AccessService
private function guardGrantable(Series $series, ?Group $group, bool $paid = false): void;
```

## Copy

None.

## Routes

None.

## Tests

**Changed:** `DocumentationTest`'s reversed claims gain one, which the live
documents pass once the words are gone. No behaviour changes, so the suite as
it stands is the rest of the proof.

## Acceptance

- [x] No code or live document says "grantlable", "Grantling" or a `/w/` path
- [x] `DocumentationTest` refuses them
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~The buyer's consent sentence — the owner's.~~ **Answered from the code, 28
  September 2026:** `T-178` removed it (Decisions).
- ~~What `guardGrantlable()` becomes.~~ **Answered 28 September 2026:**
  `guardGrantable()` (Decisions).
- ~~Whether `DocumentationTest` gains a reversed claim.~~ **Answered 28
  September 2026:** yes (Decisions).

## Re-scope log

None.

## Notes

Written while building, 28 September 2026: the reversed claim matches `grantl`
anywhere, case-insensitive, rather than as a word — a word boundary missed
`guardGrantlable` inside the flows' call chains. No English word contains
"grantl". `tests/Feature/Settings/PasskeyEndpointsTest.php` keeps the word on
purpose, in `T-116`'s account of the bug it fixed; tests are not live
documents, and that one is a record.
