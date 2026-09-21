# Conventions worth adopting

Naming and structure rules that cost nothing on day one. Qori states these in
one file in the code repository and enforces what a test can enforce.

## Where code lives

- **Everything written for one vendor lives in that vendor's own folder** —
  client, calls, response mapping, and any helper only that vendor uses. Every
  kind of vendor: payments, mail, logging, storage, video, meetings.
- **No shared folder for vendor code**, and nothing vendor-specific in a
  generic helpers, data, enums or rules folder, or in a service, model or
  controller. Nothing is shared between vendors either — each sets its own
  timeout and retry, because those are that vendor's limits.
- **The one shared folder is contracts**, because a contract holds no vendor
  code: it states what the product needs in the product's own words, and a
  vendor folder implements it.
- **Integrations take models, enums and scalars in, and hand typed value
  objects or scalars out.** Turning a vendor's payload into a product shape
  happens in the vendor's folder, never on the shape itself.
- **Entry points only delegate.** Controllers, commands, routes and config stay
  where the framework expects them and do none of the vendor's work.
- **No repository layer.** Query on the model or inside a service.
- **Any multi-field shape passed between layers is a typed object**, not a raw
  array.

## Naming a flow

A flow that leaves the product and comes back — a vendor sign-in, a checkout, a
code sent by email — has three step names and only three:

**`begin`** → **`processing`** (as many as needed) → **`finalise`**

- **Never** name a step `return`, `callback`, `complete` or `start`. Where to
  go afterwards is a *destination*, not a return.
- **`fulfil`** is reserved for delivering what a customer is owed — the access
  a payment bought, and the message that tells them. Finishing the product's
  own logic is `finalise`.
- The URL, the route name and the controller carry the same word at both ends.

## URLs

- **Lowercase words joined by hyphens.** Never an underscore, never an
  abbreviation. A value stored with an underscore reaches a URL through an
  explicit slug accessor.
- **Slugs are for reading, ids are for acting.** A GET that renders a page
  takes a slug, because that URL is typed and shared. A write takes the id,
  because the page submitting already holds it and a rename can reassign a
  slug while an id is permanent.
- **Name the parameter for what it carries.** `{thing}` is a slug; `{thingId}`
  is an id. The same path shape means different things by method.
- **The exception is real**: where a slug is not unique across the route's
  whole scope, the id is the only correct key even on a page load.
- **A vendor's return URL names the vendor**, not the service — so one landing
  serves every service at that vendor, and which one is being connected travels
  in the state the begin step wrote.
- **Group routes by what they are *for***, not by who registers them.

## Vocabulary

If any customer-facing noun is configurable, then:

- **Never hardcode it**, and never derive a plural by appending a letter —
  store both forms.
- **Never put an article immediately before it.** "an Episode" is right and
  "an Trail" is wrong, and nothing warns you. Authoring "a new :noun" is safe
  because the article agrees with "new".
- **Never change its casing** — it may be a word the customer chose.
- **Author whole sentences** with the noun interpolated; never build one by
  joining fragments.
- **No authorisation check may read from it.** A custom label grants nothing.

## Tests

- Fake every vendor. Never a real third-party call in a test.
- Assert stable things — status codes, error codes, model attributes — over
  exact prose, unless the prose is the behaviour under test.
- Separate the tests that need the framework from the pure ones, and let the
  pure ones run without it.
