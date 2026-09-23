# Fixups

Renames, copy slips and small UI faults: recorded so they are not lost, kept
out of the streams so they do not crowd the product. One line each — what,
where, and the date it was seen. Whoever is working in that file fixes it and
deletes the line in the same commit; no task, no report. A fixup that turns
out to need a decision or more than an hour is a task instead.

**For the next product:** the cause is worth more than the list. Most of these
are nouns written inline instead of through `Terminology`, and words left
mangled by find-and-replace renames — the playbook's rules on both are what
stops them recurring, not this file.

## Open

- Public Series page: the code's length is written as `6` three times instead
  of coming from `LoginCodeService::LENGTH`. `resources/js/pages/public/Series.vue:346,354,370` (23 Sep)
- The Peer's two homes have two names: "Shared with me" in the sidebar, "My
  shared" in the user menu, the access email and one error.
  `resources/js/components/UserMenuContent.vue:56`, `lang/en/accesses.php:28`, `lang/en/errors.php:590` (23 Sep)
- Profile's timezone help tells a Peer about what time "your Peers" are told a
  session starts. `resources/js/pages/settings/Profile.vue:183` (23 Sep)
- The comment says resend is limited per address and IP; resend posts no
  address, so the limiter keys on the IP alone. `routes/web.php:113-116` (23 Sep)
- `docs/flows/accesses.md` still writes the Group routes as `/w/{group}` (they
  are `/g/`) and names `CONSENT_STUDENT` (the case is `ConsentSource::Peer`). (23 Sep)
- `errors.playback.missing_content` says "That episode doesn't have anything to
  open yet" — the Episode noun hardcoded and lowercase. `lang/en/errors.php:518` (23 Sep)
- Register: the share card reads "Set up a school and publish series." — a
  noun that is not the Group's, lowercase. `resources/js/pages/auth/Register.vue:14` (21 Sep)
- New Series form: "What your peers will learn", "Shown on the certificate your
  peers can share" — lowercase and hardcoded. `resources/js/pages/share/series/Index.vue` (21 Sep)
- Episode form: "Let anyone preview this episode" — lowercase and hardcoded.
  Series page, New Episode panel (21 Sep)
- Sign in: Enter in the email field does not advance to the next step; only
  clicking Next does. `resources/js/pages/auth/Login.vue` (21 Sep)
- A file Episode shows "No materials" under itself straight after upload (21 Sep)
- CI reads a `.nvmrc` that was never committed (`T-081` listed it). `.github/workflows/tests.yml` (21 Sep)
- `php artisan qori:reachability` exits 1 on two public methods nothing calls from
  outside their own class: `AccessService::peerFor()` and
  `SuppressionService::suppress()` — private, probably. `app/Services/` (22 Sep)
