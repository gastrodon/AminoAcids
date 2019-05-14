import requests, json, os
from locale import getdefaultlocale as locale
from time import time, timezone
from amino import community
from amino.lib.util import exceptions, helpers

class Client:
    def __init__(self, path = "device.json"):
        """
        Build the client.
        path: optional location where the generated device info will be stored
        path is relative to where Client is called from (ie the file in which it's imported) and can be
        """
        try:
            with open(f"{path}", "r") as stream:
                device_info = json.load(stream)
            new_device = False

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            device_info = helpers.generate_device_info()
            with open(f"{path}", "w") as stream:
                json.dump(device_info, stream)
            new_device = True

        self.api = "https://service.narvii.com/api/v1"
        self.authenticated = False
        self.configured = False
        self.sid = None
        self.nick = "whoami"
        self.user_agent = device_info["user_agent"]
        self.device_id = device_info["device_id"]
        self.device_id_sig = device_info["device_id_sig"]

        self.client_config()

    def __repr__(self):
        """
        Represent the Client by it's nickname
        """
        return self.nick

    def client_config(self):
        """
        Configure the client by sending Amino data about the device id and such.
        sets the class' configured value if the server returns a 200 status_code
        """
        data = json.dumps({
            "deviceID": self.device_id,
            "bundleID": "com.narvii.amino.master",
            "clientType": 100,
            "timezone": -timezone // 1000,
            "systemPushEnabled": True,
            "locale": locale()[0],
            "timestamp": int(time() * 1000)
        })

        headers = self.headers(data)

        response = requests.post(f"{self.api}/g/s/device", headers = headers, data = data)

        if response.status_code == 200:
            self.configured = True

    def headers(self, data = None):
        """
        Macro for generating headers for a request.
        data: string representing what's in the post data of the request we want headers for, or None for a get request
        returns a dict containint generated headers
        """
        headers = {
            "NDCDEVICEID": self.device_id,
            "NDC-MSG-SIG": self.device_id_sig,
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": self.user_agent,
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }

        if data:
            headers["Content-Length"] = str(len(data))

        if self.sid:
            headers["NDCAUTH"] = f"sid={self.sid}"

        return headers

    def login(self, email, password):
        """
        Send a login request to Amino
        email: emial address associated with the account
        password: password associated with the account
        """
        data = json.dumps({
            "email": email,
            "v": 2,
            "secret": f"0 {password}",
            "deviceID": self.device_id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time() * 1000)
        })

        headers = self.headers(data = data)
        response = requests.post(f"{self.api}/g/s/auth/login", data = data, headers = headers)

        if response.status_code == 400:
            response = json.loads(response.text)
            if response["api:statuscode"] == 200:
                raise exceptions.FailedLogin

            else:
                raise exceptions.UnknownResponse

        response = json.loads(response.text)
        self.authenticated = True
        self.uid = response["auid"]
        self.secret = response["secret"]
        self.sid = response["sid"]
        self.profile = response["userProfile"]
        self.nick = response["userProfile"]["nickname"]
        self.sub_clients = self.get_sub_clients()

    def get_sub_clients(self):
        """
        Generates a dict of SubClients that this client owns.
        returns a dict with endpoint:SubClient objects
        """
        if not self.authenticated:
            raise exceptions.NotLoggedIn

        params = {
            "size": 50,
            "start": 0
        }

        headers = self.headers()
        response = requests.get(f"{self.api}/g/s/community/joined", params = params, headers = headers)

        if response.status_code != 200:
            raise exceptions.UnknownResponse

        response = json.loads(response.text)
        clients = {}

        for data in response["communityList"]:
            profile = response["userInfoInCommunities"][str(data["ndcId"])]["userProfile"]
            clients[data["endpoint"]] = SubClient(profile, self.sid, community_data = data)

        return clients

class SubClient(Client):
    """
    A representation of a user on an amino.
    This is different than the parent Client, as amino has different account info for each amino that a user has joined
    """
    def __init__(self, user_data, sid, community_data = None, community_obj = None):
        """
        Build the client.
        user_data: json info with the user info to build the info from
        sid: the client's sid. This is needed for forming any post-login requests (ie all of them)
        community_data: json info representing the community that the client is attached to
        community_obj: an object representing the community that the client is attached to. Takes precedence over community_data
        """
        Client.__init__(self)
        if not community and not community_data:
            raise exceptions.NoCommunity

        self.community = community_obj if community_obj else community.Community(community_data)
        self.uid = user_data["uid"]
        self.nick = user_data["nickname"]
        self.sid = sid

    def peer_search(self, query = None, type = "all"):
        """
        Search for peers on this clients amino community.

        query: search search string, or none for an unfiltered search
        type: I don't know, but it's in the api
        """
        headers = self.headers()

        params = {
            "start": 0,
            "size": 25,
            "type": type
        }

        if query:
            params["q"] = query

        response = requests.get(f"{self.api}/x{self.community.id}/s/user-profile", params = params)

        if response.status_code != 200:
            raise exceptions.UnknownResponse

        response = json.loads(response.text)

        return [community.Peer(item, self, community_obj = self.community) for item in response["userProfileList"]]
