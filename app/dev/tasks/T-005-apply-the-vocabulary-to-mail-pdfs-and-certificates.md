---
id: T-005
title: Apply the vocabulary to mail, PDFs and certificates
stream: language
status: draft
owner: unassigned
estimate: M
depends: T-004
blocks: none
---

# T-005 — Apply the vocabulary to mail, PDFs and certificates

> **Draft.** Not specified yet, and not to be started — see
> [`../PROCESS.md`](../PROCESS.md). What has to be decided before it can be
> marked `ready` is listed at the bottom.

## Why

The vocabulary reaches every screen and stops at the edge of the browser. Access emails, the certificate and any generated PDF still say Qori's own nouns, so a Group that renamed Series to Trail gets Trails on screen and Series in the email that invited somebody to one.

## Scope

**In:**

- Every notification and mailable resolving nouns through `Terminology::line()`.
- The certificate and any PDF output.
- Deciding, and recording, whether certificates inherit custom nouns at all.

**Out:**

- Custom transactional templates or creator sending domains — both deferred until after beta.

## Before this can be ready

- ~~Do certificates use neutral wording or inherit the Group's nouns?~~
  **Decided 9 September 2026: they inherit.** A certificate is the Group's
  document, and a Group that calls them Trails should not have Qori's word for
  it appear on the one artefact a Peer shows to somebody else. The reservation
  — that a custom noun may be unreadable to a stranger — is real, and is
  answered by the certificate naming the Group beside the noun, not by
  overriding the Group's own vocabulary.
- Note this points at custom certificate templates, which §13 defers until
  after beta. Inheriting the nouns does not require them and must not become
  the first step towards them in this task.
- A queued notification has no request and therefore no `CurrentGroup`. Every call site must pass the Group explicitly — list them before this is ready.

## Re-scope log

None.

## Notes

None.
