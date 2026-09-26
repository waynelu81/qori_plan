# Qori — current plan

Updated: 26 September 2026

This file is the entry point: what Qori is for, where it stands, and what blocks
release. **It does not list tasks.** Work is organised into parallel streams,
and the tasks themselves are one file each. The code is in the `qori`
repository, beside this one as `../qori`.

| Where                              | What is in it                                   |
| ---------------------------------- | ----------------------------------------------- |
| `bin/tasks`                        | Renders the board locally; it is not committed  |
| [`dev/streams/`](dev/streams/)     | Why each line of work exists, and in what order |
| [`dev/tasks/`](dev/tasks/)         | One file per task, specified to the column name |
| [`dev/PROCESS.md`](dev/PROCESS.md) | How to claim, execute and finish one            |

```bash
bin/tasks                       # render the board locally (--check applies rules)
cd ../qori && composer ci:check # the code gate: lint, types, PHPStan, tests
```

## Product north star

Qori helps people **shape what they know into a Series and share it with the
Peers they choose**. It is an invitation-led knowledge-sharing product, not a
school, marketplace, social feed or collection of integrations.

> Create Series → add Episode → make ready → share or invite → get access →
> continue → finish.

Leading brand line: **Your knowledge today. Their breakthrough tomorrow.** Keep
progress language for reporting and measurable states — Qori can observe
progress and cannot promise a breakthrough.

The immediate goal: that one loop, safe, reachable, understandable and measurable, before more surface.

## Where it stands

- Laravel 13 + Inertia/Vue on Laravel Cloud, **Neon Postgres**, Valkey for
  production session and cache, R2 for files.
- Authentication, multi-Group tenancy, Series and their Episodes, access,
  consent, progress, certificates, billing, Stripe Connect, direct-to-R2
  uploads, playback, campaigns, staff authentication and the admin shell are
  built. Stripe test mode and R2 have been exercised against their real APIs,
  and the core loop has been walked in a browser on the current schema.
- Mail from `useqori.com` **arrives** (`T-032`); SPF/DKIM/DMARC unrecorded.
- **The loop closes for a new person** (22 September 2026): an invitation reaches
  an address with no account, at its own price (`T-043`, `T-181`, `D-050`).
- **Built, with no way in**: connections and campaigns (`T-044`, `T-045`).
- **A live Episode's recording is pasted by hand** and Peers watch it from the
  card (`T-125`–`T-127`); both emails are built (`T-128`, `T-129`), unscheduled until `T-206` (`D-028`).
- **Not production-ready for real customers.** The beta gate below says why.

Completed work: [`status-history.md`](dev/status-history.md). Browser evidence: [`walkthroughs.md`](dev/walkthroughs.md).

## Execution rules

1. Finish vertical slices. A tested service with no reachable UI is not a
   finished feature. Three still are.
2. Money creates an obligation. After payment, fulfilment cannot be refused by
   a plan limit.
3. Blocking and permission states outrank encouraging next-action copy.
4. Real vendor smoke tests validate payload shape; mocks validate Qori's
   handling, not the vendor's contract.
5. No native app, catalogue or custom template system before the web core
   loop reaches beta; the seven storage and live-session providers ship in
   beta (`D-018`), each earning its place through a walked Peer journey.
6. A `ready` task's spec is frozen. If the code disagrees with it, the task goes
   back to planning rather than being improvised — see
   [`PROCESS.md`](dev/PROCESS.md).

## Streams

Twelve, ordered by what blocks release; each is one person's line of work.

| Stream                                                | Goal                                           | Blocks beta |
| ----------------------------------------------------- | ---------------------------------------------- | ----------- |
| [design](dev/streams/design.md)             | Finish the redesign; no unstyled surfaces      | Yes         |
| [identity](dev/streams/identity.md)         | Sign-in and verification that tell the truth   | Yes         |
| [onboarding](dev/streams/onboarding.md)     | A new person lands where their purpose points  | Yes         |
| [recovery](dev/streams/recovery.md)         | Every dead end gets an exit                    | Yes         |
| [reachability](dev/streams/reachability.md) | Nothing built is invisible                     | Yes         |
| [delivery](dev/streams/delivery.md)         | Transactional email that arrives               | Yes         |
| [selling](dev/streams/selling.md)           | A creator can share and sell what they made    | Yes         |
| [storage](dev/streams/storage.md)           | A creator's own files and sessions reach Peers | Yes         |
| [classroom](dev/streams/classroom.md)       | A course taught live works, week by week       | Yes         |
| [operations](dev/streams/operations.md)     | Know it broke; be able to put it back          | Yes         |
| [language](dev/streams/language.md)         | Custom vocabulary behind the entitlement       | No          |
| [workflow](dev/streams/workflow.md)         | Several developers can work at once            | No          |

## Beta release gate

- [ ] The creator and Peer core loop passes in a clean browser session at
      mobile and desktop widths
- [ ] Real Stripe test-mode, storage and email smoke tests pass on current
      payloads
- [ ] Production mail, queue, webhook endpoints and alerts are configured
- [ ] No built-in action knowingly leads to a predictable 403, plan refusal or
      dead page
- [ ] Backup and restore have been exercised
- [ ] Privacy policy, terms, refund responsibility and support ownership match
      the direct-charge model — a checklist, never a prerequisite (`D-043`)
- [ ] Five representative creators can create and share a Series without
      developer help; invited Peers understand how to get access and continue
- [ ] `composer ci:check` green from a clean checkout

## Measures for the core loop

Instrument these before broad beta; avoid vanity metrics, and never read planned
tier features as evidence that customers want them.

- Time from verified signup to first saved Series
- New Group owners who add an Episode and make a Series ready within 24 hours
- Invitation-to-access conversion, and invited Peers who start an Episode
- Series completion rate and median time to completion
- Payment-to-access fulfilment success rate and reconciliation age
- Transactional email delivery, bounce and complaint rates

## Settled, and not up for renegotiation without a decision record

- [x] Invitation/link-driven Groups and Series; **no shared catalogue in v1**
- [x] Responsive web first; native apps and public API product work deferred
- [x] Video and audio stay external/BYO; Qori storage is for supported
      documents and assets under the §8 rules
- [x] **Group, Series, Episode and Peer** are the customer-facing vocabulary,
      and the internal names too as of 9 September 2026
- [x] Certificates state what Qori can prove and never imply accredited CPD
- [x] Custom transactional templates, custom sending domains and new social
      features are deferred; Zoom and Teams ship in beta (`D-018`, `D-031`)
- [x] **One Group per person**, owned; the switcher exists for admins of other
      people's Groups and nothing else (13 September 2026)

Changing one of these belongs in [`decisions.md`](dev/decisions.md), not a task.

## Waiting on the owner

- ~~Domain, Postmark, DNS, the Laravel Cloud scheduler~~ — done 11 September 2026
- Live Stripe account: prices set in USD and published by Qori, Adaptive Pricing on (`D-048`); its webhook endpoint; Connect OAuth in the sandbox (`T-063`)
- Where an alert should go when Qori notices something broken — see `T-019`
- A month of Zoom Workplace Pro and the development app (`T-122`); `T-089`'s
  three open questions; the notify interval against the sleep timeout (`D-028`)
- Vimeo plan choice: Unlisted needs a paid plan, domain locking does not (`D-016`)
- Production queue/worker selection

Detail: [`release-prerequisites.md`](dev/release-prerequisites.md).

## Maintenance rule

Keep this file under 150 lines: intent, state and gates, never task detail or
transcripts. Anything needing a paragraph belongs in a stream, a task or `decisions.md`.
