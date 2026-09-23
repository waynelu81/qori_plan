# Positioning for solo creators at the start

Written 23 September 2026 at the owner's word, after the owner shared a
one-person-company case card about Justin Welsh and asked what Qori can be for
the people who want to become him. This is research and a proposed voice, not a
decision: the four questions at the end were asked of the owner the same day,
and `T-190` and `T-191` carry the copy lines that wait on them.

**What it settles:** where Qori sits on a solo creator's path, what is already
built for the start of that path, and the words Qori can use for it. It does
not change `PLAN.md`'s north star or the brand guide's voice; it applies them
to one audience.

[Brand guide](brand/guidelines/qori-brand-guidelines.md) ·
[Onboarding](ui-onboarding.md) · [Competitor prices](../dev/pricing-and-competitor-review-2026-09-11.md) ·
[Kajabi](competitor-kajabi.md)

## The case, corrected

The card says Justin Welsh was laid off, and earned ¥10M selling courses in
five years and nine months, alone, with no ads. Checked against his own
account:

- He was not laid off. He was SVP of Sales at PatientPop (zero to US$50M ARR)
  and had helped build two companies past US$1B. A panic attack in December
  2018 took him out; he left in 2019, at 38.
- The US$10M in five years nine months is his own figure, from his "23 steps"
  essay: US$1M at 29 months, US$10M at five years nine months. His site now
  says US$15M.
- No ads is right. "Alone" is one person plus a part-time assistant on
  support, about 20 hours a week.
- Revenue mix at US$10M: products US$6.75M, consulting US$1.17M, sponsorships
  US$795K, subscriptions US$695K, community US$630K. Margins are reported
  around 86–90% by secondary sources, not by him.
- He is Kajabi's headline customer ("US$10M+ earned on Kajabi") — see
  [`competitor-kajabi.md`](competitor-kajabi.md). The tool the grown creator
  uses is not the tool the beginner needs.

His line, on the card and on his site: "Don't build someone else's idea of a
great life. Build your own." — Justin Welsh. Qori does not borrow it, or any of
his sentences; the moves below are what to learn from.

## The model, in eight moves

The first four are where Qori's people are. The last four are what they want
to grow into, and are not Qori's job.

1. **Noise.** Daily LinkedIn posts from 2018 about what his job taught him.
   No plan, no product, volume over polish.
2. **Signal.** Watched what landed, and read every DM. The questions people
   kept asking were the product research.
3. **Service first.** Answered everyone, then sold his time to the founders who
   had come to him: US$40K on launch day, August 2019. Doubled rates, halved
   hours.
4. **A cheap, rough first product.** The DMs kept asking about LinkedIn itself,
   so he put the answer in a short course: US$50 on Gumroad, 16 April 2020, low
   production. US$10,482 in month one; US$75K over 15 months. The price was set
   to earn trust, not money.
5. **Rebuild the one that works and raise the price.** Same course, redone
   properly, three to four times the price: US$186K in three months. Now
   US$200, lifetime access, no calls, no upsell, no refunds.
6. **Own the list.** A newsletter from January 2022; 185K subscribers in 40
   months. Sponsors pay US$2,500 a slot, two a week.
7. **A ladder.** US$9 a month templates, US$200 courses, a US$549 flagship
   (111 lessons, 19 hours; US$1.6M in six days at launch), affiliates
   (US$600K through 3,247 of his own customers).
8. **Cut what costs the life.** Closed a US$15K MRR community after 15 months
   because the Slack never slept.

What stays constant: he sells the thing his free content is about; everything
is self-serve; buyers keep it forever; no ads; small on purpose.

## Where Qori sits

The target is the person at moves 1–4: a job's worth of knowledge, a few
people already asking (clients, students, DMs, colleagues), files in Drive,
maybe a Zoom class. No audience, no list, no course platform, and no appetite
for one at US$143 a month.

Move 3–4 is Qori's loop exactly: **answer the people who already came to you,
in one place, at a small price, and over-deliver.** So Qori is the room, not
the megaphone. LinkedIn or WeChat is the noise, the DMs are the signal, Qori is
where the answer lives and gets paid for.

What Qori should not become for this audience: the newsletter, the scheduler,
the affiliate programme, the community. He closed the community himself, and
`PLAN.md` already keeps Qori clear of a feed and a catalogue.

## What is built for the start of the path

Checked against the code on 23 September 2026. Paths are the code
repository's.

