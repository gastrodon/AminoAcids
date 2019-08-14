class BadAPIResponse(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FailedLogin(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NotAuthenticated(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Captcha(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
