import time, requests
from datetime import datetime
from amino.util import exceptions

date_ts = lambda t: time.mktime(datetime.strptime(t, "%Y-%m-%dT%XZ").timetuple()) if t else None


def api_req(url, status = [200], params = {}, headers = {}):
    response = requests.get(url, params = params, headers = headers)

    if not response.status_code in status:
        raise exceptions.BadAPIResponse(f"{response.url}\n{response.text}")

    return response.json()


def api_req_paginated(url, key, params = {}, headers = {}, size = 5, is_dict = False):
    start = 0
    while True:
        data = api_req(url, params = {**params, "start": start, "size": size}, headers = headers)[key]
        start += size

        if not len(data):
            break

        for item in data:
            if is_dict:
                yield (item, data[item])
            else:
                yield item


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


class MediaItem:
    def __init__(self, data, headers = {}):
        self._content = None
        self._url = None
        self.__data = data
        self._headers = headers

    def __repr__(self):
        return f"[IMG={self.get(3)}]" if self.get(3) else ""

    @property
    def type(self):
        return {100: "image", 103: "youtube"}.get(self.get(0), "unknown")

    @property
    def url(self):
        if not self._url:
            self._url = self.__data[1]

            if self.type == "youtube":
                self._url = self._url.replace("ytv://", "https://www.youtube.com/watch?v=")

        return self._url

    @property
    def caption(self):
        return self.get(2)

    @property
    def key(self):
        return self.get(3)

    @property
    def _unknown_value(self):
        return self.get(4)

    @property
    def metadata(self):
        return self.get(5)

    def __getitem__(self, key):
        return self.__data[key]

    def get(self, key, default = None):
        try:
            return self[key]
        except IndexError:
            return default
