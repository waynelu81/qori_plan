---
id: T-092
title: A Peer confirms the vendor account they will open with
stream: storage
status: draft
owner: unassigned
estimate: L
depends: T-091
blocks: T-094, T-096, T-098
---

# T-092 — A Peer confirms the vendor account they will open with

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom. Written on 16 September 2026 from
> `D-016` and the owner's BYO blueprint; reviewed the same day against the
> developer's review of the plan that day, whose asks that reach this
> task — the state vocabulary and who resolves each state, a bounded wait on
> every vendor call, identity changes as a defined reconciliation, and no
> unobserved response presented as a fixture — are folded in below. Amended on
> 17 September 2026 from `D-020` and `D-021`: the Series page's prompt is
> `awaiting_identity`'s one action and returns there, a buyer reads what the
> Series needs from them beside the buy button, and nothing promises a moment
> of opening. Amended on 19 September 2026 from `D-022`, `D-023`, `D-025`,
> `D-034` and that day's readiness audit: the landing's words are read in the
> vendor's folder, as `T-113` did for Stripe; the Peer's code exchange waits as
> long as a creator's; the before-buying list holds no code for any one
> provider; and `/u/identities` offers only the sign-ins that are built.

## Why

`D-016` grants each Peer's own vendor account on the Series container, and for
Google Drive, OneDrive and Dropbox that account has to be known before the
grant can be made: Google shares only with a Google account
(https://support.google.com/drive/answer/6033939), a personal OneDrive only
with a personal Microsoft account
(https://support.microsoft.com/en-us/office/external-or-guest-sharing-in-onedrive-sharepoint-and-lists-7aa070b8-d094-4921-9dd9-86392f2a79e7),
and Dropbox turns an address that is not the account's main email into a
pending invite rather than membership (`AddMemberSelectorError` in
https://github.com/dropbox/dropbox-api-spec/blob/main/sharing_folders.stone).
Nothing in the code can hold that account. `users` is global with no
per-provider field (`database/migrations/2026_09_08_000000_create_qori_schema.php:32-50`),
`peers` is per Group and unique on `(group_id, email)` (`:120-133`), so an
address kept there would be asked for again by every creator, and
`connections` is the Group's, unique on `(group_id, provider)` (`:193`), while a
Peer who came in from a Series page has no Group at all
(`app/Http/Controllers/SeriesAccessController.php:54-67`). `T-091` therefore
leaves `identityFor()` returning null (`T-091`, Code), so its providers answer
`GrantResult::awaitingIdentity()` with no vendor call, and every grant row for
these providers would sit at `awaiting_identity` with nobody able to resolve it.

Afterwards a person holds one confirmed identity per vendor, kept on their own
account under `/u/*`, proven by signing in with the vendor rather than typed —
the way `EmailChangeService` will not move an address until the new one proves
itself (`app/Services/EmailChangeService.php:42-106`) and the Series code
flow will not grant until the code lands (`SeriesAccessController.php:103-162`).
A Series page whose containers need an account the Peer has not confirmed asks
for it above the Episode list, and a paid Series asks before the buyer reaches
Stripe, so the webhook can grant with nobody present — the stream's first
priority, stated as "confirmed before payment where a Series needs one"
(`docs/planning/streams/storage.md`, priority 1). Before that, the buy button
has beside it what the Series' provider will need from the buyer, so nobody
learns it after paying (`D-021`). Confirming once fills every
grant that was waiting for it, in every Group. Zoom, Teams, Vimeo and YouTube
need none of this (`D-016`).

## Decisions taken to make this specifiable

**The record is the person's, not a Group's: a `vendor_identities` table with
no `BelongsToGroup`.** The reasons in Why. It joins the global tables in
`docs/architecture/tenancy.md:42-43`, and every read of it is by `user_id`,
so no scope is crossed to reach it.

**Confirmed by signing in with the vendor, never by typing.** A typed address
fails four ways the research names: a typo, an alias that is not the account's
main address (Dropbox), an address with no account at the vendor, and the wrong
one of two accounts. Sign-in removes all four and proves the address before it
controls access. The round trip requests sign-in scopes only — Google
`openid email`
(https://developers.google.com/identity/openid-connect/openid-connect),
Microsoft `openid email`
(https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow),
Dropbox `openid email` through its OpenID Connect sign-in
(https://developers.dropbox.com/oidc-guide) — and **keeps no Peer token**: the
code is exchanged, the id token read, and nothing from the vendor is stored but
the claims below.

**The key is the vendor's stable subject, and the email is what grants are
made to.** Google says to key on `sub` (unique, never reused) and never on
`email`, which may change, with `email_verified` beside it
(https://developers.google.com/identity/openid-connect/openid-connect).
Microsoft says its `email` claim can be wrong, can change and must not be used
for authorisation; the identity is `oid` in tenant `tid`, and `xms_edov`
says whether the address is verified
(https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference).
Dropbox's id token carries `sub` (the `account_id`), `email` and
`email_verified` (https://developers.dropbox.com/oidc-guide), and the folder
grant refuses an unverified account with `unverified_dropbox_id`
(`sharing_folders.stone`, the URL in Why). So: `subject` is `sub` / `oid` /
`account_id`, `tenant` holds Microsoft's `tid`, and **an identity whose email
the vendor reports unverified is refused, not stored.** Which claim says so is
the vendor's word and is read in its folder (`D-022`): the class answers
`IdentityLandingStatus::UnverifiedEmail`, and `VendorIdentityData` carries no
verified flag. No claim name in this file has been observed; each is from the
vendor page beside it, and the fixtures are owed as Preconditions says —
Google's `sub`, `email` and `email_verified` by `T-093`'s step 2, while no
capture shows its `nonce` (Preconditions).

**`IdentityProvider` is its own enum, not `ConnectionProvider`.** The Peer
signs in with Google, Microsoft or Dropbox — an account, not a product — and
one Microsoft identity serves OneDrive whatever `T-098` decides about work
tenants. `IdentityProvider::forConnection()` is the one crossing from a
container's `ConnectionProvider` to the identity it needs, and it answers null
for the providers that need none, which is how the Series page knows not to
ask. A pasted link (`D-025`), a Drive URL among them, holds no container, so it
asks for nothing either: its creator set the vendor's sharing to anyone with
the link.

**Routes live under `/u/*`, and the landing's URL is exact.** Each
vendor matches the redirect URI against a list, so the Series cannot be in the
path; it travels in the session, as the Group does to
`u/payments/stripe/finalise` (`routes/settings.php:52-60`,
`app/Http/Controllers/Settings/PaymentsFinaliseController.php:15-27`).
The path names the vendor, as every landing does (`D-033`): a Peer's Google
sign-in lands on `u/identities/google/finalise` as a creator's Google
connection lands on `T-044`'s `u/connections/google/finalise`.
The state is minted the way `PaymentsService` mints its own, `Str::random(40)`
into the session before the URL goes out
(`app/Services/PaymentsService.php:82-89`), with a nonce beside it for the id
token, and the entry is spent before the vendor is called, as it is there
(`:112`). Begin is a `POST` to
`u/identities/{vendor}/begin`, the step named in its path as the landing's is
(`D-033`), answered with `Inertia::location()`, because the prompt is an
Inertia form and an XHR cannot follow a redirect to another origin
(`app/Http/Controllers/CheckoutController.php:53-58`).

**The landing's words are the vendor's, and are read in the vendor's folder**
(`D-022`, `D-023`), as `T-113` did for Stripe.
`ConfirmsPeerIdentity::finaliseConfirmation()` takes the landing's query
whole, with the state and nonce this session sent, and answers an
`App\Data\IdentityLanding` whose `IdentityLandingStatus` is `Confirmed` (with
the identity), `Declined`, `UnverifiedEmail`, `NotFromQori` or `Failed` (with
the vendor's own code as `upstream`): the shape of
`SellsSeries::finaliseOnboarding(array $landing, string $expectedState): OnboardingOutcome`
(`app/Integrations/Contracts/SellsSeries.php:40-49`,
`app/Data/OnboardingOutcome.php`). `GoogleSignIn` reads `error=access_denied`,
`state`, `code` and the id token in the order `Connect::finaliseOnboarding()`
reads Stripe's (`app/Integrations/Stripe/Connect.php:90-151`), so a forged or
stale landing spends nothing. It never throws for what Google did or failed
to do: no answer is `Failed` with `upstream` `connection`, where Stripe's
class throws (`:121-129`), so the one place an `AppException` is built is the
Service, which fills `:vendor`. `VendorIdentityService::finaliseConfirmation()`
reads the pending state and nonce from its `SESSION_KEY`, spends the entry
before the call, and maps each status to this draft's outcomes: `Confirmed`
stores the row and backfills, `Declined` stores nothing, and the other three
are `errors.identities.email_unverified`, `errors.identities.state` and
`errors.identities.vendor_failed`. Each refusal redirects, with its toast, to
where the sign-in started — the Series page for a Peer (`D-020`), else
`/u/identities` — so the button that starts again is in reach.
`IdentitiesController::finalise()` passes `$request->query()` and reads
nothing in it. `T-044`'s connection landing takes the same shape,
`ConnectsAccounts::finaliseConnection(...): ConnectionLanding`.

**One confirmation backfills every Group, through the allow-listed
crossings only.** `Access::forUser()` (`app/Models/Access.php:253-259`) lists
the person's active accesses across Groups, `Access::grantedSeries()`
(`:235-241`) reaches each Series, and each Group's work runs inside
`CurrentGroup::runFor()` (`app/Support/CurrentGroup.php:88-101`). No new
`acrossAllGroups()` caller; `ConsoleAccessTest`'s list
(`tests/Feature/Admin/ConsoleAccessTest.php:131-151`) is untouched.

**What this task does to a grant row, in the stream's six states.** `T-091`'s
`VendorGrantStatus` has `awaiting_identity` (the Peer resolves, by signing in
with the vendor — this task is that resolution), `awaiting_acceptance` (the
Peer resolves, with a step left at the vendor), `pending` (Qori retries; its
sentence says when Qori tries next), `needs_creator` (the creator resolves;
its sentence says the creator has been told and nothing more is needed from
the Peer — both `D-020`), `granted` and `revoked`.
`identityConfirmed()` moves `awaiting_identity` to `pending`; when the
subject changed it moves `granted` and `awaiting_acceptance` to `pending`
after a best-effort `revoke()` of the old permission; it leaves
`needs_creator` and `revoked` alone; and it never writes `granted` — only
`T-091`'s `record()` does, on a provider's evidence that the Peer can open
the container now, and each provider task says when that is. The prompt on
the Series page is the `awaiting_identity` sentence, and it names the person
reading it as who resolves it.

**A confirmation is an event `VendorAccessService` handles, not a bare
`ensureFor()`.** `T-091`'s `ensureFor()` leaves an `awaiting_identity` row
alone, so this task adds `identityConfirmed()` to that service, and then runs
`ensureFor()`. The row is reused rather than replaced because `T-091` keys one
row per `(access_id, series_container_id)`.

**Every vendor call is bounded, and the backfill does not make the person
wait for every Group.** `ConfirmsPeerIdentity::finaliseConfirmation()`
takes a budget last, `$timeoutSeconds`, which the client may only shorten
(`D-034`): `GoogleSignIn` sets Google's own limit on its `Http::` chain,
`GoogleAccounts::TIMEOUT_SECONDS` (20, `T-044`), since both classes call the
same token endpoint, and uses whichever is shorter.
`VendorIdentityService::finaliseConfirmation()` passes its own
`REQUEST_TIMEOUT_SECONDS` (provisional 10), because a Peer's code exchange at
Google waits as long as a creator's does at the same endpoint (`T-044`'s
`ConnectionService::REQUEST_TIMEOUT_SECONDS`), while every grant and revoke
the backfill makes keeps `VendorAccessService::REQUEST_TIMEOUT_SECONDS`
(provisional 5). A timeout is `Failed`, and `errors.identities.vendor_failed`
says try again. The backfill moves rows
first — row writes, no vendor — then calls `ensureFor()` inline for at most
`BACKFILL_INLINE_LIMIT` (provisional 3) of the person's Accesses, newest
first; every other row is `pending` and due now, and the Series page's own
`ensureFor()`, Open and `qori:access:reconcile` (`T-091`, every few minutes)
attempt it. Nothing is `ShouldQueue` and this task adds no command. A
`granted` row this task did not reset is re-checked by `T-091`'s `checked_at`
pass, not here. The other two reconciliation triggers — the creator
reconnecting (`T-044`'s `ConnectionReconnected` event, which `T-091`'s
listener answers with `reconnected()`) and a container replaced (`attach()`)
— are `T-091`'s and go through the same `ensureFor()`. The dedicated-container
rule (a container serves one Series, settled by `D-025` and enforced by
`T-091`'s `series_containers` unique on `(group_id, provider, external_id)`)
is `T-091`'s, and the picker sentence that sharing a folder shares everything
inside it, Episodes or not, is each provider task's (`T-094`, `T-096`,
`T-098`); `neededFor()` only reads what they store.

**Removing an identity touches no grant.** The owner's terms: revoke is best
effort and rare, and a person tidying their account is not asking to lose
access they paid for. The next Series that needs the vendor asks again.

**The prompt asks before payment on a paid Series.** The stream's first
priority is working access right after buying, and the paid Access is written
by the webhook with no Peer present
(`app/Http/Controllers/StripeWebhookController.php`, `CheckoutService::fulfil()`
`app/Services/CheckoutService.php:89-147`), so a grant at fulfilment needs the
identity already on file. The step sits in front of `CheckoutService::begin()`
in both callers (`CheckoutController.php:38-47`,
`SeriesAccessController.php:152-157`). A free Series is granted inline and asks
on the Series page, where `Confirming.vue` also lands a buyer
(`resources/js/pages/shared/Confirming.vue:10-14`). **The prompt promises
nothing about when the Series opens** (`D-021`): payment starts the grant, and
a grant can still be `pending`, or wait on a Dropbox Join or a creator, after
the money is in, so `identities.prompt.before_paying` says Qori starts letting
the account in when the payment goes through and the Series page shows
anything left.

**The prompt on `shared.show` is `awaiting_identity`'s one action, and its
sign-in comes back to `shared.show`** (`D-020`). Sign in with the vendor is
that state's primary action, and `destination` on the Series page is
`shared.show`, so the Peer lands where the notice for every other state sits.
The pre-payment prompt on the public page returns to the public page, because
buying is the next step there, and payment lands the buyer on `shared.show`
through Confirming. While a prompt shows it stands in for `T-091`'s notice,
so the block holding it carries the notice's `id="access"`, and a Peer whom
`T-089`'s Open sends back to `#access` lands on the prompt.

**A buyer reads what the Series needs from them before paying** (`D-021`,
part 1). `App\Support\BuyerRequirements::for(Series)`
returns rendered lines from the Series' `Active` containers' providers and the
Group's tier for each: `accesses.vendor.<provider>.before_buying.common.*`,
then `accesses.vendor.<provider>.before_buying.<tier>.*`, in the order the
lang file lists them, as `T-044`'s `ProviderSections` reads `limits.common.*`
then the tier's. `<provider>` is the `ConnectionProvider` value and `<tier>`
the `ProviderTier` value from `Connection::tier()` (`T-044`); a Group with no
tier stored for that provider gets the common lines alone. A Series with no
`Active` container — Vimeo, YouTube, Qori-hosted, a pasted link — and a
provider with no `before_buying` lines return nothing, and then nothing
renders. The public page shows the list, titled
`identities.requirements.title`, beside the buy button of a priced Series for
every viewer who is not granted, signed in or not, because it describes the
Series rather than the viewer; `shared.show`
shows the same list above the identity prompt, which is where a free Series
asks. **This task renders the lines and writes none of them**: Google Drive's
are `T-094`'s, Dropbox's `T-096`'s, OneDrive's `T-098`'s, and Zoom's `T-100`'s
only if Zoom needs something from a registrant. **`BuyerRequirements` holds no
code for any one provider.** A line that states a vendor's number names a key
of that provider's `config('qori.connections.<provider>')` block — `T-044`'s,
where every vendor fact in copy lives, never twice — and `for()` passes the
block's integer and string entries as replacements by key, `:creator` last so
no key can take its place. A provider task therefore adds a config key and a
line, and no code: `app/Support` holds nothing vendor-specific (`CLAUDE.md`,
`D-022`), and the per-provider `factsFor()` arms this draft had would have
kept a vendor's limits outside its folder. Nothing else in the class names a
vendor: it walks `ConnectionProvider::cases()` and reads lang and config by
value. Reading models from `app/Support` is allowed, as `SignInLanding` does
(`app/Support/SignInLanding.php:27-50`).

**Only Google's sign-in class is built here; Microsoft's and Dropbox's come
with their provider tasks.** The contract and a fake are enough for every
test in this task, and each vendor's token response has to be a fixture from
its spike before its class is written. Google's is the first journey, and
`T-093` captures its id-token fixture (Preconditions).

**`/u/identities` offers only the sign-ins that are built.**
`VendorIdentityService::offered()` lists the providers whose
`ConfirmsPeerIdentity` class is tagged `identity-providers` — Google alone
until `T-096` and `T-098` bind theirs — so the page never shows a button that
ends in `errors.identities.unsupported`, which `PLAN.md`'s beta gate rules
out, and `identities.none` names no service: it points at the list beneath
it, which grows as each class lands. `errors.identities.unsupported` stays as
the answer to a request made by hand. The Series page cannot meet a provider
with no class bound: a container is attached only through a provider task's
picker, `T-094` comes after this task, and `T-096` and `T-098` bind their
sign-in class beside their picker.

**No integration reads a Service.** `GoogleSignIn` is given its budget by
the caller, takes Google's limit from `GoogleAccounts`, and reads its client
id and secret from `config('services.google.*')`, the keys `T-044` adds
(`T-044`, Code); `ArchitectureTest` refuses a `use App\Services` or
`use App\Http` under `app/Integrations`
(`tests/Feature/ArchitectureTest.php:139-147`).

**Copy lives in `lang/en/identities.php`.** One feature, one file, and the
vendor names `D-016` permits here stay in one place. `:creator` is passed as
the Group's name, as `T-091`'s lines do, because `Vocabulary::KEYS`
(`app/Data/Vocabulary.php:23`) would otherwise fill it with the creator noun.
The sidebar item's title reaches `Layout.vue` as a shared Inertia prop rather
than a fourth inline string beside the three it holds today (`:14-27`),
which are §13's to convert, and is typed beside `terminology` in
`resources/js/types/global.d.ts` (`:19-25`), whose index signature would
otherwise leave it `unknown` to `vue-tsc` in `composer ci:check`. Every
`errors.identities.*` line gets `:vendor` through the exception's
replacements and uses no noun placeholder, because `AppException` fills none
(`app/Exceptions/AppException.php:179-205`).

## Preconditions

`T-091` done: `series_containers`, `vendor_grants`, `VendorGrantStatus`,
`VendorAccessService` and the `grant-providers` tag exist. `T-044` done, so
`ConnectionProvider::GoogleDrive`, `ProviderTier`, `Connection::tier()`, the
`qori.connections` config block and the `services.google` entry exist
(`T-044`, Code). `php artisan wayfinder:generate --with-form` before touching
the Vue pages, which import the generated `@/routes/identities`.

**Data this task verifies against:** a clean database; the tests seed two
Groups, a Series with an `Active` container per provider, and grant rows at
`awaiting_identity` through `T-091`'s factories.

**Equipment:** none for the suite. A browser walk of the round trip needs the
local OAuth client with `http://localhost:8001/u/identities/google/finalise`
among its redirect URIs, the app published, and one Google account
(`docs/planning/vendor-accounts.md`, Google Drive, steps 10 and 12; `T-093`'s
`peer-gmail` profile).

**Spike:** the Google token response, `tests/Fixtures/google/oidc-token.json`
(the `POST https://oauth2.googleapis.com/token` exchange), is captured by
`T-093` in its step 2, as `peer-gmail` through the OAuth Playground with the
access type Online. Its `access_token` and `id_token` are `REDACTED`, and
`tests/Fixtures/google/README.md` records the id token's decoded `sub`,
`email` (as its role) and `email_verified`, and the names of its other claims
(`T-093`, Code, step 2, and Decisions, "Redaction is by role"). So the
fixture is the response's shape, and the claims are the README's:
`GoogleSignInTest` builds its id token from them (Tests). The Playground
probably sends no `nonce`, so the fixture cannot show Google echoing one; the
nonce check is specified from Google's page instead, which marks `nonce`
Required among the authentication request's parameters and says the id token
carries it back
(https://developers.google.com/identity/openid-connect/openid-connect,
"Authentication URI parameters" and "An ID token's payload"), and the tests
supply their own. Until that fixture and README are committed this task is
not `ready`. The Microsoft and Dropbox equivalents are owed by `T-097` and
`T-095` and are consumed by `T-098` and `T-096`, not here.

## Scope

**In:**

- `vendor_identities`, `VendorIdentity`, `IdentityProvider`, the factory.
- `ConfirmsPeerIdentity`, `VendorIdentityData`, `IdentityLanding`,
  `IdentityLandingStatus`, `GoogleSignIn` reading its own landing, the
  `identity-providers` tag, the fake.
- `VendorIdentityService`: offered, begin, finalise, remove, needed, missing,
  the backfill; `identityConfirmed()` and a filled `identityFor()` on
  `VendorAccessService`.
- Four routes and a page under `/u/identities`, a sidebar entry.
- The prompt and the confirmed line on `shared.show`; the prompt before the
  buy button and the guard before `begin()`.
- `BuyerRequirements` and the list it feeds: beside the buy button on the
  public page of a priced Series, and above the prompt on `shared.show`
  (`D-021`); `identities.requirements.title`, and `identities.prompt.before_paying`
  worded so it promises no moment of opening.
- Flow, architecture and tinker docs.

**Out:**

- Any grant, revoke, container or Open logic — `T-091`, `T-089`.
- Any scheduled command: the rows this task leaves `pending` are
  `qori:access:reconcile`'s (`T-091`), and a `granted` row it did not reset
  is re-checked by `T-091`'s `checked_at` pass.
- `MicrosoftSignIn` and `DropboxSignIn` — `T-098` and `T-096`, with their
  spikes' fixtures; this task binds only Google and the fake.
- Proving a Dropbox Peer has room for the folder, and the `awaiting_acceptance`
  state that says so — `T-096`. A confirmed identity proves the account, not
  the space.
- The lines under `accesses.vendor.<provider>.before_buying.*` and the
  `qori.connections.<provider>` keys they interpolate — Google Drive `T-094`,
  Dropbox `T-096`, OneDrive `T-098`, Zoom `T-100` if Zoom needs anything from
  a registrant. This task adds no line under `accesses.vendor` and no config
  key.
- `T-091`'s notice, its `shared.vendor_notice.reasons.*` sentences, Check
  again and the disabled Open controls; this task hides the notice while a
  prompt stands in for it and changes nothing else about them (`D-020`).
- Invitations landing on the Series page — `T-043` picks up this prompt as
  written.
- Delayed payments and refunds — `T-102`, `T-103`.
- Staff: the console reads nothing here; `vendor_identities` is a person's
  and appears on no admin page.
- Converting `Layout.vue`'s three existing inline titles — §13's.

## Files

| Path                                                                                                                   | Change | Notes                                                                                                                      |
| ---------------------------------------------------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| `database/migrations/2026_09_20_000200_create_vendor_identities_table.php`                                             | new    | Below; after `T-044`'s `2026_09_20_000000` and `T-091`'s `2026_09_20_000100`                                               |
| `app/Models/VendorIdentity.php` `app/Enums/IdentityProvider.php`                                                       | new    | No `BelongsToGroup`                                                                                                        |
| `app/Models/User.php`                                                                                                  | edit   | `identities()` relation                                                                                                    |
| `app/Integrations/Contracts/ConfirmsPeerIdentity.php` `app/Data/VendorIdentityData.php`                                | new    | The contract and the identity it confirms                                                                                  |
| `app/Data/IdentityLanding.php` `app/Enums/IdentityLandingStatus.php`                                                   | new    | What a landing came to, in Qori's words: `T-113`'s `OnboardingOutcome` and `OnboardingStatus` for a Peer                   |
| `app/Integrations/Google/GoogleSignIn.php`                                                                             | new    | `openid email`; reads its own landing; no token kept; no Service import                                                    |
| `app/Providers/IntegrationServiceProvider.php`                                                                         | edit   | `identity-providers` tag beside `media-providers` (`:35-39`)                                                               |
| `app/Services/VendorIdentityService.php`                                                                               | new    | Below                                                                                                                      |
| `app/Services/VendorAccessService.php`                                                                                 | edit   | `identityConfirmed()`; `identityFor()` filled                                                                              |
| `app/Support/BuyerRequirements.php`                                                                                    | new    | `for()`; reads inside the Series' Group; names no vendor                                                                   |
| `app/Http/Controllers/Settings/IdentitiesController.php` `app/Http/Requests/Settings/BeginIdentityRequest.php`         | new    |                                                                                                                            |
| `app/Http/Controllers/Shared/SharedController.php`                                                                     | edit   | `identity` prop on `show()`, with `requirements`                                                                           |
| `app/Http/Controllers/PublicSeriesController.php` `app/Http/Controllers/CheckoutController.php`                        | edit   | `identity` and `requirements` props; the guard before `begin()`                                                            |
| `app/Http/Controllers/SeriesAccessController.php`                                                                      | edit   | The guard before `begin()` in `verify()`                                                                                   |
| `app/Http/Middleware/HandleInertiaRequests.php`                                                                        | edit   | `settingsNav.identities` in `share()` (`:160-193`)                                                                         |
| `resources/js/types/global.d.ts`                                                                                       | edit   | `settingsNav: { identities: string }` in `sharedPageProps` (`:19-25`)                                                      |
| `routes/settings.php`                                                                                                  | edit   | Four routes                                                                                                                |
| `resources/js/pages/settings/Identities.vue` `resources/js/components/series/IdentityPrompt.vue`                       | new    | The page; the prompt shared by both Series pages                                                                           |
| `resources/js/components/series/SeriesRequirements.vue`                                                                | new    | The before-buying list, shared by both Series pages                                                                        |
| `resources/js/pages/shared/Show.vue` `resources/js/pages/public/Series.vue` `resources/js/layouts/settings/Layout.vue` | edit   | List, prompt and confirmed line, notice hidden behind a prompt; list and prompt before the button; sidebar item (`:14-27`) |
| `lang/en/identities.php`                                                                                               | new    | Copy below, `requirements.title` included                                                                                  |
| `lang/en/errors.php`                                                                                                   | edit   | `identities.*` refusals                                                                                                    |
| `database/factories/VendorIdentityFactory.php` `tests/Doubles/ConfirmsAnyPeer.php`                                     | new    | The fake is built for one `IdentityProvider` and records every argument                                                    |
| `tests/Feature/Settings/IdentitiesTest.php` `tests/Feature/Integrations/Google/GoogleSignInTest.php`                   | new    | 15 and 6 cases; the second beside Stripe's (`tests/Feature/Integrations/Stripe/`)                                          |
| `tests/Feature/Shared/IdentityPromptTest.php` `tests/Feature/Checkout/IdentityBeforeCheckoutTest.php`                  | new    | 7 and 4 cases                                                                                                              |
| `tests/Feature/Checkout/BuyerRequirementsTest.php`                                                                     | new    | 5 cases                                                                                                                    |
| `docs/flows/vendor-access.md` `docs/flows/checkout.md` `docs/flows/accesses.md`                                        | edit   | The identity step in the chain `T-091` wrote; the pre-checkout guard and the before-buying list; the page                  |
| `docs/architecture/tenancy.md` `docs/tinker/accesses.md`                                                               | edit   | `vendor_identities` in the global list (`:42-43`); a backfill recipe                                                       |

`docs/flows/vendor-access.md` is `T-091`'s new file, edited here. `config/services.php`
is not touched: `T-044` adds the `google` entry this task reads. Nor is
`config/qori.php`: the `connections` block is `T-044`'s, and each key a
before-buying line interpolates is its provider task's.
`docs/flows/auth.md` is not touched: the round trip uses its own session key
and spends neither `url.intended` nor `SignInDestination`
(`docs/flows/auth.md:173-198`).

## Database

| Table               | Column                    | Type       | Null | Default | Index / constraint                                                  |
| ------------------- | ------------------------- | ---------- | ---- | ------- | ------------------------------------------------------------------- |
| `vendor_identities` | `id`                      | ulid       | no   |         | primary                                                             |
| `vendor_identities` | `user_id`                 | ulid       | no   |         | FK `users` cascade; unique `(user_id, provider)`                    |
| `vendor_identities` | `provider`                | string     | no   |         | `IdentityProvider` value                                            |
| `vendor_identities` | `subject`                 | string     | no   |         | Google `sub`, Microsoft `oid`, Dropbox `account_id`                 |
| `vendor_identities` | `tenant`                  | string     | yes  | null    | Microsoft `tid`; null for the others                                |
| `vendor_identities` | `email`                   | string     | no   |         | lowercased; the address the grant is made to                        |
| `vendor_identities` | `email_verified_at`       | timestamp  | yes  | null    | set at confirmation; `T-096` may null it on `unverified_dropbox_id` |
| `vendor_identities` | `confirmed_at`            | timestamp  | no   |         | moves on every sign-in                                              |
| `vendor_identities` | `created_at` `updated_at` | timestamps | yes  |         |                                                                     |

No `group_id`, and no index on `subject`: nothing asks which people share a
vendor account, and two Qori accounts may legitimately hold the same one.

Migration: `database/migrations/2026_09_20_000200_create_vendor_identities_table.php`,
sorting after `T-044`'s `2026_09_20_000000` and `T-091`'s `2026_09_20_000100`
and after every migration already shipped
(`database/migrations/2026_09_17_000000_rename_qori_s3_provider_to_cloudflare_r2.php`
is the last).

## Code

```php
namespace App\Enums;

enum IdentityProvider: string
{
    case Google = 'google';
    case Microsoft = 'microsoft';
    case Dropbox = 'dropbox';

    /** The identity a container's provider needs; null for the providers that need none (D-016). */
    public static function forConnection(ConnectionProvider $provider): ?self;
}
```

`forConnection()` maps `ConnectionProvider::Dropbox` to `Dropbox`,
`ConnectionProvider::GoogleDrive` (`T-044`) to `Google`, and the OneDrive
cases `T-098` adds to `Microsoft`; `Vimeo`, `Zoom`, `Teams` and the YouTube
cases `T-090` adds answer null.

```php
namespace App\Models;

class VendorIdentity extends Model   // HasUlids, HasFactory; no BelongsToGroup
{
    protected $table = 'vendor_identities';
    // fillable: user_id, provider, subject, tenant, email, email_verified_at, confirmed_at
    // casts: provider => IdentityProvider, email_verified_at, confirmed_at => 'datetime'
    public function user(): BelongsTo;
    public function isVerified(): bool;    // email_verified_at !== null
    /** The shape T-091's grant() takes, for the container provider asking. */
    public function toGrantIdentity(ConnectionProvider $for): \App\Data\GrantIdentity;   // (provider: $for, email, subject)
    public static function verifiedFor(User $user, IdentityProvider $provider): ?self;
}

// App\Models\User
public function identities(): HasMany;   // VendorIdentity, user_id — a person's own rows, no crossing
```

```php
namespace App\Integrations\Contracts;

interface ConfirmsPeerIdentity
{
    public function provider(): IdentityProvider;
    /** The vendor's sign-in URL: sign-in scopes only, $state and $nonce round-tripped, $loginHint the Qori address where the vendor takes one. */
    public function beginConfirmation(string $redirectUrl, string $state, string $nonce, ?string $loginHint = null): string;
    /**
     * Read the landing the vendor sent the Peer back with (D-022, D-023). Its words are the vendor's, so they are read
     * here and answered in Qori's: confirmed with the identity, declined, an address the vendor has not verified, not
     * from this session when the landing's state is not $expectedState, or failed with the vendor's own code as upstream.
     * The code is exchanged within $timeoutSeconds, a budget the client may only shorten (D-034); the id token is
     * checked against $expectedNonce; every token is discarded. Never throws for anything the vendor sent or failed to
     * send: no answer, a timeout included, is failed('connection').
     *
     * @param  array<string, mixed>  $landing
     */
    public function finaliseConfirmation(array $landing, string $expectedState, string $expectedNonce, string $redirectUrl, int $timeoutSeconds): IdentityLanding;
}
```

```php
namespace App\Enums;

/** How a Peer's round trip to a vendor's sign-in ended. OnboardingStatus's four, and the vendor's own verdict on the address. */
enum IdentityLandingStatus: string
{
    case Confirmed = 'confirmed';                 // the vendor vouched for an account and its address
    case Declined = 'declined';                   // the Peer stopped at the vendor; nothing to store or undo
    case UnverifiedEmail = 'unverified_email';    // an account whose address the vendor has not verified
    case NotFromQori = 'not_from_qori';           // the landing's state is not the one this session sent
    case Failed = 'failed';                       // the vendor sent them back without an identity Qori can keep
}
```

```php
namespace App\Data;

/** What a vendor's sign-in landing came to, in Qori's terms: T-113's OnboardingOutcome for a Peer's identity. */
class IdentityLanding
{
    public function __construct(
        public IdentityLandingStatus $status,
        public ?VendorIdentityData $identity = null,   // Confirmed only
        public ?string $upstream = null,               // Failed only: the vendor's own code, for the log
    ) {}

    public static function confirmed(VendorIdentityData $identity): self;
    public static function declined(): self;
    public static function unverifiedEmail(): self;
    public static function notFromQori(): self;
    public static function failed(?string $upstream = null): self;
}

class VendorIdentityData
{
    public function __construct(
        public IdentityProvider $provider,
        public string $subject,          // the vendor's stable id for the account, never reused
        public string $email,            // as the vendor sent it; the service lowercases
        public ?string $tenant = null,   // the account's directory, where the vendor has one
    ) {}
}
```

```php
namespace App\Integrations\Google;

class GoogleSignIn implements ConfirmsPeerIdentity
{
    public const AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/v2/auth';
    public const TOKEN_URL = 'https://oauth2.googleapis.com/token';
    public const SCOPES = 'openid email';
    // beginConfirmation(): response_type=code, scope=SCOPES, redirect_uri, state, nonce, prompt=select_account, login_hint
    //   when given; client_id from config('services.google.client_id'); no access_type=offline, no include_granted_scopes.
    // finaliseConfirmation(), in the order Connect::finaliseOnboarding() reads Stripe's (app/Integrations/Stripe/Connect.php:90-151):
    //   $matches = $expectedState !== '' && hash_equals($expectedState, the landing's state), as GoogleAccounts reads its own (T-044):
    //   an error whose state is present and does not match → notFromQori(); error=access_denied → declined();
    //   any other error word → failed(<the word>); no error and ! $matches → notFromQori(); no code → failed(); no call on any of these;
    //   Http::asForm()->timeout(min(GoogleAccounts::TIMEOUT_SECONDS, $timeoutSeconds))->post(TOKEN_URL, grant_type=authorization_code,
    //     code, redirect_uri, client_id, client_secret from config('services.google.client_secret')); no retry(), since a code is
    //     single-use;
    //   no answer (ConnectionException, a timeout included) → failed('connection'); a 4xx or 5xx → failed(<status>), logged with
    //     Google's `error` word alone, never the body, which may quote the code;
    //   the id_token's payload: aud not the client id, exp past, or nonce not hash_equals($expectedNonce) → failed('id_token');
    //   email_verified not true → unverifiedEmail(); else confirmed(new VendorIdentityData(Google, sub, email)).
    //   The access_token is never read. No `use App\Services`.
}
```

`GoogleSignIn` does not check the id token's signature: the token comes
straight from Google's token endpoint over HTTPS, in answer to Qori's own
client secret, which Google's page says is enough
(https://developers.google.com/identity/openid-connect/openid-connect, "5.
Obtain user information from the ID token"). Its limit is
`GoogleAccounts::TIMEOUT_SECONDS`, which `T-044` sets for Google as Stripe's
client sets its own 20 (`app/Integrations/Stripe/Client.php:29`, `:57`),
rather than a second number for the same endpoint; inside the landing the
service's 10 is what binds.

`prompt=select_account`, `login_hint` and `nonce` are documented parameters of
Google's OpenID Connect endpoint
(https://developers.google.com/identity/openid-connect/openid-connect,
"Authentication URI parameters"). The token body's shape comes from the
fixture and the id token's claims from the README beside it (Preconditions),
not this file; the `nonce` claim and its check come from that page alone,
because the Playground capture probably sends none. The Microsoft class
(`/common` authority, `login_hint`, the `xms_edov` optional claim the app
registration has to opt into:
https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference)
and the Dropbox class (`https://www.dropbox.com/oauth2/authorize` with
`openid email`; Dropbox calls its OIDC support a developer preview that is
safe for production, and team-scoped apps cannot request it:
https://developers.dropbox.com/oidc-guide) are `T-098`'s and `T-096`'s.

```php
namespace App\Services;

class VendorIdentityService
{
    /** ['provider' => string, 'state' => string, 'nonce' => string, 'destination' => ?string] */
    public const SESSION_KEY = 'identities.oauth';
    /** Seconds the Peer's code exchange may take inside the landing: as long as a creator's connect (T-044, D-034). Provisional. */
    public const REQUEST_TIMEOUT_SECONDS = 10;
    /** Accesses whose ensureFor() runs inside the finalise request; the rest wait for the next trigger. Provisional. */
    public const BACKFILL_INLINE_LIMIT = 3;

    /** @param iterable<ConfirmsPeerIdentity> $providers */
    public function __construct(private iterable $providers, private CurrentGroup $current, private VendorAccessService $vendorAccess) {}

    /** The providers whose class is bound, in IdentityProvider::cases() order: what /u/identities offers. @return list<IdentityProvider> */
    public function offered(): array;
    /**
     * Mints state and nonce, Str::random(40) each, stores SESSION_KEY, returns the vendor URL with the person's email as
     * the login hint. Throws unsupported (errors.identities.unsupported, :vendor) when no class is bound.
     */
    public function beginConfirmation(User $user, IdentityProvider $provider, string $redirectUrl, ?string $destination): string;
    /** The destination SESSION_KEY holds, read without spending it; null when there is none. */
    public function pendingDestination(): ?string;
    /**
     * The landing. Pulls SESSION_KEY first, spent whatever happens next (PaymentsService.php:101-112); $back is its
     * destination ?? route('identities.edit'). Resolves the provider's class (unsupported when none is bound). Hands the
     * class $landing, the entry's state and nonce when the entry's provider is $provider and '' for both otherwise,
     * $redirectUrl and REQUEST_TIMEOUT_SECONDS, then maps the status:
     *   Confirmed       → updateOrCreate on (user_id, provider) with subject, tenant, email lowercased, email_verified_at
     *                     and confirmed_at now; $replaced is true when a row existed with a different subject or tenant;
     *                     backfill(); returns the row.
     *   Declined        → null; nothing written.
     *   UnverifiedEmail → AppException::invalidRequest('errors.identities.email_unverified', …).
     *   NotFromQori     → AppException::forbidden('errors.identities.state', …).
     *   Failed          → AppException::make(ErrorCode::UpstreamUnavailable, 'errors.identities.vendor_failed', …,
     *                     upstream: $landing->upstream).
     * Every refusal, unsupported included, carries ['vendor' => identities.providers.<provider>.name] and
     * ->redirectTo($back), and writes nothing.
     *
     * @param  array<string, mixed>  $landing
     */
    public function finaliseConfirmation(User $user, IdentityProvider $provider, array $landing, string $redirectUrl): ?VendorIdentity;
    /** Deletes the row; grants are untouched (Decisions). */
    public function remove(User $user, VendorIdentity $identity): void;
    /** The identities the Series' Active containers need, deduplicated, read inside the Series' Group. @return list<IdentityProvider> */
    public function neededFor(Series $series): array;
    /** Those of neededFor() the person holds no verified row for. @return list<IdentityProvider> */
    public function missingFor(Series $series, User $user): array;
    /**
     * Every active Access of the person, newest first, each inside its Group: identityConfirmed(); then ensureFor()
     * for the first BACKFILL_INLINE_LIMIT Accesses that had a row moved. Never throws; a failure is logged with the
     * access id and the loop continues.
     */
    private function backfill(User $user, IdentityProvider $provider, bool $replaced): void;
    private function providerFor(IdentityProvider $provider): ConfirmsPeerIdentity;
}
```

`neededFor()` runs `SeriesContainer::query()->where('series_id', …)->where('status', Active)`
inside `$this->current->runFor($series->group, …)`, because a Series reached
through `Series::findForPeer()` or `findPublic()` sits outside any Group
context and the container model is group-scoped. `backfill()` iterates
`Access::forUser($user)->orderByDesc('created_at')->get()`, resolves
`$access->grantedSeries()`, and inside `runFor($series->group, …)` calls
`$this->vendorAccess->identityConfirmed($access, $provider, $replaced)`, then
`ensureFor($access)` while the inline limit lasts. Rows past the limit are
`pending` and due now, for the Series page, Open and `qori:access:reconcile`.

```php
namespace App\Support;

/**
 * What a Series' storage needs from a Peer before they pay or open it (D-021): the lines under
 * accesses.vendor.<provider>.before_buying, common first, then the Group's tier. Provider tasks
 * write the lines and the config keys they interpolate; this class finds and fills them, decides
 * nothing, and names no vendor (CLAUDE.md, D-022).
 */
class BuyerRequirements
{
    /**
     * Rendered lines, ready to list. Empty for a Series with no Active container (Vimeo, YouTube,
     * Qori-hosted, a pasted link) and for a provider with no before_buying lines.
     *
     * @return list<string>
     */
    public static function for(Series $series): array;
    // [] when $series->group is null. Inside app(CurrentGroup::class)->runFor($series->group, …):
    // $held = SeriesContainer::query()->where('series_id', $series->getKey())->where('status', SeriesContainerStatus::Active)->pluck('provider');
    // foreach (ConnectionProvider::cases() as $provider) — the enum's order, so two providers list the same way every time — when $held contains it:
    //   $tier = Connection::query()->where('provider', $provider)->first()?->tier();       // null: common lines only
    //   $facts = array_filter((array) config("qori.connections.{$provider->value}", []), fn (mixed $value): bool => is_int($value) || is_string($value));
    //   foreach (array_filter(['common', $tier?->value]) as $block):
    //     $prefix = "accesses.vendor.{$provider->value}.before_buying.{$block}";
    //     foreach (array_keys(is_array($found = Lang::get($prefix)) ? $found : []) as $key):   // the lang file's order
    //       $lines[] = app(Terminology::class)->line("{$prefix}.{$key}", [...$facts, 'creator' => $series->group->name], $series->group);
}
```

A config key is its placeholder's name: `T-044`'s
`qori.connections.google_drive.free_storage_gb` fills `:free_storage_gb` in any
Google Drive line that names it, and an entry that is not an integer or a
string is never passed, since `Lang::get()` cannot fill a line with an array.
`:creator` is the Group's name, as the prompt's lines pass it. `SeriesContainer`
and `Connection` are both group-scoped, so the reads sit inside `runFor()` for
the reason `neededFor()` does; nothing crosses a scope.

```php
// App\Services\VendorAccessService — added to T-091's class
/**
 * The Peer confirmed or changed the identity $provider needs. For each of this Access's rows whose container's
 * provider maps to $provider through IdentityProvider::forConnection(): awaiting_identity → pending (attempts 0,
 * next_attempt_at null, last_error_code null); when $replaced, a granted or awaiting_acceptance row → revoke() the
 * stored vendor_ref best-effort with REQUEST_TIMEOUT_SECONDS (a failure is logged, not retried — D-016), then
 * pending as above; needs_creator and revoked rows untouched. Never writes granted. Inside the Access's Group
 * context; never throws. Returns the rows moved.
 */
public function identityConfirmed(Access $access, IdentityProvider $provider, bool $replaced): int;

// T-091's stub, filled:
protected function identityFor(User $user, ConnectionProvider $provider): ?\App\Data\GrantIdentity
{
    $needed = IdentityProvider::forConnection($provider);

    return $needed === null ? null : VendorIdentity::verifiedFor($user, $needed)?->toGrantIdentity($provider);
}
```

```php
namespace App\Http\Controllers\Settings;

class IdentitiesController extends Controller
{
    public function __construct(private VendorIdentityService $identities) {}
    /**
     * settings/Identities: rows [{id, provider, vendor, email, confirmedAt}]; providers [{provider, vendor, for, beginUrl}],
     * one per offered() provider and none for a provider whose class is not bound; copy.
     */
    public function edit(Request $request): Response;
    /** Inertia::location($this->identities->beginConfirmation(user, $vendor, route('identities.finalise', $vendor), $request->destination())). */
    public function begin(BeginIdentityRequest $request, IdentityProvider $vendor): Response;
    /**
     * $destination = pendingDestination() ?? route('identities.edit'), read first because finaliseConfirmation() spends
     * the entry; then finaliseConfirmation(user, $vendor, $request->query(), route('identities.finalise', $vendor)).
     * A row → toast identities.confirmed with :email and :vendor; null → toast identities.declined with :vendor;
     * either way redirect to $destination. A refusal is the service's AppException, which redirects itself. Reads no
     * word of the query: those are the vendor's (D-022).
     */
    public function finalise(Request $request, IdentityProvider $vendor): RedirectResponse;
    /** The row must be the signed-in person's, else notFound errors.identities.not_found. Toast identities.removed. */
    public function destroy(Request $request, string $identityId): RedirectResponse;
}

// App\Http\Requests\Settings\BeginIdentityRequest
// rules: ['destination' => ['nullable', 'string', 'max:2048', 'regex:/^\/(?!\/)/']]  — a path on this origin, never a URL
// public function destination(): ?string;
```

`{vendor}` binds implicitly to the enum on the route (`IdentityProvider
$vendor`), so an unknown value is a 404 with no code of this task's. Its three
values, `google`, `microsoft` and `dropbox`, have no underscore, so the stored
value is already the URL's word and needs no slug. It is not `{provider}`,
which `D-033` reserves for a `ConnectionProvider` slug that `T-044` binds for
every route: under that name `google` and `microsoft` would be a 404, since no
connection has either slug, and `dropbox` would be bound to
`ConnectionProvider::Dropbox`, which the action's `IdentityProvider` cannot
take. `destroy` takes an id, as every write does. Every action reads the
person through `CurrentUser::orFail($request)`
(`tests/Feature/ArchitectureTest.php:107-115`). `Identities.vue` renders the
rows, or `identities.none` when there are none, and then one line per
`providers` entry with its button: `identities.connect`, or
`identities.change` for a provider the person already holds.

**`SharedController::show()`** takes `VendorIdentityService` by method
injection and adds one prop after `deletion`
(`app/Http/Controllers/Shared/SharedController.php:150`):
`'identity' => null` when `neededFor($model)` is empty, else
`['missing' => [...], 'confirmed' => [...], 'requirements' => ?array]`. A
`missing` entry is
`['provider', 'vendor', 'title', 'body', 'action', 'beginUrl', 'destination']`
with `title`, `body` and `action` from the Copy table through
`Terminology::line()` (`app/Support/Terminology.php:89-97`) with
`'creator' => $model->group?->name`, `beginUrl` `route('identities.begin', $provider)`
and `destination` `route('shared.show', $model->getKey(), absolute: false)` — the
Series page, `D-020`'s return path. A
`confirmed` entry is `['provider', 'vendor', 'email', 'line', 'change', 'manageUrl']`
with `line` from `identities.open_with` and `manageUrl` `route('identities.edit')`.
`requirements` is `['title' => identities.requirements.title, 'lines' => BuyerRequirements::for($model)]`
while `missing` is non-empty and the lines are not, else null.
`Show.vue` renders, between the deletion notice
(`resources/js/pages/shared/Show.vue:144-153`) and the progress block
(`:155`), one block with `id="access"` holding `SeriesRequirements` when
`requirements` is set and then `IdentityPrompt` for each `missing` entry; the
`confirmed` lines sit above the Episode `Panel` (`:192`); titles stay listed
either way. The grant row behind a prompt sits at `awaiting_identity`, whose
sentence `T-091` renders in its notice as
`shared.vendor_notice.reasons.awaiting_identity` and says is replaced by this
prompt (`T-091`, Copy). `show()` still passes `T-091`'s `vendor` prop
unchanged, because the Open controls `T-091` disables while a grant is not
`granted` read that state (`D-020`); `Show.vue` renders `T-091`'s notice only
while `identity.missing` is empty, so one sentence shows, not two, and one
element carries `id="access"` at a time.

**`PublicSeriesController::show()`** adds `'identity'` in the same shape,
without `requirements`, for
a signed-in, not-granted viewer (`app/Http/Controllers/PublicSeriesController.php:50`,
`:112-116`) of a priced Series, with `destination` the public page's own path;
null otherwise. It also adds `'requirements'`: for a priced Series and a
viewer who is not granted, signed in or not,
`['title' => identities.requirements.title, 'lines' => BuyerRequirements::for($model)]`
when the lines are not empty; null otherwise, and so null for a free Series,
a granted viewer and a Series with no container. Both titles go through
`Terminology::line()` with the Series' Group. `Series.vue` renders
`SeriesRequirements` beside the buy button — directly above the three-state
block (`resources/js/pages/public/Series.vue:180-186`) in the page's single
column, below the deletion and cancelled notices, for the reason the deletion
notice gives for sitting above the buttons (`:161-165`) — and renders
`IdentityPrompt` with `identities.prompt.before_paying` in place of the buy
form (`:195-240`) while `missing` is non-empty, so the list stays above the
prompt. `SeriesRequirements.vue` takes `{ title, lines }` and renders the
title and a list; it holds no English. **`CheckoutController::store()`** and
**`SeriesAccessController::verify()`** call `missingFor($model, $peer)` before
`begin()` and, when it is non-empty, redirect to `series.public` instead —
signed in, so the page shows the prompt; the free branch of `verify()` is
unchanged. `IdentityPrompt.vue` is one component: a `Form` posting to
`beginUrl` with a hidden `destination`, the `title`, `body` and one button.

**`HandleInertiaRequests::share()`** adds
`'settingsNav' => ['identities' => __('identities.nav')]` after `sidebarOpen`
(`app/Http/Middleware/HandleInertiaRequests.php:191`),
**`resources/js/types/global.d.ts`** adds `settingsNav: { identities: string };`
to `sharedPageProps` after `sidebarOpen` (`:23`), and
**`Layout.vue`** gains a sidebar item after Security whose title is
`usePage().props.settingsNav.identities` and whose `href` is the generated
`edit` from `@/routes/identities`; `qori:reachability` reads it there.

## Copy

| Key                                             | File                     | English                                                                                                                                                   |
| ----------------------------------------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `identities.title`                              | `lang/en/identities.php` | Connected accounts                                                                                                                                        |
| `identities.intro`                              | `lang/en/identities.php` | The accounts you open shared :series_plural with. Qori keeps the address it confirmed and nothing else: no files, no password.                            |
| `identities.nav`                                | `lang/en/identities.php` | Connected accounts                                                                                                                                        |
| `identities.providers.google.name`              | `lang/en/identities.php` | Google                                                                                                                                                    |
| `identities.providers.google.for`               | `lang/en/identities.php` | Google Drive                                                                                                                                              |
| `identities.providers.microsoft.name`           | `lang/en/identities.php` | Microsoft                                                                                                                                                 |
| `identities.providers.microsoft.for`            | `lang/en/identities.php` | OneDrive                                                                                                                                                  |
| `identities.providers.dropbox.name`             | `lang/en/identities.php` | Dropbox                                                                                                                                                   |
| `identities.providers.dropbox.for`              | `lang/en/identities.php` | Dropbox                                                                                                                                                   |
| `identities.connect`                            | `lang/en/identities.php` | Sign in with :vendor                                                                                                                                      |
| `identities.change`                             | `lang/en/identities.php` | Use a different :vendor account                                                                                                                           |
| `identities.remove`                             | `lang/en/identities.php` | Remove                                                                                                                                                    |
| `identities.row`                                | `lang/en/identities.php` | :vendor — :email, confirmed :date                                                                                                                         |
| `identities.none`                               | `lang/en/identities.php` | Nothing here yet. You are asked to sign in the first time you open :series_plural kept in one of the services below.                                      |
| `identities.confirmed`                          | `lang/en/identities.php` | :vendor account confirmed: :email.                                                                                                                        |
| `identities.declined`                           | `lang/en/identities.php` | Nothing was connected. You can sign in with :vendor whenever you like.                                                                                    |
| `identities.removed`                            | `lang/en/identities.php` | :vendor account removed.                                                                                                                                  |
| `identities.prompt.title`                       | `lang/en/identities.php` | One step before this :series opens                                                                                                                        |
| `identities.prompt.body.google`                 | `lang/en/identities.php` | :creator keeps this :series in Google Drive. Sign in with the Google account you will open it with, and Qori lets that account in.                        |
| `identities.prompt.body.microsoft`              | `lang/en/identities.php` | :creator keeps this :series in OneDrive. Sign in with the Microsoft account you will open it with, and Qori lets that account in.                         |
| `identities.prompt.body.dropbox`                | `lang/en/identities.php` | :creator keeps this :series in Dropbox. Sign in with the Dropbox account you will open it with, and Qori invites that account to the folder.              |
| `identities.prompt.action`                      | `lang/en/identities.php` | Sign in with :vendor                                                                                                                                      |
| `identities.prompt.before_paying`               | `lang/en/identities.php` | Do this before you pay. Qori starts letting that account in as soon as your payment goes through, and the :series page shows anything left for you to do. |
| `identities.requirements.title`                 | `lang/en/identities.php` | What you need for this :series                                                                                                                            |
| `identities.open_with`                          | `lang/en/identities.php` | Open this :series with :email on :vendor. If your browser is signed in to a different :vendor account, switch to :email first.                            |
| `identities.open_with_change`                   | `lang/en/identities.php` | Not that account? Change it.                                                                                                                              |
| `errors.identities.state.message`               | `lang/en/errors.php`     | That sign-in did not start here.                                                                                                                          |
| `errors.identities.state.resolution`            | `lang/en/errors.php`     | Sign in with :vendor again from this page.                                                                                                                |
| `errors.identities.email_unverified.message`    | `lang/en/errors.php`     | :vendor has not verified the email on that account, so Qori cannot let it in.                                                                             |
| `errors.identities.email_unverified.resolution` | `lang/en/errors.php`     | Verify the address with :vendor, then sign in here again.                                                                                                 |
| `errors.identities.vendor_failed.message`       | `lang/en/errors.php`     | :vendor did not finish the sign-in.                                                                                                                       |
| `errors.identities.vendor_failed.resolution`    | `lang/en/errors.php`     | Try again in a moment.                                                                                                                                    |
| `errors.identities.unsupported.message`         | `lang/en/errors.php`     | Signing in with :vendor is not available yet.                                                                                                             |
| `errors.identities.not_found.message`           | `lang/en/errors.php`     | That account is not on your list.                                                                                                                         |

`:vendor` is always `identities.providers.<provider>.name`; `:creator` is the
Group's name. Vendor names appear here under `D-016`'s stated exception. Every
prompt line names the reader as who resolves it, and no line says access is
complete: for Dropbox the Join step and the storage check are `T-096`'s to
say, in `awaiting_acceptance`. No line names a moment the Series opens
either (`D-021`): `before_paying` says what payment starts and where to look
next. `errors.identities.unsupported` has no
resolution on purpose: the person cannot make a provider appear.
`identities.none` names no service, because the list beneath it is whatever
`offered()` holds (Decisions), and `errors.identities.state.resolution` names
no page, because every refusal lands back on the page the sign-in started
from, where the button is.

The lines under `identities.requirements.title` are not in this table. They
are `accesses.vendor.<provider>.before_buying.common.<key>` and
`accesses.vendor.<provider>.before_buying.<tier>.<key>` in
`lang/en/accesses.php`, `<provider>` a `ConnectionProvider` value and `<tier>`
a `ProviderTier` value, each a whole sentence about what the Peer needs — an
account on the address they will confirm, a step at the vendor, the space the
vendor takes from their own account — with numbers interpolated by key from
the provider's `qori.connections` block. `T-094` writes `google_drive`'s,
`T-096` `dropbox`'s, `T-098` OneDrive's, and `T-100` `zoom`'s only if Zoom
needs something from a registrant; the first of them to land opens the
`vendor` block in that file.
The article rule's walk (`tests/Feature/TerminologyTest.php:218-241`) covers
them there.

## Routes

| Verb   | Path                             | Name                  | Action                          |
| ------ | -------------------------------- | --------------------- | ------------------------------- |
| GET    | `u/identities`                   | `identities.edit`     | `IdentitiesController@edit`     |
| POST   | `u/identities/{vendor}/begin`    | `identities.begin`    | `IdentitiesController@begin`    |
| GET    | `u/identities/{vendor}/finalise` | `identities.finalise` | `IdentitiesController@finalise` |
| DELETE | `u/identities/{identityId}`      | `identities.destroy`  | `IdentitiesController@destroy`  |

All four inside the `['auth', 'verified']` group of `routes/settings.php`
(`:63-77`): a Peer from the Series page is verified by the code
(`SeriesAccessController.php:123-127`), and nobody reaches `/shared` without
it (`routes/shared.php:31`). The finalise path is registered with each vendor
exactly, once per environment: Google's on the production client and the
local one (`docs/planning/vendor-accounts.md`, Google Drive, step 10).

## Tests

Every case binds the fake with
`$this->app->when(VendorIdentityService::class)->needs('$providers')->give(fn () => [$this->fake])`
and, where a grant is expected, `T-091`'s `GrantsEveryPeer` the same way,
scripted for the providers the case names; both call `Http::fake()`. `T-091`
builds that fake for the `ConnectionProvider` its constructor names (`Dropbox`
by default); a case here that also names `GoogleDrive` binds a second instance
built for it.
`ConfirmsAnyPeer` is built for the `IdentityProvider` its constructor names,
answers `beginConfirmation()` with a fixed URL carrying the state and nonce it
was given, answers `finaliseConfirmation()` with the `IdentityLanding` the
case scripted (`confirmed()` with a scripted `VendorIdentityData` unless told
otherwise), and records every argument each call was handed. The service's
cases therefore script a status and never a vendor word; the words are
`GoogleSignInTest`'s.

**New: `tests/Feature/Settings/IdentitiesTest.php` — 15 cases**

1. `test_the_page_lists_the_persons_identities_and_nobody_elses`
2. `test_the_page_is_reachable_from_user_settings` — the sidebar link resolves to `identities.edit` and its title is the shared `settingsNav.identities`.
3. `test_the_page_offers_only_the_providers_whose_sign_in_is_bound` — the fake bound for Google alone: `providers` is Google's entry and nothing else; bound for all three, three entries in `IdentityProvider::cases()` order.
4. `test_begin_answers_with_the_vendors_sign_in_url_and_remembers_the_round_trip` — `Inertia::location`; `SESSION_KEY` holds provider, a 40-character state, a 40-character nonce and `destination`; the fake was handed that state and nonce and the person's email as `$loginHint`.
5. `test_begin_refuses_a_destination_that_is_not_a_path_on_this_origin` — `https://…` and `//…` are 422.
6. `test_begin_is_a_404_for_a_provider_that_does_not_exist`
7. `test_begin_says_a_provider_with_no_sign_in_bound_is_not_available` — only Google bound; Microsoft → `errors.identities.unsupported`, `:vendor` filled.
8. `test_finalise_stores_the_identity_and_lands_where_it_started` — the fake was handed the request's query as `$landing`, the stored state and nonce, `route('identities.finalise', 'google')` and `VendorIdentityService::REQUEST_TIMEOUT_SECONDS`; row with `subject`, lowercased `email`, `email_verified_at`, `confirmed_at`; session key gone; redirect to `destination`; toast `identities.confirmed`.
9. `test_finalise_lands_on_the_page_when_no_destination_was_stored`
10. `test_finalise_refuses_a_landing_that_did_not_start_here` — the fake answering `notFromQori()`: redirect to the stored `destination` with the toast `errors.identities.state`; no row; key forgotten. With no round trip in the session, and with one for Microsoft, the fake was handed `''` as the expected state and nonce.
11. `test_finalise_refuses_an_unverified_email_and_stores_nothing` — the fake answering `unverifiedEmail()`: `errors.identities.email_unverified`, `:vendor` filled; redirect to `destination`; no row.
12. `test_a_failed_landing_says_the_vendor_did_not_finish_and_keeps_its_code` — the fake answering `failed('400')`: toast `errors.identities.vendor_failed`, `:vendor` filled; redirect to `destination`; the error reported with `upstream` `400`; no row; key forgotten.
13. `test_a_decline_stores_nothing_and_says_so` — the fake answering `declined()`: toast `identities.declined`; redirect to `destination`; no row; key forgotten.
14. `test_signing_in_again_replaces_the_identity_in_place` — one row, new `subject`, `confirmed_at` moved.
15. `test_removing_an_identity_deletes_the_row_touches_no_grant_and_refuses_another_persons` — a `granted` row stays `granted`; someone else's id is 404.

**New: `tests/Feature/Integrations/Google/GoogleSignInTest.php` — 6 cases**

A case that reaches the exchange answers `Http::fake()` with
`tests/Fixtures/google/oidc-token.json` as `T-093` captured it, but for
`id_token`, which is `REDACTED` there: a private helper builds that one field
from the claims `tests/Fixtures/google/README.md` records — `sub`, `email` and
`email_verified` as decoded, plus `aud` the case's
`services.google.client_id`, `exp` an hour ahead and the `nonce` the case
hands over, which the captured token cannot show (Preconditions) — encoded as
`base64url(header).base64url(payload).signature` with a signature segment of
any bytes, since `GoogleSignIn` checks none. Cases 19 and 20 change only the
one claim they name.

16. `test_the_authorize_url_asks_for_sign_in_scopes_only_and_hints_the_qori_email` — `scope=openid email`, no `drive.file`, no `access_type`, no `include_granted_scopes`, `login_hint`, `prompt=select_account`, the state and nonce given.
17. `test_it_reads_the_subject_and_email_from_the_token_response` — the landing's `state` and `code` against the fixture and the helper's token: `confirmed()` with the README's `sub` and `email`; the request carried `grant_type=authorization_code`, the code and `redirect_uri`; the fake callback's `$options['timeout']` is a budget shorter than `GoogleAccounts::TIMEOUT_SECONDS`, and that limit under a longer one; nothing returned holds a token.
18. `test_a_decline_or_a_landing_that_did_not_start_here_sends_nothing` — `error=access_denied` with the expected state or none → `declined()`; any `error` with another state → `notFromQori()`; `error=admin_policy_enforced` with the expected state → `failed('admin_policy_enforced')`; no `error` and a state missing, different, or expected as `''` → `notFromQori()`; the expected state and no `code` → `failed()`; `Http::assertNothingSent()` after each.
19. `test_an_unverified_email_is_answered_as_such` — the helper's token with `email_verified` false → `unverifiedEmail()`.
20. `test_an_id_token_not_minted_for_this_round_trip_fails` — the helper's token with another `nonce`, another `aud`, or an `exp` in the past → `failed('id_token')` each.
21. `test_a_failed_exchange_is_answered_as_failed_with_googles_code` — a 400 whose body's `error` is `invalid_grant` → `failed('400')`, and the log line carries `invalid_grant` and not the body; a 500 → `failed('500')`; a `ConnectionException` → `failed('connection')`; nothing thrown.

**New: `tests/Feature/Shared/IdentityPromptTest.php` — 7 cases**

22. `test_the_series_page_prompts_for_each_provider_the_series_needs_and_the_peer_lacks` — a Google Drive and a Dropbox container, one identity held; one `missing`, one `confirmed`; Episode titles still in the props; the `missing` entry's `destination` is the `shared.show` path (`D-020`); `vendor` still passed, as `T-091` sets it, so its disabled Open controls stay disabled.
23. `test_the_series_page_names_the_confirmed_email_instead_of_prompting`
24. `test_no_prompt_for_a_series_whose_episodes_need_no_identity` — a Series whose Episodes are on Vimeo and on Qori's storage, neither holding a container (`T-090`): `identity` null; and `IdentityProvider::forConnection()` answers null for `Vimeo`, `Zoom` and `Teams`.
25. `test_confirming_an_identity_grants_every_waiting_series_across_groups` — two Groups, two `awaiting_identity` rows; after `finalise`, both `granted` by the grant fake, each attempted inside its own Group.
26. `test_the_backfill_attempts_a_bounded_number_inline_and_leaves_the_rest_due` — `BACKFILL_INLINE_LIMIT + 1` Accesses; the oldest is `pending` with `next_attempt_at` null and the grant fake never saw it; `needs_creator` and `revoked` rows untouched.
27. `test_changing_the_identity_revokes_the_old_grant_and_grants_the_new` — `GrantsEveryPeer` saw `revoke()` with the old `vendor_ref`, then `grant()`, each with `VendorAccessService::REQUEST_TIMEOUT_SECONDS`; row `granted` with a new `vendor_ref`, `attempts` reset.
28. `test_a_vendor_failure_during_the_backfill_never_reaches_the_peer` — the grant fake throws; `finalise` still redirects and the identity is stored.

**New: `tests/Feature/Checkout/IdentityBeforeCheckoutTest.php` — 4 cases**

29. `test_the_buy_button_gives_way_to_the_prompt_while_an_identity_is_missing` — public page prop for a signed-in viewer of a priced Series with a Google Drive container.
30. `test_checkout_sends_a_buyer_without_an_identity_back_to_the_series_page` — no checkout session created; `CheckoutPending` not marked.
31. `test_the_code_sign_in_on_a_paid_series_lands_on_the_page_instead_of_stripe_while_an_identity_is_missing`
32. `test_a_free_series_grants_without_the_step_and_asks_on_the_series_page`

**New: `tests/Feature/Checkout/BuyerRequirementsTest.php` — 5 cases**

The `before_buying` lines are the provider tasks', so these cases register
their own through a private helper that reads one real `accesses` line first
and then calls `app('translator')->addLines()` with two `common` lines, one
`google_free` line and one `google_workspace` line under
`accesses.vendor.google_drive.before_buying`: `addLines()` on a group not yet
loaded marks it loaded and hides the real file
(`vendor/laravel/framework/src/Illuminate/Translation/Translator.php:350-392`).
The assertions compare against those registered lines.

33. `test_a_google_drive_series_lists_what_a_buyer_needs_beside_the_buy_button` — a priced Series with an `Active` `google_drive` container, the Group's connection on `google_free`; for a signed-out visitor and for a signed-in, not-granted viewer, the public page's `requirements.title` is `identities.requirements.title` and `lines` are the two `common` lines then the `google_free` line, in that order; no checkout session exists; `requirements` is null for a granted viewer.
34. `test_a_series_with_nothing_to_ask_renders_no_list` — a priced Series whose Episodes are on Vimeo and one whose Episodes are Qori-hosted, neither with a container: `BuyerRequirements::for()` is `[]` and `requirements` is null on the public page.
35. `test_a_tier_line_appears_only_for_that_tier` — the Series from case 33 with the Group's connection on `google_workspace`: the `google_workspace` line listed and the `google_free` line not; with no tier stored, the `common` lines alone.
36. `test_a_line_takes_its_numbers_from_its_providers_config_by_key` — the helper's lines and a third `common` line naming `:free_storage_gb` and `:creator`, with the case setting `qori.connections.google_drive.free_storage_gb` and an array entry in the same block: that line carries the number and the Group's name, and the array entry reaches no replacement.
37. `test_a_free_series_lists_the_lines_above_the_prompt_on_the_series_page` — a free Series with a `google_drive` container and a granted Peer with no Google identity: `shared.show`'s `identity.requirements.lines` are the lines from case 33 beside a non-empty `missing`; the public page's `requirements` is null, because the Series is free.

Total: 37.

**Changed:** none expected. `SharedController`, `PublicSeriesController`,
`CheckoutController` and `SeriesAccessController` gain a method-injected
service the container resolves. `ConsoleAccessTest`'s allow-list and
`ArchitectureTest` are untouched: nothing new calls `acrossAllGroups()`, and
`GoogleSignIn` imports no Service or controller
(`tests/Feature/ArchitectureTest.php:139-147`). The article rule in
`tests/Feature/TerminologyTest.php:218-241` walks the new lang file; no line
puts an article before a noun placeholder.

## Acceptance

- [ ] A person confirms a Google account by signing in with Google, once, and
      the row holds `sub`, the verified address and no token
- [ ] `GoogleSignIn` reads the landing — `error`, `state`, `code` and the id
      token — and answers an `IdentityLanding`; neither
      `IdentitiesController` nor `VendorIdentityService` reads a word of
      Google's (`D-022`)
- [ ] A Series page whose containers need an account the person has not
      confirmed asks above the Episode list and lists the titles; one that
      has it names the address to open with
- [ ] Confirming moves every `awaiting_identity` grant the person holds to
      `pending`, in every Group, attempts at most `BACKFILL_INLINE_LIMIT`
      inline, and leaves the rest due for the next trigger; changing the
      account regrants the new one after a best-effort revoke of the old
- [ ] A paid Series asks before the buyer reaches Stripe, and a free one
      grants first and asks on the Series page; a sign-in started on
      `shared.show` comes back to `shared.show`, and a Peer sent to
      `#access` lands on the prompt while one shows (`D-020`)
- [ ] A buyer sees what the Series' provider needs from them beside the buy
      button before paying, common lines first and then only their creator's
      tier; a free Series shows the same list above the prompt; a Vimeo,
      YouTube or Qori-hosted Series shows no list; and no line on either page
      promises the Series opens the moment payment goes through (`D-021`)
- [ ] An unverified address, a mismatched state, a vendor timeout and a
      decline store nothing, land back where the sign-in started, and each
      say who can resolve it
- [ ] The page under `/u/identities` lists, adds and removes the person's own
      accounts and nobody else's, offers only the sign-ins that are built,
      and its sidebar title is not inline
- [ ] One Google sign-in walked in a browser as `T-093`'s `peer-gmail`, from
      `shared.show` back to `shared.show`, its token response shaped as the
      fixture is
- [ ] `docs/flows/vendor-access.md`, `checkout.md`, `accesses.md`,
      `docs/architecture/tenancy.md` and the tinker recipe describe what was
      built
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~Ask for the vendor account before checkout on the Series page, or only
  after payment on `shared.show` — the owner's.~~ Answered 16 September 2026:
  `docs/planning/streams/storage.md` (priority 1, and its line for this task)
  says confirmed before payment, and `D-016` calls it a prerequisite.
- ~~`tests/Fixtures/google/oidc-token.json` — the id-token exchange for the
  Peer's Google sign-in — has no owner: `T-093` puts that sign-in out of its
  scope and its fixture set does not list it, though its Playground client
  and `peer-gmail` profile could produce it in one extra step. Add that step
  to `T-093` (a wording change to that draft) or make a spike this task's
  first step — anyone's, with `T-093`.~~ **Answered 19 September 2026:**
  `T-093` produces it, in its step 2, as `peer-gmail` through the Playground,
  with the id token `REDACTED` and its claims recorded decoded in
  `tests/Fixtures/google/README.md`; the tests build their id token from
  those claims and supply the `nonce` the capture cannot show
  (Preconditions, Tests).
- ~~Whether an address with no Google account is refused loudly or accepted
  silently at grant time (`T-093` step 12) decides whether
  `identities.prompt.body.google` has to say "a Google account on any
  address" — anyone's, with `T-093`, whose step answers it.~~ **Answered
  19 September 2026:** not this task's. A confirmed identity is a Google
  account by construction, since it comes from signing in with Google, and
  the grant goes to that account's address, so step 12's answer reaches only
  what a Peer with no Google account reads before buying, which is `T-094`'s
  `before_buying` line.
- Whether `xms_edov` arrives for personal Microsoft accounts through
  `/common`, and whether `tenant` matters for a personal-versus-work OneDrive
  grant — `T-097`'s; the column is kept nullable either way.
- Whether Dropbox's OpenID Connect sign-in is acceptable in production for a
  scoped app, whether a Peer with an unverified Dropbox email should be
  stored and told, or refused as here, and whether a Peer's sign-in counts
  towards the 50 linked accounts after which Dropbox freezes an app awaiting
  production approval (`docs/planning/vendor-accounts.md`, Dropbox, "Do this
  first"), which would argue for a typed address for Dropbox alone against
  this draft's sign-in rule — `T-095`'s, for `T-096`.
- ~~`T-091`'s `App\Data\VendorIdentity` and this task's
  `App\Models\VendorIdentity` share a basename. Keep both, with the model
  producing the Data shape as written here, or have `grant()` take the model
  (the layer rule allows Models in) — anyone's, with `T-091`, which lists
  the same bullet.~~ **Decided 19 September 2026:** `T-091` renames its shape
  `App\Data\GrantIdentity`; `App\Models\VendorIdentity` stays, and its
  `toGrantIdentity()` produces the shape `grant()` takes (Code).
- ~~`T-091`'s `VendorGrantStatus` has `failed` where the stream's shared
  vocabulary has `awaiting_acceptance` and `needs_creator` — anyone's, with
  `T-091`.~~ Answered 16 September 2026: `T-091`'s enum now carries the six
  shared cases, and this draft's state moves are written against them.
- ~~`T-044` names `services.google.client_id` and `client_secret` and says this
  task registers `u/identities/google/finalise` as a second redirect URI on the
  same Web client (`T-044`, Code); whether that client's consent screen, set
  to `drive.file` alone under `T-044`, also carries `openid` and `email`, or
  the Peer sign-in needs its own client — anyone's, with `T-044` and
  `T-093`'s report.~~ **Answered 19 September 2026:**
  `docs/planning/vendor-accounts.md`, Google Drive, steps 9 and 10: the one
  project declares `drive.file`, `openid` and `userinfo.email`, and the one
  Web client registers `u/identities/google/finalise` beside
  `u/connections/google/finalise`, as the local client does for localhost.
  `GoogleSignIn` asks for `openid email` alone and sends no
  `include_granted_scopes`.
- `BACKFILL_INLINE_LIMIT` at 3, and so how long the landing may keep a Peer
  waiting: the exchange (`REQUEST_TIMEOUT_SECONDS`, 10 seconds), then for
  each of three Accesses a renewal of the creator's token when it is within
  `T-044`'s `REFRESH_MARGIN_MINUTES` of expiring, a best-effort revoke when
  the account changed, and a grant, each at
  `VendorAccessService::REQUEST_TIMEOUT_SECONDS` (5 seconds; `T-091` passes
  the same budget to `fresh()`). That is 55 seconds at worst, 10 and three
  times 15, when each Series holds the one container that needs the account.
  `ensureFor()` attempts every due row on an Access (`T-091`), so each other
  container with a row due on those Series adds a call or two at 5 seconds
  each — the owner's, with `T-093`'s observed timings, until which `D-034`
  keeps all three numbers provisional.
- Whether the sidebar item and page title read "Connected accounts" or the
  owner prefers another word — the owner's, on reading the Copy table. A
  creator who is also a Peer already has the Group's Integrations page for
  connections, and may read this one as the place to connect Drive.
- ~~`BuyerRequirements` reads `series_containers` and `connections` from
  `app/Support`, where `CLAUDE.md` keeps stateless static helpers; `T-044`'s
  `ProviderSections` reads connections from there too. Keep both, or move
  both behind a Service method — anyone's, with `T-044`.~~ **Answered
  19 September 2026:** for this task's class, `CLAUDE.md` now lets
  `app/Support` hold helpers with per-request state and bars only what is
  vendor-specific, and `SignInLanding` already reads models there; what broke
  the rule was `factsFor()`'s per-provider arms (`D-022`). `BuyerRequirements`
  stays and loses `factsFor()`: its replacements are the provider's
  `qori.connections` entries by key (Decisions, Code). `ProviderSections` is
  `T-044`'s to settle.
- **From the privacy and terms drafts (`docs/pptcs/`, 19 September 2026):**
  Google's APIs Terms s.5(c) need explicit opt-in before a person's non-public
  data is shown to other users. A confirmed Google account is visible to the
  creator and possibly to other people with access to the folder, so the
  confirmation step should say so and ask for an affirmative yes. The copy
  and whether the step records that agreement — anyone's, before `ready`.
- ~~Rewrite the landing to the vendor-folder pattern `D-022` and `D-023` set
  after this draft was written: the controller read `error=access_denied`,
  the service compared the state, and `ConfirmsPeerIdentity` took a bare
  code (the readiness audit of 19 September 2026) — anyone's.~~ **Decided
  19 September 2026:** `ConfirmsPeerIdentity::finaliseConfirmation()` takes
  the landing, the expected state and nonce, the redirect URL and a budget,
  and answers an `IdentityLanding`, as `SellsSeries::finaliseOnboarding()`
  does for Stripe; the controller passes `$request->query()`, and the
  service maps each status (Decisions, Code).
- `T-091` and `T-044` `ready` first, so the names quoted here from them are
  frozen when this one is: `GrantIdentity`, `ensureFor()`, `identityFor()`,
  `REQUEST_TIMEOUT_SECONDS`, `GrantsEveryPeer`,
  `ConnectionProvider::GoogleDrive`, `ProviderTier`, `Connection::tier()`,
  `ConnectionService::fresh()`, `GoogleAccounts::TIMEOUT_SECONDS`,
  `services.google.*` and the `qori.connections` block. Re-read both then —
  anyone's, with `T-091` and `T-044`.
- A Peer whose Google Workspace administrator blocks Qori comes back with
  Google's `admin_policy_enforced` (or `org_internal`), which `IdentityLanding`
  has no status for, so the Peer would read the generic failure. Whether it
  gains an `AdminBlocked` status with its own copy, as `T-044`'s
  `ConnectionLanding` has, waits on `T-093`'s Workspace pass showing what
  arrives — anyone's, after the spike.

### From the storage review, 20 September 2026

- **Identity discovery reads containers, so Drive asks for nothing** (`F03`).
  `neededFor()` is specified over the Series' active `SeriesContainer` rows
  and `D-036` leaves Drive with none, so a Drive-only Series shows no
  prerequisite before payment, none on the Series page, and
  `identityConfirmed()` never releases its `awaiting_identity` rows because
  it filters by the row's container provider. It has to read the targets that
  grant, whatever their shape, and the Google test arrangements have to stop
  creating fictitious Drive containers to pass — anyone's.
- **Changing or removing an identity loses the old permission** (`F04`). A
  failed revoke of the old account is logged without retry, the same row is
  reset to pending, and a successful grant to the new account overwrites
  `vendor_ref`, so nothing can find the old permission again. Removing an
  identity and then confirming another leaves `$replaced` false, the granted
  rows bound to the old account, and a check answering `granted` while the
  Peer cannot open. Keep the settled choice that removing an identity does
  not cancel a purchase; store the principal each generation actually
  granted — anyone's.
- **A cached address is not a binding to the confirmed account** (`F04`).
  The saved subject is stable but grants use the saved email indefinitely,
  and a Workspace address that is renamed and reassigned would send a later
  grant to whoever holds it now. Neither the fixtures nor the documentation
  settle this; it needs an identity probe of its own — the owner's, whether
  to spike it before release.

## Re-scope log

None.

## Notes

The blueprint's citations were written a day earlier and several moved or
were approximate: the public controllers are `app/Http/Controllers/*.php`, not
`app/Http/Controllers/Public/*.php`; `EmailChangeService.php:15-29` is the
class docblock and the methods are `:42-106`; the Series code check is
`SeriesAccessController.php:112-121` inside `verify()` (`:103-162`);
`Access::forUser()` is `:253-259`. The brief for this draft named Dropbox's
sign-in scope as `account_info.read`; that is the scope for
`users/get_current_account`, which returns the same `account_id`, `email`
and `email_verified` but needs an access token to call and revoke, whereas
the OpenID Connect sign-in returns them in the id token with nothing to keep
(https://developers.dropbox.com/oidc-guide), which is why `openid email` is
written here. When this draft was written `CLAUDE.md` said integrations
expose `name()` and are bound in `AppServiceProvider`; it now says
`provider()` and `IntegrationServiceProvider`, as the code does. There is no
`resources/js/components/shared/`; the prompt component sits in
`components/series/`, beside `SeriesProgress.vue`, which both Series pages
already import from.

Sibling drafts this one leans on: `T-091`'s Copy puts the Peer's grant-state
sentences under `shared.vendor_notice.reasons.*` in `lang/en/shared.php`,
which `T-089` creates for its redirect flash — the disagreement the two drafts
had on 16 September 2026 was settled by `D-020` on 17 September 2026, and
this task's copy is in `identities.php` either way. `T-043`'s acceptance lands on
`shared.show` on purpose so it meets this prompt (`T-043`, Before this can be
ready). `T-096` and `T-098` now carry `depends: T-092`, so the `blocks:`
line above is what the board derives. Their `DropboxSignIn` and
`MicrosoftSignIn` are sketched against this contract as it stood before
19 September 2026 — a bare code in, and a verified flag on
`VendorIdentityData` — and take the landing, `IdentityLanding` and
`UnverifiedEmail` when they are specified. `T-096`'s Dropbox allowance fills
`:gigabytes` through a `factsFor()` arm this draft no longer has; its line
names its config key instead, `:basic_storage_gb`, or the key takes the
placeholder's name.

Split: `T-091` holds every grant; this task is the identity and Google's
sign-in; `T-096` and `T-098` each add one sign-in class against their
spike's fixture, and `T-094` is the first journey to use Google's.
