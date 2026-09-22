---
id: T-178
title: A Peer agrees to the terms and chooses emails
stream: onboarding
status: done
owner: claude
estimate: M
depends: none
blocks: T-179
---

# T-178 — A Peer agrees to the terms and chooses emails

## Why

A Peer could only get a Series by ticking "I agree that :creator can email me
about this :series": consent to the creator's emails was the price of access,
free or paid (§9, `ConsentTest::test_refusing_consent_refuses_the_access`),
and Continue stayed greyed out until it was ticked, with no reason given
(`fixups.md`). The owner, 22 September 2026, asked whether that must stay:
creators should show their own terms for what they sell, and "for now please
draft a static and use as Qori supplied agreement" (`D-049`). Afterwards a
Peer agrees to the terms for the Series, and says yes or no to emails.

## Decisions taken to make this specifiable

- **The terms are required on every way a Peer lets themselves in** — the
  stranger's form, the signed-in free button, checkout — and checked on the
  server, checkout included (`StartCheckoutRequest`), where a box that only
  gated a button in the browser was no agreement anybody could show.
- **The terms are Qori's static agreement**, `App\Support\PeerTerms` with its
  words in `lang/en/terms.php`, shown on the page under "Read the terms" in the
  Group's own nouns, and versioned (`PeerTerms::VERSION`). They are a draft
  until a legal read before release (release checklist). A creator's own terms
  are `T-179`.
- **The email box stays, optional and unticked**, marked "Optional — you get
  in either way". A Peer who leaves it gets in and is not a campaign
  recipient; a purchase records consent only when it was ticked before paying.
- **The Access records the terms**: `terms_version` and `terms_accepted_at`,
  from an `AccessAgreement` carried from where the boxes were ticked — the same
  request, `SeriesAccessPending` across the code, the checkout session's
  metadata to the webhook. A session from before the agreement travelled
  records no terms and no consent, the safe way round. An Access a creator
  gives by hand carries no terms.
- **The button is not greyed out**: pressing on without the terms answers with
  "Agree to the terms to carry on." under the box.

## Preconditions

None.

**Data this task verifies against:** a clean database for the tests; the
design-review world's "Reading a Room Before You Speak" for the walk.

**Equipment:** a browser.

## Scope

**In:**

- The terms box and the terms on the public Series page; the optional email
  box; the agreement carried to the Access; the terms recorded on it.

**Out:**

