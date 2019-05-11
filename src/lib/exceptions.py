class FailedLogin(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)

class UnknownResponse(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)
