# Draft triage, 21 September 2026

**Nothing has been changed.** This is a report on the 70 `draft`, 8 `ready` and
3 `blocked` tasks, written so the deletions and re-scopes can be approved in one
pass rather than discovered one at a time.

Ordered to the stated priority: **onboarding and storage integration first.**

## How far each claim was checked

- **Verified by reading both files**: the five onboarding drafts against the
  done work, `T-028` against `T-075`, `T-091` and `T-094` against the decisions
  that reversed their design.
- **Classified from the task's front matter, its stream and the done list**:
  everything else. A `re-scope` below that was not verified is a *suspicion
  worth ten minutes*, not a finding.

| Verdict | Meaning | Count |
| --- | --- | --- |
| **Keep** | Wanted, and the spec still matches the code | 52 |
| **Re-scope** | Wanted, but part of it is already built or a decision moved under it | 11 |
| ~~**Superseded**~~ | Guessed at 4 — **checked, and none of them were** | 0 |
| **Split** | Too large to be made ready as written | 3 |

---

## Priority: the onboarding ↔ storage junction

This is where the two streams meet, and it is the right place to start: the
junction is `T-044` (done — connect a storage account *from onboarding or from
a settings page*) meeting `T-075` (done — creator setup in three skippable
parts). Both ends exist. What is missing is the middle.

### Onboarding — all five drafts

| Task | Verdict | Why |
| --- | --- | --- |
| **T-028** — Skippable storage, integrations and seller payment setup | **Re-scope, hard** | Most of it shipped. `T-075` built the three-part frame, the skip and finish writes, and resuming at the right part; `T-044` built the storage connection. `T-075`'s own **Out** list defers exactly one thing here: *prompting for seller setup at the paid action*. What genuinely remains is that prompt, an honest storage stage that distinguishes Qori uploads from external connections, an integration stage showing only working choices, and a route back after Skip. That is an **S or M**, not the **L** it still carries. |
| **T-025** — Show and send every time in a chosen timezone | **Keep — and raise it** | `T-024` stores a timezone and deliberately consumes nothing. Today browser-rendered dates are in the viewer's zone *by accident* and server-rendered ones are UTC, so the same date disagrees between a page and an email. This is a live correctness bug, not a nicety, and the classroom stream is about to make it much more visible. |
| **T-026** — Creator setup, then guided first-Series | **Split** | Already narrowed once — `T-068` took the naming. What is left is the guided first Series plus "basic details". The task says itself that its `L` is a sign it should be cut again. Two tasks: basic details; guided first Series. |
| **T-027** — Series-linked signup, payment and receiving onboarding | **Re-scope** | `T-073` and `T-074` shipped two of its pieces (access from the Series page without leaving it; after the code, straight to access). Re-read against what exists before specifying. |
| **T-086** — The rename card still says "Name your Group" | **Keep — easy win** | `S`, no dependencies, and three separate browser walks reported it. The description already switches on whether a name was chosen; the title does not. |

### Storage — 18 drafts, 1 blocked

**These are in better shape than their age suggests.** The stream has been kept
current: `T-091` and `T-094` were both re-drafted after the decisions that
reversed their design, and `T-094` says so at the top. Two notes:

- **The filenames lie, deliberately.** `T-091` is still
  `...granted-on-the-series-container.md` and `T-094` is
  `...from-a-series-folder...`, after both moved to per-file grants. `T-094`
  records that the name is kept so the spike's report and links still resolve.
  Fine — but a reader skimming the directory will draw the wrong conclusion.
  Worth one line in `PROCESS.md` saying filenames are frozen at creation.
- **`T-091` is the keystone.** It blocks eight tasks
  (`T-092`, `T-094`, `T-096`, `T-098`, `T-100`, `T-101`, `T-103`, `T-157`) and
  depends on five. Nothing else in storage moves until it is ready. It was
  consolidated, then independently verified and found *still* not ready. It is
  the single highest-value thing to finish specifying in the whole plan.
- **Three spikes are gated on accounts** (`T-095` Dropbox, `T-097` OneDrive,
  `T-099` Zoom) and `D-042` now says an integration that cannot be developed
  free goes back to you to re-approach **or drop**. Dropping is a real outcome
  now; these three need that call before they are worth specifying.

| Verdict | Tasks |
| --- | --- |
| **Keep** | `T-090`, `T-092`, `T-094`, `T-096`, `T-098`, `T-100`, `T-101`, `T-141`, `T-142`, `T-149`, `T-150`, `T-157` |
| **Keep, but decide free-or-drop first** (`D-042`) | `T-095`, `T-097`, `T-099`, and blocked `T-122` |
| **Split** | `T-091` — `L`, blocks eight, twice failed to reach ready |

---

## The rest, by stream

### ~~Superseded~~ — checked, and **none of the four were**

> **Verified 21 September 2026, same day.** The four checks named below were
> run. **Zero were superseded.** The classification was made from titles and the
> done-list without reading the code, and reading the code reversed all four.
> This is the argument for the rule that nothing is deleted on a suspicion.

