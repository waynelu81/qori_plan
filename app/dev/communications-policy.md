# Communications policy

> Consent, reminders, confirmation-email upsell and workspace-timezone rules.

[Current plan](../../PLAN.md) | [Planning index](README.md)

## Consent is captured at enrolment, explicitly and blocking (settled 2026-09-06)

From the human's own experience running this pattern in production: at the moment
a student enrols, the screen states plainly **who** will contact them, **at what
address**, and **about what**. Agreeing is required to get past that screen. If
they refuse, they do not enrol.

This is better than either option previously drafted, and it dissolves the
question rather than answering it. Consent is not _inferred_ from enrolment and
it is not deferred to a later opt-in — it is asked for, in words, at the one
moment the student is paying attention and the relationship is being formed.
`Contact::consented_at` is then written from a real act rather than assumed.

What it settles:

- **`EnrolmentService::contactFor()` stamps `consented_at`** — but only on a path
  that carried the prompt. A creator adding a student by hand in the studio has
  not shown anyone a screen, so that path still needs §9's consent checkbox with
  the creator asserting they have permission.
- **The prompt has to name the workspace and the address**, not say "you agree to
  receive emails". Naming who and where is what makes it informed, and it is also
  what a creator's own compliance rests on.
- **Record what they agreed to, not just that they did.** Store the workspace
  name and address shown at the time. Consent copy changes; a row saying
  "consented at 14:32" cannot answer what was on screen that day, and that is
  precisely the question anyone ever asks about it.

One nuance worth stating once rather than being surprised by later: making
consent a **condition of enrolling** is on solid ground where the messages are
about the course someone signed up for, and is weaker for pure marketing —
under GDPR consent bundled as a condition of service is not considered freely
given. Australia's Spam Act is more forgiving, and §13's launch locales are
en + zh-Hans, so this is not a v1 blocker. It does argue for the split below.

**Split the gate by campaign type.** §9's four types are not alike:

| Type                  | Nature                                         | Gate                             |
| --------------------- | ---------------------------------------------- | -------------------------------- |
| Receipt + access      | Transactional                                  | None — never consent-gated       |
| **Reminders** (below) | Service message about a class they enrolled in | Enrolment, not marketing consent |
| New lesson, stalled   | Service message about a course they are in     | Enrolment, not marketing consent |
| Launch                | Marketing, possibly to people who never bought | `consented_at`                   |

One `acceptsCampaigns()` gate across all of them is what forced the original
binary. Splitting it lets enrolment carry the service messages while marketing
keeps a real opt-in — which is both the safer reading and the more useful
product.

## Course reminders (Pro customises, Start gets the default, Free gets none)

|                            | Free | Start                             | Pro                                                 |
| -------------------------- | ---- | --------------------------------- | --------------------------------------------------- |
| Reminders before a session | None | **One**, Qori's own, fixed timing | **Several**, each with its own offset and send time |
| Template                   | —    | Qori's                            | Theirs (with the §9 template gate)                  |

Consistent with the rest of the Pro ladder: not more capacity, but control over
how the creator appears and when. It also pairs naturally with Pro's custom
templates — same tier, same idea — so the two should ship together.

Open questions this raises, none answered yet:

1. **Reminders before _what_?** `Lesson.starts_at` exists on live lessons (§8.1),
   so a live session has something to count back from. A self-paced course has no
   start date at all — `Course` carries no such field. Either reminders are a
   live-lesson feature, or `Course` gains a start date and the feature widens.
2. **Whose clock is "send time"?** No model carries a timezone — not `Workspace`,
   not `User`, not `Contact`. "Send at 9am" is meaningless until that is decided,
   and the two readings differ: the creator's timezone is simpler and matches who
   configured it, the student's is kinder and matches who reads it. A creator
   teaching across timezones will eventually want the second.
3. **Do reminders count against the monthly EDM allowance?** They cost the same
   to send, but by the table above they are service messages rather than
   marketing, and metering them would meter something a student is owed. Leaning
   no — and if so, they need their own guard so a reminder schedule cannot become
   an unmetered send channel.
4. **This needs a scheduler**, and it is the strongest reason yet to add one:
   unlike campaign sending, a reminder has no user action to hang off. It fires
   because a date arrived. Queue is still `sync` and no environment runs
   `schedule:work`.

## Pro can upsell in the confirmation email

After a student enrols, Pro creators can place an offer in the confirmation
email — other courses, the next module, whatever they want that student to see
next. Free and Start send Qori's plain confirmation.

Consistent with the rest of the Pro ladder, and a sharper version of it: the
other Pro gates are about how a creator _appears_, this one is about what their
email can _do_. It is also the first Pro feature with a direct return — a
creator can name the revenue it earned, which makes it the easiest of the three
to sell.

It rides on the §9 template gate rather than being a separate mechanism: Pro
already customises system email, and an upsell block is a piece of that template
bound to real courses. Build it as part of the template work, not beside it.

Two things it must not become:

- **The confirmation email is transactional and has to stay that way.** Its job
  is telling someone they have access, and that message reaches people who have
  no marketing consent — see the consent split above. An upsell block does not
  change what the message _is_, but it is exactly the kind of addition that
  invites a marketing footer and an unsubscribe link, and an unsubscribe link on
  a course-access email lets a student switch off their own access mail. Keep
  the block inside the transactional template and keep the footer out.
- **It must not delay or endanger the access itself.** The student has paid.
  Whatever the upsell does, a failure to render it cannot be allowed to stop the
  email that tells them how to get in.

Open:

1. **What can be offered?** The workspace's own other published courses is the
   obvious v1, and it needs no new pricing surface — the course already carries a
   price and a public page to link to.
2. **Does it get its own tracking?** Naming the revenue is the sales argument,
   which means knowing an enrolment came from an upsell link. `Enrolment` already
   carries a `source` attribute that `selfEnrol()` sets to `self`, so there is
   somewhere to put it.
3. **Discounted upsell, or list price?** A discount needs coupons on _course_
   sales, which do not exist — only `SubscriptionCoupon` for Qori's own billing.
   List price for v1 keeps this small.

## Timezone: the creator picks one, for the workspace (settled 2026-09-06)

`Workspace.timezone`, chosen by the creator. A reminder set for 9am sends at 9am
in the workspace's timezone, not in each student's. Settles open question 2 under
course reminders.

Simpler than per-student, and honest about who is configuring it: the person
choosing the send time is the creator, so it should mean what they meant. A
creator teaching across timezones will eventually want per-student, and the
schema does not preclude it — `Contact` can gain its own timezone later and fall
back to the workspace's.
