---
id: T-089
title: Open is a link to a Qori route that sends the Peer to the vendor
stream: storage
status: done
owner: wayne
estimate: M
depends: none
blocks: T-090, T-091, T-125
---

# T-089 — Open is a link to a Qori route that sends the Peer to the vendor

> Set `ready` by the stream owner on 19 September 2026, every question that
> kept it a draft answered or moved to the task that owns it.
> Written on 16 September 2026 from `D-016` and the owner's BYO blueprint;
> amended on 17 September 2026 from `D-020`: a link Qori will not follow yet
> redirects to the Series page's access notice, and there is no page of its
> own. Amended on 18 September 2026 by `D-024` and `D-026`: the live arm of
> this route is `T-125`'s — a live Episode answers a `VendorLink` to its
> `join_url` inside the join window, and `T-126` adds `?recording={id}` on the
> same route for a recording — and every classroom email, calendar file and
> copied message is minted against the stable `shared.episodes.show` address
> `T-125` adds, not against this route; this task itself still builds no live
> Open control. Every path and line below re-checked against the code on
> 19 September 2026: `T-113` had already shipped the 502 page this task was to
> add, so it adds none; `T-111` named Qori's own storage `cloudflare_r2`
> (`D-022`); the Vimeo check moved off `EpisodeProvider`, which the ready
> `T-123` edits, into `SharedController::opensAs()`; and the browser check is
> narrowed to a Qori-hosted Episode.

## Why

Opening an Episode on the Peer's page is a click that can do nothing.
`resources/js/pages/shared/Show.vue` `openEpisode()` (`:82-113`) awaits a
`fetch` of the JSON play route (`:87-90`) and then calls
`window.open(link.url, '_blank', 'noopener')` (`:106`). A popup opened after
an `await` can lose the click's user activation and be blocked, and `noopener`
makes `window.open` return `null` whether it was blocked or not, so a blocked
tab is indistinguishable from an opened one and nothing on the page offers the
link a second time; the only other output is the `<iframe>` for an embed
(`:254-264`). Underneath, `ResolvesMedia::linkFor(Episode, ?Connection)`
(`app/Integrations/Contracts/ResolvesMedia.php:34`) never receives the Peer,
so nothing on this path could ever make a per-Peer grant (`D-016`).

Afterwards, Open is a plain `<a target="_blank">` whose `href` is a Qori
route. That route passes the gate `PlaybackTicketService::issue()` passes
today — access, then the Episode, then `ProgressService::opened()` — and
answers with a 302: to the signed URL for a Qori-hosted Episode, to the vendor
for anything else. `T-091` puts its ensure-the-grant step into this route,
between the gate and the redirect, so that Open re-reads the stored permission
before trusting a `granted` row and answers `VendorLink::blocked()` for a row
that is not. This route turns that answer into a redirect to the Series page at
its access notice, which holds the next step, with a one-line flash saying why
the Peer landed there (`D-020`). `T-125` adds the live arm, a `VendorLink`
to a live Episode's pasted `join_url` inside its join window (`D-024`,
`D-026`), and `T-090`, `T-094`, `T-096`, `T-098` and `T-100` then swap in each
vendor's own link.

## Decisions taken to make this specifiable

**The route is `shared.episodes.open`, a GET sibling of `shared.play`, and its
parameters are named for what they carry.**
`GET /shared/{seriesId}/episodes/{episodeId}/open`, beside
`routes/shared.php:42`. Ids, because every Peer route takes ids (the file's
header, `:21-25`); named `{seriesId}` and `{episodeId}` as the progress routes
are (`:47-50`), not `{series}` and `{episode}` as the play route is — that
naming goes when `T-090` removes the play route.

**A new invokable `OpenEpisodeController`, not a second action on
`PlaybackController`.** `PlaybackController`'s whole docblock is about
answering JSON (`:11-19`); the two responses differ in kind, and `T-090`
deletes the JSON one.

