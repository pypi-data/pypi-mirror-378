from os.path import exists
from json import loads, dumps

class Sessions:
    def __init__(self, client: object) -> None:
        self.client = client
        # ذخیره موقت اطلاعات کاربران: {user_id: {"phone": str, "hash": str}}
        self._pending_logins = {}

    def checkSessionExists(self, user_id: int) -> bool:
        return exists(f"{self.client.session}_{user_id}.rub")

    def loadSessionData(self, user_id: int) -> dict:
        with open(f"{self.client.session}_{user_id}.rub", encoding="UTF-8") as f:
            return loads(f.read())

    def sendPhoneNumber(self, user_id: int, phoneNumber: str, passKey: str = None, timeout: int = 60) -> str:
        """ارسال شماره و دریافت phone_code_hash"""
        from ..methods import Methods

        methods = Methods(
            sessionData={},
            platform=self.client.platform,
            apiVersion=6,
            proxy=self.client.proxy,
            timeOut=timeout,
            showProgressBar=True
        )

        sendCodeData = methods.sendCode(phoneNumber=phoneNumber, passKey=passKey)
        if sendCodeData['status'] == 'SendPassKey' and passKey:
            sendCodeData = methods.sendCode(phoneNumber=phoneNumber, passKey=passKey)

        phone_code_hash = sendCodeData.get('phone_code_hash')
        if not phone_code_hash:
            raise ValueError("phone_code_hash دریافت نشد!")

        # ذخیره اطلاعات این کاربر
        self._pending_logins[user_id] = {
            "phone": phoneNumber,
            "hash": phone_code_hash
        }

        return phone_code_hash

    def signInWithCode(self, user_id: int, phoneCode: str, timeout: int = 60) -> dict:
        """ورود با کد تأیید و ساخت سشن"""
        if user_id not in self._pending_logins:
            raise ValueError("برای این کاربر شماره ثبت نشده است.")

        from ..methods import Methods
        from ..crypto import Cryption

        phoneNumber = self._pending_logins[user_id]["phone"]
        phone_code_hash = self._pending_logins[user_id]["hash"]

        methods = Methods(
            sessionData={},
            platform=self.client.platform,
            apiVersion=6,
            proxy=self.client.proxy,
            timeOut=timeout,
            showProgressBar=True
        )

        signInData = methods.signIn(
            phoneNumber=phoneNumber,
            phoneCodeHash=phone_code_hash,
            phoneCode=phoneCode
        )

        sessionData = {
            'auth': Cryption.decryptRsaOaep(signInData["private_key"], signInData['auth']),
            'private_key': signInData["private_key"],
            'user': signInData['user'],
        }

        with open(f"{self.client.session}_{user_id}.rub", "w", encoding="UTF-8") as f:
            f.write(dumps(sessionData, indent=4))

        Methods(
            sessionData=sessionData,
            platform=self.client.platform,
            apiVersion=6,
            proxy=self.client.proxy,
            timeOut=timeout,
            showProgressBar=True
        ).registerDevice(deviceModel=f"rubika-Api-{self.client.session}")

        # حذف از لیست موقت بعد از ثبت موفق
        del self._pending_logins[user_id]

        print(f"\nSign successful for user {user_id} ✅")
        return sessionData