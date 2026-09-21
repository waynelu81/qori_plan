---
id: T-150
title: 'Spike: can Qori upload a file into the connected Drive'
stream: storage
status: draft
owner: unassigned
estimate: S
depends: none
blocks: T-149
---

# T-150 — Spike: can Qori upload a file into the connected Drive

> Written on 20 September 2026 from the two questions `T-149` cannot be
> specified without, both raised by the owner the same day. It is a draft
> until the stream owner answers "Before this can be ready" and sets it
> `ready`.

## Why

`T-149` puts one dialog above every storage provider, and the owner asked
for Upload inside it: the creator picks a local file, Qori facilitates the
transfer, and the file lands in the creator's own storage rather than Qori's
(20 September 2026). Two facts decide whether that is buildable and in what
shape, and **both are documented and neither has been observed**:

1. **Can the browser send the bytes straight to Google?** The resumable
   upload's initiating call returns a session URI in `Location` that carries
   its own authorisation for a week, so in principle a page can `PUT` the
   file to it with no token in the browser — the same shape as
   `resources/js/lib/uploads.ts`' direct-to-bucket upload. Google documents
   that cross-origin `PUT` for Cloud Storage and says nothing either way for
   Drive (upload guide, read 20 September 2026). If Drive refuses it, Qori
   has to proxy, and the owner has already decided what that means: no media
   file uploads through Qori at all, because proxying two gigabytes through
   the app server spends bandwidth and request time on exactly the kind of
   file `§8` decided never to hold.
2. **Does a creator ever have to pick a folder?** `drive.file` authorises an
   app to the files it creates, so a folder Qori creates should be a folder
   Qori can upload into, and a file Qori uploads should be grantable with no
   Picker anywhere. If that holds, Upload needs no chooser at all and
   `D-036`'s per-file grants keep the folder unshared, so the
   `appNotAuthorizedToChild` refusal that sank the folder design cannot come
   back. If it does not hold, Upload needs a destination the creator picks,
   which the owner has ruled out for now — and then Upload waits.

`T-093` answered ten questions about grants and touched none of this: every
call it made was `files.get`, `files.list`, `permissions.*` or `changes.list`
(`reports/T-093-2026-09-20-wayne.md`). Nothing in the fixture set shows a
single byte being written.

## Decisions taken to make this specifiable

**This spike writes nothing under `app/`, and reuses `T-093`'s harness in
place.** `spikes/T-093-google-drive/` is in the repository and gitignored
whole; its `gcall` times a call and keeps the body, `redact.py` redacts by
role, and `picker/` is already an origin Google's console admits
(`http://localhost:8000`). A second harness would be a second thing to
verify. The new fixtures still land in `tests/Fixtures/google/`, because that
is where `T-149`'s tests will look for them.

**The creator consents again rather than reusing a token.** `T-093` step 15
revoked both the access and the refresh token deliberately, and a spike that
starts by working around its own findings is not measuring the product.
Consent is the Playground's, `drive.file` only, as `T-093` step 2.

**Probe A is run from a page, not from `curl`.** A cross-origin `PUT` is a
browser behaviour: the preflight, the allowed headers and, above all,
**whether JavaScript may read the `Range` header of a `308`** are the whole
question, and `curl` sees none of them. `curl` cannot fail this probe and
cannot pass it either.

**A negative from `http://localhost:8000` is re-run from an https origin
before it counts.** An origin that is plain HTTP and a loopback address is
unusual enough that a refusal there may say nothing about `useqori.com`.
Nothing about the second origin has to be registered with Google: the `PUT`
carries no API key and no token, only the session URI's own `upload_id`, so
the website restrictions that admit the Picker's key do not apply to it.
Any https page that can run a `fetch` will do.

**Each browser experiment starts its own session, and the file is larger
than one chunk.** The review of 20 September 2026 found that the draft reused
one session across the whole-file `PUT` and the chunked one, so the second
experiment would have reported the first experiment's completed upload
(`F12`). The same finding sends step 10 to re-run whichever step failed
rather than the first one, and puts Q6 in the media decision: an upload that
cannot resume is not an upload a creator should start with a video.

