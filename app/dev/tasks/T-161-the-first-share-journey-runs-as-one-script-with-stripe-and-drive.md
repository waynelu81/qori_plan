---
id: T-161
title: The first-share journey runs as one script, with Stripe and Drive
stream: onboarding
status: blocked
owner: claude
estimate: M
depends: T-159, T-160
blocks: none
---

# T-161 — The first-share journey runs as one script, with Stripe and Drive

## Why

[The first-share journey](../journeys/first-share.md) is the product's core,
and connecting Stripe and Google Drive during setup is its point (owner,
21 September 2026). It should run as one e2e script, every step, so a change
that breaks it is caught the day it lands. Where a person has to sign in to a
vendor or type a card, the script is **hardcoded** — the owner's word for it:
"Even if it needs to be hardcoded for end to end testing."

## Blocked on

What: the owner's `.env.e2e` — Stripe OAuth turned on with the redirect URI
and `STRIPE_CLIENT_ID` in `.env`, Google Drive's redirect URI, then steps 5, 6
and 9 walked once in local Qori and `php artisan qori:e2e:capture you@…
--peer=…` — and one walk of the journey by hand with a test card. Everything
that can be built and tested without them is built, committed and green
(code `25da989`); the journey is skipped until the file exists.

Who: wayne. `docs/tinker/e2e-first-share.md` in the code repository lists
every console step and what an agent may read there for you. When the file
exists, run `php artisan qori:e2e --only=first-share --headed`; whoever sees it
pass ticks the two open product boxes and closes the task.

## Decisions taken to make this specifiable

**The owner's real values live in a gitignored `.env.e2e`, or in `.env`**
(`D-045`). The owner, 21 September 2026: "please read from .env or maybe a
designated gitignore file." Loaded after `.env`, before config, only in a
local environment and only for `qori:e2e` and `qori:e2e:connect`.

**No file and no key, skipped and green; a file, and it must run.** Skipping
on a vendor refusal would hide a Qori regression, so once the file exists a
missing key or a refused value fails the run with the key and the fix.

**Stripe's sign-in and Google's consent are adopted, through the real
Services.** `PaymentsService::adopt()` writes the account where the landing
does and reads it back from Stripe; `ConnectionService::adopt()` renews the
refresh token at Google, reads the account, and writes the row a real connect
writes. Both are reached only from `qori:e2e:connect`, which refuses anything
but a local run database.

**The Picker is replaced by posting the Episode form with the picked file.**
Its button is never pressed: the answer is the creator's live Drive token, and
a Playwright trace kept on failure would keep it.

