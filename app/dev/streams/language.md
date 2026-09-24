---
stream: language
---

# Stream: language

**Goal.** Let an eligible Group speak its own words, everywhere, without
touching a single authorisation rule.

**Done when.** Two Groups render different nouns for the same underlying rows,
on authenticated pages, public pages, invitations, email and generated
documents — and a custom label has never granted anybody anything.

**State.** The resolution layer is built and tested: `App\Support\Terminology`,
`App\Data\Vocabulary`, `lang/en/terminology.php`, the shared Inertia prop and
`useTerminology()`. Storage is `groups.settings.vocabulary`; the entitlement is
the plan flag `custom_vocabulary`, currently **false on every plan**.

What is missing is the way in — there is no form — and the surfaces that still
speak inline English. Since `T-048` (24 September 2026), `ProductNounsTest`
fails any lowercase product noun in a page's prose outside the staff console,
and any page that calls the Group a school; the one allowed line left for
another task is `Register.vue`'s share hint, `T-108`'s.

## Tasks, in order

1. `T-004` — Vocabulary settings form behind the entitlement
2. `T-048` — The receiving home offers a school: one sentence on the dashboard
   still spells a noun the vocabulary owns
3. `T-005` — Apply the vocabulary to mail, PDFs and certificates
4. `T-006` — Convert the remaining inline English in Vue to lang keys

## Owner decision needed before T-004 ships

Which paid tier sets `custom_vocabulary`. Shipping it enabled for a tier would
answer that by accident, so it is false everywhere until somebody chooses. The
form can be built and tested against a config override in the meantime.

Also open, from [`../terminology-refactor.md`](../terminology-refactor.md):
whether a downgrade keeps custom terms read-only or reverts to defaults.
