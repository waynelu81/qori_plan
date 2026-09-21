---
id: T-067
title: Integrations are a settings page
stream: reachability
status: done
owner: claude
estimate: M
depends: none
blocks: T-044, T-062
---

# T-067 — Integrations are a settings page

## Why

The owner's model, recorded on 2026-09-13: a connection to Stripe, Google
Drive or Dropbox is a setting of the one Group a person owns, one per provider,
disconnected before it can be connected again, the same way the plan is one
per Group. Today Stripe lives behind a "Payments" item in the sidebar next to
"Settings", and "Settings" is plan-gated and points at custom vocabulary. The
integrations note from 2026-09-07 already proposed one page grouped by purpose
and chose to build it after the other connectors; the owner reversed that
order. The page comes now, with the one connector that works, and `T-044`
adds storage and video to it.

Afterwards: "Settings" is offered to every owner and lands on Integrations,
whose first section is getting paid through Stripe; Vocabulary sits beside it
in a settings sub-navigation when the plan allows; "Payments" is gone from the
sidebar; and the old page URL answers 404.

## Decisions taken to make this specifiable

**The page moves; the actions do not.** `GET settings/integrations` renders
the page. `payouts/connect`, `payouts/return` and `payouts/connection` stay
where they are: they act on the Stripe connection, they are not pages, and
`T-062` changes their verbs in its own commit.

**A share-settings layout, modelled on the user-settings one.** A left
sub-navigation with Integrations always and Vocabulary when
`canCustomiseVocabulary`, which the shared `sharing` prop already carries.
Both pages move under `pages/share/settings/`.

**The old route goes without a redirect.** Nothing outside the codebase links
to `share.payouts.show`; the Series page, the return and disconnect landings
and the screenshot run are updated in this task.

**Copy stays where it was.** The page's inline English predates this task and
is §13's unwired i18n; the section title changes from "Taking card payments"
to "Getting paid", and the layout's header uses the Group noun through
`useTerminology()` as the sidebar does. No new lang keys.

## Preconditions

`T-064` done, which it is.

## Scope

**In:**

- The route, `IntegrationsController::show()` taking over
  `PayoutsController::show()` unchanged in behaviour, and the two landings
  pointing at the new route.
- The layout, the two page moves, the sidebar.
- The Series page's `payoutsUrl`, the screenshot run's two shots, the tests
  that name the route, and `docs/flows/checkout.md`.

**Out:**

- The connect form's verb, the country, the disconnect: `T-062`, `T-064`.
- Storage and video sections: `T-044`.
- Any lang work on the page.

## Files

| Path                                                    | Change | Notes                                          |
| ------------------------------------------------------- | ------ | ---------------------------------------------- |
| `routes/share.php`                                      | edit   | `settings/integrations`; `payouts` GET removed |
| `app/Http/Controllers/Share/IntegrationsController.php` | new    | `show()`                                       |
| `app/Http/Controllers/Share/PayoutsController.php`      | edit   | `show()` removed; landings retargeted          |
| `app/Http/Controllers/Share/VocabularyController.php`   | edit   | Render path                                    |
| `app/Http/Controllers/Share/SeriesController.php`       | edit   | `payoutsUrl`                                   |
| `app/Console/Commands/DesignReviewCommand.php`          | edit   | Two shots                                      |
| `resources/js/layouts/share-settings/Layout.vue`        | new    | Sub-navigation                                 |
| `resources/js/pages/share/Payouts.vue`                  | move   | → `pages/share/settings/Integrations.vue`      |
| `resources/js/pages/share/Vocabulary.vue`               | move   | → `pages/share/settings/Vocabulary.vue`        |
| `resources/js/components/AppSidebar.vue`                | edit   | Payments gone; Settings for every owner        |
| `docs/flows/checkout.md`                                | edit   | The page's address                             |
| `tests/Feature/Share/PayoutsPageTest.php`               | move   | → `IntegrationsPageTest.php`, +1 case          |
| `tests/Feature/Share/PayoutsReturnTest.php`             | edit   | Route name                                     |
| `tests/Feature/Share/PayoutsDisconnectTest.php`         | edit   | Route name                                     |
| `tests/Feature/Series/SeriesPriceTest.php`              | edit   | Route name                                     |

## Database

None.

## Code

```php
namespace App\Http\Controllers\Share;

class IntegrationsController extends Controller
{
    public function __construct(private PayoutsService $payouts) {}

    /** The body of PayoutsController::show() as T-064 left it, rendering 'share/settings/Integrations'. */
    public function show(string $group, CurrentGroup $current, Terminology $terminology): Response;
}
```

`PayoutsController::return()` and `disconnect()` land on
`to_route('share.settings.integrations', $model->slug)`.
`SeriesController::show()` passes `route('share.settings.integrations', $scope?->slug)`.

```vue
<!-- resources/js/layouts/share-settings/Layout.vue -->
<!-- PageHeader title `${noun('group')} settings`; aside nav of Buttons as in
     layouts/settings/Layout.vue; items from useShareContext(): -->
[{ title: 'Integrations', href: `${base}/settings/integrations` },
...(current.canCustomiseVocabulary ? [{ title: 'Vocabulary', href:
`${base}/settings/vocabulary` }] : [])]
```

In `AppSidebar.vue` the `manage` block offers, to an owner, "Plan and billing"
and "Settings" → `${base}/settings/integrations`. The `canCustomiseVocabulary`
gate moves from the sidebar to the layout's nav.

## Copy

None.

## Routes

| Verb | Path                              | Name                          | Action                        |
| ---- | --------------------------------- | ----------------------------- | ----------------------------- |
| GET  | `g/{group}/settings/integrations` | `share.settings.integrations` | `IntegrationsController@show` |
| GET  | `g/{group}/payouts`               | —                             | Removed; answers 404          |

## Tests

**Moved: `tests/Feature/Share/PayoutsPageTest.php` → `IntegrationsPageTest.php`,
same 3 cases against the new route — 1 new case**

1. `test_the_old_payouts_address_is_gone` — GET `g/{group}/payouts` answers
   404 for the owner.

**Changed:** `PayoutsReturnTest`, `PayoutsDisconnectTest`, `SeriesPriceTest`
— the route name only.

## Acceptance

- [x] An owner's sidebar shows "Settings" and no "Payments"; Settings lands
      on Integrations with a Stripe section
- [x] Vocabulary appears in the settings sub-navigation only when the plan
      allows it
- [x] Coming back from Stripe and disconnecting both land on Integrations
- [x] The Series form's "connect payouts" link points at Integrations
- [x] `g/{group}/payouts` answers 404
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`T-037` in the design stream ("One heading per settings page, not two") was
written against the user-settings layout. The share-settings layout should
not repeat the mistake: one `PageHeader`, in the layout, and none in the page.
