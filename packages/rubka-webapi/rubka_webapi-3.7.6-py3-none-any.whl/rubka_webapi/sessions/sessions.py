from os.path import exists
from json import loads, dumps

class Sessions:

    def __init__(self, client: object) -> None:
        self.client = client

    def check_session_exists(self):
        return exists(f"{self.client.session}.rubka")  # session file with .rubka extension
    
    def load_session_data(self):
        return loads(open(f"{self.client.session}.rubka", encoding="UTF-8").read())
        
    def create_session(self):
        from ..methods import Methods
        methods: object = Methods(
            sessionData={},
            platform=self.client.platform,
            apiVersion=6,
            proxy=self.client.proxy,
            timeOut=self.client.timeOut,
            showProgressBar=True
        )

        while True:
            phone_number: str = input("Enter your phone number » ")
            try:
                send_code_data: dict = methods.sendCode(phoneNumber=phone_number)
            except:
                print("Invalid phone number! Please try again.")
                continue

            if send_code_data['status'] == 'SendPassKey':
                while True:
                    pass_key: str = input(f'\nEnter pass key [{send_code_data.get("hint_pass_key", "")}] » ')
                    send_code_data: dict = methods.sendCode(phoneNumber=phone_number, passKey=pass_key)
                    
                    if send_code_data['status'] == 'InvalidPassKey':
                        print("Invalid pass key! Please try again.")
                        continue
                    break
            
            while True:
                phone_code: str = input("\nEnter the code » ").strip()
                sign_in_data: dict = methods.signIn(
                    phoneNumber=phone_number, 
                    phoneCodeHash=send_code_data['phone_code_hash'], 
                    phoneCode=phone_code
                )
                if sign_in_data['status'] != 'OK':
                    print("Invalid code! Please try again.")
                    continue
                break
            
            from ..crypto import Cryption

            session_data = {
                'auth': Cryption.decryptRsaOaep(sign_in_data["private_key"], sign_in_data['auth']),
                'private_key': sign_in_data["private_key"],
                'user': sign_in_data['user'],
            }

            open(f"{self.client.session}.rubka", "w", encoding="UTF-8").write(dumps(session_data, indent=4))

            Methods(
                sessionData=session_data,
                platform=self.client.platform,
                apiVersion=6,
                proxy=self.client.proxy,
                timeOut=self.client.timeOut,
                showProgressBar=True
            ).registerDevice(deviceModel=f"rubka_webapi-{self.client.session}")

            print(f"\nSigned in as \"{self.client.session}\" successfully.")

            return session_data