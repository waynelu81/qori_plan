# Reachability findings

> What `php artisan qori:reachability` reports, and what to do about each one.
> Produced by `T-012`; this file is what `T-014` is scoped from.

[Current plan](../../PLAN.md) | [Stream](streams/reachability.md) | [Planning index](README.md)

First run: 9 September 2026.

## What the command checks, and what it does not

- **GET routes in `App\`** that no `.vue` or `.ts` file, and no PHP file
  under `app/` outside `app/Console`, links to — by name, by importing its
  Wayfinder helper, or by a hand-built URL. Package and framework routes are
  skipped; so is anything on the allow-list in `config/qori.php`. Until
  `T-051` a route's own registration in `routes/`, and any test that visited
  it, counted as a link — so no named route could ever be reported (below);
  until `T-208` a developer command's printed address did too.
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

## Second run, after `T-051`: 27 September 2026

**Routes: none, and three of them by accident.** With `routes/` and `tests/`
out of the haystack, all 47 GET routes still count as linked: 45 by their
name in the frontend or in `app/`, two by a URL a Vue file builds by hand
(`shared.play`, `share.payments.begin`). The name in `app/` is almost always a
real way in — a redirect, an email, a vendor's return address, a prop that
carries a URL — with three exceptions:

| Route                   | Named in `app/` only by | How a person actually gets there                               |
| ----------------------- | ----------------------- | -------------------------------------------------------------- |
| `security.edit`         | `DesignReviewCommand`   | The settings layout imports `@/routes/security`                |
| `share.vocabulary.edit` | `DesignReviewCommand`   | The Group settings layout builds `${base}/settings/vocabulary` |
| `share.peers.index`     | `DesignReviewCommand`   | The sidebar builds `${base}/peers`                             |

All three are reachable, and the scan cannot see how: a Wayfinder import names
a module and an export rather than a route, and `${base}/…` hides the
`/g/{group}` prefix the URI pattern needs. A developer command that prints
review URLs is what makes them pass, so the scan would call them unreachable
the day it stopped naming them. `T-208` teaches the scan Wayfinder imports and
stops counting developer commands.

The allow-list is empty today. `share.payouts.return`, allow-listed at the
first run, became `payments.oauth.finalise` (`D-033`), which
`PaymentsController` names as the address Stripe sends the creator back to.

**Service methods: 3.** The two below, and `RecordingService::recordingOf`,
which only `RecordingService` calls: the same shape as `peerFor`, a public
method that could be private. The method half still counts `tests/` as a
caller; `T-051` left it alone so that neither change could hide the other's
findings.

## Third run, after `T-208`: 27 September 2026

**Routes: none, and none by accident.** The scan now counts a Wayfinder
import — `import { edit } from '@/routes/security'` — as the link it is, and no
longer reads `app/Console`, whose commands print addresses for developers. The
six `${base}/…` links in the sidebar and the Group settings layout became
Wayfinder calls. Of the 47 GET routes, 13 are linked through an import, 4 by
their name in the frontend, 20 by their name in `app/` — a redirect, an email,
a vendor's return address or a URL in a prop — and 10 by a URL a page builds
in full. Before the six links were converted, the run reported one route,
`share.vocabulary.edit`, whose only way in was `${base}/settings/vocabulary`.

**Service methods: 2**, and one of them left for the wrong reason.
`AccessService::peerFor` and `RecordingService::recordingOf` remain.
`SuppressionService::suppress` left the list because `T-194`'s test now calls
it — the method half still counts `tests/` as a caller, the weakness `T-051`
left for a separate look.

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
