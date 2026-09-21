---
id: T-149
title: One dialog adds files from any connected storage
stream: storage
status: draft
owner: unassigned
estimate: S
depends: T-150
blocks: none
---

# T-149 — One dialog adds files from any connected storage

> Start one with `php artisan qori:tasks --new <stream> <slug>`, which copies
> this file under the next free id. Keep every heading, and delete the
> guidance in quotes. A section that does not apply says **None**, so a reader
> can tell "nothing to do here" from "nobody thought about it".
>
> `blocks:` is derived from every other task's `depends:` and a test asserts
> the field agrees with the derivation; write it for the reader, and fix it
> when the board says so.
>
> Read [`../PROCESS.md`](../PROCESS.md) first if you have not.

## Why

Each storage provider brings its own way of choosing a file: `T-094` opens
Google's Picker, and `T-096` and `T-098` will open Dropbox's and OneDrive's.
Without anything above them, a creator adding an Episode meets a different
entry point for each provider. The owner asked on 19 September 2026, during
`T-093`, for one Qori dialog that switches between them
(`reports/T-093-2026-09-20-wayne.md`). Qori cannot draw Google Drive's file
list itself under `drive.file`. Listing files nobody picked needs the
Restricted `drive.readonly` or `drive` scope and Google's security
assessment every 12 months (`docs/planning/vendor-accounts.md`, Google
Drive). So the dialog is Qori's, and its Google Drive entry opens Google's
Picker inside it, as Uppy's Google Drive Picker plugin does for the same
reason (https://uppy.io/docs/google-drive-picker/, read 19 September 2026).
Afterwards a creator chooses Upload, Google Drive, Dropbox or OneDrive in one
place, and every choice reaches the Episode in the same shape.

**Upload means into the creator's own storage, not Qori's.** The owner settled
the shape on 20 September 2026: a picking-and-progress component in front, as
the direct-to-R2 upload already has, and the destination is whichever provider
the creator chose — Qori facilitates the transfer and does not become the home
of the file. Which component, or whether a new one is needed at all, is
decided by the probes below and answered under "Before this can be ready". `drive.file` is a write scope, so this is reachable:
`POST /upload/drive/v3/files?uploadType=resumable` creates a file with the
creator's token, `PATCH` on the same path replaces its bytes keeping the id,
and **a file the app creates is authorised to the app from birth, so an
uploaded file never has to be picked** (Google's upload guide and scope
documentation, read 20 September 2026; no call of `T-093`'s made either, so
both are documented and unobserved). A folder is a file with the folder
mimeType, so Qori can create one named for the Series, upload into it and
manage it as a whole, and the creator picks nothing — and because `D-036`
grants per file and never shares a folder, that folder cannot bring back the
`appNotAuthorizedToChild` refusal that sank the folder design. **A creator is
never asked to choose a folder**, the owner on 20 September 2026: a chooser
offers files, Qori makes its own destination, and if that is ever to change
it changes as its own decision rather than as an option added to a dialog.

**Where the bytes travel decides whether this is cheap.** The initiating POST
returns a session URI in `Location` that is good for a week and carries its
own authorisation, so the browser can PUT the file straight to Google with no
token in the page — the same shape as the presigned direct-to-R2 upload, and
it keeps the creator's video off Qori's bandwidth entirely. Google documents
that cross-origin PUT for Cloud Storage and says nothing either way for
Drive. If Drive refuses it, Qori has to proxy the bytes, and a 2 GB video
through the app server is a good reason to offer upload for documents only
and leave video as "choose a file you already have". **This is the question
that decides the task**, and it is one call to answer.

**The owner settled what happens if the answer is no**, 20 September 2026: if
the bytes cannot go straight to the vendor, no media file is uploaded through
Qori at all. Video and audio are external by `§8` and `D-016`, and proxying a
two-gigabyte file through the app server would spend Qori's bandwidth and
request time on precisely the kind of file the product has decided never to
hold. So Upload accepts whatever the provider accepts when the browser can
reach it directly, and documents only when it cannot, with media left to
"choose a file you already have" — which is `T-094`'s path and needs nothing
new.

**Every action says whose storage it touches** (`D-037`, the owner's rule the
same day). Uploading writes a file to their Drive; adding an Episode writes
nothing there; removing one takes readers off a file and leaves the file
alone. The dialog is where a creator first meets the distinction, so it is
where the words belong, and `D-038` fixes the other half: nothing here
deletes, bins or moves a creator's file, so an abandoned upload leaves its
file where it was put and says so.

## Decisions taken to make this specifiable

> Every choice the spec makes that somebody could reasonably have made the
> other way, each as one bold sentence and its reason. This is where a draft
> becomes a spec: a task with a decision still open in it is not ready, and a
> decision hidden inside the Code section is one the developer will re-make.
> **None** only when the task genuinely had no choices in it.

## Preconditions

> Anything that must be true of the machine before this task can be done or
> verified — a running container, a generated directory, credentials, seeded
> data. **None** if it runs from a clean checkout.
>
> Worth its own section because a check that silently reads an empty directory
> reports success. `resources/js/routes` is generated and gitignored, so
> anything analysing it needs `php artisan wayfinder:generate --with-form`
> first, and finds nothing at all without it.

**Data this task verifies against:** > The rows the check needs — a seeded
world, a Group in a particular state, a realistic row count — and how to get
them (`php artisan qori:reset …`, a factory, a fixture). **A clean database**
when nothing more is needed.

**Equipment:** > A visible browser, vendor credentials, a mailbox, a phone —
whatever a check needs that a shell does not have. **None** when everything
can be verified from the terminal.

> **Spike, for vendor-facing work.** A spec that names a vendor payload cites
> where the shape came from: an observed response (the date and the call), or
> a committed fixture under `tests/Fixtures/<vendor>/`. Guessing the field
> names from documentation is how `contact_email` became `peer_email` and
> how a v2 requirements summary read "nothing outstanding" for an account
> that had not started. If nobody has seen the response, the first step is a
> spike that does, and its result is a fixture, not a memory.

## Scope

**In:**

- …

**Out:**

- …

> Name the things a reader would reasonably assume are included and are not.
> "Out" is the section that prevents a task from growing while it is being done.

## Files

| Path             | Change | Notes |
| ---------------- | ------ | ----- |
| `app/…`          | new    | …     |
| `resources/js/…` | edit   | …     |

> Every file, exactly, one row per file or several backticked paths in one
> cell — the parser reads all of them, expands a glob against the repository,
> and refuses a bare basename (`SeriesService.php` claims nothing the collision
> check can compare). Two `doing` tasks listing the same path is a collision
> the board will show — see PROCESS.md.
>
> **Wiring.** A file that is new is not reached by anything until something
> is edited to reach it. Go down this list and add the rows:
>
> - a route, in `routes/*.php`, for a new controller action
> - a nav or a link, for a new page; `qori:reachability` finds the ones you forget
> - a lang file, for every sentence a person reads
> - a flow doc, for a changed call chain: a `docs/flows/*.md` row here, or the
>   line below when nothing in `docs/flows/` describes the chain this touches
> - a tinker recipe, when a `docs/tinker/*.md` recipe drives what changed
> - `config/qori.php`, for a number that would otherwise be written twice
> - a factory or the design-review seeder, for a new column
>
> A task whose Files include anything under `app/Http`, `app/Services`,
> `app/Listeners` or `routes/` must either list a `docs/flows/*.md` path or
> carry the line below, and a test checks it.

Flows: none — > why no flow file changes, in a few words; delete this line
when a flow row is in the table.

## Database

> Table, column, type, nullability, default, index or constraint, and the
> migration's file name. **None** if the task touches no schema.

| Table | Column | Type | Null | Default | Index / constraint |
| ----- | ------ | ---- | ---- | ------- | ------------------ |

Migration: `database/migrations/YYYY_MM_DD_HHMMSS_<name>.php`

## Code

> Literal names. Namespaces, class names, method signatures with types,
> property and constant names. Enough that two developers would write the same
> declarations.

```php
namespace App\…;

class Thing
{
    public const SOME_KEY = 'value';

    public function doIt(Group $group, string $name): Result;
}
```

## Copy

> Every user-facing string, as a lang key and its file. Never inline (§23).
> **None** if the task adds no copy.

| Key | File | English |
| --- | ---- | ------- |

## Routes

> Verb, path, route name, controller action. **None** if no routes change.

| Verb | Path | Name | Action |
| ---- | ---- | ---- | ------ |

## Tests

> One line per case with its method name, and the total. A reviewer counts them
> against the file. Say which existing tests are expected to change and why.

**New: `tests/Feature/…Test.php` — N cases**

1. `test_it_…` — …

**Changed:**

- `tests/…` — …

## Acceptance

> The product lines first, then the closing lines in this order — status and
> the board check come before the gate, because the gate includes the board
> check and a task that is `done` with `status: doing` fails it.

- [ ] …
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Whether this waits for two providers' pickers to exist, `T-094` and one of
  `T-096` or `T-098`, or is written first and each provider task mounts into
  it — the owner's.
- Which providers each dialog offers: every provider the Group has
  connected, or also the unconnected ones with a Connect link — the owner's,
  with `T-044`.
- Whether a provider's own chooser opens inside the dialog or replaces it
  while it is open, since Google's Picker draws its own overlay and needs the
  person's Google session in a third-party frame (`T-093`'s report, Found,
  not fixed) — anyone's, once `T-094` is re-drafted.
