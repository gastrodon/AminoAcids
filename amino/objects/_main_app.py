import requests, json, time

from amino._mixin import mixin
from amino.util import helpers, exceptions


class Client(mixin.ClientMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _object_data(self):
        if not self.authenticated:
            raise exceptions.NotAuthenticated("No user authenticated")

        if self._object_data_payload is None or self._update:
            self._update = False
            response = requests.get(self._url, headers = self.headers)

            if response.status_code != 200:
                raise exceptions.BadAPIResponse(f"{response.url}\n{response.text}")

            self._object_data_payload = response.json()["account"]

        return self._object_data_payload

    def login(self, email, password, force = False):
        """
        Login to Amino and get an api-key.
        You might need to ``configure_client``
        You also might need to solve a captcha, functionality for that  may come soon

        :param email: email associated with this account
        :param password: password to this account
        :param force: bypass saved tokens and force a new login

        :type email: str
        :type password: str
        :type force: bool

        :returns: self
        :rtype: Client
        """
        if self.authenticated:
            raise exceptions.AlreadyAuthenticated("instance has an authenticated user")

        if f"{email}" in self.config and not force:
            _user_config = self.config[f"{email}"]
            self._secret = _user_config.get("secret")
            self._sid = _user_config.get("sid")

            response = requests.get(f"{self.api}/g/s/account", headers = self.headers)

            if response.status_code == 200:
                self.authenticated = True
                return self

        data = json.dumps({
            "email": email,
            "v": 2,
            "secret": self._secret if self._secret else f"0 {password}",
            "deviceID": self._device_id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time.time() * 1000)
        })

        response = requests.post(f"{self.api}/g/s/auth/login", data = data, headers = self.headers)

        data = response.json()

        if response.status_code == 400:
            if data["api:statuscode"] == 200:
                raise exceptions.FailedLogin("Could not log in with this info")
            if data["api:statuscode"] == 270:
                raise exceptions.Captcha("This device needs to be verified with a captcha")
            else:
                raise exceptions.BadAPIResponse(f"{response.url}\n{response.text}")

        self.authenticated = True
        self._sid = data["sid"]
        self._auid = data["auid"]
        self._secret = data.get("secret", self._secret)
        self.config = {**self.config, f"{email}": {"secret": self._secret, "sid": self._sid}}

        return self

    @property
    def status(self):
        """
        :returns: account status
        :rtype: int
        """
        # TODO more research
        return self._get_prop("status")

    @property
    def uid(self):
        """
        :returns: account uid (auid)
        :rtype: str
        """
        return self._get_prop("uid")

    @property
    def nickname(self):
        """
        :returns: account nickname (nick)
        :rtype: str
        """
        return self._get_prop("nickname")

    @property
    def nick(self):
        """
        Alias to ``client.nickname``
        """
        return self.nickname

    @property
    def phone_activated(self):
        """
        :returns: does this account have an activated phone?
        :rtype: bool
        """
        return bool(self._get_prop("phoneNumberActivation", False))

    @property
    def email_activated(self):
        """
        :returns: does this account have an activated email?
        :rtype: bool
        """
        return bool(self._get_prop("emailActivation", False))

    @property
    def amino_id(self):
        """
        :return: unique amino id (@)
        :rtype: str
        """
        return self._get_prop("aminoId")

    @property
    def amino_id_editable(self):
        """
        :return: is ``self.amino_id`` editable?
        :rtype: bool
        """
        return self._get_prop("aminoIdEditable")

    @property
    def facebook_id(self):
        """
        :returns: account facebook id
        :rtype: bool
        """
        return self._get_prop("facebookID")

    @property
    def twitter_id(self):
        """
        :returns: account twitter id
        :rtype: str
        """
        return self._get_prop("twitterID")

    @property
    def google_id(self):
        """
        :returns: account google id
        :rtype: str
        """
        return self._get_prop("googleID")

    @property
    def amplitude_id(self):
        """
        :returns: account amplitude id, if amplitude analytics enabled
        :rtype: str
        """
        return self._get_prop("advancedSettings", {}).get("amplitudeAppId")

    @property
    def birthdate(self):
        """
        :returns: account birthdate timestamp
        :rtype: float
        """
        return self._get_time("dateOfBirth")

    @property
    def role(self):
        """
        :returns: account role
        :rtype: int
        """
        # TODO more research
        return self._get_prop("role")

    @property
    def latitude(self):
        """
        :returns: account latitude
        :rtype: str
        """
        return self._get_prop("latitude")

    @property
    def longitude(self):
        """
        :returns: account longitude
        :rtype: str
        """
        return self._get_prop("longitude")

    @property
    def address(self):
        """
        :returns: account address (unable to test)
        :rtype: ?
        """
        return self._get_prop("address")

    @property
    def phone_number(self):
        """
        :returns: account phone number
        :rtype: str
        """
        return self._get_prop("phoneNumber")

    @property
    def email(self):
        """
        :returns: account email
        :rtype: str
        """
        return self._get_prop("email")

    @property
    def username(self):
        """
        :returns: account username
        :rtype: str
        """
        return self._get_prop("username")

    @property
    def last_modified(self):
        """
        :returns: last modification timestamp
        :rtype: float
        """
        return self._get_time("modifiedTime")

    @property
    def created(self):
        """
        :returns: creation timestamp
        :rtype: float
        """
        return self._get_time("createdTime")

    @property
    def activation(self):
        """
        :returns: activation status
        :rtype: int
        """
        return self._get_prop("activation")

    @property
    def membership(self):
        """
        :returns: membership status (unable to test)
        :rtype: ?
        """
        # TODO more research
        return self._get_prop("membership")

    @property
    def icon(self):
        """
        :returns: acount icon image
        :rtype: Image
        """
        return self._get_pic_prop("icon")

    @property
    def security_level(self):
        """
        :returns: account security level
        :rtype: int
        """
        return self._get_prop("securityLevel")

    @property
    def gender(self):
        """
        :returns: account gender
        :rtype: str
        """
        return self._get_prop("gender")


