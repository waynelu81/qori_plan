---
id: T-116
title: Password managers can find where to create a passkey
stream: identity
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-116 — Password managers can find where to create a passkey

## Why

`GET /.well-known/passkey-endpoints` (`routes/settings.php:80-85`, named
`well-known.passkeys`) tells a password manager where a person creates and
manages a passkey for Qori. The W3C document it follows names those members
`enroll` and `manage`. Qori's says `grantl` and `manage`, so a password manager
finds the manage link and nothing for creating a passkey.

`git log -S grantl` finds one commit, `f74757a` ("Rename the domain all the way
through", 9 September 2026), whose search and replace turned "enrol" into
"grant" inside the word "enroll". No test requested the document, so nothing
failed. Observed on 17 September 2026 against the local server:
`curl http://localhost:8001/.well-known/passkey-endpoints` returned
`{"grantl":"http:\/\/localhost:8001\/u\/security","manage":"http:\/\/localhost:8001\/u\/security"}`.

Afterwards the document says `enroll` and `manage`, both pointing at the
security page, and a test holds its exact keys so the next bulk rename fails
the gate.

## Decisions taken to make this specifiable

**The member names come from the W3C document, not memory.** "A Well-Known URL
for Relying Party Passkey Endpoints", Editor's Draft of 14 January 2026
(`https://w3c.github.io/webappsec-passkey-endpoints/`), read on 17 September 2026. It defines three optional members: `enroll`, a direct URL to the passkey
creation page; `manage`, a direct URL to the passkey management page; and
`prfUsageDetails`. A response is `200 OK` with `application/json`, and must not
redirect.

**`enroll` and `manage` both stay `route('security.edit')`.** Passkeys are
created and removed on the one security page (`/u/security`), and Qori has no
URL that opens straight to creating one.

**No `prfUsageDetails`.** Qori does not use the WebAuthn PRF extension, and the
member is optional.

**The test asserts the exact document, keys and values.** A test that looked
for `enroll` alone would pass beside a stray `grantl`; `assertExactJson` fails
on either.

**The route stays where it is.** It is served without sign-in, because a
password manager reads it without the person's session, and moving it is not
what is broken.

## Preconditions

**Data this task verifies against:** a clean database.

**Equipment:** None. A request to the local server shows the document, and
the test is the proof.

## Scope

**In:**

- The `grantl` key in `routes/settings.php`, renamed `enroll`.
- One test requesting the document as a visitor who is not signed in.
- `docs/flows/auth.md`: one paragraph saying what the document is and where it
  points, and the route-namespace table's `/w/{group}/*` row, which has said
  `/g/{group}/*` in the code since the rename.

**Out:**

- Every other word the same rename mangled: `AccessService::guardGrantlable()`,
  which draft `T-094` names, "grantlable" and "Grantling" in comments and docs,
  and `accesses.consent`'s "Please agree to be peered before granting.", which
  a buyer reads. They are draft `T-118`.
- Serving the document only when `Features::passkeys()` is enabled.
- A page that opens straight to creating a passkey.

## Files

| Path                                              | Change | Notes                                          |
| ------------------------------------------------- | ------ | ---------------------------------------------- |
| `routes/settings.php`                             | edit   | `grantl` becomes `enroll`                      |
| `tests/Feature/Settings/PasskeyEndpointsTest.php` | new    | 1 case                                         |
| `docs/flows/auth.md`                              | edit   | The document's paragraph; the `/g/{group}` row |

## Database

None.

## Code

```php
// routes/settings.php
Route::get('.well-known/passkey-endpoints', function () {
    return response()->json([
        'enroll' => route('security.edit'),
        'manage' => route('security.edit'),
    ]);
})->name('well-known.passkeys');
```

The `@chisel-passkeys` markers around the route stay.

## Copy

None.

## Routes

None change. `GET /.well-known/passkey-endpoints`, `well-known.passkeys`, a
closure in `routes/settings.php`, answers with the corrected document.

## Tests

**New: `tests/Feature/Settings/PasskeyEndpointsTest.php` — 1 case**

1. `test_the_document_names_the_enroll_and_manage_pages` — a visitor who is not
   signed in requests `route('well-known.passkeys')`; the response is `200`,
   its `Content-Type` is `application/json`, and `assertExactJson` matches
   `['enroll' => route('security.edit'), 'manage' => route('security.edit')]`.
   **Fails today**: the document says `grantl`.

**Changed:** none.

## Acceptance

- [x] The passkey endpoints document names `enroll` and `manage`, both the security page
- [x] It answers a visitor who is not signed in with `200` and JSON, not a redirect
- [x] `docs/flows/auth.md` describes the document, and its namespace table says `/g/{group}/*`
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Specified on 17 September 2026 from a readiness check of small tasks, and
approved by the stream owner in the same session.

The Out list first said each leftover of the rename "is its own task"; none
had one, and it missed the "Grantling" forms. Corrected to draft `T-118` on
closing.
