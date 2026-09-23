---
id: T-108
title: Registration describes sharing and receiving in Qori's nouns
stream: design
status: draft
owner: unassigned
estimate: S
depends: T-196
blocks: none
---

# T-108 — Registration describes sharing and receiving in Qori's nouns

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 17 September 2026 from
> [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-8.

## Why

Registration asks "What brings you here?", and each option's hint is inline
English in `resources/js/pages/auth/Register.vue`: line 14 reads "Set up a
school and publish series." and line 19 "Take series someone has shared with
you." R-004 F-8 found both on `040-register` and `720-register-validation` at
both widths and in both themes, reconfirming R-001 F-1 a week on. "School" is a
thing `PLAN.md` says Qori is not, "series" is a product noun spelled by hand and
lowercased, and "take series" is course language rather than receiving what
somebody chose to share. The hint is all a stranger is told about a choice that
does one thing: decide, once, whether a Group is made (D-007).

Afterwards both hints are lang lines with Group and Series interpolated through
the terminology layer, one describing sharing and one receiving, and
`Register.vue` spells neither sentence.

## Decisions taken to make this specifiable

**Provisional: the hints move to lang now, as page props, without waiting on
`T-006`.** CLAUDE.md forbids adding inline English to Vue, and two rewritten
sentences are two added. `T-006` has not decided how Vue reads lang, but the
auth pages already answer it for themselves: `Fortify::loginView` and
`Fortify::verifyEmailView` in `app/Providers/FortifyServiceProvider.php` pass
lang lines as named props, under a comment leaving field labels to `T-006`.
Whatever `T-006` settles converts these props along with Login's.

**Provisional: the nouns resolve in PHP through `Terminology::line()`, not
`useTerminology()`.** A sentence is authored whole in lang with the noun
interpolated; `useTerminology()` serves a noun Vue spells itself, and Vue will
spell none here. A guest has no Group, so the defaults apply, and the existing
article test in `tests/Feature/TerminologyTest.php` covers the new lines.

**Copy only, saying what the choice does and nothing durable.** Per D-007 it is
read once, by `CreateGroupForNewUser`, and not stored, so the sharing hint may
say a Group is set up and the receiving hint may not imply a role. The values
`share` and `learn`, `App\Enums\SignupIntent` and the preselected `share` stay.

**`T-048` is not widened.** Its line 248 in `resources/js/pages/Dashboard.vue`
is the same mistake on the receiving home, and stays its own `ready` task.

## Preconditions

**Data this task verifies against:** a clean database, and the worlds
`php artisan qori:design-review` seeds to recapture both screens.

**Equipment:** None beyond the browser that command drives.

## Scope

**In:**

- The two intent hints, moved to `lang/en/auth.php` and passed as props.

**Out:**

- The labels "I want to share" and "I want to learn" and the page's other
  inline English: `T-006`, unless the owner moves the labels here.
- `T-048`'s Dashboard sentence and its planned `ProductNounsTest`.
- What the choice does (D-007), and custom nouns for a registration begun from
  a public Series: the register page has no Group.
- R-001 F-3's required-field bubble on `720-register-validation`; R-004 F-7,
  paid entry (`T-011`, `T-027`); R-004 F-12, the certificate (`T-109`).
- "School" in comments and docblocks, as in `SignupIntentTest`.

## Files

| Path                                       | Change | Notes                                             |
| ------------------------------------------ | ------ | ------------------------------------------------- |
| `resources/js/pages/auth/Register.vue`     | edit   | Two props replace the literals on lines 14 and 19 |
| `app/Providers/FortifyServiceProvider.php` | edit   | `Fortify::registerView` passes both props         |
| `lang/en/auth.php`                         | edit   | A new `register` group, two keys                  |
| `tests/Feature/Auth/RegistrationTest.php`  | edit   | Two cases                                         |

Flows: none — the register page's props are not a call chain the auth flow doc
describes, and the registration request is unchanged.

## Database

None.

## Code

Provisional, following the first two decisions. `Fortify::registerView`, inside
its `@chisel-registration` markers, adds `shareHint` and `learnHint`, each
`app(Terminology::class)->line('auth.register.share_hint')` or `learn_hint`.
`Register.vue` declares both as `string` props; `intents`, between the imports
today (lines 10–21), becomes a `computed` below `defineProps` using them.

## Copy

Proposed English, the owner's to approve.

| Key                        | File               | English                                                                 |
| -------------------------- | ------------------ | ----------------------------------------------------------------------- |
| `auth.register.share_hint` | `lang/en/auth.php` | Set up your :group and share :series_plural with the people you choose. |
| `auth.register.learn_hint` | `lang/en/auth.php` | Open :series_plural somebody has shared with you.                       |

## Routes

None.

## Tests

Provisional on the first decision; if the hints stay inline, these become file
reads and `T-048`'s `ProductNounsTest` is their home.

**New, in `tests/Feature/Auth/RegistrationTest.php` — 2 cases**

1. `test_it_passes_the_intent_hints_from_lang` — the `register` route renders
   `auth/Register` with `shareHint` and `learnHint` equal to
   `Terminology::line()` of their keys.
2. `test_it_names_the_group_and_series_in_the_intent_hints` — `shareHint`
   contains the default Group singular and Series plural, `learnHint` the
   Series plural, and neither contains "school".

**Changed:** None; `tests/Feature/TerminologyTest.php` already checks articles.

## Acceptance

- [ ] `040-register` and `720-register-validation` describe sharing and
      receiving in Group and Series, with no "school" or lowercased "series"
- [ ] Both hints come from `lang/en/auth.php` through `Terminology::line()`,
      and `Register.vue` spells neither sentence
- [ ] No article sits immediately before either noun placeholder
- [ ] Registering with either choice makes a Group, or does not, as before
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Confirm the hints move to lang now as `Fortify::registerView` props, rather
  than staying inline beside `useTerminology()` as `T-048` chose, or waiting for
  `T-006` to decide how Vue reads lang. The language stream owner's.
- Approve the two sentences under Copy, the receiving verb most. The owner's.
- Decide whether "I want to share" and "I want to learn" move with the hints:
  "learn" is the course framing F-8 objects to, and an inline label over a lang
  hint is the half-conversion `T-048` declined. The owner's.
- Settle the order with `T-048`: its planned
  `test_no_vue_file_calls_the_group_a_school` walks `resources/js`, and its
  Scope fixes what the test names, so landing first it would likely fix line 14
  inline. The design and language stream owners'.

## Re-scope log

None.

## Notes

R-001 marked F-1 "Task needed", grouped with its F-5 and F-6, but no task file
cites it, which is why R-004 found the hints unchanged. F-5 and F-6 stay out.

**23 September 2026.** `T-196` changes the same page first: while a Series is
waiting, `registerView` passes `receiving` and `Register.vue` shows one line
in place of the choice, from `auth.register.for_series`. This task's two hints
are for the ordinary page, where the choice is still asked; it depends on
`T-196` for `Register.vue`, `FortifyServiceProvider.php` and `lang/en/auth.php`.
