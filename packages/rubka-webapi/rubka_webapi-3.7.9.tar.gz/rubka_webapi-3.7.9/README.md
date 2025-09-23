# rubka_webapi

یک کتابخانه قدرتمند، مدرن و آسان برای ساخت ربات‌های خودکار در روبیکا با پایتون.

**توسعه‌دهنده اصلی:** httex
**ایمیل:** wanwsnys69@gmail.com
**لایسنس:** MIT

## معرفی

`rubka_webapi` یک کتابخانه پایتون است که به شما امکان می‌دهد به راحتی با API روبیکا تعامل داشته باشید و ربات‌های قدرتمند و خودکار برای پلتفرم روبیکا بسازید. این کتابخانه با تمرکز بر سادگی، کارایی و مدرن بودن طراحی شده است تا تجربه توسعه را برای شما لذت‌بخش‌تر کند. با استفاده از `asyncio` و `httpx`، عملکرد بهینه و پاسخگویی بالا را تضمین می‌کند.

## ویژگی‌ها

| ویژگی | توضیحات |
| --- | --- |
| **آسان برای استفاده** | رابط کاربری ساده و شهودی برای تعامل با API روبیکا. |
| **مدرن و بهینه** | استفاده از `asyncio` برای عملیات ناهمزمان و `httpx` برای درخواست‌های HTTP سریع. |
| **پشتیبانی کامل از API** | پیاده‌سازی گسترده‌ای از متدهای API روبیکا برای مدیریت چت‌ها، کاربران، گروه‌ها، کانال‌ها و پیام‌ها. |
| **مدیریت رویدادها** | سیستم هندلر پیام برای پردازش آسان پیام‌های دریافتی. |
| **امنیت** | پشتیبانی از امضای درخواست‌ها با کلید خصوصی RSA. |
| **مستندات فارسی** | مستندات کامل و جامع به زبان فارسی. |

## نصب

برای نصب `rubka_webapi`، می‌توانید از `pip` استفاده کنید:

```bash
pip install rubka-webapi
```

**وابستگی‌ها:**

این کتابخانه به وابستگی‌های زیر نیاز دارد که به صورت خودکار نصب خواهند شد:

*   `cryptography`
*   `httpx`
*   `pydantic`
*   `websockets`
*   `urllib3`
*   `tqdm`
*   `websocket-client`
*   `pycryptodome`
*   `mutagen`
*   `filetype`

## شروع به کار سریع

برای شروع، ابتدا باید یک نمونه از `Client` ایجاد کنید. شما می‌توانید از کلید احراز هویت (Auth Key) و کلید خصوصی (Private Key) خود برای ورود استفاده کنید. در صورت عدم وجود، باید ابتدا با استفاده از متدهای احراز هویت، وارد حساب کاربری خود شوید.

