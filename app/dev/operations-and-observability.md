# Operations and observability

> Queue, scheduler, activity-log, Sentry and error-contract research and decisions.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## A queue and scheduler are coming, but not now (2026-09-06)

Confirmed: a queue service will be added, later. Everything specified in the
meantime has to work on `sync`, and anything that genuinely needs a clock —
course reminders above — waits for it rather than being faked with a request-time
hack.

## Activity log — how a thing got to its current state

Wanted: the Xero-invoice pattern, applied to Qori. Enrolling a student, a student
changing their details, an EDM going out, a course being created or edited —
each leaves a line, and reading the lines tells you how the record reached the
state it is in. The concern was data volume, which is the right concern.

### One interface, two collections — and the split is deliberate

`StaffAuditLog` already has the shape to copy: `action`, `subject_type`,
`subject_id`, `workspace_id`, `metadata`, and a static `record()`. The new
`activity_log` mirrors it exactly, so both are written the same way and a reader
learns one shape.

They stay **separate collections**, because they differ on every axis that
matters:

|                      | `staff_audit_log`                                           | `activity_log`               |
| -------------------- | ----------------------------------------------------------- | ---------------------------- |
| Audience             | Compliance, and Qori's own defence                          | The creator, in their studio |
| Scope                | Cross-tenant, global model                                  | Workspace-owned              |
| Reads logged?        | **Yes** (§24.6 — opening someone's business leaves a trace) | No, writes only              |
| Retention            | Never pruned                                                | Pruned by plan               |
| Deleting a workspace | Trail survives                                              | Trail goes with it           |

Merging them would force a choice between pruning compliance records and keeping
creator activity forever. Neither is acceptable, so the interface is shared and
the storage is not.

### The one decision that makes it affordable

**Never log what another collection already records.**

Modelled at 1,000 workspaces, 400 bytes a row:

|                             | Events/workspace/month | 12-month steady state |
| --------------------------- | ---------------------- | --------------------- |
| A row per EDM **recipient** | 5,190                  | **23.2 GB**           |
| A row per EDM **campaign**  | 196                    | **0.9 GB**            |

A Neon starter plan ships 10 GB. The naive version exhausts it inside six months; the
lean one uses 9% of it — and the entire difference is one line of design.
`campaign_recipients` **is already the per-recipient log**: a row each, with
status, failure reason and sent_at. Writing "emailed Sam" into activity as well
stores the same fact twice.

So activity records _"Rita sent 'Spring launch' to 340 people"_ — one row,
linking to the campaign. The per-person detail is one click away and was already
paid for.

Generalised: activity is for **transitions that leave no other trace**, plus a
narrative pointer to the ones that do.

### Four more things that keep it small

1. **Log verbs, not diffs.** Xero shows "Invoice edited by Sam", not a field-by-
   field dump. Store the changed field _names_, and values only where the
   narrative needs them — a price, a status. Full before/after on every write is
   where activity logs actually balloon, and almost nobody reads it.
2. **Denormalise the actor's name at write time.** ~30 bytes, and it buys two
   things: no join on read, and history that survives the person leaving. A trail
   that says "deleted user changed the price" is worse than useless.
3. **Never log reads.** §24.6 requires it of staff because looking inside
   someone's business is itself the event. On the creator's own data it would
   multiply volume for no product value.
4. **Cap the context blob** to a few named fields, not an arbitrary payload.

### ~~Retention with no scheduler: a Mongo TTL index~~ — superseded 2026-09-08

> Kept because the requirement it solved is still real and now needs an answer.
> Postgres has no TTL index, so retention needs a scheduled command — which is
> the same shape `T-010`'s `qori:series:purge` takes, and the same reason `T-018`
> has to settle a scheduler before either can run unattended. The original
> design follows.

Stamp `expires_at` on each row at write time from the workspace's plan, and index
it with `expireAfterSeconds: 0`. **MongoDB then deletes the rows itself** — no
job, no worker, no cron. That matters precisely because the queue and scheduler
are deferred: retention is the one part of this that cannot wait for them, and
this is the one mechanism that does not need them.

It also makes history length a plan feature — free 90 days, paid 12 months,
matching §14's spirit — which is another Pro lever that costs nothing to hold.

### Audience: the creator, not the student (settled 2026-09-06)

`activity_log` is a studio feature. A student sees their own courses and their
own progress; they do not get a feed of what the creator did to their record.

### Still open

- Which verbs exist. Keep the list small and closed like `ErrorCode`, because
  the values end up in UI copy and in translations (§13).

## Sentry — closed for now (2026-09-06)

**Built and committed: application errors only.** The human will explore Sentry
further independently and may reopen this; treat the section below as the state
it was left in, not as an open question.

## What belongs in Sentry, and what does not

The goal stated is not exception tracking: it is **knowing what the system is
doing** — "someone enrolled", "someone paid for a course" — while sitting at a
desk. That changes the recommendation, because most of that is not Sentry's job.

### "xx enrolled, xx paid" is the activity log, read differently

Those events are already being written. The creator sees their own workspace's
slice in the studio; an operator wanting _"what is happening across Qori"_ wants
the **same rows read cross-tenant**, which is exactly what §24 already builds
for: `App\Admin\Queries\*` is the sanctioned cross-tenant read layer, and
`acrossAllWorkspaces()` is permitted there and almost nowhere else.

So the operator view is a **console page (§24.5), not a third-party feed**. Three
reasons it beats piping business events to Sentry:

1. **PII.** "wayne@example.com enrolled in Piano" is personal data leaving the
   building. §14 is careful about exactly this, and doing it deliberately is
   worse than the accidental leak `send_default_pii` would cause.
2. **Cost.** Sentry bills logs by volume. Errors are rare; business events are
   continuous and grow with the business — the same "buying observability by the
   unit" trap that put broadcast mail on SES rather than Postmark.
3. **It is already stored.** Sending it somewhere else too stores the same fact
   twice, which is the exact rule that cut 23 GB down to 0.9 GB above.

If a Sentry feed is still wanted for convenience, send **ids and counts, never
addresses or names** — enough to correlate with an error, nothing that is a
person.

### What Sentry is genuinely for here

- **Errors**, and only real ones. Do not report every `AppException`: a
  `planLimitReached` or a `notFound` is the error layer working correctly, and
  reporting them buries real failures in expected ones. `ErrorCode::status()`
  already gives the discriminator — report 5xx, ignore the rest. An upstream
  timeout is worth waking for; a student hitting a plan cap is not.
- **Performance**, at a low `traces_sample_rate`.
- **Operational oddities that are nobody's business event**: a malformed webhook,
  a Stripe call that retried, a bounce spike, a slow query. These do not belong
  in `activity_log` — they are not a creator's business — and they are low
  volume and free of PII, which is precisely what Sentry is good at.

`sentry/sentry-laravel`, `SENTRY_LARAVEL_DSN` in the Cloud dashboard, unset
locally, and **`send_default_pii` off**.

## `devMessage` is an API contract, not a debug note (revised 2026-09-06)

Stated intent: `devMessage` is for an **external party integrating with the
API** — a machine-facing explanation of what was wrong with their request. That
is a different thing from a developer reading logs, and §23's current wording
("the technical detail, never shown in production") describes the second.

Two consequences, and the first is a live contradiction:

1. **Some existing `devMessage` values would leak if published.** The clearest:

    ```php
    devMessage: "User {$user->getKey()} is not a member of workspace {$workspace->getKey()}."
    ```

    It sits behind `errors.workspace.not_found`, whose public copy carries the
    comment _"Deliberately vague: a sharper message would confirm to a non-member
    that a given workspace exists."_ Publishing that `devMessage` **undoes the
    exact protection it sits behind**, and hands over two ids while doing it.

    The rule that follows: **a `devMessage` may never be more revealing than its
    public message about whether something exists.** It may be far more specific
    about _why a request was malformed_ — that is its whole value to an integrator
    — but it cannot answer a question the public message deliberately refuses.

2. **The field is currently doing two jobs and should be split.** Compare
   "Could not copy [a] to [b]" with "The workspace in X-Qori-Workspace is not one
   this token can act in". The first is an internal diagnostic that belongs in
   logs and Sentry; the second is genuinely useful to an integrator. Keeping both
   in one field means either publishing the diagnostics or withholding the
   contract. `upstream` already exists for third-party detail; the clean shape is
   a publishable integrator-facing message, with internal diagnostics going to
   the log context instead of onto the exception's public surface.

Neither is urgent — `devMessage` reaches no production response today — but both
have to be settled **before `routes/api.php` exists**, because publishing it is
the moment the contradiction becomes real.
