---
id: T-152
title: An Episode needs its provider connected
stream: storage
status: done
owner: claude
estimate: S
depends: T-044, T-123
blocks: T-094, T-098
---

# T-152 — An Episode needs its provider connected

> **Cut out of `T-044` on 20 September 2026**, which was `L` at 68 paths and
> named this as part (d) of its own split under "Before this can be ready".
> Nothing here is new: the decision is `D-025`, the copy, the code and the
> test cases are `T-044`'s, moved whole. It takes `T-123` out of `T-044`'s
> `depends:` with it, because `EpisodeProvider::Link` is a case this task's
> `match` has an arm for and `T-044` never names.

## Why

`EpisodeService::add()` will take a Dropbox file id — and, once `T-094` and
`T-098` land, a Google Drive or OneDrive one — into an Episode whose `content`
is meaningless without the creator's own account, with no connection in the
Group to turn it into something a Peer can open. `DropboxStorage::linkFor()`
refuses at the far end (`app/Integrations/Dropbox/DropboxStorage.php:31-38`),
so what a creator gets today is a published Series that does not open, and the
person told about it is the Peer.

Afterwards the refusal happens where the creator can act on it: at add, with a
sentence naming the provider and pointing at Integrations.

## Decisions taken to make this specifiable

**The refusal is a property of the provider, not a list in the Service**
(`D-025`). `EpisodeProvider::isAccountBound()` is true where the Episode's
`content` is an item in the creator's own account that only the creator's
token turns into something a Peer can open — `dropbox` today, and the
`google_drive` and `onedrive` cases `T-094` and `T-098` add — and false for
everything else.

**Vimeo is not account-bound, and no Vimeo Episode is refused here.**
`VimeoVideos::linkFor()` builds the player URL from the id and never reads the
connection (`app/Integrations/Vimeo/VimeoVideos.php:62-86`), a Vimeo Episode
plays with no connection today
(`tests/Feature/Storage/PlaybackTest.php:143-155`), and the browser runs add
one with nothing connected (`tests/e2e/support/creator.ts:109-125`,
`tests/e2e/public-link.spec.ts:67`). `T-090` decides what a Vimeo picker needs
from a connection; it is not this.

**A live Episode's pasted `join_url` is never refused.** `zoom`, `teams` and
`T-123`'s `link` are the unconnected tier `D-025` names — a creator pastes a
URL Qori never follows — and `cloudflare_r2` is nobody's to connect.

**The predicate is a `match` with no default arm, beside `connection()`**, so
the list is written once and each task that adds a case adds its arm:
`T-094`'s `GoogleDrive` and `T-098`'s `OneDrive` true, `T-090`'s `YouTube`
false.

**Two errors, not one, because the creator can only act on one of them.** The
Episode form offers Dropbox for files, video and audio
(`resources/js/pages/share/series/Show.vue:199-202`) and nothing binds a
Dropbox connector until `T-096`. A provider whose connector is not bound yet
cannot be connected at all, so `errors.series.provider_not_available` is final
and carries no resolution (`CLAUDE.md`: omitting `resolution` means the path
is final), and it names no provider, because a provider's name is
`connections.providers.<provider>.name`, which that provider's task adds with
its connector. A provider whose connector _is_ bound and whose Group has no
live row gets `errors.series.provider_not_connected`, which names the provider
and points at Integrations, so the refusal never sends a creator to a section
that is not there. `ConnectionService::connectorFor()` is what tells the two
apart, which is why this task depends on `T-044`.
`provider_not_available` covers only Dropbox's window before `T-096`, which
closes before beta.

**Both sentences are about a missing connection, never about which tier is
connected** (`D-018`). An Episode is refused because Qori cannot act on that
provider at all; a connected account is never refused for the tier it is on.

**The form goes on offering Dropbox behind the refusal rather than hiding
it** — answered on `T-044`, 17 September 2026 (`D-018`). Every provider is in
the beta release, so each connector lands before release and the refusal
covers a gap that closes; removing an option and putting it back is work for a
state that is temporary by decision.

**A revoked or reconnect-marked row counts as not connected.** The guard reads
`Connection::isLive()` — `T-044`'s `isUsable() && ! needsReconnect()` — not the
row's existence.