**One gate, shared; each caller records the open.** `issue()` and the new
`open()` both call a private `admit()` that does the access check
(`PlaybackTicketService.php:46-56`) and the Episode lookup (`:58-64`), and
each then calls `ProgressService::opened()` (`:70`) itself. Recording stays
outside the gate so `T-091` can put its ensure step between the two in
`open()` without reopening the gate. **The redirect records the Episode as
opened before the link is resolved**, exactly as play does — a vendor that
fails after the gate still counts as an open.

**`open()` returns `MediaLink|VendorLink`.** A Qori-hosted Episode
(`EpisodeProvider::isQoriHosted()`, `app/Enums/EpisodeProvider.php:28-31`)
keeps its `MediaLink` ticket: `D-016` says nothing about Qori's own storage
changes, and `D-022` only renamed it `cloudflare_r2`. Everything else is
wrapped in a new `App\Data\VendorLink` with **no expiry** — the vendor's own
permission governs access, and Qori's part is deciding whether to send the
person there. `VendorLink` carries a nullable url, the provider, a nullable
`accountHint` and a nullable `blockedState`. `accountHint` stays null in this
task: each provider's `openLink()` fills it from the Peer's confirmed identity
(`T-094`, `T-096`, `T-098`, through `T-092`'s `VendorIdentity::verifiedFor()`),
and whether a vendor URL carries it — Google's `authuser` — waits on `T-093`'s
Q6 and is `T-094`'s. **`VendorLink::blocked($state, $provider)` is the answer
when Qori decided not to send the person**: no url, and the grant state
`open()` read, as `T-091`'s `VendorGrantStatus` value — a string here, because
that enum is `T-091`'s and does not exist when this task lands. It is the
outcome of one read, not a flag kept beside the grant: who has to act on a
grant that is not usable is the grant row's state — `awaiting_identity` and
`awaiting_acceptance` are the Peer's to resolve, `pending` is Qori's retry and
`needs_creator` is the creator's — `T-091` reads it before `openLink()` is ever
called, and the Series page's notice reads the same row, so a `needsJoin` flag
on a link that can be followed would be a second copy of one fact. In this
task `VendorLink::fromMediaLink()` wraps what the existing resolvers return,
so Dropbox behaviour is unchanged and only the transport is new; `T-091`
replaces that branch with the grant contract's `openLink()` and is the first
caller of `blocked()`.

**The interim Dropbox call is kept as it is, timeout included.** The vendor
branch still fetches `files/get_temporary_link` with the creator's token and
a 15-second timeout (`app/Integrations/Dropbox/DropboxStorage.php:49-52`),
which `D-016` supersedes and `T-096` replaces. `T-091`'s
`VendorAccessService::REQUEST_TIMEOUT_SECONDS` bounds the ensure step it adds
to this route, not this call. The 15 seconds is the Dropbox client's own
limit, which is where `D-034` puts a vendor's timeout, and `linkFor()` takes
no `$timeoutSeconds` budget a Service could shorten it with; adding one would
change `ResolvesMedia` and `DropboxStorage`, which is out of scope. Nothing in
this task grants, so nothing in it becomes `granted`.

**The Vimeo embed stays on the JSON play route until `T-090`.**
`VimeoVideos::linkFor()` returns `https://player.vimeo.com/video/{id}` with
`embed: true` (`app/Integrations/Vimeo/VimeoVideos.php:76-85`) under a domain
whitelist (`:39-60`). Loaded top-level in a new tab that player has no
whitelisted embedding domain, so a 302 to it would not play. So the brief's
"vendor branch for dropbox/vimeo" is followed for Dropbox only:
`SharedController::show` tells the page how each Episode opens, and the page
keeps the fetch-and-`<iframe>` path for the ones that embed. `T-090` deletes
that path, the play route and the `inline` arm together.

**Which Episodes embed is one private check inside
`SharedController::opensAs()`, not a method on `EpisodeProvider`.**
`$episode->provider === EpisodeProvider::Vimeo` is the whole answer, and it
lives only until `T-090` makes `opensAs()` `$episode->isLive() ? null : 'tab'`.
On the enum it would put this task on `app/Enums/EpisodeProvider.php`, which
the ready `T-123` edits to add `Link`, for a method `T-090` deletes. The check
restates a fact `VimeoVideos::linkFor()` already returns as `embed: true`, but
asking the resolver would mint a link per Episode on every page load, which
`Show.vue:74-81` exists to prevent; it reads the Episode's stored column and
calls nothing.

**A live Episode gets no Open control.** No resolver exists for a live
provider — Zoom, Teams, or the `Link` `T-123` adds — so `resolve()` throws
`errors.playback.unsupported_provider` (`:85-89`), and today the button ends
in a notice. A link would open a 400 in a new tab. That is Qori's page now:
`T-113` added `errors/400.blade.php`, so `AppException::render()` shows the
exception's own line through `errors.layout`
(`app/Exceptions/AppException.php:273-278`). But the line is final, with no
resolution, in a tab the Peer had no reason to open: the predictable dead page
the beta gate forbids. `T-125` gives a live Episode its Join, through this
route's live arm (`D-024`, `D-026`).

**A blocked link is a redirect to the Series page, never a page of its own
(`D-020`).** When `open()` answers `VendorLink::blocked()`, the controller
sends the Peer to `route('shared.show', $seriesId).'#access'` — the Series
page at the access notice `T-091` renders with `id="access"` — and flashes
`shared.vendor_notice.redirected` as an `info` toast through
`Inertia::flash('toast', …)`, as `PaymentsFinaliseController` does before a
redirect (`app/Http/Controllers/Settings/PaymentsFinaliseController.php:64-75`).
The Open tab arrives by a full page load, and Inertia fires the flash event on
the initial load too (`app/Http/Controllers/PublicSeriesController.php:59-65`).
The Series page already carries each state's sentence — `T-091`'s
`shared.vendor_notice.reasons.*`, `T-092`'s identity prompt, `T-096`'s and
`T-098`'s vendor steps — so each state has one sentence in one place, and
there is no `shared/OpenBlocked` page, no second copy and no second return
path. While a grant is not `granted`, `T-091` renders the affected Episodes'
Open controls disabled on that page, so the redirect only catches a page
rendered before the state changed, a saved link, or Open's own re-check
finding a permission gone. Nothing in this task produces a blocked link — the
interim branch either redirects to the file or throws — so the branch is
tested with `open()` mocked, and `T-091` only has to return one. The toast
names the `:episode` in the Series' Group's words, so the controller reads
that Group through `Series::findForPeer()`, as `SharedController::show()`
does for Confirming (`app/Http/Controllers/Shared/SharedController.php:99-107`),
on this branch alone. **This task creates `lang/en/shared.php`** with that one
line, as the Peer surface's file `T-091` then adds the notice's lines to;
`lang/en/accesses.php` (`join`, `confirming`, `:43-70`) keeps what it holds.
No Vue page is added.

**No new inline English in Vue.** The anchor wraps exactly the row content the
button wraps today. The page's existing inline sentences (`Show.vue:95`,
`:109`, `:279`) are §13's unwired i18n and stay.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests build
their own Series through `SeriesService::create()` and `EpisodeService::add()`,
as `tests/Feature/Storage/PlaybackTest.php:42-49` does; a live Episode needs a
Group with a `timezone` (`tests/Feature/Series/LiveSessionTest.php:47`) and a
start still ahead, because `EpisodeService::add()` refuses a past one
(`app/Services/EpisodeService.php:107-112`). The browser check needs one
Series whose File Episode on Qori's own storage has a PDF really uploaded —
through the creator's Episode form, or by hand as `docs/tinker/uploads.md`
does on the `local` disk — because the design-review seeder's `cloudflare_r2`
paths name files nobody put there; and a Peer granted access to it
(`docs/tinker/accesses.md`, "Grant someone").

