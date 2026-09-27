---
id: T-182
title: Every page renders the same on the server and in the browser
stream: design
status: doing
owner: claude
estimate: M
depends: none
blocks: none
---

# T-182 — Every page renders the same on the server and in the browser

## Why

Every page logs "Hydration completed but contains mismatches" in the browser's
console, once per load: the Series list, a Series, the invitations page on 22
September 2026 (`T-043`'s walk), and the dashboard, Billing and the home page
when `T-046`'s report first recorded it on 12 September and said it needed a
task. A mismatch means the markup the server rendered and the browser's first
render disagree, which is how a page shows the wrong state until something
touches it. Afterwards no page logs one.

## Decisions taken to make this specifiable

Brought to ready on 28 September 2026, from the dev server's console at 375
and 1280px.

**Two causes, both measured.** At 1280px the only mismatches are money: the
Series list renders "2 Episodes · $89.00" on the server and "A$89.00" in the
browser, and `/pricing` "GBP 30" and "£30". The server renders in the
machine's locale (`en-AU` here, which writes AUD as "$" and GBP as its code),
the browser in its own. At 375px every page with the sidebar adds two more:
the sidebar trigger's icon, and a `Sheet` the server never rendered. The Peers
page, whose dates use the runtime's locale too, showed none at 1280px.

**The reader's locale is decided once, on the server, and handed to the page.**
`money.ts` formats "in the reader's own locale" on purpose (`T-058`), so the
fix keeps that and makes both renders agree on who the reader is: a shared
Inertia prop `locale`, the first language of the request's `Accept-Language`
as a BCP 47 tag, `en` when there is none. `formatMoney()` takes it as a third
argument, and `Pricing.vue`'s `amount()` the same, so the server and the
browser format with one locale. Not a fixed locale: that would reverse
`T-058`'s decision for every reader outside it.

**Dates take the same locale, and a zone.** The nine `toLocaleDateString()` and
`toLocaleString()` calls that pass `undefined` pass the shared `locale`, and
the date ones a `timeZone` — the signed-in person's resolved zone
(`auth.user.timezone`), or UTC for a guest — so the day cannot change across
midnight between the server's zone and the browser's. `SessionTime.vue` keeps
its own rules (`T-027`), which already name the zone.

**The sidebar's first render assumes a desktop, on both sides.** VueUse's
`useMediaQuery()` asks `matchMedia` during the browser's first render —
`useSupported()` reads its mounted flag without using it — so a phone decides
"mobile" before hydration while the server, with no window, said desktop.
`SidebarProvider` passes `ssrWidth: 1024`, which makes the first render on
both sides the desktop one; the browser's real width applies straight after,
as an update rather than a mismatch. The open state already comes from the
`sidebar_state` cookie the server reads.

## Preconditions

**Data this task verifies against:** the dev server's seeded pages.

**Equipment:** a browser at 375 and 1280px reading the console, which the dev
server's development build of Vue fills with each mismatch's node.

## Scope

**In:**

- The `locale` shared prop, and `formatMoney()` and `Pricing.vue` using it.
- The nine date and number calls that use the runtime's locale.
- `SidebarProvider`'s `ssrWidth`.

**Out:**

- `SessionTime.vue`, whose zone rules are `T-027`'s.
- What the reader's locale means for words: `T-006`'s i18n.

## Files

| Path                                                     | Change | Notes                                  |
| -------------------------------------------------------- | ------ | -------------------------------------- |
| `app/Http/Middleware/HandleInertiaRequests.php`          | edit   | the `locale` shared prop               |
| `resources/js/types/global.d.ts`                         | edit   | `locale` on the shared props           |
| `resources/js/lib/money.ts`                              | edit   | `formatMoney(cents, currency, locale)` |
| `resources/js/composables/useReaderLocale.ts`            | new    | the prop, and the viewer's zone        |
| `resources/js/pages/**/*.vue`                            | edit   | the callers: money and dates           |
| `resources/js/components/ui/sidebar/SidebarProvider.vue` | edit   | `ssrWidth`                             |
| `tests/Feature/ReaderLocaleTest.php`                     | new    | 3 cases                                |

Flows: none — no call chain changes; the prop is presentation.

## Database

None.

## Code

```ts
export function formatMoney(
  cents: number,
  currency: string,
  locale: string,
): string;
export function useReaderLocale(): {
  locale: ComputedRef<string>;
  timeZone: ComputedRef<string>;
};
```

## Copy

None.

## Routes

None.

## Tests

**New: `tests/Feature/ReaderLocaleTest.php` — 3 cases**

1. `test_the_page_carries_the_readers_locale` — `Accept-Language: en-US,en;q=0.9`
   → `locale` is `en-US`.
2. `test_a_request_with_no_language_reads_as_english`.
3. `test_an_underscore_tag_becomes_a_hyphenated_one` — `zh_CN` → `zh-CN`.

The rest is the browser: no JavaScript test runner exists, so the proof is the
console at 375 and 1280px on the pages above, before and after.

## Acceptance

- [ ] No page logs a hydration mismatch at 375 or 1280px: the Series list, a Series, `/pricing`, the Peers page, the dashboard
- [ ] Money still reads in the reader's own locale
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~What differs.~~ **Measured 28 September 2026** (Decisions).
- ~~Whether one shared cause explains every page.~~ **Two do** (Decisions).

## Re-scope log

None.

## Notes

Found again during `T-043`'s browser walk, 22 September 2026.
