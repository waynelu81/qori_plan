---
id: T-016
title: Read the mail Qori sends, before a provider ever does
stream: delivery
status: done
owner: claude
estimate: M
depends: none
blocks: T-032, T-055
---

# T-016 — Read the mail Qori sends, before a provider ever does

## Why

**Nobody has ever read a Qori email.** `MAIL_MAILER=log` locally and `array` in
tests, so every message this application has produced has gone to a log file or
into a fake. `qori:magic-link` exists only because there was no inbox to fetch a
link out of.

The test suite does not close that gap and cannot. Eleven test files fake mail
and there are **seventeen send assertions, none of which renders a template**.
They assert that a notification was dispatched to the right address with the
right data, and stop there. A body that renders a lang key as a literal, drops a
placeholder, or points at a dead URL passes every one of them.

That is not hypothetical. `T-002` shipped `$resolution ??= __(...)` returning the
literal string `errors.pages.500.resolution` onto a page, and the terminology
work had to add a test that walks every lang line because an article in front of
a noun placeholder is invisible until somebody reads the sentence. Mail is the
one surface in this product where nobody reads the sentence.

This task builds the inbox and the reader. Verifying the same messages through
the real provider is `T-032`, which is blocked on the owner; this is not, and it
is the half that makes that one cheap.

## Decisions taken to make this specifiable

**Mailpit, not MailHog.** Chosen by the owner on 10 September 2026. MailHog's
last release was 2020 and it is effectively unmaintained. Mailpit is active and
carries the three things this task needs: a REST API to read messages back, an
HTML compatibility check against caniemail data, and a link checker. The ports
are the same, 1025 and 8025, so it is close to a drop-in.

The HTML check earns its place specifically: `decisions.md` chose MJML for the
EDM builder because it "compiles to table-based HTML that survives Outlook", and
that claim has never been tested against anything.

**In `compose.yaml`, beside Postgres.** Not a container living outside the
project. The comment at the top of that file already explains why, about a Mongo
service that collided with another project's port and had local development
talking to the wrong database for weeks: "is it mine?" has to be answerable.

**The PHPUnit suite does not touch it.** `.env.testing` keeps `MAIL_MAILER=array`
and that is not negotiable. A suite that needs a container running is a suite
that fails on a clean clone, and 537 tests must not open sockets. What _is_
tested in PHPUnit is the checking logic, against strings, with no container in
sight — see **Tests**.

**Six messages, not seven.** The draft this replaces listed registration,
password reset, magic link, email change, verification, Series access and
receipt. Two of those are wrong. There is no registration mail — verification
_is_ the message a new account receives. And **Qori sends no receipt at all**:
there is no Mailable, no notification and no lang file for one, although
`Peer::acceptsCampaigns()` and `EmailSuppression` both have docblocks referring
to "the receipt-and-access email" as though one existed. Recorded under **Found**
rather than fixed here.

Campaign mail is out for the same reason it is out of `T-015`: broadcast is SES
and a separate decision (§9).

## Preconditions

Docker, and `docker compose up -d`. Nothing from the owner.

## Scope

**In:**

- A `mailpit` service in `compose.yaml`, and the local mailer pointed at it.
- A client for Mailpit's REST API.
- `qori:mail:check`, which sends all six messages, reads them back and reports.
- Two content checks that this project's bug history justifies: a lang key
  rendered as a literal, and an unreplaced `:placeholder`.
- A tinker recipe and a runbook entry.

**Out:**

- Anything against a real provider. That is `T-032` and it is blocked on the
  owner. Nothing here proves deliverability, SPF, DKIM or inbox placement.
- Bounce and complaint handling. Those arrive by webhook, not over SMTP, so
  Mailpit cannot produce one. `T-017`.
- Campaign and broadcast mail. SES, §9.
- Changing `.env`, which is gitignored and holds live credentials. `.env.example`
  is the file this task touches.
- Writing the missing receipt. See **Found**.
- Mailpit's spam analysis, which needs an external SpamAssassin or Rspamd and is
  a second service for a question `T-032` answers better with a real provider.