**Equipment:** a visible browser with its popup blocker at its default —
Safari, and Firefox with strict protection — to see the tab open from the link
where `window.open` after an `await` was blocked. Nothing else: there is no
vendor call this task adds, and the browser check opens only the Qori-hosted
Episode. A Dropbox Episode cannot be opened by hand, because nothing in the
product creates a Dropbox connection until `T-044` and `T-096`; its redirect
is case 2's, against `Http::fake`.

**Spike:** none owed. This task introduces no vendor payload. The Dropbox
response it forwards is the one `DropboxStorage::linkFor()` already reads —
`link` from `files/get_temporary_link`, documented at
`https://www.dropbox.com/developers/documentation/http/documentation#files-get_temporary_link`
— and the existing test fakes it inline (`PlaybackTest.php:109`); that fake
is Qori's guess at the shape, not an observed response. No fixture exists
under `tests/Fixtures/dropbox/`; `T-095` owes the first one, and `T-096`
replaces this call.

## Scope

**In:**

- The route, the controller, `PlaybackTicketService::open()` and `admit()`,
  `VendorLink` with `blocked()`.
- The controller's redirect for a blocked link to `shared.show` at `#access`,
  with the `shared.vendor_notice.redirected` toast (`D-020`), and
  `lang/en/shared.php` holding that one line.
