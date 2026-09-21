# Module: onboarding

**What it is.** Getting a new person from "account created" to "did the thing
the product is for", by the shortest path that matches why they arrived.

**Done when.** A person who arrived to *buy* is never shown *seller* setup; a
person who arrived to *build* is walked through setup they can skip; and where
they are up to survives signing out.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| One onboarding, or one per entry purpose? | One per purpose | Someone who followed a link to buy something has no use for payout setup, even if their account could also sell. |
| Is the entry purpose stored? | **No** — read once at registration, never persisted | It is a runtime decision. What is durable is what they *have*. A stored intent drifts the moment they do something else. |
| Where does progress live — on the person or the tenant? | The person | The walk is the person's. The tenant keeps the *facts* the walk reads beside — a chosen name, a connected account. |
| Are setup steps skippable? | Yes, all of them | Blocking on payout setup before they have made anything is asking for a commitment they cannot yet evaluate. |
| When is payout setup prompted? | Before selling something paid — not before creating anything | The obligation appears with the sale. |
| Same fact in two places? | Never | Qori kept "has the tenant been named" on both the tenant and the person's record; it was the same bookkeeping twice and one copy was dropped. |

## Build order

1. **Ask the entry purpose at registration**, use it in the same request to
   decide what to create, and discard it.
2. **Ask for a timezone and store it** — everything scheduled is wrong without
   it, and it is cheapest to ask at the start.
3. **A progress record on the person**: which parts finished or skipped, and
   when the walk ended. Needs 1.
4. **One question — "what is next for this person?"** — answered in one place,
   and honoured by the home routes. Needs 3.
5. **The buyer path**: confirm details, verify or pay as required, get access,
   open the thing. Needs 2.
6. **The creator path**: details, tenant details, then storage, integrations
   and payouts — each skippable — then a guided first build. Needs 3, 4.

## Rules that bite

- **The home route is the honourer.** If the next step is decided in one place
  and the home route ignores it, people land in limbo.
- **Creating a tenant resets the walk**, or a second tenant starts halfway
  through.
- **Guidance sits where the person acts**, not in help, and a wait they can end
  has a button that ends it.
- **A buyer sees what the thing needs from them *before* paying** — including
  which vendor account they will need.

## Native contract

**Not proven.** The progress record must be readable by a native client so the
walk resumes across platforms; it is the person's state, not the web session's.

## Traps

| Symptom | Cause |
| --- | --- |
| "A buyer is being asked to set up payouts" | One onboarding for everybody. |
| "Onboarding restarts after signing out" | Progress kept in the session. |
| "Session times are an hour out for some people" | No timezone asked at signup. |
| "Two places disagree about whether setup finished" | The same fact recorded twice. |

## Proven / Not proven

**Proven**: the purpose-driven split, timezone capture, progress on the person
honoured by both home routes, three skippable creator parts, access-from-the-
Series-page without leaving it.

**Not proven**: the guided first-build flow end to end.

## Source

Qori tasks `T-024`, `T-029`, `T-068`, `T-073`, `T-074`, `T-075`, `T-076`,
`T-078`. Decisions `D-001`, `D-007`, `D-011`, `D-021`. Stream `onboarding`.
