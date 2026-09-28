---
id: T-213
title: An admin reads a note where Stripe's Disconnect would be
stream: selling
status: draft
owner: unassigned
estimate: S
depends: none
blocks: none
---

# T-213 — An admin reads a note where Stripe's Disconnect would be

## Why

On Integrations, Stripe's Disconnect shows whenever the Group holds an account,
to anybody who can open the page (`resources/js/pages/share/settings/Integrations.vue`,
`<Dialog v-if="disconnect">`; `IntegrationsController` builds the `disconnect`
prop for owner and admin alike). Letting go is the owner's (§15,
`PaymentsController::guardOwner()`), so an admin who opens the dialog and
confirms is sent back with "Only the owner can change how payments are taken."

Every other write on the page is shown to the owner alone, with a note in its
place, said before the click rather than as the refusal after it:

- Connect Stripe (`PaymentDoors`): an admin reads `payments.owner_only_note`,
  "Connecting payments is the owner's to do.", whose lang comment says why —
  "Said before the click rather than as the refusal after it (§15)".
- Each storage section's Connect, Reconnect and Disconnect (`ProviderSection`,
  `<template v-if="isOwner">`), where an admin reads the section's owner note;
  `errors.connections.owner_only`'s comment gives the rule: "an admin reads a
  note where the button would be".

Stripe's Disconnect, built by `T-064`, is the one that did not inherit it.
Found on 28 September 2026 by `T-153`, whose case asserts the refusal an admin
meets today.

Afterwards an admin reads a note where the button would be, and only the owner
is offered Disconnect.

## Decisions taken to make this specifiable

None yet.

## Preconditions

None.

**Data this task verifies against:** a Group holding a Stripe account, with an
admin.

**Equipment:** a browser, as the owner and as the admin.

## Scope

**In:**

- Stripe's Disconnect shown to the owner alone, and a note in its place for an
  admin.

**Out:**

- The refusal itself, which stays for a request that reaches it anyway
  (`T-153`'s case).

## Files

| Path                                                    | Change | Notes                                        |
| ------------------------------------------------------- | ------ | -------------------------------------------- |
| `app/Http/Controllers/Share/IntegrationsController.php` | edit   | `disconnect.ownerNote`                       |
| `resources/js/pages/share/settings/Integrations.vue`    | edit   | the dialog for the owner, the note otherwise |
| `lang/en/payments.php`                                  | edit   | `disconnect_owner_note`                      |
| `tests/Feature/Share/PaymentsDisconnectTest.php`        | edit   | the prop carries the note                    |

Flows: `docs/flows/billing.md`, "Disconnecting".

## Database

None.

## Code

As the other two: the server sends the note to both, and the page picks by
`isOwner`.

## Copy

| Key                              | File                   | Text                                       |
| -------------------------------- | ---------------------- | ------------------------------------------ |
| `payments.disconnect_owner_note` | `lang/en/payments.php` | Disconnecting Stripe is the owner's to do. |

## Routes

None.

## Tests

To be settled when ready: the `disconnect` prop carries the note; the page is
checked in a browser as each, there being no JavaScript test runner.

## Acceptance

- [ ] An admin reads a note where Stripe's Disconnect would be, and the owner is offered Disconnect as before
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- **Hide it from an admin, with the note, as the rest of the page does?** It
  changes what an admin sees, so it is the owner's (asked 28 September 2026).
  The words follow `payments.owner_only_note`.

## Re-scope log

None.

## Notes

None.
