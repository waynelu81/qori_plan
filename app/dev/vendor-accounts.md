# Vendor accounts and developer access

> What to open, sign up for and pay for before the storage integrations can be built. Written 17 September 2026 from the vendors' own pages; every price and limit carries the date it was checked.

[Current plan](../../PLAN.md) | [Planning index](README.md) | [Storage stream](streams/storage.md)

Almost all of this is free, and most of it can be started today. None of the six
vendors charges Qori for developer access: the Google Cloud project that serves
Google Drive and YouTube, the Microsoft app registration, and the Dropbox, Zoom
and Vimeo apps all cost nothing to create and nothing to run at Qori's volumes.
Money is needed only to test the paid tiers that creators will arrive on: one
cancellable month of Zoom Workplace Pro at US$16.99, because a free Zoom account
cannot host a meeting that people register for; one month of Vimeo Starter at
US$20, because a free Vimeo account cannot make a video unlisted; and one
Microsoft 365 Business Basic seat at US$7.00 a month, because every OneDrive
tier is in the beta release (`D-018`), work and school included (all three
checked 17 September 2026). What
costs time is approval. Zoom will not let any creator outside Qori's own Zoom
account connect until its Marketplace review passes, and it publishes no total
turnaround. Microsoft will not let a work or school creator connect until Qori is
a verified publisher, which sits behind a business check Microsoft publishes as
three to five business days. Dropbox freezes an unapproved app two weeks after it
links 50 accounts. Google caps a YouTube connection at 100 people behind a
warning screen unless its read-only permission turns out not to be classed as
sensitive, and Google Drive, which has no review at all, must still be switched
out of testing before real use or every connection dies after seven days. Vimeo
and YouTube also carry a term about charging that binds Qori rather than the
creator. You have decided that both hold Episodes in paid Series as well as free
ones (`D-019`), because a paid Series sells the creator's time and knowledge;
those two terms have their own section near the end.

| Vendor                         | What the creator needs                                                                                                                                                                                                                | What Qori needs                                                                                                                                                                                                      | What it costs Qori                                                                                                                                                                           | What gates it                                                                                                                                                                                                                                         |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Google Drive                   | Any Google account with Drive, free or Google Workspace. The legacy free G Suite edition works, but nobody can obtain one any more.                                                                                                   | A Google Cloud project with the Drive API and Picker API switched on, an OAuth client, an API key for the picker, and the project number.                                                                            | Nothing. Drive API use is free at Qori's volumes (checked 17 September 2026).                                                                                                                | No permission review, because Qori's Drive permission is non-sensitive. The app must be published, which is a self-serve button, or every connection expires after seven days. Brand verification is optional and light.                              |
| Microsoft (OneDrive and Teams) | OneDrive: any Microsoft account. Personal tiers need no paperwork; a work or school account needs Qori to be a verified publisher and may need the creator's IT administrator. Teams: any Teams account and a recurring meeting link. | An app registration in Microsoft Entra ID, owned by a work account in a tenant Qori controls; for work and school creators, a Partner Center enrolment and publisher verification as well. Nothing at all for Teams. | Nothing for the app or for verification. One Microsoft 365 Business Basic seat at US$7.00 a month (checked 17 September 2026), to test work and school OneDrive, which is in beta (`D-018`). | No app review. Publisher verification blocks work and school creators until it is done; it is free and takes minutes once Partner Center's business verification clears, which Microsoft publishes as three to five business days. Teams has no gate. |
| Dropbox                        | A Dropbox account. Whether a free account can add a Peer as a viewer is unresolved, and Dropbox's own API specification says it cannot. Every Peer needs free space at least the size of the Series folder.                           | An app in the Dropbox App Console with scoped access, Full Dropbox access and five permissions.                                                                                                                      | Nothing; a free Dropbox account can own the app. A paid tier can be tested on the free trial of Dropbox Professional (checked 17 September 2026).                                            | Nothing for testing. Production approval is needed within two weeks of the app linking 50 accounts; Dropbox says it answers nearly all requests within a few business days, and does not review before 50 unless an early review is argued for.       |
| Zoom                           | A paid Zoom Workplace licence, Pro or above, because a free account cannot host a meeting with registration. Peers need no Zoom account.                                                                                              | A General app on the Zoom App Marketplace, managed by each user, with six permissions.                                                                                                                               | Nothing for the app. One month of Zoom Workplace Pro to test with, US$16.99 billed monthly (checked 17 September 2026).                                                                      | Marketplace review before any creator outside Qori's own Zoom account can connect. Zoom publishes a 72-hour first-response commitment and no total. Development mode needs no review and covers the whole spike.                                      |
| Vimeo                          | Any Vimeo account. A video may be Public on every plan; Unlisted needs a paid plan, Starter or above. Peers need no Vimeo account.                                                                                                    | A Vimeo API app. Qori's own Vimeo account can stay on the free plan.                                                                                                                                                 | Nothing for the app. One month of Vimeo Starter to prove the unlisted link, US$20 billed monthly (checked 17 September 2026).                                                                | Nothing. No review to create the app or to let creators connect.                                                                                                                                                                                      |
| YouTube                        | A Google account with a YouTube channel, free, with each video Public or Unlisted. Peers need no account.                                                                                                                             | The YouTube Data API switched on in a Google Cloud project, an OAuth client and one read-only permission.                                                                                                            | Nothing. No price is published and access is rationed by a free daily allowance (checked 17 September 2026).                                                                                 | Google's OAuth verification if the read-only permission is classed as sensitive; until it passes, at most 100 people behind a warning screen.                                                                                                         |

A few words recur below. **OAuth** is the standard "sign in with this vendor and
press Allow" flow that lets a creator give Qori limited access to their account;
the **OAuth client** is the pair of values (a client ID and a client secret) that
identifies Qori during that flow. A **scope** or **permission** is one specific
thing the creator is asked to allow. A **redirect** or **callback address** is the
page on `useqori.com` the vendor sends the creator back to after they press
Allow; the developer gives you the exact address. A **spike** is the short
experiment each task runs against the real vendor before anything is built.

---

## Google Drive

Tasks `T-093` (the spike), `T-094` (Drive Episodes) and `T-044` (the connect
step).

### What the creator brings

A creator needs nothing but a Google account that has Drive, and pays Google
nothing extra to connect it to Qori. They never create a Cloud project or a
developer account; all of that is Qori's, done once, for everybody.

**A free personal Google account** works with no purchase and no approval. The
creator presses Connect in Qori, signs in, and Google's consent screen asks them
to let Qori see, edit, create and delete only the Drive files they use with Qori.
Google describes this permission, `drive.file`, as covering files the person
opens with the app or shares with it through Google's own file picker or the
app's own picker, so nothing Qori does can reach a file the creator did not
choose. The limit worth stating on the connect screen is storage: a free
account's Drive space is shared with Gmail and Google Photos, so a creator whose
Drive is full cannot add Episodes.

