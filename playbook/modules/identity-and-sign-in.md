# Module: identity and sign-in

**What it is.** Getting a person into the product and proving the address they
claim is theirs — sign-up, sign-in by password, email link or passkey, email
verification, and deciding where they land afterwards. It is the first thing
every product builds and the one most often shipped subtly wrong, because the
failures only appear on the second person to use the same browser.

**Done when.** A person can reach the product by every offered method; a
consumed email link counts as proof of that address; a verification detour
explains itself and returns to where it started; and no authentication path
lands somewhere the reader cannot act.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| Does a consumed email link verify the address? | Yes | A link sent to an address and clicked *is* proof of that address. Sending a second "verify your email" afterwards asks the person to prove something they just proved. |
| Address first, or address and method together? | Address on a step of its own, then the methods | Password and email-link both need the address; the choice belongs after it. Shown together, it reads as too much at once — the owner rejected the combined layout twice before this landed. |
| Does the first step check whether the account exists? | **No** | A step that answered "no account" is an unthrottled way to enumerate who has registered. The second step appears for any well-formed address. |
| Where does sign-in land? | The tenant they last opened, remembered on the user row; else their only one; else the switchboard home | Every sign-in landing on the same home is wrong for whichever role you are not. Remembering on the user row means it survives signing out. |
| Does an intended URL beat that? | Yes, always | A guest sent to sign in from a protected page must return there. |
| Where does sign-out land? | The sign-in page, with one sentence saying so | Not a holding page: its two options would be "sign in again", which that page already is, and "close the tab", which needs no button. |
| Is the sign-up purpose stored? | No — read once, at registration, never persisted | It is a runtime decision about which onboarding to show. What is durable is what the person *has*, not what they once said. A stored intent drifts from reality the moment they do something else. |
| Is passkey a method or a function? | A separate function, below the rule | It is complete on its own — no address needed — so putting it in the method chooser implies a symmetry that is not there. |

## Build order

1. **Registration and the identity record.** Email unique across the whole
   platform, whatever the tenancy model. Get this wrong and every later "is
   this the same person" question is unanswerable.
2. **Password sign-in and sign-out**, with sign-out landing on sign-in under
   its own flash key.
3. **The sign-in destination.** One resolver — Qori calls it
   `SignInDestination` — consulted by every method, never re-implemented per
   controller. Needs 2.
4. **Email verification**, with the detour naming the address it wrote to and
   returning to the page that triggered it. Needs 1.
5. **Email link sign-in**, consuming the link as verification of that address.
   Needs 4.
6. **The two-step form**: address alone with **Next**, then the method choice
   and the chosen method's controls. One form, one posted address, manual
   activation so arrow keys never change the operation, a confirmation that
   replaces the form, and a neutral "if that email has an account" sentence.
   Needs 2 and 5.
7. **Passkeys**, below the rule, with the well-known document reachable so
   password managers can offer to create one. Needs 2.
8. **Destination hygiene** — see the trap below. Needs 3.

## Rules that bite

- **A stored destination belongs to the sign-in that asked for it.** Not to the
  browser, and not to the session. Every sign-in regenerates the session and
  *keeps its data*, so a destination written for one person waits for whoever
  signs in next in that browser.
- **Never let reading a page store a destination.** Store it on the deliberate
  act — the "sign in instead" link — which can carry the page with it.
- **The neutral sentence has to be neutral everywhere.** "If that email has an
  account, we've sent a link" is worth nothing if a different path says "no
  such user".
- **Two guards means `$request->user()` is ambiguous.** If the product has a
  staff console on its own guard, anything wanting the customer identity goes
  through an explicit accessor, so a staff identity reaching customer data
  fails closed rather than silently succeeding.

## Native contract

**Not proven** — nothing native is built. What iOS and Android will need:

- Tokens carry **user identity only**, never a tenant. The tenant is chosen
  per request, or the token becomes a second, stale source of truth.
- App tokens and web sessions register in **one** table, so "sign me out
  everywhere" has one list to read and a device cap counts both.
- Revoking a web session needs both a direct session-store destroy *and* a
  per-request check of the registry row. The per-request check is the real
  guarantee; the destroy is the fast path.
- Email links must deep-link into the app when it is installed and fall back to
  the web page when it is not — which means the link cannot be single-use at
  the HTTP layer if the OS may prefetch it.
- Remember-me must not resurrect a revoked session.

## Traps

| Symptom | Cause |
| --- | --- |
| "I signed in and landed on a page that was never mine" | The session keeps `url.intended` across regeneration. Three separate browser walks hit this before it was understood. |
| "Signing in always lands on the wrong side" | One home route for every role, with no per-person memory. |
| "The password manager won't offer to create a passkey" | The well-known document's path broke — in Qori's case a domain rename silently rewrote a word inside it. Nothing warns you; it just stops being offered. |
| "Verification succeeded but the page says nothing" | The success flag is set but no page reads it. Verification that is silent reads as failure. |
| "The tab order jumps around the auth form" | Panels remounting on method switch. One form whose action follows the choice avoids it. |

## Proven / Not proven

**Proven** — walked in a browser on the current schema: password sign-in, email
link sign-in and its verification, the two-step address-then-method form,
sign-in landing, sign-out landing, the stale-destination fix, passkey
enrolment discovery.

**Not proven**: anything native; the one-table session registry and the device
cap (designed, not built); revocation semantics.

## Source

Qori tasks `T-007`, `T-008`, `T-036`, `T-052`, `T-053`, `T-059`, `T-065`,
`T-077`, `T-084`, `T-087`, `T-116`. Decisions `D-006`, `D-007`, `D-012`,
`D-013`, `D-015`, `D-017`. Stream `identity`. Architecture `sessions.md`.
