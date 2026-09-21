# Module: tenancy

**What it is.** The organising unit every other row hangs off, and the guarantee
that one tenant never reads another's data. It is the cheapest thing to get
right on day one and among the most expensive to retrofit.

**Done when.** Every tenant-owned read is scoped without the caller
remembering, the crossings that must read across tenants are named and few, and
a test proves a foreign row is invisible rather than merely unlinked.

## Decide first

| Question | Qori's answer | Why |
| --- | --- | --- |
| How many tenants may one person own? | **One** | A switcher implies several. Qori's spec said many; the product never made a second, and the code refused to. Owning one is simpler in billing, payouts, connections and support. |
| Then why a switcher at all? | Because a person may be an *admin* in tenants other people own | That is the only case where one person sees more than one, and it is worth saying out loud. |
| Are the product's staff also users? | No — separate guard, separate table, no self-registration | A staff identity reaching customer data must fail closed. |
| Are paying customers of a tenant "seats"? | No — separate table, uncapped | Seats are the people who *run* the tenant. Conflating them caps the thing the business wants to grow. |
| What stops a cross-tenant read? | A global scope on the model, applied by a trait | A foreign key constrains which tenant a row may *belong* to, never which one a query *reads*. |
| Primary keys? | ULIDs | Ids appear in URLs; sequential integers leak how many tenants and customers exist. |

## Build order

1. **The tenant model and the trait** — global scope for reads plus a write
   stamp, applied to every tenant-owned model, `tenant_id` indexed first.
2. **Per-request tenant context**, one per request or job, resolved once.
3. **The explicit escape hatch** — one named method for the few legitimate
   cross-tenant reads, and a test asserting the list of its callers.
4. **Separate tables** for the people who run the tenant and the people who buy
   from it. Needs 1.
5. **Staff guard**, if there is a console. Independent.
6. **A test that a foreign row is invisible**, not merely unreferenced.

## Rules that bite

- **Do not rely on remembering a `where()`.** The trait is the guard; a
  hand-written clause is a guard you will forget once.
- **Name every crossing.** Qori allows exactly three callers of its escape
  hatch and a test enforces the list.
- **A tenant-scoped uniqueness is not a global one.** A slug unique per tenant
  identifies nothing on a route with no tenant in its path — there, the id is
  the only correct key.
- **Console routes never set a tenant context**, and non-staff get 404 rather
  than 403 on them.

## Native contract

**Not proven.** A token carries **user identity only, never a tenant** — the
tenant is resolved per request. A token that carries one is a second source of
truth that goes stale the moment the person switches.

## Traps

| Symptom | Cause |
| --- | --- |
| "Occasionally someone sees another tenant's row" | A query on a model missing the trait, or a raw builder bypassing the scope. |
| "A slug route resolves the wrong record" | Tenant-scoped slug used on a route with no tenant prefix. |
| "Staff actions skipped a business rule" | An admin-only write path rather than impersonation into the normal one. |

## Proven / Not proven

**Proven**: the scope and trait, one tenant per person enforced in the service,
separate seat and customer tables, the staff guard and console shell.

**Not proven**: impersonation; the console's write phase.

## Source

Qori tasks `T-065`, `T-056`, `T-046`. Decisions `D-003`, `D-012`.
Architecture `tenancy.md`, `admin-console.md`.