**Google Workspace**, the paid business tiers, behaves identically from Qori's
side: the same sign-in, the same consent screen and the same permission. Two
differences are the creator's rather than Qori's. They get far more storage, and
their Workspace administrator can centrally allow or block third-party apps.
That administrator control is documented by Google: an administrator can mark an
app Trusted, Limited or Blocked by its OAuth client ID, refuse third-party apps
altogether, and restrict a list of high-risk Drive permissions
([Google Workspace admin help](https://knowledge.workspace.google.com/admin/apps/control-which-apps-access-google-workspace-data),
checked 17 September 2026). Google's OAuth documentation also lists an
administrator's policy as one of the reasons a long-lived connection stops
working. So a creator inside a managed organisation may have to ask their
administrator to allow Qori before connecting, and the administrator can cut
the connection off later.

**The legacy free G Suite edition** behaves like Workspace, because it is also a
managed domain. Google's help now states that nobody can sign up for it any
more, so Qori can support a creator who already holds one, but neither you nor
anyone else can obtain one to test with. Treat that tier as supported but
untested, or leave it out of the connect dropdown until a real creator with one
appears.

**What nobody can say yet.** Google's documentation describes `drive.file` as
access to individual files and says nothing about folders. Whether Qori can
share a _folder_ the creator picked with each Peer under that permission, and
whether files the creator adds to the folder later reach the Peer, is exactly
what `T-093` exists to find out; no amount of further reading answers it. Google
documents a limit for a single file — "You can share a single file with up to
600 individual email addresses"
([Google Drive help](https://support.google.com/drive/answer/2494822), checked
19 September 2026) — and none for a folder. That matters when every Peer of a
Series is granted on the same folder. You decided on 19 September 2026 not to
measure it: `T-094` stops a sale at a number held in configuration, 600 to
begin with, which can change without a release.

### What you open

1. **Choose the Google account that will own everything below, before creating
   anything.** It is tied to whichever account you sign in with and cannot be
   handed over cleanly later, so use a Qori account on `useqori.com` rather
   than a personal Gmail address. Sign in to the Google Cloud console, Google's
   control panel for developers, at
   [console.cloud.google.com](https://console.cloud.google.com). The first visit
   asks you to accept Google Cloud's terms and choose a country.
2. **Create the project.** Go to
   [console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate),
   name the project Qori and press Create. Read the YouTube section's "Do this
   first" before deciding whether YouTube will later share this project; there
   is a real decision hiding there.
3. **Write down the project _number_.** With the Qori project selected in the
   bar at the top, open
   [console.cloud.google.com/iam-admin/settings](https://console.cloud.google.com/iam-admin/settings).
   The developer needs the "Project number" for the Google file picker. The
   project ID shown next to it, a word-word-number string, is a different value
   and not the one they need.
4. **Switch on the Google Drive API.** Open the API Library at
   [console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library),
   search for "Google Drive API", open it and press Enable.
5. **Switch on the Google Picker API** in the same library. The picker is the
   file-chooser window a creator sees when choosing what a Series holds. Keep
   the picker, the Drive API and the OAuth client in this one project; it is
   sensible practice, although Google does not state that the picker requires
   it.
6. **Prove to Google that Qori owns `useqori.com`.** Open
   [Google Search Console](https://search.google.com/search-console), signed in
   as the same account, add `useqori.com` as a Domain property, and add the DNS
   text record it shows you in Cloudflare, where the domain's DNS lives. Google
   requires someone who is an owner or editor on the Cloud project to have
   verified the domain before brand verification. Start it now because DNS can
   take a while to be seen, but nothing else in this list has to wait for it.
7. **Fill in the Branding page** at
   [console.cloud.google.com/auth/branding](https://console.cloud.google.com/auth/branding).
   Add `useqori.com` under Authorized domains **first**, because Google states
   that authorised domains must be added before any of the addresses. For an
   external app in production Google then requires a user support email (use a
   monitored address such as `support@useqori.com`, since every creator sees
   it), a developer contact address, and links to the application home page,
   privacy policy and terms of service, all on `useqori.com`. The app name and
   logo are optional on this form; they are needed only if you want Qori's name
   and mark shown on the consent screen, which is what brand verification is
   for. Qori must actually have a live privacy policy and terms at those
   addresses, which is already on the beta gate in `PLAN.md`.
8. **Set the audience** at
   [console.cloud.google.com/auth/audience](https://console.cloud.google.com/auth/audience).
   Choose External. While the status reads Testing, add the Google accounts you
   will test with under Test users; Google allows up to 100.
9. **Declare the permissions** on the Data Access page at
   [console.cloud.google.com/auth/scopes](https://console.cloud.google.com/auth/scopes).
   Press "Add or remove scopes" and add `drive.file`, which Google classifies as
   non-sensitive, plus `openid` and `userinfo.email`, the two basic sign-in
   permissions the Peer side uses. Do **not** add the broad `drive` permission:
   it is restricted, and restricted permissions bring a security assessment
   with them (see "What has to be approved").
10. **Create the OAuth client** on the Clients page at
    [console.cloud.google.com/auth/clients](https://console.cloud.google.com/auth/clients).
    Press Create client and choose Web application, named "Qori web". Under
    Authorised JavaScript origins add `https://useqori.com`, because the picker
    runs in the browser. Under Authorised redirect URIs add the two pages
    Google sends a person back to:
    `https://useqori.com/u/connections/google/finalise`, where a creator
    lands after connecting Drive (`T-044`), and
    `https://useqori.com/u/identities/google/finalise`, where a Peer lands
    after confirming their Google account (`T-092`). Both name Google rather
    than Drive (`D-033`). YouTube's connect lands on the same Google address,
    so it needs no redirect URI of its own; if YouTube ends up in a Cloud
    project of its own (see the YouTube section's "Do this first"), that
    project's client registers this same address. Press Create and copy the
    client ID and client secret straight into Qori's configuration; the secret
    is shown only once. Create a second client the same way for local
    development, with `http://localhost:8001` as its JavaScript origin for
    work on the picker, and three redirect URIs:
    `http://localhost:8001/u/connections/google/finalise`,
    `http://localhost:8001/u/identities/google/finalise`, and
    `https://developers.google.com/oauthplayground`, where the `T-093` spike
    collects its tokens.
11. **Create the picker's API key** on the Credentials page at
    [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials).
    Press Create credentials, then API key, then edit the key. Under application
    restrictions choose Websites and add `https://useqori.com/*` and
    `https://docs.google.com/*`, plus `http://localhost:8001/*` for the
    developer's local copy of Qori and `http://localhost:8000/*` for the
    `T-093` spike's test page. The `docs.google.com` entry is required: the
    picker draws itself inside a window served from `docs.google.com`, and
    without it the picker reports that the key is invalid. Under API restrictions tick the Google
    Picker API, and the Drive API too if the developer wants it; Google marks
    the Drive API as optional there.
12. **Press Publish app** on the Audience page at
    [console.cloud.google.com/auth/audience](https://console.cloud.google.com/auth/audience)
    once the privacy policy and terms are live on `useqori.com`, because
    Google requires links to both for an app in production. For Qori's
    permissions it is self-serve, with no review to wait for. Until then the
    app stays in Testing: list every Google account you test with under Test
    users, and expect each sign-in to stop working after seven days. The
    `T-093` spike can run either way and says which it ran under; the reason
    it matters is under "What has to be approved".

    **Done 20 September 2026**, ahead of this step's own advice: the app is In
    production while `useqori.com/privacy` and `/terms` still 404, so the
    consent screen carries two dead links. Nothing reaches it yet — the
    Integrations section is hidden until `T-094` — and `T-155` closes it.
    Publishing was worth doing first regardless, because the seven-day clock
    was breaking connections and the pages are blocked on a lawyer.

13. **Submit brand verification when you want Qori's name and logo on the
    consent screen.** Once the app is external, published and has a name or
    logo, a Verify branding button appears on the Branding page. When the result
    comes back compliant, press Publish branding within seven days, or the
    result lapses and has to be verified again. This can wait until after the
    spike; `T-093` actually wants a record of what the unverified screen looks
    like.
14. **Hand the developer four values**: the client ID, the client secret, the
    API key and the project number.

### What it costs

Nothing, on every count Qori needs, as at 17 September 2026.

- **The Cloud project, OAuth client, API key, branding and brand verification**:
  free. No fee is published for any of them. Google's setup guides for these
  APIs ask for no billing account; that no credit card is requested when the
  project is created is expected but was not confirmed from an official page,
  because it happens inside a signed-in console.
- **The Google Drive API**: free at Qori's volumes. Google states that all
  standard use of the Drive API comes at no additional cost, within a daily
  ceiling of 400,000,000 quota units per project, 1,000,000 per minute per
  project and 325,000 per minute per user. Sharing a file or reading one costs
  a handful of units. Google has announced that exceeding those limits is
  planned to be charged to a Cloud billing account later in 2026, with at least
  90 days' notice before anything changes; whether a billing account will then
  be required of every project, or only of projects over the ceiling, is not
  yet published.
- **The Google Picker API**: no price is published anywhere in its
  documentation, and its setup guide mentions no cost or billing account.
  Treating it as free, like the Drive API, is an assumption rather than a
  published fact.
- **Brand verification, and any sensitive or restricted permission review**: no
  fee is published for any of them, and Google states that it charges developers
  nothing for a security assessment.

If you want to test the Workspace creator tier yourself, the cost is the
creator's kind of cost rather than Qori's, and it can be avoided:

- **Google Workspace** is listed at A$9.90, A$19.80 and A$30.90 per user per
  month for Business Starter, Standard and Plus, with Enterprise by quotation
  only (checked 17 September 2026). Google's pricing page shows prices in the
  visitor's own currency, and these are the Australian prices it showed. The
  same page advertises an annual-commitment option about 16% cheaper, so it is
  not established which billing term those figures belong to, and its
  introductory discounts changed between visits.
- **The Workspace free trial** lasts 14 days for up to ten users (checked 17
  September 2026). A payment method must be entered at signup but is not
  charged until the trial ends. If the trial ends without billing set up the
  account is suspended, and if it ends without billing set up and the domain
  verified, the account is deleted.
- **A domain for that trial** is free if you use one you already own. Google
  offers to sell one during signup for an additional fee it does not state on
  its help page.
- **The legacy free G Suite edition** cannot be bought at any price.

### What has to be approved

**No permission review.** Google classifies `drive.file` as non-sensitive and
states that an app using only non-sensitive permissions does not have to
complete app verification. There is nothing to submit and nothing to wait for.

**Testing versus production is the gate that actually bites, and it fails
silently.** While the Audience page says Testing, only the accounts on the test
user list can connect, up to 100, and every authorisation expires seven days
after the person consents, including the long-lived token Qori keeps so it never
has to ask the creator again. Qori's design (`D-016`) holds that token
indefinitely, so a project left in Testing breaks every creator's Drive
connection a week after it is made, with nothing in Qori to explain why. Pressing
Publish app removes both the 100-account limit and the seven-day expiry. It
takes effect at once, with no queue, because none of Qori's permissions are
sensitive. This is the one gate here that blocks other people using the app.

**Done 20 September 2026**, on project `910317206529`, and one thing was
learned by measuring it afterwards that neither Google's pages nor the reasoning
above says: **publishing does not rescue a grant that was made while the project
was in Testing.** A refresh against a token consented to that morning, four
hours after Publish app, still answered `refresh_token_expires_in: 590467` —
the original seven-day clock, counting down from the consent rather than
restarting or lifting. The clock is a property of the grant, not of the project
as it stands today, so every connection made before publishing has to be
re-consented to be rid of it. What this does not yet establish is the other
half: that a grant made _after_ publishing comes back with no expiry at all.
Nobody has consented since, because `T-094` has not brought the connect UI
back; the first real connect settles it, and is worth watching for.

**Brand verification** is the only review Qori faces, and it is light. It applies
once the app is external, published and shows a name or logo on the consent
screen. Google publishes a turnaround: the automated check typically takes a few
minutes, and a case that has to go to a person usually takes two to three
business days. It does **not** stop anyone using the app. An unverified app still
works; the consent screen simply shows `useqori.com` instead of Qori's name and
logo, which costs trust rather than function. What it asks for is the Branding
page filled in, `useqori.com` verified in Search Console, a home page that plainly
describes Qori, and a privacy policy on the same domain as the home page.

**The 100-new-user cap on unverified apps does not apply to Qori's Drive
connection.** Google attaches that cap to apps showing its unverified-app warning,
which is triggered by sensitive or restricted permissions, and Qori's Drive
permissions are neither.

**If Qori ever needs the broad `drive` permission, everything changes.** That
permission, which reaches files the creator did not pick, is restricted. An app
holding restricted data on its own servers must pass restricted-permission
verification and an independent security assessment, repeated at least every 12
months. Google publishes an estimate of about six weeks for restricted
verification on its help centre, and says on its developer pages only that the
process can take several weeks. Google charges nothing for the assessment and
offers a free self-scan route for the lower tier of it; only a developer who
chooses to engage one of Google's authorised assessors instead pays them, at a
price agreed with the assessor. Google publishes no figure. Security vendors'
own blogs quote roughly US$1,200 to US$6,000 for that paid route (read 17
September 2026); that is their figure, not Google's, and it prices the optional
route rather than the free one. For comparison, sensitive permissions need a
written justification, a demo video and a privacy policy, and Google publishes
two different turnarounds for that review: three to five business days on its
developer pages and ten business days in its help-centre FAQ.

### Do this first

**Verify `useqori.com` in Search Console and get the privacy policy and terms
pages live on `useqori.com`.** Those are the only items for Google Drive that can
take days rather than minutes, and brand verification cannot be submitted until
both are true. Then **press Publish app**: one click with no waiting. Until
you can, the app stays in Testing, where Google quietly expires every token
after seven days whatever Qori does. The `T-093` spike can still run in
Testing if it finishes its free-account pass inside those seven days, and it
cites Google's documented lifetime for a published app instead of measuring
it. Real creators cannot connect until the app is published.

---

## Microsoft: OneDrive and Teams

Tasks `T-097` (the OneDrive spike), `T-098` (OneDrive Episodes) and `T-101`
(Teams). Two completely different worlds sit inside this vendor, and which of
them Qori supports decides whether any of the slow paperwork is needed at all.

### What the creator brings

**A personal Microsoft account: free OneDrive, Microsoft 365 Basic, Personal,
Family or Premium.** The creator needs nothing but the account. They press
Connect, sign in with Microsoft and press Accept, with no IT administrator, no
approval and no review. Microsoft's rule that blocks unverified apps is written
for people consenting from inside an organisation other than the one that
registered the app, so by every reading it should not touch personal accounts;
no Microsoft page says that in so many words, though, and `T-097` should confirm
it. Storage per tier, checked 17 September 2026: a free Microsoft account gets 5
GB shared across OneDrive, Outlook.com attachments and the Microsoft 365 apps
(email has a separate 15 GB); Basic gets 100 GB; Personal 1 TB; Family and
Premium up to 6 TB, 1 TB per person.

Two standing constraints apply to every personal tier. Microsoft cannot share
the very top level of a personal OneDrive, so the creator must pick a sub-folder
for the Series and never the root. And commercial use is only clearly permitted
on Personal and Family: Microsoft's terms for those two plans say the
non-commercial restriction in its general services agreement does not apply to
them, but that document covers only Personal, Family and a few special editions.
It says nothing about free OneDrive, Basic or Premium, so a creator selling a
Series from one of those sits in an unresolved position.

**A work or school account: Microsoft 365 Business Basic and up.** This is the
world that needs paperwork. The creator's organisation has to permit three
separate things: that a user may consent to a third-party app at all, that
OneDrive sharing with new external guests is allowed, and that this user may
invite guests. And unless Qori is a verified publisher, the creator cannot
connect on their own at all. Microsoft turns a consent request from a recently
registered, unverified app that asks for more than basic sign-in into an
administrator-only request, and the creator sees a message telling them the app
needs permission only an administrator can grant.

Microsoft's own consent policy for new organisations (its "Microsoft managed"
policy, documented on a page updated 28 August 2026) excludes about 32
higher-risk Microsoft Graph permissions, covering mail, calendars, chats, online
meetings, contacts, tasks and broad file and site access, from what users may
approve for themselves. The
permission Qori needs, `Files.ReadWrite`, is not among them; its broader cousin
`Files.ReadWrite.All` is. An organisation can also choose a stricter built-in
policy that allows consent only to verified publishers **and** only for
permissions the administrator has classed as low impact, and Microsoft publishes
no default list saying whether `Files.ReadWrite` counts. So even a verified Qori
may still need an administrator's action in such an organisation; only a real
work tenant will show it. In practice, tell work and school creators to expect
to ask their IT administrator once.

**What each Peer needs.** On the personal tiers, every Peer needs a personal
Microsoft account on the exact email address Qori grants to. On a work or school
tier, each Peer becomes an external guest in the creator's organisation, and can
sign in with a work account, a Google account, a Microsoft account, or a one-time
code Microsoft emails them.

**What nobody can say yet about OneDrive.** Microsoft limits how much a free or
storage-only OneDrive can share each day and publishes no figures. It also
publishes nothing about how soon a Peer can open a folder shared with them when
Qori grants access without Microsoft's own invitation email. That second
unknown is the biggest untested step in the whole OneDrive design, and it is
what `T-097` is for.

**Teams** is unlike everything else in this document: the creator needs no
connection to Qori at all. They paste a recurring meeting's join link and Qori
shows it to Peers with access. Any Teams account can host: the free tier, a
Microsoft 365 Personal or Family subscription, or a work account. Two things are
unproven. The design assumes every occurrence of a recurring Teams meeting uses
the same join link, and that rests on a community answer, not a Microsoft page;
ten minutes with a free Teams account should settle it before `T-101` is written
up. And Microsoft publishes no default for who may skip the lobby on the free
tier, so creators should be told to check that setting rather than assume it; a
work organisation's administrator can also switch off joining without an account
altogether. If Qori ever reads Teams meetings through Microsoft's API instead of
taking a pasted link, note that the meeting permissions are on Microsoft's
administrator-only list.

### What you open

A few Microsoft words first. **Microsoft Entra ID** (formerly Azure Active
Directory) is Microsoft's sign-in and directory service for organisations. A
**tenant** is one organisation's own directory inside it. **Partner Center** is
Microsoft's portal for businesses that build on Microsoft, and the **Microsoft AI
Cloud Partner Program** is the renamed Microsoft Partner Network that you enrol
in there.

1. **Decide which account owns the app registration before creating anything.
   This is the one irreversible choice here.** Qori supports creators on work
   and school OneDrive (`D-018`), so the registration must be created by a
   Microsoft work account, not a personal Outlook.com, Hotmail or Live account:
   Microsoft refuses publisher verification for apps registered by personal
   accounts, and an app cannot be moved to another tenant afterwards. Two more
   traps sit in the documentation. The tenant the app is registered in must be
   the tenant linked to Qori's Partner Center account, or verification fails
   later with an unhelpful error. And Microsoft refuses verification for
   tenants created through its self-service email sign-up, for national
   government clouds and for its consumer-login ("B2C") tenants, so create the
   tenant the way step 2 describes.
2. **Create the work account and tenant for `useqori.com`.** Start the Partner
   Center enrolment at
   [partner.microsoft.com/dashboard/account/v3/enrollment/introduction/partnership](https://partner.microsoft.com/dashboard/account/v3/enrollment/introduction/partnership),
   choose Partner, then Next. At the sign-in step choose "Create work account";
   Microsoft warns on that page against using personal Microsoft, Hotmail or
   Outlook.com accounts or free Azure trial accounts. This creates a tenant and
   an organisation billing account. The Entra ID Free subscription added to it
   costs nothing, but Microsoft takes a credit card to verify your identity and
   states that the card is not charged for it. If you later buy a Microsoft 365
   Business Basic seat, buy it signed in as this work account so it lands in
   this same tenant, not in a new one.
3. **Add `useqori.com` as a verified domain on that tenant.** Sign in to the
   Microsoft Entra admin centre at
   [entra.microsoft.com](https://entra.microsoft.com) with the new work account,
   go to Entra ID, then Domain names, then Add custom domain, enter
   `useqori.com`, and add the DNS text record Microsoft shows you in Cloudflare.
   Make Qori's Partner Center primary contact an address on `useqori.com`,
   because verification compares that address's domain with the app's
   publisher domain, and the publisher domain may not be Microsoft's default
   `onmicrosoft.com` one.
4. **Register the app** at [entra.microsoft.com](https://entra.microsoft.com):
   Entra ID, then App registrations, then New registration. Name it Qori. Under
   supported account types choose the fourth option, shown in the current
   portal as "Any Entra ID Tenant + Personal Microsoft accounts"; it is the only
   one that covers both work OneDrive and the personal tiers. Leave the redirect
   address empty for now, press Register, and record the "Application (client)
   ID" from the Overview page. Microsoft's quickstart lists an Azure account
   with an active subscription, and at least the Application Developer role, as
   prerequisites; the free subscription from step 2 and the account that
   created the tenant are expected to satisfy that.
5. **Add the callback addresses.** In the app, under Manage, choose
   Authentication, then Add a platform, then Web. Enter Qori's two Microsoft
   addresses on `useqori.com`:
   `https://useqori.com/u/connections/microsoft/finalise`, where a creator
   lands after connecting OneDrive (`T-098`), and
   `https://useqori.com/u/identities/microsoft/finalise`, where a Peer lands
   after confirming their Microsoft account (`T-092`). Both name Microsoft
   rather than OneDrive (`D-033`). Add the same two on
   `http://localhost:8001` for local development, and press Configure.
6. **Create the client secret** under Certificates & secrets, then New client
   secret. Microsoft caps its lifetime at 24 months and recommends less than 12.
   The value is shown once and never again, so copy it straight into Qori's
   configuration, and put a reminder in the diary to replace it before it
   expires.
7. **Add three permissions** under API permissions, then Add a permission, then
   Microsoft Graph, then Delegated permissions: `Files.ReadWrite`,
   `offline_access` (which lets Qori keep the connection without asking again)
   and `User.Read`. Press Add permissions. Microsoft's own documentation confirms
   `Files.ReadWrite` is the least powerful permission that allows the sharing
   call Qori depends on, on both personal and work accounts. Do not choose the
   `.All` variants, for the consent reason explained above.
8. **Set the publisher domain** under Branding & properties, then Update
   Publisher Domain, to `useqori.com`; the DNS record from step 3 proves it. On
   the same page fill in Qori's terms of service and privacy statement
   addresses, because they appear on the consent screen every creator reads.
9. **Keep going: steps 10 to 13 are for work and school creators**, who are in
   the beta release (`D-018`). A personal-accounts-only test can stop here and
   come back.
10. **Complete the partner enrolment** you began in step 2. Sign in at
    [partner.microsoft.com/dashboard/home](https://partner.microsoft.com/dashboard/home)
    with the work account, choose the billing account, read and accept the
    Microsoft AI Cloud Partner Program agreement, and press Enroll. Whoever
    enrols must be a global administrator of the tenant and authorised to sign
    agreements for the business.
11. **Clear Partner Center's verification.** Microsoft runs five checks: a
    business email address rather than a free one; a government-issued identity
    document whose name matches the account; current domain documentation for
    `useqori.com` from the registrar, showing the business name, address,
    domain, and purchase and expiry dates; business formation documents, such as
    a certificate of registration, matching the account's name and address
    exactly, without abbreviations; and a discretionary extra check. Upload them
    on the Business Information page under Verification Summary, and follow the
    status under Account settings, Legal info, at
    [partner.microsoft.com/dashboard/account/v3/organization/legalinfo](https://partner.microsoft.com/dashboard/account/v3/organization/legalinfo).
    The enrolment is active only once the status reads Authorized.
12. **Find the Partner One ID** under Account settings, Identifiers, at
    [partner.microsoft.com/dashboard/account/v3/overview](https://partner.microsoft.com/dashboard/account/v3/overview).
    Use the ID whose type is PartnerGlobal; a location ID is rejected.
13. **Mark the app publisher verified.** Turn on multi-factor sign-in (a code
    or app prompt as well as the password) and actually complete it in the
    browser session you use, or the request fails. You need the Application
    Administrator or Cloud Application Administrator role in Entra, and an
    administrator role in Partner Center, which Microsoft's own pages name three
    different ways, so check the list under Partner Center's user management
    rather than relying on one name. Sign in at
    [aka.ms/PublisherVerificationPreview](https://aka.ms/PublisherVerificationPreview)
    or open the app in [entra.microsoft.com](https://entra.microsoft.com), go to
    Branding & properties, scroll to the bottom, choose "Add Partner ID to verify
    publisher", enter the Partner One ID and press "Verify and save". A blue
    verified badge then appears beside Qori's publisher name on the consent
    screen.

For **Teams** there are no steps. Nothing developer-side exists for the shape
Qori is building.

### What it costs

Free, as at 17 September 2026: the Entra app registration, its callback
addresses, secret and permissions, and publisher verification. Microsoft states
that it does not charge developers for publisher verification, that no licence is
required, and that no charges attach to completing its prerequisites. The Entra
ID Free subscription is free, although a card is taken for identity
verification and not charged. No fee is published anywhere for basic enrolment
in the partner programme; Microsoft never says the word "free" about it, so that
one is an inference from the statement about prerequisites.

Paid, in US dollars, all checked 17 September 2026:

- **Microsoft 365 Business Basic**, the cheapest work seat and therefore the
  cheapest real work OneDrive to test against: US$7.00 per user per month,
  raised from US$6.00 on 1 July 2026. Microsoft's licensing page gives one
  monthly figure without saying whether it assumes an annual commitment.
  Microsoft's business list prices conventionally do, with month-to-month
  billing dearer, but the page does not say so; budget a little above US$84 a
  year if you want to be able to cancel monthly. A version without Teams is
  listed at US$5.40.
- **Microsoft 365 Personal**: US$9.99 a month or US$99.99 a year, 1 TB.
- **Microsoft 365 Family**: US$12.99 a month or US$129.99 a year, up to 6 TB.
- **Microsoft 365 Premium**: US$19.99 a month or US$199.99 a year, up to 6 TB.
- **Microsoft 365 Basic** (100 GB): **price not confirmed.** Microsoft's own page
  about Basic confirms the plan exists and gives no figure, Basic no longer
  appears on Microsoft's consumer comparison page, and the OneDrive plans page
  would not load for the research. The figure repeated elsewhere is not
  published by Microsoft and is not quoted here.
- **Teams free**: US$0, with group meetings up to 60 minutes, up to 100
  participants, 5 GB of file storage and no recording. A Microsoft 365 Personal
  or Family subscription raises that to 30 hours, 300 participants and
  recording.

The Microsoft developer programmes, and what they would cost to qualify for, are
under "The cheapest way to run the spikes".

### What has to be approved

**There is no app review.** Unlike Zoom, Microsoft does not review or approve an
app before other people use it: no marketplace submission, no questionnaire and
no listing. Microsoft's app attestation and certification programmes exist but
are optional extras, not prerequisites. Qori can serve personal Microsoft
accounts the day the app registration is created.

**Publisher verification is the gate, and it blocks work and school creators
entirely until it is done.** Microsoft states that since November 2020 users
cannot consent to most newly registered multi-tenant apps that are not publisher
verified. The rule covers apps registered after 8 November 2020 that ask for
more than basic sign-in and profile reading, which `Files.ReadWrite` does, and
applies to people in organisations other than the one that registered the app.
The protection is on by default, but it only changes anything where the
organisation allows users to consent at all; where an administrator has turned
user consent off, verification buys nothing and the creator hits the same wall
for a different reason.

Verification itself is free, and Microsoft says a developer who already meets
the prerequisites can be verified in minutes. The wait that matters is Partner
Center's business verification in front of it, which Microsoft publishes as
taking three to five business days in most cases, with the caveat that some
checks take longer when they need more information. There is no published
service level and no published appeal timeline, so plan for a week and do not
promise a creator a date.

**The organisation's own settings can still refuse**, even after verification:
consent may be off or limited, external sharing may be restricted, the creator
may not be allowed to invite guests, and domain allow or deny lists and guest
expiry policies can cut Peers off later. Qori cannot fix any of these; it can
only detect them and tell the creator what to ask their administrator for.

### Do this first

**Start the Partner Center enrolment now.** Work and school OneDrive is in the
beta release (`D-018`), so the slow paperwork is needed: gather the business
registration documents and the registrar's record for `useqori.com` and begin
immediately. It is the only Microsoft item with a multi-day clock, and publisher
verification cannot begin until it clears. The personal tiers and Teams can be
tested today, for nothing, while it runs.

---

## Dropbox

Tasks `T-095` (the spike) and `T-096` (Dropbox Episodes).

### What the creator brings

Any Dropbox account, including the free one, can connect to Qori. Whether a free
account can do what Qori actually needs is the single most consequential open
question in this document, because it decides which tiers Qori can offer.

**Dropbox Basic, free, 2 GB.** It can connect, and can have Qori turn a folder
into a shared folder. But Dropbox's own published API specification, the formal
description of every call, says the call that adds a Peer as a view-only member
fails on an account that has not been upgraded to a "Pro or Business" plan. It
says the same of changing an existing member from editor to viewer. Dropbox's
help centre points the other way: its page on folder permissions describes "can
view" with no plan restriction and says the article applies to all Dropbox users
unless stated otherwise. Both are current, official Dropbox documents, they
contradict each other, and nothing published reconciles them. Plan on the
specification being right, because it is the more specific statement and the
alternative is finding out from a paying creator. 2 GB is in any case too little
for a course of any size.

Nobody sells a plan called "Pro" today, so which paid plans the specification
means is also open. Prices below were checked 17 September 2026, in Australian
dollars, because Dropbox prices by the visitor's location.

**Dropbox Plus**, A$18.69 a month, 2 TB, one person. The individual paid plan was
called Dropbox Pro before it became Plus, which suggests Plus qualifies, but that
is an inference from Dropbox's naming history, not a statement. Plus does **not**
get Dropbox's shared-link controls (a password, an expiry date, turning off
downloads), so the fallback of handing out a plain view-only link is uncontrolled
on this tier and on Basic.

**Dropbox Professional**, A$30.79 a month, 3 TB, one person, with a free trial.
It is on sale today, has at least as strong a claim on the word "Pro", and does
get the shared-link controls. **Dropbox Essentials** is a separate plan that
Dropbox's help centre still describes (Professional plus e-signature features),
but it appears on none of Dropbox's current purchase pages; some creators may
hold it and new ones apparently cannot buy it.

**Dropbox Standard**, the cheapest team plan, sold from one user at A$27.50 per
user per month. It is unambiguously a business plan in the specification's
language, so the grant will work. Two things come with a team account: a shared
folder counts once against the team's pooled storage rather than against each
colleague, and a team administrator can turn external sharing off, in which case
every grant to an outside Peer fails and Qori can only detect it and say so.

**What the Peer needs, and this is the sharpest edge in the whole storage
design.** Dropbox states that the size of a shared folder counts against the
storage quota of every member, unless everyone is on the same Standard, Advanced
or Enterprise team or the same Family plan. A Peer on a free 2 GB account
therefore cannot join a 5 GB Series folder at all, and a Peer whose account is
nearly full cannot join a folder bigger than what is left. Dropbox's own suggested
workaround is a view-only link, which uses none of the recipient's storage, and
that is exactly the uncontrolled link the grant was meant to replace. Whether a
Peer who has been invited but has not joined can view the folder through its web
preview, which would sidestep the quota, is not documented anywhere; `T-095`
should try it.

**Two structural rules Qori's folder picker must enforce on every tier**: a
shared folder cannot sit inside another shared folder, and cannot contain one.

### What you open

1. **Sign in at [dropbox.com](https://www.dropbox.com) with the account that
   will own the app**: a Qori company address, not a personal one, because the
   app cannot be moved to another account later. A free Basic account is
   enough; Dropbox states that a free account is all that is needed to use its
   APIs.
2. **Open the App Console**, Dropbox's control panel for developers, at
   [dropbox.com/developers/apps](https://www.dropbox.com/developers/apps).
   Bookmark it; you will come back to it.
3. **Press Create app**, which opens a short wizard at
   [dropbox.com/developers/apps/create](https://www.dropbox.com/developers/apps/create).
4. **Choose "Scoped access"** as the API type. It is Dropbox's current model and
   the one that lets Qori ask for individual permissions.
5. **Choose "Full Dropbox", not "App folder".** This cannot be undone: Dropbox
   says changing it means deleting the app and creating a new one. The wrong
   choice makes Qori's whole pattern impossible, because Dropbox refuses to
   share an app folder. Be ready to justify the broader choice at review, since
   Dropbox checks that an app does not ask for more access than it needs.
6. **Name it Qori** and press Create app. Dropbox's branding guide forbids names
   containing "Dropbox", names beginning with "drop", and "DBX", "DB" or "DfB";
   Qori breaches none of them. Once the app has production status the name is
   frozen.
7. **On the Settings tab**, copy the app key and app secret for the developer,
   and add Qori's two addresses on `useqori.com` under the OAuth redirect
   addresses: `https://useqori.com/u/connections/dropbox/finalise`, where a
   creator lands after connecting Dropbox (`T-096`), and
   `https://useqori.com/u/identities/dropbox/finalise`, where a Peer lands after
   confirming their Dropbox account (`T-092`). Add the same two on
   `http://localhost:8001` for local development. Turn off the implicit grant
   option, because Qori talks to Dropbox from its server and does not need it.
   The research could not see the signed-in console, so the exact labels on
   this tab may differ slightly.
8. **On the Permissions tab**, tick exactly five and nothing more:
   `account_info.read`, `files.metadata.read`, `files.content.read`,
   `sharing.read` and `sharing.write`, then press Submit. Keeping the list short
   is itself a review criterion, and adding a permission later forces every
   creator who has already connected to approve Qori again.
9. **On the Branding tab**, fill in the publisher (Qori's legal entity), a
   one-sentence description written for creators, the website
   `https://useqori.com`, and the small and large Qori icons from `../design/brand/`.
   Dropbox says this information is also used in production review.
10. **Tell the developer the connection shape**, from Dropbox's OAuth guide:
    the connect link must ask for offline access, or Dropbox returns no
    long-lived token, and should use the PKCE safeguard. Dropbox's ordinary
    access tokens are short-lived, but it publishes neither their lifetime nor
    whether the long-lived token ever expires, so Qori should read the expiry
    from each response rather than assume one.
11. **Test at once, with no approval.** A new app is in development status and
    links to your own account immediately; the "Enable additional users" control
    on the Settings tab adds more test accounts. The whole spike runs here.
12. **Apply for production** with the "Apply for Production" button on the
    Settings tab, when real creators need to connect. The form asks how the app
    uses the API and for an icon. Dropbox advises being descriptive, because the
    more information you give the faster it may approve the app once it reaches
    50 linked accounts. To be reviewed before then, which Qori will want, argue
    the case in the form's "Request early review" field.

### What it costs

The App Console, the API and production approval cost nothing, as at
17 September 2026. There is no paid Dropbox developer programme and no fee for
API access. Dropbox never says in words that production approval does not need a paid plan,
but no plan requirement appears anywhere in its approval criteria or its
developer terms.

Creator plan prices, all checked 17 September 2026 and all in Australian dollars.
Dropbox's pages served Australian prices and Dropbox publishes no
location-independent price list, so no US dollar figures are given:

- **Basic**: free, 2 GB, one person.
- **Plus**: A$18.69 a month, or A$184.67 a year, 2 TB, one person. No trial.
- **Professional**: A$30.79 a month, or A$306.90 a year, 3 TB, one person. Free
  trial.
- **Family**: A$31.89 a month, or A$323.27 a year, up to six people.
- **Standard**, the cheapest team plan: A$27.50 per user per month, or A$277.20
  per user per year, from one user, team storage from 3 TB. Free trial.
- **Advanced**: A$43.45 per user per month, or A$435.60 per user per year, from
  three users, team storage from 15 TB. Free trial.
- **Enterprise**: by quotation.

Dropbox's help centre confirms free trials of Professional, Standard and Advanced
and says billing details are taken at signup. **Dropbox does not state the
trial's length in any page text.** Thirty days appears only in the pricing page's
browser-tab title; the "30 days" in the page body is about restoring deleted
files, not about trials. Take the billing date from the confirmation email and
set the cancellation reminder from that.

### What has to be approved

**Nothing, to run the spike.** A development app works immediately.

**Production approval, before the app can serve real creators.** A development
app can link at most 500 Dropbox accounts, but the number that matters is 50:
once the app links 50 accounts, you have two weeks to apply for **and receive**
production approval before its ability to link any more is frozen. The freeze is
sticky; Dropbox says the only way out is to apply for and receive production
status, and that unlinking accounts does not lift it. This blocks other people
from connecting.

Dropbox publishes a turnaround, on its developer support page rather than in its
developer guide: it responds to nearly all production requests within a few
business days (checked 17 September 2026). That is a soft statement, not a
service level, and the clock starts only once the app has 50 linked accounts,
because Dropbox also states that a request is not reviewed before then unless an
early review is granted. A refusal is not final: Dropbox gives feedback and you
resubmit.

What the review looks at: Dropbox's branding guidelines and developer terms (it
says an app that breaks them is rejected); that the app asks for no broader
access than its function needs; a clear privacy policy specific to the app,
which should be Qori's own on `useqori.com`; and that the app uses only the
current version of the API. One criterion deserves reading twice before the
application is written. Among the apps it does not allow, Dropbox lists
publicly searchable file-sharing networks built on Dropbox. Qori is not that, as
it is invitation-led with no catalogue, but an app whose job is adding outside
people to a creator's folders will look adjacent to it on a reviewer's screen.
Describe Qori in the application as invitation-only delivery of a creator's own
material to people they personally invited, and say in as many words that there
is no public catalogue and no search.

**Limits Dropbox confirms but does not quantify**, all of which Qori will meet: a
cap on how many shared-folder invitations one account can send in 24 hours, a
cap on how many members one folder can have, and a cap on how many files a
folder being shared can contain. None of the numbers is published.

**The creator's team administrator** can switch off sharing outside the team, as
described above. That is not a review of Qori, but it blocks that creator's
Peers.

### Do this first

**Run the free test, then write the production application early.** The free
test takes minutes and costs nothing: on a free Basic account, share a folder
and try to add a second free account as a view-only member. If Dropbox refuses,
Qori's Dropbox tier starts at a paid plan and the connect screen must say so; if
it succeeds, the specification is out of date and free creators can be offered.
The item with the longest lead time is production approval, which in the normal
course cannot even begin until 50 accounts are linked and then allows only two
weeks. So as soon as the spike has proved the pattern, submit the application
with the early-review field filled in.

Behind that sits a decision the developer needs before `T-092` (a Peer confirming
their vendor account) is specified: **does a Peer who signs in to Dropbox through
Qori count towards the 50?** Dropbox publishes no definition of a linked account
beyond authorising the app, and a Peer signing in authorises it, so assume Peers
count until shown otherwise. If they do, one busy Series could reach 50 on its
own. Watching the Analytics tab in the App Console during the spike will show
it; having Peers type their Dropbox email address instead of signing in would
avoid it.

---

## Zoom

Tasks `T-099` (the spike) and `T-100` (Zoom live Episodes).

### What the creator brings

**A paid Zoom Workplace licence. A free Zoom account cannot do this at all.**
Zoom's API reference for the call that registers each Peer states that the host
must be a licensed user, and its help centre lists a Pro, Business, Education or
Enterprise account and a Zoom Workplace licence as the requirements for a meeting
with registration. A free creator who connects and then fails at the first Peer
is the worst possible outcome, so the connect screen must say this before they
connect.

**Zoom Workplace Pro** is the minimum that works. The ceilings a Pro creator
lives inside, checked 17 September 2026: 100 participants in the room at once,
meetings of up to 30 hours, and a limit that will surprise people, a maximum of
60 occurrences in a recurring meeting with fixed times. Zoom enforces the 60 in
its API, not just in its app, and its usual workaround, a recurring meeting with
no fixed time, is exactly what a meeting with registration may not be. A Series
with weekly sessions therefore reaches Zoom's wall after about 14 months, and
Qori has to say so rather than let a creator discover it. Whether scheduling by
end date instead of by number of occurrences gets past 60 is not documented, and
is worth one call in the spike.

**Zoom Workplace Business** is the same with a bigger room, 300 participants.
Recommend it only to a creator expecting more than 100 Peers live at once. Above
that, Zoom's own material disagrees about Enterprise (500 in one place, 1,000 in
another), and Large Meeting add-ons go to 500 or 1,000.

**The Peer needs nothing.** Zoom states in its help centre that you do not need a
Zoom account to join a meeting as a participant, and its pricing FAQ says the
same. The exception Zoom names is a meeting whose host requires participants to
be signed in, so Qori must create the meeting with that "authenticated users
only" setting off and read it back afterwards, because a creator who switches it
on in Zoom's web portal silently locks out every Peer. What is not documented is
whether the personal join link Zoom returns for each registered Peer takes them
straight into the meeting or to a registration page first; the spike has to
look.

**The meeting Qori creates**, for the developer, from Zoom's API reference and
rate-limit page (checked 17 September 2026): a recurring meeting with fixed times
(Zoom's type 8); registration once for all occurrences (registration type 1,
which Zoom describes as register once and attend any occurrence); and automatic
approval (approval type 0). Manual approval is not an option, because Zoom then
returns no join link at all. Zoom allows three registration requests a day, in
UTC, for the same person in the same meeting, ten status requests a day for the
same registrant, and 100 meeting create or update requests a day per user. Two
facts the design depends on are **not documented** and are the reason `T-099`
exists. First, whether a Peer registered once is carried into occurrences the
creator adds later; if not, every new session costs another registration per
Peer against that three-a-day limit. Second, whether Zoom's "maximum attendee
capacity" refusal fires at the room size (100 on Pro) or at the 4,999-registrant
limit Zoom states elsewhere; if it is the room size, a Series on Zoom needs a
Peer ceiling checked before checkout.

**One upkeep fact that costs engineering time rather than money.** A Zoom access
token lasts an hour, and the long-lived token behind it expires after 90 days and
changes every time it is used. A creator's Zoom connection therefore dies after
90 days unless Qori refreshes it well inside that, or asks the creator to
reconnect.

### What you open

1. **Sign in at [zoom.us/signin](https://zoom.us/signin) with a Qori company
   account** on a `useqori.com` address, not a personal one. The app's listing,
   terms and privacy links must sit on a domain Qori owns, and Zoom checks that
   the company name matches.
2. **Give that account developer permission**, if it is not the account owner,
   who already has it. In the Zoom web portal at
   [zoom.us/role](https://zoom.us/role), go to User Management, Roles, choose
   the role, Edit, Role Settings, Advanced features, and tick both View and Edit
   for "Zoom for developers". The Marketplace shows its Developer link only to
   accounts with this.
3. **Open the Zoom App Marketplace** at
   [marketplace.zoom.us](https://marketplace.zoom.us) and sign in. Click
   Developer in the lower-left navigation, then Develop, then Build an app, and
   select **General app**, then Create. Zoom still offers other types on that
   screen, such as Server-to-Server OAuth and Meeting SDK; neither is the right
   one for Qori.
4. **On the Basic Information page**, name the app and, where it asks how the
   app is managed, choose **User-managed**. Zoom defines that as individual users
   adding and managing the app, with access only to their own authorised data,
   which is exactly Qori's model. The alternative asks each creator's account
   administrator to approve, which most solo creators cannot do.
5. **Note the two sets of credentials on the same page**, Development and
   Production; the development pair is for building and testing, the production
   pair for once the app is published. Copy the **development** client ID and
   secret for now. Under OAuth Information, set the redirect address to
   `https://useqori.com/u/connections/zoom/finalise`, where a creator lands
   after connecting Zoom (`T-141`), and add `https://useqori.com` to the
   required OAuth allow list. For local testing, add
   `http://127.0.0.1:8001/u/connections/zoom/finalise` to the allow list as
   well, on the numeric address `127.0.0.1` rather than the word `localhost`:
   Zoom does not document whether `localhost` is accepted, and developers on
   Zoom's forum report it being refused.
6. **On the Scopes page**, press Add Scopes, choose the Meeting product, and add
   six permissions, writing a reason for each in its description box:
   `meeting:write:meeting` (create the Series meeting),
   `meeting:read:meeting` (read it back, including its occurrences and its
   sign-in setting), `meeting:write:registrant` (register a Peer),
   `meeting:read:list_registrants` (check who is registered),
   `meeting:delete:registrant` (remove a Peer on a refund or removal), and
   `user:read:user` (identify which Zoom account connected). Settle this list
   now. Zoom treats adding a permission as a request to its security review
   team, which may refuse one it thinks unnecessary, and adding one after
   publication brings a complete security review again.
7. **For the spike, stop here and test.** On the Local Test page press Add App
   Now, then Allow. That installs the app into Qori's own Zoom account on the
   development credentials, with no review, no submission, no fee and no
   waiting; Zoom states that private and beta apps are not reviewed. Every
   question in `T-099` can be answered this way.
8. **When outside creators must be able to connect**, switch from the
   Development tab to the Production tab in the same build flow and fill in the
   App Listing: name, description, images and category. The Links section needs
   four addresses, all on a domain Qori owns (Zoom explicitly forbids hosting
   them on Google Drive or Dropbox): a support page, a documentation page that
   is a Zoom-specific guide to adding, using and removing the app, the terms of
   use, and the privacy policy.
9. **Complete the Technical Design section**, which is what Zoom's security
   review reads: the technology stack (Laravel, Inertia and Vue on Laravel Cloud,
   Neon Postgres, Valkey, R2, with versions where possible), an architecture
   diagram showing every component that touches Zoom, and three attestations:
   that all traffic uses TLS 1.2 or newer, that Zoom's secret token is used to
   check event notifications, and that all Zoom user data, including OAuth
   tokens, is stored encrypted. Qori already encrypts connection tokens, so the
   third can be answered today.
10. **Verify `useqori.com`.** In the production build flow go to Publish your
    app, then App Submission, where each domain you entered appears under Verify
    Domains. Press Verify, choose the DNS text record method and add the record
    in Cloudflare. (The other methods are uploading a file, adding a tag to the
    home page, or asking Zoom support, which Zoom says answers within 48 hours.)
    Verification belongs to the Zoom account, so a later Zoom app on the same
    domain does not need it again.
11. **Submit for review** from App Submission. Set the audience to external Zoom
    users; the other choice limits the app to Qori's own staff. Whether the app
    is listed in the Marketplace or unlisted is set on the App Listing's "EU &
    Discoverability" page and can be changed at any time without another review.
    Put a test plan in the release notes, and give reviewers working Qori logins
    for every role, a creator and a Peer, behind a Series that already has a Zoom
    Episode, because reviewers click through the integration itself. Note Zoom's
    quirk: a first submission must use the _production_ client ID when
    authorising, while later updates use the development one. Choose whether the
    app goes live on approval or when you activate it, agree to the Marketplace
    Developer Agreement, and submit.
12. **After approval**, have the developer swap Qori's stored Zoom client ID and
    secret from the development pair to the production pair.

### What it costs

Free, as at 17 September 2026: a Zoom account on the free Basic tier, creating
the General app, adding permissions, development-mode testing, submitting for
review and publishing, listed or unlisted. No fee appears anywhere in Zoom's
developer documentation or build flow, though Zoom also never says in words that
it is free.

**Also free, and worth knowing: the Marketplace route needs no paid penetration
test.** Zoom requires a penetration test report, secure-development documentation
and code-scanning reports only to approve a private sharing link for an
unreviewed app. Publishing on the Marketplace needs none of them.

Paid, checked 17 September 2026. Zoom's pricing page offered only Australian and
US dollars and labelled its US dollar prices "excluding GST", so the US figures
are the Australian page shown in US dollars, not confirmed US-market prices:

- **Zoom Workplace Pro**: US$16.99 per user per month billed monthly, or US$14.16
  per user per month billed annually (about US$169.92 a year, charged up front).
  In Australian dollars, A$25.99 monthly or A$21.66 a month billed annually,
  both excluding GST. Zoom's pricing FAQ says a plan renews monthly or yearly
  depending on the term chosen and can be cancelled at any time during the term
  to stop the renewal, so one cancellable month is a legitimate way to run the
  spike. No free trial of Pro is offered on the pricing page.
- **Zoom Workplace Business**: US$21.99 a month billed monthly, or US$18.33 a
  month billed annually; A$32.99 or A$27.83, excluding GST.
- **Large Meeting add-on**, which raises a paid plan's room to 500 or more and
  needs a paid plan beneath it: from US$50, or from A$75.99, a month for 500
  participants, billed monthly. Not needed for Qori's beta.
- **Zoom Developer Pack**: prepaid credits for Zoom's more specialised API
  products, with a small free allowance. **Not needed** for anything Qori does;
  listed only so nobody buys it by mistake.

### What has to be approved

**Marketplace review is the gate on every creator outside Qori's own Zoom
account.** Zoom states that public and unlisted apps go through a dedicated
review and private and beta apps do not. It runs in two phases: Zoom's
Marketplace operations team reviews the listing, usability and compliance, then
its security team audits the app and tests the permissions it uses. **Zoom does
not publish a total turnaround.** It commits only to a first response, stating a
72-hour first-response service level and that it typically responds within 36
hours, and it says review time varies with the app's quality, features and
clarity. Developers on Zoom's own forum describe a full publication as commonly
taking more than four weeks, and one 2026 thread reports an app waiting more than
ten weeks with no first response
([Zoom developer forum](https://devforum.zoom.us/t/app-stuck-in-review-10-weeks-withdraw-action-errors-editor-locked/143374),
read 17 September 2026). Those are developers' reports, not Zoom's figures, and
should never be quoted as Zoom's. Plan for at least a month and budget for three.

**Choosing "unlisted" is not a way round the review.** It keeps the app out of
the Marketplace's search results; Zoom states that unlisted apps are still
reviewed, and fail if the full listing details are missing.

**The private-link route is not a way round it either.** Zoom can approve a
private installation link for an unreviewed app, answering within three to four
business days, valid four weeks at a time with two extensions and capped at 100
installations. But it is the route that needs the penetration test, Zoom forbids
presenting the app as a Zoom integration while using it, and Zoom's API terms
restrict the link to the developer's own staff for a limited private beta and
forbid making it available to anyone else. It cannot be used to onboard creators.

**Development mode needs no review and is enough for the whole spike.**

**Other conditions of submission, none of which block the spike**: domain
verification of `useqori.com`; reviewer logins for every role with a working
Zoom-backed Series behind them; and the developer role permission inside Qori's
Zoom account. Whether Zoom's security review will object to Qori holding one
creator's token and using it to register many Peers is not predictable from
anything Zoom publishes; the permissions requested are the minimum for the job.

**One term still needs reading before `T-100` is specified.** Qori will store,
for each Peer, the registrant ID and personal join link Zoom returns. Which clause
of Zoom's terms governs storing those was asked and **not established**. The
clause numbers the research first found do not exist in the current Zoom API
License and Terms of Use (last updated 16 July 2025, checked 17 September 2026),
whose Section 3 runs from the licence grant through limitations, responsibilities
and registration to prohibited uses. The Zoom Marketplace Developer Agreement
(last updated 28 November 2022) does have sections on direct relationships with
end users and on data subject requests, but nobody has yet read them against
Qori's case.

### Do this first

**Buy one month of Zoom Workplace Pro and run the spike in development mode, but
do not submit for review to do it.** Submission buys nothing the spike needs and
starts a clock measured in weeks. The item with the longest lead time is the
Marketplace review itself, and Zoom is in the beta release (`D-018`), so
prepare what the submission needs (the Zoom guide on `useqori.com`, the
architecture diagram and the reviewer logins) and submit at least a month,
ideally two, before the date you want.

---

## Vimeo

Task `T-090` (Vimeo and YouTube Episodes open as unlisted links).

### What the creator brings

**Any Vimeo account, with each video Public or Unlisted.** Vimeo's privacy help
page (updated 7 July 2026, checked 17 September 2026) states that public and
private are available on all plans but **unlisted is available on paid plans
only**. Qori's Vimeo pattern works with either: the Series is the container, and
Qori shows the video's link only to Peers with access. Public means anyone on
Vimeo can also find the video; Unlisted keeps it off the creator's profile and
out of Vimeo search, if the creator prefers that. A creator on the free plan
therefore uses Public videos (`D-018`). Private means only the creator and their
own Vimeo team can watch it, which locks out every Peer, so a Private video is
the one Qori refuses (`D-019`).

**Vimeo Starter** is the cheapest plan with unlisted links, for a creator who
wants them. **Standard** and **Advanced** add player branding, more seats and
live events, none of which Qori's Episode flow needs. **Enterprise**
deserves one warning: an Enterprise administrator can restrict privacy settings
account-wide, and when they disable one, Vimeo offers to move every video that
used it to private. An administrator turning unlisted off would therefore convert
already-shared Episodes to private and break every link Qori has already handed
to Peers, without Qori doing anything.

Two more things the creator should be told. An **unlisted link carries a privacy
hash**, an extra run of characters in the address, which must be kept intact or
the link stops working; the viewer needs no Vimeo account. And Vimeo now runs an
**age check** (help page updated 3 June 2026, checked 17 September 2026): a
signed-out viewer may be asked to sign in and verify their age for content rated
mature in the United Kingdom, the European Union and Brazil, and for unrated
content in the United Kingdom. Verification is run by a third party, Persona,
using a selfie or a government document, or in the UK a credit card as well.
Videos embedded on other sites are not affected, but Qori's design opens
vimeo.com in a new tab rather than embedding, so **the check does apply to
Peers**. Vimeo's own advice is the mitigation Qori should enforce when a video is
picked: rate the content, because proper ratings reduce unnecessary prompts.

### What you open

1. **Sign in at [vimeo.com](https://vimeo.com) with the Qori company account that
   will own the app.** If that account is a team member of another Vimeo
   account, Vimeo requires you to sign in as the primary account holder instead.
   The account can stay on the **free** plan, because creating an app and
   reading a connected creator's videos costs nothing.
2. **Open the developer site's My Apps page** at
   [developer.vimeo.com/apps](https://developer.vimeo.com/apps) and press
   "Create an app".
3. **Fill in the four things on the "Create a New App" form.** The app name,
   Qori. The app description: Vimeo shows this text on the permission prompt
   every creator reads, so write it for them, for example that Qori shows your
   Vimeo videos to the people you choose, reads your video list and links, and
   never uploads, edits or deletes anything. The question asking whether people
   besides you will be able to access the app, answered **Yes**; that is what
   lets other creators connect their own Vimeo accounts, and "No" means only
   your own account ever can. And the checkbox agreeing to Vimeo's Developer
   Addendum and Terms of Service.
4. **Press Create App.** There is no review and no waiting; Vimeo takes you
   straight to the app's information page.
5. **Copy the client ID and client secret** from that page into Qori's server
   configuration. Vimeo's developer terms forbid putting them in code that runs
   in the browser or in a public code repository.
6. **Add Qori's callback address** on the same page, in the settings for OAuth
   redirect addresses: `https://useqori.com/u/connections/vimeo/finalise`,
   where a creator lands after connecting Vimeo (`T-090`, `D-033`). It must be
   an address on `useqori.com`, and the developer must send exactly the same
   address when a creator connects. The field sits behind a signed-in page the
   research could not see, so its exact label is unconfirmed, and Vimeo does
   not document whether a `localhost` address is accepted for development.
7. **For the spike, generate a personal access token** on the same page: choose
   "Generate an access token", pick the option for your own account
   ("Authenticated (you)"), and tick the `private` permission, which Vimeo
   requires. That token lets the developer prove the whole read path against a
   real account before writing the connect flow.
8. **Tell the developer the connection shape**: Vimeo's standard authorisation
   flow, sending the creator to `https://api.vimeo.com/oauth/authorize` and
   asking for the `public` and `private` permissions only. Vimeo describes
   `private` as access to the member's private data and requires it for any
   permission beyond `public`. Qori needs no upload, edit or delete permission.

### What it costs

**Qori's own developer access is free** (checked 17 September 2026). Vimeo states
that its API is available to all plans and users and needs no payment to access,
though some features need a paid account; uploading is the one that matters, and
Qori never uploads. Do not upgrade Qori's own account. A paid plan on it buys
nothing here except faster support replies, which is worth remembering if you
ever write to Vimeo about its terms.

Creator plan prices, in US dollars, from Vimeo's own pricing data, checked 17
September 2026:

- **Free**: US$0, permanent, not a trial. Cannot make a video unlisted.
- **Starter**: US$12 per seat per month billed annually (US$144 a year), or US$20
  a month billed monthly. One user, 2 TB of storage. **The cheapest plan with
  unlisted links.**
- **Standard**: US$25 per seat per month billed annually (US$300 a year), or US$41
  monthly. Five users, 4 TB.
- **Advanced**: US$75 per seat per month billed annually (US$900 a year), or US$125
  monthly. Ten users, 7 TB.
- **Enterprise**: no published price; Vimeo routes to a contact form.

A trial link for Starter exists on Vimeo's site, but it leads straight to signup
without stating any terms, so **neither the length nor the conditions of a Vimeo
trial are published anywhere reachable without signing up.** Budget US$20 for one
month of Starter billed monthly and treat a trial as a bonus. That is the cheaper
way to buy one month despite the higher monthly rate, because annual billing
commits US$144 up front.

**Request limits are free, and they are counted per creator, not for Qori as a
whole.** Vimeo's published allowance per connected creator per minute (checked 17
September 2026) is 25 requests on Free, 125 on Starter, 250 on Standard, 750 on
Advanced and 2,500 on Enterprise, each doubled when Qori asks only for named
fields. Over the limit, that one creator's requests are refused for the rest of
the minute, and Vimeo says it may block an app that exceeds the limit
persistently. Vimeo's table also lists 1,500 for a plan called Studio, which is
not for sale on its pricing page, so leave it out of anything creators see. Qori's
daily re-read of stored videos uses a tiny fraction of even the free allowance.

### What has to be approved

**Nothing, to create the app or to let other creators connect.** The "people
besides you" question is a radio button, not an application, and there is no
queue and no questionnaire.

**One review exists and Qori never needs it.** Vimeo reviews apps that _upload_
video, and only when the developer's own account is unpaid; it publishes a
turnaround of up to five business days for that. Qori never uploads, because no
video passes through Qori, so this never applies. It is recorded only so nobody
requests it by mistake and puts the app in a queue.

**Contractual conditions to meet before launch**, from Vimeo's Developer Addendum
(last updated 9 March 2026, checked 17 September 2026). Section 4.6 requires a
publicly posted privacy policy for any app that is not internal-only; use
`useqori.com/privacy`. Section 4.8 requires a simple, easily found way for a
creator to disconnect their Vimeo account at any time, so Qori needs a visible
Disconnect control. Neither is a review, but launching without them is a breach.

**Vimeo reserves the right to add a gate later.** Section 1 says it may require
further registration, verification or approval before granting access _or while
maintaining it_, so the reservation applies after launch too. Nothing is
required today for a read-only app.

**Nothing gates a paid Series either.** Vimeo holds Episodes in every Series,
priced or free (`D-019`). The charging clause, section 3.5, and your reading of
it are in "Two terms that bind Qori, not the creator" below.

**One thing the developer must know before `T-090` is built**, because it
conflicts with how Qori holds every other vendor's connection. Vimeo's
authentication guide documents no refresh token at all for the flow Qori uses;
the word does not appear on the page. It describes the token as staying active
while Vimeo sees it being used, and says tokens that appear inactive are deleted
automatically. Meanwhile section 5.4 of the Developer Addendum forbids keeping,
refreshing or extending tokens beyond their authorised duration. So for Vimeo,
"Qori stores the refresh token" (`D-016`) may not describe anything real, and the
scheduled daily re-read may be what keeps each connection alive. How long a
token may sit idle before Vimeo deletes it is not published; that is a spike, not
a fact.

### Do this first

**Create the app and prove the read path with a personal access token.** Both
are free and take an afternoon, and nothing about Vimeo has a long clock. Then
buy one month of Starter only to prove the Unlisted link end to end, and have the
spike watch how long an idle token survives. Writing to Vimeo about section 3.5
is optional; how to do it is under "Two terms that bind Qori, not the creator".

---

## YouTube

Task `T-090` (Vimeo and YouTube Episodes open as unlisted links). YouTube's API
lives inside Google Cloud, in the same console as Google Drive.

### What the creator brings

A Google account with a YouTube channel, free, and videos set to Public or
Unlisted. There is no paid YouTube tier to buy and nothing to apply for. YouTube
holds Episodes in every Series, priced or free (`D-019`).

**A personal channel or a Brand Account channel** (a channel several people can
manage). The creator signs in with Google, allows the permission and picks videos
from their own channel. Google's help (checked 17 September 2026) states that
anyone with the link can watch an unlisted video, that it does not appear in
YouTube's search results or on the channel page, and that the people it is shared
with do not need a Google account. A Public video works the same way for Qori;
Unlisted keeps it off the channel page and out of search, if the creator prefers
that. Only a Private video is refused, because a Peer cannot open it (`D-019`).
How Google chooses between a personal channel and a Brand Account channel when
one Google account owns both was not researched; a creator who connects and sees
the wrong channel's videos will report it as Qori's fault, so the picker should
show which channel is connected.

Three things to tell the creator when they pick a video. Do not **age-restrict**
these videos: an age-restricted video cannot be watched signed out, and on most
other sites the viewer is sent to YouTube to sign in and prove they are over 18.
YouTube **cannot replace a video**: trimming it, or changing its title,
description, category or privacy, keeps the same address, but uploading a new
version creates a new address and the creator has to pick it again in Qori. And
for a creator keeping videos Unlisted, a playlist used for the Series must be
unlisted too, because an unlisted video added to a _public_ playlist becomes
findable.

**A channel on a Google Workspace account** works identically at no extra charge,
but that creator's administrator can block Qori's app or turn YouTube off, and a
Peer watching while signed in to their own work or school account may be limited
by their own administrator.

**Channel memberships should stay out of the connect dropdown.** YouTube's API
lets a channel read its own member list and nothing more, so Qori cannot add a
Peer as a member. More generally, YouTube has no call that gives a named person
private access to a video, which is why the Qori Series is the container and the
video is Public or Unlisted (`D-016`, `D-019`).

### What you open

1. **Sign in to the Google Cloud console at
   [console.cloud.google.com](https://console.cloud.google.com) with a Qori
   company Google account**, not a personal Gmail address. YouTube's developer
   policies say the email address of the account used to sign in to the console
   is YouTube's main way of contacting the developer, so a policy warning or an
   audit request would otherwise land in someone's personal inbox.
2. **Choose the project** with the project picker in the bar at the top of the
   console: either the Qori project created for Google Drive, or a new one from
   [console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate).
   Read "Do this first" below before choosing; this decision has a cost attached.
3. **Switch on the YouTube Data API** at
   [console.cloud.google.com/apis/library/youtube.googleapis.com](https://console.cloud.google.com/apis/library/youtube.googleapis.com),
   checking the project name at the top, and press Enable. Confirm "YouTube Data
   API v3" is listed at
   [console.cloud.google.com/apis/enabled](https://console.cloud.google.com/apis/enabled).
   No billing account is asked for.
4. **Fill in the Branding page** at
   [console.cloud.google.com/auth/branding](https://console.cloud.google.com/auth/branding),
   exactly as in step 7 of the Google Drive section: `useqori.com` as an
   authorised domain first, then the support email, developer contact, home
   page, privacy policy and terms on `useqori.com`. If YouTube shares the Drive
   project, this is already done, because branding belongs to the project.
5. **Set the audience** at
   [console.cloud.google.com/auth/audience](https://console.cloud.google.com/auth/audience):
   External, and while the status reads Testing, list your own test accounts
   under Test users, up to 100.
6. **Add one permission only**, on the Data Access page at
   [console.cloud.google.com/auth/scopes](https://console.cloud.google.com/auth/scopes):
   press "Add or remove scopes" and tick `youtube.readonly`, which Google labels
   "View your YouTube account". **Look at the category the console shows beside
   it** (non-sensitive, sensitive or restricted) and tell the developer; that
   label decides whether the verification described below is needed at all. Do
   not add the broader `youtube` permission ("Manage your YouTube account").
   Qori would need it only to change a video's privacy, and YouTube's policies
   forbid an app changing a video's visibility unless the creator expressly told
   it to. Leaving it off also keeps any verification small.
7. **Create the OAuth client**, unless YouTube shares the Drive project. If it
   does, this is already done: the "Qori web" client from step 10 of the
   Google Drive section serves YouTube too, and a YouTube connection comes back
   to the same Google address as a Drive one, so there is nothing to add
   (`D-033`). In a project of its own, open the Clients page at
   [console.cloud.google.com/auth/clients](https://console.cloud.google.com/auth/clients),
   press Create client, choose Web application, and add that same address,
   `https://useqori.com/u/connections/google/finalise`, under Authorised
   redirect URIs, with `http://localhost:8001/u/connections/google/finalise`
   for local development. Copy the client ID and secret into Qori's
   configuration. Either way, the developer must ask for offline access when a
   creator connects, so Google issues the long-lived token.
8. **Verify `useqori.com` in
   [Google Search Console](https://search.google.com/search-console)**, signed in
   as the same account, if it was not already done for Google Drive. Google's
   verification requires it.
9. **Publish the app, and submit it for verification if the permission is
   sensitive.** Press Publish app on the Audience page, then follow the "Prepare
   for verification" prompt; the status is shown at
   [console.cloud.google.com/auth/verification](https://console.cloud.google.com/auth/verification).
   Google asks for the verified domain, the privacy policy and home page on
   `useqori.com`, a support email, a written reason for `youtube.readonly`
   explaining exactly what Qori does with it, and a demo video of the whole
   permission flow, which Google requires to be uploaded to YouTube as unlisted.
10. **Only if Qori ever outgrows the free daily allowance**: YouTube's Audit and
    Quota Extension Form at
    [support.google.com/youtube/contact/yt_api_form](https://support.google.com/youtube/contact/yt_api_form).
    It is not needed to launch; what it asks for is under "What has to be
    approved".

### What it costs

Nothing, as at 17 September 2026. Google publishes no price for the YouTube Data
API; access is rationed by a daily allowance rather than billed. The default
allowance per project is 10,000 units a day for ordinary calls, plus 100 searches
and 100 uploads. The calls Qori makes, listing a channel's uploads and reading a
video, cost one unit each, and every request costs at least one even if it fails,
so the allowance covers roughly 10,000 Episode checks a day across all creators.
The call to avoid is YouTube's search, capped at 100 a day for the whole project;
the developer should list a creator's uploads from their uploads playlist instead.

No billing account, credit card or trial credit is needed. To be precise about
the evidence, **no Google page says the YouTube Data API is free in so many
words.** The conclusion rests on the absence of any published price, on access
being rationed by allowance rather than billed, and on Google's rule that billing
must be switched on only for the APIs that charge.

Google's OAuth verification is free, and YouTube's audit form is free. The
independent security assessment that does cost money applies only to Google's
restricted permissions. Google's restricted families are Gmail, Google Drive,
Google Fit, Google Chat, Data Portability, Photos Ambient and Google Health, and
no YouTube Data API permission is among them. (Google's separate Data Portability
API does have restricted YouTube entries, but Qori does not use that API.)

### What has to be approved

**Google's OAuth verification is the gate on other people using Qori's YouTube
connection, and it is Google's gate, not YouTube's.** It applies if
`youtube.readonly` is classed as sensitive. A published app requesting a sensitive
permission without verification shows an "unverified app" warning before the
consent screen and is capped at 100 users. Google words the cap two ways, as 100
new users after the warning first appears and as 100 users in total, so treat 100
as the ceiling either way. People other than the developer _can_ therefore use an
unverified Qori, up to that cap, past a warning. **Google publishes two
turnarounds for this review, and they disagree**: its developer page on sensitive
permissions says the process typically takes three to five business days, while
its help page on unverified apps warns that verification may take several months
depending on how sensitive the data is. Both are official and current, and no
Google page reconciles them. Treat three to five business days as the best case
and do not plan the beta around it.

**The 30-second check that could remove this gate.** Google publishes no readable
list of which permissions count as sensitive, but the console shows the category
beside each one (step 6). If `youtube.readonly` is non-sensitive, Google states
that verification is not required, the 100-user cap does not apply and no warning
appears. The research found no reliable evidence either way, so assume it is
sensitive until somebody has looked.

**YouTube's own compliance audit is not required and Qori should not need it.**
YouTube states that the audit is how a project asks for more than the default
allowance, and Qori lives far inside it. It is worth knowing what the form asks,
because YouTube also runs periodic audits of its own choosing: legal entity
details and address, contacts, the monetisation model, the app's privacy policy
and terms addresses, working demo login details so a reviewer can walk through
the product, and for each Cloud project (one to ten of them) screenshots of the
privacy policy, home page, terms and permission flow, the calls used and a reason
for every unit of allowance requested. **YouTube publishes no turnaround for it**,
committing only to contact you as soon as possible, and no reliable outside
estimate exists either. YouTube has a separate appeals form for developers who
fail an audit, but does not say what failing means for the project.

**The seven-day trap applies exactly as for Google Drive.** While the status reads
Testing, a connection expires seven days after consent, long-lived token
included, and the exception Google makes for basic profile permissions does not
cover `youtube.readonly`. That is expected behaviour, not a Qori bug, but it is why
the app must be published before a real creator connects, and publishing is what
brings Google's verification onto the critical path.

**Nothing gates the Peer.** Anyone with the link can watch a Public or Unlisted
video without an account, so there is no vendor sign-in, no per-Peer grant and
nothing to accept.

**Nothing gates a paid Series either.** YouTube holds Episodes in every Series,
priced or free (`D-019`); the policy clauses about selling, and your reading of
them, are in "Two terms that bind Qori, not the creator" below.

**One design rule that is not about accounts but binds the developer.** YouTube's
developer policies (section III.E.4.c) allow data taken from the API, such as
titles, thumbnails and durations, to be kept for no longer than 30 calendar days
before it is deleted or refreshed; only the authorisation tokens themselves may be
kept as long as necessary. Qori's stored Episode details and its daily re-read
must be designed around that.

Also unconfirmed: whether a creator who connects both Google Drive and YouTube
from one Cloud project sees one consent experience or two.

### Do this first

**Decide which permission Google Drive will use before YouTube shares its Cloud
project, then submit Google's verification as soon as the project is settled,
since YouTube Episodes are in the beta release (`D-018`).** Verification and
security assessment apply to a whole project, not to one permission. The narrow
Drive permission in the Google Drive section is not restricted, but the broad
`drive` permission is. If `T-093` concludes that sharing a folder needs the
broad permission, putting Drive and YouTube in one project turns YouTube's free,
days-long verification into restricted verification (several weeks, after brand
verification) plus an independent security assessment repeated every 12 months,
which is the one genuinely expensive item anywhere in this document, acquired by
accident. `T-093` answers it; until it does, keep YouTube in the same project
only if Drive stays on `drive.file`, or give YouTube a project of its own.

---

## Published rate limits, read 20 September 2026

Read from each vendor's own page during the storage review of that date, and
**documented limits, not observations from Qori's own credentials** — project
dashboards, lower backend limits and the real response headers still have to
be checked by each provider's spike. Every one of them bears on the fan-out
in `T-091`, which is one list plus one create per Peer per item.

| Vendor                  | What the page says                                                                                                                                                                                                                                       | What it means for Qori                                                                                                                                                                                                                                                                              |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Google Drive            | Limits are quota units now: 1,000,000 a minute per project and 325,000 a minute per user per project, with backend 429s and exponential backoff with jitter. The sharing limit carries no published numeric rate.                                        | Do not reuse an older requests-per-minute figure, and do not treat one Peer's row as its own bucket. The measured workload is a latency problem first; an undisclosed sharing throttle can still dominate. The quota cost of the permission methods, and this project's allocation, are unverified. |
| Dropbox                 | No exact number published. Limits apply per authorisation for user-linked apps, 429s carry `Retry-After`, and a throttled call still counts.                                                                                                             | Stop work for the whole authorisation, not the one failing Peer. `T-095` measures the invitation restriction separately from ordinary throttling.                                                                                                                                                   |
| OneDrive and SharePoint | Graph sends file limits to SharePoint's guidance: 3,000 requests per five minutes per user, tenant budgets that depend on licensing, and five resource units for every permission operation, reads included. External-sharing email limits are separate. | The "300 sharing calls per five minutes" figure this repository once carried is not on that page. A permission list avoids a mutation but still spends quota. Consumer OneDrive is not SharePoint; do not apply the figures unqualified.                                                            |
| Zoom                    | Plan and account-wide, shared by every installed app. Pro is 30 light and 20 medium requests a second; heavy calls share 30,000 a day. Registration allows three requests per registrant per meeting per UTC day, ten for status changes.                | `T-100`'s look-up-before-create is justified by the registration limit. Back off at account level and respect the daily UTC reset. The expensive scan is every registrant page and status, not one lookup.                                                                                          |
| YouTube                 | 10,000 units a day for the ordinary endpoints; `videos.list` costs one.                                                                                                                                                                                  | One check per stored Episode can spend the project's day with no Peer traffic at all. Deduplicate video ids, batch where supported, and keep reads off Open.                                                                                                                                        |
| Vimeo                   | Per-user, per-minute limits, 429s and a pause of up to a minute; no general numeric allowance for the video API on that page.                                                                                                                            | Read the account's own limits and headers, and do not substitute the separately listed AI-endpoint figure. Cool down other checks on the same authorisation.                                                                                                                                        |
| Teams                   | No Microsoft API call in the pasted-link design.                                                                                                                                                                                                         | No fan-out quota to solve; meeting policy is the risk instead.                                                                                                                                                                                                                                      |

---

## The cheapest way to run the spikes

**Nearly all of this can be proved for nothing. The spend that cannot be avoided
is about US$37: one month of Zoom Workplace Pro at US$16.99 and one month of Vimeo
Starter at US$20, both billed monthly and cancellable, both checked 17 September 2026.** Everything else is optional, or covered by a free trial if it is cancelled
in time.

Free today, with no application and no waiting:

- **Google Drive.** The Cloud project, both APIs, the OAuth client, the API key
  and the branding. Ordinary free Google accounts stand in as the creator and
  the Peers, at least three distinct accounts in all, which `T-093` requires.
  Leave the app in Testing until the privacy policy and terms are live on
  `useqori.com`, with every account listed as a test user, and finish the
  free-tier pass within seven days of the first consent (step 12).
- **Microsoft OneDrive, personal tiers.** The app registration costs nothing (a
  card is taken for identity and not charged). A free Outlook.com account is the
  creator and a second one the Peer, and the free 5 GB is plenty for a test
  Series folder.
- **Microsoft Teams, entirely.** There is nothing to set up. Create a free Teams
  account, schedule one recurring meeting, and check whether its occurrences
  share one join link.
- **Dropbox, the decisive question.** A free account owns the app and answers the
  free-plan question with two calls against a second free account playing the
  Peer. Fill a third free account close to its 2 GB and try to add it to a
  larger shared folder; that is the storage refusal Qori will meet in real use.
- **Vimeo, the read path.** A free Vimeo account owns the app, and a personal
  access token from the app's page proves listing and reading videos before any
  connect flow is written.
- **YouTube, everything.** The API, the project and the OAuth client; the whole
  spike uses a rounding error of the free daily allowance.

Paid, or free on a trial, all checked 17 September 2026:

- **Zoom Workplace Pro, one month, US$16.99** (A$25.99 excluding GST),
  cancellable before it renews. Unavoidable, because a free Zoom account cannot
  host a meeting with registration.
- **Vimeo Starter, one month, US$20** billed monthly, only to prove the unlisted
  link end to end, since a free account cannot set a video unlisted. A trial may
  cover it, but Vimeo publishes no trial terms, so budget the US$20.
- **Dropbox, A$0 if done in order.** A paid tier is needed only if the free
  account is refused, and Dropbox Professional has a free trial, so whether a
  paid individual plan satisfies Dropbox's rule can be answered for nothing.
  Standard's free trial answers the business-plan case the same way. Paying
  A$18.69 for a month of Plus is then a commercial question (can Qori's entry
  tier be the cheaper plan?) rather than the technical one. Dropbox does not
  publish the trial length, so set the cancellation reminder from the billing
  date in the confirmation email.
- **Microsoft 365 Business Basic, US$7.00 a month**, because work and school
  OneDrive is in the beta release (`D-018`). One seat does three jobs: it is a work account in the
  tenant the app is registered in, it lets `useqori.com` be attached to that
  tenant, and it gives a real work OneDrive to test against. The Peer needs no
  second seat, because they join as an external guest. Buy it signed in as the
  work account from the Microsoft section's step 2, so it lands in the same
  tenant.
- **Google Workspace, A$0 on the 14-day trial**, only to test that creator tier. A
  payment method is required at signup, so set a reminder for day 12. **Do not run
  this trial on `useqori.com`.** Switching on Gmail for a Workspace domain points
  that domain's mail records at Google, and `useqori.com`'s mail records point at
  Postmark for Qori's transactional email (`T-015`). Use a throwaway domain;
  whether Workspace accepts a subdomain of `useqori.com` for a trial was not
  confirmed, so have the developer check the signup flow before any DNS on
  `useqori.com` is touched.

**Free developer programmes: what is genuinely still open.** Google Drive,
YouTube, Dropbox and Vimeo have no developer programme to join at all; the free
access _is_ the programme, open to anyone, with nothing to be admitted to and
nothing closing. Zoom is the same, as building is free and only publishing is
reviewed. Microsoft is the exception, and the door most people picture is shut.
The **Microsoft 365 Developer Program** still exists and still offers a free
sandbox organisation with 25 Microsoft 365 E5 licences (its FAQ is dated 4
September 2026, checked 17 September 2026), but there is no longer any way for an
individual developer to sign up. It has four routes in: an eligible Visual Studio
Professional or Enterprise subscription; the ISV Success programme or an eligible
partner-programme tier; a Premier or Unified Support contract with Microsoft; and
none at all in government clouds. Setting up the sandbox also now requires linking
a Microsoft Customer Agreement billing account with an active Azure subscription,
though the sandbox itself stays free. The sandbox renews only on genuine
development activity every 60 to 90 days, Microsoft warns it may require the
sandbox to be recreated every 90 days, and it allows one per phone number. A solo
owner with none of the four will be told they do not qualify.

The two routes Qori could take both cost more than the seat. **Visual Studio
Professional** as a standard subscription is US$99.99 per user per month paid
annually, about US$1,199.88 for the first year (checked 17 September 2026).
**ISV Success** is free for its first 12 months and then US$1,550 a year, and
includes an E5 developer subscription, but it demands a B2B app built on or
integrated with Microsoft's cloud, development started within three months and
finished within 12, and a commitment to publish Qori on Microsoft's Marketplace.
Microsoft also announced on 29 July 2026 that ISV Success is being folded into a
new offering, Frontier Accelerate for Marketplace, from September 2026, and has
published no terms for it, so none of ISV Success's current terms should be
planned around. One Business Basic seat at US$7.00 a month is cheaper and far
simpler than qualifying.

---

## Two terms that bind Qori, not the creator

Everywhere else in this document, a platform's limits are the creator's to live
with: their plan, their storage, their administrator. These two are different.
They are clauses in the agreements **Qori** accepts as the party using the API,
and they are about charging money while doing so.

**Your reading, recorded as `D-019` on 17 September 2026.** A paid Series on Qori
charges for the creator's consultation, live sessions and knowledge. The videos
are course material, and may be public. Neither clause describes what a paid
Series does, so both vendors are offered in every Series, priced or free. What
follows is kept as reference: what each clause says, and how to write to each
vendor.

### YouTube: selling access to anything built on its API

YouTube's developer policies, section III.G.1.b, forbid a developer to "sell
YouTube API Services or access to any components of YouTube API Services"
without YouTube's prior written approval
([YouTube API Services Developer Policies](https://developers.google.com/youtube/terms/developer-policies),
last updated 14 September 2026, checked 17 September 2026).

**Who it binds: Qori.** The policies bind the developer and the app the developer
builds, and also forbid the developer to encourage or enable others to break
them. The creator is neither the developer nor the app.

**The clauses beside it.** The clause just before it, III.G.1.a, forbids selling,
redistributing or sublicensing any part of the API services and names YouTube's
audiovisual content as part of them. A separate clause, III.F.3.a, forbids
charging users to watch content in an embedded YouTube player; Qori opens YouTube
in a new tab rather than embedding.

**Where to write to YouTube, if you ever want to.** Nothing in this document
requires it. The policies themselves name the same form as the quota audit,
[support.google.com/youtube/contact/yt_api_form](https://support.google.com/youtube/contact/yt_api_form),
as the channel for approvals. YouTube publishes no turnaround and no criteria.
The form expects a public product with working demo logins, so it cannot
realistically be filed before Qori has one.

### Vimeo: charging your own users while using its API

Vimeo's Developer Addendum, section 3.5, says a developer "may not charge End
Users a fee for your Application unless we expressly authorize" it, in writing
([Vimeo Developer Addendum](https://vimeo.com/legal/service-terms/api), last
updated 9 March 2026, checked 17 September 2026).

**Who it binds: Qori**, as the party using Vimeo's developer interfaces. The
addendum defines an end user as a user of the developer's application, which for
Qori means its creators and Peers. The creator's own Vimeo plan has nothing to do
with it.

**Writing to Vimeo is optional.** If you ever want your reading confirmed in
writing, a support ticket costs nothing. It is not required for anything in this
document.

**Where to write to Vimeo.** Its ordinary support channel at
[vimeo.com/help/contact](https://vimeo.com/help/contact), which Vimeo's developer
guidelines point developers to for anything unclear. There is no dedicated form
and no dedicated address. Sign in, choose "Contact us" at the top of Vimeo's help
centre (or the chat box at the lower right), work through the assistant until it
offers to create a ticket, and keep the ticket number. **Vimeo publishes no
turnaround for a decision.** It publishes only first-reply times by the plan of
the account filing the ticket (checked 17 September 2026): usually within three
business days on Free, eight hours on Starter, six on Standard and two on
Advanced, with its own caveat that complex issues are passed to specialists and
can still take several days. Those are first replies, not decisions, and filing
from a paid account gets a faster first reply. Vimeo's support also states that
it cannot connect you to a sales representative, so there is no route round it
through sales.

**What to put in a ticket, if you file one.** Describe both money flows: Qori's
own subscription fee, and a Peer paying a creator for a Series that uses Vimeo
videos as course material alongside the creator's time and knowledge, with the
reading recorded in `D-019`.

---

## Owner checklist

In the order to do them. Every price was checked 17 September 2026.

- Make sure **the privacy policy and terms of service are live on
  `useqori.com`**. Google, Microsoft, Dropbox, Zoom and Vimeo all need them, and
  they are already on the beta gate.
- Create **Qori company accounts on `useqori.com` addresses** for Google, Dropbox,
  Vimeo and Zoom, because each vendor ties the app to the account that creates it.
  Free.
- Create the **Google Cloud project for Google Drive**: switch on the Drive and
  Picker APIs, verify `useqori.com` in Search Console, fill in branding, create the
  OAuth client and the API key, and **press Publish app**. Free.
- Start the **Partner Center enrolment** for work and school OneDrive, which is
  in beta (`D-018`), with the business registration documents and the
  `useqori.com` registrar record to hand; Microsoft publishes three to five
  business days for its verification. Free.
- Create the **Microsoft Entra app registration** in the tenant from that
  enrolment. Free; a card is taken for identity and not charged.
- Create the **Dropbox app** on a free account, with scoped access and Full
  Dropbox, and run the free test of whether a free creator can add a view-only
  Peer. Free.
- Create a **free Microsoft Teams account**, schedule one recurring meeting and
  check its join link. Free.
- Create the **Vimeo API app** on a free Vimeo account, answering Yes to other
  people accessing it. Free.
- Buy **one month of Zoom Workplace Pro**, US$16.99 (A$25.99 excluding GST) billed
  monthly, then build the Zoom General app and test it in development mode. The app
  is free.
- Buy **one month of Vimeo Starter**, US$20 billed monthly, to prove the unlisted
  link, then cancel.
- Check **the category beside `youtube.readonly`** in the Cloud console, and, once
  `T-093` has settled the Drive permission, switch on the YouTube Data API in the
  project that decision points to. Free.
- **Only if the free Dropbox test is refused:** start a Dropbox Professional or
  Standard free trial, and cancel from the billing date in the confirmation email.
- Buy one **Microsoft 365 Business Basic** seat, US$7.00 per user per month, in the same tenant, and complete
  publisher verification once Partner Center shows Authorized.
- **Optional:** a 14-day Google Workspace trial, A$0 if cancelled by day 12, on a
  throwaway domain and never on `useqori.com`.
- **Optional:** a Vimeo support ticket, if you ever want your reading of section
  3.5 (`D-019`) confirmed in writing. Free.
- **Before the beta date, since every vendor is in it (`D-018`):** submit Google's brand verification,
  and its OAuth verification if `youtube.readonly` is sensitive; apply for Dropbox
  production with an early-review request; and submit the Zoom Marketplace review
  at least a month, ideally two, before the beta date. All free; only Dropbox
  publishes a turnaround, and even that one starts at 50 linked accounts.
