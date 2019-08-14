import time, requests
from datetime import datetime

date_ts = lambda t: time.mktime(datetime.strptime(t, "%Y-%m-%dT%XZ").timetuple())


def api_req(url, status = [200]):
    response = requests.get(url)

    if not response.status_code in status:
        raise BadAPIResponse(f"{response.url}\n{response.text}")

    return response.json()


class Image:
    def __init__(self, url, headers = {}):
        self.url = url
        self._content = None
        self._headers = headers

    def __repr__(self):
        return self.url

    @property
    def content(self):
        if not self._content:
            self._content = requests.get(self.url, headers = self._headers).content

        return self._content
