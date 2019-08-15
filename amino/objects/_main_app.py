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
            self._object_data_payload = helpers.api_req(self._url, headers = self.headers)["account"]

        return self._object_data_payload

    def login(self, email, password = None, force = False):
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
            self._auid = _user_config.get("auid")

            response = requests.get(f"{self.api}/g/s/account", headers = self.headers)
            data = response.json()["account"]

            if response.status_code == 200:
                self.authenticated = True
                return self

        if not password:
            raise ValueError("unable to load from config, a password or secret is needed to log in")

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
        self.config = {**self.config, f"{email}": {"secret": self._secret, "sid": self._sid, "auid": self._auid}}

        return self

    @property
    def joined_communities(self):
        """
        :returns: communities that this client has joined
        :rtype: generator<Community>
        """
        return (Community(data["ndcId"], client = self, data = data) for data in helpers.api_req_paginated(
            f"{self.api}/g/s/community/joined", "communityList", headers = self.headers))

    @property
    def community_users(self):
        """
        :returns: this client as represented on other communities
        :rtype: generator<User>
        """
        for user in helpers.api_req_paginated(f"{self.api}/g/s/community/joined",
                                              "userInfoInCommunities",
                                              headers = self.headers,
                                              is_dict = True):
            yield User(user[1]["userProfile"]["uid"], ndcid = user[0], client = self, data = user[1]["userProfile"])

    # _get_prop properties

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
    def nickname_verified(self):
        """
        :returns: is this user's nickname verified?
        :rtype: bool
        """
        return self._get_prop("isNicknameVerified")

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

    # TODO more research needed for the below

    @property
    def _status(self):
        """
        """
        return self._get_prop("status")

    @property
    def _membership(self):
        """
        """
        # amino+ membership status
        return self._get_prop("membership")

    @property
    def _role(self):
        """
        """
        # curator/leader roles? admin levels?
        return self._get_prop("role")


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
            self._object_data_payload = helpers.api_req(f"{self._url}/community/info",
                                                        headers = self.headers)["community"]

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
    def me(self):
        """
        :returns: this objects client's representatoin on this community
        :rtype: User
        """
        return User(self.client._auid, ndcid = self.id, client = self.client)

    # _get_prop properties

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
    def agent(self):
        """
        :returns: community agent (owner)
        :rtype: dict
        """
        _data = self._get_prop("agent")
        return User(_data["uid"], ndcid = self.id, data = _data)

    @property
    def heads(self):
        """
        :returns: community heads (leaders, curators, ect) (more soon)
        :rtype: generator<User>
        """
        _data = self._get_prop("communityHeadList")
        return (User(user["uid"], ndcid = self.id, data = user) for user in _data)

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
        # TODO objectify, more research
        return self._get_prop("extensions")

    @property
    def aliases(self):
        """
        :returns: community name aliases
        :rtype: list<str>
        """
        return self.extensions.get("communityNameAliases", "").split(",")

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

    # TODO more research needed on those below

    @property
    def _joinType(self):
        """
        """
        # join type/status for the attached client?
        return self._get_prop("joinType")

    @property
    def _template_id(self):
        """
        """
        # theme stuff? batch test from scraped aminos
        return self._get_prop("templateId")

    @property
    def _status(self):
        """
        """
        # status of what?
        return self._get_prop("status")

    @property
    def _is_standalone_app(self):
        """
        """
        # test with equestria, that has an app
        return self._get_prop("isStandaloneAppDeprecated")


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
            self._object_data_payload = helpers.api_req(self._url, headers = self.headers)["userProfile"]

        return self._object_data_payload

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
    def fan_club(self):
        """
        :returns: user's fan club data (more soon)
        :rtype: list<dict>
        """
        # TODO objectify, more research
        return self._get_prop("fanClubList")

    # TODO more research needed on those below

    @property
    def _status(self):
        """
        """
        #
        return self._get_prop("status")

    @property
    def _age(self):
        """
        """
        #, probably an integer
        return self._get_prop("age")

    @property
    def _race(self):
        """
        """
        #, probably a string
        return self._get_prop("race")

    @property
    def _gender(self):
        """
        """
        #, integer for gender 1:male, 2:female? or null
        return self._get_prop("gender")

    @property
    def _item_count(self):
        """
        """
        #
        return self._get_prop("itemsCount")

    @property
    def _global_user(self):
        """
        """
        #
        return self._get_prop("isGloba")

    @property
    def _online_status(self):
        """
        """
        # (online/offline/appear offline?)
        return self._get_prop("onlineStatus")

    @property
    def _account_membership_status(self):
        """
        """
        #
        return self._get_prop("accountMembershipStatus")

    @property
    def _membership_status(self):
        """
        """
        # (amino+? vip?)
        return self._get_prop("membershipStatus")

    @property
    def _content(self):
        """
        """
        #, objectify (wall blog, or content for wall blog?)
        return self._get_prop("content")

    @property
    def _push_enabled(self):
        """
        """
        #
        return self._get_prop("pushEnabled")

    @property
    def _notification_subscription(self):
        """
        """
        #
        return self._get_prop("notificationSubscriptionStatus")

    @property
    def _join_count(self):
        """
        """
        # (fan club?)
        return self._get_prop("joinedCount")

    @property
    def _extensions(self):
        """
        """
        #, objectify (frame objects, what else?)
        return self._get_prop("extensions")

    @property
    def _post_count(self):
        """
        """
        #
        return self._get_prop("postsCount")

    @property
    def _blog_count(self):
        """
        """
        #
        return self._get_prop("blogsCount")

    @property
    def _role(self):
        """
        """
        #
        return self._get_prop("role")

    @property
    def _member_count(self):
        """
        """
        # (fan club size?)
        return self._get_prop("membersCount")

    @property
    def _following_status(self):
        """
        """
        # (is_followng bool?)
        return self._get_prop("followingStatus")

    @property
    def _online_status_setting(self):
        """
        """
        # (appear_offline bool?)
        return self._get_prop("settings", {}).get("onlineStatus")


