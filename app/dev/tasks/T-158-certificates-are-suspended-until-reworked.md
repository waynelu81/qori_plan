---
id: T-158
title: Certificates are suspended until reworked
stream: design
status: doing
owner: claude
estimate: S
depends: none
blocks: none
---

# T-158 — Certificates are suspended until reworked

## Why

The owner, 21 September 2026: "suspend certificate feature first, the current
implementation does not work. I do not want to spend effort right now to
correct it. Shall pick it up in the future." Today a Peer who finishes a
Series is shown "View your certificate", the Peer sidebar carries "My record",
and a creator's Series forms ask for hours "shown on the certificate". After
this, none of those is shown and the public check page answers 404, while
every certificate code is still minted and kept, so the rework (`T-109`)
turns it back on with nothing lost (`D-044`).

## Decisions taken to make this specifiable

- **One switch, `config('qori.certificates.enabled')`, default off**, read from
  `QORI_CERTIFICATES`. Suspending by deleting code would make `T-109` rebuild
  what exists; a switch keeps the code tested and the data growing.
- **Minting stays on.** `ProgressService` still writes `certificate_code` when
  an Access finishes. Nobody sees it, and stopping it would leave every Peer
  who finished during the suspension without a code when it returns.
- **"My record" is suspended with it.** It is §12's hours log and every row
  links to a certificate; without certificates it is a list of links to 404s.
- **The creator's Hours field is hidden, and kept in the form requests.** Hours
  feed only the certificate and the record. A Series that already has hours
  keeps them.
- **Suspended routes answer 404**, the same as a page that is not there, rather
  than an error that names a feature nobody can see.
- **Copy that mentions certificates in passing is left alone** — the deletion
  lines in `lang/en/series.php` and the vocabulary settings page. Each is still
  true of the data, and rewording them is `T-109`'s job when it decides what a
  certificate is.

## Preconditions

None.

## Scope

**In:** the switch; the public check page, the Peer record page and its nav
item, the certificate link on a Peer's Series, and the creator's Hours field
all hidden or 404 while it is off; the three design-review shots skipped; tests
covering the certificate code run with the switch on, and one new test file
shows everything hidden with it off; the flow doc says so.

**Out:** changing what a certificate says (`T-109`), the vocabulary in
certificates (`T-005`), and any change to minting or to `completed_at`.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `config/qori.php` | edit | `certificates.enabled` |
| `.env.example` | edit | `QORI_CERTIFICATES=false` with a line saying why |
| `app/Http/Controllers/CertificateController.php` | edit | 404 while suspended |
| `app/Http/Controllers/Shared/SharedController.php` | edit | `record()` 404 while suspended; `show()` passes `certificateCode` null |
| `app/Http/Middleware/HandleInertiaRequests.php` | edit | shares `features.certificates` |
| `resources/js/types/global.d.ts` | edit | the shared prop's type |
| `resources/js/components/AppSidebar.vue` | edit | "My record" only while on |
| `resources/js/pages/share/series/Index.vue` | edit | Hours field only while on |
| `resources/js/components/series/SeriesForm.vue` | edit | Hours field only while on |
| `app/Console/Commands/DesignReviewCommand.php` | edit | skip `090-certificate`, `420-shared-record`, `620-empty-shared-record` while off |
| `tests/Feature/Shared/CertificatesSuspendedTest.php` | new | the suspended behaviour |
| `tests/Feature/Shared/CertificateTest.php` | edit | switch on in `setUp()` |
| `tests/Feature/DesignReviewFixtureTest.php` | edit | switch on where it opens the certificate |
| `tests/e2e/public-link.spec.ts` | edit | ends at "mark it as done", and asserts no certificate link |
| `docs/flows/series.md` | edit | the certificates section says it is suspended and how |
| `docs/tinker/e2e.md` | edit | the journey no longer reaches a certificate |

## Database

None. `accesses.certificate_code` and `series.hours` are unchanged and still written.

## Code

`config('qori.certificates.enabled')` is the only switch; every reader asks it
directly. `HandleInertiaRequests::share()` adds
`'features' => ['certificates' => (bool) config('qori.certificates.enabled')]`.

## Copy

None — nothing new is said; things stop being shown.

## Routes

None added or removed. `GET certificates/{code}` and `GET shared/record` stay
registered and answer 404 while suspended.

## Tests

**New: `tests/Feature/Shared/CertificatesSuspendedTest.php` — 4 cases**

1. `test_the_check_page_is_not_found_while_suspended` — a real code, 404.
2. `test_the_record_is_not_found_while_suspended` — a Peer with a finished Access, 404.
3. `test_a_finished_series_offers_no_certificate_while_suspended` — `certificateCode` null, and the code is still minted on the Access.
4. `test_pages_are_told_certificates_are_off` — the shared `features.certificates` prop is false.

**Changed:**

- `tests/Feature/Shared/CertificateTest.php` — switched on in `setUp()`; every case still passes.
- `tests/Feature/DesignReviewFixtureTest.php` — switched on before opening the certificate.

## Acceptance

- [ ] With `QORI_CERTIFICATES` unset: no "View your certificate", no "My record", no Hours field, and `/certificates/{code}` and `/shared/record` answer 404
- [ ] A Peer finishing a Series still gets a `certificate_code`
- [ ] With it set to `true`, everything behaves as before
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

None.