| Task | Guess | What the check actually found |
| --- | --- | --- |
| **T-014** — unreachable capabilities | done by `T-012`/`T-046`/`T-067` | **Half right, and the good half is real.** `qori:reachability` now reports **no unreachable routes at all** — that part of the task is satisfied. What remains is two `public` service methods nothing calls from outside their own class (`AccessService::peerFor`, `SuppressionService::suppress`); both are called internally, so the fix is `private` or an allow-list entry with a reason. **Re-scope to S**, do not close. |
| **T-104** — pricing page leads somewhere | done by `T-050` | **No.** `resources/js/pages/Pricing.vue` is 92 lines with no `Link`, no `href`, no lockup, no header and no call to action. The dead end is exactly as reported. **Keep.** |
| **T-118** — words the renames mangled | done by `T-041`/`T-056`/`T-116` | **No — and this one should be raised.** `T-116` fixed only the string a password manager reads. Everything else is still there: `guardGrantlable()` ×4, "grantlable" ×8, "Grantling" ×6, `/w/` in the flow docs ×8. Including **a live buyer-facing string**: `lang/en/accesses.php:76` reads *"Please agree to be peered before granting."* A buyer who leaves the consent box unticked sees that sentence today. **Keep, and treat the lang line as a defect rather than a tidy-up.** |
| **T-153** — Integrations page claims | done by `T-067` | **No.** The task had already narrowed itself: its own **Why** records the count query as *verified, no defect*, and its remaining scope is one assertion — what a non-owner collaborator sees when a write is refused in a browser. **Keep at one test row.** |

### The reachability scan has a blind spot worth knowing

`qori:reachability` reporting "routes nothing links to: none" does **not** mean
nothing built is invisible. It cannot flag a capability that has **no routes at
all** — which is precisely `T-045`, campaigns: built, tested, and with no route
to be unreachable. The scan answers "is every route linked", not "is everything
built reachable", and the plan's own headline still says three features had no
way in. Worth a line in the `reachability` stream so a clean scan is not read as
a clean bill of health.

### Re-scope — a decision moved under them

| Task | What moved |
| --- | --- |
| `T-102` — A delayed payment still becomes access | `D-040`: grants are inline at Open now, with no sweep. Check the confirming path assumes no reconciler. |
| `T-103` — A refund revokes access and the vendor grant | `D-040` (revocation is inline, once, failures surfaced not retried) and `D-041` (revoke on the **last** entitlement, not the first). |
| `T-157` — The creator fixes a grant that did not land | Written before `D-040` made the creator-pressed retry the *only* retry. It is now more central than its draft status suggests. |
| `T-085` — The public Series page still offers to buy when disconnected | `D-023` replaced account creation with OAuth-only connect; the disconnected states changed shape. |
| `T-045` — Campaigns reachable from nowhere | Still true and still a headline on the plan, but `D-035`'s vendor-naming rule and the communications policy both landed after it. |
| `T-005`, `T-006` — vocabulary into mail/PDFs, and Vue inline English | `T-004` shipped the settings form; these are the consumers. Check the lang-file rule's current coverage first. |

### Keep as written

**delivery** `T-017`, `T-055`.

> **`T-032` closed the same day this was written.** It was called the most
> urgent unclaimed task here; the owner cleared it on 21 September 2026 and
> mail is confirmed arriving. What that leaves is narrower and still open: the
> SPF/DKIM/DMARC result and the receiving providers were not recorded, and
> `T-017` will need them.

**design** `T-040`, `T-088`, `T-105`, `T-106`, `T-107`, `T-108`, `T-109`,
`T-110`, blocked `T-022`.
**operations** `T-018`, `T-019`, `T-020`, `T-021`, `T-117`, `T-148`, `T-156`.
**reachability** `T-013`, `T-155`.
**recovery** `T-011`, `T-115`.
**selling** `T-043`, `T-049`, `T-079`, `T-114`.
**classroom** `T-128`, `T-129`, `T-132`, `T-133`, `T-135`, `T-137`, `T-138`,
`T-139`, `T-140`, `T-143`, `T-144`.
**workflow** `T-145`, `T-154`, blocked `T-121`.

---

### Corrected the same day: the consent line is not what a buyer sees

The **T-118** row above says a buyer who leaves the consent box unticked sees
*"Please agree to be peered before granting."* today. **They do not.** The
browser walk on 21 September 2026 found the public page disables Continue
until the box is ticked, and pressing Enter does not submit past it, so the
line is only reachable by bypassing the page's own check. The string is still
wrong and still belongs to `T-118`, but it is a fixup, not a live defect. What
a person does meet is a button that looks dead with no reason given — see the
onboarding walk in `walkthroughs.md`.

## What this says about the plan as a whole

**70 drafts against 8 ready is the wrong ratio**, and the board's own target is
4 ready. The drafts are not junk — the triage found only four plausibly
superseded — but a draft is a promise to specify something later, and 70 of
them is a backlog that cannot be read.

Three observations:

1. **The bottleneck is specification, not building.** 76 tasks are done and 8
   are ready. The queue is starved at the front.
2. **`T-091` alone gates eight tasks.** Storage cannot start until it is ready,
   and it has twice failed to get there. It deserves a dedicated session with a
   fresh reader, not another consolidation pass by whoever wrote it.
3. **Three streams block beta on work nobody has specified**: delivery (mail
   that arrives), operations (alerting, restore) and storage. Design is the
   fourth, and its drafts are small and specifiable.

## Recommended order

1. ~~**`T-032`** — prove mail arrives.~~ **Done, 21 September 2026.** Worth one
   line in `walkthroughs.md` recording which providers and whether
   authentication passed, which `T-017` will need.
2. **`T-086`** — the rename card. `S`, no dependencies, three reports.
3. **`T-028` re-scoped down** to the seller prompt and the honest storage
   stage. Closes the onboarding ↔ storage junction with what is already built.
4. **`T-025`** — timezones, before the classroom stream multiplies the bug.
5. **`T-091` split and specified**, with a fresh reader. Unblocks eight.
6. **The free-or-drop call** on `T-095`, `T-097`, `T-099`, `T-122`.
7. ~~**The four supersession checks.**~~ **Done — none were superseded.** The
   by-product worth acting on: `lang/en/accesses.php:76` shows buyers
   *"Please agree to be peered before granting."* today.