```python
import asyncio
from rubka_webapi.client.client import Client

async def main():
    # کلید احراز هویت و کلید خصوصی خود را اینجا قرار دهید.
    # این مقادیر را نباید به صورت مستقیم در کد قرار دهید و بهتر است از متغیرهای محیطی استفاده کنید.
    auth_key = "YOUR_AUTH_KEY"
    private_key = """-----BEGIN RSA PRIVATE KEY-----
YOUR_PRIVATE_KEY_IN_PEM_FORMAT
-----END RSA PRIVATE KEY-----"""

    client = Client(auth=auth_key, private=private_key)

    # مثال: دریافت لیست چت‌ها
    try:
        print("در حال دریافت لیست چت‌ها...")
        chats_response = await client.get_chats()
        if chats_response and chats_response.get("data") and chats_response["data"].get("chats"):
            print("چت‌های شما:")
            for chat in chats_response["data"]["chats"]:
                print(f"  - {chat.get("title", "نامشخص")} (GUID: {chat.get("object_guid", "نامشخص")})")
        else:
            print("هیچ چتی یافت نشد یا خطایی رخ داد.")
    except Exception as e:
        print(f"خطا در دریافت چت‌ها: {e}")

    # مثال: ارسال پیام متنی (نیاز به GUID چت معتبر)
    # object_guid = "g0XXXXXXXXXXXXXX" # GUID چت مقصد را اینجا قرار دهید
    # message_text = "سلام از ربات rubka_webapi!"
    # try:
    #     print(f"در حال ارسال پیام به {object_guid}...")
    #     send_result = await client.send_text(object_guid, message_text)
    #     print(f"نتیجه ارسال پیام: {send_result}")
    # except Exception as e:
    #     print(f"خطا در ارسال پیام: {e}")

    # مثال: استفاده از هندلر پیام
    # @client.on_message(regexp=".*سلام.*")
    # async def handle_greeting(message):
    #     print(f"پیام 'سلام' دریافت شد: {message.text}")
    #     await message.reply("سلام به شما! من یک ربات هستم.")

    # برای شروع گوش دادن به پیام‌ها (نیاز به اتصال WebSocket):
    # await client.run()

    await client.network_manager.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## مستندات API

در ادامه، متدهای اصلی کتابخانه `rubka_webapi` به همراه توضیحات و پارامترهای آن‌ها آورده شده است.

### کلاس `Client`

کلاس اصلی برای تعامل با API روبیکا. مسئول مدیریت سشن‌ها، ارسال درخواست‌ها و دریافت پیام‌ها است.

**مقداردهی اولیه:**

```python
client = Client(
    session: Optional[str] = None, 
    auth: Optional[str] = None, 
    private: Optional[str] = None,
    platform: str = "web",
    api_version: int = 6,
    proxy: Optional[str] = None,
    time_out: int = 10,
    show_progress_bar: bool = True
)
```

**پارامترها:**

| پارامتر | نوع | توضیحات |
| --- | --- | --- |
| `session` | `str` (اختیاری) | نام سشن برای ذخیره و بارگذاری اطلاعات ورود. |
| `auth` | `str` (اختیاری) | کلید احراز هویت برای ورود دستی. |
| `private` | `str` (اختیاری) | کلید خصوصی RSA برای ورود دستی (در فرمت PEM). |
| `platform` | `str` (اختیاری) | پلتفرم مورد استفاده (پیش‌فرض: "web"). |
| `api_version` | `int` (اختیاری) | نسخه API روبیکا (پیش‌فرض: 6). |
| `proxy` | `str` (اختیاری) | آدرس پروکسی برای اتصال (اختیاری). |
| `time_out` | `int` (اختیاری) | مهلت زمانی برای درخواست‌ها بر حسب ثانیه (پیش‌فرض: 10). |
| `show_progress_bar` | `bool` (اختیاری) | نمایش نوار پیشرفت برای عملیات‌های طولانی (پیش‌فرض: True). |

**متدها:**

#### `async run()`

شروع به گوش دادن به پیام‌ها و پردازش آن‌ها. این متد اتصال WebSocket را برقرار کرده و پیام‌های دریافتی را به هندلرهای ثبت شده ارسال می‌کند.

#### `on_message(regexp: str)`

دکوراتور برای ثبت توابع به عنوان هندلر پیام‌ها. تابع دکوریت شده هر زمان که یک پیام با الگوی `regexp` مطابقت داشته باشد، فراخوانی می‌شود.

*   `regexp` (str): یک عبارت منظم (Regular Expression) برای فیلتر کردن پیام‌ها.

**مثال:**

```python
@client.on_message(regexp="^سلام")
async def handle_greeting(message):
    await message.reply("سلام! چطور می‌توانم کمکتان کنم؟")
