---
id: T-015
title: Configure Postmark and the production sender
stream: delivery
status: done
owner: wayne
estimate: M
depends: none
blocks: T-032, T-017
---

# T-015 — Configure Postmark and the production sender

> **Closed 11 September 2026.** Everything below was verified rather than
> reported — see the table and the report. What it does **not** establish is
> that mail arrives; that is `T-032`.

## Why

`MAIL_MAILER=log` everywhere. No transactional email has ever left the
application, and none ever will until a domain, a DNS record and a verified
sender exist.

## Scope

**In:**

- Postmark configuration, `MAIL_FROM_ADDRESS`, DNS authentication (SPF, DKIM, DMARC), and delivery monitoring.

**Out:**

- Broadcast/EDM sending, which is SES and a different decision (§9).

## What is done, verified 11 September 2026

The owner registered `useqori.com`, verified the domain in Postmark against a
`qori_production` server, pointed the domain at Laravel Cloud and deployed both
Postmark and Sentry configuration. Sentry was removed from the local `.env`, so
a dev machine no longer files into the production issue stream.

Confirmed from this machine rather than taken on report:

| What                     | State                                                                                                                                               |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `useqori.com` and `www`  | Resolve, through Cloudflare                                                                                                                         |
| `https://useqori.com`    | **200, and it is Qori** — serving the app, `qori-session` cookie set                                                                                |
| `pm-bounces.useqori.com` | `CNAME → pm.mtasv.net`, and **not proxied** — the lookup returns the target rather than Cloudflare IPs, which is what it must do                    |
| `.env.testing`           | Still carries no vendor keys at all                                                                                                                 |
| Packages and wiring      | `symfony/postmark-mailer`, `sentry/sentry-laravel`, the Postmark transport, and `Integration::handles()` in `bootstrap/app.php`. No code was needed |

DKIM is verified by Postmark's own domain status. It cannot be checked from
outside without the selector, which Postmark generates per domain.

The apex `TXT` remains Cloudflare Email Routing's SPF, for receiving. It is
unrelated to Postmark and correctly untouched — Postmark aligns SPF through the
return-path CNAME above rather than through the sending domain's SPF record.

## Files

None. This task changed nothing in the repository, which was the finding: both
packages, the Postmark transport, `services.postmark.key` and
`Integration::handles()` were already in place, so the whole of it was account
and DNS configuration. The only edits here are to this task file and its report.

## Database

None.

## Code

None.

## Copy

None.

## Routes

None.

## Tests

None that can run here. A test asserting production DNS would either hit the
network from the suite or assert a fixture, and neither tells you anything about
the live zone. What holds this instead is `.env.testing` carrying no vendor keys
at all, so the suite cannot reach Postmark whatever anybody configures.

Verification was by public DNS lookup and one HTTP request, recorded in the
report.

## Acceptance

- [x] `useqori.com` registered, on Cloudflare, and resolving
- [x] The application answers on it over HTTPS
- [x] Postmark shows the domain verified, against a `qori_production` server
- [x] Return path `pm-bounces → pm.mtasv.net`, and **not proxied**
- [x] DMARC published at `p=none` with an aggregate report address
- [x] `MAIL_MAILER=postmark`, `MAIL_FROM_ADDRESS` on the verified domain
- [x] Sentry deployed, and **removed** from the local `.env`
- [x] `.env.testing` still reaches no vendor
- [ ] Real transactional mail confirmed arriving at two providers — **this is
      `T-032`, deliberately not here.** Configuration being right is not the
      same fact as mail arriving.

## Re-scope log

None.

## Notes

**One unchecked assumption sits inside the DMARC record.** `rua` points at
`dmarc@useqori.com`, and aggregate reports are the entire reason to publish
`p=none`. If that address does not route — the domain uses Cloudflare Email
Routing, so it needs a rule — the reports bounce and the record is decoration.
Send something to it and confirm it lands before trusting the fortnight of data
that is supposed to decide whether to tighten to `quarantine`.

**`APP_URL` was not in the list of environment variables the owner confirmed.**
Four mail variables were. It matters as much as any of them: magic links and
verification links are signed and the signature covers the whole URL, so an
`APP_URL` that is not `https://useqori.com` produces links that never validate.
Worth reading once in the Laravel Cloud dashboard.
