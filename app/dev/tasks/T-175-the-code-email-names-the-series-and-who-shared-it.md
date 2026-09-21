---
id: T-175
title: The code email names the Series and who shared it
stream: onboarding
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-175 — The code email names the Series and who shared it

## Why

A Peer asking for a Series from its page got "Your Qori code is 123456" and
"Type 123456 on the page you came from" — from a product they had not heard
of, naming neither the Series nor who shared it (the first-share journey's
step 11: "the code email never names who shared it"). Afterwards a code asked
for from a Series page names both.

## Decisions taken to make this specifiable

- **The code stays in the subject**, where a phone shows it (`T-073`), beside
  the Series' title: "Your code for Beginner Piano is 123456".
- **The line names the Group that shared it**: "You asked to get Beginner
  Piano, shared by Rita's Piano. Type 123456 on its page to carry on. It works
  for 10 minutes." The minutes come from `LoginCodeService::LIFETIME_MINUTES`.
- **A code sent without a Series stays plain**, as `qori:mail:check` sends
  one.

## Preconditions

None.

**Data this task verifies against:** a clean database.

**Equipment:** None.

## Scope

**In:**

- `LoginCodeService::send()` takes the Series; `SeriesAccessController` passes
  it on start and resend; `LoginCodeNotification` names it.

**Out:**

- The magic-link email and the access email, which already name what they
  are for.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Services/LoginCodeService.php` | edit | `send(User, ?Series)` |
| `app/Notifications/LoginCodeNotification.php` | edit | the Series' lines |
| `app/Http/Controllers/SeriesAccessController.php` | edit | passes the Series |
| `lang/en/auth.php` | edit | `code.series_subject`, `code.series_line` |
| `docs/flows/auth.md` | edit | sign in with a code |
| `tests/Feature/Access/SeriesAccessCodeTest.php` | edit | two cases |

## Database

None.

## Code

```php
public function send(User $user, ?Series $series = null): void; // LoginCodeService
// LoginCodeNotification(string $code, int $minutes, ?string $seriesTitle = null, ?string $sharedBy = null)
```

## Copy

| Key | File | English |
| --- | --- | --- |
| `code.series_subject` | `lang/en/auth.php` | "Your code for :title is :code" |
| `code.series_line` | `lang/en/auth.php` | "You asked to get :title, shared by :name. Type :code on its page to carry on. It works for :minutes minutes." |

## Routes

None.

## Tests

**Changed: `tests/Feature/Access/SeriesAccessCodeTest.php` — 2 new cases**

1. `test_the_code_email_names_the_series_and_who_shared_it`
2. `test_a_code_sent_without_a_series_stays_plain`

## Acceptance

- [x] A code asked for from a Series page names the Series and who shared it
- [x] A code sent without a Series stays plain
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

The e2e journeys find the code by "code" in the subject, which both subjects
carry.
