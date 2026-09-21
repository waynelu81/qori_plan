# Qori — project plan

Working name: **Qori**. Folder: `/Users/dev/dev/qori`. This document is the product plan for the **webapp** first. Native iOS/Android come later and should reach about 90% of web capability.

Not legal, tax, or financial advice. Store/name checks were public searches only. Entity notes are operating decisions for this product, not a structure for the company being exited.

---

## 1. What it is

A **private classroom**, not a university LMS and not a stall that sells anything to strangers.

Brand feel: **sharing is caring** — you pass on what you know to people you already look after (clients, students, your list). Money is optional infrastructure, not the story.

- **Who we serve:** people who teach in public (KOLs, coaches, buyer’s agents, one-person practices, small agencies).
- **Who learns:** people they already know. Qori does not go hunting for students.
- They publish a **course** (module) made of **lessons** — a private series of materials. In v1, access can be a one-off enrolment if they choose to charge.
- One product for solo and “school”: **one workspace**, different plan limits — not two apps.

Positioning vs Teachable / Thinkific / Skool: easier on the phone, **their files stay theirs**, Qori **carries the email** so they can look after the group. They keep files and any student payments; we keep enrolments, access, and mail.

**Audience and pitch clarified 11 September 2026:** lead with creators who
already use **Google Drive, OneDrive, Dropbox and YouTube** for their materials.
The target promise is **“Start sharing with the files you already have”**:
connect familiar tools and organise their content into a Series without moving
the source files. Qori's paid value is the teaching and sharing workflow around
those files. Compare subscriptions directly for this audience; do not add an
assumed storage or video-hosting subscription to Qori's price. Provider support
must be working before it is advertised. See the
[owner decision](planning/decisions.md#position-around-creators-existing-files-and-familiar-tools-2026-09-11)
and [revised pricing review](planning/pricing-and-competitor-review-2026-09-11.md#owner-clarification-existing-files-are-the-starting-point).

---

## 2. Naming

### Chosen (working)

**Qori** — invented/short. Quechua “gold” is a nice aside; English users will not hear 课. Public scan: no major App Store / Play title clash found. Still confirm `.com` / `.app` and IP Australia + USPTO class 9 / 42 before locking the brand.

Store listing shape: **Qori — sharing is caring**

Voice: share with your people, not “sell anything.” Avoid marketplace / bargain / hustle copy. Subtitle can mention a classroom or program; it does not have to mention price.

### Ten naming suggestions (researched)

Public App Store / Play / brand scan. Prefer invented words or short codes. Avoid lesson-themed first words that collide (Keto diet, Folio wallet + AppFolio + library FOLIO, Podium.com reviews).

| Name               | Example listing                        | Store / brand notes                                                                                           |
| ------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Qori**           | Qori — sharing is caring               | **Working pick.** No major exact app found. Check domains + TM.                                               |
| **Blen**           | Blen — for the people you teach        | No major exact app found.                                                                                     |
| **Ixel**           | Ixel — your private classroom          | No standalone app found. Speech can sound like “Excel”.                                                       |
| **Drov**           | Drov — share it with yours             | None found.                                                                                                   |
| **Jexa**           | Jexa — teach from your phone           | No consumer app; small IT firms named Jexa.                                                                   |
| **Wexa**           | Wexa — keep the group together         | None found. Speech can sound like “Wix”.                                                                      |
| **Hext**           | Hext — one place for your program      | No exact Hext app; nearby Hexel/Hexpel games.                                                                 |
| **Pelm**           | Pelm — look after your program         | No consumer app; inactive YC utilities API leftover in Google.                                                |
| **Lectern Studio** | Lectern Studio — teach from your phone | Two-word. Hobby GitHub LMS “Lectern”; Lecto Studio (Canvas builder) similar sound. Cleaner than Folio/Podium. |
| **Roster Class**   | Roster Class — your people, your room  | Two-word. Generic; sports roster apps. Weaker ASO.                                                            |

**Dropped after search (do not use):** Keto / Keeto (diet category + `keto.app`); Folio (wallet app, EBSCO FOLIO libraries, AppFolio / Folio by Amitree for real estate); Podium (Podium.com + App Store, classroom AI at podiumapp.live); Kova, Vexl, Mivo, Tavo, Orvo, Ryvo, Gleo, Plio, Qulo, ARCA, BRIO, ELAN.

Same name on **web, iOS, and Android**.

---

## 3. Who uses it

| Role                   | How they arrive                    | Job                                      |
| ---------------------- | ---------------------------------- | ---------------------------------------- |
| Creator / owner        | App Store / Play (free tool) + web | Build courses, enrol, EDM, pay Qori      |
| Admin (paid, up to 20) | Invited                            | Teaching side except billing             |
| Student                | Teacher’s email → web              | Get access, then watch on web and/or app |

One login can teach and learn.

---

## 4. Funnel (locked)

```
App Store / Play (free) → creator installs
  → builds courses in app and web
  → Qori invoices SaaS → pay on the web (Qori’s Stripe)
  → EDM built on web → send / recipients on web or app
  → they invite their people (EDM)
  → learner enrols on the web (charges only if the teacher chooses)
  → email: you’re in + optional “get the app”
```

- Apps attract **teachers**. Learners are not the store audience.
- **No payments in the app.** No Apple/Google IAP.
- Learner path: **enrol and watch on web**; app is a nicer way in, not a lock on the door.
- Creator SaaS: Stripe Invoice / hosted Billing; in-app **Pay this invoice** opens the **browser**.

---

## 5. Pricing (subscription, cheap entry)

**Review note, 11 September 2026:** the table below is the original price sketch,
not a confirmed live offer. School was subsequently made available on request,
without a public $499 price. Current vocabulary and beta scope follow `PLAN.md`.
See §5.1 for the current competitor review and proposed packaging.

**22 September 2026 (`D-046`, `D-047`):** Start and Pro are set at the
review's figures, US$39 and US$99, with fixed prices of their own in the
major currencies — A$55 and A$139 among them. Everyone else pays the USD
price; no price moves with the exchange rate.

Price **courses**, not individual lessons inside a series. **0% platform fee** on student checkout. Creators pay **Stripe’s** processing on **direct charges** (not a Qori cut, not a destination-charge recoup). Qori **eats** Stripe fees on **SaaS** — bake them into Start/Pro/School; no card surcharge.

| Plan       | Price (sketch) | Courses                                                                          | Team members       | Notes                                                                                                                       |
| ---------- | -------------- | -------------------------------------------------------------------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **Free**   | $0 forever     | **1 course** (cap lessons inside it, start with **1 lesson** if a sharper nudge) | **1** (owner only) | Neon / Laravel Cloud spirit                                                                                                 |
| **Start**  | ~$39–49/mo     | Unlimited                                                                        | **20** ceiling     | One person in practice; 20 is an anti-sharing cap, not a seat SKU                                                           |
| **Pro**    | ~$99/mo        | Unlimited                                                                        | **20**             | Same login cap; extras TBD (domain, certificates, EDM volume, listing)                                                      |
| **School** | ~$499/mo       | Unlimited                                                                        | **20**             | Prefer on day one if a visible delta exists (e.g. light white-label, bulk contacts, certificates). Do not sell extra seats. |

**Students are never “seats.”** Enrolments unlimited (or a very high cap). Do not copy Teachable’s 100-student trap.

**Not selling seats.** All paid plans share the **20 admin** ceiling. Free = 1 owner. Prefer **20**, not 30.

**Unpaid / free SaaS lock**

- Cannot **publicly list** on `/lessons`.
- EDM: **10 sends per day**.
- Transactional mail (magic link, receipts) stays unlimited.
- Recommend: they **can take student payment** on the free course (conversion path). Confirm before build.

**3-month friction:** inconvenience for the **creator** (banner, freeze edits, or hibernate the teaching side). **Enrolled students keep access.** Do not expire paid content out from under buyers.

**Currency for SaaS:** **USD** is the base price of Qori Start/Pro, and the major currencies — AUD, EUR, GBP, CAD, NZD, SGD — carry **fixed prices** the owner sets. A buyer in any other currency pays USD, and Adaptive Pricing is off (`D-047`, 22 September 2026, amending `D-046`'s AUD base the same day). Qori's Stripe account settles in AUD, so every non-AUD sale pays Stripe's 2% conversion. Student course prices live on **their** Connect account (their currency). GST on Qori SaaS to AU customers applies once Qori registers for it.

---

### 5.1 Competitors and pricing review

Qori's working competitor shortlist is:

- **Course and creator platforms:** Thinkific, Teachable, Podia and Payhip.
- **Community platforms:** Skool, Circle and Mighty Networks.
- **Broader creator-business platform:** Kajabi.
- **Existing-workflow substitute:** email, shared files and Zoom/Teams with manual follow-up.

The [11 September 2026 pricing and competitor review](planning/pricing-and-competitor-review-2026-09-11.md)
compares official vendor prices and fees, identifies Qori's current strengths
and unfinished features, and proposes a Free / Start / Pro ladder with School
by enquiry. Its price recommendations remain proposals for discussion; no
Stripe prices or application entitlements were changed by the review.

---

## 6. Surfaces

|         | Web                                               | iOS / Android (free download)               |
| ------- | ------------------------------------------------- | ------------------------------------------- |
| Role    | Full product + **all payments** + EDM **builder** | Daily tool; ~90% of web                     |
| Creator | Everything                                        | CRUD courses/lessons, students, EDM **ops** |
| Student | Buy + watch                                       | Watch only (reader app)                     |
| Billing | SaaS invoice + Connect + student checkout         | Invoice **status** + Pay → browser          |

**EDM:** drag-and-drop composer = **web only**. App: scheduled list, send status, add/remove recipients.

**Sessions:** max **3 live sessions per user** (web + app + one spare — revised up from 2, which made the cap identical to normal web+app use and would have tripped anyone with two computers). A fourth login revokes the least-recently-used one. Do **not** log out the other device on every login (breaks web + phone). Optional “log out all other sessions” in settings. Mechanics in §22.

---

## 7. Money (one Stripe platform, direct Connect)

One Stripe platform account: **Qori's own platform account**. SaaS subscriptions bill directly on it. Creators **bring their own Stripe account, or open one on Stripe's own page**, and connect it to Qori's platform as a **connected account** through Stripe Connect's sign-in; Qori never opens an account for them or asks what Stripe's page asks (`D-023`). Their student charges run as **direct charges** on that connection.

| Money                | Where it runs                                           | Charge type                          | What                            |
| -------------------- | ------------------------------------------------------- | ------------------------------------ | ------------------------------- |
| Creator pays Qori    | **Qori's platform account** (Billing / invoices)        | Ordinary Subscriptions               | Start / Pro in **USD**, fixed in major currencies (`D-047`) |
| Student pays creator | **Creator's connected account** (under Qori's platform) | **Direct charges**, Standard Connect | One-off course in v1            |

No platform wallet. No in-app course buy. Xiaohongshu / shop later = redeem code or webhook → enrol, not in-app pay.

**Never mix.** Qori SaaS and creator course money are separate products on Connect. Do not dump course GPV onto the platform as destination charges.

### 7.1 SaaS billing (Qori's platform account)

- **New** Stripe account for Qori only. Do not reuse an old unverified account. Do not reuse the exit company/trust.
- Payout: **Wise Business AU BSB** (AUD) is fine vs a local bank. AU Stripe still wants a BSB; it will **not** take Wise’s US routing number to skip FX.
- Prices are **USD at base, fixed in the major currencies** (`D-047`). Every sale not in AUD settles through Stripe's 2% conversion, which Qori pays; an Australian's A$55 does not. Wise converts only what Qori spends in USD. USD settlement for Australian accounts exists for a limited number of businesses, to an Australian bank's USD account and not Wise, at 1% per payout (US$10 minimum); do not assume USD-in-USD-out.
- Volume for a cheaper Stripe **SaaS** rate comes from Qori subscriptions, not from pushing lesson money through the platform.

### 7.2 Lesson checkout (Connect) — direct, not destination

Stripe’s own pattern for “educators sell courses on your software” is **direct charges** (Thinkific-shaped). That matches **0% take**.

|                            | Direct (locked)              | Destination (do not use for lessons)                                 |
| -------------------------- | ---------------------------- | -------------------------------------------------------------------- |
| Merchant of record         | Creator                      | Qori                                                                 |
| Where the payment sits     | Creator balance              | Qori balance, then transfer                                          |
| Who pays Stripe processing | Creator (actual fee)         | Qori, then recoup via `application_fee`                              |
| Refunds / disputes         | Creator balance              | **Qori** balance first; reverse transfer                             |
| Dispute rate / monitoring  | That creator                 | **Qori’s** account — including SaaS billing                          |
| Recoup                     | None                         | Estimate intl/AMEX/FX; will not match                                |
| Cross-border               | Settles in creator’s country | Tied to platform; `on_behalf_of` does **not** move dispute liability |

- `application_fee` = **0**. Can add a payments cut later without changing charge type.
- **Standard** connected accounts — the creator's own, connected through Stripe's OAuth sign-in — so creators have a real Stripe dashboard and fight their own disputes. Opening the account is the creator's concern; Qori only runs the sign-in that lets them choose.
- `on_behalf_of` on destination only changes statement / fee country / settlement. Chargebacks still hit Qori.

**Separate charges and transfers:** out for v1 (split carts, many sellers per checkout). One student, one course, one creator.

### 7.3 Stripe “vendor rebate”

Stripe does **not** pay a Tyro-style vendor rebate on day one of an integration.

Closest analogue: **Connect revenue share** (SaaS partner track). Gated, unpublished rate, typically needs ~**US$1M/year** Connect volume, Standard accounts, Checkout/Payment Element, and **Stripe setting the processing price** (direct charges, connected account pays Stripe). Destination + recoup usually **disqualifies** that model.

Until then: money is the SaaS plan. Do not pick destination charges to “look bigger” for a rate negotiation — Connect GPV is visible either way; destination only parks other people’s money and dispute rate on Qori.

---

## 8. Content and storage

Qori provides **basic S3 storage** as the default for images and non-AV lesson content (PDF / PPT / docs), set **per item**. Creators can instead point any given item at their own **BYO storage** (Dropbox now, OneDrive later) — a per-item choice, not workspace-wide. **Video and audio are never stored on Qori's S3**, no exception; those always go to external storage.

| Use                                | Provider (v1)                                                                                                                     |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Image / PDF / PPT — default        | **Qori S3**, per item; small upload cap for free (e.g. 20MB **per file**).                                                        |
| Image / PDF / PPT — BYO (per item) | Dropbox (`get_temporary_link`). OneDrive later. **Google Drive v1 = no** (weak anonymous tickets).                                |
| Paid video — external only         | **Vimeo** — API sets private + embed whitelist on Qori domains. Paid Vimeo often required for domain lock — say so in onboarding. |
| Audio — external only              | Provider **TBD** (see §17).                                                                                                       |
| Trailer / free                     | YouTube OK on public sales page only                                                                                              |

On attach: force private, strip public shares, re-lock on a job if they reopen sharing. Admin UI never “copy public share link.”

Playback: enrolment check → **short-lived ticket** → player hits Qori S3 / Dropbox / Vimeo **directly**. PDFs can still be saved during the ticket window (not DRM).

Progress: opened / marked complete / quiz — not YouTube watch %.

**v1 connectors:** Qori Billing, Connect, email, Qori S3, Dropbox, Vimeo, Zoom, Microsoft Teams. YouTube trailer only.

### 8.1 Live lessons (Zoom / Teams)

Creators run live sessions alongside their uploaded material — same course, mixed format. Qori does not host or relay the live video itself (same no-hosting principle as on-demand content); it **integrates** with the creator's own Zoom and/or Microsoft Teams account.

- Creator connects **Zoom** and/or **Teams** via OAuth — same connect pattern as Dropbox/Vimeo.
- A live lesson is scheduled from Qori (date/time, tied to a course); Qori calls the Zoom/Teams API to create the meeting and stores the join link + meeting ID against that lesson.
- Enrolled students see **Join** on the lesson page — enrolment-gated, same ticket pattern as on-demand playback — not a public Zoom/Teams link.
- Recording, if the creator turns it on, lands in the creator's own Zoom cloud / Teams storage, not Qori's — same BYO principle as the rest of §8. Qori can optionally pull the recording link back in afterward for on-demand replay, handled like any other BYO video item.

---

## 9. Email (Qori provides)

We send; they do not bring Mailgun. **Provider: Postmark** (transactional + broadcast streams), chosen for deliverability and setup simplicity over SES/Resend/Mailgun.

v1 types:

1. Launch / invite to **in-system** contacts → web checkout
2. Receipt + access (magic link to **web** player + optional app links)
3. Stalled (e.g. no lesson in 7 days)
4. New lesson published

From-name / reply-to; DKIM; unsubscribe. Not a full Klaviyo. Start with **templates**, not a blank builder.

**Recipients:** only contacts **in the system**. Admin **creates** them (including **prospects**). No CSV blast. Consent checkbox when creating a prospect. Status: `prospect` | `enrolled` | `customer`.

---

## 10. Auth

- **Email/password** (Fortify) is the primary sign-in method — kept from the starter-kit scaffold rather than removed.
- **Email magic link** is offered as an alternative on the same login screen (a "sign in with a link instead" option below the password form), not a replacement. Revises the earlier "no password as the main path" call.
- **No SMS OTP** (cost / abuse).
- **QR:** logged-in web shows a short-lived nonce; app scans and takes the session. Not yet built.

---

## 11. Optional (not v1 core)

- Meta Pixel + GA4 IDs in admin — their sales/views, off by default, only on **their** public/checkout pages; purchase from Stripe webhook.
- Public `/lessons` catalogue (opt-in).
- BYO AI key later.
- School extras: light white-label, bulk create contacts, certificates.
- Other **business** stores later (Stripe Marketplace, Xero-like) as creator channels.

---

## 12. Certificates / CPD

v1: **completion certificate** (PDF + verify URL, hours, name, date) and a **hours log**. Market as certificate / CPD-ready log.

Do **not** claim regulator-accredited CPD (NSW licence hours, KYC, RTO) until a real path exists.

---

## 13. Languages

Ship **English + Simplified Chinese**. i18n wired so two more locales are translation files. Extra two languages later.

---

## 14. Data hygiene (no video on our disk)

Expire **tickets and junk**, not courses students already paid for.

| Record                                | Policy (default)                                                    |
| ------------------------------------- | ------------------------------------------------------------------- |
| Magic link / QR nonce                 | 5–15 minutes                                                        |
| Playback ticket                       | 1–4 hours                                                           |
| Sessions                              | 90 days idle; max 2 concurrent                                      |
| Email events                          | 30 days free / 90 days paid; keep aggregates                        |
| Prospects never enrolled              | 90 days archive → 12 months delete PII                              |
| Free account, 0 students              | 12 months no login → hibernate; 24 months anonymize if still 0 paid |
| Paid enrolments                       | Keep while creator exists + legal minimum                           |
| Invoices                              | ~7 years; separate from profile PII                                 |
| Disconnected Dropbox/Vimeo/Zoom/Teams | Drop OAuth tokens immediately                                       |

**Caps on free:** 1 course, contact cap (e.g. 20–50), 10 EDM/day, no public list. Unique `(workspace, email)` on contacts. Soft-delete → hard-delete after 30 days except billing.

**Hibernate:** workspace remains, login works, no EDM / listing / tickets until they return. Students who paid still access.

---

## 15. Roles (v1)

|                                         | Owner | Admin (invited, counts toward 20) |
| --------------------------------------- | ----- | --------------------------------- |
| Courses / lessons                       | Yes   | Yes                               |
| Students / prospects                    | Yes   | Yes                               |
| EDM                                     | Yes   | Yes                               |
| Connect, Qori invoice, delete workspace | Yes   | No                                |

---

## 16. V1 in / out

**In:** webapp; forever-free 1 course; Start/Pro invoices on Qori Stripe from a **USD** base, fixed prices in major currencies (`D-047`); thin School if delta is real; Connect **direct** one-off checkout; magic link + QR; EDM to in-system contacts; 10 EDM/day if unpaid; no public list if unpaid; Qori S3 + Dropbox + Vimeo tickets; Zoom/Teams live lessons; completion certificates; en + zh-Hans; 20 admin cap on paid; 2 sessions.

**Out:** student memberships, CSV blasts, Drive / YouTube as paywall, IAP, EDM designer on mobile, accredited CPD, 4 languages, 5 currencies, SMS OTP, selling seats, video/audio hosting/proxy, Skool-style feed as acquisition, destination charges / fee recoup on lessons, Tyro-style Stripe rebate as a v1 revenue line.

---

## 17. Still confirm before build

1. Unpaid/free: **can they take student payment** on the one free course? (Recommend yes.)
2. 3-month rule: **creator friction only**; students keep access.
3. Domain + trademark for **Qori**.
4. Free course: **1 lesson** vs **1 course with a lesson cap**.
5. Skip **Start** SKU and only ship Free / Pro / School if fewer prices are better.
6. Accountant: new sole-trader ABN vs new Pty Ltd before first **live** SaaS charge (see §18). GST on AU SaaS customers if seller is AU.
7. Audio-only lesson content: no external provider chosen yet (Vimeo covers video; audio still open) — left open per §8.

---

## 18. Entity, expenses, sale hygiene

Do **not** run Qori through the exit wrapper:

- **GNW PTY LTD** (ACN 619 052 023) as trustee
- **WNLU Trust** — ABN 97 293 195 453 (**cancelled** 9 May 2023; discretionary **investment** trust, not a trading ABN)

That box is for the company being left. Putting Cursor, domains, or Stripe on it mixes a new product into someone else’s story.

**Build phase (no real customers):** personal card + a **dedicated** Wise/bank (not groceries, not the old company). Spreadsheet: date, vendor, amount, app tag, receipt. New **personal ABN** if Claude/Cursor ask (GST-off). Do **not** use the cancelled trust ABN. Incorporating later does **not** reclaim those 10%s except a narrow ATO pre-establishment path (company + GST-registered within **six months**, full reimbursement). Treat early GST as gone, or never pay it by using a live ABN.

**First live money:** the Stripe account, terms, and invoices must be the **new** seller (you + new ABN, or a new Pty Ltd). Do not turn SaaS live on a personal Stripe you plan to abandon a month later — subscription migration is the painful part. Cards and AI subs are easy to reimburse.

**When to split a Pty Ltd:** not when you pick a brand name. One company can trade as Qori (ASIC business name). Split **Qori Pty Ltd** when there is recurring revenue you would not want sued with a sibling app, outside equity, or a real buyer. Hive-out = assign IP, novate Stripe/customers, move domains.

**Sale unit (IT you already know; money the same idea):**

| Per product (when it is real)                           | Can stay shared for a while |
| ------------------------------------------------------- | --------------------------- |
| Stripe account (SaaS + that product’s Connect platform) | Your Wise as **treasury**   |
| Cloud project + billing                                 | Accountant, laptop          |
| Domain + sending domain                                 |                             |
| Store listings                                          |                             |
| Books tagged to that app                                |                             |

Not strictly “one Wise per app.” Buyer re-points payout. They will not buy a Stripe that also has another app’s subscriptions.

---

## 19. Webapp folder

This repo/folder is the **webapp**. Native apps are separate later and share the same API.

Suggested later (not created yet): app code, API, auth, billing, Connect, EDM, ticket vending.

---

## 20. Tech stack (v1)

> **Moved on 14 September 2026 (T-082)** to
> [`architecture/stack.md`](architecture/stack.md), rewritten in the code's
> names. This section described the queue as `sync` everywhere; it is
> `deferred` outside tests, and the new file says so.

---

## 21. Tenancy and data model (v1)

> **Moved on 14 September 2026 (T-082)** to
> [`architecture/tenancy.md`](architecture/tenancy.md), rewritten in the names
> the code has used since 9 September 2026 — Group, Series, Episode, Access,
> Peer, Collaborator — with the mapping in
> [`planning/decisions.md`](planning/decisions.md). This section still said
> Lessons were embedded in their Course; Episodes are rows in their own table.

---

## 22. Sessions and app tokens

> **Moved on 14 September 2026 (T-082)** to
> [`architecture/sessions.md`](architecture/sessions.md), which separates what
> runs today (the Fortify cookie session, two guards) from what is designed and
> not built (app tokens, the `user_sessions` registry).

---

## 23. Errors and user-facing copy

> **Moved on 14 September 2026 (T-082)** to
> [`architecture/errors.md`](architecture/errors.md). The `ErrorCode` case this
> section called `workspace_paused` is `group_paused`.

---

## 24. Platform admin console

> **Moved on 14 September 2026 (T-082)** to
> [`architecture/admin-console.md`](architecture/admin-console.md). The
> console is built; the "buildable now" table this section carried is
> history, and the pages as they exist are listed there.
