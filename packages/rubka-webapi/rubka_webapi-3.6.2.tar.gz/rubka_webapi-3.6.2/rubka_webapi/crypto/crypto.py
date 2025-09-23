# rubka_webapi/crypto/crypto.py

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5 as Signature_RSA
import base64
import json

class CryptoManager:
    """
    مدیریت کننده عملیات رمزنگاری برای API روبیکا.
    شامل توابعی برای امضای درخواست‌ها و رمزگشایی پاسخ‌ها.
    """

    def __init__(self, private_key_pem: str):
        """
        مقداردهی اولیه با کلید خصوصی RSA.

        پارامترها:
            private_key_pem (str): کلید خصوصی RSA در فرمت PEM.
        """
        self.private_key = RSA.import_key(private_key_pem)

    def sign_request(self, payload: Dict[str, Any]) -> str:
        """
        امضای یک درخواست با استفاده از کلید خصوصی.

        پارامترها:
            payload (dict): داده‌های درخواست که باید امضا شوند.

        بازگشتی:
            str: امضای دیجیتال به صورت base64 encoded.
        """
        message = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        h = SHA256.new(message)
        signer = Signature_RSA.new(self.private_key)
        signature = signer.sign(h)
        return base64.b64encode(signature).decode('utf-8')

    # در صورت نیاز به رمزگشایی پاسخ‌ها، متدهای مربوطه در اینجا اضافه می‌شوند.

