---
id: T-197
title: Someone who signs up to receive is told how a Series reaches them
stream: onboarding
status: ready
owner: unassigned
estimate: S
depends: T-048
blocks: none
---

# T-197 — Someone who signs up to receive is told how a Series reaches them

## Why

Registering with "I want to learn" and verifying lands on the receiving home,
`/dashboard` (`HomeController::index()`), which for someone with nothing yet
says "Hello, Sam — Your Series will show up here", then an In progress panel,
"Nothing on the go: When someone shares Series with you, they show up here",
then "Want to share?". Nothing says that a Series arrives as a link from the
person sharing it, or which inbox it will reach. The onboarding plan, which
spells out `D-001`'s receiving path, asks for "an honest receiving welcome
explaining how to open the sender's link" with no invented catalogue
([`ui-onboarding.md`](../../design/ui-onboarding.md), "Receiving a Series"),
and R-004 F-10 found the same gap on the empty `/shared` list. Cut from
`T-027` on 23 September 2026.

Afterwards someone with nothing shared yet is told how a Series reaches them,
at which address, and what to do if they cannot find it.

## Decisions taken to make this specifiable

**The receiving home, not the `/shared` list.** A direct signup lands on
`/dashboard`, so that is where the welcome is owed. `/shared` is the "Shared
with me" composition the redesign sprint rebuilds with its cards
([`ui-redesign-next-sprint.md`](../../design/ui-redesign-next-sprint.md) §5,
R-004 F-10: "rebuild this composition once"), and its controller is claimed
by five ready tasks in other streams. The three lines are written in
`lang/en/shared.php` so that rebuild can use them.

**Only when nothing is shared with them now.** The test is `$shared === []`,
which `HomeController::shared()` builds from active accesses to Series that
still exist, so a person whose Series are all finished still meets the
existing "Nothing on the go", and a person whose only access was revoked, or
whose Series was deleted, meets the welcome — which is true of them: nothing
is shared with them now.

**It names their own address and promises nothing else.** The link usually
comes by email to the address they signed up with; saying which address is
the recovery R-004 asked for. It does not say a Series will come, or from
whom.

## Preconditions

**Data this task verifies against:** a clean database; a learner from a
factory, with and without an Access.

**Equipment:** a browser for the walk, and Mailpit for the verification
email.

## Scope

**In:**

- The In progress panel on `/dashboard` for someone with nothing shared: a
  title, the sentence naming their address, and what to do if the link is
  missing.

**Out:**

- The empty `/shared` list and the receiving cards → the redesign sprint, §5.
- The "Want to share?" sentence → `T-048`, which this task follows in the
  same file.
- The header's "Your Series will show up here" and the other inline English on
  the page → `T-006`.
- The timezone: `T-027` asks it on the first Series page they open.

## Files

| Path | Change | Notes |
| --- | --- | --- |
| `app/Http/Controllers/HomeController.php` | edit | `welcome` prop when nothing is shared |
| `resources/js/pages/Dashboard.vue` | edit | the panel's empty state from `welcome` |
| `lang/en/shared.php` | edit | `shared.welcome.*`, three keys |
| `tests/Feature/Access/ReceivingWelcomeTest.php` | new | 3 cases |

Flows: none — the receiving home gains one prop built from lang;
`HomeController::index()`'s redirect, which `docs/flows/onboarding.md`
describes, does not change.

## Database

None.

## Code

`HomeController::index()` adds, beside `shared`, `summary` and `sharing`:

```php
'welcome' => $shared === [] ? [
    'title' => __('shared.welcome.title'),
    'body' => app(Terminology::class)->line('shared.welcome.body', ['email' => $peer->email]),
    'missing' => __('shared.welcome.missing'),
] : null,
```

`Dashboard.vue` takes `welcome: { title: string; body: string; missing:
string } | null`. In the In progress `Panel`, before the existing
`EmptyState`:
`<EmptyState v-if="welcome" :icon="BookOpen" :title="welcome.title" :description="welcome.body">`
with `<p class="text-muted-foreground text-sm">{{ welcome.missing }}</p>` in
its slot; the existing one becomes `v-else-if="!inProgress.length"`.

## Copy

| Key | File | English |
| --- | --- | --- |
| `shared.welcome.title` | `lang/en/shared.php` | Nothing shared with you yet |
| `shared.welcome.body` | `lang/en/shared.php` | Anything shared with you arrives as a link from the person sharing it, usually by email to :email. Open the link and the :series is here from then on. |
| `shared.welcome.missing` | `lang/en/shared.php` | Can't find it? Look in that inbox's spam folder, or ask them to send the link again. |

## Routes

None.

## Tests

**New: `tests/Feature/Access/ReceivingWelcomeTest.php` — 3 cases**

1. `test_someone_with_nothing_shared_is_told_how_a_series_reaches_them` — `/dashboard` for a learner with no Access: `welcome.body` is `shared.welcome.body` with their address.
2. `test_someone_with_a_series_is_not_welcomed_again` — one active Access: `welcome` is null.
3. `test_a_learner_lands_on_the_welcome_after_verifying` — `register.store` with `signup_intent` `learn`, the signed verification link, then `/dashboard`: `welcome` is set.

3 new. No existing case changes.

## Acceptance

- [ ] A learner with nothing shared with them is told on the receiving home how a Series reaches them, at their own address, and what to do if it does not
- [ ] Someone with a Series, finished or not, never sees it
- [ ] A browser walk: register to learn, verify, land on the welcome, at 375px and desktop
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `bin/tasks --check` passes in `qori-plan`
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Re-scope log

None.

## Notes

The receiving home and the `/shared` list are named differently across the
product: "My shared" in the user menu, the access email and one error, "Shared
with me" in the sidebar. A fixup line in `fixups.md`, not this task.