**The card is replaced by a signed `checkout.session.completed`** built from
the real session read back from Stripe (`T-121`'s second option), posted by
`qori:e2e:checkout-paid` with a webhook secret `qori:e2e` mints per run.

**Neither vendor's page is loaded.** Stripe's Checkout and Drive are stood in
for in the browser; the run checks where Qori sent the Peer.

**Mailpit is read, never emptied.** Its 1025/8025 may be another project's.
The fixed Peer address reads only messages whose ids were not there before the
step that sent them — no clock is compared.

**Node never holds a secret.** Playwright's environment is stripped of every
inherited name holding `SECRET`, `TOKEN`, `PASSWORD`, `_KEY` or `_DSN`, or
ending in `_URL`; the PHP seams load theirs again from the files.

**The shell is not a source.** The seams read only `.env` and `.env.e2e`, so a
journey key, or a secret `.env` also holds, exported in the shell with a
different value is refused by name rather than half-used.

## Preconditions

**Data this task verifies against:** the run's own database, rebuilt by
`qori:e2e`; for the capture command, the development database after the
owner's walk.

**Equipment:** Docker (Postgres, a Mailpit on 1025/8025), Chromium through
Playwright, and for the journey itself the owner's `.env.e2e`
(`docs/tinker/e2e-first-share.md`).

## Scope

**In:**

- `.env.e2e`: the ignore line, the loader, the config keys, `.env.example`.
- `qori:e2e`: skip or fail by the rule above, the per-run webhook secret,
  stripped secrets, Mailpit no longer emptied.
- `qori:e2e:capture`, `qori:e2e:connect`, `qori:e2e:checkout-paid`.
- `tests/e2e/first-share.spec.ts`, the helpers it shares with the others.
- The owner's guide and the docs that describe the run.

**Out:**

- `qori:mail:check` still empties the inbox → `T-162`.
- Driving Stripe's own Checkout page with the test card: the owner walks it by
  hand once (the last box) → what is left of `T-121`.
- A Peer whose Google account is not their Qori email → `T-092`.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `.gitignore` | edit | `.env.e2e`, `.env.e2e.*` |
| `.env.example` | edit | the seven keys, empty |
| `config/qori.php` | edit | `e2e.first_share` |
| `bootstrap/app.php` | edit | loads `.env.e2e` in local only |
| `app/Providers/AppServiceProvider.php` | edit | `singletonIf` for the credentials |
| `app/Support/EndToEndCredentials.php` | new | load, check, read, write |
| `app/Concerns/GuardsEndToEndRuns.php` | new | the refusals every `qori:e2e*` shares |
| `app/Console/Commands/EndToEndCommand.php` | edit | skip/fail, secrets, Mailpit |
| `app/Console/Commands/EndToEndCaptureCommand.php` | new | `qori:e2e:capture` |
| `app/Console/Commands/EndToEndConnectCommand.php` | new | `qori:e2e:connect` |
| `app/Console/Commands/EndToEndCheckoutPaidCommand.php` | new | `qori:e2e:checkout-paid` |
| `app/Integrations/Stripe/Webhooks.php` | new | session read back, envelope, signature |
| `app/Data/WebhookDelivery.php` | new | body and headers, as sent |
| `app/Integrations/Google/GoogleAccounts.php` | edit | `#[SensitiveParameter]` on `refresh()` |
| `app/Services/PaymentsService.php` | edit | `adopt()` |
| `app/Services/ConnectionService.php` | edit | `adopt()` |
| `tests/e2e/first-share.spec.ts` | new | the journey |
| `tests/e2e/support/creator.ts` | edit | split into reusable steps |
| `tests/e2e/support/mailpit.ts` | edit | `inboxOf()`, `after` |
| `tests/e2e/support/seams.ts` | new | `artisan()` |
| `docs/tinker/e2e-first-share.md` | new | the owner's guide |
| `docs/tinker/e2e.md` | edit | Mailpit, environment, journeys |
| `docs/tinker/README.md` | edit | the guide's row |
| `docs/architecture/stack.md` | edit | Environment files |
| `docs/flows/checkout.md` | edit | the run's two stand-ins |
| `docs/flows/storage.md` | edit | Drive adopted in the run |

## Database

None.

## Code

As built; `docs/flows/checkout.md` and `docs/flows/storage.md` name the call
chains, `docs/tinker/e2e-first-share.md` the keys and commands.

## Copy

None. Every line the commands print is developer console output.

## Routes

None.

## Tests

**New: `tests/Feature/Support/EndToEndCredentialsTest.php` — 11 cases**

1. `test_it_loads_only_its_own_filled_keys`
2. `test_it_replaces_a_value_loaded_earlier_and_never_a_shell_export`
3. `test_a_file_git_does_not_ignore_is_not_read`
4. `test_a_file_that_cannot_be_parsed_is_refused_without_quoting_it`
5. `test_the_real_file_name_is_ignored_by_git_here_and_nowhere_git_does_not_know`
6. `test_it_is_wanted_only_when_the_file_or_a_key_exists`
7. `test_problems_name_every_empty_key_and_no_value`
8. `test_a_complete_set_has_no_problems_and_each_bad_value_has_one`
9. `test_it_writes_every_key_owner_only_and_reads_them_back`
10. `test_it_refuses_to_write_a_value_it_cannot_quote`
11. `test_a_journey_key_exported_in_the_shell_is_refused_by_name`

**New: `tests/Feature/Console/EndToEndCaptureCommandTest.php` — 5 cases**

1. `test_it_writes_every_value_and_never_shows_the_token`
2. `test_what_it_cannot_find_keeps_what_the_file_had`
3. `test_the_peer_cannot_be_the_creator_and_nothing_is_written`
4. `test_it_refuses_a_file_git_would_commit`
5. `test_it_refuses_a_run_database_a_live_key_and_another_environment`

**New: `tests/Feature/Console/EndToEndConnectCommandTest.php` — 4 cases**

1. `test_it_connects_both_and_prints_no_token`
2. `test_a_token_google_will_not_renew_fails_and_writes_nothing`
3. `test_an_account_that_cannot_charge_fails`
4. `test_it_refuses_anything_but_a_local_run_database`

**New: `tests/Feature/Console/EndToEndCheckoutPaidCommandTest.php` — 3 cases**

1. `test_a_real_session_read_back_and_signed_grants_access` — through the real webhook controller
2. `test_a_signature_the_server_does_not_accept_fails`
3. `test_it_refuses_a_secret_it_did_not_mint_and_an_origin_off_this_machine`

23 new. **Changed:** none; `EndToEndCommandTest`'s inbox refusal still names
`docker compose up -d mailpit`.

## Acceptance

- [x] Without `.env.e2e` and its keys, `php artisan qori:e2e` skips the journey with the reason and passes
- [x] A `.env.e2e` missing a key fails the run, naming the key and never a value
- [x] The other three journeys pass with Mailpit no longer emptied
- [x] PHPUnit never reads `.env.e2e`, and every vendor stays faked
- [ ] With the owner's `.env.e2e`, `php artisan qori:e2e --only=first-share` passes end to end
- [ ] The owner walks the journey once by hand for real — two sign-ins and a test card — recorded in `walkthroughs.md`; it is also `T-159`'s first real run of the Picker
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

- 21 September 2026: the owner answered the draft's first question — the
  values may come from `.env` or a designated gitignored file. Which Google
  account plays the Peer is theirs to put in `QORI_E2E_PEER_GOOGLE_EMAIL`.
- The design was reviewed adversarially before building. Its fixes are in:
  skip only when nothing was set up; `.env.example` carries the keys;
  Mailpit read by message ids, not time; the seams refuse outside a local run
  database; the signer posts the exact bytes it signed.
- The build was reviewed the same way (three lenses, each finding checked by
  a refuter): 9 confirmed, all minor, all fixed before the commit — the shell
  precedence above, the temporary file born `0600` rather than chmodded, `_URL`
  names stripped and `DB_URL` refused, the Picker's token request blocked
  rather than watched, a broken file failing whatever `--only` says, the
  command found past a leading `-v`, and the gitignore test pointed at the
  root rule. The lens that walked the spec against the real pages found no
  step that fails.
- The owner, on the loader hook: "Pretty sure can detect environment is
  production and skip." It runs only when `APP_ENV` is `local`.
