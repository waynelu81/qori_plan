# Product language and custom terminology refactor

> Selected customer vocabulary, higher-tier custom labels, implementation boundary and acceptance criteria.

[Current plan](../../PLAN.md) | [Planning index](README.md) | [UI redesign](ui-redesign.md)

Recorded 2026-09-08 after the owner rejected school-coded language as Qori's default voice. Updated after testing the replacement nouns as real interface actions.

## Direction

“Teach”, “teacher”, “course”, “lesson”, “student” and “classroom” make Qori sound like school software. They create an unwanted hierarchy: one person teaches and another is taught. Qori is about knowledge moving between people by choice.

The public description is:

> Qori helps you shape what you know into a Series and share it with the Peers you choose.

Qori remains invitation-led. A Group controls identity and context; it does not imply a public catalogue, recurring Peer subscription or community feed.

## Selected default vocabulary

| Existing customer term    | Qori default                 | Natural interface copy                                           |
| ------------------------- | ---------------------------- | ---------------------------------------------------------------- |
| Teach / teaching          | **Share / sharing**          | “Share what you know.”                                           |
| Teacher / instructor      | **No required public title** | Prefer “Shared by Wayne.”                                        |
| Classroom / workspace     | **Group**                    | Prefer the actual name, such as “Ruff Club.”                     |
| Course                    | **Series**                   | “Create a new Series.”                                           |
| Lesson                    | **Episode**                  | “Add an Episode.”                                                |
| Student / learner         | **Peer**                     | “Invite Peers.”                                                  |
| Team member / studio seat | **Collaborator / Team**      | “Invite a Collaborator”; retain Owner/Admin as permission roles. |
| Enrol / enrolment         | **Get access / access**      | “Get access to this Series.”                                     |
| Invitation acceptance     | **Accept invitation**        | “Accept invitation and open Series.”                             |
| Published                 | **Ready to share**           | “Your Series is ready to share.”                                 |
| Teaching dashboard        | **Share**                    | The creator-facing mode.                                         |
| Learning dashboard        | **Shared with me**           | The invitation-led receiving view; do not call it Explore.       |

The core flow reads:

> Create a Series -> add an Episode -> make it ready -> share it -> get access -> continue -> finish.

Use the object's title whenever it removes unnecessary terminology. “Continue Puppy Basics” is better than “Continue this Series.” Do not replace school jargon with a full set of branded jargon on every screen.

## Why Series and Episode

The terms survive the actual button and status tests:

- Create a new Series
- Add an Episode
- 6 Episodes
- Episode 2 of 6
- Ready to share
- Share this Series
- Continue to the next Episode
- Series completed

“Path” and “Step” sounded like workflow software. “Part” was flexible but had no identity. “Episode” is familiar, ordered and creator-led. It may contain text, audio, video, a document, a link, an activity or a live-session reference; the word describes its place in the Series, not its media type.

**Series has the same singular and plural spelling.** Count and grammar logic must select the configured singular/plural field; it must never assume a different spelling proves plurality.

## Peer, creator and Team

Peer is selected because it does not imply school, hierarchy or recurring payment. It deliberately presents the relationship as person-to-person.

- **Peer** always means someone invited to access a Series.
- **Team / Collaborator** means someone who helps manage a Group.
- **Owner / Admin** remain permission roles.
- Public attribution defaults to **Shared by {name}**, avoiding a forced replacement for Teacher.

Do not say a Peer “joined the Group” when the underlying access remains per Series. Show the Group's name for identity, then say the Peer has access to the specific Series. Terminology must not promise group-wide access the product does not grant.

## Navigation model

Do not introduce Studio: it implies a large creative suite and adds a concept the product does not need.

- **Shared with me** contains Series the current person can access.
- **Share** opens the creator side for the selected Group.
- Inside a Group, use plain destinations such as **Overview**, **Series**, **Peers**, **Messages**, **Earnings**, **Team** and **Settings**.
- Show the selected Group's actual name in the context switcher instead of repeating the generic word Group.

Do not use Explore for the receiving view. Without a public catalogue, Explore suggests discovery that does not exist.

## Brand line

The selected working line is:

> **Your knowledge today. Their breakthrough tomorrow.**

It is the boldest and most memorable expression of the intended transformation. Confirm it on Welcome, signup and a real public Series before using it broadly. Reporting and status copy continues to say progress because progress is observable; Qori must not claim that it guarantees a breakthrough.

Retire **Sharing is caring** as the primary Qori line. Do not use **Their future tomorrow**; future and tomorrow duplicate one another.

## Higher-tier custom labels

Custom terminology is configured once per Group and inherited by its public pages and communications. It is presentation data, not a new authorisation or access model.

| Field                          | Default            | Example custom value |
| ------------------------------ | ------------------ | -------------------- |
| Group singular / plural        | Group / Groups     | Pack / Packs         |
| Creator role singular / plural | Creator / Creators | Ruff / Ruffs         |
| Series singular / plural       | Series / Series    | Trail / Trails       |
| Episode singular / plural      | Episode / Episodes | Practice / Practices |
| Peer singular / plural         | Peer / Peers       | Ruffy / Ruffies      |