- `opens` per Episode on `shared.show`, with the Vimeo check inside
  `SharedController::opensAs()`.
- `Show.vue`: the anchor for Episodes that open in a tab, the existing fetch
  path kept for the ones that embed, nothing for live ones; the Continue
  control follows the same rule.
- `docs/flows/storage.md`, "Getting to the media".

**Out:**

- The ensure-the-grant step in this route and the first call to
  `VendorLink::blocked()`, `series_containers`, `vendor_grants`,
  `VendorGrantStatus`, `VendorAccessService::REQUEST_TIMEOUT_SECONDS`,
  re-checking `granted` rows, `qori:access:reconcile`, and the reconciliation
  that runs when a Peer changes an identity, the creator reconnects or a
  container is replaced (`T-091`).
- The notice on `shared.show` and its `id="access"`, the Peer-facing sentence
  for each grant state (`shared.vendor_notice.reasons.*`), Check again, and
  the Open controls rendered disabled with `shared.vendor_notice.open_disabled`
  while a grant is not `granted` (`T-091`, `D-020`, `D-021`). This task builds
  the Open link those controls disable.
- The Peer's vendor identity (`T-092`), and `accountHint` being filled, by
  each provider's `openLink()` (`T-094`, `T-096`, `T-098`).
- The dedicated-container rule and the picker copy that says sharing a folder
  shares everything inside it (`T-044`, `T-093`).
- Any change to `ResolvesMedia`, `DropboxStorage` or `VimeoVideos`, the
  15-second timeout included; removing the play route, `PlaybackController`,
  `MediaLink::$embed`, the `<iframe>` or the `inline` arm of `opensAs()`
  (`T-090`).
- Any change to `app/Enums/EpisodeProvider.php`, which the ready `T-123`
  edits to add `Link`.
- Join for a live Episode, through this route's live arm, and the
  `access_opens` row (`T-125`, `D-024`, `D-026`); Watch for a recording on the
  same route (`T-126`); the connected tier's per-Peer join links after that
  (`T-100`, `T-101`).
- Error pages. `errors/400`, `422` and `502` are `T-113`'s and already show an
  `AppException`'s own lines on a GET; the statuses still without a page are
  `T-115`'s.
- The `cloudflare_r2` ticket lifetimes and `MediaLifetime`; unchanged.
- `docs/flows/vendor-access.md`; it describes a chain `T-091` builds.

## Files

