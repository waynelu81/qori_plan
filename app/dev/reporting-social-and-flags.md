# Reporting, social features and flag audit

> Preserved product-fit research and data-modelling audit.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## Reporting: what the data can already answer

Nothing here is built. This is what is _derivable_ from what is captured today,
separated from what is not, because the difference points at one missing model.

### For the creator — available now

| Report                                 | From                                                    | Why it earns its place                                                                                                  |
| -------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Revenue over time**                  | `enrolments.price_cents` + `enrolled_at`                | Real money, monthly bars. The only chart most creators actually want                                                    |
| **Enrolments over time, free vs paid** | Same rows; a null price means given away (§21.1)        | Shows whether free courses feed paid ones                                                                               |
| **Per-course leaderboard**             | Enrolments grouped by `course_id`                       | Which course to make more of                                                                                            |
| **Contact funnel**                     | `contacts.status` — prospect → enrolled → customer      | The field is already literally a funnel; three bars, no new data                                                        |
| **List health**                        | `consented_at`, `unsubscribed_at`, `email_suppressions` | Unsubscribes and bounces are early warning on deliverability, and they are the creator's problem before they are Qori's |
| **Campaign delivery**                  | `campaigns.stats`, already written on send              | Sent, skipped, and why. **Not** opens or clicks — nothing tracks those                                                  |
| **Email allowance**                    | `CampaignService::allowance()`                          | Built                                                                                                                   |
| **Storage per course**                 | `media_assets.size_bytes`                               | Needs the `course_id` the flag audit already flagged as missing                                                         |

### For the creator — needs the progress model

The single most valuable creator chart cannot be drawn: **drop-off by lesson.**
"Everyone stops at lesson 4" is the one insight that changes what a creator makes
next, and it needs a completion record that does not exist. Same model unlocks
completion rate, time-to-complete, the §9 stalled campaign, and §12's
certificates. Four features behind one model is the strongest argument in the
build order.

Also absent and worth knowing: **no opens or clicks.** That is a deliberate
consequence of not running tracking pixels, and it should be said out loud on the
report page rather than looking like a gap — "we do not track whether your
students opened it" is a defensible sentence for this product, and an
indefensible silence.

### For the student — mostly no

An honest answer: **students do not want charts, they want to know what to do
next.** A learner dashboard full of graphs is a product talking about itself.

Two things genuinely help, and only one is a chart:

1. **A progress bar per course, and "continue where you left off".** Needs the
   progress model. This is the whole of it.
2. **Upcoming live sessions**, from `lessons.starts_at` — derivable today, and a
   list rather than a chart.

Explicitly rejected: streaks, leaderboards, "you are in the top 10%". They are
engagement mechanics for products that need to manufacture a reason to return,
and Qori's students have one already — they paid for a course and want the
thing inside it. §1's voice is "sharing is caring", not a habit loop.

### Keeping reports cheap

- **Aggregate at write time where the row count is large.** `campaigns.stats`
  already does this, and it is the right pattern: never scan
  `campaign_recipients` — millions of rows — to draw one bar.
- Enrolments and contacts are small enough to aggregate on read for a long time.
  Do not pre-compute what a thousand rows can answer.
- Any report over `activity_log` must respect its TTL: a chart that silently
  shortens when rows expire is worse than one that states its window.

## Social features: what fits, and what does not

Prompted by Dabble (social betting — follow a punter, copy their bets, get a
push). The question was whether Qori wants an equivalent: follow a student,
one-click enrol in what they enrolled in.

### Follow-a-student is a bad fit, and the reason is not squeamishness

Three separate objections, any one of which is enough:

1. **What someone is learning is not what someone is betting.** A punter chooses
   to be public about a wager. A student enrolled in _Managing Anxiety_,
   _Bankruptcy Basics_ or _Getting Back Into Work_ has disclosed something about
   their life to one teacher, not to an audience. A follow-graph makes a private
   circumstance discoverable, and no consent checkbox really fixes that — the
   default has to be that nobody can see it, at which point the feature has no
   graph to run on.
2. **The behaviour is too sparse to build on.** Copy-betting works because
   punters place many bets quickly and the outcome is public and verifiable. A
   student enrols in perhaps three courses a year. There is no signal, and no
   feed that is not mostly empty.
3. **It points at the wrong customer.** Qori's paying customer is the creator. A
   student follow-graph sends students to _other people's_ courses from inside
   the classroom a creator paid for — which any creator would reasonably object
   to, and which §1 rules out anyway ("does not go hunting for students").

### What does fit, in order of how well

1. **Student referral with attribution — the strongest.** A student shares a
   course with someone they know; the creator gets a new student; the referrer is
   recognised. It is the brand line ("sharing is caring") expressed as a
   mechanic, it is private by construction — one person to one friend, no feed —
   and it points the right way, bringing the _creator_ students rather than
   diverting them. `enrolments.source` already exists as the place attribution
   lands, so the data model is ready. This is the growth loop Qori lacks without
   a marketplace, and it is the one worth designing properly.
