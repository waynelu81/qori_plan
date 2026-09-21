---
id: T-164
title: The creator is told exactly what Stripe needs before it takes payments
stream: selling
status: done
owner: claude
estimate: M
depends: none
blocks: T-166
---

# T-164 — The creator is told exactly what Stripe needs before it takes payments

## Why

A connected Stripe account that cannot charge told the creator almost nothing.
Integrations had two states for it: `incomplete` ("Finish setting up in your
Stripe dashboard") and `pending` ("Stripe is still checking your details.
Nothing to do"). The owner met the second beside an account that was missing
an identity document on 21 September 2026, and asked what to set in Stripe; the
answer took a Stripe API read. Nothing else in the product said anything: the
dashboard and the price field only knew whether an account id existed.

The owner, 22 September 2026: "If the stripe is not able to collect payment we
must let the creator know to check their stripe setting, the help or prompt
need to be detail so they can go there and enable exactly the setting." And,
on what a Peer meets meanwhile: "We just notify and advice … that's for the
creator to deal with."

Afterwards Integrations lists, for an account that cannot charge, each thing
Stripe asked for under the page in the creator's own Stripe dashboard where it
is done, with a link there; connecting such an account says where that list
is; and the dashboard and the price field say payments are held back.

## Decisions taken to make this specifiable

- **The card_payments capability's requirements are the list, not the
  account's.** Observed on 22 September 2026: an unfinished account listed
  `external_account` among sixteen past-due fields, and its card_payments
  capability listed the same fields without it — a bank account is for
  payouts. The account's list stands in only when the capability read fails,
  gets no answer, or finds card payments never requested (it has no list of
  its own then).
- **One step per page in the creator's Stripe dashboard**, at the addresses
  Stripe documented on 22 September 2026: the "Verify your business" form
  (`/account/onboarding`) for an account that never finished sign-up and for
  the terms; Home (`/dashboard`), which Stripe says surfaces identity
  verifications, for a document it asked for, a question of its own
  (`interv_…`) and anything unmapped; Settings → Business → Business details
  for personal, business and public details and the statement descriptor;
  Settings → Business → Bank accounts and currencies; Settings → Payments →
  Payment methods for card payments never requested; and Stripe support for a
  refusal. Each step lists what Stripe asked for in plain words.
- **"Nothing to do" is said only while Stripe is checking** — something in
  `pending_verification`, a pending capability, or a review — and nothing is
  due.
- **The readiness is remembered on the Group, and read from there where a
  Stripe call does not belong.** `groups.payments_readiness` is written by
  every account read when it moves and cleared with the account. The dashboard
  and the price field read it; Integrations reads Stripe on every visit. Null
  means never read and is never a warning.
- **The steps are the owner's.** An admin reads them without the links and
  without Stripe's own words about a rejected document, which can quote the
  owner's name or address back.
- **The dashboard speaks only when there is something to do and something on
  sale**: a priced Series, and a readiness that asks the creator (not
  `checking`). It outranks the next steps below it, after paused, over-cap and
  a failing plan payment.
- **Nothing changes for the Peer** (owner, 22 September 2026). In test mode
  Stripe creates a Checkout Session even for an account that cannot charge
  (observed 22 September 2026), so the Peer reaches Stripe's page.
- **Reading Stripe's account payload moves to the Stripe folder** (CLAUDE.md,
  `T-114`'s list), because it grew: `ConnectAccount::fromStripe()` became
  `ConnectAccountReader::read()`.

## Preconditions

None to build. The live checks need `STRIPE_SECRET` set to a test key.

**Data this task verifies against:** the bodies Stripe's test mode returned on
21 and 22 September 2026, in `tests/Fixtures/stripe` (one assembled, and its
README says which).

**Equipment:** a browser for the walk; Stripe test mode for the live reads.

## Scope

**In:**

- Reading, for an account that cannot charge, why, and the steps out of it.
- Integrations showing them; the connect landing's toast; the dashboard's next
  action; the price field's note.
- Remembering the readiness on the Group, and clearing it on disconnect and on
  Stripe's deauthorise.

**Out:**

- The Peer's side: the public page and checkout are unchanged (`T-085`).
- Hearing Stripe's `account.updated`, so the remembered readiness moves without
  a read (→ draft `T-166`).
- Payouts held back while charges work.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Integrations/Stripe/ConnectAccountReader.php` | new | the account and capability read into readiness and steps; the pages |
| `app/Integrations/Stripe/Connect.php` | edit | `account()` reads card_payments when charges are off |
| `app/Data/ConnectAccount.php` | edit | `readiness`, `steps`; `fromStripe()` moved out |
| `app/Data/PaymentsStep.php` | new | a step: task, page, details, Stripe's words |
| `app/Enums/PaymentsReadiness.php` | new | ready, incomplete, action_needed, checking, refused |
| `app/Enums/PaymentsTask.php` | new | one per page, in the order shown |
| `app/Enums/PaymentsDetail.php` | new | what Stripe asked for, in Qori's words |
| `app/Models/Group.php` | edit | the cast |
| `database/migrations/2026_09_22_000000_add_payments_readiness_to_groups.php` | new | the column |
| `app/Services/PaymentsService.php` | edit | `read()` remembers it; `disconnect()` and `forget()` clear it |
| `app/Services/ShareDigest.php` | edit | the dashboard's next action |
| `app/Support/PaymentsReadinessCopy.php` | new | the Integrations props |
| `app/Http/Controllers/Share/IntegrationsController.php` | edit | status from readiness; the `readiness` prop |
| `app/Http/Controllers/Settings/PaymentsFinaliseController.php` | edit | the toast |
| `app/Http/Controllers/Share/SeriesController.php` | edit | `paymentsReady` and the note |
| `resources/js/components/share/PaymentsReadiness.vue` | new | the steps |
| `resources/js/pages/share/settings/Integrations.vue` | edit | shows them |
| `resources/js/components/series/SeriesForm.vue` | edit | the price note |
| `resources/js/pages/share/series/Show.vue` | edit | its props |
| `lang/en/payments.php` | edit | readiness, steps, details, toast |
| `lang/en/share.php` | edit | the dashboard's lines |
| `lang/en/series.php` | edit | the price note |
| `docs/flows/billing.md` | edit | the read, the steps, where each is said |
| `docs/tinker/e2e-first-share.md` | edit | reading the steps from a shell |
| `tests/Fixtures/stripe/README.md`, `tests/Fixtures/stripe/account-sign-up-unfinished.json`, `tests/Fixtures/stripe/capability-card-payments-sign-up-unfinished.json`, `tests/Fixtures/stripe/account-charges-enabled-payouts-due.json`, `tests/Fixtures/stripe/capability-card-payments-active.json`, `tests/Fixtures/stripe/account-identity-document-due.json` | new | observed bodies |
| `tests/Unit/Integrations/Stripe/ConnectAccountReaderTest.php` | new | |
| `tests/Feature/Share/PaymentsReadinessTest.php` | new | |
| `tests/Feature/ShareDigestTest.php` | edit | three cases |
| `tests/Feature/Series/SeriesPriceTest.php` | edit | one case |
| `tests/Feature/Share/PaymentsDisconnectTest.php` | edit | readiness cleared |
| `tests/Feature/Share/PaymentsOauthTest.php` | edit | the removed prop; the capability faked |
| `tests/Feature/Checkout/ConnectOnboardingTest.php` | edit | the reader's new home |

## Database

| Table | Column | Type | Null | Default | Index / constraint |
| --- | --- | --- | --- | --- | --- |
| `groups` | `payments_readiness` | `varchar(255)`, a `PaymentsReadiness` value | yes | null | none |

Migration: `database/migrations/2026_09_22_000000_add_payments_readiness_to_groups.php`

## Code

```php
namespace App\Integrations\Stripe;

class ConnectAccountReader
{
    public const VERIFY_URL = 'https://dashboard.stripe.com/account/onboarding';
    public const HOME_URL = 'https://dashboard.stripe.com/dashboard';
    public const BUSINESS_DETAILS_URL = 'https://dashboard.stripe.com/settings/business-details';
    public const BANK_ACCOUNTS_URL = 'https://dashboard.stripe.com/settings/payouts';
    public const PAYMENT_METHODS_URL = 'https://dashboard.stripe.com/settings/payment_methods';
    public const SUPPORT_URL = 'https://support.stripe.com/contact';

    public static function read(array $account, ?array $cardPayments = null): ConnectAccount;
}

namespace App\Data;

class PaymentsStep
{
    public function __construct(public PaymentsTask $task, public string $url, public array $details = [], public array $problems = []) {}
}

// ConnectAccount gains PaymentsReadiness $readiness and list<PaymentsStep> $steps.
// PaymentsReadiness::asksTheCreator(): incomplete, action_needed, refused.
// PaymentsReadinessCopy::props(ConnectAccount $account, bool $isOwner): array
```

## Copy

| Key | File | English |
| --- | --- | --- |
| `not_ready`, `not_ready_where` | `lang/en/payments.php` | "Your Stripe account is connected, but it can't take payments yet." / "Integrations, under Settings, lists exactly what Stripe needs and where to do it." |
| `readiness.{incomplete,action_needed,checking,refused}.{badge,headline,body}` | `lang/en/payments.php` | e.g. "Needs you" / "Stripe can't take payments for you until you do the steps below." |
| `readiness.{details_label,problems_label,owner_note,refresh}` | `lang/en/payments.php` | "Stripe needs:" / "Stripe says:" / "Only the owner can do these, in their own Stripe account." / "This page asks Stripe again each time you open it." |
| `steps.<task>.{title,body,link}`, one per `PaymentsTask` | `lang/en/payments.php` | e.g. "Turn on card payments" / "In Stripe, go to Settings, then Payments, then Payment methods, and press Turn on beside Cards." / "Open Payment methods in Stripe" |
| `details.<detail>`, one per `PaymentsDetail` | `lang/en/payments.php` | e.g. "a photo of your ID: passport, driving licence or national ID card" |
| `blocked.payments_not_ready.{message,detail,label}`, `blocked.payments_not_ready_admin.{message,detail}` | `lang/en/share.php` | "Stripe can't take payments for you yet" / "Nobody can pay for your priced :series_plural until it can. …" / "See what Stripe needs" |
| `price_payments_not_ready`, `price_payments_not_ready_link` | `lang/en/series.php` | "Stripe can't take payments for you yet, so nobody can pay for this :series." / "See what Stripe needs" |

Removed: `payments.incomplete`, whose words are now the `incomplete` headline.

## Routes

None.

## Tests

**New: `tests/Unit/Integrations/Stripe/ConnectAccountReaderTest.php` — 17 cases**

1. `test_an_account_that_charges_is_ready_whatever_payouts_still_need`
2. `test_an_unfinished_sign_up_is_one_step_listing_what_stripe_asked_for`
3. `test_the_capability_leaves_out_what_only_payouts_need`
4. `test_a_missing_identity_document_sends_the_creator_to_stripes_home_page`
5. `test_a_capability_that_is_not_one_is_not_believed`
6. `test_stripes_own_words_reach_the_step_they_are_about`
7. `test_details_after_sign_up_go_to_the_page_that_holds_them`
8. `test_waiting_on_stripes_checks_asks_nothing`
9. `test_a_capability_that_is_only_checking_is_believed_over_the_accounts_list`
10. `test_card_payments_never_asked_for_leave_the_accounts_list_to_stand_in`
11. `test_a_refused_account_is_sent_to_stripe_support`
12. `test_card_payments_never_asked_for_are_turned_on_in_stripe`
13. `test_an_account_without_card_payments_in_its_map_turns_them_on`
14. `test_card_payments_off_for_no_listed_reason_points_at_the_account`
15. `test_an_unfinished_sign_up_with_nothing_listed_still_says_finish_it`
16. `test_a_field_nobody_mapped_is_one_more_item_on_stripes_list`
17. `test_a_companys_fields_are_named_for_what_they_are`

**New: `tests/Feature/Share/PaymentsReadinessTest.php` — 7 cases**

1. `test_the_owner_is_shown_each_step_with_what_stripe_asked_for_and_where`
2. `test_the_owner_reads_what_stripe_said_was_wrong`
3. `test_an_admin_reads_the_steps_without_links_or_stripes_words`
4. `test_while_stripe_checks_there_is_nothing_to_do`
5. `test_the_read_is_remembered_on_the_group`
6. `test_connecting_an_account_stripe_holds_back_says_where_the_list_is`
7. `test_connecting_an_account_stripe_is_checking_says_it_is_being_checked`

**Changed:**

- `tests/Feature/ShareDigestTest.php` — three cases: the owner is told first,
  the admin is told it is the owner's, and the warning waits for a price and
  for something to do.
- `tests/Feature/Series/SeriesPriceTest.php` — the price field's note.
- `tests/Feature/Share/PaymentsDisconnectTest.php` — disconnect and Stripe's
  deauthorise clear the readiness.
- `tests/Feature/Share/PaymentsOauthTest.php` — `incompleteNote` is gone; the
  capability read is faked so nothing strays to Stripe.
- `tests/Feature/Checkout/ConnectOnboardingTest.php` — reads through
  `ConnectAccountReader`.

## Acceptance

- [x] An account Stripe will not let charge shows on Integrations why, and each
      step with exactly what Stripe asked for and a link to its page in the
      creator's Stripe dashboard
- [x] "Nothing to do" is said only while Stripe is checking
- [x] Connecting an account that cannot charge says where the list is
- [x] The dashboard and the price field say payments are held back, from what
      the last read found
- [x] An admin reads the steps without the links or Stripe's own words
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

Specified and built on 22 September 2026 as the owner's "small fixup"; it
outgrew `fixups.md`'s hour, so it is a task.

The pages were read from Stripe's own documentation that day: the set-up guide
(`/account/onboarding`, "Verify your business"), the Dashboard guide (Home at
`/dashboard`, which "surfaces important notifications, like … identity
verifications"), the support articles for Bank accounts and currencies
(`/settings/payouts`), Business details (`/settings/business-details`, where
the statement descriptor is now set) and Payment methods
(`/settings/payment_methods`).

Two live reads confirmed the path against test mode: the fixture account
`acct_1UI86UKUCxf9uWKz` (made for this task, test mode, nothing filled in) reads
`incomplete` with one step and eight details; the first-share seller
`acct_1UI6URKUCxZU2qfd` reads `ready`. The fixture account can be removed with
`php artisan qori:stripe:purge-connected-accounts` whenever the sandbox wants
tidying.
