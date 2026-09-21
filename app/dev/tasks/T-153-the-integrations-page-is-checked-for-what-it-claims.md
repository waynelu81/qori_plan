---
id: T-153
title: The Integrations page is checked for what it claims
stream: reachability
status: draft
owner: unassigned
estimate: S
depends: T-044
blocks: none
---

# T-153 — The Integrations page is checked for what it claims

> **Written on 20 September 2026 from two findings in `T-044`'s report.** Both
> are about the same page telling a creator something nobody checks. Neither
> was fixed there, because one belongs to `T-064`'s line and the other is a
> testing gap that a frozen spec could not be widened to cover.
>
> **The first finding was checked on 20 September 2026 and is not a defect.**
> The count is scoped, and the test this task was going to write already
> exists. What is left of the first half is a judgement call about a comment,
> recorded under "Before this can be ready". The second finding stands.

## Why

**The count of priced Series is the creator's own — verified, no defect.**
`app/Http/Controllers/Share/IntegrationsController.php:51` builds
`pricedSeriesCount` with `Series::query()->whereNotNull('price_cents')->count()`
and no explicit group scope, which is why it was worth reading. It is scoped by
`GroupScope` and always has been. `Series` uses `BelongsToGroup`
(`app/Models/Series.php:49`); `GroupScope::apply()`
(`app/Models/Scopes/GroupScope.php:22`) adds
`where('group_id', CurrentGroup->idOrFail())`; and the route is registered
inside `middleware(['auth', 'verified', 'group'])` (`routes/share.php:25`), so
`SetCurrentGroup` (`app/Http/Middleware/SetCurrentGroup.php:45`) has set the
context before the controller runs. The SQL the line actually emits, with
context set:

```
select * from "series" where "price_cents" is not null and "group_id" = ?
```

The predicate is dropped only by the explicit `acrossAllGroups()` scope, which
this line does not use. It also fails closed rather than open: with no context
`idOrFail()` throws, so a missing group surfaces as a `RuntimeException`
instead of a count of every Group's priced Series.

**And the test is already written.**
`tests/Feature/Share/PaymentsDisconnectTest.php:153`,
`test_the_page_counts_priced_series_for_the_dialog()`, creates two priced
Series and one free one in the current Group and a fourth priced Series in a
second Group, then asserts the prop is `2`. `SeriesService::create()` stamps
`group_id` from the Group it is passed (`app/Services/SeriesService.php:46`),
so the fourth row genuinely belongs elsewhere and an unscoped count would
answer `3`. That is this task's own acceptance bar — a test that would fail if
the scope were removed — met verbatim, and its docblock already says "Scoped to
this Group". The whole file passes, 7 of 7.

So the count rendered at `resources/js/pages/share/settings/Integrations.vue:50`
and `:224`, and the warning it drives at `lang/en/payments.php:43` — "`:count`
priced `:series_plural` will stop being purchasable" — are telling the truth,
and were never a cross-tenant leak.

**Nothing checks what an admin actually sees when they are refused.**
This finding stands, and re-reading it is what is left of the task.
`T-044`'s cases assert 403 through `postJson`, because its spec said 403.
`tests/Feature/Share/PaymentsDisconnectTest.php:119-126` asserts the same
refusal as a redirect, because that is what a form POST really gets:
`AppException::render()` (`app/Exceptions/AppException.php:248-288`) returns a
status response only when the request expects JSON or the method is `GET`, and
otherwise flashes a toast and returns `back()`. Both tests are right about
their own request. Neither covers the browser path — an admin pressing Connect
or Disconnect on the page and seeing a redirect and a toast — so the copy in
that toast is rendered by nothing any test reads. Confirmed on 20 September
2026: `test_an_admin_is_refused()` asserts the redirect and the unchanged
`connect_account_id` column, and nothing in that file asserts the flashed
message at all.

Afterwards the second claim is checked, and has one asserted answer rather than
two half-answers.

## Decisions taken to make this specifiable

**None yet.** See "Before this can be ready".

## Preconditions

**Data this task verifies against:** a clean database; the test builds a Group
and a non-owner collaborator in it.

**Equipment:** none.

**`T-044` done**, because the browser-path case acts against
`share.connections.begin`, which `T-044` creates, and belongs beside the cases
it complements. The first finding no longer depends on it — that half touches
no file `T-044` holds.

