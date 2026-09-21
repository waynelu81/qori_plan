# The stack

What Qori runs on, and which parts of the playbook survive changing it.

| Layer | Qori's choice | Transfers? |
| --- | --- | --- |
| Backend | Laravel | Paths and idioms do not; the module decisions do |
| Frontend | Inertia + Vue, server-driven routing | Mostly — the decisions are about flow, not framework |
| Database | Postgres (managed in production, pinned container locally) | Yes |
| Primary keys | ULIDs on every model | Yes, and strongly recommended |
| Session and cache | A Redis-compatible store in production; file/array locally | Yes |
| Object storage | S3-compatible, for documents and assets only | Yes |
| Queue | After-response locally and in production; synchronous in tests | **No** — see below |
| Hosting | A managed platform that builds and deploys | Neutral |

## The parts worth copying whatever the stack

- **ULID primary keys.** Ids appear in URLs. Sequential integers leak how many
  customers you have.
- **Money as integer minor units with an explicit currency beside it.** Never a
  float, never a bare number.
- **Polymorphic payloads in a real JSON column with an index**, not a blob and
  not a separate document store. Qori migrated off a document database to get
  this, and the rule inverted: the cast that was a trap became the right answer.
- **Uniqueness as a database constraint**, with a form check in front of it for
  a readable message. The constraint is the guarantee; the form check is the
  manners.
- **Defaults hold raw storage values.** A cast does not run over a column
  default, so a JSON default is the string `'[]'`, not an empty array. Qori's
  symptom was an error naming neither the model nor the column.
- **The test suite refuses any database whose name does not mark it as a test
  database**, and refuses a non-local host.

## The queue is a decision, not a default

Qori runs an after-response driver, which **cannot retry**: a job that fails is
lost. So nothing is marked queueable, and that is enforced rather than
remembered.

This is a legitimate early choice — it is one fewer service — but it must be a
choice. The rule that follows from it is absolute: **do not mark work for a
queue that cannot retry**, and do not build anything whose correctness depends
on a retry until a real worker exists. Scheduled notices, reconciliation sweeps
and delayed deletion all belong on the far side of that line.

When a worker does arrive, a database-backed queue on the existing Postgres is
one fewer service than a hosted queue.

## Local development

- Pin the local database's major version to production's.
- Give the local database a **dedicated port**. Qori's predecessor collided
  with another project's container on the default port, and local development
  silently talked to the wrong database for a while.
- One database per checkout, so two suites do not deadlock.
- A local mail inbox, and be aware it is another default port that collides.
