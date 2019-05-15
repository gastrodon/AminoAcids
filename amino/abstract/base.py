from abc import ABC

class ABCChatThread(ABC):
    def send_text_message(self, message):
        raise NotImplementedError

    @property
    def community(self):
        raise NotImplementedError


class ABCClient(ABC):
    def client_config(self):
        raise NotImplementedError

    def headers(self):
        raise NotImplementedError

    def login(self):
        raise NotImplementedError

    def get_sub_clients(self):
        raise NotImplementedError

class ABCCommunity(ABC):
    @property
    def member_count(self):
        raise NotImplementedError


class ABCPeer(ABC):
    def set_community_obj(self):
        raise NotImplementedError

    def get_pm_thread(self):
        raise NotImplementedError

    def request_chat(self):
        raise NotImplementedError

    def send_text_message(self):
        raise NotImplementedError

class ABCBlog(ABC):
    pass

class ABCMediaItem(ABC):
    pass