class Community(mixin.ObjectMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug = self.id
        self._url = f"{self.client.api}/g/s-x{self.id}"

    def __repr__(self):
        return self.endpoint

    @property
    def _object_data(self):
        if self._object_data_payload is None or self._update:
            self._update = False
            response = requests.get(f"{self._url}/community/info", headers = self.headers)

            if response.status_code != 200:
                raise exceptions.BadAPIResponse(f"{response.url}\n{response.text}")

            self._object_data_payload = response.json()["community"]

        return self._object_data_payload

    @property
    def kindred(self):
        """
        :returns: kindred communities (Leader Pics)
        :rtype: list<Community>
        """
        response = helpers.api_req(f"{self._url}/community/kindred")
        return (Community(data["ndcId"], client = self.client, data = data) for data in response["communityList"])

    @property
    def tagline(self):
        """
        :returns: community tagline
        :rtype: str
        """
        return self._get_prop("tagline")

    @property
    def searchable(self):
        """
        :returns: is this community searchable?
        :rtype: bool
        """
        return self._get_prop("searchable")

    @property
    def influencerList(self):
        """
        :returns: list of influencers
        :rtype: ?
        """
        return self._get_prop("influencerList")

    @property
    def last_modified(self):
        """
        :returns: last modification timestamp
        :rtype: float
        """
        return self._get_time("modifiedTime")

    @property
    def theme_pack(self):
        """
        :returns: theme pack data (more soon)
        :rtype: dict
        """
        # TODO objectify
        return self._get_prop("themePack")

    @property
    def primaryLanguage(self):
        """
        :returns: primary natural language
        :rtype: str
        """
        return self._get_prop("primaryLanguage")

    @property
    def promotional_media(self):
        """
        :returns: current promotional media (more soon)
        :rtype: list<dict>
        """
        # TODO objectify
        return self._get_prop("promotionalMediaList")

    @property
    def joinType(self):
        """
        :returns: join type (needs testing)
        :rtype: int
        """
        # TODO more research
        return self._get_prop("joinType")

    @property
    def agent(self):
        """
        :returns: community agent (owner) (more soon)
        :rtype: dict
        """
        # TODO objectify a User
        return self._get_prop("agent")

    @property
    def icon(self):
        """
        :returns: community icon
        :rtype: Image
        """
        return self._get_pic_prop("icon")

    @property
    def advanced_settings(self):
        """
        :returns: community advanced settings (more soon)
        :rtype: dict
        """
        # TODO objectify
        return self._get_prop("advancedSettings")

    @property
    def user_added_topics(self):
        """
        :returns: user added topic list (more soon)
        :rtype: list<dict>
        """
        # TODO objectify
        return self._get_prop("userAddedTopicList")

    @property
    def template_id(self):
        """
        :returns: template id
        :rtype: int
        """
        # TODO more research
        return self._get_prop("templateId")

    @property
    def link(self):
        """
        :returns: url to this amino
        :rtype: str
        """
        return self._get_prop("link")

    @property
    def url(self):
        """
        Alias for Community.link
        """
        return self.link

    @property
    def status(self):
        """
        :returns: community status
        :rtype: int
        """
        # TODO more research
        return self._get_prop("status")

    @property
    def keywords(self):
        """
        :returns: community keywords
        :rtype: list<str>
        """
        return self._get_prop("keywords", "").split(",")

    @property
    def configuration(self):
        """
        :returns: community configuration (more soon)
        :rtype: dict
        """
        # TODO objectify
        return self._get_prop("configuration")

    @property
    def is_standalone_app(self):
        """
        :returns: is this community a standalone app?
        :rtype: bool
        """
        # TODO more research
        return self._get_prop("isStandaloneAppDeprecated")

    @property
    def name(self):
        """
        :returns: community name
        :rtype: str
        """
        return self._get_prop("name")

    @property
    def extensions(self):
        """
        :returns: community extensions (more soon)
        :rtype: dict
        """
        return self._get_prop("extensions")

    @property
    def aliases(self):
        """
        :returns: community name aliases
        :rtype: list<str>
        """
        return self.extensions.get("communityNameAliases", "").split(",")

    @property
    def heads(self):
        """
        :returns: community heads (leaders, curators, ect) (more soon)
        :rtype: list<dict>
        """
        # TODO objectify
        return self._get_prop("communityHeadList")

    @property
    def probation_status(self):
        """
        :returns: community probation status
        :rtype: int
        """
        return self._get_prop("probationStatus")

    @property
    def standalone_app_monetized(self):
        """
        :returns: is this communities standalone app monetized?
        :rtype: bool
        """
        return self._get_prop("isStandaloneAppMonetizationEnabled")

    @property
    def heat_level(self):
        """
        :returns: community heat level
        :rtype: int
        """
        return self._get_prop("communityHeat")

    @property
    def member_count(self):
        """
        :returns: number of members in community
        :rtype: int
        """
        return self._get_prop("membersCount")

    @property
    def media_list(self):
        """
        :returns: media list for media content (more soon)
        :rtype: list<list<*>>
        """
        # TODO objectify
        return self._get_prop("mediaList")

    @property
    def content(self):
        """
        :returns: community blog (more soon)
        :rtype: str
        """
        # TODO objectify
        return self._get_prop("content")

    @property
    def tags(self):
        """
        :returns: community tag list (more soon)
        :rtype: list<dict>
        """
        # TODO objectify
        return self._get_prop("communityTagList")

    @property
    def created(self):
        """
        :returns: creation timestamp
        :rtype: float
        """
        return self._get_time("createdTime")

    @property
    def endpoint(self):
        """
        :returns: community endpoint
        :rtype: str
        """
        return self._get_prop("endpoint")


class User(mixin.ObjectMixin):
    def __init__(self, *args, ndcid = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self._ndcid = ndcid

        if self._ndcid == 0:
            self._url = f"{self.client.api}/g/s/user-profile/{self.id}"
        else:
            self._url = f"{self.client.api}/x{self._ndcid}/s/user-profile/{self.id}"

    def __repr__(self):
        return self._get_prop("nickname", "")

    @property
    def _object_data(self):
        if self._object_data_payload is None or self._update:
            self._update = False
            response = requests.get(self._url, headers = self.headers)

            if response.status_code != 200:
                raise BadAPIResponse(f"{response.url}\n{response.text}")

            self._object_data_payload = response.json()["userProfile"]

        return self._object_data_payload

    @property
    def status(self):
        """
        :returns: user status
        :rtype: int
        """
        # TODO more research
        return self._get_prop("status")

    @property
    def uid(self):
        """
        :returns: user uid (auid)
        :rtype: str
        """
        return self._get_prop("uid")

    @property
    def nickname(self):
        """
        :returns: user nickname (nick)
        :rtype: str
        """
        return self._get_prop("nickname")

    @property
    def nick(self):
        """
        Alias to ``User.nickname``
        """
        return self.nickname

    @property
    def amino_id(self):
        """
        :return: unique amino id (@)
        :rtype: str
        """
        return self._get_prop("aminoId")

    @property
    def last_modified(self):
        """
        :returns: last modification timestamp
        :rtype: float
        """
        return self._get_time("modifiedTime")

    @property
    def created(self):
        """
        :returns: creation timestamp
        :rtype: float
        """
        return self._get_time("createdTime")

    @property
    def icon(self):
        """
        :returns: acount icon image
        :rtype: Image
        """
        return self._get_pic_prop("icon")

    @property
    def mood_sticker(self):
        """
        :returns: user's mood sticker data
        :rtype: dict
        """
        self._get_prop("moodSticker")

    @property
    def mood(self):
        """
        :returns: user's mood data
        :rtype: dict
        """
        self._get_prop("mood")

    @property
    def comment_count(self):
        """
        :returns: number of comments on a user's wall
        :rtype: int
        """
        return self._get_prop("commentsCount")

    @property
    def stroy_count(self):
        """
        :returns: number of stories from a user
        :rtype: int
        """
        return self._get_prop("storiesCount")

    @property
    def item_count(self):
        """
        :returns: number of items attached to a user
        :rtype: int
        """
        # TODO more research
        return self._get_prop("itemsCount")

    @property
    def global_user(self):
        """
        :returns: is this user global?
        :rtype: bool
        """
        # TODO more research
        return self._get_prop("isGloba")

    # community dependant properties

    @property
    def community(self):
        """
        :returns: attached Community
        :rtype: Community
        """
        self._ndcid = self._get_prop("ndcId", self._ndcid)

        if self._ndcid == 0:
            return None

        return Community(self._ndcid, client = self.client)

    @property
    def check_in_streak(self):
        """
        :returns: user's check in streak for a Community
        :rtype: int
        """
        return self._get_prop("consecutiveCheckInDays")

    @property
    def level(self):
        """
        :returns: user's level for a Community (more soon)
        :rtype: int
        """
        # TODO objectify
        return self._get_prop("level")

    @property
    def reputation(self):
        """
        :returns: user's reputatoin for a Community
        :rtype: int
        """
        return self._get_prop("reputation")

    @property
    def post_count(self):
        """
        :returns number of posts a user has made on a Community
        :rtype: int
        """
        # TODO more research
        return self._get_prop("postsCount")

    @property
    def blog_count(self):
        """
        :returns number of blogs a user has made on a Community
        :rtype: int
        """
        # TODO more research
        return self._get_prop("blogsCount")

    @property
    def role(self):
        """
        :returns: user role in a Community
        :rtype: int
        """
        # TODO more research
        return self._get_prop("role")

    @property
    def fan_club(self):
        """
        :returns: user's fan club data (more soon)
        :rtype: list<dict>
        """
        # TODO more research, objectify
        return self._get_prop("fanClubList")
