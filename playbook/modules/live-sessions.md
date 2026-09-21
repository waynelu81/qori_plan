# Module: live sessions

**What it is.** A scheduled session inside a product — a class, a call, a
consultation — that starts, ends, may be recorded, and whose recording reaches
the people entitled to it.

**Done when.** A participant with an entitlement has one place to go for a
session before, during and after it; a session that was recorded produces a
recording they can reach; and a cancelled session says so.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| Is a recording a second unit of content? | No — a row beside the session | Progress and certificates count the session; a recording that counted separately would double it. |
| Does a session have an end? | Yes, stored, required, entered as a length | State computed from a start alone cannot distinguish "running" from "long over". |
| Is state stored or computed? | Computed from start and end | Stored state needs something to write it, which means a scheduler, which means a second source of truth. |
| Where does a recording come from? | Pasted by the creator (published immediately) or found by the product (held for review) | Something the product found may be the wrong meeting instance; something pasted was chosen. |
| How are notices tracked? | A ledger row per (session, recipient, kind, publication) | Makes "did they get told" answerable and resends idempotent. |
| Are materials part of the session? | Yes — an ordered, labelled, released list on it | Preparation, material and homework are the same shape with different labels and release rules. |

## Build order

1. **An end time on the session**, required, entered as a length, with the
   start moving out of any free-form payload onto its own column.
2. **Computed state** — upcoming, running, over, cancelled — from those two.
   Needs 1.
3. **Correction**: the creator can fix the link, time and length. Needs 1.
4. **Recordings as rows**, with a source, a vendor reference where there is
   one, and a published/held distinction. Needs 1.
5. **Materials** — ordered, labelled, released, capped by config. Needs 1.
6. **The notice ledger and its sends**. Needs 2, 4, and a worker.
7. **Vendor integration** for hosted meetings — see
   [byo-vendor-integration](byo-vendor-integration.md); a meeting is just
   another container to grant on.

## Rules that bite

- **A participant has exactly one destination for a session**, before, during
  and after. Anything else means they have to work out where to look.
- **Do not migrate existing content into a new shape while the shape is new.**
  Qori kept the existing primary item where it was and added the new rows
  beside it, leaving the fold-in as a later, separate task.
- **The unit of progress is the session, not the artefacts on it.**

## Native contract

**Not proven.** Join links open in the system browser or the vendor's own app,
never a webview. Session times must be rendered in the participant's timezone,
which means the API sends an absolute instant and the client formats it.

## Traps

| Symptom | Cause |
| --- | --- |
| "A finished session still says Join" | State from a start with no end. |
| "The wrong recording appeared on a session" | A found recording published without review. |
| "Participants were notified twice" | No ledger uniqueness key. |
| "Times are wrong for some people" | No timezone captured at signup, or a formatted time sent from the server. |

## Proven / Not proven

**Proven**: the end time and computed state; correction of link, time and
length; materials on a session.

**Not proven**: recordings end to end; the notice ledger and any send; the
meeting-vendor integration; the whole participant-facing half — a live session
is currently a dead end for the participant, which is what this stream exists
to close.

## Source

Qori tasks `T-123`, `T-124`, `T-130`. Decisions `D-024` to `D-031`.
Stream `classroom`.