| Path                                                    | Change | Notes                                                                                |
| ------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------ |
| `app/Data/VendorLink.php`                               | new    | url, provider, accountHint, blockedState; `fromMediaLink()`, `blocked()`             |
| `app/Services/PlaybackTicketService.php`                | edit   | `open()`; the gate extracted into `admit()`                                          |
| `app/Http/Controllers/Shared/OpenEpisodeController.php` | new    | 302 to the ticket or the vendor; a blocked link to `shared.show#access` with a toast |
| `lang/en/shared.php`                                    | new    | `vendor_notice.redirected`; `T-091` adds the notice's lines                          |
| `app/Http/Controllers/Shared/SharedController.php`      | edit   | `opens` per Episode; `opensAs()` with the Vimeo check, `T-090` removes that arm      |
| `routes/shared.php`                                     | edit   | `shared.episodes.open`                                                               |
| `resources/js/pages/shared/Show.vue`                    | edit   | anchor; fetch kept for embeds; nothing for live                                      |
| `docs/flows/storage.md`                                 | edit   | "Getting to the media": both routes                                                  |
| `tests/Feature/Storage/OpenEpisodeTest.php`             | new    | 11 cases                                                                             |
| `tests/Feature/Storage/PlaybackTest.php`                | edit   | 1 case for `open()`                                                                  |
| `tests/Unit/Data/VendorLinkTest.php`                    | new    | 2 cases; `tests/Unit/` holds only `.gitkeep`, so `Data/` is new too                  |

No tinker recipe drives playback (`docs/tinker/` names neither
`PlaybackTicketService` nor the play route), so none changes.
`qori:reachability` will not see the link in `Show.vue`: Wayfinder's
`openRoute.url()` spells neither the route's name nor its path, and
`resources/js/routes` is skipped as generated
(`app/Support/Reachability.php:37`, `:162-171`). The route counts as linked
through `OpenEpisodeTest.php`, because `tests/` is in the haystack
(`:194-201`, `:238-242`), so it needs no allow-list entry.

## Database

None.

## Code

```php
namespace App\Data;

use App\Enums\EpisodeProvider;

/**
 * Where a Peer goes to open an Episode on the vendor's own site (D-016), or
 * why Qori is not sending them there yet (D-020).
 *
 * No expiry, unlike MediaLink: the vendor's permission governs access, and
 * Qori's part is deciding whether to send the person there. A blocked link
 * carries the grant state that decided it (T-091), read once in open(); it is
 * not a second copy of the grant.
 */
class VendorLink
{
    public function __construct(
        /** Null exactly when $blockedState is set. */
        public ?string $url,
        public EpisodeProvider $provider,
        /** The vendor account the Peer should be signed in with. Null here; each provider's openLink() fills it (T-094, T-096, T-098). */
        public ?string $accountHint = null,
        /** A VendorGrantStatus value other than granted; a string because the enum is T-091's. */
        public ?string $blockedState = null,
    ) {}

    /** The existing resolvers' answer, with the ticket's expiry and embed flag dropped. */
    public static function fromMediaLink(MediaLink $link): self;

    /** Not to be followed yet: no url, and the state that stopped it. T-091 is the first caller. */
    public static function blocked(string $state, EpisodeProvider $provider): self;

    /** @phpstan-assert-if-false string $this->url */
    public function isBlocked(): bool;   // $this->blockedState !== null
}
```

```php
// App\Services\PlaybackTicketService — issue() keeps its signature and behaviour,
// now written as admit(), then opened(), then resolve().

/** The Open route's answer: the ticket for Qori's own storage, a VendorLink for anything else. */
public function open(User $peer, string $seriesId, string $episodeId): MediaLink|VendorLink;
// [$access, $series, $episode] = $this->admit($peer, $seriesId, $episodeId);
// $this->progress->opened($access, $episodeId);      // T-091's ensure step goes between these two lines, and answers VendorLink::blocked() there
// $link = $this->resolve($episode, $series);
// return $episode->provider->isQoriHosted() ? $link : VendorLink::fromMediaLink($link);

/**
 * Access, then the Episode — the gate both routes pass. Recording the open is
 * the caller's line, so T-091 can act between the gate and the record.
 *
 * @return array{Access, Series, Episode}
 */
private function admit(User $peer, string $seriesId, string $episodeId): array;
// the bodies of today's :46-64, unchanged, moved
```