## Files

| Path                                        | Change | Notes                                     |
| ------------------------------------------- | ------ | ----------------------------------------- |
| `compose.yaml`                              | edit   | The `mailpit` service                     |
| `.env.example`                              | edit   | `MAIL_MAILER=smtp`, host, port            |
| `config/qori.php`                           | edit   | `mail.mailpit_url`                        |
| `app/Support/Mailpit.php`                   | new    | The API client                            |
| `app/Support/MailContent.php`               | new    | The two content checks, as pure functions |
| `app/Console/Commands/MailCheckCommand.php` | new    | `qori:mail:check`                         |
| `docs/tinker/mail.md`                       | new    | The recipe                                |
| `docs/tinker/README.md`                     | edit   | One row in the table                      |
| `docs/planning/engineering-runbook.md`      | edit   | Setup, and the port note                  |
| `tests/Feature/Mail/MailContentTest.php`    | new    | 8 cases, no container                     |

## Database

None.

## Code

```yaml
# compose.yaml
mailpit:
    image: axllent/mailpit
    container_name: qori-mailpit
    restart: unless-stopped
    ports:
        - '1025:1025' # SMTP, which .env.example already points at
        - '8025:8025' # Web UI and REST API
    environment:
        MP_MAX_MESSAGES: 500
        MP_SMTP_AUTH_ACCEPT_ANY: 1
        MP_SMTP_AUTH_ALLOW_INSECURE: 1
```

```php
namespace App\Support;

/**
 * Reading the local inbox back.
 *
 * Only ever talks to Mailpit, which is a development service — so it is Support
 * rather than an Integration: there is no vendor contract here and nothing in
 * production may depend on it.
 */
class Mailpit
{
    public function isReachable(): bool;

    public function clear(): void;                        // DELETE /api/v1/messages

    /** @return list<array<string, mixed>> */
    public function messages(): array;                    // GET  /api/v1/messages

    /** @return array<string, mixed> */
    public function message(string $id): array;           // GET  /api/v1/message/{id}

    /** Polls until $count have arrived, or gives up. */
    public function waitFor(int $count, int $seconds = 10): bool;
}
```

**Confirm the response shape against the running container before writing
against it.** The endpoints above are stable and the field names are not
something this spec should be trusted on: they were written from memory rather
than from the code, and Mailpit capitalises its JSON keys in a way that is easy
to get subtly wrong. Read one message from `/api/v1/messages` first. If the
shape differs from what a reasonable reading of this section suggests, that is a
note in the report, not a re-scope.

```php
namespace App\Support;

class MailContent
{
    /**
     * Translation keys that reached the reader as literals.
     *
     * The exact bug T-002 shipped: `$resolution ??= __(...)` put
     * "errors.pages.500.resolution" on a page. A dotted lowercase token that
     * Lang::has() recognises is that bug and essentially nothing else — real
     * prose does not contain a string the translator knows.
     *
     * @return list<string>
     */
    public static function leakedLangKeys(string $body): array;

    /**
     * Placeholders nothing filled in.
     *
     * ":minutes" or ":episode_plural" surviving into a sent body means a
     * replacement array missed a key, which renders as punctuation the reader
     * has to decode.
     *
     * @return list<string>
     */
    public static function unreplacedPlaceholders(string $body): array;
}
```

```php
// App\Console\Commands\MailCheckCommand
protected $signature = 'qori:mail:check {--keep : Leave the scratch rows and the inbox in place}';
```

Behaviour, in order:

1. Refuse loudly unless `config('mail.default')` is `smtp` and
   `Mailpit::isReachable()`. Name the fix in the message; a developer staring at
   an empty inbox because the mailer is still `log` is the failure this prevents.
2. Clear the inbox, so a run is deterministic for the same reason
   `DesignReviewSeeder` pins its ids and its clock.
3. Build scratch rows: one User, one Group, one Series, one Peer, with fixed
   ULIDs via the same `id()` helper shape `DesignReviewSeeder` uses. **I, L, O
   and U are not in the ULID alphabet** and a bad id is stored happily and then
   404s three layers away.
