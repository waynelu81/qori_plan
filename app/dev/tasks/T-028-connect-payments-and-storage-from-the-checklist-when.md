---
id: T-028
title: Connecting Stripe or Google Drive from a Series comes back to it
stream: onboarding
status: done
owner: claude
estimate: M
depends: T-044
blocks: none
---

# T-028 — Connecting Stripe or Google Drive from a Series comes back to it

## Why

Since `D-056` a new creator is asked for nothing up front: Stripe is asked
where a price is typed and Google Drive where a file is chosen. Both links on
the Series page go to Integrations, and the vendor's landing returns to
Integrations too, so a creator in the middle of a Series has to find it again.
The couple of clicks `D-056` promised becomes a hunt.

Afterwards a connection begun from the Series page lands back on that Series,
at the control that asked for it, whether the creator connected or stopped
partway. And a file Episode starts on Qori storage while Google Drive is not
connected, so the first file needs nothing connected at all (the owner, 23
September 2026: "yes start on Qori storage").

## Decisions taken to make this specifiable

**The links keep going to Integrations, and Integrations remembers where they
came from.** Integrations is where Google's tiers and their limits are read
and where Stripe's country is chosen; linking straight to a vendor would skip
both. Each link carries `series` (the slug) and `control` (`series-details` or
`new-episode`), and the Episode form's adds `kind`. `IntegrationsController::show()`
resolves the slug inside the Group and remembers
`share.series.show?kind=…#control` through the existing
`PaymentsDestination` (price) or `ConnectionsDestination` (Drive), which the
vendor landings already spend once, first, whatever happened.

**Only a link that names a Series sets an address; nothing on Integrations
clears one.** Setup's part three (until `T-195`) leaves a `ConnectionsDestination`
and then links to Integrations, and clearing on every visit would break it. The
cost is the one setup's parts already accepted: a creator who opens
Integrations from a Series and connects later, from Integrations, returns to
that Series.

**A slug that is not this Group's, a control that is not one of the two, or a
kind that is not an `EpisodeType` sets nothing.** The query never becomes a
URL of its own, so it cannot redirect anywhere Qori did not build.

**The query's kind decides the form when the page opens; the last Episode
decides it after each save.** `T-026` applied the query only while a Series
had no Episodes, and a return from Drive may land on a Series that has some.

**The file default follows the connection, not a list.** `EpisodeType::File`
offers Google Drive first. The form starts on Qori storage while Drive is not
connected and on the server's first choice once it is, so a creator returning
from connecting Drive lands on Drive.

## Preconditions

**Data this task verifies against:** a Group with one draft Series and no
connections. `php artisan qori:reset basic`.

**Equipment:** a browser. The vendor round trip itself was not walked: it
needs a real Stripe or Google sign-in, which is the owner's.

## Scope

**In:**

- The two links naming the Series, the control and the kind.
- `IntegrationsController::show()` remembering the address.
- The Episode form's starting kind and provider.

**Out:**

- Setup stages (`D-056` removed them).
- The connectors themselves (`storage` stream, `T-044`).
- Seller readiness at the paid action, which the price field and the
  dashboard's blocking action already read from Stripe's account (`T-164`).

## Files

| Path                                                   | Change | Notes                                        |
| ------------------------------------------------------ | ------ | -------------------------------------------- |
| `app/Http/Controllers/Share/IntegrationsController.php` | edit  | Remembers the Series address                 |
| `app/Http/Controllers/Share/SeriesController.php`      | edit   | `paymentsUrl`, `driveProps()`'s link         |
| `resources/js/pages/share/series/Show.vue`             | edit   | Drive link's kind; starting kind and provider |
| `docs/flows/billing.md`, `docs/flows/storage.md`       | edit   | The Series as a forwarding address           |
| `tests/Feature/Series/SeriesReturnTest.php`            | new    | 6 cases                                      |

## Database

None.

## Code

`IntegrationsController::show()` takes the `Request` and calls a private
`rememberSeries(Request $request): void`. `SeriesController::driveProps()`
takes the `Series` beside the Group.

## Copy

None.

## Routes

None. `share.settings.integrations` gains three optional query keys.

## Tests

**New: `tests/Feature/Series/SeriesReturnTest.php` — 6 cases**

1. `test_the_series_page_links_name_the_series_and_the_control`
2. `test_integrations_from_the_price_remembers_the_series_for_stripe`
3. `test_integrations_from_the_episode_form_remembers_the_series_and_kind_for_drive`
4. `test_a_series_of_another_group_sets_nothing`
5. `test_an_unknown_control_or_kind_sets_nothing_of_its_own`
6. `test_stripe_landing_returns_to_the_series` — the landing spends the
   address, faked as `PaymentsOauthTest` fakes it

## Acceptance

- [x] From a Series' price, Connect Stripe goes to Integrations and Stripe's
      landing returns to that Series' details
- [x] From the Episode form, Connect Google Drive goes to Integrations and the
      landing returns to the Episode form on the kind it was on, on Drive
- [x] A file Episode starts on Qori storage while Drive is not connected
- [x] Every box above ticked, `status: done` and `owner:` set in the front matter
- [x] `bin/tasks --check` passes in `qori-plan`
- [x] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [x] Report written in `reports/` (see [its README](reports/README.md))

## Added during execution

- `tests/Feature/Series/SeriesPriceTest.php` — pinned the bare Integrations
  URL as `pricing.paymentsUrl`; updated to the link that names the Series.

## Re-scope log

**2026-09-11 — owner revised this draft.** Setup now appears before the first
Series guide, and integrations are included. The owner explicitly confirmed
seller setup can be skipped during onboarding and is prompted before paid
selling. The former blanket connector exclusion and cap-trigger-only sequence
are superseded. No implementation was started.

**2026-09-13 — the seller stage is cut out.** `T-075` places the Stripe doors and a storage explanation in the setup frame, each skippable. What remains here is the prompt for seller setup at the paid action and the storage connectors once `T-044` exists.

**2026-09-16 — the connectors are the `storage` stream's.** `D-016` settled how every storage and live-session integration works and moved `T-044` into a stream of its own, with one task per provider after it. The "inventory the connection flows" bullet above is answered there. What this draft keeps is the storage stage itself: its copy, the link to the Integrations page's provider sections (where the creator picks a tier and reads its limitations), and the seller prompt at the paid action.

**2026-09-23 — the stages are gone (`D-056`).** The owner replaced creator
setup with one first-Series screen, and Stripe and Google Drive are asked
where they are needed. Rewritten to the one piece that still matters: coming
back to the Series afterwards. `T-026` no longer comes first, so the
dependency on it is dropped.

**2026-09-23 — brought to ready and claimed.** The owner answered the file
default ("start on Qori storage"). The draft's bullets were answered from the
code: both links go to Integrations today, and the landings already spend a
forwarding address.

## Notes

Existing Payments/Connect screens and provider capability reads can be reused;
Qori uploads already work without an external account. Dropbox/Vimeo media
resolvers are not connection flows. The
[onboarding plan](../ui-onboarding.md) distinguishes existing capabilities from
new stage presentation, context persistence and provider work.

**23 September 2026, from `T-026`'s walk.** The files shape lands on the
Episode form with "Where it lives" on Google Drive, the first provider the
server offers for a file, so a brand-new creator's first view asks them to
connect Drive although Qori storage needs nothing. Whether the form should
start on Qori storage while Drive is not connected belongs with this task's
round trip.
