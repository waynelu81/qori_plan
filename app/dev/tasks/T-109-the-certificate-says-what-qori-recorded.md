---
id: T-109
title: The certificate says what Qori recorded
stream: design
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-109 — The certificate says what Qori recorded

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 17 September 2026 from
> [R-004](../design-review/passes/R-004-2026-09-17-final-web-review.md) F-12.

## Why

On `090-certificate`, and live after Sam marked the last two Episodes done on
`410-shared-series`, the footer said Harbour Lane Studio "marked this series
complete for this peer". Nobody at Harbour Lane did, and nobody could:
`ProgressService::complete()` (`:204`) stamps `completed_at` and mints
`certificate_code` once the Peer has ticked every Episode, with no creator
step. The sentence claims an attestation Qori never records; `PLAN.md` settles
that certificates state only what Qori can prove. It is inline English in
`resources/js/pages/public/Certificate.vue` (`:103-109`), and the same claim
sits in that file's docblock (`:13-15`), `CertificateController`'s
(`:19-21`) and `docs/flows/series.md` (`:207`).

Afterwards the footer says the Peer marked every Episode done on Qori, that it
is not an accredited qualification, and, when hours are declared, that the
Group stated them — from lang, in the Group's own nouns.

## Decisions taken to make this specifiable

- **The certificate reports the Peer's action and nothing more.** Completion is
  declared, not observed (`ProgressService.php:17`), so it says "marked done".
- **No approval step is added to make the old sentence true.** A creator
  sign-off is a product change and would start in `decisions.md`.
- **`CertificateController` renders the lines through `Terminology::line()`
  with the access's Group.** Vue has no i18n wired, so pages take sentences as
  props (`PublicSeriesController`, `SharedController`); passing the Group
  also honours `T-005`'s decision that certificates inherit the Group's nouns.
- **Values go in as `:name`, never `:peer`, `:group` or `:series`.** Those are
  the noun placeholders, and a caller's value would replace the noun
  (`Terminology.php:84`).
- **Three keys; the hours line only when `series.hours` is set.** Today's
  footer mentions "the hours shown" when none are shown. _Provisional._
- **A new `lang/en/certificates.php`.** One file per feature. _Provisional._
- **The Group is required, like the Series and the Peer.** `accesses.group_id`
  cascades on delete, so the inline `'the creator'` fallback
  (`Certificate.vue:105`) is unreachable and goes. _Provisional._

## Preconditions

**Data this task verifies against:** A clean database for the tests; for the
page, the design-review world (`php artisan qori:reset full --force`) and
`DesignReviewSeeder::CERTIFICATE_CODE`.

**Equipment:** None for the tests. Reading the footer needs a browser, or a
capture from `php artisan qori:design-review --only=090-certificate`.

## Scope

**In:**

- Replace the first footer paragraph of `public/Certificate.vue` with the three
  lines, passed in as props by `CertificateController::show()`.
- Correct the two docblocks and the §12 paragraph in `docs/flows/series.md`.

**Out:**

- Any creator approval, sign-off or revocation of a certificate.
- The rest of the certificate's inline English ("Certificate of completion",
  "Issued by", "This certifies that", "Hours", "as stated by the creator", the
  verify and print lines), and nouns in mail. Those belong to `T-005`.
- Sticky completion, which is unchanged (`docs/flows/series.md` §12).
- R-004's neighbouring findings: touch targets on `410-shared-series` (`T-105`,
  F-4), the paid-entry sentence (`T-011`, F-7) and the receiving card
  (`T-027`, F-10).
- A PDF or emailed certificate. None exists: the page is print-styled, and
  nothing in `app/Notifications` or `resources/views` mentions a certificate.

## Files