The Group's display name remains separate from its noun. For example:

- Group display name: **Ruff Club**
- Creator label: **Ruff / Ruffs**
- Peer label: **Ruffy / Ruffies**

Default public attribution remains “Shared by Wayne.” When a custom creator label is intentionally displayed, render it as independent metadata such as **Wayne · Ruff**, not a generated sentence that may be grammatically wrong.

Requirements:

- Store singular and plural explicitly. Never pluralise arbitrary customer words in code.
- Preserve customer casing, accept plain text only and escape output everywhere.
- Set sensible length limits and reject empty or whitespace-only labels.
- Show a live preview using real Series, Episode, count and invitation sentences.
- Fall back atomically to the complete Qori defaults; never mix half a custom vocabulary with half the default set.
- Do not support custom verbs in v1. Arbitrary conjugation, articles and translation make generated copy unreliable.
- Avoid “a/an” before custom terms and do not assume a term can be lowercased.
- Cache by workspace identifier and invalidate on update. Never leak one Group's vocabulary into another.
- Resolve the correct vocabulary on signed-out public and invitation pages as well as authenticated pages.

## Implementation boundary

> **Reversed on 9 September 2026.** The rename went all the way through — models, tables, columns, routes — and the code is the authority on every name; see [`decisions.md`](decisions.md), "The rename went all the way through". The section below is kept as the record of what was decided first and why, and is not to be followed. (Struck 14 September 2026, T-082.)

~~Phase 1 changes the language people see, not Qori's persistence model. Keep these stable unless a separate technical case justifies changing them:~~

- PHP models, collections and service names: `Workspace`, `Course`, `Lesson`, `Enrollment`
- database fields and existing identifiers
- route names and API paths such as `/courses`
- analytics event keys and webhook contracts
- permission roles such as Owner and Admin
- internal workspace-membership records; customer copy presents these as Team/Collaborators

This avoids a high-risk database/API migration for a brand-language decision. Customer-facing components consume terminology keys so a later internal rename remains optional.

## Refactor plan

### Phase 0 — prove the language in context

- Render the defaults on Welcome, first-run Share, Series card, public Series, invitation, checkout, player, progress and certificate screens.
- Read the full flow aloud and test it with representative creators and Peers.
- Confirm that Series/Episode still feels natural for text, document, audio, video, activity and live-link content.

### Phase 1 — central terminology layer

- Define stable semantic keys for Group, creator role, Series, Episode and Peer, each with singular and plural values.
- Expose one resolved vocabulary object to Inertia rather than scattering configuration reads through Vue pages.
- Add server-side helpers for validation, email, notifications, PDFs and certificates.
- Keep actions as authored templates; do not build sentences by joining fragments.

### Phase 2 — replace school-coded copy

- Inventory hardcoded terms across Vue, Blade, controllers, validation, policies, notifications, mail, PDFs, certificates, metadata and tests.
- Replace customer-facing terms with the selected defaults or terminology helpers.
- Update navigation from Teaching/Learning to Share/Shared with me.
- Leave internal diagnostics and developer documentation on stable domain vocabulary where precision matters.
- Update `docs/project-plan.md` so the canonical product specification no longer contradicts this decision.

### Phase 3 — higher-tier customisation

- Add an entitlement-gated settings form with singular/plural fields, examples, reset-to-default and live preview.
- Apply custom terms consistently to Share, Shared with me, public pages, invitations, transactional messages and generated documents.
- Decide downgrade behaviour before launch: preserve configured terms read-only or revert to defaults. Do not alternate by page.
- Record changes in the activity log without treating a display label as a role or permission change.

### Phase 4 — verification and rollout

- Add tests for resolution, validation, fallback, invariant plurals, count selection and cache isolation.
- Prove two Groups can render different terms for the same underlying `Course` and `Enrollment` data.
- Test signed-out public pages, invitations, email, PDFs, certificates, checkout and every access state.
- Search rendered customer surfaces for retired school terms; allow only user-authored content or deliberately technical screens.
- Roll out the defaults first, then custom labels behind the higher-tier entitlement.

## Acceptance criteria

- A first-time visitor understands Qori without Qori calling anyone a teacher or student, or calling content a course or lesson.
- The default flow reads naturally: create a Series, add an Episode, make it ready, share it, get access, continue and finish.
- One Group can display creator “Ruff” and Peer “Ruffy/Ruffies” consistently without changing any permission.
- Peer means the invited audience; Team/Collaborator means someone who manages the Group.
- Per-Series access is never described as joining or unlocking an entire Group.
- Zero, one and many counts use the configured forms correctly, including Series / Series.
- Public pages and communications resolve the same vocabulary as authenticated pages.
- Existing links, purchases, access, progress, certificates, API clients and analytics continue working because internal identifiers remain stable.

## Remaining product decisions

1. Choose the exact paid tier that unlocks custom terminology.
2. Decide whether custom terms remain visible but read-only or revert to defaults after downgrade.
3. Decide whether certificates always use neutral Qori wording or inherit custom Series/Episode/Peer labels.
4. Keep custom terminology Group-wide in v1; reconsider per-Series vocabularies only after real demand.
