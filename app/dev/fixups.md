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

- Register: the share card reads "Set up a school and publish series." — a
  noun that is not the Group's, lowercase. `resources/js/pages/auth/Register.vue:14` (21 Sep)
- New Series form: "What your peers will learn", "Shown on the certificate your
  peers can share" — lowercase and hardcoded. `resources/js/pages/share/series/Index.vue` (21 Sep)
- Episode form: "Let anyone preview this episode" — lowercase and hardcoded.
  Series page, New Episode panel (21 Sep)
- `consent.required` reads "Please agree to be peered before granting." — a
  rename's leftover; not reachable from the page, which disables Continue.
  `lang/en/accesses.php:76` → `T-118` holds the rest of that rename's debris (21 Sep)
- Setup part 1 says "Change it if that is not right, then save" beside a
  button labelled Continue, and says "Your Peers see this…" twice. `resources/js/pages/share/setup/` (21 Sep)
- Setup part 3: "Continue" and "Set this up later" do the same thing from the
  creator's side (21 Sep)
- Sign in: Enter in the email field does not advance to the next step; only
  clicking Next does. `resources/js/pages/auth/Login.vue` (21 Sep)
- Public Series page: Continue is disabled until consent is ticked, with no
  hint why (21 Sep)
- A file Episode shows "No materials" under itself straight after upload (21 Sep)
- The dashboard's rename card still says "Name your Group" once named → `T-086` (seen three times, again 21 Sep)
- CI reads a `.nvmrc` that was never committed (`T-081` listed it). `.github/workflows/tests.yml` (21 Sep)
