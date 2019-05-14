import requests, json
from time import time
from amino import chat
from amino.lib.util import exceptions

class Community:
    def __init__(self, community):
        self.name = community["name"]
        self.endpoint = community["endpoint"]
        self.url = community["link"]
        self.id = community["ndcId"]
        self.member_count = community["membersCount"]

    def __repr__(self):
        return f"{self.name}"

class Peer:
    def __init__(self, user_data, client, community_obj = None, community_data = None):
        """
        Build the peer.
        user_data: json representing the peer
        client: logged in client or sub_client who the peer belongs to
        community_data: json info representing the community that the peer is attached to
        community_obj: an object representing the community that the peer is attached to. Takes precedence over community_data
        """
        self.community = community_obj if community_obj else Community(community_data) if community_data else None
        self.client = client
        self.uid = user_data["uid"]
        self.nick = user_data["nickname"]
        self._data = user_data

    def __repr__(self):
        """
        Represent the client with it's nickname
        """
        return self.nick

    def get_pm_thread(self, lazy = True):
        """
        Request the pm channel for a peer from amino.
        If there is one (both users have accepted the chat) a Thread is returned
        If there is not one, None is returned
        lazy: the lazy parameter to be passed on to the Thread constructor in the event that a thread exists
        """
        params = {
            "type": "exist-single",
            "cv": "1.2",
            "q": self.uid
        }

        headers = self.client.headers()

        response = requests.get(f"{self.client.api}/x{self.community.id}/s/chat/thread", params = params, headers = headers)

        if response.status_code == 200:
            return chat.Thread(json.loads(response.text)["threadList"][0], self.client, lazy = lazy)

        if json.loads(response).get("api:statuscode", False) == 1600:
            return None

        else: raise exceptions.UnknownResponse

    def open_thread(self, message = None):
        """
        Ask a user to open a chat with them.
        message: message to send with the request, or None
        """
        if not self.community:
            raise exceptions.NoCommunity

        data = {
            "type": 0,
            "inviteeUids": [self.uid],
            "timestamp": int(time() * 1000)
        }

        if message:
            data["initialMessageContent"] = message

        data = json.dumps(data)
        headers = self.client.headers(data)

        response = requests.post(f"{self.client.api}/x{self.community.id}/s/chat/thread", data = data, headers = headers)

        return response

    def send_text_message(self, message, allow_new = True):
        """
        Send a message to a user.
        message: message to send to the peer
        allow_new: if there is no open thread we will send an open_thread request
        """
        thread = self.get_pm_thread()

        return thread.send_text_message(message)

        timestamp = int(time() * 1000)

        data = json.dumps({
            "type": 0,
            "content": message,
            "attachedObject": None,
            "timestamp": timestamp,
            "clientRefId": int(timestamp / 10 % 1000000000)
        })

        headers = self.client.headers(data)

        self.h, self.d = headers, data

        return requests.post(
            f"{self.client.api}/x{self.community.id}/s/chat/thread/{self.uid}/message",
            data = data,
            headers = headers
        )
