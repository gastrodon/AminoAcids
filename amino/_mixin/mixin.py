import json, os, threading, time, warnings, requests
from locale import getdefaultlocale
from pathlib import Path
from amino.util import helpers, exceptions


class MainMixin:
    def __init__(self, data = None):
        self._object_data_payload = data
        self._images = {}
        self._url = None
        self._update = False

    def _get_prop(self, key, default = None):
        if key not in self._object_data:
            return self.fresh._object_data.get(key, default)

        return self._object_data.get(key, default)

    def _get_pic_prop(self, key):
        if key not in self._images or self._update:
            self._images[key] = helpers.Image(self._get_prop(key), headers = self.client.headers)

        return self._images[key]

    def _get_time(self, key, default = None):
        t = self._get_prop(key, default)
        return helpers.date_ts(t) if t != default else t

    @property
    def _object_data(self):
        raise NotImplementedError

    @property
    def fresh(self):
        """
        :returns: self with update flag
        :rtype:
        """
        self._update = True
        return self


class ClientMixin(MainMixin):
    _api = "https://service.narvii.com/api/v1"
    # device id was taken from a device I don't use. That being said, please don't abuse it.
    _device_id = "010E4A69D1B3066CA9A127890A5531929F3818F16BA22092D5A91DEFB2CB73F53648E28EFAB98A4B61"

    # TODO:  test if I need this after loggin in
    # _device_sig = "AaauX/ZA2gM3ozqk1U5j6ek89SMu"

    def __init__(self, socket_trace = False, api = None):
        super().__init__(data = None)
        self.api = api if api else self._api
        self.authenticated = False
        self.configured = False

        self._url = f"{self.api}/g/s/account"

        # account auth stuff
        self._sid = None
        self._auid = None
        self._secret = None

        # io locks
        self.config_lock = threading.Lock()

        # config file stuff
        self._config = None
        self._config_dir = f"{Path.home()}/.aminoacids"
        self._config_file = f"{self._config_dir}/config.json"

        if not os.path.isdir(self._config_dir):
            os.mkdir(self._config_dir)

        try:
            with open(self._config_file) as stream:
                self._config = json.load(stream)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.config = {}

    # public properties

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        """
        Config setter.

        For updating config values, do not ``client.config["foo"] = "bar", as this will not trigger this setter.
        Instead, merge dics like so ``client.config = {**client.config, "foo": "bar"}
        """
        if not isinstance(value, dict):
            raise TypeError(f"Value must be a class of dict, not {type(value)}")

        self.config_lock.acquire()

        with open(self._config_file, "w") as stream:
            json.dump(value, stream)

        with open(self._config_file) as stream:
            self._config = json.load(stream)

        self.config_lock.release()

    @property
    def headers(self):
        """
        Headers for a client that is not logged in, default device id

        :returns: headers
        :rtype: dict
        """
        _headers = {"NDCDEVICEID": self._device_id}

        if self._sid:
            _headers["NDCAUTH"] = f"sid={self._sid}"

        if self._auid:
            _headers["AUID"] = self._auid

        return _headers

    # public methods

    def configure_client(self):
        """
        Configure the client by sending device info to Amino.

        :returns: self
        :rtype: ClientMixin
        """

        data = json.dumps({
            "bundleID": "com.narvii.master",
            "clientCallbackURL": "narviiapp://default",
            "deviceID": self._device_id,
            "timezone": 0 - time.timezone // 60,
            "locale": "en_US",
            "timestamp": int(time.time() * 1000),
            "systemPushEnabled": 1,
            "clientType": 100
        })

        response = requests.post(f"{self.api}/g/s/device", data = data, headers = self.headers)

        if response.status_code != 200:
            raise util.BadAPIResponse(f"{response.url}\n{response.text}")

        return self


class ObjectMixin(MainMixin):
    def __init__(self, id, client = ClientMixin(), data = None):
        super().__init__(data = data)
        self.id = id
        self.client = client

    @property
    def headers(self):
        """
        Alias for ``ObjectMixin.client.headers``
        """
        return self.client.headers
