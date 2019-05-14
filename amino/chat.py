import json, requests
from time import time
from amino import community

class Thread:
    def __init__(self, data, client, lazy = True):
        """
        Build the client.
        """

        self.client = client
        self.community = None
        self.community_id = data["ndcId"]       # fetch community info somehow and generate a Community object
        self.members = data["membersSummary"]   # create a Peer object for each item in the list
        self.uid = data["threadId"]

        if not lazy:
            pass

    def send_text_message(self, message):
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
            f"{self.client.api}/x{self.community_id}/s/chat/thread/{self.uid}/message",
            data = data,
            headers = headers
        )