```php
namespace App\Http\Controllers\Shared;

class OpenEpisodeController extends Controller
{
    public function __invoke(Request $request, string $seriesId, string $episodeId, PlaybackTicketService $tickets, Terminology $terminology): RedirectResponse;
    // $link = $tickets->open(CurrentUser::orFail($request), $seriesId, $episodeId);
    //
    // if ($link instanceof VendorLink && $link->isBlocked()) {           // D-020: back to the notice, never a page of its own
    //     Inertia::flash('toast', [
    //         'type' => 'info',
    //         'message' => $terminology->line('shared.vendor_notice.redirected', [], Series::findForPeer($seriesId)?->group),
    //     ]);
    //
    //     return redirect()->to(route('shared.show', $seriesId).'#access');
    // }
    //
    // return redirect()->away($link->url);
    // Past the branch, both MediaLink and VendorLink expose a string $url; nothing else on either is read here.
}
```

```php
// App\Http\Controllers\Shared\SharedController::show() — one more key per Episode (:134-142):
'opens' => $this->opensAs($episode),

/** 'tab' for a link, 'inline' for the embed the play route still serves, null for a live Episode. */
private function opensAs(Episode $episode): ?string;
// match (true) {
//     $episode->isLive() => null,
//     $episode->provider === EpisodeProvider::Vimeo => 'inline',   // the stop-gap; T-090 deletes this arm
//     default => 'tab',
// }
```

`Show.vue`: `GrantedEpisode` gains `opens: 'tab' | 'inline' | null`; the page
imports `{ open as openRoute } from '@/routes/shared/episodes'` — aliased,
because `open` is already the page's `ref` (`:70`). Each Episode row is an
`<a :href="openRoute.url([series.id, episode.id])" target="_blank" rel="noopener">`
carrying today's row content when `opens === 'tab'`; today's
`<button @click="openEpisode(episode)">` when `'inline'`; the same content
with no control when `null`. The Continue control (`:175-183`) follows the
same three-way rule. `openEpisode()`, `opening`, `failed` and the `<iframe>`
stay for the inline case.

`docs/flows/storage.md`, "Getting to the media": the open chain beside the
play chain, with the controller's redirect for a blocked link to
`shared.show#access`; the play route described as serving only the Vimeo
embed; "the link is short-lived" said of `cloudflare_r2` alone. The section
names Qori's storage `cloudflare_r2` or `CloudflareR2Storage`, never by its
old name, which `DocumentationTest` fails in a live doc
(`tests/Feature/DocumentationTest.php:253`).

`lang/en/shared.php`: the file header in `accesses.php`'s style
(`lang/en/accesses.php:3-10`), naming it the Peer surface's copy, and
`'vendor_notice' => ['redirected' => …]`.

## Copy

| Key                               | File                 | English                                             |
| --------------------------------- | -------------------- | --------------------------------------------------- |
| `shared.vendor_notice.redirected` | `lang/en/shared.php` | That :episode can't open yet. What's left is below. |

`shared.vendor_notice.redirected` is read through `Terminology::line()` with
the Series' Group, so `:episode` is that Group's word; it names no state,
because the notice it points at does. The Peer-facing sentence for each grant
state that is not `granted` is `T-091`'s, under
`shared.vendor_notice.reasons.*` in the same file — `pending` saying when Qori
tries next, `needs_creator` saying the creator has been told and nothing more
is needed from the Peer (`D-020`); the provider-specific step a Peer still has
to take is each provider task's. A failure on this route adds no copy: the
gate and the resolvers throw the `errors.access.*` and `errors.playback.*`
lines they throw on the play route today, and Qori's error pages show them
(see Scope).

## Routes

| Verb | Path                                           | Name                   | Action                                   |
| ---- | ---------------------------------------------- | ---------------------- | ---------------------------------------- |
| GET  | `/shared/{seriesId}/episodes/{episodeId}/open` | `shared.episodes.open` | `Shared\OpenEpisodeController::__invoke` |

Inside the existing `auth`, `verified`, `shared.` group
(`routes/shared.php:31-34`). `shared.play` is unchanged.

## Tests

