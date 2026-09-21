---
stream: identity
owner: wayne
---

# Stream: identity

**Goal.** Sign-in and email verification that tell the truth about what has been
proven, and never strand somebody mid-task.

**Done when.** A consumed magic link counts as verification of the address it
was sent to; a verification detour explains itself and returns to the page that
triggered it; and no authentication path ends somewhere the reader cannot act.

**State, 13 September 2026.** `T-007` and `T-008` made a consumed magic link
verify its address, and the verification wall name the address it wrote to and
return people to the Series they came from. The owner's own walkthrough that
day found the two ends of a session wrong: every sign-in landed on the
receiving home whoever you were, and a passkey sign-in with nothing intended
landed on the marketing page; signing out landed on the marketing page too.
Both were small and both are specified. Still open from `T-008`: nothing reads
`?verified=1`, so a successful verification is silent on the page it lands on.
The same day's review reordered sign-in: the address first, then Password or
Email link, with passkey left below as its own function (`T-077`). Three
browser walks since have met the same thing — a stale intended URL from an
earlier person in the same browser winning over the sign-in landing — which
is `T-084`.

## Tasks, in order

1. `T-007` — A consumed magic link verifies the address it was sent to
2. `T-008` — Explain the verification detour and return to where it started
3. `T-036` — One sign-in composition: one email field, Password or Email link,
   the neutral "if that email has an account" sentence
4. `T-052` — Signing in lands on the side you last used
5. `T-053` — Signing out lands on the sign-in page, and says so
6. `T-059` — The sign-up choice is used once, and not stored
7. `T-065` — A person owns one Group, and the service refuses a second
8. `T-077` — Sign-in asks for the email first, then the method
9. `T-084` — A stale intended URL survives another person's sign-in: the
   session keeps `url.intended` across regeneration, so the next person in
   the same browser lands on a page that was never theirs
10. `T-087` — Sign-in asks for the email on a step of its own, then offers
    Password or Email link: the owner still found everything arriving at once
    too much after `T-077`
11. `T-116` — Password managers can find where to create a passkey: the
    domain rename turned the well-known document's `enroll` into `grantl`

`T-052` before `T-053` only because it is the one the owner hits first. They
share one provider file and nothing else; run them in sequence, either order.

## Notes

The email-change flow (`App\Services\EmailChangeService`) already does the
honest thing — a pending address is confirmed before it becomes the sign-in
address. `T-007` is the same principle applied to sign-in.