**Resume is probed, throughput is not.** Whether a component is needed at
all turns on resume, and resume is two calls on a small file: interrupt, ask
the session where it got to, finish. The 200 MB run that would have measured
throughput was dropped by the owner on 20 September 2026 — it costs an hour
and answers a question `T-149` can be specified without, and the uploader
will measure it for real anyway.

**The spike's own files are removed by hand, by the person who ran it.**
`D-038` binds Qori, not a tester, but nothing here deletes anything through
the API either — the report lists what was left in the Drive and the owner
clears it.

## Preconditions

**Data this task verifies against:** A clean database. This spike never
touches Qori's own database; every row it reads is Google's.

**Equipment:**

- The Cloud project of `T-093`, unchanged: the Drive and Picker APIs
  enabled, the consent screen declaring `drive.file`, the local-development
  client whose redirect URIs include the Playground, and the API key
  admitting `http://localhost:8000/*`. Its four values are already in
  `spikes/T-093-google-drive/secrets.env`.
- Two Google accounts: the creator, and one Peer to be granted on an
  uploaded file. `T-093`'s cast serves; both must still be Test users.
- The spike harness at `spikes/T-093-google-drive/`, served with
  `php -S localhost:8000 spikes/T-093-google-drive/picker/router.php`. Port
  8000 is the owner's wave server's; stop it first.
- An https origin serving one static page, for the re-run of step 7. The
  owner will provide it (20 September 2026); `cloudflared tunnel --url http://localhost:8000`
  puts the harness itself behind a `https://<name>.trycloudflare.com` with no
  account and no console change, and a page under `useqori.com` does as well.
- A local file to upload of about 1 MB, so that 256 KB is a first chunk and
  not the whole thing (`F12`). `spikes/T-093-google-drive/content/` holds one.
- The probe page, `spikes/T-093-google-drive/picker/upload.html`, served by
  the same router. It starts nothing and signs nobody in: paste a session URI
  into it and it runs one experiment per button, printing every response
  header it is allowed to read and saving each result beside the other
  fixtures.

## Scope

**In:**

- The numbered steps under Code, run in order, each answered in the report or
  marked as not run with the reason; the status and the seconds of every call.
- One fixture per observed response, redacted by `T-093`'s rule — addresses
  and display names become roles, tokens and the session URI's `upload_id`
  become `REDACTED`, ids stay — and indexed in a new section of
  `tests/Fixtures/google/README.md`.
- The report, `docs/planning/tasks/reports/T-150-YYYY-MM-DD-<owner>.md`,
  whose Outcome answers Q1 to Q7 in order and names the fixture for each.
- Carrying the answers into `T-149`: its two probe bullets struck with the
  date, the answer and the fixture, and its Upload scope written to whichever
  branch the answers select.

**Out:**

- Any code under `app/`, `resources/`, `routes/` or `lang/`, and the dialog
  itself (`T-149`).
- Dropbox and OneDrive uploads. Each has its own upload-session protocol and
  its own spike (`T-095`, `T-097`); nothing here generalises to them, and
  `T-149` must not assume it does.
- A Workspace tenant. Everything here is free-tier; whether an administrator
  can forbid an app writing files is `T-093`'s Workspace pass, not this.
- Choosing the uploader component. That follows the answers and is `T-149`'s
  (its "Before this can be ready" carries the recommendation).
- Deleting anything through the API, including the spike's own files
  (`D-038`).

## Files

| Path                                                                            | Change | Notes                                                                                    |
| ------------------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------- |
| `tests/Fixtures/google/README.md`                                               | edit   | A new section for this spike's steps, in the existing table shape, with its own run note |
| `tests/Fixtures/google/*.json`                                                  | new    | One per observed response, named under Code                                              |
| `tests/Fixtures/google/upload-resumable-session.txt`                            | new    | Status line and headers of the initiating call, the session URI's `upload_id` redacted   |
| `tests/Fixtures/google/upload-resumable-put-308.txt`                            | new    | Status line and headers of a chunk `PUT`, including every CORS header that came back     |
| `tests/Fixtures/google/upload-cors-preflight.txt`                               | new    | The `OPTIONS` response, or the browser error where there was none                        |
| `docs/planning/tasks/reports/T-150-YYYY-MM-DD-<owner>.md`                       | new    | The report; Q1 to Q7 in order                                                            |
| `docs/planning/tasks/T-149-one-dialog-adds-files-from-any-connected-storage.md` | edit   | The probe bullets struck with the date, the answer and the fixture                       |

