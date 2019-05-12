import requests, json, time
from lib import exceptions

class Client:
    api = "https://service.narvii.com/api/v1"
    user_agent = "Dalvik/2.1.0 (Linux; U; Android 6.0; LG-UK495 Build/MRA58K; com.narvii.amino.master/2.0.24532)"
    device_id = "010E4A69D1B3066CA9A127890A5531929F3818F16BA22092D5A91DEFB2CB73F53648E28EFAB98A4B61"
    device_id_sig = "AbIkXPl49A/pCMJZGQtomJRFdHDg"



    def __init__(self, user_agent = user_agent, device_id = device_id, api = api):
        self.authenticated = False
        self.configured = False
        self.api = api
        self.user_agent = user_agent
        self.device_id = device_id
        headers = {
            "User-Agent": self.user_agent,
            "NDCDEVICEID": self.device_id,
            "Accept-Language": "en-US",
            "Accept-Encoding": "gzip"
        }

        response = requests.get(f"{self.api}/g/s/auth/config", headers = headers)
        response_data = json.loads(response.text)

        if response.status_code is 200:
            self._config_json = response_data
            self.configured = True
        else:
            raise exceptions.UnknownResponse

    def login(self, email, password):

        data = {
            "email": email,
            "v": 2,
            "secret" : f"0 {password}",
            "deviceID": self.device_id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time.time() * 1000)
        }

        headers = {
            "NDCDEVICEID" : self.device_id,
            "NDC-MSG-SIG": self.device_id_sig,
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent" : self.user_agent,
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Content-Length": str(len(json.dumps(data))),
            "Connection": "keep-alive"

        }

        response = requests.post(f"{self.api}/g/s/auth/login", data = json.dumps(data), headers = headers)

        if response.status_code == 200:
            self._handle_login()
            self.authenticated = True
        if response.status_code == 400 and response_data["api:statuscode"] == 200:
            raise exceptions.FailedLogin
        else:
            raise exceptions.UnknownResponse

    def _handle_login(self, data):
        self.uid = data["auid"]
        self.secret = data["secret"]
        self.sid = data["sid"]
        self.profile = data["userProfile"]
        self.nick = data["userProfile"]["nickname"]
