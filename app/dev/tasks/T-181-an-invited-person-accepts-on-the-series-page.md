---
id: T-181
title: An invited person accepts on the Series page, free or at their price
stream: selling
status: ready
owner: unassigned
estimate: M
depends: T-043
blocks: none
---

# T-181 — An invited person accepts on the Series page, free or at their price

## Why

`T-043` sends an invitation whose link remembers it and lands on the Series
page. Nothing there knows about it yet: the stranger's form asks for any
address, the button sells at the Series' price, and a free invitation to a
priced Series cannot be taken at all, because `AccessService::selfGrant()`
refuses a priced Series. Afterwards the person who was invited gets in with
the address it was sent to, free or at the price the creator gave them, and
the creator sees it accepted (`D-050`).

## Decisions taken to make this specifiable

- **The Series page is where an invitation is accepted**, not a page of its
  own (`T-043`, `D-016`): the same code step, button and checkout, ending on
  `shared.show`.
- **The invited address is the only one that can accept it** (`D-050`). A guest
  sees it on the form, not in a box to type, with their name filled in from
  the invitation; the code goes to that address whatever the form posts. A
  person signed in with that address gets a button. A person signed in with
  another sees that the invitation is for someone else — the address masked —
  and the page otherwise as usual.
- **The price on the page is the invitation's.** Free (0, or a free Series):
  a right code or the button grants it, through `AccessService::
  acceptInvitation()`, source `invitation`, no price, the Peer cap applying as
  it does to any grant. Priced: checkout at that price — `CheckoutService::
  begin()` takes the invitation and refuses it unless it is waiting and for
  this person, `SellsSeries::checkoutFor()` charges its price and carries
  `metadata[invitation_id]`, and `fulfil()` grants at the amount paid.
- **The terms and the email box are the page's own** (`D-049`): required and
  optional, as on every other way in.
- **Accepted means an Access exists**: `accepted_at` and `access_id` on the
  invitation, written where the Access is — at once when free, by the webhook
  when paid. Someone who already has access is sent to it, and the invitation
  is marked accepted.
- **An expired or withdrawn invitation says so and changes nothing else**:
  "This invitation ended on :date. Ask :name for a new one." — and the page
  sells as usual. The session forgets an invitation once it is accepted.

## Preconditions

`T-043` done.

**Data this task verifies against:** a clean database for the tests; the
design-review world for the walk; the e2e run's own database for the journey.

**Equipment:** a browser, and Mailpit — read by message, never emptied.

## Scope

**In:**

- The invitation on the public Series page, in each state; the code step and
  the button using it; checkout at its price; the invitation marked accepted.
- A journey: a creator invites someone with no account, free, and they get in
  from the email with a code.

**Out:**

- The rest of `T-027`'s receiving journey — profile correction, a changed
  address, the time between payment and access.