Flows: none — nothing under `app/` or `routes/` changes, so no call chain exists to describe yet.

## Database

None.

## Code

None under `app/`. A spike's code is the calls it makes. They are written
out as commands, in order, in `spikes/T-093-google-drive/steps/T-150.md`,
which is the sheet the person running this follows; the steps below are the
specification it implements. Every `curl` runs through
`spikes/T-093-google-drive/gcall`, which times it and keeps the body;
steps 6 to 9 run in the browser, from a page served at
`http://localhost:8000`, and their evidence is the response headers and the
console.

**Setup**

1. **Consent again.** The Playground, `drive.file` only, creator account, as
   `T-093` step 2. Keep the access token in `state/access-token`. No fixture:
   `oauth-token.json` already shows the shape.

**Probe B — a folder Qori made, a file Qori uploaded, a Peer let in**

2. **Create a folder.**
   `POST /drive/v3/files`, body
   `{"name":"Qori spike 150","mimeType":"application/vnd.google-apps.folder"}`,
   `fields=id,name,mimeType,owners,webViewLink`
   (https://developers.google.com/workspace/drive/api/guides/folder).
   → `files-create-folder.json`. **Q1: may an app with `drive.file` create a
   folder, and who owns it?**
3. **Read it back** with the same token, `files.get`,
   `fields=id,name,mimeType,parents,capabilities`. →
   `files-get-created-folder.json`. Confirms an app-created folder needs no
   pick.
4. **Upload the small PDF into it**, multipart:
   `POST /upload/drive/v3/files?uploadType=multipart`, metadata
   `{"name":"uploaded.pdf","parents":["<folderId>"]}`,
   `fields=id,name,parents,owners,ownedByMe,quotaBytesUsed,md5Checksum,version,webViewLink`.
   → `files-create-multipart.json`. **Q2: does `parents` pointing at an
   app-created folder work, and does the file count against the creator's
   quota, not Qori's?** A refusal is `errors-files-create-<status>-<reason>.json`
   and ends the branch.
5. **Grant a Peer on the uploaded file**, with nothing ever picked:
   `POST /drive/v3/files/{fileId}/permissions?sendNotificationEmail=false`,
   body `{"role":"reader","type":"user","emailAddress":"<peer>"}`, exactly
   `T-093` step 6's call. → `permissions-create-uploaded-file.json`. The Peer
   opens `webViewLink` in their own browser and the report says what they
   saw. **Q3: is a file Qori uploaded grantable and openable with no Picker
   anywhere in the story?**

**Probe A — can the browser send the bytes**

**Every experiment below starts its own session** (`F12`, the review of
20 September 2026). A session that has received its last byte is finished: a
later `PUT` to it reports the upload that already completed and says nothing
about chunking or resume, so one session reused across steps 7 to 9 would
return three answers to the first question. The file is about 1 MB, which is
four chunks of 256 KB — a file smaller than one chunk cannot produce a first
chunk at all.

6. **Start session A** from `curl`:
   `POST /upload/drive/v3/files?uploadType=resumable`,
   `Content-Type: application/json`, body
   `{"name":"upload-a.pdf","parents":["<folderId>"]}`. Keep the `Location`
   header. → `upload-resumable-session.txt`, `upload_id` redacted.
7. **`PUT` the whole file to session A from the page** at
   `http://localhost:8000`, no `Content-Range`. Record the `OPTIONS` if the
   browser sent one, every `Access-Control-*` header that came back, and
   whether the response body was readable from JavaScript. →
   `upload-cors-preflight.txt`, `upload-resumable-put-200.json`.
   **Q4: does a cross-origin `PUT` to a session URI succeed at all?**
8. **Start session B**, the same call under a different name, and from the
   page **`PUT` its first chunk alone**: `Content-Range: bytes 0-262143/<total>`,
   expecting `308`. → `upload-resumable-put-308.txt`.
   **Q5: is `Range` readable from JavaScript, or is it missing from
   `Access-Control-Expose-Headers`?** A `308` whose `Range` cannot be read is
   a pass that is still a failure — the client cannot learn where to resume —
   and the report says so in those words.
9. **Interrupt session B and resume it.** Send its second chunk, stop, then
   query the offset with `PUT <session URI>`, `Content-Range: bytes */<total>`
   and an empty body, and send the remaining chunks from the offset it names.
   → `upload-resumable-resume-308.txt`, `upload-resumable-complete.json`.
   **Q6: can the browser resume an interrupted upload?** The owner dropped the
   200 MB throughput run on 20 September 2026, so this measures that resume
   works, not what a real video costs; the uploader measures that when it is
   built.
10. **Whichever of steps 7 to 9 failed, run that same step again from the
    https origin** — not step 7 in its place — with a fresh session and
    unchanged in every other respect. The report states both origins and both
    outcomes, and only a failure at both is an answer.

**What it means afterwards**

11. **Replace the bytes of the uploaded PDF from the app:**
    `PATCH /upload/drive/v3/files/{fileId}?uploadType=media`, then
    `files.get` with `fields=id,version,md5Checksum,modifiedTime` and
    `permissions.list`. → `files-update-media.json`,
    `files-get-after-app-new-version.json`,
    `permissions-list-after-app-new-version.json`. **Q7: does an app-side new
    version keep the id and leave the Peer's permission standing**, as the
    creator-side one did in `T-093` step 13 row 2?
12. **List the folder Qori made**: `GET /drive/v3/files?q='<folderId>' in parents`.
    Then add a file to that folder by hand in Drive's own interface and list
    again. → `files-list-created-folder.json`,
    `files-list-created-folder-after-hand-add.json`. Says whether Qori can
    ever reconcile the folder it manages, or sees only its own uploads —
    which is what "manage that folder as a whole" can mean in practice.
13. **Abandon a session**: start one as step 6 and send nothing. After an
    hour, list the folder again. Says whether a failed upload leaves anything
    in the creator's Drive, which `D-038` promises Qori will not tidy.

**Decides**

| Answer                    | What `T-149` does                                                                                                      |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Q4, Q5 and Q6 all pass    | Upload is direct to the vendor, offered for every file type, and `@uppy/core` is weighed against the existing uploader |
| Q4 passes, Q5 or Q6 fails | Direct upload that cannot resume: documents only, capped at what one `PUT` carries, and no media (`F12`)               |
| Q4 fails at both origins  | No media upload through Qori at all (the owner, 20 September 2026); documents proxy, or Upload waits                   |
| Q1 to Q3 pass             | No chooser in Upload: Qori makes the folder, and an uploaded file is granted like any other                            |
| Q2 or Q3 fails            | Upload needs a destination the creator picks, which is ruled out for now, so Upload is out of `T-149`                  |

## Copy

None.

## Routes

None.

## Tests

None. A spike commits no test: its output is the fixtures, which `T-149`'s
tests load into `Http::fake()`.

## Acceptance

- [ ] Every numbered step run, or marked in the report as not run with the
      reason
- [ ] One fixture per response, verbatim in content, redacted by role with
      the session URI's `upload_id` removed, indexed in a new section of
      `tests/Fixtures/google/README.md` with date, call, request, status,
      seconds and account role
- [ ] The report's Outcome answers Q1 to Q7 in order and names the fixture
      that shows each answer; Q4 and Q5 each state the origin they were
      answered from, and a failure states both origins
- [ ] The report names every file and folder left in the creator's Drive, for
      the owner to clear by hand
- [ ] Every "Found, not fixed" bullet in the report ends in a disposition
- [ ] `T-149` carries the answers: both probe bullets struck with the date,
      the answer and the fixture, and its Upload scope written to the branch
      the Decides table selects
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- Who runs it, and when. It needs a person at a browser with two Google
  accounts and about an hour — the stream owner's. Everything else is
  settled: the owner provides the https origin for step 7's re-run, and the
  200 MB throughput run is dropped (both 20 September 2026).

## Re-scope log

None.

## Notes

The two questions are `T-149`'s, but the answers reach further: `T-095` and
`T-097` will ask the same two of Dropbox and OneDrive, whose upload sessions
are the same idea with different words, and the shape of this report is meant
to be copied there.
