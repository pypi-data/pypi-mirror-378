# rubka_webapi/client/client.py

import asyncio
import httpx
import websockets
from typing import Optional, Dict, Any, Callable, List
import re

from ..network.network import NetworkManager
from ..types.message import Message
from ..utils.exceptions import RubikaException

class Client:
    """
    کلاس اصلی برای تعامل با API روبیکا.
    این کلاس مسئول مدیریت سشن‌ها، ارسال درخواست‌ها و دریافت پیام‌ها است.
    """

    def __init__(
        self, 
        session: Optional[str] = None, 
        auth: Optional[str] = None, 
        private: Optional[str] = None,
        platform: str = "web",
        api_version: int = 6,
        proxy: Optional[str] = None,
        time_out: int = 10,
        show_progress_bar: bool = True
    ):
        """
        مقداردهی اولیه کلاینت روبیکا.

        پارامترها:
            session (str, اختیاری): نام سشن برای ذخیره و بارگذاری اطلاعات ورود.
            auth (str, اختیاری): کلید احراز هویت برای ورود دستی.
            private (str, اختیاری): کلید خصوصی RSA برای ورود دستی.
            platform (str, اختیاری): پلتفرم مورد استفاده (پیش‌فرض: "web").
            api_version (int, اختیاری): نسخه API روبیکا (پیش‌فرض: 6).
            proxy (str, اختیاری): آدرس پروکسی برای اتصال (اختیاری).
            time_out (int, اختیاری): مهلت زمانی برای درخواست‌ها بر حسب ثانیه (پیش‌فرض: 10).
            show_progress_bar (bool, اختیاری): نمایش نوار پیشرفت برای عملیات‌های طولانی (پیش‌فرض: True).
        """
        self.session_name = session
        self.auth_key = auth
        self.private_key = private
        self.platform = platform
        self.api_version = api_version
        self.proxy = proxy
        self.time_out = time_out
        self.show_progress_bar = show_progress_bar

        self.network_manager = NetworkManager(
            auth_key=self.auth_key, 
            private_key=self.private_key, 
            proxy=self.proxy, 
            time_out=self.time_out
        )
        self.message_handlers: List[Dict[str, Any]] = []

        print("کلاینت rubka_webapi مقداردهی اولیه شد.")

    async def run(self):
        """
        شروع به گوش دادن به پیام‌ها و پردازش آن‌ها.
        """
        print("شروع به گوش دادن به پیام‌ها...")
        # این بخش نیاز به پیاده‌سازی اتصال WebSocket و دریافت پیام‌ها دارد.
        # برای سادگی، فعلاً یک حلقه بی‌نهایت برای شبیه‌سازی گوش دادن قرار می‌دهیم.
        while True:
            await asyncio.sleep(1) # شبیه‌سازی دریافت پیام
            # در اینجا باید منطق دریافت پیام از WebSocket و پردازش آن اضافه شود.
            # مثال: message_data = await self.network_manager.receive_message()
            # if message_data:
            #     message = Message(self, message_data) # تبدیل داده خام به شیء Message
            #     await self._process_message(message)

    def on_message(self, regexp: str):
        """
        دکوراتور برای ثبت توابع به عنوان هندلر پیام‌ها.
        
        پارامترها:
            regexp (str): یک عبارت منظم (Regular Expression) برای فیلتر کردن پیام‌ها.
        """
        def decorator(func: Callable[[Message], Any]):
            self.message_handlers.append({"regexp": re.compile(regexp), "func": func})
            return func
        return decorator

    async def _process_message(self, message: Message):
        """
        پردازش پیام‌های دریافتی و فراخوانی هندلرهای مربوطه.
        """
        for handler in self.message_handlers:
            if handler["regexp"].search(message.text):
                await handler["func"](message)

    # متدهای احراز هویت
    async def send_code(self, phone_number: str, pass_key: Optional[str] = None) -> Dict[str, Any]:
        """
        برای ارسال کد تایید به شماره تلفن مشخص شده.

        پارامترها:
            phone_number (str): شماره تلفن کاربر.
            pass_key (str, اختیاری): کلید عبور (در صورت نیاز).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"phone_number": phone_number}
        if pass_key: payload["pass_key"] = pass_key
        return await self.network_manager.send_request("sendCode", payload)

    async def sign_in(self, phone_number: str, phone_code_hash: str, phone_code: str) -> Dict[str, Any]:
        """
        برای ورود به حساب کاربری پس از دریافت کد تایید.

        پارامترها:
            phone_number (str): شماره تلفن کاربر.
            phone_code_hash (str): هش کد تایید دریافت شده.
            phone_code (str): کد تایید دریافت شده.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {
            "phone_number": phone_number,
            "phone_code_hash": phone_code_hash,
            "phone_code": phone_code
        }
        return await self.network_manager.send_request("signIn", payload)

    async def register_device(self, device_model: str) -> Dict[str, Any]:
        """
        برای ثبت دستگاه جدید.

        پارامترها:
            device_model (str): مدل دستگاه.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"device_model": device_model}
        return await self.network_manager.send_request("registerDevice", payload)

    async def logout(self) -> Dict[str, Any]:
        """
        برای خروج از حساب کاربری فعلی.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        return await self.network_manager.send_request("logout", {})

    async def send_text(self, object_guid: str, text: str, message_id: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال پیام متنی به یک چت.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            text (str): متن پیام.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن (reply).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {
            "object_guid": object_guid,
            "text": text,
        }
        if message_id:
            payload["reply_to_message_id"] = message_id
        
        return await self.network_manager.send_request("sendMessage", payload)

    async def edit_message(self, object_guid: str, message_id: str, text: str, file: Optional[str] = None, file_name: Optional[str] = None, thumbnail: Optional[str] = None) -> Dict[str, Any]:
        """
        ویرایش یک پیام.

        پارامترها:
            object_guid (str): GUID چت.
            message_id (str): شناسه پیام.
            text (str): متن جدید پیام.
            file (str, اختیاری): مسیر فایل جدید (در صورت ویرایش فایل).
            file_name (str, اختیاری): نام فایل جدید.
            thumbnail (str, اختیاری): بندانگشتی جدید.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {
            "object_guid": object_guid,
            "message_id": message_id,
            "text": text,
        }
        # منطق اضافه کردن فایل، نام فایل و بندانگشتی در صورت وجود
        return await self.network_manager.send_request("editMessage", payload)

    async def delete_message(self, object_guid: str, message_id: str, type: str = "Global") -> Dict[str, Any]:
        """
        حذف یک پیام.

        پارامترها:
            object_guid (str): GUID چت.
            message_id (str): شناسه پیام.
            type (str, اختیاری): نوع حذف (مثلاً "Global" برای حذف برای همه، پیش‌فرض: "Global").

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {
            "object_guid": object_guid,
            "message_id": message_id,
            "type": type,
        }
        return await self.network_manager.send_request("deleteMessage", payload)

    # متدهای چت‌ها
    async def get_chats(self, start_id: Optional[str] = None) -> Dict[str, Any]:
        """
        دریافت لیست چت‌های کاربر.

        پارامترها:
            start_id (str, اختیاری): شناسه شروع برای دریافت چت‌ها (برای صفحه‌بندی).

        بازگشتی:
            dict: حاوی اطلاعات چت‌ها.
        """
        payload = {}
        if start_id: payload["start_id"] = start_id
        return await self.network_manager.send_request("getChats", payload)

    async def get_top_users(self) -> Dict[str, Any]:
        """
        دریافت لیست کاربران برتر.

        بازگشتی:
            dict: حاوی اطلاعات کاربران برتر.
        """
        return await self.network_manager.send_request("getTopUsers", {})

    async def remove_from_top_users(self, object_guid: str) -> Dict[str, Any]:
        """
        حذف کاربر از لیست کاربران برتر.

        پارامترها:
            object_guid (str): GUID (شناسه جهانی منحصر به فرد) کاربر مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("removeFromTopUsers", payload)

    async def get_chat_ads(self) -> Dict[str, Any]:
        """
        دریافت تبلیغات چت.

        بازگشتی:
            dict: حاوی اطلاعات تبلیغات.
        """
        return await self.network_manager.send_request("getChatAds", {})

    async def get_chats_updates(self) -> Dict[str, Any]:
        """
        دریافت بروزرسانی‌های چت‌ها.

        بازگشتی:
            dict: حاوی اطلاعات بروزرسانی‌ها.
        """
        return await self.network_manager.send_request("getChatsUpdates", {})

    async def join_chat(self, guid_or_link: str) -> Dict[str, Any]:
        """
        پیوستن به یک چت (گروه یا کانال) با استفاده از GUID یا لینک دعوت.

        پارامترها:
            guid_or_link (str): GUID چت یا لینک دعوت.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"guid_or_link": guid_or_link}
        return await self.network_manager.send_request("joinChat", payload)

    async def leave_chat(self, object_guid: str) -> Dict[str, Any]:
        """
        ترک یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("leaveChat", payload)

    async def remove_chat(self, object_guid: str) -> Dict[str, Any]:
        """
        حذف یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("removeChat", payload)

    async def get_chat_info(self, object_guid: str) -> Dict[str, Any]:
        """
        دریافت اطلاعات یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات چت.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("getChatInfo", payload)

    async def get_chat_info_by_username(self, username: str) -> Dict[str, Any]:
        """
        دریافت اطلاعات یک چت با استفاده از نام کاربری.

        پارامترها:
            username (str): نام کاربری چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات چت.
        """
        payload = {"username": username}
        return await self.network_manager.send_request("getChatInfoByUsername", payload)

    async def get_link(self, object_guid: str) -> Dict[str, Any]:
        """
        دریافت لینک دعوت یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی لینک دعوت.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("getLink", payload)

    async def set_link(self, object_guid: str) -> Dict[str, Any]:
        """
        تنظیم لینک دعوت یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("setLink", payload)

    async def set_admin(self, object_guid: str, member_guid: str, access_list: Optional[List] = None, custom_title: Optional[str] = None) -> Dict[str, Any]:
        """
        تنظیم یک عضو به عنوان ادمین در چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            member_guid (str): GUID عضو مورد نظر.
            access_list (list, اختیاری): لیست دسترسی‌های ادمین.
            custom_title (str, اختیاری): عنوان سفارشی برای ادمین.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "member_guid": member_guid}
        if access_list: payload["access_list"] = access_list
        if custom_title: payload["custom_title"] = custom_title
        return await self.network_manager.send_request("setAdmin", payload)

    async def unset_admin(self, object_guid: str, member_guid: str) -> Dict[str, Any]:
        """
        حذف وضعیت ادمین از یک عضو در چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            member_guid (str): GUID عضو مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "member_guid": member_guid}
        return await self.network_manager.send_request("unsetAdmin", payload)

    async def add_member(self, object_guid: str, member_guids: List[str]) -> Dict[str, Any]:
        """
        افزودن اعضا به چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            member_guids (list): لیستی از GUID اعضای مورد نظر برای افزودن.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "member_guids": member_guids}
        return await self.network_manager.send_request("addMember", payload)

    async def ban_member(self, object_guid: str, member_guid: str) -> Dict[str, Any]:
        """
        بن کردن یک عضو از چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            member_guid (str): GUID عضو مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "member_guid": member_guid}
        return await self.network_manager.send_request("banMember", payload)

    async def unban_member(self, object_guid: str, member_guid: str) -> Dict[str, Any]:
        """
        لغو بن یک عضو از چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            member_guid (str): GUID عضو مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "member_guid": member_guid}
        return await self.network_manager.send_request("unbanMember", payload)

    async def get_banned_members(self, object_guid: str, start_id: Optional[str] = None) -> Dict[str, Any]:
        """
        دریافت لیست اعضای بن شده در چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            start_id (str, اختیاری): شناسه شروع برای صفحه‌بندی.

        بازگشتی:
            dict: حاوی اطلاعات اعضای بن شده.
        """
        payload = {"object_guid": object_guid}
        if start_id: payload["start_id"] = start_id
        return await self.network_manager.send_request("getBannedMembers", payload)

    async def get_all_members(self, object_guid: str, search_text: Optional[str] = None, start_id: Optional[str] = None, just_get_guids: bool = False) -> Dict[str, Any]:
        """
        دریافت تمام اعضای چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            search_text (str, اختیاری): متن برای جستجو در میان اعضا.
            start_id (str, اختیاری): شناسه شروع برای صفحه‌بندی.
            just_get_guids (bool, اختیاری): فقط GUID اعضا را دریافت کند (پیش‌فرض: False).

        بازگشتی:
            dict: حاوی اطلاعات اعضا.
        """
        payload = {"object_guid": object_guid, "just_get_guids": just_get_guids}
        if search_text: payload["search_text"] = search_text
        if start_id: payload["start_id"] = start_id
        return await self.network_manager.send_request("getAllMembers", payload)

    async def get_admin_members(self, object_guid: str, start_id: Optional[str] = None, just_get_guids: bool = False) -> Dict[str, Any]:
        """
        دریافت لیست اعضای ادمین در چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            start_id (str, اختیاری): شناسه شروع برای صفحه‌بندی.
            just_get_guids (bool, اختیاری): فقط GUID ادمین‌ها را دریافت کند (پیش‌فرض: False).

        بازگشتی:
            dict: حاوی اطلاعات ادمین‌ها.
        """
        payload = {"object_guid": object_guid, "just_get_guids": just_get_guids}
        if start_id: payload["start_id"] = start_id
        return await self.network_manager.send_request("getAdminMembers", payload)

    async def get_admin_access_list(self, object_guid: str, member_guid: str) -> Dict[str, Any]:
        """
        دریافت لیست دسترسی‌های ادمین یک عضو.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            member_guid (str): GUID عضو مورد نظر.

        بازگشتی:
            dict: حاوی لیست دسترسی‌ها.
        """
        payload = {"object_guid": object_guid, "member_guid": member_guid}
        return await self.network_manager.send_request("getAdminAccessList", payload)

    async def get_chat_preview(self, link: str) -> Dict[str, Any]:
        """
        دریافت پیش‌نمایش چت از طریق لینک دعوت.

        پارامترها:
            link (str): لینک دعوت چت.

        بازگشتی:
            dict: حاوی اطلاعات پیش‌نمایش چت.
        """
        payload = {"link": link}
        return await self.network_manager.send_request("getChatPreview", payload)

    async def create_voice_chat(self, object_guid: str) -> Dict[str, Any]:
        """
        ایجاد چت صوتی در یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("createVoiceChat", payload)

    async def join_voice_chat(self, object_guid: str, my_guid: str, voice_chat_id: str) -> Dict[str, Any]:
        """
        پیوستن به یک چت صوتی.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            my_guid (str): GUID کاربر فعلی.
            voice_chat_id (str): شناسه چت صوتی.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "my_guid": my_guid, "voice_chat_id": voice_chat_id}
        return await self.network_manager.send_request("joinVoiceChat", payload)

    async def set_voice_chat_setting(self, object_guid: str, voice_chat_id: str, title: Optional[str] = None, join_mute: Optional[bool] = None) -> Dict[str, Any]:
        """
        تنظیمات چت صوتی.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            voice_chat_id (str): شناسه چت صوتی.
            title (str, اختیاری): عنوان چت صوتی.
            join_mute (bool, اختیاری): آیا اعضای جدید به صورت بی‌صدا وارد شوند (پیش‌فرض: None).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "voice_chat_id": voice_chat_id}
        if title: payload["title"] = title
        if join_mute is not None: payload["join_mute"] = join_mute
        return await self.network_manager.send_request("setVoiceChatSetting", payload)

    async def get_voice_chat_updates(self, object_guid: str, voice_chat_id: str) -> Dict[str, Any]:
        """
        دریافت بروزرسانی‌های چت صوتی.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            voice_chat_id (str): شناسه چت صوتی.

        بازگشتی:
            dict: حاوی اطلاعات بروزرسانی‌ها.
        """
        payload = {"object_guid": object_guid, "voice_chat_id": voice_chat_id}
        return await self.network_manager.send_request("getVoiceChatUpdates", payload)

    async def get_voice_chat_participants(self, object_guid: str, voice_chat_id: str) -> Dict[str, Any]:
        """
        دریافت شرکت‌کنندگان در چت صوتی.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            voice_chat_id (str): شناسه چت صوتی.

        بازگشتی:
            dict: حاوی اطلاعات شرکت‌کنندگان.
        """
        payload = {"object_guid": object_guid, "voice_chat_id": voice_chat_id}
        return await self.network_manager.send_request("getVoiceChatParticipants", payload)

    async def set_voice_chat_state(self, object_guid: str, voice_chat_id: str, activity: str) -> Dict[str, Any]:
        """
        تنظیم وضعیت چت صوتی (مثلاً در حال صحبت).

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            voice_chat_id (str): شناسه چت صوتی.
            activity (str): وضعیت فعالیت (مثلاً "speaking").

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "voice_chat_id": voice_chat_id, "activity": activity}
        return await self.network_manager.send_request("setVoiceChatState", payload)

    async def send_voice_chat_activity(self, object_guid: str, voice_chat_id: str, activity: str, participant_object_guid: str) -> Dict[str, Any]:
        """
        ارسال فعالیت در چت صوتی.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            voice_chat_id (str): شناسه چت صوتی.
            activity (str): نوع فعالیت.
            participant_object_guid (str): GUID شرکت‌کننده.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "voice_chat_id": voice_chat_id, "activity": activity, "participant_object_guid": participant_object_guid}
        return await self.network_manager.send_request("sendVoiceChatActivity", payload)

    async def leave_voice_chat(self, object_guid: str, voice_chat_id: str) -> Dict[str, Any]:
        """
        ترک چت صوتی.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            voice_chat_id (str): شناسه چت صوتی.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "voice_chat_id": voice_chat_id}
        return await self.network_manager.send_request("leaveVoiceChat", payload)

    async def discard_voice_chat(self, object_guid: str, voice_chat_id: str) -> Dict[str, Any]:
        """
        پایان دادن به چت صوتی.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            voice_chat_id (str): شناسه چت صوتی.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "voice_chat_id": voice_chat_id}
        return await self.network_manager.send_request("discardVoiceChat", payload)

    async def pin_chat(self, object_guid: str) -> Dict[str, Any]:
        """
        پین کردن یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("pinChat", payload)

    async def unpin_chat(self, object_guid: str) -> Dict[str, Any]:
        """
        برداشتن پین از یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("unpinChat", payload)

    async def mute_chat(self, object_guid: str) -> Dict[str, Any]:
        """
        بی‌صدا کردن یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("muteChat", payload)

    async def unmute_chat(self, object_guid: str) -> Dict[str, Any]:
        """
        خارج کردن چت از حالت بی‌صدا.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("unmuteChat", payload)

    async def seen_chats(self, seen_list: Dict[str, str]) -> Dict[str, Any]:
        """
        علامت‌گذاری پیام‌ها به عنوان خوانده شده.

        پارامترها:
            seen_list (dict): دیکشنری شامل GUID چت و شناسه آخرین پیام خوانده شده (مثال: `{"object_guid": "message_id", ...}`).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"seen_list": seen_list}
        return await self.network_manager.send_request("seenChats", payload)

    async def send_chat_activity(self, object_guid: str, activity: str) -> Dict[str, Any]:
        """
        ارسال وضعیت فعالیت در چت (مثلاً در حال تایپ).

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            activity (str): نوع فعالیت (مثلاً "Typing").

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "activity": activity}
        return await self.network_manager.send_request("sendChatActivity", payload)

    async def search_chat_messages(self, object_guid: str, search_text: str) -> Dict[str, Any]:
        """
        جستجو در پیام‌های یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            search_text (str): متن مورد جستجو.

        بازگشتی:
            dict: حاوی نتایج جستجو.
        """
        payload = {"object_guid": object_guid, "search_text": search_text}
        return await self.network_manager.send_request("searchChatMessages", payload)

    async def upload_avatar(self, object_guid: str, main_file: str, thumbnail_file: Optional[str] = None) -> Dict[str, Any]:
        """
        آپلود آواتار برای چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            main_file (str): مسیر فایل اصلی آواتار.
            thumbnail_file (str, اختیاری): مسیر فایل بندانگشتی آواتار.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "main_file": main_file}
        if thumbnail_file: payload["thumbnail_file"] = thumbnail_file
        return await self.network_manager.send_request("uploadAvatar", payload)

    async def get_avatars(self, object_guid: str) -> Dict[str, Any]:
        """
        دریافت آواتارهای یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات آواتارها.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("getAvatars", payload)

    async def delete_avatar(self, object_guid: str, avatar_id: str) -> Dict[str, Any]:
        """
        حذف آواتار از چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            avatar_id (str): شناسه آواتار مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "avatar_id": avatar_id}
        return await self.network_manager.send_request("deleteAvatar", payload)

    async def delete_history(self, object_guid: str, last_message_id: str) -> Dict[str, Any]:
        """
        حذف تاریخچه چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            last_message_id (str): شناسه آخرین پیام برای حذف تاریخچه تا آن نقطه.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "last_message_id": last_message_id}
        return await self.network_manager.send_request("deleteHistory", payload)

    async def delete_user_chat(self, user_guid: str, last_deleted_message_id: str) -> Dict[str, Any]:
        """
        حذف چت کاربر.

        پارامترها:
            user_guid (str): GUID کاربر مورد نظر.
            last_deleted_message_id (str): شناسه آخرین پیام حذف شده.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"user_guid": user_guid, "last_deleted_message_id": last_deleted_message_id}
        return await self.network_manager.send_request("deleteUserChat", payload)

    async def get_pending_owner(self, object_guid: str) -> Dict[str, Any]:
        """
        دریافت مالک در انتظار برای چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات مالک در انتظار.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("getPendingOwner", payload)

    async def request_change_owner(self, object_guid: str, member_guid: str) -> Dict[str, Any]:
        """
        درخواست تغییر مالکیت چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            member_guid (str): GUID عضو جدید برای مالکیت.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "member_guid": member_guid}
        return await self.network_manager.send_request("requestChangeOwner", payload)

    async def accept_request_owner(self, object_guid: str) -> Dict[str, Any]:
        """
        پذیرش درخواست تغییر مالکیت چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("acceptRequestOwner", payload)

    async def reject_request_owner(self, object_guid: str) -> Dict[str, Any]:
        """
        رد درخواست تغییر مالکیت چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("rejectRequestOwner", payload)

    async def cancel_change_owner(self, object_guid: str) -> Dict[str, Any]:
        """
        لغو تغییر مالکیت چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("cancelChangeOwner", payload)

    async def get_chat_reaction(self, object_guid: str, min_id: str, max_id: str) -> Dict[str, Any]:
        """
        دریافت واکنش‌های چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            min_id (str): حداقل شناسه پیام.
            max_id (str): حداکثر شناسه پیام.

        بازگشتی:
            dict: حاوی اطلاعات واکنش‌ها.
        """
        payload = {"object_guid": object_guid, "min_id": min_id, "max_id": max_id}
        return await self.network_manager.send_request("getChatReaction", payload)

    async def report_chat(self, object_guid: str, description: str) -> Dict[str, Any]:
        """
        گزارش یک چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            description (str): توضیحات گزارش.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "description": description}
        return await self.network_manager.send_request("reportChat", payload)

    async def set_chat_use_time(self, object_guid: str, time: int) -> Dict[str, Any]:
        """
        تنظیم زمان استفاده از چت.

        پارامترها:
            object_guid (str): GUID چت مورد نظر.
            time (int): زمان استفاده.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "time": time}
        return await self.network_manager.send_request("setChatUseTime", payload)

    # متدهای کاربران
    async def block_user(self, object_guid: str) -> Dict[str, Any]:
        """
        بلاک کردن یک کاربر.

        پارامترها:
            object_guid (str): GUID کاربر مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("blockUser", payload)

    async def unblock_user(self, object_guid: str) -> Dict[str, Any]:
        """
        خارج کردن کاربر از حالت بلاک.

        پارامترها:
            object_guid (str): GUID کاربر مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("unblockUser", payload)

    async def check_user_username(self, username: str) -> Dict[str, Any]:
        """
        بررسی وجود نام کاربری.

        پارامترها:
            username (str): نام کاربری مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"username": username}
        return await self.network_manager.send_request("checkUserUsername", payload)

    # متدهای گروه‌ها
    async def add_group(self, title: str, member_guids: List[str]) -> Dict[str, Any]:
        """
        ایجاد یک گروه جدید.

        پارامترها:
            title (str): عنوان گروه.
            member_guids (list): لیستی از GUID اعضای اولیه گروه.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"title": title, "member_guids": member_guids}
        return await self.network_manager.send_request("addGroup", payload)

    async def get_group_default_access(self, object_guid: str) -> Dict[str, Any]:
        """
        دریافت دسترسی‌های پیش‌فرض گروه.

        پارامترها:
            object_guid (str): GUID گروه مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات دسترسی‌ها.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("getGroupDefaultAccess", payload)

    async def set_group_default_access(self, object_guid: str, access_list: List = []) -> Dict[str, Any]:
        """
        تنظیم دسترسی‌های پیش‌فرض گروه.

        پارامترها:
            object_guid (str): GUID گروه مورد نظر.
            access_list (list, اختیاری): لیستی از دسترسی‌های جدید (پیش‌فرض: لیست خالی).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "access_list": access_list}
        return await self.network_manager.send_request("setGroupDefaultAccess", payload)

    async def get_group_mention_list(self, object_guid: str, search_mention: str) -> Dict[str, Any]:
        """
        دریافت لیست منشن‌های گروه.

        پارامترها:
            object_guid (str): GUID گروه مورد نظر.
            search_mention (str): متن برای جستجو در منشن‌ها.

        بازگشتی:
            dict: حاوی اطلاعات منشن‌ها.
        """
        payload = {"object_guid": object_guid, "search_mention": search_mention}
        return await self.network_manager.send_request("getGroupMentionList", payload)

    async def edit_group_info(self, object_guid: str, title: Optional[str] = None, description: Optional[str] = None, slow_mode: Optional[int] = None, event_messages: Optional[bool] = None, chat_history_for_new_members: Optional[bool] = None, reaction_type: Optional[str] = None, selected_reactions: Optional[List] = None) -> Dict[str, Any]:
        """
        ویرایش اطلاعات گروه.

        پارامترها:
            object_guid (str): GUID گروه مورد نظر.
            title (str, اختیاری): عنوان جدید گروه.
            description (str, اختیاری): توضیحات جدید گروه.
            slow_mode (int, اختیاری): حالت آهسته (زمان بین ارسال پیام‌ها بر حسب ثانیه).
            event_messages (bool, اختیاری): نمایش پیام‌های رویداد (مثلاً ورود/خروج اعضا).
            chat_history_for_new_members (bool, اختیاری): نمایش تاریخچه چت برای اعضای جدید.
            reaction_type (str, اختیاری): نوع واکنش‌های مجاز.
            selected_reactions (list, اختیاری): لیست واکنش‌های انتخاب شده.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        if title: payload["title"] = title
        if description: payload["description"] = description
        if slow_mode is not None: payload["slow_mode"] = slow_mode
        if event_messages is not None: payload["event_messages"] = event_messages
        if chat_history_for_new_members is not None: payload["chat_history_for_new_members"] = chat_history_for_new_members
        if reaction_type: payload["reaction_type"] = reaction_type
        if selected_reactions: payload["selected_reactions"] = selected_reactions
        return await self.network_manager.send_request("editGroupInfo", payload)

    # متدهای کانال‌ها
    async def add_channel(self, title: str, description: Optional[str] = None, member_guids: Optional[List[str]] = None, private: bool = False) -> Dict[str, Any]:
        """
        ایجاد یک کانال جدید.

        پارامترها:
            title (str): عنوان کانال.
            description (str, اختیاری): توضیحات کانال.
            member_guids (list, اختیاری): لیستی از GUID اعضای اولیه کانال.
            private (bool, اختیاری): آیا کانال خصوصی باشد (پیش‌فرض: False).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"title": title, "private": private}
        if description: payload["description"] = description
        if member_guids: payload["member_guids"] = member_guids
        return await self.network_manager.send_request("addChannel", payload)

    async def edit_channel_info(self, object_guid: str, title: Optional[str] = None, description: Optional[str] = None, username: Optional[str] = None, private: Optional[bool] = None, sign_message: Optional[bool] = None, reaction_type: Optional[str] = None, selected_reactions: Optional[List] = None) -> Dict[str, Any]:
        """
        ویرایش اطلاعات کانال.

        پارامترها:
            object_guid (str): GUID کانال مورد نظر.
            title (str, اختیاری): عنوان جدید کانال.
            description (str, اختیاری): توضیحات جدید کانال.
            username (str, اختیاری): نام کاربری جدید کانال.
            private (bool, اختیاری): آیا کانال خصوصی باشد.
            sign_message (bool, اختیاری): آیا پیام‌ها با امضا ارسال شوند.
            reaction_type (str, اختیاری): نوع واکنش‌های مجاز.
            selected_reactions (list, اختیاری): لیست واکنش‌های انتخاب شده.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        if title: payload["title"] = title
        if description: payload["description"] = description
        if username: payload["username"] = username
        if private is not None: payload["private"] = private
        if sign_message is not None: payload["sign_message"] = sign_message
        if reaction_type: payload["reaction_type"] = reaction_type
        if selected_reactions: payload["selected_reactions"] = selected_reactions
        return await self.network_manager.send_request("editChannelInfo", payload)

    async def check_channel_username(self, username: str) -> Dict[str, Any]:
        """
        بررسی وجود نام کاربری کانال.

        پارامترها:
            username (str): نام کاربری مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"username": username}
        return await self.network_manager.send_request("checkChannelUsername", payload)

    async def get_channel_seen_count(self, object_guid: str, min_id: str, max_id: str) -> Dict[str, Any]:
        """
        دریافت تعداد بازدیدهای کانال.

        پارامترها:
            object_guid (str): GUID کانال مورد نظر.
            min_id (str): حداقل شناسه پیام.
            max_id (str): حداکثر شناسه پیام.

        بازگشتی:
            dict: حاوی اطلاعات تعداد بازدیدها.
        """
        payload = {"object_guid": object_guid, "min_id": min_id, "max_id": max_id}
        return await self.network_manager.send_request("getChannelSeenCount", payload)

    # متدهای پیام‌ها
    async def send_file(self, object_guid: str, file: str, message_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال فایل عمومی.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            file (str): مسیر فایل برای ارسال.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن.
            text (str, اختیاری): متن همراه فایل.
            file_name (str, اختیاری): نام فایل.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "file": file}
        if message_id: payload["message_id"] = message_id
        if text: payload["text"] = text
        if file_name: payload["file_name"] = file_name
        return await self.network_manager.send_request("sendFile", payload)

    async def send_image(self, object_guid: str, file: str, message_id: Optional[str] = None, text: Optional[str] = None, is_spoil: bool = False, thumbnail: Optional[str] = None, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال تصویر.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            file (str): مسیر فایل تصویر.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن.
            text (str, اختیاری): متن همراه تصویر.
            is_spoil (bool, اختیاری): آیا تصویر به عنوان اسپویل ارسال شود (پیش‌فرض: False).
            thumbnail (str, اختیاری): بندانگشتی تصویر.
            file_name (str, اختیاری): نام فایل تصویر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "file": file, "is_spoil": is_spoil}
        if message_id: payload["message_id"] = message_id
        if text: payload["text"] = text
        if thumbnail: payload["thumbnail"] = thumbnail
        if file_name: payload["file_name"] = file_name
        return await self.network_manager.send_request("sendImage", payload)

    async def send_video(self, object_guid: str, file: str, message_id: Optional[str] = None, text: Optional[str] = None, is_spoil: bool = False, thumbnail: Optional[str] = None, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال ویدئو.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            file (str): مسیر فایل ویدئو.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن.
            text (str, اختیاری): متن همراه ویدئو.
            is_spoil (bool, اختیاری): آیا ویدئو به عنوان اسپویل ارسال شود (پیش‌فرض: False).
            thumbnail (str, اختیاری): بندانگشتی ویدئو.
            file_name (str, اختیاری): نام فایل ویدئو.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "file": file, "is_spoil": is_spoil}
        if message_id: payload["message_id"] = message_id
        if text: payload["text"] = text
        if thumbnail: payload["thumbnail"] = thumbnail
        if file_name: payload["file_name"] = file_name
        return await self.network_manager.send_request("sendVideo", payload)

    async def send_video_message(self, object_guid: str, file: str, message_id: Optional[str] = None, text: Optional[str] = None, thumbnail: Optional[str] = None, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال پیام ویدئویی (ممکن است با `send_video` تفاوت داشته باشد).

        پارامترها:
            object_guid (str): GUID چت مقصد.
            file (str): مسیر فایل ویدئو.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن.
            text (str, اختیاری): متن همراه ویدئو.
            thumbnail (str, اختیاری): بندانگشتی ویدئو.
            file_name (str, اختیاری): نام فایل ویدئو.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "file": file}
        if message_id: payload["message_id"] = message_id
        if text: payload["text"] = text
        if thumbnail: payload["thumbnail"] = thumbnail
        if file_name: payload["file_name"] = file_name
        return await self.network_manager.send_request("sendVideoMessage", payload)

    async def send_gif(self, object_guid: str, file: str, message_id: Optional[str] = None, text: Optional[str] = None, thumbnail: Optional[str] = None, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال فایل GIF.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            file (str): مسیر فایل GIF.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن.
            text (str, اختیاری): متن همراه GIF.
            thumbnail (str, اختیاری): بندانگشتی GIF.
            file_name (str, اختیاری): نام فایل GIF.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "file": file}
        if message_id: payload["message_id"] = message_id
        if text: payload["text"] = text
        if thumbnail: payload["thumbnail"] = thumbnail
        if file_name: payload["file_name"] = file_name
        return await self.network_manager.send_request("sendGif", payload)

    async def send_music(self, object_guid: str, file: str, message_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None, performer: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال فایل موسیقی.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            file (str): مسیر فایل موسیقی.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن.
            text (str, اختیاری): متن همراه موسیقی.
            file_name (str, اختیاری): نام فایل موسیقی.
            performer (str, اختیاری): نام هنرمند.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "file": file}
        if message_id: payload["message_id"] = message_id
        if text: payload["text"] = text
        if file_name: payload["file_name"] = file_name
        if performer: payload["performer"] = performer
        return await self.network_manager.send_request("sendMusic", payload)

    async def send_voice(self, object_guid: str, file: str, message_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None, time: int = 0) -> Dict[str, Any]:
        """
        ارسال پیام صوتی.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            file (str): مسیر فایل صوتی.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن.
            text (str, اختیاری): متن همراه پیام صوتی.
            file_name (str, اختیاری): نام فایل صوتی.
            time (int, اختیاری): مدت زمان پیام صوتی بر حسب ثانیه (پیش‌فرض: 0).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "file": file, "time": time}
        if message_id: payload["message_id"] = message_id
        if text: payload["text"] = text
        if file_name: payload["file_name"] = file_name
        return await self.network_manager.send_request("sendVoice", payload)

    async def send_location(self, object_guid: str, latitude: int, longitude: int, message_id: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال موقعیت مکانی.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            latitude (int): عرض جغرافیایی.
            longitude (int): طول جغرافیایی.
            message_id (str, اختیاری): شناسه پیام برای پاسخ دادن.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "latitude": latitude, "longitude": longitude}
        if message_id: payload["message_id"] = message_id
        return await self.network_manager.send_request("sendLocation", payload)

    async def send_message_api_call(self, objectGuid: str, text: str, message_id: str, button_id: str) -> Dict[str, Any]:
        """
        ارسال پیام با فراخوانی API (برای دکمه‌ها یا اکشن‌های خاص).

        پارامترها:
            objectGuid (str): GUID چت مقصد.
            text (str): متن پیام.
            message_id (str): شناسه پیام.
            button_id (str): شناسه دکمه.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"objectGuid": objectGuid, "text": text, "message_id": message_id, "button_id": button_id}
        return await self.network_manager.send_request("sendMessageApiCall", payload)

    async def reaction_message(self, object_guid: str, message_id: str, reaction: int) -> Dict[str, Any]:
        """
        افزودن واکنش به یک پیام.

        پارامترها:
            object_guid (str): GUID چت.
            message_id (str): شناسه پیام.
            reaction (int): شناسه واکنش (مثلاً 1 برای لایک).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "message_id": message_id, "reaction": reaction}
        return await self.network_manager.send_request("reactionMessage", payload)

    async def unreaction_message(self, object_guid: str, message_id: str, reaction: int) -> Dict[str, Any]:
        """
        حذف واکنش از یک پیام.

        پارامترها:
            object_guid (str): GUID چت.
            message_id (str): شناسه پیام.
            reaction (int): شناسه واکنش.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "message_id": message_id, "reaction": reaction}
        return await self.network_manager.send_request("unreactionMessage", payload)

    async def pin_message(self, object_guid: str, message_id: str) -> Dict[str, Any]:
        """
        پین کردن یک پیام.

        پارامترها:
            object_guid (str): GUID چت.
            message_id (str): شناسه پیام.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "message_id": message_id}
        return await self.network_manager.send_request("pinMessage", payload)

    async def unpin_message(self, object_guid: str, message_id: str) -> Dict[str, Any]:
        """
        برداشتن پین از یک پیام.

        پارامترها:
            object_guid (str): GUID چت.
            message_id (str): شناسه پیام.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "message_id": message_id}
        return await self.network_manager.send_request("unpinMessage", payload)

    async def get_messages(self, object_guid: str, min_id: Optional[str] = None, max_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        دریافت پیام‌های یک چت.

        پارامترها:
            object_guid (str): GUID چت.
            min_id (str, اختیاری): حداقل شناسه پیام.
            max_id (str, اختیاری): حداکثر شناسه پیام.
            limit (int, اختیاری): تعداد پیام‌های قابل دریافت (پیش‌فرض: 20).

        بازگشتی:
            dict: حاوی اطلاعات پیام‌ها.
        """
        payload = {"object_guid": object_guid, "limit": limit}
        if min_id: payload["min_id"] = min_id
        if max_id: payload["max_id"] = max_id
        return await self.network_manager.send_request("getMessages", payload)

    async def get_message_by_id(self, object_guid: str, message_id: str) -> Dict[str, Any]:
        """
        دریافت یک پیام با شناسه.

        پارامترها:
            object_guid (str): GUID چت.
            message_id (str): شناسه پیام.

        بازگشتی:
            dict: حاوی اطلاعات پیام.
        """
        payload = {"object_guid": object_guid, "message_id": message_id}
        return await self.network_manager.send_request("getMessageById", payload)

    async def forward_messages(self, object_guid: str, from_object_guid: str, message_ids: List[str]) -> Dict[str, Any]:
        """
        فوروارد کردن پیام‌ها.

        پارامترها:
            object_guid (str): GUID چت مقصد.
            from_object_guid (str): GUID چت مبدا.
            message_ids (list): لیستی از شناسه‌های پیام برای فوروارد.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid, "from_object_guid": from_object_guid, "message_ids": message_ids}
        return await self.network_manager.send_request("forwardMessages", payload)

    async def get_messages_by_id(self, object_guid: str, message_ids: List[str]) -> Dict[str, Any]:
        """
        دریافت چندین پیام با شناسه‌ها.

        پارامترها:
            object_guid (str): GUID چت.
            message_ids (list): لیستی از شناسه‌های پیام.

        بازگشتی:
            dict: حاوی اطلاعات پیام‌ها.
        """
        payload = {"object_guid": object_guid, "message_ids": message_ids}
        return await self.network_manager.send_request("getMessagesById", payload)

    async def get_message_link(self, object_guid: str, message_id: str) -> Dict[str, Any]:
        """
        دریافت لینک یک پیام.

        پارامترها:
            object_guid (str): GUID چت.
            message_id (str): شناسه پیام.

        بازگشتی:
            dict: حاوی لینک پیام.
        """
        payload = {"object_guid": object_guid, "message_id": message_id}
        return await self.network_manager.send_request("getMessageLink", payload)

    async def get_messages_updates(self, object_guid: str, min_id: Optional[str] = None, max_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        دریافت بروزرسانی‌های پیام‌ها.

        پارامترها:
            object_guid (str): GUID چت.
            min_id (str, اختیاری): حداقل شناسه پیام.
            max_id (str, اختیاری): حداکثر شناسه پیام.
            limit (int, اختیاری): تعداد پیام‌های قابل دریافت (پیش‌فرض: 20).

        بازگشتی:
            dict: حاوی اطلاعات بروزرسانی‌ها.
        """
        payload = {"object_guid": object_guid, "limit": limit}
        if min_id: payload["min_id"] = min_id
        if max_id: payload["max_id"] = max_id
        return await self.network_manager.send_request("getMessagesUpdates", payload)




    # متدهای استیکرها
    async def get_stickers_by_id(self, sticker_ids: List[str]) -> Dict[str, Any]:
        """
        دریافت اطلاعات استیکرها با شناسه‌هایشان.

        پارامترها:
            sticker_ids (list): لیستی از شناسه‌های استیکر.

        بازگشتی:
            dict: حاوی اطلاعات استیکرها.
        """
        payload = {"sticker_ids": sticker_ids}
        return await self.network_manager.send_request("getStickersById", payload)

    async def get_sticker_set_by_id(self, sticker_set_id: str) -> Dict[str, Any]:
        """
        دریافت اطلاعات یک مجموعه استیکر با شناسه.

        پارامترها:
            sticker_set_id (str): شناسه مجموعه استیکر.

        بازگشتی:
            dict: حاوی اطلاعات مجموعه استیکر.
        """
        payload = {"sticker_set_id": sticker_set_id}
        return await self.network_manager.send_request("getStickerSetById", payload)

    async def search_sticker_sets(self, query: str) -> Dict[str, Any]:
        """
        جستجوی مجموعه‌های استیکر.

        پارامترها:
            query (str): عبارت جستجو.

        بازگشتی:
            dict: حاوی نتایج جستجو.
        """
        payload = {"query": query}
        return await self.network_manager.send_request("searchStickerSets", payload)

    async def add_sticker_set(self, sticker_set_id: str) -> Dict[str, Any]:
        """
        افزودن یک مجموعه استیکر به لیست کاربر.

        پارامترها:
            sticker_set_id (str): شناسه مجموعه استیکر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"sticker_set_id": sticker_set_id}
        return await self.network_manager.send_request("addStickerSet", payload)

    async def remove_sticker_set(self, sticker_set_id: str) -> Dict[str, Any]:
        """
        حذف یک مجموعه استیکر از لیست کاربر.

        پارامترها:
            sticker_set_id (str): شناسه مجموعه استیکر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"sticker_set_id": sticker_set_id}
        return await self.network_manager.send_request("removeStickerSet", payload)

    async def get_my_sticker_sets(self) -> Dict[str, Any]:
        """
        دریافت لیست مجموعه‌های استیکر کاربر.

        بازگشتی:
            dict: حاوی اطلاعات مجموعه‌های استیکر.
        """
        return await self.network_manager.send_request("getMyStickerSets", {})

    async def get_trending_sticker_sets(self) -> Dict[str, Any]:
        """
        دریافت لیست مجموعه‌های استیکر پرطرفدار.

        بازگشتی:
            dict: حاوی اطلاعات مجموعه‌های استیکر پرطرفدار.
        """
        return await self.network_manager.send_request("getTrendingStickerSets", {})

    # متدهای مخاطبین
    async def get_all_contacts(self, start_id: Optional[str] = None) -> Dict[str, Any]:
        """
        دریافت تمام مخاطبین کاربر.

        پارامترها:
            start_id (str, اختیاری): شناسه شروع برای صفحه‌بندی.

        بازگشتی:
            dict: حاوی اطلاعات مخاطبین.
        """
        payload = {}
        if start_id: payload["start_id"] = start_id
        return await self.network_manager.send_request("getAllContacts", payload)

    async def get_contacts_updates(self) -> Dict[str, Any]:
        """
        دریافت بروزرسانی‌های مخاطبین.

        بازگشتی:
            dict: حاوی اطلاعات بروزرسانی‌ها.
        """
        return await self.network_manager.send_request("getContactsUpdates", {})

    async def delete_contact(self, object_guid: str) -> Dict[str, Any]:
        """
        حذف یک مخاطب.

        پارامترها:
            object_guid (str): GUID مخاطب مورد نظر.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        payload = {"object_guid": object_guid}
        return await self.network_manager.send_request("deleteContact", payload)

    async def search_contacts(self, search_text: str) -> Dict[str, Any]:
        """
        جستجو در میان مخاطبین.

        پارامترها:
            search_text (str): متن جستجو.

        بازگشتی:
            dict: حاوی نتایج جستجو.
        """
        payload = {"search_text": search_text}
        return await self.network_manager.send_request("searchContacts", payload)