**New: `tests/Feature/Storage/OpenEpisodeTest.php` — 11 cases**
(`Http::preventStrayRequests()` in `setUp`; the `seriesWith()` helper from
`PlaybackTest.php:42-49`; every GET through
`route('shared.episodes.open', [$seriesId, $episodeId])`)

1. `test_a_qori_hosted_episode_redirects_to_its_signed_link` — 302 whose
   `Location` contains `one.pdf`; no JSON.
2. `test_a_dropbox_episode_redirects_to_the_link_fetched_with_the_creators_token`
   — `Http::fake` as `PlaybackTest.php:109`; 302 to
   `https://dl.dropbox.test/f.pdf`; `assertSent` sees `Bearer creator-token`.
3. `test_opening_records_the_episode_as_opened` — after the GET,
   `$access->fresh()->hasOpened($episodeId)` and `last_activity_at` is set.
4. `test_someone_without_access_gets_a_forbidden_page_not_a_redirect` — 403;
   sees `errors.access.not_granted.message`.
5. `test_a_revoked_access_gets_a_forbidden_page` — `AccessService::revoke()`,
   then 403.
6. `test_an_episode_not_in_the_series_is_not_found` — 404.
7. `test_a_guest_is_sent_to_sign_in` — redirect to the sign-in page.
8. `test_a_live_episode_cannot_be_opened` — a Zoom Episode with the content
   `LiveSessionTest.php:185` passes, its `starts_at` set to
   `now()->addDay()` rather than that line's fixed date, which
   `EpisodeService::add()` will refuse once it has passed; 400 on Qori's page
   (`T-113`'s `errors/400.blade.php`), seeing
   `errors.playback.unsupported_provider.message`.
9. `test_a_dropbox_episode_without_a_connection_renders_the_qori_502_page` —
   502 on `T-113`'s `resources/views/errors/502.blade.php`: because the view
   exists, `AppException::render()` renders `errors.layout` with the
   exception's own lines (`app/Exceptions/AppException.php:273-278`), so the
   page sees `errors.playback.provider_unavailable.message` and
   `.resolution`, and not the view's default
   `errors.upstream_unavailable.message` or the framework page.
10. `test_the_shared_page_says_how_each_episode_opens` — a `cloudflare_r2`
    file, a Vimeo video and a Zoom session; `opens` is `tab`, `inline`,
    `null` in that order.
11. `test_a_blocked_link_sends_the_peer_back_to_the_series_page_at_its_notice`
    — `$this->mock(PlaybackTicketService::class, …)`, as
    `tests/Feature/Checkout/PaidFulfilmentTest.php:227` mocks
    `AccessService`, answers `open()` with
    `VendorLink::blocked('pending', EpisodeProvider::Dropbox)`; the GET
    redirects to `route('shared.show', $seriesId).'#access'`, never away;
    `assertSessionHas(SessionKey::FLASH_DATA, …)` sees an `info` toast whose
    message is `shared.vendor_notice.redirected` with the Group's `:episode`,
    the way `tests/Feature/Access/SeriesAccessCodeTest.php:87-89` reads one;
    no request leaves.

**New: `tests/Unit/Data/VendorLinkTest.php` — 2 cases** (bare
`PHPUnit\Framework\TestCase`)

1. `test_it_wraps_a_media_link_and_drops_the_expiry` — url and provider
   copied; `accountHint` and `blockedState` null; `isBlocked()` false; the
   object has no `expiresAt` and no `embed`.
2. `test_a_blocked_link_has_no_url_and_keeps_the_state` — `blocked('pending',
EpisodeProvider::Dropbox)`: `url` null, `blockedState` `pending`,
   `isBlocked()` true.

**Changed:**

- `tests/Feature/Storage/PlaybackTest.php` — 1 new case,
  `test_open_keeps_the_ticket_for_qori_storage_and_wraps_a_vendor_link`:
  `open()` returns a `MediaLink` for `cloudflare_r2` and a `VendorLink` for
  Dropbox. The eight existing cases are untouched; `issue()` keeps its
  signature.

`tests/Feature/ErrorPagesTest.php` does not change. Its two status lists
(`:90`, `:105`) assert `errors.pages.{status}.*` copy, which the 502 view does
not carry, and `test_the_app_exception_statuses_render_the_qori_page`
(`:165-172`) already covers 502.

Total: 14 new cases.

## Acceptance

- [x] With the popup blocker at its default in Safari and in Firefox strict
      mode, a Peer with access opens a Qori-hosted (`cloudflare_r2`) Episode
      from the page in a new tab, and lands on the file; the Dropbox redirect
      is case 2's, against `Http::fake`, because nothing in the product can
      create a Dropbox connection until `T-044` and `T-096`
- [x] The open is recorded as opened and `last_activity_at` moves, whether or
      not the vendor then answers
- [x] No access, a revoked access, a missing Episode, a Dropbox Episode with no
      connection and a guest each meet the page or redirect the tests name —
      never a blank tab
- [x] The Vimeo embed still plays inline through the play route; a live
      Episode shows no Open control
- [x] `VendorLink` carries no expiry, and no grant state but the one
      `blocked()` is given; `open()` records the open between `admit()` and
      `resolve()`, where `T-091`'s ensure step will go
- [x] A blocked link lands the Peer on `shared.show` at `#access` with the
      `shared.vendor_notice.redirected` toast, and no Open ever renders a
      page of its own for a grant that is not `granted` (`D-020`)
- [x] `docs/flows/storage.md` describes both routes and says which one is
      leaving
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

`CLAUDE.md` now agrees with the code this draft followed from the start:
`IntegrationServiceProvider` tags every `ResolvesMedia` implementation
`media-providers` for `PlaybackTicketService`
(`app/Providers/IntegrationServiceProvider.php:32-39`), and each names itself
through `provider()` (`ResolvesMedia.php:29`). `open()` needs no new binding.

The brief for this draft named `tests/Feature/PlaybackTest.php` and
`lang/en/shared.php`; the test lives at `tests/Feature/Storage/PlaybackTest.php`,
and no `shared.php` exists yet. This task creates it with the one line
`D-020` gives the redirect, and `T-091` adds the notice's lines to it.

`routes/shared.php:40-41` and `PlaybackTicketService.php:19-21` say the link
is short-lived so revoking access revokes it. That stays true of
`cloudflare_r2` and of nothing else once the vendor branch redirects; the
docblocks are reworded with the flow doc, and `T-091` gives revocation its
real mechanism.

Whether the `Location` of a `cloudflare_r2` redirect is signed depends on the
disk (`app/Integrations/CloudflareR2/CloudflareR2Storage.php:53-55`): R2 signs
it in production, and the `local` disk the tests use carries
`'serve' => true` (`config/filesystems.php:33-39`) and signs it through
Laravel's own file route, whatever the comment above those lines says. Case 1
asserts the path, not the signature.

**18 September 2026 (`D-026`).** Case 8 and the Preconditions line above build
their live Episode the way `LiveSessionTest.php:185` does today, passing the
start inside the content array. `T-123` moves the start onto `episodes.starts_at`
alone, so whichever of the two lands second writes the case as
`EpisodeService::add(..., startsAt: ...)` with the content
`['join_url' => 'https://zoom.us/j/91827405566', 'records' => true]`, and reads
the start from the column rather than from `content['starts_at']`. `T-125`
later removes case 8, when a live Episode gains its Join.

A Dropbox call that runs past its 15 seconds raises the HTTP client's
`ConnectionException`, which nothing on this path catches (only Stripe's
`Connect` catches its own), so on the play route today that is the 500 page
rather than the 502; Open inherits it until `T-096` replaces the call and
`T-091`'s constant bounds what the route waits on. Not fixed here:
`DropboxStorage` is out of scope.

**19 September 2026, on completion.** The Continue control's `null` arm is
built as written: when the next unfinished Episode is live, the page shows
"Continue — N. title" as plain text with no control. That is consistent with
the spec, but it reads like a broken link. `T-125` should give Continue its
Join together with the row. The first Acceptance line, Safari and Firefox
strict mode, was not walked in those browsers; the report says what was
checked instead.
