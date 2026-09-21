# Streams

A stream is a line of work one person can pick up end to end without waiting
on another stream. Its tasks touch a mostly disjoint set of files, which is what
makes them safe to run in parallel — see [`../PROCESS.md`](../PROCESS.md).

**Nobody owns a stream and nobody approves its tasks** (`D-043`). Pick one up by
claiming its next task; while you are on it, keep its order and its reasons
true. Questions only the product owner can answer go to wayne, and the work
carries on around them. A stream file says what the stream is for, when it is
done, and its tasks in order with one line of reason each — never a status: the
board says what is done.

| Stream                          | Owns                                                                                          | Blocks release? |
| ------------------------------- | --------------------------------------------------------------------------------------------- | --------------- |
| [design](design.md)             | The remaining redesign days and error surfaces                                                | Beta            |
| [identity](identity.md)         | Sign-in, verification and email change                                                        | Beta            |
| [onboarding](onboarding.md)     | Where a new person lands, by why they arrived                                                 | Beta            |
| [recovery](recovery.md)         | Archiving, deletion and honest dead ends                                                      | Beta            |
| [reachability](reachability.md) | Built things nobody can click                                                                 | Beta            |
| [delivery](delivery.md)         | Transactional email in production                                                             | Beta            |
| [selling](selling.md)           | A price, a link, an invitation and a voucher                                                  | Beta            |
| [storage](storage.md)           | A creator's own files, videos and live sessions, opened by each Peer on the vendor's site     | Beta            |
| [classroom](classroom.md)       | A course taught live: the session card, its recording, materials, homework and the class chat | Beta            |
| [operations](operations.md)     | Queue, alerts, backup and restore                                                             | Beta            |
| [language](language.md)         | Custom vocabulary behind the entitlement                                                      | No              |
| [workflow](workflow.md)         | Several developers at once, without treading on each other                                    | No              |

**Where they touch.** `design`, `language` and `onboarding` all edit Vue pages,
so a task in one names the files it changes and a task in the other depends on
it rather than racing. `onboarding` also extends `ShareDigest`, which `design`
finished with — check the board before claiming either. `selling` and
`onboarding` meet at the Series page: `selling` owns what it offers, and
`onboarding` owns what happens to a stranger who takes the offer. Everything
else is separable: `identity` lives in `app/Http/Controllers/Auth`, `recovery`
in `SeriesService` and its screens, `reachability` adds a command and an admin
page, `delivery` and `operations` are configuration and infrastructure, and
`workflow` is the planning tooling, the build files and the docs that describe
the code. `classroom` meets `storage` on the Peer's Open route and the Zoom
connection, and waits on the `storage` task that owns each shared file
(`T-089`, `T-044`); its own tables, components and lang files are its own.