4. Send all six, each through the path the application actually uses rather than
   by constructing the notification directly. A message that a service never
   dispatches is a message this command should not claim to have verified.
5. `waitFor(6)`.
6. For each: print the subject, and fail on an empty subject, a leaked lang key,
   an unreplaced placeholder, or a body with no link where the flow needs one.
7. Delete the scratch rows unless `--keep`. Exit non-zero on any failure.

The six, and the path each is sent by:

| Message                          | Sent by                             |
| -------------------------------- | ----------------------------------- |
| `VerifyEmail`                    | Fortify registration                |
| `ResetPassword`                  | Fortify's forgot-password flow      |
| `MagicLinkLoginNotification`     | `MagicLinkLoginController`          |
| `ConfirmEmailChangeNotification` | `EmailChangeService::request()`     |
| `EmailChangedNotification`       | `EmailChangeService`, on confirm    |
| `SeriesAccessNotification`       | `AccessService`, on granting a Peer |

## Copy

None. Everything this command prints is aimed at a developer, which `CLAUDE.md`
exempts explicitly along with `Log::` and `devMessage`.

## Routes

None.

## Tests

The command needs a container and therefore cannot be in the suite. **What can
be, and is, is every judgement it makes** — the checks are pure functions over a
string, so they are testable with no Docker at all. That split is the point: the
logic is covered on a clean clone, and the container only ever supplies input.

**New: `tests/Feature/Mail/MailContentTest.php` — 8 cases**

1. `test_a_rendered_lang_key_is_caught` — a body containing
   `errors.pages.500.resolution`, the literal string `T-002` shipped.
2. `test_ordinary_prose_with_a_full_stop_is_not_a_lang_key` — "Check your inbox.
   Then sign in." must not trip it. The false-positive case, and the one that
   decides whether anybody keeps the check.
3. `test_a_dotted_token_that_no_lang_file_knows_is_ignored` — `useqori.test`
   and `nadia@example.test` appear in real bodies.
4. `test_an_unreplaced_placeholder_is_caught` — `:minutes`.
5. `test_a_time_is_not_a_placeholder` — "9:00am" and "1:1" must not trip it.
6. `test_a_url_with_a_port_is_not_a_placeholder` — `localhost:8025`, which
   appears in every link this command reads.
7. `test_a_clean_body_reports_nothing` — both checks, one real rendered body.
8. `test_every_notification_class_is_covered_by_the_command` — walks
   `app/Notifications`, and fails when a class exists that
   `MailCheckCommand` does not send. This is the case that stops the command
   rotting: a seventh message added next month is a failing test, not a silent
   gap. `CampaignNotification` is named as deliberately excluded, with §9 as the
   reason.

**Changed:** none expected.

## Acceptance

- [x] `docker compose up -d` gives a working local inbox on 1025 and 8025
- [x] `qori:mail:check` sends all six messages and reads them back
- [x] It refuses to run, loudly, when the mailer is still `log`
- [x] A rendered lang key and an unreplaced placeholder both fail the run
- [x] The PHPUnit suite still runs with no container, on `array`
- [x] A new notification class fails the suite until the command sends it
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

**Two messages named in the previous draft do not exist.** There is no
registration mail, and there is no receipt. The receipt is the interesting one:
two model docblocks describe "the receipt-and-access email" and
`EmailSuppression` reasons about preserving "their receipts", so the product's
own comments believe in a message nobody wrote. Money creates an obligation per
`PLAN.md`, and a purchase that produces no receipt is a gap with a product
decision inside it. It needs its own task and is not this one.

**Mailpit's chaos mode is the tool for `RecipientStatus::Failed`.** `T-023`'s
reachability test found that enum case has no producer, because nothing catches
a send failure. Mailpit can be told to reject a proportion of messages with a
chosen SMTP response, which is how that code would be written and proved. Out of
scope here and worth writing down, because it is not obvious that a development
mail sink is the right instrument for it.
