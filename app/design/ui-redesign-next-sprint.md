# Next redesign sprint — make Qori feel tangible and finished

Recorded 2026-09-10 following the owner's feedback that the interface feels
empty and unfinished, and their positive response to the recommendations below.

**Status:** proposed direction for the next redesign sprint. This is a design
recommendation report, not a new review pass, a frozen implementation spec or
authorisation to begin building.

[Planning index](README.md) · [Current redesign brief](ui-redesign.md) ·
[R-002: interface findings](design-review/passes/R-002-2026-09-10-surface-and-state-second-look.md)

Follow-up: [component recommendations and sign-in design](ui-components-and-sign-in.md)
records the available foundations and the owner's requirement to offer both
Password and Email link, with app QR login deferred.

**Onboarding sequence updated by the owner, 2026-09-11:**
[creator setup now precedes guided first-Series creation](ui-onboarding.md).
The object compositions below apply to that guide and ongoing home; they must
not bypass required profile/Group confirmation or put a Series-link recipient
through creator setup. Storage, integrations and seller setup are skippable;
selling readiness is required at the paid-selling action.

## Assessment

Qori has a consistent visual foundation, but the screens do not yet make the
product feel tangible. Warm paper, charcoal, gold actions and the open-Q mark
already provide a recognisable family. The next improvement should come from
composition, visible Series identity and emphasis on the person's current task.

The captured welcome page places a small text block inside a large canvas.
Creator home devotes substantial space to a next-action notice, an expanded
Group-name form and metrics. Small initial tiles give Series limited presence.
Repeated, similarly weighted panels make the creator interface feel like a
stack of administration forms. Receiving cards show inventory facts more
prominently than the relationship and the next Episode.

These are design interpretations informing a future direction. The concrete
defects and their dispositions remain in R-002; this report does not add findings
to that historical pass.

## Recommended direction

### 1. Let welcome show what someone can create

Pair the headline with a substantial, clearly labelled example Series: its
title, the person sharing it, a short introduction and a few Episodes. Use that
composition to explain the product alongside the promise.

On desktop, explore a headline/action area beside the Series preview. On mobile,
keep the headline and **Start sharing** action first, then the compact preview.
Any example must be labelled as such; it must not imply real customer activity.

**Intended result:** a visitor can recognise what a Series is and what starting
with Qori will produce.

### 2. Make creator home feel like the creator's workspace

Give the main area to the current Series, with its next action attached to the
object. Include recognisable identity and enough context to explain the action.
For example, the composition could show the Series title, that its first Episode
is ready, and the permitted access-sharing action together. Example wording is
illustrative, not approved production copy.

Use a compact Group-name edit control once the name is established; reserve a
prominent naming prompt for the state that needs it. Place useful activity below
the Series. A new creator should see a Series-shaped starting point in the same
space, with one permitted create action.

**Intended result:** the first screen answers what the person is creating and
what to do next, without making an established Group feel perpetually in setup.

### 3. Give Series stronger visual identity

Develop a restrained cover system using warm tonal fields, deliberate typography
and a subtle repeatable motif. It should work without uploaded images and remain
recognisable across creator, receiving and public compositions. Preserve the
brief's requirement that generated identity is stable across title changes.

Keep compact rows for inventories that need scanning, but let titles retain
their identifying words. A larger object treatment belongs where a Series is
the focus; it need not turn every list into a grid of large cards.

**Intended result:** Series feel like identifiable things people make and share,
with consistent identity across their different audiences.

### 4. Establish hierarchy within creator pages

Give Series identity and the current task the strongest emphasis. Make secondary
editing controls quieter and available when needed, without adding a search for
the completing control. Constrain desktop form interiors to a readable width.

Differentiate object presentation, the main action, supporting information and
secondary management through spacing, scale and placement. Reuse the existing
foundations; a bordered panel need not give every section equal prominence.

**Intended result:** someone can recognise the main task immediately, while
secondary controls remain predictable and reachable.

### 5. Make receiving views personal and actionable

Emphasise who shared the Series, what the person is working through, their next
Episode and a clear **Continue** or **Start** action. Keep progress attached to
the Series and express it in meaningful Episode counts. Give joined dates a
secondary role.

**Intended result:** Shared with me helps someone resume their activity and
recognise its source, rather than merely reporting that access exists.

## Sprint focus and order

1. Establish the stronger Series identity and object composition on creator home.
2. Apply the audience-specific version to Shared with me, including attribution
   and continuation.
3. Use the same visual identity in the welcome example, with its own public
   composition and explanation.
4. Carry the hierarchy and form-width rules into the affected Series screens.

The three anchor compositions are **welcome, creator home and Shared with me**.
Review them together before expanding the visual scope. Resolve R-002's misleading
actions and title-layout defects alongside this work; they affect whether the
finished-looking interface can be trusted and used.

## Boundaries and review criteria

- Retain the palette and logo as the starting foundation. A replacement brand
  identity is not proposed.
- Work with the product's real objects, relationships and supported actions.
  Do not invent activity, metrics or capabilities to occupy space.
- Preserve role and plan restrictions, object-first empty states, direct
  completion controls and the terminology contract in the current brief.
- Review empty, one-item and populated compositions together, including long
  titles and permission/plan restrictions.
- Carry forward both-theme checks, the required 360px/768px/desktop widths,
  keyboard/focus, contrast and interaction-state verification. Attractive static
  compositions do not replace those gates.
- Before implementation, settle the proposed compositions and any interaction
  changes, record new product-intent decisions in `decisions.md` if needed, and
  create scoped tasks through the existing planning process.

## Evidence and limits

Recommendations are based on the screens reviewed in R-002, from
`docs/design-review/2026-09-10-0300-561095f-dirty` at `561095f-dirty`.
They are not usability-research results or validation of a new design.

Concurrent Series-form changes appeared during that review, including T-030 and
T-031. Start sprint design work with a fresh capture so those changes are included
and completed work is not inadvertently specified again.

This report records the recommendation only. No application changes, design
mockups, task files or commits were produced for it.
