# rubka_webapi/types/message.py

from typing import Dict, Any, Optional

class Message:
    """
    کلاس Message نماینده یک پیام دریافت شده از روبیکا است.
    این کلاس شامل اطلاعات مربوط به پیام و متدهایی برای پاسخ دادن به آن می‌باشد.
    """
    def __init__(self, client_instance, message_data: Dict[str, Any]):
        self._client = client_instance # ارجاع به نمونه کلاینت برای ارسال پاسخ
        self.message_data = message_data

        self.object_guid: str = message_data.get("object_guid", "")
        self.message_id: str = message_data.get("message_id", "")
        self.text: str = message_data.get("text", "")
        self.author_guid: str = message_data.get("author_guid", "")
        self.is_edited: bool = message_data.get("is_edited", False)
        self.is_deleted: bool = message_data.get("is_deleted", False)
        self.file_id: Optional[str] = message_data.get("file_id")
        self.file_type: Optional[str] = message_data.get("file_type")

    async def reply(self, text: str) -> Dict[str, Any]:
        """
        برای پاسخ دادن به پیام دریافت شده.

        پارامترها:
            text (str): متن پاسخ.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        if not self.object_guid or not self.message_id:
            raise ValueError("Cannot reply to a message without object_guid or message_id.")
        
        # فرض می‌کنیم متد send_text در client_instance وجود دارد
        return await self._client.send_text(self.object_guid, text, message_id=self.message_id)

    async def edit(self, text: str) -> Dict[str, Any]:
        """
        برای ویرایش پیام فعلی (اگر پیام توسط ربات ارسال شده باشد).

        پارامترها:
            text (str): متن جدید پیام.

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        if not self.object_guid or not self.message_id:
            raise ValueError("Cannot edit a message without object_guid or message_id.")
        
        # فرض می‌کنیم متد edit_message در client_instance وجود دارد
        return await self._client.edit_message(self.object_guid, self.message_id, text)

    async def delete(self) -> Dict[str, Any]:
        """
        برای حذف پیام فعلی (اگر پیام توسط ربات ارسال شده باشد).

        بازگشتی:
            dict: حاوی اطلاعات پاسخ API.
        """
        if not self.object_guid or not self.message_id:
            raise ValueError("Cannot delete a message without object_guid or message_id.")
        
        # فرض می‌کنیم متد delete_message در client_instance وجود دارد
        return await self._client.delete_message(self.object_guid, self.message_id)

    def __repr__(self) -> str:
        return f"<Message id={self.message_id} from={self.author_guid} chat={self.object_guid} text=\"{self.text[:20]}...\">"

