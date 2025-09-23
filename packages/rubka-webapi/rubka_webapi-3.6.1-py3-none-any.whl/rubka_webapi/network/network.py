# rubka_webapi/network/network.py

import httpx
import websockets
import json
from typing import Optional, Dict, Any

from ..crypto.crypto import CryptoManager
from ..utils.exceptions import RubikaException

class NetworkManager:
    """
    مدیریت کننده درخواست‌های شبکه برای API روبیکا.
    مسئول ارسال درخواست‌های HTTP و مدیریت اتصال WebSocket.
    """

    BASE_URL = "https://messengerg2c4.iranlms.ir"
    WEB_SOCKET_URL = "wss://messengerg2c4.iranlms.ir/" # این URL ممکن است نیاز به بررسی دقیق‌تر داشته باشد

    def __init__(
        self,
        auth_key: Optional[str] = None,
        private_key: Optional[str] = None,
        proxy: Optional[str] = None,
        time_out: int = 10
    ):
        self.auth_key = auth_key
        self.private_key = private_key
        self.proxy = proxy
        self.time_out = time_out
        self.http_client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=self.time_out, proxies=self.proxy)
        self.websocket = None
        self.crypto_manager = CryptoManager(private_key) if private_key else None

    async def send_request(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        ارسال درخواست HTTP به API روبیکا.

        پارامترها:
            method (str): نام متد API (مثلاً "getChats").
            payload (dict): داده‌های ارسالی به API.

        بازگشتی:
            dict: پاسخ از API.
        """
        headers = {
            "Auth": self.auth_key, # نیاز به بررسی نحوه ارسال Auth Key واقعی
            "Content-Type": "application/json"
        }
        
        if self.crypto_manager:
            signature = self.crypto_manager.sign_request(payload)
            headers["Signature"] = signature # فرض می‌کنیم امضا در هدر Signature ارسال می‌شود

        request_data = {
            "method": method,
            "input": payload,
            "api_version": "6", # یا هر نسخه دیگری که مناسب است
            "client": {
                "app_name": "Main",
                "app_version": "3.6.0",
                "platform": "Web",
                "package": "ir.rubika.web",
                "lang_code": "fa"
            }
        }

        try:
            response = await self.http_client.post("/", json=request_data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise RubikaException(f"خطای HTTP: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise RubikaException(f"خطای درخواست: {e}")

    async def connect_websocket(self):
        """
        برقراری اتصال WebSocket.
        """
        try:
            self.websocket = await websockets.connect(self.WEB_SOCKET_URL)
            print("اتصال WebSocket برقرار شد.")
        except Exception as e:
            raise RubikaException(f"خطا در اتصال WebSocket: {e}")

    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        دریافت پیام از WebSocket.
        """
        if not self.websocket:
            await self.connect_websocket()
        try:
            message = await self.websocket.recv()
            return json.loads(message)
        except websockets.exceptions.ConnectionClosedOK:
            print("اتصال WebSocket بسته شد.")
            self.websocket = None
            return None
        except Exception as e:
            print(f"خطا در دریافت پیام از WebSocket: {e}")
            return None

    async def send_websocket_message(self, data: Dict[str, Any]):
        """
        ارسال پیام از طریق WebSocket.
        """
        if not self.websocket:
            await self.connect_websocket()
        try:
            await self.websocket.send(json.dumps(data))
        except Exception as e:
            raise RubikaException(f"خطا در ارسال پیام از WebSocket: {e}")

    async def close(self):
        """
        بستن کلاینت HTTP و اتصال WebSocket.
        """
        await self.http_client.aclose()
        if self.websocket:
            await self.websocket.close()
            print("اتصال WebSocket بسته شد.")

