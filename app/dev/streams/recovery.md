---
stream: recovery
owner: wayne
---

# Stream: recovery

**Goal.** Give every dead end an exit that does not destroy what somebody paid
for.

**Done when.** A creator over their plan cap can get back under it without
losing enrolment or payment records, the product never promises a capability it
does not have, and no built-in action leads to a refusal the reader could not
have seen coming.

**State.** Archiving is built (`T-009`): instant, reversible, out of the plan
cap and off the public page, with every Peer keeping their access. It is the
over-cap lock's escape and the copy that offers it is true now.

Deletion is built too (`T-010`). It is deliberately the slower half — a
seven-day window and a scheduled sweep — and it keeps what belongs to the Peer
while removing what belongs to the creator.

## Tasks, in order

1. `T-009` — Archive a Series, with the consequences stated before confirming
2. `T-031` — Edit a Series: the title and summary a creator typed wrong are
   the first dead end anyone meets
3. `T-010` — Delete a Series on a seven-day timer
4. `T-011` — Remove copy that promises what the product cannot do: the audit
   runs against the product with archive and delete in it
5. `T-115` — Every error status renders Qori's own page: `T-113` found a
   refused landing showing the framework's bare page, and 401, 402 and 504 still do

## Notes

§7.2 puts refunds in the creator's own Stripe, so neither "archive" nor
"delete" may read as "refund". A Peer who paid keeps their access when a Series
is archived and keeps their payment record and certificate when one is deleted
— what they lose in the second case is the material itself, and the
confirmation has to say so.

**`T-010` added the first scheduled command Qori has.** The owner switched the
Laravel Cloud scheduler on the same day; nothing runs `schedule:run` locally,
so the sweep is driven by hand here (see the `operations` stream).