- Anything on the creator's side, which is `T-043`'s.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Http/Controllers/PublicSeriesController.php` | edit | the `invitation` prop, in its state |
| `resources/js/pages/public/Series.vue` | edit | the invited form, the button, the notices |
| `resources/js/components/series/InvitationOffer.vue` | new | what the invitation offers, and the notices |
| `app/Http/Controllers/SeriesAccessController.php` | edit | the invited address on start; accepting on verify |
| `app/Http/Controllers/PublicInvitationController.php` | new | the signed-in button |
| `app/Http/Requests/AcceptInvitationRequest.php` | new | terms required, emails optional |
| `routes/web.php` | edit | the accept route |
| `app/Services/AccessService.php` | edit | `acceptInvitation()` |
| `app/Services/CheckoutService.php` | edit | `begin(…, ?Invitation)`; `fulfil()` marks it accepted |
| `app/Integrations/Contracts/SellsSeries.php` | edit | `checkoutFor(…, ?Invitation)` |
| `app/Integrations/Stripe/Connect.php` | edit | its price, and `metadata[invitation_id]` |
| `app/Models/Invitation.php` | edit | `markAccepted()`, `isFor()` |
| `app/Support/InvitationPending.php` | edit | `waitingFor(Series, User)` |
| `lang/en/invitations.php` | edit | the page's words |
| `lang/en/errors.php` | edit | ended, someone else's |
| `docs/flows/invitations.md` | edit | accepting |
| `docs/flows/checkout.md` | edit | an invitation's price |
| `docs/flows/accesses.md` | edit | source `invitation` |
| `docs/tinker/invitations.md` | edit | accepting by hand |
| `tests/Feature/Invitations/AcceptInvitationTest.php` | new | |
| `tests/Feature/Checkout/CheckoutTest.php` | edit | the invitation's price and metadata |
| `tests/e2e/invitation.spec.ts` | new | the journey |

## Database

None: `T-043`'s `accepted_at` and `access_id`.

## Code

```php
// AccessService::acceptInvitation(Invitation $invitation, User $user, AccessAgreement $agreement): Access
// CheckoutService::begin(Series, User, string, string, AccessAgreement, ?Invitation $invitation = null): HostedCheckout
// SellsSeries::checkoutFor(Series, Group, User, string, string, AccessAgreement, ?Invitation $invitation = null): HostedCheckout
// Invitation::markAccepted(Access $access): void; Invitation::isFor(User $user): bool
// InvitationPending::waitingFor(Series $series, User $user): ?Invitation
```

## Copy

| Key | File | English |
| --- | --- | --- |
| `public.offer` | `lang/en/invitations.php` | ":name invited you." |
| `public.price` | `lang/en/invitations.php` | "Your price: :price" |
| `public.free` | `lang/en/invitations.php` | "Free for you" |
| `public.for_address` | `lang/en/invitations.php` | "This invitation is for :email." |
| `public.someone_else` | `lang/en/invitations.php` | "This invitation is for :email. You're signed in with another address." |
| `public.ended` | `lang/en/invitations.php` | "This invitation ended on :date. Ask :name for a new one." |
| `public.accepted` | `lang/en/invitations.php` | "You accepted this invitation." |
| `public.accept` | `lang/en/invitations.php` | "Accept" |
| `invitations.someone_else` | `lang/en/errors.php` | "This invitation is for another address." / "Sign in with the address it was sent to." |
| `invitations.ended` | `lang/en/errors.php` | "This invitation has ended." / "Ask the person who sent it for a new one." |

## Routes

| Method | Path | Name | Controller |
| --- | --- | --- | --- |
| POST | `s/{seriesId}/invitation/accept` | `series.invitation.accept` | `PublicInvitationController@accept` |

Signed in and verified, like `series.grant`.

## Tests

**`tests/Feature/Invitations/AcceptInvitationTest.php`:**

1. `test_a_guest_gets_in_free_with_the_code_sent_to_the_invited_address`
2. `test_the_code_goes_to_the_invited_address_whatever_the_form_posts`
3. `test_a_free_invitation_to_a_priced_series_is_granted_without_checkout`
4. `test_a_priced_invitation_goes_to_checkout_at_its_price`
5. `test_a_signed_in_invitee_accepts_with_the_button`
6. `test_someone_signed_in_with_another_address_cannot_accept`
7. `test_an_ended_invitation_says_so_and_the_page_sells_as_usual`
8. `test_accepting_records_the_access_on_the_invitation`
9. `test_the_terms_are_required_and_the_emails_stay_optional`
10. `test_a_paid_invitation_is_accepted_when_the_payment_lands`

**Changed: `tests/Feature/Checkout/CheckoutTest.php`** —
`test_an_invitation_sets_the_price_and_travels_in_the_metadata`.

**New journey: `tests/e2e/invitation.spec.ts`** — a creator invites an address
with no account, free; the email's link lands on the Series; the name is
filled, the terms ticked, the code read from the inbox and typed; the Series
opens.

## Acceptance

- [ ] The invited person gets in with the invited address only — by the code as a guest, by the button signed in
- [ ] Free is granted; a price goes to checkout at that price; either way the invitation shows accepted
- [ ] An ended invitation, or one for someone else, says so and changes nothing else
- [ ] The journey passes in `php artisan qori:e2e`
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Cut from `T-043` on 22 September 2026, when the owner's answers (`D-050`)
brought it to ready.
