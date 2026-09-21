# Module: recovery and deletion

**What it is.** Archive, delete, and the principle that no built-in action ever
leads somewhere the reader cannot act.

**Done when.** Every destructive action states its consequences before it is
confirmed, deletion is reversible for a stated window, and no path in the
product ends on a dead page.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| Immediate delete, or a timer? | A timer — seven days | Reversible by default. The alternative is a support request that cannot be satisfied. |
| What happens to what people already bought? | Preserved — access and payment history survive the deletion of the thing | The record of a transaction is not the seller's to delete. |
| Are consequences stated before confirming? | Yes, specifically — what happens to buyers, to payments, to the link | A generic "are you sure" transfers no information. |
| Can a next-action prompt point at something archived? | No | Encouraging copy pointing at a dead end is worse than no copy. |
| Does the product delete a customer's files at a vendor? | Never — see [byo-vendor-integration](byo-vendor-integration.md) | |

## Build order

1. **Archive** — reversible, with consequences stated, and everything that
   surfaces "what next" taught to skip archived things.
2. **Delete on a timer**, preserving access and payment history. Needs 1.
3. **A sweep** that performs the deletion once the timer expires. Needs 2.
4. **Editability** — the thing can be changed after creation, so deletion is
   not the only correction. Independent, and it removes most deletions.

## Rules that bite

- **Blocking and permission states outrank encouraging next-action copy.** If
  the person cannot do the thing, do not invite them to.
- **The sweep is a real job with a real failure mode.** Deleting on a timer
  without a worker means never deleting.
- **Editing is the cheapest recovery feature.** Most "delete and start again"
  is a missing edit form.

## Native contract

**Not proven.** Destructive confirmations must restate consequences on the
client; a native client cannot rely on a web page's wording.

## Traps

| Symptom | Cause |
| --- | --- |
| "The dashboard suggests something that was archived" | Next-action queries not filtering archived rows. |
| "Deleting removed a buyer's purchase record" | Cascading past the boundary of what the seller owns. |
| "Nothing is ever actually deleted" | The timer exists, the sweep does not. |

## Proven / Not proven

**Proven**: archive with stated consequences; delete on a seven-day timer
preserving access and payment history; editability after creation; next-action
copy skipping archived things.

**Not proven**: the sweep running unattended in production.

## Source

Qori tasks `T-009`, `T-010`, `T-031`, `T-033`. Stream `recovery`.
