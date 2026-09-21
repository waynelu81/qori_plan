---
stream: reachability
owner: wayne
---

# Stream: reachability

**Goal.** Nothing built is invisible, and nothing visible is unfinished.

**Done when.** Every GET route and every service has either a discoverable way
in or an explicit, recorded decision to defer it — and the admin console can
answer "which payments failed to become access".

**State.** The inventory was walked by hand on 11 September 2026 and is worse
than this stream assumed. Three capabilities are built, tested and reachable
from **nothing at all**: connections, campaigns and collaborators. Connect
onboarding, this stream's original example, has been linked since the redesign.
`payment_fulfilments` still has no reader. `ShareDigest::nextAction()` was in
this category until Day 3 of the redesign, which is the pattern this stream
exists to catch earlier.

**And the command cannot find any of them.** `qori:reachability` looks for
routes nothing links to. A capability with no routes has nothing to report, so a
clean run says only that everything routed is linked. `T-012`'s report said this
on the day it shipped; it took a hand audit two days later to produce the list.

## Tasks, in order

1. `T-012` — A command that lists routes and services with no way in
2. `T-051` — A route counts as linked to itself: the command's haystack
   includes the page a route renders, so a page linking only to itself passes
3. `T-067` — Integrations are a settings page — Stripe first, under Settings,
   where the owner says integrations belong
4. `T-045` — Campaigns are built, tested, and reachable from nowhere
5. `T-046` — A Group cannot have a second person in it
6. `T-013` — Failed fulfilments in the admin console
7. `T-014` — Finish or explicitly hide each unreachable capability: an index
   of the three above rather than work of its own, and it closes when they do
8. `T-023` — Fixed-value attributes become PHP enums

`T-044` — nothing in the product can connect a storage or video account — was
first among the capabilities because its failure lands on the wrong person:
nothing refuses an Episode whose provider is not connected, so a creator can
publish a video that only fails when a Peer tries to watch it. On 16 September
2026 it moved to the `storage` stream, which `D-016` created around it: the
connect flow is the first slice of every storage and live-session integration,
and the tasks that follow it share its files. `T-014`'s index still counts the
capability here.

`T-023` is here because it is the same problem in a different shape:
`Series::STATUS_ARCHIVED` was declared and read by nothing for a month, and a
`cases()` call would have surfaced it the day it was added. `T-012` finds
routes and methods nothing reaches; enums make a _value_ nothing reaches
visible too.

## Notes

`T-012` first, deliberately. The inventory decides what `T-014` contains, and
guessing that list is how a reachability audit turns into a rewrite.
