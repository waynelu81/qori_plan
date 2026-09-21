---
id: T-132
title: A Peer with access finds the class chat on the Series page
stream: classroom
status: draft
owner: unassigned
estimate: M
depends: T-130, T-131
blocks: T-136, T-137
---

# T-132 — A Peer with access finds the class chat on the Series page

> **Draft.** Specified from `D-029` on 18 September 2026 and not to be started —
> see [`../PROCESS.md`](../PROCESS.md). `T-130` is `ready`; it waits on `T-131`
> being `ready`, because it calls names that task mints; the list at the bottom
> says what else has to be settled before it can be marked `ready`.

## Why

The course this stream is built around runs its conversation in a WhatsApp or
WeChat group, and today Qori has nowhere to put the way in. The Peer's Series
page renders a title, a summary, the Episode rows and progress
(`app/Http/Controllers/Shared/SharedController.php:129-161`) and nothing else;
the creator's page has panels for Episodes, details, progress, Peers, the share
link, access, archiving and deletion (`resources/js/pages/share/series/Show.vue`)
and none for a chat. So the invite is pasted into the access email by hand or
sent one Peer at a time, and a WeChat group code — which lasts seven days —
goes stale with nobody told.

`D-029` decided the shape: a chat invite is creator content, one row in
`series_chats` per Series, a link or a QR image, shown only to Peers with
access, opened through a Qori route that logs the open, hidden after its
expiry date with the creator told to replace it. Qori calls no chat vendor,
reads no link host and has no `app/Integrations` folder for any of them; a
Peer who leaves is removed from the chat by hand. `D-024` fixes where the card
lives — the Series page under `/shared` — and that every new `/shared/*` route
requires an active Access; `D-029` puts it at `id="chat"` and has every email
point at that anchor rather than at the invite itself.

Afterwards a creator adds the group's invite link or its code image, with the
date printed under the code, from the Series page. A Peer with access finds a
"Join the class chat" card above the Episodes, follows it to the invite or the
image in a new tab, and dismisses it with "I've joined". After the date the
card hides the code and says so, the creator's page asks for a new one, and a
stale link lands back on `#chat` with a one-line toast (`D-020`). Removing the
chat, replacing its image and purging the Series each delete the image from
Qori's storage, because `SeriesService::purge()` keeps the Series row and
nothing cascades (`app/Services/SeriesService.php:277-310`).

## Decisions taken to make this specifiable

**One chat per Series, with exactly one way in: a link or a code, never
both.** `qori.chats.per_series` is 1 (`D-029`, declared by `T-123`), and the
`position` column stays for later as the decision says. `D-029`'s "one of
`url` or `media_asset_id` required" is read as exactly one, as a check
constraint in the shape `series_price_has_currency` already uses
(`database/migrations/2026_09_13_000002_couple_series_price_to_currency.php:34-39`):
the card then has one control and the open route one target, and each platform
hands a creator one thing — WhatsApp an invite link, WeChat a code image. The
form asks "How people get in" the way the Episode form asks "Where it lives".

**The code image is opened, not embedded.** "Show the code" is an
`<a target="_blank">` to `shared.chats.open`, which answers a 302 to a signed
URL that lives `qori.storage.link_ttl.image` minutes. An inline `<img>` would
mint a signed URL on every page view and log an open nobody made — the reason
`shared/Show.vue:74-81` gives for not fetching links with the page. In a new
tab a phone shows the code full-screen, which is what a WeChat user long-presses
to open in the app.

**The Peer's page carries the open route and never the invite.** The prop is
`openUrl`, built with `route('shared.chats.open', …)` in the controller; the
raw `url` never reaches the Peer surface or the public page. That is what makes
the `access_opens` row honest — a URL in the props is a URL that can be
followed unlogged — and what keeps a replaced link from stranding anybody who
bookmarked the page (`D-029`).

**Expiry is a calendar day in the Group's zone.** `expires_on` is a `date`,
entered as printed under the code. The code works through that whole day and
is expired from the next midnight in `Group::timezone()`, so
`SeriesChat::isExpired(CarbonImmutable $now)` compares date strings in that
zone and never a UTC instant against a local day. A creator who pastes an
already-expired code sees the expired notice at once, which is honest, so the
Form Request does not refuse a past date.

**An expiry belongs to a code and never to a link.** `expires_on` is accepted
only beside `media_asset_id`: `StoreChatRequest::withValidator()` refuses a
date on a link with `errors.chats.expiry_needs_code`, `guardWayIn()` refuses
the same at the service, and `ChatForm.vue` shows the field only when `kind`
is `code`. The column stays nullable on every row because a code may have no
date printed under it. The rule is what makes every expiry line true —
`chats.form.expires_label`, `chats.form.expires_help`, `chats.form.expired`,
`chats.peer.expires` and `chats.peer.expired` all speak of a code, as `D-029`
does ("hides the code") — and a WhatsApp invite link has no day a creator can
read off it; a link that stops working is replaced, not dated.

**The Peer's gate lives in `SeriesChatService::open()`, which answers the URL
or null.** Access through `Access::forUser()` (active rows only, so a revoked
Access is absent), the Series through `Series::findForPeer()`, the chat through
`forGroup($series->group_id)` — never `acrossAllGroups()`, so the allow-list in
`tests/Feature/Admin/ConsoleAccessTest.php:131-151` is unchanged. The service
records the `AccessOpen` and returns the invite URL or the signed image URL;
null means the code has expired and the controller sends the Peer back to
`#chat` with the toast, exactly as `T-089`'s controller does for a blocked
link. The tuple-versus-Data-object question `T-089` leaves open does not arise,
because the answer here is a string.

**A code's size and type are refused when the upload is signed, and enforced
when the chat is saved.** `SignUploadRequest` already takes `purpose`
(`app/Http/Requests/Share/SignUploadRequest.php:34`); for `chat_code` it adds
`extension` in `SeriesChatService::CODE_EXTENSIONS` and `size` at most
`qori.chats.code_max_mb`, so a 15 MB photo is refused before any bytes move
rather than after. `SeriesChatService::guardCode()` then checks the asset row
on save — stored, this Group's, purpose `chat_code`, extension and
`size_bytes` — because a Form Request is a message, not an enforcement
boundary (the reason `StoreEpisodeRequest.php:20-25` gives). `UploadService`
is untouched: `sign()` knows the purpose and not what each purpose allows, and
`T-130` did not teach it either.