**The guard reads the Series' own Group, not the ambient one.**
`Connection::query()->forGroup($series->group_id)`, because `add()` does not
require a `CurrentGroup` context and `tests/Feature/Storage/PlaybackTest.php`
calls it outside one.

## Preconditions

**Data this task verifies against:** a clean database.

**Equipment:** none.

**`T-044` done**, for `ConnectionService::connectorFor()`, `Connection::isLive()`
and the `connections.providers.<provider>.name` copy this task interpolates.
**`T-123` done**, which adds `EpisodeProvider::Link` — an arm this task's
`match` must carry.

**Spike:** none. No vendor payload is named.

## Scope

**In:**

- `EpisodeProvider::isAccountBound()`, with every case today given an arm.
- `EpisodeService::guardProviderConnected()`, run in `add()` beside and after
  `guardEpisodeType()`.
- The two error keys.
- The existing tests that add a Dropbox Episode with no connection, which the
  guard now refuses.

**Out:**

- `EpisodeProvider::GoogleDrive` and `OneDrive`, and their `isAccountBound()`
  arms (`T-094`, `T-098`).
- Any refusal on `update()` or on making a Series ready: `add()` is where a
  creator chooses the provider, and a connection that dies afterwards is
  `T-044`'s reconnect path and `T-091`'s grant states, not a refusal.
- Any check that the item id exists at the vendor. That is a vendor call, and
  the picker in `T-094` is where an id comes from.

## Files

| Path                                                                                   | Change | Notes                                                                                   |
| -------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------------- |
| `app/Enums/EpisodeProvider.php`                                                        | edit   | `isAccountBound()` beside `connection()` (`D-025`); `T-123` adds `Link` first           |
| `app/Services/EpisodeService.php`                                                      | edit   | `guardProviderConnected()`; `ConnectionService` by constructor, the class having none   |
| `lang/en/errors.php`                                                                   | edit   | `series.provider_not_connected`, `series.provider_not_available`                        |
| `docs/flows/series.md`                                                                 | edit   | The add chain gains the guard                                                           |
| `tests/Feature/Share/EpisodeServiceTest.php`                                           | edit   | +3 cases, and `:56` and `:165` get a connection                                         |
| `tests/Feature/Storage/MediaLifetimeTest.php` `tests/Feature/Storage/PlaybackTest.php` | edit   | A Dropbox connection before each Dropbox Episode; see Tests                             |
| `tests/Feature/Storage/OpenEpisodeTest.php`                                            | edit   | Added during execution — the HTTP twin of `PlaybackTest`'s case, which the table forgot |

Nothing else that adds an Episode changes, because Dropbox is the one
account-bound provider today: `tests/e2e/support/creator.ts` adds a Vimeo
Episode with nothing connected (`:109-125`) and keeps doing so, and
`tests/Feature/Series/EpisodeRoutesTest.php` and
`tests/Feature/Series/LiveSessionTest.php` add Vimeo, Zoom and Qori-hosted
Episodes only. `DesignReviewSeeder` writes its Episodes with
`$series->episodes()->create()` (`:422-436`) and is untouched, and so is
`MailCheckCommand`, whose one Episode is Qori-hosted (`:196-198`).

## Added during execution

- `tests/Feature/Storage/OpenEpisodeTest.php` —
  `test_a_dropbox_episode_without_a_connection_renders_the_qori_502_page` adds
  a Dropbox Episode with no connection through its own `seriesWith()`, so the
  new guard refuses it before the case can reach what it was testing. The
  table listed `PlaybackTest`'s case and missed its HTTP twin. Changed exactly
  as the spec prescribes for the twin — the connection created, the Episode
  added through `$group`, `revoke()` before the request — so the 502 the case
  exists to prove is unchanged.

## Database

None.

## Code

```php
namespace App\Enums;

enum EpisodeProvider: string
{
    /** True where the Episode's content is an item in the creator's own account that only the creator's token turns into
     *  something a Peer can open (D-025): dropbox today; google_drive and onedrive when T-094 and T-098 add them.
     *  A match with no default arm, beside connection(), so each task that adds a case adds its arm. */
    public function isAccountBound(): bool;
}
```