| Path                                             | Change | Notes                                                    |
| ------------------------------------------------ | ------ | -------------------------------------------------------- |
| `app/Http/Controllers/CertificateController.php` | edit   | Require the Group; three lines in the prop; docblock     |
| `resources/js/pages/public/Certificate.vue`      | edit   | Footer paragraph from props; drop the fallback; docblock |
| `lang/en/certificates.php`                       | new    | Three keys                                               |
| `tests/Feature/Shared/CertificateTest.php`       | edit   | Four cases                                               |
| `docs/flows/series.md`                           | edit   | The §12 paragraph at `:204-208`                          |

## Database

None.

## Code

`show(string $code, Terminology $terminology): Response`, method-injected like
`Share\SetupController::show()`. The `certificate` prop keeps its six keys,
`creator` non-null, and gains `recorded` (string), `notAccredited` (string) and
`hoursStated` (`?string`, null when `$series->hours` is). Names provisional.

## Copy

| Key                           | File                       | English                                                                     |
| ----------------------------- | -------------------------- | --------------------------------------------------------------------------- |
| `certificates.recorded`       | `lang/en/certificates.php` | This records that :name marked every :episode in this :series done on Qori. |
| `certificates.not_accredited` | `lang/en/certificates.php` | It is not an accredited qualification.                                      |
| `certificates.hours_stated`   | `lang/en/certificates.php` | :name stated the hours shown for this :series. Qori does not measure them.  |

`:name` is the Peer in `recorded` and the Group in `hours_stated`. Provisional.

## Routes

None.

## Tests

**Changed: `tests/Feature/Shared/CertificateTest.php` — 4 new cases**

1. `test_it_says_the_peer_marked_every_episode_done` — `recorded` names Priya
   Nair and not "Rita's Piano"; `notAccredited` is the lang line
2. `test_it_attributes_declared_hours_to_the_group` — `hoursStated` names the Group
3. `test_it_says_nothing_about_hours_when_none_were_declared` — `hours` null
4. `test_it_speaks_the_groups_own_nouns` — an entitled Group's nouns in `recorded`

No existing case changes; `test_a_stranger_can_check_a_certificate` still holds.

## Acceptance

- [ ] A finished Peer's certificate says they marked every Episode done on
      Qori; nothing says the Group marked, approved or confirmed completion
- [ ] It still says it is not an accredited qualification, and attributes
      declared hours to the Group. With no hours, it says nothing about hours
- [ ] Every new sentence comes from `lang/en/certificates.php` in the Group's
      nouns, and `TerminologyTest`'s article check passes
- [ ] `docs/flows/series.md` and both docblocks describe what the page says
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Added 21 September 2026: certificates are suspended (`T-158`, `D-044`).**
  The owner found the implementation does not work and switched it off rather
  than fix it now. This task is now where it comes back: whoever picks it up
  first finds out from the owner what fails — _asked_ is the state to record —
  then fixes it, rewords the lines that mention certificates while it was off
  (`lang/en/series.php` `delete_confirm`, `deletion_notice_for_peer`,
  `purged_for_peer`; `resources/js/pages/share/settings/Vocabulary.vue`), puts
  back the e2e steps `T-158` took out of `tests/e2e/public-link.spec.ts`, and
  sets `QORI_CERTIFICATES=true`. Codes minted during the suspension are valid.

- Approve the three sentences, and whether to say "marked every Episode done"
  or "finished". The stream owner's.
- Decide whether "Issued by" and "This certifies that" in the header also
  overstate. If they do, this task grows; if `T-005`'s "the Group's document"
  covers them, they stay Out. The owner's.
- Which task edits `Certificate.vue` and `CertificateController.php` first:
  proposed `T-109`, with `T-005` depending on it, since this is small and
  `design` blocks beta. Both streams are wayne's: the stream owner's.
- Confirm or overturn the three provisional decisions (the separate hours
  line, the new lang file, the required Group). The stream owner's.
- Before marking it `ready`, check again that nobody has built an emailed or
  PDF certificate. Anyone's.

## Re-scope log

None.

## Notes

- R-004 left Sam's new completion stamp in place, because completion is
  sticky. Reseeding removes it; the seeded certificate belongs to Priya.
- `T-090` (a draft) also edits `docs/flows/series.md`, in another section.
