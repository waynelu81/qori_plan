# Reachability findings

> What `php artisan qori:reachability` reports, and what to do about each one.
> Produced by `T-012`; this file is what `T-014` is scoped from.

[Current plan](../../PLAN.md) | [Stream](streams/reachability.md) | [Planning index](README.md)

First run: 9 September 2026.

## What the command checks, and what it does not

- **GET routes in `App\`** that no `.vue`, `.ts`, controller or route file
  links to, by name or by a hand-built URL. Package and framework routes are
  skipped; so is anything on the allow-list in `config/qori.php`.
- **Public methods on `App\Services\*`** that nothing outside their own class
  calls.

It does not look at models, tables, columns, components, lang keys or CSS.
Those have much higher false-positive rates and each deserves its own tool, if
any of them deserves one at all.

The matching is grep, deliberately — see the class docblock. A false positive
costs one allow-list line; a parser costs a dependency and a week.

## Routes: none

Every GET route in `App\` is linked from somewhere. The two the reachability
stream was written about have both since been connected:

- **Connect onboarding** (`share.payouts.connect`) is now reached from the
  Payments page, which explains what connecting means before it happens.
- **`share.payouts.return`** is allow-listed: Stripe redirects the creator
  there after onboarding, so nothing in Qori links to it and nothing should.

**Campaigns are not in this list, and that is not good news** — there are no
campaign routes at all. `CampaignService` and the `campaigns` table exist, and
nothing has ever been routed to them. A tool that looks for unreachable routes
cannot see a feature that was never routed, which is a real limit of this
approach and worth remembering before treating a clean run as a clean bill.

## Service methods: 2

| Class                | Method     | What it means                                                  |
| -------------------- | ---------- | -------------------------------------------------------------- |
| `AccessService`      | `peerFor`  | Called only from inside `AccessService`. Public overstates it. |
| `SuppressionService` | `suppress` | Called only by `bounce()` and `complaint()` in the same class. |

Neither is dead code, and neither needs a UI. Both are **public methods that
could be private**, which is what "nothing calls this from outside" actually
means most of the time. The fix is a keyword.

`SuppressionService::suppress` is worth a second look for a different reason:
its two callers, `bounce()` and `complaint()`, have no callers of their own
outside tests. Nothing feeds the suppression list from a real provider, which
is exactly `T-017`. The scanner found the shape of a missing integration by
noticing the end of a chain nobody enters.

## Known, and outside what this command can see

- **`payment_fulfilments`** records every failed payment and no screen reads
  it. `T-013` covers it. A table is not a route or a service method, so the
  command will never report this — the acceptance criterion in `T-012` that
  said it would was wrong, and has been corrected.

- **`episodes.starts_at` has no input.** The column exists, the validation
  exists, the controller sends it and three Vue files render it — and no form
  in the product sets it, so a live session cannot be given a time. Found by a
  person reading the Episode form, not by this command, which looks at routes
  and service methods rather than form fields. `T-029` fixes it.

    This is the most useful entry in this file, because it names a shape the
    scanner is blind to: **a capability that is fully wired except for the one
    end a human touches.** Every route resolves, every method is called, and the
    feature does not work. If this file grows a second example of that shape, the
    scanner needs a third check rather than another allow-list line.

    **Fixed on 10 September 2026 by `T-029`**, and the fix found something the
    original finding did not: adding the field naively would have been worse
    than leaving it out. `config('app.timezone')` is UTC, so a naive
    `datetime-local` string parses as UTC and a Melbourne creator's 9am becomes
    their Peers' 7pm. The entry stands as a record of the shape rather than as
    an open item.

## Not wired into CI yet

Deliberately. A new check that fails the day it lands is a check somebody
switches off. `T-014` wires it in once this list has been worked through and
the allow-list has settled.