```

#### متدهای احراز هویت

| متد | توضیحات |
| --- | --- |
| `async send_code(phone_number: str, pass_key: Optional[str] = None)` | ارسال کد تایید به شماره تلفن مشخص شده. |
| `async sign_in(phone_number: str, phone_code_hash: str, phone_code: str)` | ورود به حساب کاربری پس از دریافت کد تایید. |
| `async register_device(device_model: str)` | ثبت دستگاه جدید. |
| `async logout()` | خروج از حساب کاربری فعلی. |

#### متدهای پیام‌ها

| متد | توضیحات |
| --- | --- |
| `async send_text(object_guid: str, text: str, message_id: Optional[str] = None)` | ارسال پیام متنی به یک چت. |
| `async edit_message(object_guid: str, message_id: str, text: str, ...)` | ویرایش یک پیام. |
| `async delete_message(object_guid: str, message_id: str, type: str = "Global")` | حذف یک پیام. |
| `async send_file(object_guid: str, file: str, ...)` | ارسال فایل عمومی. |
| `async send_image(object_guid: str, file: str, ...)` | ارسال تصویر. |
| `async send_video(object_guid: str, file: str, ...)` | ارسال ویدئو. |
| `async send_video_message(object_guid: str, file: str, ...)` | ارسال پیام ویدئویی. |
| `async send_gif(object_guid: str, file: str, ...)` | ارسال فایل GIF. |
| `async send_music(object_guid: str, file: str, ...)` | ارسال فایل موسیقی. |
| `async send_voice(object_guid: str, file: str, ...)` | ارسال پیام صوتی. |
| `async send_location(object_guid: str, latitude: int, longitude: int, ...)` | ارسال موقعیت مکانی. |
| `async send_message_api_call(objectGuid: str, text: str, ...)` | ارسال پیام با فراخوانی API (برای دکمه‌ها). |
| `async reaction_message(object_guid: str, message_id: str, reaction: int)` | افزودن واکنش به یک پیام. |
| `async unreaction_message(object_guid: str, message_id: str, reaction: int)` | حذف واکنش از یک پیام. |
| `async pin_message(object_guid: str, message_id: str)` | پین کردن یک پیام. |
| `async unpin_message(object_guid: str, message_id: str)` | برداشتن پین از یک پیام. |
| `async get_messages(object_guid: str, ...)` | دریافت پیام‌های یک چت. |
| `async get_message_by_id(object_guid: str, message_id: str)` | دریافت یک پیام با شناسه. |
| `async forward_messages(object_guid: str, from_object_guid: str, ...)` | فوروارد کردن پیام‌ها. |
| `async get_messages_by_id(object_guid: str, message_ids: List[str])` | دریافت چندین پیام با شناسه‌ها. |
| `async get_message_link(object_guid: str, message_id: str)` | دریافت لینک یک پیام. |
| `async get_messages_updates(object_guid: str, ...)` | دریافت بروزرسانی‌های پیام‌ها. |

#### متدهای چت‌ها

| متد | توضیحات |
| --- | --- |
| `async get_chats(start_id: Optional[str] = None)` | دریافت لیست چت‌های کاربر. |
| `async get_top_users()` | دریافت لیست کاربران برتر. |
| `async remove_from_top_users(object_guid: str)` | حذف کاربر از لیست کاربران برتر. |
| `async get_chat_ads()` | دریافت تبلیغات چت. |
| `async get_chats_updates()` | دریافت بروزرسانی‌های چت‌ها. |
| `async join_chat(guid_or_link: str)` | پیوستن به یک چت (گروه یا کانال). |
| `async leave_chat(object_guid: str)` | ترک یک چت. |
| `async remove_chat(object_guid: str)` | حذف یک چت. |
| `async get_chat_info(object_guid: str)` | دریافت اطلاعات یک چت. |
| `async get_chat_info_by_username(username: str)` | دریافت اطلاعات یک چت با نام کاربری. |
| `async get_link(object_guid: str)` | دریافت لینک دعوت یک چت. |
| `async set_link(object_guid: str)` | تنظیم لینک دعوت یک چت. |
| `async set_admin(object_guid: str, member_guid: str, ...)` | تنظیم یک عضو به عنوان ادمین. |
| `async unset_admin(object_guid: str, member_guid: str)` | حذف وضعیت ادمین از یک عضو. |
| `async add_member(object_guid: str, member_guids: List[str])` | افزودن اعضا به چت. |
| `async ban_member(object_guid: str, member_guid: str)` | بن کردن یک عضو از چت. |
| `async unban_member(object_guid: str, member_guid: str)` | لغو بن یک عضو از چت. |
| `async get_banned_members(object_guid: str, ...)` | دریافت لیست اعضای بن شده. |
| `async get_all_members(object_guid: str, ...)` | دریافت تمام اعضای چت. |
| `async get_admin_members(object_guid: str, ...)` | دریافت لیست اعضای ادمین. |
| `async get_admin_access_list(object_guid: str, member_guid: str)` | دریافت لیست دسترسی‌های ادمین. |
| `async get_chat_preview(link: str)` | دریافت پیش‌نمایش چت از طریق لینک. |
| `async create_voice_chat(object_guid: str)` | ایجاد چت صوتی. |
| `async join_voice_chat(object_guid: str, my_guid: str, voice_chat_id: str)` | پیوستن به یک چت صوتی. |
| `async set_voice_chat_setting(object_guid: str, voice_chat_id: str, ...)` | تنظیمات چت صوتی. |
| `async get_voice_chat_updates(object_guid: str, voice_chat_id: str)` | دریافت بروزرسانی‌های چت صوتی. |
| `async get_voice_chat_participants(object_guid: str, voice_chat_id: str)` | دریافت شرکت‌کنندگان در چت صوتی. |
| `async set_voice_chat_state(object_guid: str, voice_chat_id: str, activity: str)` | تنظیم وضعیت چت صوتی. |
| `async send_voice_chat_activity(object_guid: str, voice_chat_id: str, ...)` | ارسال فعالیت در چت صوتی. |
| `async leave_voice_chat(object_guid: str, voice_chat_id: str)` | ترک چت صوتی. |
| `async discard_voice_chat(object_guid: str, voice_chat_id: str)` | پایان دادن به چت صوتی. |
| `async pin_chat(object_guid: str)` | پین کردن یک چت. |
| `async unpin_chat(object_guid: str)` | برداشتن پین از یک چت. |
| `async mute_chat(object_guid: str)` | بی‌صدا کردن یک چت. |
| `async unmute_chat(object_guid: str)` | خارج کردن چت از حالت بی‌صدا. |
| `async seen_chats(seen_list: Dict[str, str])` | علامت‌گذاری پیام‌ها به عنوان خوانده شده. |
| `async send_chat_activity(object_guid: str, activity: str)` | ارسال وضعیت فعالیت در چت. |
| `async search_chat_messages(object_guid: str, search_text: str)` | جستجو در پیام‌های یک چت. |
| `async upload_avatar(object_guid: str, main_file: str, ...)` | آپلود آواتار برای چت. |
| `async get_avatars(object_guid: str)` | دریافت آواتارهای یک چت. |
| `async delete_avatar(object_guid: str, avatar_id: str)` | حذف آواتار از چت. |
| `async delete_history(object_guid: str, last_message_id: str)` | حذف تاریخچه چت. |
| `async delete_user_chat(user_guid: str, last_deleted_message_id: str)` | حذف چت کاربر. |
| `async get_pending_owner(object_guid: str)` | دریافت مالک در انتظار برای چت. |
| `async request_change_owner(object_guid: str, member_guid: str)` | درخواست تغییر مالکیت چت. |
| `async accept_request_owner(object_guid: str)` | پذیرش درخواست تغییر مالکیت چت. |
| `async reject_request_owner(object_guid: str)` | رد درخواست تغییر مالکیت چت. |
| `async cancel_change_owner(object_guid: str)` | لغو تغییر مالکیت چت. |
| `async get_chat_reaction(object_guid: str, min_id: str, max_id: str)` | دریافت واکنش‌های چت. |
| `async report_chat(object_guid: str, description: str)` | گزارش یک چت. |
| `async set_chat_use_time(object_guid: str, time: int)` | تنظیم زمان استفاده از چت. |

#### متدهای کاربران

| متد | توضیحات |
| --- | --- |
| `async block_user(object_guid: str)` | بلاک کردن یک کاربر. |
| `async unblock_user(object_guid: str)` | خارج کردن کاربر از حالت بلاک. |
| `async check_user_username(username: str)` | بررسی وجود نام کاربری. |

#### متدهای گروه‌ها

| متد | توضیحات |
| --- | --- |
| `async add_group(title: str, member_guids: List[str])` | ایجاد یک گروه جدید. |
| `async get_group_default_access(object_guid: str)` | دریافت دسترسی‌های پیش‌فرض گروه. |
| `async set_group_default_access(object_guid: str, access_list: List = [])` | تنظیم دسترسی‌های پیش‌فرض گروه. |
| `async get_group_mention_list(object_guid: str, search_mention: str)` | دریافت لیست منشن‌های گروه. |
| `async edit_group_info(object_guid: str, ...)` | ویرایش اطلاعات گروه. |

#### متدهای کانال‌ها

| متد | توضیحات |
| --- | --- |
| `async add_channel(title: str, ...)` | ایجاد یک کانال جدید. |
| `async edit_channel_info(object_guid: str, ...)` | ویرایش اطلاعات کانال. |
| `async check_channel_username(username: str)` | بررسی وجود نام کاربری کانال. |
| `async get_channel_seen_count(object_guid: str, min_id: str, max_id: str)` | دریافت تعداد بازدیدهای کانال. |

#### متدهای استیکرها

| متد | توضیحات |
| --- | --- |
| `async get_stickers_by_id(sticker_ids: List[str])` | دریافت اطلاعات استیکرها با شناسه‌هایشان. |
| `async get_sticker_set_by_id(sticker_set_id: str)` | دریافت اطلاعات یک مجموعه استیکر با شناسه. |
| `async search_sticker_sets(query: str)` | جستجوی مجموعه‌های استیکر. |
| `async add_sticker_set(sticker_set_id: str)` | افزودن یک مجموعه استیکر به لیست کاربر. |
| `async remove_sticker_set(sticker_set_id: str)` | حذف یک مجموعه استیکر از لیست کاربر. |
| `async get_my_sticker_sets()` | دریافت لیست مجموعه‌های استیکر کاربر. |
| `async get_trending_sticker_sets()` | دریافت لیست مجموعه‌های استیکر پرطرفدار. |

#### متدهای مخاطبین

| متد | توضیحات |
| --- | --- |
| `async get_all_contacts(start_id: Optional[str] = None)` | دریافت تمام مخاطبین کاربر. |
| `async get_contacts_updates()` | دریافت بروزرسانی‌های مخاطبین. |
| `async delete_contact(object_guid: str)` | حذف یک مخاطب. |
| `async search_contacts(search_text: str)` | جستجو در میان مخاطبین. |

### کلاس `Message`

کلاس `Message` نماینده یک پیام دریافت شده از روبیکا است و متدهایی برای پاسخ دادن، ویرایش و حذف پیام فراهم می‌کند.

**ویژگی‌ها:**

| ویژگی | نوع | توضیحات |
| --- | --- | --- |
| `object_guid` | `str` | GUID چت. |
| `message_id` | `str` | شناسه پیام. |
| `text` | `str` | متن پیام. |
| `author_guid` | `str` | GUID فرستنده پیام. |
| `is_edited` | `bool` | آیا پیام ویرایش شده است. |
| `is_deleted` | `bool` | آیا پیام حذف شده است. |
| `file_id` | `Optional[str]` | شناسه فایل پیوست شده (در صورت وجود). |
| `file_type` | `Optional[str]` | نوع فایل پیوست شده (در صورت وجود). |

**متدها:**

| متد | توضیحات |
| --- | --- |
| `async reply(text: str)` | برای پاسخ دادن به پیام دریافت شده. |
| `async edit(text: str)` | برای ویرایش پیام فعلی (اگر پیام توسط ربات ارسال شده باشد). |
| `async delete()` | برای حذف پیام فعلی (اگر پیام توسط ربات ارسال شده باشد). |

## مشارکت

از مشارکت شما در توسعه `rubka_webapi` استقبال می‌کنیم! اگر پیشنهادی برای بهبود دارید، یا با مشکلی مواجه شدید، لطفاً یک Issue در گیت‌هاب ایجاد کنید یا یک Pull Request ارسال نمایید.

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای جزئیات بیشتر، فایل `LICENSE` را مشاهده کنید.

## تماس

**توسعه‌دهنده اصلی:** httex
**ایمیل:** wanwsnys69@gmail.com
**گیت‌هاب:** [https://github.com/xetay12/rubka_webapi](https://github.com/xetay12/rubka_webapi)

