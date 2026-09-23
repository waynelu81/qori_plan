---
id: T-190
title: The home page says who Qori is for
stream: design
status: doing
owner: claude
estimate: S
depends: none
blocks: T-193
---

# T-190 — The home page says who Qori is for

> Written on 23 September 2026 from
> [the positioning note](../../design/positioning-solo-creators.md), at the
> owner's word, and made ready the same day on the owner's answers.

## Why

`Welcome.vue` says what Qori is — the claim line, one sentence on shaping a
Series, and a note that nothing is listed publicly — and nothing about who it
is for. The person Qori is built for is at the start of the path the
positioning note describes: a job's worth of knowledge, a few people already
asking, no audience, no list, and no appetite for a course platform at US$143 a
month. That person reads the page today and cannot tell whether they are early
enough for it.

Afterwards the page says, in one sentence, that they are: start with the
people who already ask you. Under the buttons it says what Qori is not for,
that their files stay where they are, that what Peers pay is theirs less
Stripe's fee, and that the first Series is free. The headline's missing space
at mobile width (`R-004` F-9), which the design stream left to whoever next
edits the headline, goes with it.

## Decisions taken to make this specifiable

**The lines stay inline English, as `T-048` decided for the dashboard panel.**
Every other string on this page is inline, and converting Vue templates to lang
keys is `T-006`'s whole job; one lang key here would leave the page
half-converted.

**The nouns come from `useTerminology()`,** which the page already destructures
as `noun` and `plural`. No article sits immediately before a noun.

**No number is written on the page.** "Fifty Peers" and "ten a day" are
`config('qori.plans.free')`, and a marketing line that restates a limit drifts
the day the limit moves. The page says the first Series is free; the pricing
page carries the numbers, from the price rows.

**Stripe is named.** `D-035` confirms it, and "less Stripe's fee" says more
than "less the card fee".

**The "not for" paragraph joins the invitation-led note rather than replacing
it.** The note is a fact about the product; the new paragraph is a stance. Both
are small type under the buttons.

**No role, stage or "charge".** The owner's answers of 23 September 2026:
Qori is for anyone who wants to share or sell what they know, so the lines
name no job and no audience size; "share" leads, not "teach"; and the word
"charge" is not Qori's — the lines say pay and price. English only; the
Chinese card that prompted the note is a reference.

## Preconditions

**Data this task verifies against:** a clean database; the page reads nothing.

**Equipment:** a browser at 390px and 1440px, signed out, to read the lines in
place and check the headline at mobile width.

## Scope

**In:**

- A sentence about who Qori is for, opening the paragraph under the headline,
  before the existing "Shape what you know…" sentence.
- A second small-type paragraph after the invitation-led note: not for
  strangers, files stay where they are, what Peers pay is theirs less Stripe's
  fee, the first Series is free.
- The missing space between the headline's `<br>` and its second span
  (`R-004` F-9).

**Out:**

- Converting the page to lang keys (`T-006`); a `PublicHeader` (`T-104`).
- The pricing page: its sentence is `T-104`'s, in the same words.
- The claim line, "Your knowledge today. Their breakthrough tomorrow." —
  settled in `PLAN.md`.
- The store listing and promo lines in the positioning note, which are not
  code.

## Files

| Path                             | Change | Notes                     |
| -------------------------------- | ------ | ------------------------- |
| `resources/js/pages/Welcome.vue` | edit   | Two paragraphs, one space |

Flows: none — copy on a `Route::inertia` page.

## Database

None.

## Code

The headline and the buttons do not change.

```vue
<p class="text-muted-foreground mt-6 max-w-xl text-lg leading-relaxed">
    Start with the people who already ask you. Shape what you know into one
    {{ noun('series') }} and share it with the {{ plural('peer') }} you choose.
</p>
```

```vue
<p class="text-muted-foreground mt-10 text-sm">
    Qori is invitation-led. Nothing you make is listed publicly, and nobody
    sees it unless you share it with them.
</p>
<p class="text-muted-foreground mt-3 text-sm">
    Not for selling to strangers, not a feed and not a school: for the people
    you already know. Your files stay where they are, what your
    {{ plural('peer') }} pay you is yours less Stripe's fee, and your first
    {{ noun('series') }} is free.
</p>
```

The F-9 fix: `<br class="hidden sm:inline" />` is followed directly by the
span, so below `sm` the two halves of the headline run together. Put a space
between them, `{{ ' ' }}` if the formatter strips a literal one.

## Copy

None as lang keys — see the decisions. The English is in the Code section.

## Routes

None.

## Tests

**New:** none. The prose lives in a Vue template no test reads, and asserting
marketing prose word for word would pin what the owner may still reword.

**Changed:** none. `LegalPageTest` already renders `/` and stays green.

## Acceptance

- [ ] A guest at `/` reads who Qori is for in the paragraph under the
      headline, and the stance paragraph under the buttons, at 390px and 1440px
- [ ] The headline reads as two lines with a space between them at 390px
- [ ] Every noun comes from `useTerminology()`, no article sits before one, and
      no plan number is written on the page
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

The lines come from the positioning note's "Words" section, which also holds
the store listing and promo lines that are not this task's.
