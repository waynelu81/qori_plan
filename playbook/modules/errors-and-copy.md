# Module: errors and user-facing copy

**What it is.** One exception type, one stable error vocabulary, and the rule
that no string a person can read is written inline. It is the module that makes
a second language a translation file rather than an archaeology project.

**Done when.** Every app-defined failure is one exception class raised through a
named constructor; every failure answers *what happened* and *what to do*; and
no user-facing sentence exists outside a language file.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| One exception type or one per feature? | **One**, with named constructors | Per-feature exception classes multiply without ever being caught individually. |
| What must an error carry? | A machine code, a message, and a resolution | A message with no resolution tells someone they are stuck without telling them what to do. |
| What if there is no resolution? | Omit it **deliberately** — that means the path is final | Never invent a hopeful suggestion for a dead end. Omission has to be meaningful or it is just laziness. |
| Which strings go in language files? | Every one a person can read — errors, mail, flashes, notifications, console output aimed at users | If the rule has exceptions, the exceptions are where the untranslated strings hide. |
| What is *not* covered? | Log messages, developer-facing exception text, diagnostics | Those are for whoever is debugging, and translating them helps nobody. |
| Are values restated in copy? | No — interpolated | A mail line saying "expires in 15 minutes" beside a `LIFETIME_MINUTES = 15` is two facts that drift. |
| How big is the error-code vocabulary? | Small, non-overlapping, and treated as a public contract | One code can serve many messages; many codes for one situation cannot be consumed by anyone. |

## Build order

1. **The exception and the code enum.** The enum's values are a contract from
   the moment anything reads them.
2. **Named constructors** per failure, so raising one is a single readable line.
3. **The renderer** — how an exception becomes an HTML page and a JSON body,
   with debug-only fields kept out of production responses.
4. **Language files, one per feature**, not one large file. Needs 1.
5. **A test that walks every language line** for the rules that cannot be
   enforced by review — Qori checks article agreement before interpolated
   nouns, because "an Trail" is wrong and nothing warns you.

## Rules that bite

- **Write for someone mid-task and annoyed.** No vendor names, no status codes,
  no jargon in public copy.
- **Debug fields never reach a production response.** Always record the
  upstream detail when wrapping a third party — in the log, not the page.
- **Plain language-runtime exceptions only for programmer errors** no user can
  trigger.
- **One file per feature.** A single strings file becomes a merge conflict on
  every branch.

## Native contract

**Not proven.** The error code is the shared contract: native clients switch on
the code and render their own copy, so the code vocabulary must be stable and
the message must never be the thing a client parses.

## Traps

| Symptom | Cause |
| --- | --- |
| "The error page shows an internal detail in production" | Debug fields rendered unconditionally. |
| "Translating revealed a hundred inline strings" | The inline-string rule had exceptions. |
| "The copy says 15 minutes; the code says 10" | A value restated rather than interpolated. |
| "A grammatical error only in one language" | An article written before an interpolated noun. |

## Proven / Not proven

**Proven**: the single exception and code enum, error pages in the product's
palette, the language-file rule with a test enforcing article agreement.

**Not proven**: a second locale actually loaded; the JSON error body, which
waits on the native API.

## Source

Qori task `T-002`. Architecture `errors.md`. `CLAUDE.md`, "Errors and
user-facing copy".