- A creator's own terms, or a template per Series (`T-179`).
- The creator's "I have permission to email this person" on Give access, which
  is their assertion and unchanged.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Support/PeerTerms.php` | new | the static terms, versioned; the page's props |
| `lang/en/terms.php` | new | the words, a draft |
| `app/Data/AccessAgreement.php` | new | the terms' version and time, and the email choice |
| `database/migrations/2026_09_22_000100_add_terms_to_accesses.php` | new | `terms_version`, `terms_accepted_at` |
| `app/Models/Access.php` | edit | the two columns |
| `app/Services/AccessService.php` | edit | `selfGrant(…, AccessAgreement)`; `grant()` writes the terms |
| `app/Services/CheckoutService.php` | edit | `begin(…, AccessAgreement)`; `fulfil()` reads it back |
| `app/Integrations/Contracts/SellsSeries.php` | edit | `checkoutFor(…, AccessAgreement)` |
| `app/Integrations/Stripe/Connect.php` | edit | the metadata |
| `app/Support/SeriesAccessPending.php` | edit | remembers the agreement across the code |
| `app/Http/Requests/StartSeriesAccessRequest.php` | edit | terms required, consent optional |
| `app/Http/Requests/GrantInSeriesRequest.php` | edit | the same |
| `app/Http/Requests/StartCheckoutRequest.php` | new | the same, for checkout |
| `app/Http/Controllers/SeriesAccessController.php` | edit | carries the agreement |
| `app/Http/Controllers/PublicAccessController.php` | edit | the same |
| `app/Http/Controllers/CheckoutController.php` | edit | the same |
| `app/Http/Controllers/PublicSeriesController.php` | edit | `terms`, `consentOptional` |
| `resources/js/components/series/PeerTermsBox.vue` | new | the box and the terms |
| `resources/js/pages/public/Series.vue` | edit | both forms |
| `lang/en/accesses.php` | edit | `consent.optional` |
| `docs/flows/accesses.md` | edit | terms and consent at access |
| `docs/flows/checkout.md` | edit | the agreement through checkout |
| `docs/flows/campaigns.md` | edit | who is a recipient |
| `tests/Feature/Access/ConsentTest.php` | edit | the rule, rewritten |
| `tests/Feature/Access/SeriesAccessContinueTest.php` | edit | terms required; leaving the email box |
| `tests/Feature/Access/SeriesAccessCodeTest.php` | edit | posts the terms |
| `tests/Feature/Auth/StaleDestinationTest.php` | edit | posts the terms |
| `tests/Feature/PublicSeriesTest.php` | edit | posts the terms |
| `tests/Feature/Checkout/CheckoutTest.php` | edit | `begin()` takes the agreement |
| `tests/Feature/Checkout/BuyButtonTest.php` | edit | posts the terms |
| `tests/Feature/Checkout/ConfirmingTest.php` | edit | posts the terms |
| `tests/e2e/public-link.spec.ts` | edit | ticks the terms |
| `tests/e2e/first-share.spec.ts` | edit | ticks the terms |

## Added during execution

- `tests/Feature/Series/StatementDescriptorTest.php` — two of its tests call
  `Connect::checkoutFor()` directly, and the Files table missed them; the first
  full gate failed on both. They pass an agreement now.

## Database

| Table | Column | Type | Null | Default | Index / constraint |
| --- | --- | --- | --- | --- | --- |
| `accesses` | `terms_version` | `varchar(255)` | yes | null | none |
| `accesses` | `terms_accepted_at` | `timestamp` | yes | null | none |

Migration: `database/migrations/2026_09_22_000100_add_terms_to_accesses.php`

## Code

```php
class AccessAgreement { public function __construct(public ?string $termsVersion, public ?CarbonImmutable $agreedAt, public bool $emailConsent) {} public static function agreedNow(bool $emailConsent): self; }
class PeerTerms { public const VERSION = 'qori-2026-09-22'; public static function props(?Group $group): array; }
// AccessService::selfGrant(Series, User, AccessAgreement); CheckoutService::begin(…, AccessAgreement)
// SellsSeries::checkoutFor(…, AccessAgreement) → metadata terms_version, terms_agreed_at, email_consent
```

## Copy

| Key | File | English |
| --- | --- | --- |
| `peer.agree` | `lang/en/terms.php` | "I agree to the terms for this :series." |
| `peer.read` | `lang/en/terms.php` | "Read the terms" |
| `peer.required` | `lang/en/terms.php` | "Agree to the terms to carry on." |
| `peer.title`, `peer.intro`, `peer.sections.*` | `lang/en/terms.php` | Qori's terms: what you get, paying, using what you get, ending your access, what the creator sees, Qori's part |
| `consent.optional` | `lang/en/accesses.php` | "Optional — you get in either way." |

## Routes

None.

## Tests

**Changed: `tests/Feature/Access/ConsentTest.php`** — `test_refusing_consent_refuses_the_access`
and `test_a_paying_peer_consents_through_the_purchase` replaced by:

1. `test_leaving_the_email_box_still_grants_and_records_no_consent`
2. `test_refusing_the_terms_refuses_the_access`
3. `test_the_access_records_the_terms_agreed`
4. `test_a_paying_peer_consents_only_when_they_ticked_the_box`
5. `test_a_purchase_without_the_agreement_records_no_consent`

**Changed: `tests/Feature/Access/SeriesAccessContinueTest.php`** —
`test_the_terms_are_required_on_the_first_form` (was consent),
`test_leaving_the_email_box_still_gets_the_series` new.

**New in `tests/Feature/Checkout/CheckoutTest.php`:**
`test_the_agreement_travels_with_the_checkout` — the terms' version, the time
and the email choice reach Stripe's metadata, which is all the webhook has.

Every other file above posts the terms, or passes an agreement to `begin()` or
`checkoutFor()`.

## Acceptance

- [x] Every way a Peer lets themselves in requires the terms, shown on the page, and checks them on the server
- [x] The email box is optional; leaving it gets the Series and no campaign
- [x] The Access records which terms, and when; a purchase carries both choices to the webhook
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

The terms' words are the product's draft; the release checklist carries the
legal read, beside `T-155`'s terms and privacy policy.
