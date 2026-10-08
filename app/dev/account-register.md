# Account register

> Every external account Qori runs on: who signs in, who owns it, what it costs and when it renews.

[Current plan](../PLAN.md) | [Planning index](README.md) | [Release prerequisites](release-prerequisites.md) | [Vendor accounts](vendor-accounts.md)

Started 26 September 2026. **Every account signs in as `accounts@useqori.com`**,
so nobody has to wonder why one service knows a different address, and Qori's
accounts, assets and spend stay apart from anyone's personal ones. `accounts@`
is a Zoho group that delivers to `wayne.lu@useqori.com`. **Owner: Wayne Lu on
every row.**

This lists accounts, not secrets. Passwords, API keys and recovery codes never
go here.

## Accounts

**Login** is the address that signs in. **Backup login** is a second member kept
only to get back in if `accounts@` ever stops receiving mail. `?` is still to be
checked.

| Service       | What Qori uses it for                                                                   | Login                   | Backup login                    | Owner    | Cost                                                    | Renews                                              | On `accounts@`      |
| ------------- | --------------------------------------------------------------------------------------- | ----------------------- | ------------------------------- | -------- | ------------------------------------------------------- | --------------------------------------------------- | ------------------- |
| Cloudflare    | `useqori.com`'s registration and DNS, R2 file storage, the Worker                       | `accounts@useqori.com`  | Wayne's personal Gmail          | Wayne Lu | Domain US$10.44 a year at cost; R2 free to 10 GB, then usage | Domain: 11 Sep 2027 if registered for one year — check | ✅ 24 Sep 2026      |
| Zoho Mail     | Mail for `useqori.com`: the `wayne.lu@` mailbox, `accounts@` and `support@`             | `wayne.lu@useqori.com`  | ?                               | Wayne Lu | Free plan, up to 5 users                                | —                                                   | Exception, see notes |
| Google Cloud  | Project `910317206529`: Google Drive's OAuth client and Picker; Search Console          | Moving to `accounts@`   | Wayne's personal Gmail, if kept | Wayne Lu | Free                                                    | —                                                   | ⬜ In progress      |
| Laravel Cloud | Hosting, Valkey, the scheduler                                                          | ?                       | ?                               | Wayne Lu | Starter US$5 a month plus usage                         | Monthly                                             | ⬜                  |
| Neon          | Production Postgres                                                                     | ?                       | ?                               | Wayne Lu | ?                                                       | ?                                                   | ⬜                  |
| Postmark      | Transactional mail from `useqori.com`, server `qori_production`                         | ?                       | ?                               | Wayne Lu | Free to 100 a month; US$15 a month for 10,000 — which?  | ?                                                   | ⬜                  |
| Mailtrap      | Test mail on Laravel Cloud until launch                                                 | ?                       | ?                               | Wayne Lu | ?                                                       | ?                                                   | ⬜                  |
| Sentry        | Error reports                                                                           | ?                       | ?                               | Wayne Lu | ?                                                       | ?                                                   | ⬜                  |
| Stripe        | Payments and Connect; sandbox now                                                       | ?                       | ?                               | Wayne Lu | Per transaction, no monthly fee                         | —                                                   | ⬜ Before live      |
| Dropbox       | The `Qori Share` app, in development                                                    | ?                       | ?                               | Wayne Lu | Free                                                    | —                                                   | ⬜ See notes        |
| Vimeo         | The API app                                                                             | ?                       | ?                               | Wayne Lu | Free; Starter US$20 for one test month                  | —                                                   | ⬜ See notes        |
| GitHub        | The `qori` and `qori_plan` repositories                                                 | `waynelu81`             | —                               | Wayne Lu | ?                                                       | ?                                                   | Exception, see notes |

### Notes

- **Cloudflare.** Moved off Google sign-in with the personal Gmail on 24
  September 2026. The Gmail came back as a second member, which is the way in
  if the domain ever lapses and takes `accounts@` with it, so it must be a
  Super Administrator. The domain's registrant contact is a separate record
  from the login: changing its name or email needs approval from both
  addresses within seven days, then locks transfers for 60 days unless the
  opt-out is ticked. Before removing any Cloudflare user, check whether
  Laravel Cloud's R2 key is a User API token, which stops working when its
  user leaves; an Account API token does not.
  - **8 October 2026, a correction:** the Google link outlived the change of
    email. "Sign in with Google" with the personal Gmail still opens this
    login, and Cloudflare offers no way to unlink it (seen on 3 October 2026,
    when the owner was locked out until that day). The backup member signs in
    with email and password, never with the Google button.
- **Zoho Mail.** Australian data centre, MX `mx.zoho.com.au`, since 24
  September 2026, replacing Cloudflare Email Routing. It signs in as
  `wayne.lu@` because `accounts@` is a group here, and a group cannot sign in.
  DKIM selector `zohodkim`, SPF `include:zohomail.com.au`, DMARC `p=none` with
  reports to `dmarc@`, which must exist as an alias or a group. Confirm the
  plan is Forever Free, not the 15-day trial.
- **Google Cloud.** Invite `accounts@` as Owner under IAM and accept it; then,
  signed in as `accounts@`, set the Branding page's support and developer
  emails, and add `accounts@` as an owner of `useqori.com` in Search Console.
  The project, client, secret and API key do not change.
- **Stripe.** Move the login before activating the live account
  ([`release-prerequisites.md`](release-prerequisites.md)).
- **Dropbox and Vimeo.** Each app stays with the account that created it
  ([`vendor-accounts.md`](vendor-accounts.md)). If that account is Qori's
  alone, change its email to `accounts@`. If it is personal, re-register the
  app under an `accounts@` account: a new key and secret in Laravel Cloud, and
  every connection made again, which costs least before the beta.
- **GitHub.** The repositories can move to an organisation owned by an
  `accounts@` user, and GitHub redirects the old addresses, but Laravel Cloud
  deploys from them and its connection would need redoing. A job of its own.

## Not opened yet

Open each on `accounts@` from the start, signing up by email rather than
"Sign in with Google".

| Service                 | What Qori will use it for                                                        | Cost                                                                        | When                       |
| ----------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------- |
| Microsoft               | Entra tenant and app registration for OneDrive; Partner Center to verify Qori     | Free: the E5 developer sandbox where eligible, otherwise a one-month Business trial cancelled before it bills (`D-042`, `T-097`) | Next                       |
| Zoom                    | The General app for live sessions                                                | App free; Zoom Workplace Pro US$16.99 for one test month                    | Next                       |
| Wise Business           | Stripe's AUD payouts                                                             | ?                                                                           | Before Stripe goes live    |
| AWS                     | SES for broadcast mail                                                           | US$0.10–0.16 per 1,000 emails                                               | When broadcast goes live   |
| Apple Developer Program | The iOS app                                                                      | US$99 a year                                                                | When the iOS app starts    |
| Google Play Console     | The Android app                                                                  | US$25 once                                                                  | When the Android app starts |

## Moving an account onto `accounts@`

1. On the service's Team, Members, Users or IAM page, invite
   `accounts@useqori.com` with the highest role there is.
2. Accept from the Zoho inbox, and sign in as `accounts@` from then on.
3. Where there is no team feature, change the login email in the profile
   instead. Re-register only where neither exists, and before the beta, while no
   creator is connected through it.
4. Keep an old login only as a backup, and write it in this register.