2. **Cohort presence.** "Eleven others are working through this course",
   "four people are in Thursday's session". Not a feed and not identities —
   just the fact that you are not alone, which is the single most common thing
   missing from self-paced learning. Cheap, and it needs the progress model that
   four other features already need.
3. **Per-lesson discussion.** Already in the roadmap. A thread scoped to one
   lesson has no discovery surface and no algorithm, so it stays inside the
   private classroom while being the thing people actually want from "social".
4. **Creator-to-creator, not student-to-student.** Two creators cross-promoting,
   co-teaching, or bundling courses is a social graph aimed at the paying
   customer. It fits the shared catalogue already planned, it is B2B so the
   privacy objection evaporates, and a bundle is a product a creator can sell.
   Worth more thought than the student graph ever was.

### Push notifications

The app is a reader for students (§6), so pushes should be about **their own**
courses — a new lesson published, a live session starting soon, a certificate
earned. Those are service messages and ride on enrolment, per the consent split.

A push saying "someone you follow just enrolled in X" is the wrong product in one
sentence: it interrupts a person on behalf of a stranger, to sell something
neither of them chose. Do not build it.

## Flag audit, 2026-09-06

Prompted by the question of whether flags should be booleans, timestamps, or a
boolean plus a timestamp. The codebase is already consistent about this; three
fields are not, and one of them makes a shipped feature inert.

### The rule the codebase already follows

| The field answers            | Shape                                                         | Examples                                                                                                                       |
| ---------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Did something happen?**    | Nullable timestamp, **no boolean**                            | `consented_at`, `unsubscribed_at`, `email_verified_at`, `confirmed_at`, `revoked_at`, `accepted_at`, `two_factor_confirmed_at` |
| **Is something configured?** | Boolean, **no timestamp**                                     | `is_preview`, `is_public`, `is_active`                                                                                         |
| **Which of several states?** | Status constant, plus timestamps for transitions worth dating | `Course.status` + `published_at`, `Enrolment.status` + `enrolled_at`/`revoked_at`                                              |

**A nullable timestamp is the flag.** Null means it has not happened; a value
means it has, and says when. Adding a boolean beside it creates two sources of
truth that can disagree, and with no trigger maintaining the second one, nothing
stops them drifting. Do not pair them.

The boolean cases are settings rather than events: someone flips `is_public`
back and forth and "when was it last toggled" is not a property of the row. Where
that history does matter it belongs in `staff_audit_log`, which already records
who and when for exactly these.

**`published_at` deliberately survives unpublishing.** `publish()` writes
`$course->published_at ?? now()`, so it means _first_ published rather than
_currently_ published; `status` is the authoritative current state. The two
cannot disagree because they answer different questions. Worth knowing before
someone "fixes" it.

### Three fields that break the pattern

1. **`Contact::consented_at` is never written by application code, and it gates
   every campaign.** `acceptsCampaigns()` returns
   `unsubscribed_at === null && consented_at !== null`, and the only place a
   contact is created — `EnrolmentService::contactFor()` — does not set it. No
   UI sets it either. So **the EDM feature can send to nobody**: confirmed
   against dev data, where Rita's workspace has 2 contacts and 0 that can
   receive a campaign. The suite passes only because
   `Contact::factory()->consented()` sets it explicitly, which is the same shape
   as trap 6 — a feature that is fully built, fully tested, and silently inert.
   §9 says "consent checkbox when creating a prospect", and there is no prospect-
   creation surface at all yet. **The product decision is now made** — see
   "Consent is captured at enrolment" above: an explicit, blocking prompt at
   enrolment writes it, and the gate splits by campaign type so service messages
   do not wait on marketing consent.

2. **`Workspace::hibernated_at` is dead.** Cast on the model, set by the factory,
   never written or read by any application code; `isHibernated()` uses `status`.
   Either write it when a workspace hibernates — §21.8's data-hygiene rules are
   about elapsed time, so a date is plausibly wanted — or drop the field and the
   cast.

3. **`Staff::disabled_at` is dead.** Never written, never read, so a staff member
   cannot be disabled. §24 does not require it explicitly, but a console with no
   way to revoke a colleague's access is a gap worth closing rather than a field
   worth deleting.

### What fixing (1) now takes

1. A consent step in the enrolment flow that names the workspace and the address,
   and blocks progress until it is agreed.
2. `EnrolmentService::contactFor()` writing `consented_at` on that path, plus the
   workspace name and address as shown.
3. §9's consent checkbox on the studio's own add-a-student path, where no student
   ever saw a screen.
4. Splitting `acceptsCampaigns()` so service messages ride on enrolment and only
   `launch` waits on marketing consent.