**Spike:** none. No vendor payload is named.

## Scope

**In:**

- One asserted answer for what a non-owner collaborator sees when a write on
  the Integrations page is refused in a browser: the redirect, the flashed
  toast and its copy.

**Out:**

- **Any change to `IntegrationsController.php:51`, and any new test of the
  count.** Checked on 20 September 2026: the query is scoped, and
  `PaymentsDisconnectTest::test_the_page_counts_priced_series_for_the_dialog()`
  already proves it to this task's acceptance bar. Whether to add a comment is
  the one question left, below.
- Any change to `AppException::render()`. Its behaviour is the app's, is
  deliberate, and is relied on by every form in the product.
- Re-opening `T-044`'s frozen assertions. Its `postJson` cases stay as they
  are; this task adds the browser reading beside them rather than replacing it.
- The duplicated comment block at `Integrations.vue:141-154`, which `T-044`'s
  report decided is not worth a commit of its own.

## Files

> One row, unless the comment question below is answered yes — in which case
> `IntegrationsController.php` joins it and this task must rebase onto `T-044`.

| Path                                                                                                 | Change | Notes                                                     |
| ---------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------- |
| `tests/Feature/Share/IntegrationsPageTest.php` _or_ `tests/Feature/Share/ConnectionsConnectTest.php` | edit   | The browser-path refusal case; which file is question two |

Flows: none — this changes no call chain.

## Database

None.

## Code

None. Both halves are tests; the first half is already written.

## Copy

None. The toast copy this task asserts already exists.

## Routes

None.

## Tests

> One case, once question two is answered: acting as a non-owner collaborator
> against `share.connections.begin` and `share.payments.disconnect` with a
> plain form POST, asserting the redirect and the flashed toast copy — the part
> `test_an_admin_is_refused()` leaves unasserted.

## Acceptance

- [x] `pricedSeriesCount` is proven to count only the current Group's priced
      Series, by a test that would fail if the scope were removed — **already
      true** via `PaymentsDisconnectTest:153`; verified 20 September 2026, no
      change needed
- [ ] What a non-owner sees when a write on this page is refused in a browser
      is asserted once — the redirect and the toast copy — beside `T-044`'s
      JSON cases
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- ~~**Is `pricedSeriesCount` actually unscoped?**~~ **Answered 20 September
  2026: no, it is scoped, and the regression test already exists.** Evidence
  in "Why". This removed the whole first half of the task.
- **Does the bare query want a comment saying why it is safe?** The remaining
  question from the first finding, and the recommendation is **no**. A bare
  `::query()` on a group-scoped model is the idiom — 30 such calls across
  `app/Http/Controllers` and `app/Services`, none annotated — and `CLAUDE.md`'s
  tenancy rule is that the trait is the guarantee precisely so a caller does
  not have to remember or restate it. Annotating this one line implies the
  other 29 were checked and this one was special. There is also a cost: the
  file is `T-044`'s, so a comment turns a no-file task into one that clashes
  with a task in flight and must rebase, for no behaviour. The owner's, and it
  is two minutes either way.
- **Whether the browser-path assertion belongs in
  `tests/Feature/Share/IntegrationsPageTest.php` or beside the cases it
  complements in `ConnectionsConnectTest.php`.** That file's own docblock says
  the page is Vue and there is no JavaScript test runner, which is the honest
  limit on what any of this can assert. Anyone's.
- ~~**Whether `T-064` would rather own the first half**~~ **Moot: there is no
  first half.** With the count verified and already covered, nothing here
  touches `IntegrationsController.php` or the Stripe Dialog, so the task is
  wholly `reachability`'s and `selling` need not be consulted — unless the
  comment question above is answered yes, which puts `T-064`'s file back in
  scope and the question back with it.

## Re-scope log

None. This task is a `draft`; the entries above answer its own open questions
rather than re-scoping a frozen spec.

## Notes

Both findings came from `T-044`'s report of 20 September 2026, which found
them while mapping the page it extends and deliberately did not fix them:
"that is how a task grows until nobody can review it".

The first was checked the same day, from a worktree, at the `T-044` owner's
request: scoped, covered, no defect. The reading cost ten minutes and is
recorded above so it is not paid twice — a bare group-scoped query looking
unscoped is a thing a reader will notice again on some other line, and the
answer is the same one every time.
