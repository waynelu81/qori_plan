---
id: T-053
title: Signing out lands on the sign-in page, and says so
stream: identity
status: done
owner: claude
estimate: S
depends: none
blocks: none
---

# T-053 — Signing out lands on the sign-in page, and says so

## Why

Signing out sends a person to `/`, the marketing page. Fortify's
`LogoutResponse` falls through to `Fortify::redirects('logout', '/')` and
nothing overrides it. The owner, 13 September 2026: "For a registered user,
back to the home page is useless — they know Qori." They asked for either the
sign-in page or a holding page that says they are signed out and offers to sign
in again or close the tab.

## Decisions taken to make this specifiable

**The sign-in page, with one quiet sentence.** A holding page whose two options
are "sign in again" and "close the tab" is the sign-in page with a button in
front of it: signing in again is what that page is for, and closing a tab needs
no button. What the holding page would add is the sentence, so the sentence
goes on the sign-in page instead.

**Its own flash key, not `status`.** The sign-in page deliberately renders
`status` only after a link was requested from that page (`T-036`), because
`status` is a general flash and showing "Check your email" for somebody else's
sentence would be a lie. That rule stays. The sign-out sentence arrives under a
key of its own and is rendered where a person who just signed out will read it,
above the method chooser.

**The flash survives the session being invalidated.** Fortify's
`AuthenticatedSessionController::destroy()` invalidates and regenerates before
the response is built, so a flash set by the response lands in the fresh
session. Read from the framework source rather than assumed.

## Preconditions

None beyond a clean checkout.

## Scope

**In:**

- Where a creator or Peer lands after signing out, and what that page says.

**Out:**

- Staff sign-out (`admin.logout`), which belongs to the console.
- Session expiry, which is not a sign-out anyone chose and has its own copy.
- The sign-in composition itself.

## Files

| Path                                        | Change | Notes                         |
| ------------------------------------------- | ------ | ----------------------------- |
| `app/Http/Responses/LogoutResponse.php`     | new    | Replaces Fortify's            |
| `app/Providers/FortifyServiceProvider.php`  | edit   | Binding; one prop on the view |
| `resources/js/pages/auth/Login.vue`         | edit   | Render the sentence           |
| `lang/en/auth.php`                          | edit   | 1 key                         |
| `tests/Feature/Auth/SignOutTest.php`        | new    | 2 cases                       |
| `tests/Feature/Auth/AuthenticationTest.php` | edit   | One redirect assertion        |

`app/Providers/FortifyServiceProvider.php` is also claimed by `T-052`; run the
two in sequence.

## Database

None.

## Code

```php
// App\Http\Responses\LogoutResponse
public const FLASH = 'auth.signed_out';

public function toResponse($request): RedirectResponse|JsonResponse
{
    return $request->wantsJson()
        ? new JsonResponse('', 204)
        : redirect()->route('login')->with(self::FLASH, __('auth.signed_out'));
}
```

```php
// FortifyServiceProvider::configureViews(), loginView:
'signedOut' => $request->session()->get(LogoutResponse::FLASH),
```

```vue
// Login.vue, above <SignInMethods>:
<p v-if="signedOut" class="text-muted-foreground text-center text-sm">{{ signedOut }}</p>
```

`defineProps` gains `signedOut?: string | null`.

## Copy

| Key               | File               | English              |
| ----------------- | ------------------ | -------------------- |
| `auth.signed_out` | `lang/en/auth.php` | `You're signed out.` |

## Routes

None. `login` and `logout` both exist.

## Tests

**New: `tests/Feature/Auth/SignOutTest.php` — 2 cases**

1. `test_signing_out_lands_on_the_sign_in_page` — POST `logout`, redirected to
   `route('login')`, and a guest afterwards. **Fails today**, landing on `/`.
2. `test_the_sign_in_page_says_they_signed_out` — follow the redirect, and the
   `signedOut` prop carries the sentence; a fresh visit to the page carries
   null, so it is said once.

**Changed:**

- `tests/Feature/Auth/AuthenticationTest.php::test_users_can_logout` asserts
  `route('home')` and must assert `route('login')`. That is the defect, and
  the assertion was recording it.

## Acceptance

- [x] Signing out lands on the sign-in page
- [x] That page says "You're signed out." once, and not on the next visit
- [x] The link-sent confirmation still only appears after a link is requested
      from that page
- [x] Staff sign-out is untouched
- [x] `composer ci:check` green from a clean tree
- [x] Board regenerated (`php artisan qori:tasks`)
- [x] Report written in `reports/`

## Re-scope log

None.

## Notes

`T-008` put the first application-owned Fortify response in
`app/Http/Responses/`. This is the second, and `T-052` adds three more. Once
they exist, `config/fortify.php`'s missing `redirects` block is no longer a
gap worth filling: every landing that matters is decided in code that can look
at who is signing in or out.