class Blog(mixin.ObjectMixin):
    def __init__(self, *args, ndcid = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self._ndcid = ndcid
        self._url = f"{self.api}/x{self._ndcid}/s/blog/{self.id}"

    @property
    def _object_data(self):
        if self._object_data_payload is None or self._update:
            self._update = False
            self._object_data_payload = helpers.api_req(self._url, headers = self.headers)["blog"]

        return self._object_data_payload

    @property
    def community(self):
        """
        :returns: community that this blog was posted on, if any
        :rtype: Community
        """
        if self._ndcid == 0:
            return None

        return Community(self._ndcid, client = me.client)

    @property
    def modified(self):
        """
        :returns: was this blog modified?
        :rtype: bool
        """
        return self.created == self.last_modified

    @property
    def disabled(self):
        """
        :returns: is this blog disabled?
        :rtype: bool
        """
        return self.status == 9

    @property
    def visible(self):
        """
        :returns: is this blog visible?
        :rtype: bool
        """
        return self.status == 0

    @property
    def featured(self):
        """
        :returns: is this blog featured?
        :rtype: bool
        """
        return self._get_prop("extensions", {}).get("featuredType") == 1

    @property
    def liked(self):
        """
        :returns: did the attached client like this post?
        :rtype: bool
        """
        return self._get_prop("votedValue") == 4

    # properties from _get_prop("extensions")

    @property
    def fan_club_only(self):
        """
        :returns: is this blog only visible to fan club members?
        :rtype: bool
        """
        return self._get_prop("extensions", {}).get("fansOnly", False)

    @property
    def background_media(self):
        """
        :returns: blog background media, if any
        :rtype: list<MediaItem>
        """
        _data = self._get_prop("extensions", {}).get("style", {}).get("backgroundMediaList", [])
        return [helpers.MediaItem(item, headers = self.headers) for item in _data]

    # properties from _get_prop("tipInfo")

    @property
    def minimum_tip(self):
        """
        :returns: minimum coin tip amount
        :rtype: int
        """
        return self._get_prop("tipInfo", {}).get("tipMinCoin")

    @property
    def maximum_tip(self):
        """
        :returns: maximum coin tip amount
        :rtype: int
        """
        return self._get_prop("tipInfo", {}).get("tipMaxCoin")

    @property
    def tip_count(self):
        """
        :returns: number of times tipped
        :rtype: int
        """
        return self._get_prop("tipInfo", {}).get("tippersCount")

    @property
    def tip_total(self):
        """
        :returns: blog tipped total
        :rtype: int
        """
        return self._get_prop("tipInfo", {}).get("tippedCoins")

    @property
    def tippable(self):
        """
        :returns: can this blog be tipped?
        :rtype: bool
        """
        return self._get_prop("tipInfo", {}).get("tippable", False)

    @property
    def tip_options(self):
        """
        :returns: amounts a blog can be tipped by the attached client
        :rtype: list<int>
        """
        _data = self._get_prop("tipInfo", {}).get("tipOptionList", [])
        return [opt["value"] for opt in _data]

    # _get_prop properties

    @property
    def author(self):
        """
        :returns: blog author
        :rtype: User
        """
        _data = self._get_prop("author")
        return User(_data["uid"], ndcid = self._ndcid, client = self.client, data = _data)

    @property
    def media_list(self):
        """
        :returns: media items in this blog
        :rtype: list<MediaItem>
        """
        return [helpers.MediaItem(item, headers = self.headers) for item in self._get_prop("mediaList", [])]

    @property
    def content(self):
        """
        :returns: blog text content
        :rtype: str
        """
        return self._get_prop("content")

    @property
    def title(self):
        """
        :returns: blog title
        :rtype: str
        """
        return self._get_prop("title")

    @property
    def keywords(self):
        """
        :returns: blog keywords
        :rtype: list<str>
        """
        return self._get_prop("keywords", "").split(", ")

    @property
    def vote_count(self):
        """
        :returns: blog vote count
        :rtype: int
        """
        return self._get_prop("votesCount")

    @property
    def comment_count(self):
        """
        :returns: blog comment count
        :rtype: int
        """
        return self._get_prop("commentsCount")

    @property
    def created(self):
        """
        :returns: blog creation timestamp
        :rtype: float
        """
        return helpers.date_ts(self._get_prop("createdTime"))

    @property
    def last_modified(self):
        """
        :returns: last modification timestamp
        :rtype: float
        """
        return helpers.date_ts(self._get_prop("modifiedTime"))

    @property
    def status(self):
        """
        :returns: status integer value of this blog (visible, disabled, ect)
        :rtype: int
        """
        return self._get_prop("status")

    @property
    def voted_value(self):
        """
        :returns: voted integer value of this blog, in relation to the client (liked, disliked, ect)
        :rtype: int
        """
        return self._get_prop("votedValue")

    # TODO more research needed for the below

    @property
    def _type(self):
        """
        """
        return self._get_prop("type")

    @property
    def _global_vote_count(self):
        """
        """
        return self._get_prop("globalVotedValue")

    @property
    def _global_comment_count(self):
        """
        """
        return self._get_prop("globalCommentsCount")

    @property
    def _global_voted_value(self):
        """
        """
        # what are global values, in relation to regular values?
        # these seem to corespond with _vote_count, _comment_count and _voted_value
        return self._get_prop("globalVotedValue")

    @property
    def _guest_vote_count(self):
        """
        """
        # can you vote without signing in?
        return self._get_prop("guestVotesCount")

    @property
    def _content_rating(self):
        """
        """
        # can you set content ratings for blogs? unused/to-be-implemented feature
        return self._get_prop("contentRating")

    @property
    def _need_hidden(self):
        """
        """
        # related to _content_rating?
        return self._get_prop("needHidden")

    @property
    def _view_count(self):
        """
        """
        # normal views don't affect this, so I don't know what it is
        return self._get_prop("viewCount")

    @property
    def _language(self):
        """
        """
        # could be related to non-english communities, but I don't know yet
        # so far is just None
        return self._get_prop("language")

    @property
    def _end_time(self):
        """
        """
        # end of featured time? time removed?
        return self._get_prop("endTime")