```php
// App\Services\EpisodeService — public function __construct(private ConnectionService $connections) {}, the class having none today;
// guardProviderConnected() runs beside guardEpisodeType() in add(), after it.
private function guardProviderConnected(Series $series, EpisodeProvider $provider): void;
// return unless $provider->isAccountBound();
// $needs = $provider->connection();   // never null for an account-bound case
// return when Connection::query()->forGroup($series->group_id)->where('provider', $needs)->first()?->isLive();
//   forGroup(): the Series' own Group, read without the ambient context, which add() does not require (PlaybackTest calls it outside one)
// $nouns = app(Terminology::class)->for($series->group)->replacements(), as guardLiveSessionTime() builds them (:90-96)
// $this->connections->connectorFor($needs) === null
//   ? throw AppException::invalidRequest('errors.series.provider_not_available', $nouns, devMessage: …)
//   : throw AppException::invalidRequest('errors.series.provider_not_connected', ['provider' => __("connections.providers.{$needs->value}.name")] + $nouns, devMessage: …)
```

## Copy

| Key                                    | File                 | English                                                                                                        |
| -------------------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------- |
| `errors.series.provider_not_connected` | `lang/en/errors.php` | :provider isn't connected to your :group yet. / Connect it from Integrations, then add the :episode.           |
| `errors.series.provider_not_available` | `lang/en/errors.php` | That storage can't be connected to Qori yet, so the :episode can't be added from there. (final, no resolution) |

## Routes

None.

## Tests

**Changed: `tests/Feature/Share/EpisodeServiceTest.php` — +3 cases**

`:56` and `:165` add Dropbox Episodes and get a live Dropbox connection on the
Group `series()` makes, created with
`Connection::factory()->create(['group_id' => …, 'provider' => ConnectionProvider::Dropbox])`
inside `CurrentGroup::runFor()`, as `tests/Feature/Storage/PlaybackTest.php:112-116`
already does. Then:

1. `test_an_episode_whose_provider_is_not_connected_is_refused` — `ConnectsNothing`
   tagged for Dropbox and no row: a Dropbox file is refused with
   `errors.series.provider_not_connected` and nothing is written.
2. `test_a_revoked_connection_counts_as_not_connected` — the double tagged for
   Dropbox, and a Dropbox row first revoked, then one with `needs_reconnect_at`
   set: each refused with `errors.series.provider_not_connected`.
3. `test_only_an_account_bound_provider_needs_a_connection` — nothing connected
   and no connector bound: a Qori-hosted file, a Vimeo video
   (`['vimeo_id' => '123456789']`), a live Zoom Episode and a live `Link`
   Episode, each live one with a pasted `join_url` and a start a day ahead
   (`T-123`'s `startsAt:`), are all added; a Dropbox file is refused with
   `errors.series.provider_not_available`; and among today's `EpisodeProvider`
   cases `isAccountBound()` is true for `Dropbox` alone.

**Changed, no case added or removed:**

- `tests/Feature/Storage/MediaLifetimeTest.php` — the `episode()` helper
  (`:38-47`) creates a Group per call and now gives it a Dropbox connection
  when the provider `isAccountBound()`, which `:62`'s audio Episode needs;
  `:132-135` already has one.
- `tests/Feature/Storage/PlaybackTest.php` —
  `test_a_dropbox_episode_without_a_connection_fails_cleanly` (`:130-141`)
  creates the Group and a Dropbox connection on it, adds the Episode through
  `seriesWith()`'s `$group`, and calls `revoke()` on the row before `issue()`,
  which keeps what it tests; `:112-116` already has one.

Total: 3 new cases, all in a changed file.

## Acceptance

- [x] Adding a Dropbox Episode, the one account-bound provider today, with no
      live Dropbox connection is refused, with
      `errors.series.provider_not_available` until a Dropbox connector is bound
      and `errors.series.provider_not_connected` after; a revoked row and a row
      marked for reconnect each count as not connected
- [x] A Qori-hosted file, a Vimeo video and a live Episode with a pasted join
      link are added with nothing connected
- [x] `EpisodeProvider::isAccountBound()` is a `match` with no default arm, so
      a case added later will not compile until it is given one
- [x] `docs/flows/series.md` shows the guard in the add chain
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `php artisan qori:tasks --check` passes
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

Nothing. `T-044` carried this to a specified state before the split; the
questions still open on `T-044` are about connecting an account, which this
task does not do.

## Re-scope log

None.

## Notes

`T-094` and `T-098` each add their provider's `isAccountBound()` arm in the
same change that adds the `EpisodeProvider` case, so this task's `match`
having no default arm is what makes them do it.
