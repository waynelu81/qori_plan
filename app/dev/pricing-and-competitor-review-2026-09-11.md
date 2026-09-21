# Qori pricing and competitor review

Reviewed: **11 September 2026**. Status: **research and proposals for discussion**, not an approved price change or implementation brief.

[Product plan](../project-plan.md#51-competitors-and-pricing-review) · [Product and pricing research](product-and-pricing.md) · [Current release plan](../../PLAN.md)

## Assessment

Qori has a credible position at **US$39–49/month for Start** for creators who already keep teaching material in familiar tools and want an organised way to share it with their audience. **Start with existing files, without moving them** is the primary benefit. Unlimited Series and Peers on paid plans, optional payment and no Qori percentage of sales support that offer. Google Drive, OneDrive, Dropbox and YouTube should be named in the pitch when their workflows are supported.

The **US$99 Pro proposition needs more evidence**. Its current configured differences are primarily custom vocabulary, five times the campaign allowance and a larger per-file upload limit. That is a narrower upgrade than the older research suggests. The catalogue, custom sending domains, custom templates and native apps are deferred; they cannot justify a present-day price. Email needs a usable customer-facing workflow before it becomes a saleable benefit. A later September 11 owner decision defers collaborators; the configured 20-person cap is not a beta selling point or launch prerequisite.

Keep **School available by enquiry**, following the recorded owner decision. The older public $499 sketch is superseded. A $499 offer would invite comparison with mature platforms providing broader business tools, governance and service; Qori has not yet established that value.

## Owner clarification: existing files are the starting point

The primary audience already shares course documents through **Google Drive,
OneDrive or Dropbox**, and may already use **YouTube** for videos. Qori adds a
clear learning path, participant access, progress, communication and optional
payment around the material. Creators keep using the tools they know and the
original files stay with their provider. The owner has seen this workflow across
multiple creator Series they attended; it is a concrete target segment, not a
claim that every creator works this way.

For these customers, bundled competitor hosting need not be a benefit they value.
Existing storage subscriptions should not be charged again in the comparison,
and a sufficient free plan adds no new subscription expense. Google provides up
to **15 GB** shared across Drive, Gmail and Photos; Microsoft provides **5 GB**
of free cloud storage shared across OneDrive and other account usage. That can
support a document-based starting offer, depending on the files and remaining
allowance. The pitch should emphasise familiar tools and continuity, rather than
promise that every customer will have enough free storage forever.
[Google storage](https://support.google.com/drive/answer/9312312?hl=en),
[Microsoft storage](https://support.microsoft.com/en-us/onedrive/microsoft-storage-faqs).

**Target website copy, once the named workflows work:**

> **Start sharing with the files you already have.**
>
> Connect Google Drive, OneDrive or Dropbox. Add your YouTube videos. Turn your
> existing material into a Series your audience can follow, without moving your
> files.

Suggested call to action: **Create your first Series**. Provider names belong
beside the action as recognisable choices, rather than behind the term “BYO
storage.” Connections remain skippable during setup, following the existing
onboarding decision; prompt for the relevant provider when material needs it.

This is product positioning, not a claim that the connectors are already built.
Google Drive, OneDrive and YouTube are absent from the current
[Episode providers](../../app/Enums/EpisodeProvider.php) and
[connection providers](../../app/Enums/ConnectionProvider.php).
Use “connect” for an actual account connection, and “use your existing links”
for a link-based flow. “Without moving your files” covers source assets; course
structure and learner history may still need setup. Qori access does not make
an independently shareable source link private: unlisted YouTube links can be
reshared. That describes the access model, not a reason to recreate video
hosting or exclude the intended audience.
[YouTube visibility](https://support.google.com/youtube/answer/157177?hl=en-CA&ref_topic=9257440).

The immediate product priority implied by this position is proving a creator
can use existing material and share a useful Series quickly. Provider delivery
work still follows the current beta/task process; this discussion changes no
implementation or release dates.

## 1. What the plans actually say

There are three separate sources, and they should not be blended:

- The original [product specification](../project-plan.md#5-pricing-subscription-cheap-entry) sketches Start at $39–49, Pro at $99 and School at $499.
- The [decision record](decisions.md) makes School an offer on request and sets custom vocabulary at Pro and above. The [root plan](../../PLAN.md) takes precedence on product intent and release readiness.
- [DesignReviewSeeder.php](../../database/seeders/DesignReviewSeeder.php) contains **$19 Start / $49 Pro design fixtures with fake Stripe price IDs**. These are not evidence of approved commercial or live prices. Actual prices are staff-managed `SubscriptionPrice` data; this review did not inspect production billing data.

Current entitlements in [config/qori.php](../../config/qori.php):

| Allowance / capability           | Free              | Start             | Pro               | School                                         |
| -------------------------------- | ----------------- | ----------------- | ----------------- | ---------------------------------------------- |
| Series                           | 1                 | Unlimited         | Unlimited         | Unlimited                                      |
| Episodes per Series              | No configured cap | No configured cap | No configured cap | No configured cap                              |
| Peer records                     | 50                | Unlimited         | Unlimited         | Unlimited                                      |
| Collaborators, including owner   | 1                 | 20                | 20                | 20                                             |
| Campaign recipients/month        | 300, also 10/day  | 5,000             | 25,000            | Unbounded in config; intended to be negotiated |
| Custom vocabulary                | No                | No                | Yes               | Yes                                            |
| Peer payments enabled            | Yes               | Yes               | Yes               | Yes                                            |
| Qori file upload limit, per file | 20 MB             | 200 MB            | 500 MB            | 500 MB                                         |

The Free payment flag still carries a “confirm before launch” comment. Paid fulfilment bypasses plan caps after payment, while checkout checks eligibility before charging. Free is therefore **not an unlimited-audience offer**: its 50-Peer limit matters even though access records are separate from collaborator seats. Sources: [CheckoutService](../../app/Services/CheckoutService.php), [AccessService](../../app/Services/AccessService.php).

The preserved proposal for **100 MB total storage per Series** differs from current per-file enforcement. Resolve that deliberately before publishing storage allowances. Likewise, `public_listing=true` on paid plans is not proof of an available catalogue: the current root plan explicitly defers it.

Subscriptions belong to a **Group**, not a person. Someone running two separately billed Groups needs two subscriptions under the current model. Make that clear beside the price.

## 2. Competitors

Prices below are USD, checked against official sources on the review date. Annual figures are monthly equivalents, usually requiring a full year upfront. Taxes, payment processing and optional services are excluded unless explicitly included. The list is a practical shortlist, not an exhaustive market directory.

### Course and creator platforms

| Competitor    | Monthly subscription                    | Annual option                                                 | Sales fee and commercial relevance                                                                                                                                                                                                                                                                                                                               |
| ------------- | --------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thinkific** | Basic $54; Start $109; Grow $219        | $475 / $978 / $1,968 per year, about $40 / $82 / $164 monthly | No additional third-party gateway fee with Thinkific Payments; external gateway charges vary. Mature course delivery, hosting and assessments. [USD price update](https://support.thinkific.com/hc/en-us/articles/41582716364567-Thinkific-s-2026-Plan-Pricing-Update-What-It-Means-for-You), [features and payment caveats](https://www.thinkific.com/pricing/) |
| **Teachable** | Starter $39; Builder $89; Growth $189   | $29 / $69 / $139 monthly equivalents                          | Starter adds 7.5%; Builder/Growth advertise 0% with qualifying gateways; processing and usage charges remain. [Pricing](https://www.teachable.com/pricing)                                                                                                                                                                                                       |
| **Podia**     | Mover $49; Shaker $99; Earthquaker $179 | $42 / $84 / $150; $504 / $1,008 / $1,800 annually             | Mover adds 5%; higher plans 0%, plus processing. Broad bundle of website, courses, community and email. [Annual pricing](https://www.podia.com/pricing), [Podia's own monthly prices](https://www.podia.com/podia-vs-mighty-networks)                                                                                                                            |
| **Payhip**    | Free $0; Plus $29; Pro $99              | No annual rate established in this review                     | 5% / 2% / 0%, plus processing. All tiers include unlimited products and the same feature set. A significant budget competitor. [Pricing](https://payhip.com/pricing)                                                                                                                                                                                             |

**Thinkific is the course-delivery benchmark.** Its current table includes unlimited courses, 10,000 current students, hosted video, and 1/2/6 site administrators on Basic/Start/Grow. Video bandwidth is 100/200/400 GB monthly. Private/hidden courses and certificates begin at Start. Qori's potential advantage is inexpensive private delivery and collaboration; unlimited courses alone is not distinctive. [Thinkific plan comparison](https://www.thinkific.com/pricing/)

**Teachable needs a specific qualification.** Its September 3 usage policy charges **$0.50/month for each countable student above 100**. Countable students include manual/imported access and $0 checkouts, even where a student also has a paid enrolment. The policy applies immediately to new schools; existing schools migrate at their first renewal on or after April 30, 2027 unless they opt in earlier. A new school with 1,000 countable learners would incur **$450/month extra**. Its pricing page lists 5/10/50 products, while the new policy says unlimited: treat product limits as unresolved between official sources. This is especially relevant to Qori's invitation-led audience. [Usage policy](https://www.teachable.com/legal/usage-fees)

**Podia is a price benchmark for Pro at $99.** It bundles video and a broader business surface, whose relevance depends on whether the buyer wants to replace their existing tools. Current limits are 50/150/unlimited products, 500/1,000/unlimited videos, and 0/1/unlimited assistant accounts. Included email subscribers are 100/500/1,000, with paid expansion. Qori's sending-based allowance could appeal to the chosen audience once usable; subscriber limits and monthly send limits measure different things. Qori collaborators are deferred. [Podia limits](https://help.podia.com/en/articles/15350975-understanding-podia-plan-limits)

**Payhip prevents a simplistic “others force expensive upgrades” story.** It supports certificates, drip lessons, subscriptions and payment plans, plus custom domains. Creators can bring video hosting or pay the advertised $5/month video-hosting add-on. Qori needs to win on the private teaching experience and administration, not merely on owning files or using Stripe. [Payhip courses](https://payhip.com/features/sell-courses)

### Community and broader business platforms

| Competitor          | Relevant subscription                                                                                                        | Fees                                                                                                                                     | Why it belongs in the comparison                                                                                                                                                                                                                       |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Skool**           | Hobby $9/month; Pro $99/month; annual billing advertises two months free                                                     | Hobby 10% + $0.30; Pro usually 2.9% + $0.30, with a higher rate for large transactions. These include payment processing.                | Courses, community, video and live calls together; particularly strong price pressure when a group generates little platform revenue. [Pricing](https://www.skool.com/pricing), [payment details](https://help.skool.com/article/86-subscriptions-faq) |
| **Circle**          | Professional advertised $89/month with annual billing; Business $199/month advertised; Plus quoted                           | 2% / 1% / 0.5%, plus payment processing                                                                                                  | Mature discussions, courses, live events and memberships. [Pricing](https://circle.so/pricing), [annual entry-price confirmation](https://circle.so/blog/membership-site)                                                                              |
| **Mighty Networks** | Launch $95 monthly or about $79 with annual billing; Scale/Growth advertised annual equivalents $179/$354; Mighty Pro quoted | Launch 2%; Scale 1%; Growth/Pro 0.5%, with processing separate                                                                           | Community engagement, courses, native video and mobile delivery. [Launch billing](https://docs.mightynetworks.com/for-hosts/meet-mighty/whats-included-in-the-mighty-networks-courses-plan), [plan comparison](https://www.mightynetworks.com/pricing) |
| **Kajabi**          | Basic $179; Growth $249; Pro $499 monthly. Annual equivalents $143/$199/$399                                                 | No revenue share using Kajabi Payments; external-provider surcharge 2%/1%/0.5%, excluding PayPal and Kajabi Payments; processing remains | Website, funnels, email, products and automation for an entire creator business. [Pricing and fee table](https://www.kajabi.com/pricing)                                                                                                               |

Circle's entry tier has unlimited members, three admins and 200 GB storage. The page quotes Email Hub at **+$99/month for 10,000 contacts**, not necessarily as a universal starting fee. Qori's included campaigns would be useful to people who need straightforward updates; they are not equivalent to Circle's marketing automation. A separate month-to-month Circle subscription price was not independently established in this review, so the annual headline is not used as a monthly-contract quote. [Circle comparison](https://circle.so/pricing)

Mighty's Launch includes three hosts, ten moderators and shared iOS/Android apps. Qori is not currently a substitute for a business built around member discussions and recurring community subscriptions. The deliberate absence of a social feed can help a focused teaching experience, but it is a product choice, not overall feature superiority. [Mighty Launch](https://docs.mightynetworks.com/for-hosts/meet-mighty/whats-included-in-the-mighty-networks-courses-plan)

Kajabi's Basic includes five products, 2,500 contacts and two admins; higher tiers expand these alongside business tools. It remains a useful subscription-price benchmark. Buyers looking for that complete replacement stack have a different goal from Qori's primary audience, which wants to keep familiar tools and add a structured sharing experience. [Kajabi pricing](https://www.kajabi.com/pricing)

**The adoption alternative is continuing to share links manually.** Google Drive, OneDrive, Dropbox and YouTube are complementary services. Qori must improve what happens around their files: the learning sequence, audience access, progress and follow-up. The owner's experience identifies this workflow as the starting audience. Paying for that improvement is the customer hypothesis to validate.

## 3. Feature position: strengths and gaps

| Customer need                                | Qori's position                                                                            | Pricing implication                                                                          |
| -------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| Share structured knowledge with known people | Series, Episodes, invitations/access, progress and certificates exist                      | This should be the core paid promise after beta verification                                 |
| Grow the audience without paying per learner | Paid plans have no configured Peer cap                                                     | Strong for client education and free-access programmes; distinguish Free's 50-Peer allowance |
| Work with a small delivery team              | 20 collaborators configured across paid plans                                              | Deferred by owner decision; not a beta offer or release prerequisite                         |
| Receive payments                             | One-off Series checkout through connected Stripe accounts; no application fee              | Useful pricing clarity; no guarantee of zero Stripe fees or unrestricted payouts             |
| Keep existing files and videos               | Provider-hosted media is the design; named Drive/OneDrive/YouTube workflows still needed   | Central benefit for the chosen audience: familiar tools, original files stay where they are  |
| Keep people informed                         | Campaign service, consent, suppression and allowances exist                                | Creator campaign routes/UI are absent; not yet a completed email product                     |
| Express a professional identity              | Custom vocabulary is implemented for Pro/School                                            | Distinctive but willingness to pay $60/month extra is unproven                               |
| Run memberships                              | Current access belongs to a Series; learner recurring billing is outside the current offer | A Group is not proof of an all-Series membership product                                     |
| Run live sessions                            | Episode form accepts Zoom/Teams references and scheduling                                  | Do not claim full OAuth meeting creation, recording synchronisation or hosted video calls    |
| Use mobile                                   | Responsive web is the current scope                                                        | Native/shared/branded apps from competitors are a present capability Qori has deferred       |
| Build a whole marketing business             | Qori deliberately has a narrower scope                                                     | Compete for delivery-focused buyers, not feature-for-feature with all-in-one suites          |

Local evidence: [root plan](../../PLAN.md), [sharing routes](../../routes/share.php), [reachability findings](reachability.md), [GroupService](../../app/Services/GroupService.php), [CampaignService](../../app/Services/CampaignService.php), [Episode form](../../resources/js/pages/share/series/Show.vue), [vocabulary task](tasks/T-004-vocabulary-settings-form.md). This was a source/document review, not a new end-to-end production test. Some historical flow documents are stale; current routes/config and the root plan take precedence.

## 4. Direct pricing comparison for the chosen audience

Compare **Qori's subscription with competitor subscriptions on the same billing
basis**, with platform fees separately visible. The intended customer continues
using existing Google Drive, OneDrive, Dropbox or YouTube services, through a
sufficient free allowance or an existing subscription. **No new hosting purchase
is assumed or added to Qori's column.**

The table below adds sales fees to show their effect at different revenue levels.
It assumes monthly billing and product counts within the named plans, and
excludes processing, taxes, email expansions and other add-ons on both sides.
Processing fees still need a separate explanation because rates and fee bundles
differ between providers.

| Monthly sales | Qori Start at proposed $39 | Podia cheapest Mover/Shaker fee combination | Payhip cheapest fee combination |
| ------------- | -------------------------- | ------------------------------------------- | ------------------------------- |
| $0            | $39                        | $49                                         | $0                              |
| $1,000        | $39                        | $99                                         | $49                             |
| $5,000        | $39                        | $99                                         | $99                             |

Calculations use [Podia's monthly prices](https://www.podia.com/podia-vs-mighty-networks) and [Payhip's fees](https://payhip.com/pricing). They compare financial charges for a constrained use case, not equivalent feature sets. Payhip video hosting, if chosen, is additional.

At $1,000 sales, proposed Qori Start is **$10/month below Payhip Plus** on these
charges. At $5,000 sales, it is **$60/month below Podia Shaker**. Use the
competitor's economical eligible plan rather than inflating savings by keeping
them on an expensive percentage-fee tier.

Never subtract Skool's whole 2.9% from Qori's 0%: one includes processing and the other excludes it. Skool Hobby at $9 also remains a serious alternative for free communities. [Skool payment fees](https://help.skool.com/article/86-subscriptions-faq)

If a particular customer needs to purchase additional provider capacity or
different media access controls, explain that in their individual fit assessment.
It is not a standard surcharge in this audience's Qori price comparison. A
customer seeking one vendor to replace their whole tool stack has a different
purchasing goal from the creator this pitch addresses.

## 5. Recommended plan structure

These are proposals. No application settings, billing rows or Stripe prices were changed.

| Plan       | Suggested price / timing                                        | Offer                                                                                                                                       |
| ---------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Free**   | $0, permanent                                                   | One usable Series, 50 Peers, owner only, complete basic access/progress experience; current limited campaigns once usable                   |
| **Start**  | **$39/month** at a completed beta launch                        | Owner-run Group; unlimited Series/Peers; 5,000 campaign recipients/month once sending works; basic certificates; 0% Qori platform fee       |
| **Pro**    | **$99/month target**, conditional on demonstrated upgrade value | Start plus 25,000 campaign recipients and custom vocabulary; stronger professional controls needed to support broad promotion at this price |
| **School** | **Quote only**                                                  | Defined requirements, usage and service terms agreed individually; no public $499 promise                                                   |

**Start:** $39 is an entry-price hypothesis within the original range, not a finding that the market has validated it. Test $49 with later prospects once independent onboarding and retention are working. Do not adopt the $19 design fixture as the default without understanding support costs. The creator runs the Group as its owner; collaborator invitations remain deferred and the internal cap is not a sales claim.

**Free:** keep enough Episodes to complete a real small programme. A one-Episode limit would weaken the demonstration of structured learning. Let a creator experience success before asking them to upgrade for another Series or more Peers. If Free payments are confirmed, clearly show the Peer cap before checkout. Do not remove existing learner access because a creator's subscription lapses; the existing downgrade policy protects that obligation, subject to the creator maintaining external content.

**Pro:** custom vocabulary can be valuable, particularly for a named programme, but it is not yet evidence of a $60/month upgrade. The best future supporting features are branding across the learner experience, practical progress reports, and configurable follow-up/reminders. Custom sending domains may help later. These are post-beta validation candidates, not instructions to expand the current release. A public catalogue should not be the reason someone buys Pro. If users do not value the current upgrade, launch Free/Start first and defer broad Pro promotion rather than advertise deferred features.

**School:** define what the quote buys. Potential service value includes a scoped migration, onboarding assistance and an agreed support response. Do not imply enterprise features such as SSO, detailed roles, compliance reporting or branded apps before they exist. School's `null` email allowance currently means unlimited in code; a negotiated contract needs a real operational allowance, not an unbounded promise by accident.

**Annual billing:** after retention and support costs are understood, $390/year for Start and $990/year for an adequately packaged Pro would provide two months free. These are optional proposals, not existing offers. Avoid permanent lifetime discounts; state any founding-customer price protection period explicitly.

## 6. Economics and pricing guardrails

**Email allowances are sensible; capacity is not a substitute for a finished workflow.** Count recipient deliveries, not campaigns: one email to 500 people consumes 500 sends. Keep necessary access/receipt messages outside marketing allowances. Retain visible limits and the existing hard-stop policy rather than surprise overage billing.

| Monthly marketing recipients | SES à la carte base sending | SES Essentials base sending | Postmark Platform marginal overage equivalent |
| ---------------------------- | --------------------------- | --------------------------- | --------------------------------------------- |
| 5,000                        | $0.50                       | $0.80                       | $6.00                                         |
| 25,000                       | $2.50                       | $4.00                       | $30.00                                        |

These are marginal/base transport calculations, **not total per-customer costs**. Postmark Platform currently starts at $18 for a pooled 10,000 messages, then $1.20/1,000 extra. SES retains $0.10/1,000 à la carte, while new/inactive account-region combinations start on Essentials at $0.16/1,000 from July 21, 2026. Attachments/data, optional services, operations and support add cost. Sources: [Postmark pricing](https://postmarkapp.com/pricing/), [SES pricing](https://aws.amazon.com/ses/pricing/). This qualifies the older assumption that every new SES account simply starts at $0.10/1,000.

**Treat Qori document storage as supporting convenience.** Resolve the existing
100 MB per-Series proposal versus current per-file enforcement so the limits
are accurate. For this chosen audience, validate the familiar-provider workflow
first; expanding Qori storage is not the primary answer to onboarding or pricing.
Provider-hosted video remains the settled architecture.

The unresolved business inputs are support time per Group, activation, retention, average and high-end sending, infrastructure allocation, acquisition cost and free-user cost. A low email bill is not proof of a profitable subscription. Track net subscription revenue less payment/billing costs, mail, infrastructure and support before selecting aggressive discounts.

## 7. Claims to use, claims to correct

Suggested proposition:

> Start sharing with the files you already have. Connect Google Drive, OneDrive
> or Dropbox, add your YouTube videos, and organise a Series your audience can
> follow without moving your files.

This is target copy for supported workflows. Supporting pricing language:
**“Keep using the tools you know. Pay Qori for organising, sharing and following
your audience's progress.”** Keep the 0% Qori platform fee, paid-plan learner
allowances and email limits clear, with payment-processing charges separately
explained. Do not advertise the deferred collaborator allowance.

Correct these older arguments before reusing them publicly:

- **“0% is unique or permanent by architecture.”** Other platforms offer 0%; Qori's absent application fee is a current implementation and commercial policy. Direct charges can support application fees. Do not claim that changing Qori's policy is technically impossible.
- **“Qori cannot have payout holds or payment lock-in.”** Qori does not hold a platform wallet, but Stripe controls connected-account processing and payouts. Existing independent Stripe-account connection and migration/portability should not be promised without validation.
- **“Your bill never grows with success.”** Audience seats and sales percentages do not raise the Qori charge on paid plans, but extra Groups, email-driven upgrades and external hosting can increase the total cost.
- **“Private Groups are a Pro feature.”** Group is the tenancy unit on every tier. Bundled group-wide access or recurring memberships are separate, unbuilt propositions.
- **“Email, 20 team members, every integration and mobile apps are included now.”** Differentiate configured entitlements, reachable workflows and deferred capabilities.

## 8. Decisions to take from discussion to a launch offer

1. Set one commercial Start price, distinct from design fixtures; $39 is this review's recommended initial hypothesis.
2. Confirm the Free payment policy and publish the 50-Peer allowance accurately.
3. Demonstrate campaign sending without developer help before selling its allowance. Keep the owner-deferred collaborator feature out of the beta offer.
4. Validate whether real prospects will choose Pro for vocabulary and email capacity; otherwise keep its $99 target for a stronger package after beta.
5. Validate the named familiar-provider workflows and the promise that source files stay in place. Resolve supporting document limits and School email allowances; no assumed hosting purchase belongs in the target audience's price comparison.
6. After the existing beta gates pass, use the five representative creators already required by the root plan to measure time to first shared Series, invitation-to-start conversion, support time and willingness to pay. Do not contact prospects or change billing as part of this research task.

The offer should earn its price through a dependable private teaching experience. More roadmap items on a comparison table do not establish that value.