- The shape every provider hands back to the Episode form, which `T-094`,
  `T-096` and `T-098` each write today in their own terms — anyone's.
- **`T-150` decides whether Upload is in this task at all.** Its two probes
  are (a) does a browser `PUT` to a resumable session URI from Qori's origin
  succeed, and can JavaScript read the `Range` header it needs to resume, and
  (b) does `files.create` with `parents` set to a folder the app created
  itself work under `drive.file`, with the uploaded file grantable and no
  pick anywhere. (a) settles direct-to-Drive against proxying, and with it
  whether media may be uploaded through Qori at all; (b) settles whether a
  creator ever picks a folder. `T-150`'s Decides table says what each answer
  makes of this task — written, waiting on the stream owner to set it
  `ready`.
- **Which uploader component, if any — the same probe decides it.** Qori's
  direct-to-bucket upload is 138 lines in `resources/js/lib/uploads.ts` and a
  124-line `FileUpload.vue`: a ticket from Qori, a PUT from the browser to a
  URL the server signed, a confirm. Drive's resumable upload is those same
  three steps with a `Location` header where the signed URL was, so documents
  need no new dependency at all. A library earns its place only for what
  documents do not need: chunk-level retry on a failing connection, pause and
  resume across a reload, a queue of large files each with its own progress —
  which is to say only if the probe passes and media uploads are on. If they
  are, the recommendation is `@uppy/core` as a headless engine behind Qori's
  own components, not `@uppy/dashboard`, whose interface would arrive with
  its own design language into a redesign that is a release gate. FilePond's
  chunking is its own protocol and would be bypassed for the vendor's, which
  removes the reason to take it; tus does not apply, because none of these
  vendors speak it. Either way the transfer itself is vendor code under
  `app/Integrations/<Vendor>` and the component only hands it bytes —
  anyone's, after the probes.

- ~~**The storage review of 20 September 2026 proposes deferring this task
  entirely.**~~ **Declined by the owner the same day**: every provider stays
  in the beta, `D-018` is reaffirmed, and this dialog with it. "I plan to do
  all, it is a lot of work. But I see this is the major selling point for
  Qori." The review's reasoning, for whoever reads this next: Its reading is that the first connected-storage beta should
  prove Google Drive end to end and defer the Dropbox and OneDrive
  connectors, Zoom registration, Teams' grant machinery, the Vimeo and
  YouTube expansion, and this dialog with its uploads. A dialog above one
  provider is not a dialog. If the owner takes that proposal, this task waits
  for the second provider and `T-150` becomes research rather than a
  precondition — the owner's, and it outranks every bullet above.

## Re-scope log

> Empty until something in the spec turns out to be wrong. Then: what was
> expected, what was found, and what it means for the spec. Set
> `status: rescope` and stop.

None.

## Notes

> Anything learned that the next reader would want and that does not belong in
> `decisions.md`.

None.