**The cap is an invalid request, not a plan limit.** `errors.chats.limit`
throws `AppException::invalidRequest()`: the cap is a sanity cap on every plan
and not a tier lever (`D-030`'s rule for materials, applied here), and
`PlanLimitReached`'s default copy tells the reader to upgrade. The page hides
the add form at the cap, so the refusal is the service's guarantee against a
stale page.

**Three constants on the service, not config.** `T-123` alone declares
`qori.chats` and `qori.live` (`streams/classroom.md`, claim order), and none of
these three is a number the owner tunes: `NOTE_MAX = 300` is the column's
length (`D-029`), read by the request's `max:` and the textarea's `maxlength`;
`WECHAT_CODE_DAYS = 7` is WeChat's own rule, read by the help line's `:days`
and by the form's pre-filled expiry; `CODE_EXTENSIONS` is what a QR image is.
Each is written once and interpolated everywhere it is said.

**The row goes before the asset.** `D-029` gives `media_asset_id` null on
delete and requires one way in; the two meet at the check constraint, which
would refuse a nulled asset on a code-only row. Nothing but this task's service
deletes a `media_assets` row today (`CloudflareR2Uploads.php:20-24`: nothing
there deletes), and the service orders every deletion object → chat row →
asset row, so the constraint never fires in practice and a future delete path
that forgets the order fails loudly rather than leaving a card that opens
nothing.

**The image goes with the row.** `remove()`, a replacement on `update()` and
`purgeFor()` each delete the object by `media_assets.key` and then the
`media_assets` row: a stored asset whose object is gone is a pointer to
nothing, and `app/Models/MediaAsset.php:29-32` says only a _pending_ row is
harmless. A failed object delete is logged and swallowed, as `purge()` does
(`SeriesService.php:285-298`), so a creator who asked for a removal gets one.

**Both cards are components, mounted once each.** `ChatCard.vue` (the panel,
the rows, the expired notice) and `ChatForm.vue` (add and edit, one form) on
the creator's page after the `series-details` Panel and before `#progress`;
`PeerChatCard.vue` on the Peer's page after the progress block and before the
Episodes Panel, because the access email of `T-136` points at `#chat` and a
newly admitted Peer wants the chat before the first Episode. Every sentence
reaches Vue as a prop from lang; the platform names extend `D-016`'s exception
as `D-025` and `D-029` allow, and `ChatPlatform::labelKey()` holds a lang key,
never English.

**"I've joined" is the browser's memory and nothing else.** Nothing reads it —
no email, no report, no reconciliation — so a Peer-scoped row would be state to
purge and to sync for no reader. `localStorage`, wrapped in `try`/`catch`, and
the card renders correctly without it.

**`group_id` is set from the Series on create, and every read the service
makes is `forGroup($series->group_id)`.** The creator route runs inside
`group` middleware and `BelongsToGroup` would stamp it anyway
(`app/Concerns/BelongsToGroup.php:24-28`), but the global `GroupScope` throws
with no current Group (`app/Models/Scopes/GroupScope.php:22-25`), so a service
that stamped the id and then counted through a bare `SeriesChat::query()`
would still need one. `add()`'s position count, `guardLimit()`,
`chatOrFail()`, `purgeFor()`, `open()` and `removeCode()` all read
`forGroup()`, as `Group::seriesUsed()` does for the over-cap guard
(`app/Models/Group.php:278-286`), which is what lets `purgeFor()` run from
`qori:series:purge` with no current Group and a future command add a chat with
none. The tinker recipe sets one in its Setup (`docs/tinker/uploads.md:20`)
and does not depend on this.

**Add, edit and remove are behind the over-cap lock, as Episodes are.**
`guardSeriesUnlocked()` on all three (`app/Concerns/LocksOverCapSeries.php`);
the page passes `lock.active` as `disabled`.

**The tests are two files, one per surface.** The layout puts Peer-surface
tests under `tests/Feature/Shared/` and creator-side ones under
`tests/Feature/Series/`; the brief named one file, and the total is what a
reviewer counts.

## Preconditions

**Data this task verifies against:** a clean database. The feature tests build
a Series through `SeriesService::create()` and grant access through
`AccessService::grant()` as `tests/Feature/Access/SharedRoutesTest.php:27-35`
does; a code image is a `MediaAsset::factory()->stored()` row with purpose
`chat_code`, extension `png` and a `chat-codes/…` key, with an object put on
`Storage::fake()` the way `tests/Feature/Series/DeleteSeriesTest.php:65-80`
puts one.

**Equipment:** a visible browser, to see the two cards, the new tab a code
opens in, and "I've joined" collapsing the card on that browser only. Nothing
vendor-facing: Qori calls no chat vendor (`D-029`), so there is no payload to
cite, no spike owed and no fixture.

## Scope

**In:**

- `series_chats`, `SeriesChat`, `ChatPlatform`, `MediaAssetPurpose::ChatCode`,
  `SeriesChatService` with add, update, remove, `purgeFor()` and `open()`.
- The creator's three routes, `ChatController`, `StoreChatRequest` and
  `UpdateChatRequest`, and the `chat_code` rule in `SignUploadRequest`.
- `ChatCard.vue` and `ChatForm.vue` on `share/series/Show.vue`, with the
  platform picker, the link-or-code switch, the expiry date — offered for a
  code only — with WeChat's help line, the note, and the expired notice.
- `shared.chats.open` and `OpenChatController`: the access gate, the
  `access_opens` row with target `chat`, the redirect to the invite or to the
  signed image, and the return to `#chat` with a toast once expired.
- `PeerChatCard.vue` on `shared/Show.vue` at `id="chat"`, with "I've joined".
- `SeriesService::purge()` deleting the rows and their images.
- `lang/en/chats.php`, the `chats` group in `errors.php`, three flashes in
  `series.php`; `docs/flows/chats.md` and its README row; the upload recipe;
  a factory and one seeded chat for the design-review world.

**Out:**

- Who opened the chat card on the creator's Peer list. `D-029` says the list
  shows it; the brief keeps it out of this task, which writes the
  `access_opens` rows and reads none back — see the last section.
- The access email's "Join the class chat from the :title page" line
  (`T-136`), and "Copy message for your chat" (`T-135`).
- Several chats on one Series: `position` is stored, the cap is 1, and the
  page shows one card.
- Any chat API, bot, `wa.me` share link or message Qori sends; any
  `app/Integrations` folder for a chat platform (`D-029`).
- Telegram, Discord, Slack, LINE and Signal as named platforms: `D-029` keeps
  four cases, and "Another app" covers the rest with no vendor name.
- A server-side record of "I've joined", or any reconciliation of who is in
  the chat; removal is by hand.
- The help line about a WeChat group over 200 members refusing its code, until
  the fact is confirmed (last section).
- Series-level materials and their list above the Episodes (`T-137`), and the
  Series total (`T-139`).

## Files

| Path                                                            | Change | Notes                                                                                                                                      |
| --------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `database/migrations/2026_09_18_000500_create_series_chats.php` | new    | The table, the index, the `series_chats_one_way_in` check                                                                                  |
| `app/Models/SeriesChat.php`                                     | new    | `HasUlids`, `BelongsToGroup`; `isCode()`, `isExpired()`                                                                                    |
| `app/Enums/ChatPlatform.php`                                    | new    | Four cases; `labelKey()`                                                                                                                   |
| `app/Enums/MediaAssetPurpose.php`                               | edit   | `ChatCode = 'chat_code'` beside `T-130`'s `Material`                                                                                       |
| `app/Services/SeriesChatService.php`                            | new    | The constants, add/update/remove, `purgeFor()`, `open()`, the guards                                                                       |
| `app/Services/SeriesService.php`                                | edit   | `purge()` calls `SeriesChatService::purgeFor()`; the constructor gains it beside whatever `T-130` added                                    |
| `app/Http/Requests/Share/StoreChatRequest.php`                  | new    | The rules, the way-in check, the expiry-needs-a-code check, the code check, `chatAttributes()`                                             |
| `app/Http/Requests/Share/UpdateChatRequest.php`                 | new    | `extends StoreChatRequest`; the edit form posts the whole row                                                                              |
| `app/Http/Requests/Share/SignUploadRequest.php`                 | edit   | For purpose `chat_code`: `extension` in `CODE_EXTENSIONS`, `size` at most the cap                                                          |
| `app/Http/Controllers/Share/ChatController.php`                 | new    | `store`, `update`, `destroy`; only delegates                                                                                               |
| `app/Http/Controllers/Share/SeriesController.php`               | edit   | `chats` and `chatForm` props on `show()`                                                                                                   |
| `app/Http/Controllers/Shared/OpenChatController.php`            | new    | 302 to the invite or the image; expired → `shared.show#chat` with a toast                                                                  |
| `app/Http/Controllers/Shared/SharedController.php`              | edit   | `chat` prop on `show()`, built by `chatCard()`                                                                                             |
| `routes/share/series.php`                                       | edit   | `share.series.chats.store`, `.update`, `.destroy`                                                                                          |
| `routes/shared.php`                                             | edit   | `shared.chats.open`, beside `T-131`'s `shared.materials.open`                                                                              |
| `resources/js/components/series/ChatCard.vue`                   | new    | Creator: the panel, the rows, edit and remove, the expired notice, the add form under the cap                                              |
| `resources/js/components/series/ChatForm.vue`                   | new    | Creator: one form for add and edit; platform, way in, link or `FileUpload`, expiry, note                                                   |
| `resources/js/components/series/PeerChatCard.vue`               | new    | Peer: `id="chat"`, the action link, the expiry line, "I've joined" in `localStorage`                                                       |
| `resources/js/pages/share/series/Show.vue`                      | edit   | Mounts `ChatCard` after `#series-details`; `chats` and `chatForm` in the props type                                                        |
| `resources/js/pages/shared/Show.vue`                            | edit   | Mounts `PeerChatCard` between progress and the Episodes; `chat` in the props type                                                          |
| `lang/en/chats.php`                                             | new    | Platform names, the form, the creator's lines, the Peer's card                                                                             |
| `lang/en/errors.php`                                            | edit   | The `chats` group                                                                                                                          |
| `lang/en/series.php`                                            | edit   | `chat_added`, `chat_updated`, `chat_removed`                                                                                               |
| `database/factories/SeriesChatFactory.php`                      | new    | `forSeries()`, `code()`                                                                                                                    |
| `database/seeders/DesignReviewSeeder.php`                       | edit   | One WhatsApp link on the shared Series, so the designer's screenshots carry the card; `wipe()` deletes it by prefix before the Series rows |
| `docs/flows/chats.md`                                           | new    | Shape, adding, opening, expiry, purge                                                                                                      |
| `docs/flows/README.md`                                          | edit   | The `chats.md` row                                                                                                                         |
| `docs/tinker/uploads.md`                                        | edit   | "Attach it to a chat" after the Episode recipe; `chat-codes` in Clean up                                                                   |
| `tests/Feature/Series/SeriesChatTest.php`                       | new    | 14 cases: the creator's side and purge                                                                                                     |
| `tests/Feature/Shared/OpenChatTest.php`                         | new    | 12 cases: the Peer's card and route                                                                                                        |

No `config/qori.php` row: `qori.chats.per_series`, `qori.chats.code_max_mb`
and `storage.live_prefix.chat_code` are declared by `T-123`, and this task
reads them. `qori:reachability` sees `shared.chats.open` through the `route()`
call in `SharedController` and `OpenChatController`, because its haystack
includes the PHP files (`app/Support/Reachability.php:194-201`).

## Database

| Table          | Column           | Type         | Null | Default | Index / constraint                                                           |
| -------------- | ---------------- | ------------ | ---- | ------- | ---------------------------------------------------------------------------- |
| `series_chats` | `id`             | ulid         | no   | —       | primary                                                                      |
| `series_chats` | `group_id`       | ulid         | no   | —       | FK `groups`, cascade on delete                                               |
| `series_chats` | `series_id`      | ulid         | no   | —       | FK `series`, cascade on delete                                               |
| `series_chats` | `position`       | integer      | no   | —       | index `(group_id, series_id, position)`                                      |
| `series_chats` | `platform`       | string       | no   | —       | a `ChatPlatform` value                                                       |
| `series_chats` | `url`            | string(2048) | yes  | null    | check `series_chats_one_way_in`: `(url IS NULL) <> (media_asset_id IS NULL)` |
| `series_chats` | `media_asset_id` | ulid         | yes  | null    | FK `media_assets`, null on delete                                            |
| `series_chats` | `expires_on`     | date         | yes  | null    |                                                                              |
| `series_chats` | `note`           | string(300)  | yes  | null    |                                                                              |
| `series_chats` | `created_at`     | timestamp    | yes  | null    |                                                                              |
| `series_chats` | `updated_at`     | timestamp    | yes  | null    |                                                                              |

Migration: `database/migrations/2026_09_18_000500_create_series_chats.php`

```php
Schema::create('series_chats', function (Blueprint $table): void {
    $table->ulid('id')->primary();
    $table->foreignUlid('group_id')->constrained()->cascadeOnDelete();
    $table->foreignUlid('series_id')->constrained()->cascadeOnDelete();
    $table->integer('position');
    $table->string('platform');
    $table->string('url', 2048)->nullable();
    $table->foreignUlid('media_asset_id')->nullable()->constrained('media_assets')->nullOnDelete();
    $table->date('expires_on')->nullable();
    $table->string('note', 300)->nullable();
    $table->timestamps();
    $table->index(['group_id', 'series_id', 'position']);
});

// Exactly one way in, in the shape series_price_has_currency uses.
DB::statement(
    'ALTER TABLE series_chats ADD CONSTRAINT series_chats_one_way_in '
    .'CHECK ((url IS NULL) <> (media_asset_id IS NULL))',
);

// down(): Schema::dropIfExists('series_chats');
```

## Code

```php
namespace App\Enums;

/**
 * Where a class chat lives (D-029). Four cases and "another app", because nine
 * platforms with identical behaviour is vocabulary without code. The names
 * reach Vue as props from lang/en/chats.php, never from here.
 */
enum ChatPlatform: string
{
    case WhatsApp = 'whatsapp';
    case WeChat = 'wechat';
    case WeCom = 'wecom';
    case Other = 'other';

    /** The lang key the picker and the card read the name from. */
    public function labelKey(): string;   // 'chats.platforms.'.$this->value
}

// App\Enums\MediaAssetPurpose gains, beside T-130's Material:
case ChatCode = 'chat_code';   // live prefix 'chat-codes', declared by T-123
```

```php
namespace App\Models;

use App\Concerns\BelongsToGroup;
use App\Enums\ChatPlatform;
use Carbon\CarbonImmutable;

/**
 * The invite to a Series' group chat: a link or a code image (D-029).
 *
 * @property string $group_id
 * @property string $series_id
 * @property int $position
 * @property ChatPlatform $platform
 * @property ?string $url
 * @property ?string $media_asset_id
 * @property ?CarbonImmutable $expires_on
 * @property ?string $note
 */
class SeriesChat extends Model
{
    use BelongsToGroup, HasFactory, HasUlids;

    protected $table = 'series_chats';

    /** @var list<string> */
    protected $fillable = ['group_id', 'series_id', 'position', 'platform', 'url', 'media_asset_id', 'expires_on', 'note'];

    // casts: platform => ChatPlatform::class, position => 'integer',
    //        series_id => 'string', media_asset_id => 'string', expires_on => 'immutable_date'

    /** @return BelongsTo<Series, $this> */
    public function series(): BelongsTo;

    /** @return BelongsTo<MediaAsset, $this> */
    public function code(): BelongsTo;   // belongsTo(MediaAsset::class, 'media_asset_id')

    public function isCode(): bool;      // $this->media_asset_id !== null

    /**
     * Expired from the first midnight after expires_on in the Group's zone.
     * A chat with no expiry never expires.
     */
    public function isExpired(CarbonImmutable $now): bool;
    // $this->expires_on !== null
    //     && $now->setTimezone($this->group?->timezone() ?? Timezones::fallback())->toDateString()
    //         > $this->expires_on->toDateString()
}
```

```php
namespace App\Services;

use App\Concerns\LocksOverCapSeries;
use App\Integrations\Contracts\SignsStoredFiles;

/**
 * A Series' class chat (D-029): what a creator adds, what a Peer opens.
 *
 * No vendor code. Qori stores a link or an image and follows neither; the one
 * contract it calls is SignsStoredFiles, for the image's signed URL.
 */
class SeriesChatService
{
    use LocksOverCapSeries;

    /** What a code image may be. Read by SignUploadRequest and guardCode(). */
    public const CODE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'webp'];

    /** How long a WeChat group code lasts, per WeChat's help page. The form pre-fills the expiry from it and the help line interpolates it. */
    public const WECHAT_CODE_DAYS = 7;

    /** The note column's length; the request's max and the textarea's maxlength both read it. */
    public const NOTE_MAX = 300;

    public function __construct(private SignsStoredFiles $files) {}

    /**
     * @param  array{platform: ChatPlatform, url: ?string, media_asset_id: ?string, expires_on: ?string, note: ?string}  $attributes
     */
    public function add(Series $series, array $attributes): SeriesChat;
    // guardSeriesUnlocked($series->group, 'add a chat'); guardLimit($series); guardWayIn($attributes);
    // media_asset_id set → guardCode($series->group, $attributes['media_asset_id']);
    // SeriesChat::create([... 'group_id' => $series->group_id, 'series_id' => $series->getKey(),
    //     'position' => SeriesChat::query()->forGroup($series->group_id)->where('series_id', $series->getKey())->count() + 1]);

    /** @param array{platform: ChatPlatform, url: ?string, media_asset_id: ?string, expires_on: ?string, note: ?string} $attributes */
    public function update(Series $series, string $chatId, array $attributes): SeriesChat;
    // guardSeriesUnlocked($series->group, 'edit a chat'); $chat = $this->chatOrFail($series, $chatId); guardWayIn($attributes);
    // $incoming = $attributes['media_asset_id'];
    // $incoming !== null && $incoming !== $chat->media_asset_id → guardCode($series->group, $incoming);
    // $replaced = $chat->isCode() && $incoming !== $chat->media_asset_id;   // a new code, or a code dropped for a link
    // DB::transaction(function () use ($chat, $attributes, $replaced): void {
    //     $old = $replaced ? $this->removeCode($chat) : null;   // 1. the old object goes
    //     $chat->fill($attributes)->save();                     // 2. the row now points at the new asset, or at none
    //     $old?->delete();                                      // 3. the old media_assets row, never before step 2
    // });

    public function remove(Series $series, string $chatId): void;
    // guardSeriesUnlocked($series->group, 'remove a chat'); $chat = $this->chatOrFail($series, $chatId);
    // DB::transaction(function () use ($chat): void {
    //     $asset = $chat->isCode() ? $this->removeCode($chat) : null;   // 1. the object goes
    //     $chat->delete();                                               // 2. the chat row
    //     $asset?->delete();                                             // 3. the media_assets row, never before step 2
    // });

    /**
     * Every chat of a Series and its image, for SeriesService::purge().
     * Reads with forGroup() because the sweep has no current Group.
     */
    public function purgeFor(Series $series): void;
    // SeriesChat::query()->forGroup($series->group_id)->where('series_id', $series->getKey())->get()
    //     ->each(function (SeriesChat $chat): void {
    //         $asset = $chat->isCode() ? $this->removeCode($chat) : null;   // the same three steps as remove()
    //         $chat->delete();
    //         $asset?->delete();
    //     });

    /**
     * The Peer's gate and their destination: the invite URL, the signed image
     * URL, or null when the code has expired. Records the open on either URL.
     *
     * @throws AppException forbidden with no active Access; notFound for a chat not on this Series
     */
    public function open(User $peer, string $seriesId, string $chatId, CarbonImmutable $now): ?string;
    // $access = Access::forUser($peer)->where('series_id', $seriesId)->first()
    //     ?? throw AppException::forbidden('errors.access.not_granted', devMessage: …);
    // $series = Series::findForPeer($seriesId) ?? throw AppException::notFound('errors.access.series_unavailable');
    // $chat = SeriesChat::query()->forGroup($series->group_id)->where('series_id', $series->getKey())->whereKey($chatId)->first()
    //     ?? throw AppException::notFound('errors.chats.not_found', devMessage: …);
    // if ($chat->isExpired($now)) { return null; }
    // $to = $chat->url;
    // if ($to === null) {
    //     $asset = MediaAsset::query()->forGroup($series->group_id)->whereKey($chat->media_asset_id)->first();
    //     if (! $asset instanceof MediaAsset || ! $asset->isStored() || $asset->key === null) {
    //         throw AppException::notFound('errors.chats.not_found', devMessage: 'Code asset missing or not stored.');
    //     }
    //     $to = $this->files->temporaryLink($asset->key, MediaLifetime::minutesForExtension($asset->extension))->url;
    // }
    // AccessOpen::record($access, OpenTarget::Chat, null, (string) $chat->getKey());   // only once there is a URL to follow
    // return $to;

    /** Read as SeriesChatService::codeMaxBytes() by SignUploadRequest, StoreChatRequest and guardCode(); static so a request needs no service. */
    public static function codeMaxBytes(): int;   // (int) config('qori.chats.code_max_mb') * 1024 * 1024

    private function chatOrFail(Series $series, string $chatId): SeriesChat;
    // SeriesChat::query()->forGroup($series->group_id)->where('series_id', $series->getKey())->whereKey($chatId)->first()
    //     ?? throw AppException::notFound('errors.chats.not_found', devMessage: …)

    private function guardLimit(Series $series): void;
    // SeriesChat::query()->forGroup($series->group_id)->where('series_id', $series->getKey())->count()
    //     >= (int) config('qori.chats.per_series') → AppException::invalidRequest('errors.chats.limit',
    //     app(Terminology::class)->for($series->group)->replacements(), devMessage: …)

    private function guardWayIn(array $attributes): void;
    // exactly one of url / media_asset_id, else invalidRequest('errors.chats.way_in_required' | 'errors.chats.one_way_in');
    // expires_on with url → invalidRequest('errors.chats.expiry_needs_code')

    private function guardCode(?Group $group, string $assetId): MediaAsset;
    // MediaAsset::query()->forGroup($group)->find($assetId): must exist, isStored(), purpose ChatCode,
    // extension in CODE_EXTENSIONS, size_bytes <= self::codeMaxBytes(); else invalidRequest('errors.chats.code_invalid', ['mb' => config…])

    /**
     * The object behind a code, deleted; the asset row is handed back for the
     * caller to delete after the chat row. Called only when $chat->isCode().
     * forGroup(), not the $chat->code relation: MediaAsset is BelongsToGroup
     * and purgeFor() runs with no current Group (the trap T-131's
     * storedAsset() names).
     */
    private function removeCode(SeriesChat $chat): ?MediaAsset;
    // $asset = MediaAsset::query()->forGroup($chat->group_id)->whereKey($chat->media_asset_id)->first();
    // if ($asset === null) { Log::warning('Chat code asset missing', ['chat' => $chat->getKey()]); return null; }   // nothing to delete; the chat row still goes
    // if ($asset->isStored() && $asset->key !== null) {                        // a pending asset has no object: skip the delete, still hand the row back
    //     try { Storage::disk((string) config('qori.storage.disk'))->delete($asset->key); }
    //     catch (Throwable $e) { report($e); }                                 // logged and swallowed, as purge() does
    // }
    // return $asset;
}
```

```php
// App\Services\SeriesService — purge(), after the material objects T-130 removes and before the Episodes go:
$this->chats->purgeFor($series);
// constructor: public function __construct(private SeriesChatService $chats, …T-130's dependency…) {}
```

```php
namespace App\Http\Requests\Share;

class StoreChatRequest extends FormRequest
{
    // rules():
    //   'platform'       => ['required', Rule::enum(ChatPlatform::class)],
    //   'url'            => ['nullable', 'string', 'url:https', 'max:2048'],   // D-025: https, at most 2048
    //   'media_asset_id' => ['nullable', 'string'],
    //   'expires_on'     => ['nullable', 'date_format:Y-m-d'],
    //   'note'           => ['nullable', 'string', 'max:'.SeriesChatService::NOTE_MAX],
    //
    // withValidator(): neither url nor media_asset_id → errors on 'url' with __('errors.chats.way_in_required.message');
    //   both → 'url' with __('errors.chats.one_way_in.message');
    //   url with expires_on → 'expires_on' with __('errors.chats.expiry_needs_code.message');
    //   media_asset_id → the asset must be found by MediaAsset::query()->find() (scoped), isStored(), purpose ChatCode,
    //   extension in SeriesChatService::CODE_EXTENSIONS, size_bytes <= SeriesChatService::codeMaxBytes(),
    //   else errors on 'media_asset_id' with __('errors.chats.code_invalid.message', ['mb' => config('qori.chats.code_max_mb')]).

    public function platform(): ChatPlatform;   // ChatPlatform::from((string) $this->input('platform'))

    /**
     * Not attributes(): FormRequest already owns that name for field labels.
     *
     * @return array{platform: ChatPlatform, url: ?string, media_asset_id: ?string, expires_on: ?string, note: ?string}
     */
    public function chatAttributes(): array;
}

/** The edit form posts the whole row, so the rules are the same. */
class UpdateChatRequest extends StoreChatRequest {}
```

```php
// App\Http\Requests\Share\SignUploadRequest — rules() gains, when purpose is chat_code:
'extension' => ['required', Rule::in(SeriesChatService::CODE_EXTENSIONS)],
'size' => ['required', 'integer', 'min:1', 'max:'.SeriesChatService::codeMaxBytes()],
// messages(): 'extension.in' for chat_code → __('errors.chats.code_invalid.resolution', ['mb' => …]);
//             'size.max' → __('errors.chats.code_invalid.message', ['mb' => …])
```

```php
namespace App\Http\Controllers\Share;

class ChatController extends Controller
{
    use ResolvesShareSeries;

    public function store(string $group, string $seriesId, StoreChatRequest $request, SeriesChatService $chats, Terminology $terminology): RedirectResponse;
    // $chats->add($this->seriesById($seriesId), $request->chatAttributes());
    // Inertia::flash('toast', ['type' => 'success', 'message' => $terminology->line('series.chat_added')]); return back();

    public function update(string $group, string $seriesId, string $chatId, UpdateChatRequest $request, SeriesChatService $chats, Terminology $terminology): RedirectResponse;
    // …update(…); flash series.chat_updated; back()

    public function destroy(string $group, string $seriesId, string $chatId, SeriesChatService $chats, Terminology $terminology): RedirectResponse;
    // …remove(…); flash series.chat_removed; back()
}
```

```php
// App\Http\Controllers\Share\SeriesController::show() — two more props:
'chats' => $this->chats($series),
'chatForm' => [
    'platforms' => array_map(fn (ChatPlatform $platform): array => [
        'value' => $platform->value,
        'label' => __($platform->labelKey()),
    ], ChatPlatform::cases()),
    'limit' => (int) config('qori.chats.per_series'),
    'noteMax' => SeriesChatService::NOTE_MAX,
    'codeMaxMb' => (int) config('qori.chats.code_max_mb'),
    'codeAccept' => implode(',', array_map(fn (string $ext): string => '.'.$ext, SeriesChatService::CODE_EXTENSIONS)),
    'wechatCodeDays' => SeriesChatService::WECHAT_CODE_DAYS,
    'copy' => [
        /* every chats.form.* line keyed by its last segment, through $terminology->line(); :mb, :days, :max filled from the values above */
        'limit' => $terminology->choice('chats.form.limit', $limit, ['count' => $limit]),
        'kinds' => ['link' => __('chats.kinds.link'), 'code' => __('chats.kinds.code')],
    ],
],

/** @return list<array<string, mixed>> */
private function chats(Series $series): array;
// SeriesChat::query()->where('series_id', $series->getKey())->orderBy('position')->get() — scoped by the middleware's Group
// each: ['id', 'platform' => value, 'platformLabel' => __($chat->platform->labelKey()), 'kind' => $chat->isCode() ? 'code' : 'link',
//        'url', 'codeName' => $chat->code?->name, 'expiresOn' => $chat->expires_on?->toDateString(),
//        'expired' => $chat->isExpired(CarbonImmutable::now()),
//        'expiresLine' => null | line('chats.form.expires', ['date' => …]) | line('chats.form.expired', ['date' => …]), 'note']
// — the date formatted 'j M Y', as deletionNotice() formats one
```

```php
namespace App\Http\Controllers\Shared;

class OpenChatController extends Controller
{
    public function __invoke(Request $request, string $seriesId, string $chatId, SeriesChatService $chats, Terminology $terminology): RedirectResponse;
    // $to = $chats->open(CurrentUser::orFail($request), $seriesId, $chatId, CarbonImmutable::now());
    //
    // if ($to === null) {                                                     // expired: back to the card (D-020)
    //     Inertia::flash('toast', [
    //         'type' => 'info',
    //         'message' => $terminology->line('chats.peer.expired_toast', [], Series::findForPeer($seriesId)?->group),
    //     ]);
    //
    //     return redirect()->to(route('shared.show', $seriesId).'#chat');
    // }
    //
    // return redirect()->away($to);
}
```

```php
// App\Http\Controllers\Shared\SharedController::show() — one more prop:
'chat' => $this->chatCard($model),

/** The one card, or null when the Series has no chat. @return ?array<string, mixed> */
private function chatCard(Series $series): ?array;
// $chat = SeriesChat::query()->forGroup($series->group_id)->where('series_id', $series->getKey())->orderBy('position')->first();
// null → null. $expired = $chat->isExpired(CarbonImmutable::now()); $t = app(Terminology::class); $g = $series->group;
// [
//     'id' => (string) $chat->getKey(),
//     'platform' => $chat->platform->value,
//     'kind' => $chat->isCode() ? 'code' : 'link',
//     'expired' => $expired,
//     'expiresOn' => $chat->expires_on?->toDateString(),
//     'note' => $chat->note,
//     'openUrl' => $expired ? null : route('shared.chats.open', ['seriesId' => $series->getKey(), 'chatId' => $chat->getKey()]),
//     'copy' => [
//         'eyebrow' => $chat->platform === ChatPlatform::Other
//             ? $t->line('chats.peer.eyebrow_other', [], $g)
//             : $t->line('chats.peer.eyebrow', ['platform' => __($chat->platform->labelKey())], $g),
//         'title' => $t->line('chats.peer.title', [], $g),
//         'intro' => $t->line($chat->isCode() ? 'chats.peer.intro_code' : 'chats.peer.intro_link', [], $g),
//         'action' => $t->line($chat->isCode() ? 'chats.peer.action_code' : 'chats.peer.action_link', [], $g),
//         'expires' => $chat->expires_on === null || $expired ? null : $t->line('chats.peer.expires', ['date' => $chat->expires_on->format('j M Y')], $g),
//         // a code's line only: a link never carries expires_on (the request and guardWayIn() refuse one)
//         'expired' => $t->line('chats.peer.expired', [], $g),
//         'joined' => …'chats.peer.joined', 'joinedDone' => …'chats.peer.joined_done', 'showAgain' => …'chats.peer.show_again',
//     ],
// ]
// The invite url is never in this array.
```

```ts
// resources/js/components/series/PeerChatCard.vue
interface PeerChat {
    id: string;
    platform: string; // a ChatPlatform value
    kind: 'link' | 'code';
    expired: boolean;
    expiresOn: string | null; // Y-m-d
    note: string | null;
    openUrl: string | null; // shared.chats.open; null once expired
    copy: {
        eyebrow: string;
        title: string;
        intro: string;
        action: string;
        expires: string | null;
        expired: string;
        joined: string;
        joinedDone: string;
        showAgain: string;
    };
}
defineProps<{ chat: PeerChat }>();
// Root: <Panel id="chat" :title="chat.copy.title" :description="chat.copy.eyebrow">.
// Not expired: intro, note, <a :href="chat.openUrl" target="_blank" rel="noopener">{{ chat.copy.action }}</a>,
//   the expires line, and a "I've joined" <button> that writes localStorage['qori.chat.joined.' + chat.id] = '1'
//   and collapses the body to joinedDone + a showAgain <button> that removes the key. Every read and write in try/catch.
// Expired: intro replaced by chat.copy.expired; no link, no button.

// resources/js/components/series/ChatCard.vue (creator)
interface CreatorChat {
    id: string;
    platform: string;
    platformLabel: string;
    kind: 'link' | 'code';
    url: string | null;
    codeName: string | null;
    expiresOn: string | null;
    expired: boolean;
    expiresLine: string | null;
    note: string | null;
}
interface ChatFormProps {
    platforms: { value: string; label: string }[];
    limit: number;
    noteMax: number;
    codeMaxMb: number;
    codeAccept: string;
    wechatCodeDays: number;
    copy: Record<string, string> & { kinds: { link: string; code: string } };
}
defineProps<{
    seriesId: string;
    groupSlug: string;
    chats: CreatorChat[];
    form: ChatFormProps;
    disabled: boolean;
}>();
// <Panel id="chat" :title="form.copy.title" :description="form.copy.intro">: one row per chat — platformLabel, the link
// or codeName, expiresLine as plain text, or <InlineNotice tone="warning"> when expired — with Edit (toggles a ChatForm
// in place, method patch) and Remove (<Form method="delete">); a ChatForm (method post) when chats.length < form.limit.
// Both controls take :disabled.

// resources/js/components/series/ChatForm.vue (creator)
defineProps<{
    action: string;
    method: 'post' | 'patch';
    chat: CreatorChat | null;
    form: ChatFormProps;
    groupSlug: string;
    disabled: boolean;
}>();
// <Form :action :method reset-on-success>: a <select name="platform"> from form.platforms; a radio pair name="kind"
// (form.copy.kinds); when link an <Input name="url">; when code
// <FileUpload purpose="chat_code" :group="groupSlug" :accept="form.codeAccept" :label="form.copy.code_label" @stored="assetId = $event.id" />
// with form.copy.code_help and <input type="hidden" name="media_asset_id" :value="assetId"> — the `stored` emit and the
// hidden field exactly as T-130's MaterialForm.vue reads them; when kind is code, and only then, an
// <Input name="expires_on" type="date"> labelled form.copy.expires_label with form.copy.expires_help, pre-filled with
// today + form.wechatCodeDays when platform is wechat and the field is empty; a <TextareaField name="note"
// :maxlength="form.noteMax">. Every label and help line from form.copy; no inline English.
```

`docs/flows/chats.md`: "Shape" (the table and the one-way-in rule), "Adding"
(the three creator routes, the sign-time rule, the guards), "Opening" (the
`shared.chats.open` chain, the `access_opens` row, the 302 to the invite or
the signed image, the expired return to `#chat`), "Expiry" (the day rule),
"Purge" (`purgeFor()` from `SeriesService::purge()`, object → row → asset
row). `docs/flows/README.md` gains the row beside `storage.md`.

`docs/tinker/uploads.md`: after "Attach it to an episode", "Attach it to a
chat" — `$uploads->sign($group, $user, 'group-code.png', 40_000,
App\Enums\MediaAssetPurpose::ChatCode)`, put bytes, confirm, then
`app(App\Services\SeriesChatService::class)->add($series, ['platform' =>
App\Enums\ChatPlatform::WeChat, 'url' => null, 'media_asset_id' =>
$asset->getKey(), 'expires_on' => now()->addDays(7)->toDateString(), 'note' =>
null])`; and `$disk->deleteDirectory('chat-codes')` in Clean up.

`database/factories/SeriesChatFactory.php`: definition `group_id` and
`series_id` from `forSeries(Series $series): static` (the factory refuses to
guess a Series, as `AccessFactory::forSeries()` is used), `position` 1,
`platform` `ChatPlatform::WhatsApp`, `url` `'https://chat.whatsapp.test/'.Str::random(22)`,
`media_asset_id` null, `expires_on` null, `note` null;
`code(MediaAsset $asset, ?string $expiresOn = null): static` sets `platform`
`WeChat`, `url` null, `media_asset_id` and `expires_on`.

`database/seeders/DesignReviewSeeder.php`, in `sharedSeries()`: one row with
`id` `self::id('CHAT0001')`, platform WhatsApp, a link, position 1,
`group_id` set explicitly as every seeded row is, and the note "Say hello and
tell us which room you're in." `wipe()` gains
`SeriesChat::query()->forGroup($groupId)->where('id', 'like', $prefix)->delete();`
inside its per-Group loop, before the `Series` line (`:247`), because the
seeder's rule is child-first and nothing there relies on cascade (`:231-235`);
the prefix match reaches `CHAT0001` as it reaches every other seeded id.

## Copy

| Key                                      | File                 | English                                                                                                                             |
| ---------------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `chats.platforms.whatsapp`               | `lang/en/chats.php`  | WhatsApp                                                                                                                            |
| `chats.platforms.wechat`                 | `lang/en/chats.php`  | WeChat                                                                                                                              |
| `chats.platforms.wecom`                  | `lang/en/chats.php`  | WeCom                                                                                                                               |
| `chats.platforms.other`                  | `lang/en/chats.php`  | Another app                                                                                                                         |
| `chats.kinds.link`                       | `lang/en/chats.php`  | An invite link                                                                                                                      |
| `chats.kinds.code`                       | `lang/en/chats.php`  | A QR code image                                                                                                                     |
| `chats.form.title`                       | `lang/en/chats.php`  | Class chat                                                                                                                          |
| `chats.form.intro`                       | `lang/en/chats.php`  | The group chat your :peer_plural talk in. Only :peer_plural with access to this :series see it, and Qori never posts into it.       |
| `chats.form.platform_label`              | `lang/en/chats.php`  | Where the chat is                                                                                                                   |
| `chats.form.kind_label`                  | `lang/en/chats.php`  | How people get in                                                                                                                   |
| `chats.form.url_label`                   | `lang/en/chats.php`  | Invite link                                                                                                                         |
| `chats.form.url_help`                    | `lang/en/chats.php`  | Paste the group's own invite link. It has to start with https.                                                                      |
| `chats.form.code_label`                  | `lang/en/chats.php`  | Code image                                                                                                                          |
| `chats.form.code_help`                   | `lang/en/chats.php`  | PNG, JPG or WebP, up to :mb MB.                                                                                                     |
| `chats.form.expires_label`               | `lang/en/chats.php`  | Code expires on                                                                                                                     |
| `chats.form.expires_help`                | `lang/en/chats.php`  | A WeChat group code lasts :days days. Enter the date printed under it, and this page will tell you when to replace it.              |
| `chats.form.note_label`                  | `lang/en/chats.php`  | A line for your :peer_plural                                                                                                        |
| `chats.form.note_help`                   | `lang/en/chats.php`  | Shown on their card. Up to :max characters.                                                                                         |
| `chats.form.add`                         | `lang/en/chats.php`  | Add the chat                                                                                                                        |
| `chats.form.save`                        | `lang/en/chats.php`  | Save                                                                                                                                |
| `chats.form.edit`                        | `lang/en/chats.php`  | Edit                                                                                                                                |
| `chats.form.cancel`                      | `lang/en/chats.php`  | Cancel                                                                                                                              |
| `chats.form.remove`                      | `lang/en/chats.php`  | Remove                                                                                                                              |
| `chats.form.limit`                       | `lang/en/chats.php`  | {1} One chat per :series for now.\|[2,\*] Up to :count chats per :series.                                                           |
| `chats.form.expires`                     | `lang/en/chats.php`  | Expires :date.                                                                                                                      |
| `chats.form.expired`                     | `lang/en/chats.php`  | This code expired on :date. Your :peer_plural can't join from it — replace it with a new one.                                       |
| `chats.peer.eyebrow`                     | `lang/en/chats.php`  | :platform group                                                                                                                     |
| `chats.peer.eyebrow_other`               | `lang/en/chats.php`  | Group chat                                                                                                                          |
| `chats.peer.title`                       | `lang/en/chats.php`  | Join the class chat                                                                                                                 |
| `chats.peer.intro_link`                  | `lang/en/chats.php`  | The :peer_plural on this :series talk here. Open the invite and ask to join, and say who you are so whoever runs it can let you in. |
| `chats.peer.intro_code`                  | `lang/en/chats.php`  | The :peer_plural on this :series talk here. Open the code and scan it from your phone, or save the image and open it from the app.  |
| `chats.peer.action_link`                 | `lang/en/chats.php`  | Join the chat                                                                                                                       |
| `chats.peer.action_code`                 | `lang/en/chats.php`  | Show the code                                                                                                                       |
| `chats.peer.expires`                     | `lang/en/chats.php`  | The code works until :date.                                                                                                         |
| `chats.peer.expired`                     | `lang/en/chats.php`  | This code has expired. Check back here for a new one.                                                                               |
| `chats.peer.joined`                      | `lang/en/chats.php`  | I've joined                                                                                                                         |
| `chats.peer.joined_done`                 | `lang/en/chats.php`  | You've joined this chat.                                                                                                            |
| `chats.peer.show_again`                  | `lang/en/chats.php`  | Show it again                                                                                                                       |
| `chats.peer.expired_toast`               | `lang/en/chats.php`  | That code has expired. Check here for a new one.                                                                                    |
| `errors.chats.limit.message`             | `lang/en/errors.php` | This :series already has as many chats as it can hold.                                                                              |
| `errors.chats.limit.resolution`          | `lang/en/errors.php` | Edit the one that is there, or remove it and add another.                                                                           |
| `errors.chats.not_found.message`         | `lang/en/errors.php` | We couldn't find that chat.                                                                                                         |
| `errors.chats.not_found.resolution`      | `lang/en/errors.php` | It may have been removed — reload the page.                                                                                         |
| `errors.chats.way_in_required.message`   | `lang/en/errors.php` | Add an invite link or a code image.                                                                                                 |
| `errors.chats.one_way_in.message`        | `lang/en/errors.php` | Give an invite link or a code image, not both.                                                                                      |
| `errors.chats.expiry_needs_code.message` | `lang/en/errors.php` | A date goes with a code image. An invite link has none — remove the date, or add the code instead.                                  |
| `errors.chats.code_invalid.message`      | `lang/en/errors.php` | That image can't be used as the code.                                                                                               |
| `errors.chats.code_invalid.resolution`   | `lang/en/errors.php` | Upload a PNG, JPG or WebP under :mb MB, chosen here as the code image.                                                              |
| `series.chat_added`                      | `lang/en/series.php` | Chat added. :peer_plural with access can find it on the :series page.                                                               |
| `series.chat_updated`                    | `lang/en/series.php` | Chat saved.                                                                                                                         |
| `series.chat_removed`                    | `lang/en/series.php` | Chat removed.                                                                                                                       |

`chats.form.*` and `chats.peer.*` carry nouns and go through
`Terminology::line()` — the creator's with the current Group, the Peer's with
the Series' Group passed explicitly, because the Peer surface has no current
Group. `chats.form.limit` is a `trans_choice` line through
`Terminology::choice()` with the configured cap as its count, so the number is
never written into it. `errors.chats.limit` carries `:series`, so its throw
passes `Terminology::for($group)->replacements()`, as
`EpisodeService.php:90-97` does for `timezone_required`; the other error lines
carry no noun. `:mb`, `:days`, `:max` and `:count` come from
`qori.chats.code_max_mb`, `WECHAT_CODE_DAYS`, `NOTE_MAX` and
`qori.chats.per_series`. The platform names are the vendor names `D-025` and
`D-029` allow, and `chats.form.expires_help` names WeChat inside the same
exception: it states WeChat's own rule, is shown beside the picker where the
creator has just chosen the platform, and is the one line outside the picker
and the card that carries a vendor name; `chats.peer.eyebrow` never puts an
article before `:platform`,
and `Other` takes `eyebrow_other` so "Another app group" is never rendered. No
line under `chats.*` says "live now", "has ended", "on its way" or
"processing".

## Routes

| Verb   | Path                                          | Name                         | Action                                |
| ------ | --------------------------------------------- | ---------------------------- | ------------------------------------- |
| POST   | `/g/{group}/series/{seriesId}/chats`          | `share.series.chats.store`   | `Share\ChatController::store`         |
| PATCH  | `/g/{group}/series/{seriesId}/chats/{chatId}` | `share.series.chats.update`  | `Share\ChatController::update`        |
| DELETE | `/g/{group}/series/{seriesId}/chats/{chatId}` | `share.series.chats.destroy` | `Share\ChatController::destroy`       |
| GET    | `/shared/{seriesId}/chats/{chatId}/open`      | `shared.chats.open`          | `Shared\OpenChatController::__invoke` |

The three creator routes sit in `routes/share/series.php` after the accesses
pair (`:59-62`), inside the `share.` group with prefix `g/{group}`; ids
throughout, because every one mutates. The Peer route sits in
`routes/shared.php` inside the `auth`, `verified`, `shared.` group (`:31-34`),
beside `T-131`'s `shared.materials.open`; it has more segments than the
`{series}` page route (`:38`), so the two cannot collide.

## Tests

**New: `tests/Feature/Series/SeriesChatTest.php` — 14 cases** (`setUp` builds
a creator, a `start` Group, an owner Collaborator and a Series, as
`tests/Feature/Series/EpisodeRoutesTest.php:35-55` does; a `storedCode(Group,
array $overrides = [])` helper makes a `MediaAsset::factory()->stored()` row
with purpose `ChatCode`, extension `png`, mime `image/png`, `size_bytes` 1024
and a `chat-codes/{group}/{ulid}.png` key, and puts bytes at that key on
`Storage::fake()`)

1. `test_a_creator_adds_an_invite_link` — POST `share.series.chats.store` with
   platform `whatsapp` and an https url; one row with `position` 1,
   `group_id` the Group's, `media_asset_id` null; the toast is
   `series.chat_added`.
2. `test_a_creator_adds_a_code_image` — POST with platform `wechat`,
   `media_asset_id` from `storedCode()` and `expires_on`; the row references
   the asset, `url` null, `expires_on` stored as the date given.
3. `test_exactly_one_way_in_is_required` — POST with neither → session error
   on `url`; POST with both → session error on `url`; POST with a link and an
   `expires_on` → session error on `expires_on`; no row any time.
4. `test_a_second_chat_is_refused_by_the_cap` — through
   `SeriesChatService::add()` after one row: `AppException` whose
   `errorCode()` is `ErrorCode::InvalidRequest` and whose `publicMessage()`
   is `errors.chats.limit.message` with the Group's `:series`.
5. `test_only_a_stored_chat_code_image_in_this_group_can_be_a_code` — four
   POSTs, each a session error on `media_asset_id` and no row: an asset with
   purpose `episode`; a pending asset; a `png` with `size_bytes` one over
   `codeMaxBytes()`; another Group's asset.
6. `test_signing_a_code_refuses_a_document_and_an_oversized_file` —
   `share.uploads.sign` with `purpose` `chat_code`: `notes.pdf` → 422 on
   `extension`; `big.png` with `size` one over the cap → 422 on `size`;
   `small.png` at 1024 → 200 with a pending row of purpose `chat_code`.
7. `test_a_creator_edits_the_expiry_and_the_note` — PATCH
   `share.series.chats.update` with the same `media_asset_id`, a new
   `expires_on` and a note; both stored, the asset untouched; the toast is
   `series.chat_updated`.
8. `test_replacing_or_dropping_a_code_deletes_the_old_image` —
   `Storage::fake()`; PATCH with a second `storedCode()` → the first key is
   missing, its `media_assets` row gone, the row references the second; then
   PATCH to a link → `media_asset_id` null and the second key missing.
9. `test_removing_a_chat_deletes_its_image` — `Storage::fake()`; DELETE →
   no row, the key missing, the asset row gone; the toast is
   `series.chat_removed`.
10. `test_a_slug_on_a_chat_action_does_not_resolve` — POST to
    `/g/{group}/series/{slug}/chats` → 404 from
    `ResolvesShareSeries::orNotFound()`, and no row;
    `tests/Feature/Series/ShareSeriesRoutesTest.php:143` covers the same rule
    by asserting the state did not change.
11. `test_the_over_cap_lock_refuses_chat_changes` — a Group over its cap
    (`tests/Feature/Series/OverCapLockTest.php:59-71`): `add()`, `update()`
    and `remove()` each throw `PlanLimitReached` with
    `errors.series.locked_over_cap`.
12. `test_the_creator_page_lists_the_chat_with_its_platform_name` —
    `share.series.show`: `chats.0.platformLabel` is
    `__('chats.platforms.wechat')`, `chats.0.kind` is `code`,
    `chatForm.platforms` has four entries, `chatForm.limit` equals
    `config('qori.chats.per_series')`, and `chatForm.copy.expires_help`
    contains `WECHAT_CODE_DAYS`.
13. `test_the_creator_is_told_when_a_code_has_expired` — `expires_on`
    yesterday in the Group's zone → `chats.0.expired` true and
    `chats.0.expiresLine` is `chats.form.expired` with that date; a code
    expiring today → `expired` false.
14. `test_purging_a_series_deletes_the_chat_and_its_image` —
    `Storage::fake()`; request deletion, travel past
    `SeriesService::DELETE_AFTER_DAYS`, run `qori:series:purge`: the row is
    gone (`SeriesChat::query()->forGroup($group)->count()` is 0), the key
    missing, the asset row gone, the Series purged.

**New: `tests/Feature/Shared/OpenChatTest.php` — 12 cases** (a
`publishedSeries()` helper as `SharedRoutesTest.php:27-35`, a
`chatOn(Series, array $attributes = [])` helper through
`SeriesChat::factory()->forSeries()`)

1. `test_a_peer_with_access_sees_the_chat_card` — `shared.show`: `chat.id`,
   `chat.kind` `link`, `chat.expired` false, `chat.openUrl` equal to
   `route('shared.chats.open', …)`, `chat.copy.title`; the prop has no `url`
   key and the response body does not contain the invite URL.
2. `test_an_expired_code_is_hidden_on_the_peer_page` — a `code()` chat with
   `expires_on` yesterday → `chat.expired` true, `chat.openUrl` null,
   `chat.copy.expires` null.
3. `test_a_series_without_a_chat_has_no_card` — `chat` is null.
4. `test_opening_the_link_redirects_and_logs_the_open` — GET
   `shared.chats.open` → 302 whose `Location` is the invite URL; one
   `access_opens` row with `target` `chat`, `subject_id` the chat id,
   `episode_id` null, `access_id` the Peer's and `group_id` the Access's.
5. `test_opening_a_code_redirects_to_its_image_link` — a `code()` chat on a
   stored asset → 302 whose `Location` contains the asset's key (a plain URL
   on the local disk, signed in production, as `T-089`'s Notes say); one
   `access_opens` row.
6. `test_opening_an_expired_code_returns_to_the_series_page` — 302 to
   `route('shared.show', $seriesId).'#chat'`; the session flash is an `info`
   toast whose message is `chats.peer.expired_toast`, read with a
   `toastContains()` helper as
   `tests/Feature/Access/SeriesAccessCodeTest.php:87-90` reads one; no
   `access_opens` row.
7. `test_someone_without_access_gets_a_forbidden_page` — 403; sees
   `errors.access.not_granted.message`; no `access_opens` row.
8. `test_a_revoked_access_gets_a_forbidden_page` — `AccessService::revoke()`
   then 403.
9. `test_a_chat_on_another_creators_series_is_not_found` — a Peer with access
   to Series A, a chat on Series B in another Group: GET
   `/shared/{A}/chats/{chatB}/open` → 404, GET `/shared/{B}/chats/{chatB}/open`
   → 403; no `access_opens` row either way.
10. `test_a_guest_is_sent_to_sign_in` — redirect to the sign-in page.
11. `test_the_public_page_never_carries_the_chat` — `series.public` for a
    Series with a chat: the props have no `chat` key and the body contains
    neither the invite URL nor `/chats/` (owner acceptance 11, `D-024`).
12. `test_a_renamed_vocabulary_reaches_the_card` — an entitled Group with
    custom labels, set up as `tests/Feature/TerminologyTest.php:85-97` does:
    `chat.copy.intro` contains the Group's own Series word and never
    "Series".

**Changed:** none. `tests/Feature/Share/UploadTest.php` signs with no
`purpose`, so the `chat_code` rule does not reach it;
`tests/Feature/DesignReviewFixtureTest.php:99-115` counts Series, Peers,
Accesses, Users, Staff and Groups and not chats;
`tests/Feature/Admin/ConsoleAccessTest.php` sees no new `->acrossAllGroups(`
caller; `ReachabilityTest` finds the new route by name in the controllers.

Total: 26 new cases.

## Acceptance

- [ ] A creator on the Series page adds a WhatsApp invite link, or a WeChat
      code image with the date printed under it, sees it listed with its
      platform name, and is not offered a second one
- [ ] A Peer with access finds the card at `#chat` above the Episodes, follows
      "Join the chat" to the invite or "Show the code" to the image in a new
      tab, and "I've joined" collapses the card on that browser only
- [ ] After the date under the code the Peer's card hides the code and says
      so, the creator's page asks for a new one, and a stale "Show the code"
      link lands on `#chat` with the toast — never a blank tab
- [ ] The invite link and the image URL appear in no page prop and nowhere on
      the public page; no access, a revoked Access and another creator's chat
      id meet 403, 403 and 404 (owner acceptance 11)
- [ ] Every open is one `access_opens` row with target `chat` and the
      Access's `group_id`, and an expired code writes none
- [ ] Removing a chat, replacing its code and purging the Series each delete
      the image and its `media_assets` row, with the chat row gone first
- [ ] A photo over `qori.chats.code_max_mb` or a PDF is refused when the
      upload is signed, and a note over `NOTE_MAX` is refused with the same
      number the textarea shows
- [ ] The platform names reach the picker and the card from
      `lang/en/chats.php`, and a Group with its own vocabulary reads its own
      nouns on both cards
- [ ] `docs/flows/chats.md` describes the chain and `docs/flows/README.md`
      lists it; the upload recipe attaches a code and cleans it up
- [ ] Every box above ticked, `status: done` and `owner:` set in the front matter
- [ ] `php artisan qori:tasks --check` passes
- [ ] `npm run check:fix` run, then `composer ci:check` green from a clean tree
- [ ] Report written in `reports/` (see [its README](reports/README.md))

## Before this can be ready

- `T-131` `ready`, so the names this task calls are frozen:
  `SignsStoredFiles`, `MediaLifetime::minutesForExtension()`, and through it
  `T-125`'s `AccessOpen::record()` and `OpenTarget::Chat` — the stream
  owner's. `T-130` is `ready`, so `MediaAssetPurpose::Material` beside
  `ChatCode` and `FileUpload.vue`'s `stored` emit are settled and this task
  reads them as written there.
- Whether the creator's Peer list showing who opened the chat card belongs
  here or in a task of its own: `D-029` says the list shows it and the brief
  keeps it out of this task; the `access_opens` rows are written here and
  nothing in the sprint reads them — the owner's.
- ~~Exactly one way in, as this draft reads `D-029`'s "one of `url` or
  `media_asset_id` required", against a row that may carry both — the
  owner's.~~ Settled in the 18 September 2026 reconciliation: exactly one, as
  the `series_chats_one_way_in` check above implements.
- ~~Whether a WeChat group over 200 members refuses its code, so the help line
  says to ask a member for an invite and recommends a WeCom code for a large
  class; WeChat's own page on the seven-day code says nothing about 200, and
  the line is written only once the fact is confirmed — anyone's.~~ Settled in
  the 18 September 2026 reconciliation: the line is not written while the
  fact is unconfirmed, as Scope Out says.

## Re-scope log

None.

## Notes

The brief's shared names put `qori.chats.per_series`, `qori.chats.code_max_mb`
and the `chat_code` live prefix in `T-123`'s config block; this task adds no
config key and reads those three. The note length, WeChat's seven days and the
image extensions are constants on `SeriesChatService` for the reasons in the
decisions, and nothing else in the stream reads them.

`D-029` gives `media_asset_id` null on delete and requires one way in; at the
database those meet in the check constraint, which refuses a code-only row
whose asset has been nulled. The service deletes the chat row before the asset
row everywhere, and the constraint makes any other order fail loudly. If
`T-130`'s `materials.media_asset_id` carries the same pair, its draft has the
same ordering to state.

`T-137`'s draft is edited to say where its Series-level material list sits
relative to `#chat` on `shared/Show.vue`: this task puts the chat card between
the progress block and the Episodes Panel, and both are page edits the claim
order in `streams/classroom.md` serialises.

`D-029` cut an earlier nine-platform, three-invite shape to four cases and one
row, and this task follows the decision. The `position` column is kept for
later as `D-029` says.

`SignUploadRequest` gains its first purpose-specific rule. `T-130`'s material
uploads share the document allow-list and need none; a chat code is the first
purpose whose allowed set is narrower than `qori.storage.allowed_uploads`.

The brief allocated one test file of about ten cases; this draft splits them
by surface into two files of 14 and 12, because the Peer route earns the
wrong-tenant, revoked, guest and public-page cases every new `/shared/*` route
carries, and the creator side earns the image-deletion and sign-time cases.