| His move                        | Qori today                                                                                                                                                                    | Where                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| A rough first product           | One Episode is enough to make a Series ready                                                                                                                                  | `lang/en/share.php`, `next.first_episode`                     |
| A US$50 price to earn trust     | A price per Series, and a price per invitation, 0 for free; repricing touches nobody who already paid                                                                         | `lang/en/series.php` `price_help`; `T-043`, `T-181`, `D-050`  |
| Sell to the people who asked    | Invitations by email with a typed code, no password; a Series link that works on the Free plan, to paste under a post or into a DM                                            | `app/Http/Controllers/PublicSeriesController.php`             |
| Keep the money                  | Direct charges, no platform fee; only Stripe's                                                                                                                                | `docs/project-plan.md` §7                                     |
| Low production                  | Files stay in Google Drive (per-file view access on open), Vimeo by id, links, materials and homework                                                                          | `lang/en/materials.php`, `lang/en/series.php`                 |
| Read the signal                 | Who started, how far they got, who went quiet                                                                                                                                 | `lang/en/share.php`, `next.quiet`                             |
| Lifetime access                 | Access does not expire and survives archiving; deleting the creator's account ends it, which the privacy policy now says                                                       | `resources/legal/privacy-policy.md`                           |
| Free until it works             | Free plan: 1 Series, 50 Peers, 10 invitations a day, 20 MB uploads, payments allowed                                                                                          | `config/qori.php`, `plans.free`                               |
| Live, then the recording        | A live Episode with a join link and a recording card — in progress                                                                                                            | stream `classroom`                                            |

Three small things his path suggests. Ideas, not tasks; the owner decides
whether any becomes one.

- **Say that raising the price later touches nobody already in.** True today;
  `T-191` puts it in the price field's help.
- **Ask a finished Peer for a sentence.** His testimonials came from
  customers; Qori sees the finish and could ask once. Not built.
- **A "who this is for" prompt on the Series description.** His sales page's
  "not for" list is what makes it credible. Not built.

## Words

Original lines in Qori's voice: second person, short, honest about the
tradeoff, no hustle, no vendor but Stripe (`D-035`), nouns through the
terminology layer where they are UI. None is his.

**Home page** (`T-190`), beside the settled claim line:

- Start with the people who already ask you.
- You don't need an audience. You need one Series and the people who already
  trust you.
- Share what your work taught you, with the people who want it.
- Made for one person and the people they teach.
- Not for selling to strangers, not a feed and not a school: for the people
  you already know.
- Your files stay where they are. What they pay is yours, less Stripe's fee.
- Your first Series is free.

**First steps** (`T-191`), as lang lines with placeholders:

- Name your first :series. The thing people keep asking you about is a good
  place to start.
- One :episode is enough to share it. Add the rest as you go.
- Start with a price that is easy to say yes to. You can raise it later;
  :peer_plural who already paid keep what they paid.
- Start with the first few people you would tell about it.

**Pricing page** (`T-104`): the "not for" sentence, in the same words as the
home page. The plan numbers come from the price rows, never from prose.

**Store listing**, for when the native app exists (`PLAN.md` defers it):

- Subtitle, 25 characters: Teach the people you know
- Opener: Qori is for one person with something to teach and a few people who
  already want it. Make one Series from the files you already have, invite them
  by email, reward yourself if you like, and see who gets through it. Nothing is
  listed
  publicly. Nobody sees it unless you invite them.

**Promo**, for a LinkedIn post or the Chinese card format. Free to use; not
code.

- The people who will pay you first are the ones already asking you questions
  for free.
- Before the newsletter and before the course platform: one thing you know, in
  one place, for the people who asked.
- You already have the material. It's in your Drive, your slides and your last
  ten answers.
- Ask a little. Give a lot. Raise it when they tell you to.
- Small on purpose: one Group, one owner, the people you invite.

## The owner's answers, 23 September 2026

Asked and answered the same day, in the conversation that wrote this note.

1. **No word "charge" in Qori's voice.** The owner finds it aggressive:
   "charge if you like" is "reward yourself if you like". The lines above
   say price, pay and ask; the word itself is kept for describing other
   platforms and Stripe's mechanics.
2. **Anyone who wants to share or sell what they know.** No role is named —
   not the ex-corporate, not the coach — and no stage: the lines work for a
   person with no audience and for one with a small following, because they
   start from the people who already ask, which both have.
3. **"Share" leads.** The owner likes it, and the plan and the home page
   already lean that way. Suggested to the owner: the brand guide's subline,
   "A private classroom for people you already teach", becomes "Share what
   you know with the people you choose", which the pricing page already says;
   "teach" stays available inside the product where the classroom stream
   needs it.
4. **The Chinese card is a reference only.** English first; no zh-Hans line
   now.

## Sources

Read 23 September 2026: [justinwelsh.me](https://justinwelsh.me/),
[About](https://justinwelsh.me/about),
[My complete $10M journey, 23 steps](https://justinwelsh.me/essays/my-10m-journey),
[The Creator MBA](https://learn.justinwelsh.me/creator-mba),
[Store](https://learn.justinwelsh.me/store),
[Growth In Reverse](https://growthinreverse.com/justin-welsh/),
[Everything-PR](https://everything-pr.com/justin-welsh-solopreneur-creator-economy),
[Osmosis podcast](https://www.osmosis.org/podcast/turning-what-you-know-into-a-business),
[meet-lea](https://meet-lea.com/en/success-stories/justin-welsh/justin-welsh),
[Kajabi home page](https://www.kajabi.com/). The margin and assistant figures
are secondary sources; everything else is his own account.
