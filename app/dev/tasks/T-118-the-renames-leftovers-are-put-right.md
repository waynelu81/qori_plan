---
id: T-118
title: The words the renames mangled are put right
stream: operations
status: draft
owner: unassigned
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

To be written once the questions below are answered.

## Preconditions

To be written.

## Scope

**In:**

- To be written.

**Out:**

- To be written.

## Files

To be written.

## Database

None.

## Code

To be written.

## Copy

To be written.

## Routes

None.

## Tests

To be written.

## Acceptance

- [ ] To be written
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- The buyer's consent sentence, in Qori's nouns and the buyer's own verb. It
  is consent copy under §9, and the classroom sprint's invitee work reads the
  same request. The owner's.
- What `guardGrantlable()` becomes (`guardGrantable()`, or a name that says
  what it checks), and the matching `T-094` wording. Anyone's.
- Whether `DocumentationTest` gains a reversed claim for `/w/{group}` and the
  made-up words, so the next rename cannot leave them. Anyone's.

## Re-scope log

None.

## Notes

None.
