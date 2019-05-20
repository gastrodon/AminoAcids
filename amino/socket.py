import websocket, time, json, threading

class SocketHandler():
    def __init__(self, client, socket_trace = False, handlers_dict = {}):
        websocket.enableTrace(True)
        self.socket_url = "wss://ws1.narvii.com"
        self.client = client
        self.active = False
        self.headers = None
        self.socket = None
        self.socket_thread = None

        self.handlers = handlers_dict

        websocket.enableTrace(socket_trace)

    def on_open(self):
        pass

    def handle_message(self, data):
        return self.client.handle_socket_message(data)

    def default_handler(self, data):
        print(f"Default handler called for t:{message['t']}")

    def send(self, data):
        self.socket.send(data)

    def start(self):
        self.headers = {
            "NDCDEVICEID": self.client.device_id,
            "NDCAUTH": f"sid={self.client.sid}"
        }

        self.socket = websocket.WebSocketApp(
            f"{self.socket_url}/?signbody={self.client.device_id}%7C{int(time.time() * 1000)}",
            on_message = self.handle_message,
            on_open = self.on_open,
            header = self.headers
        )

        self.socket_thread = threading.Thread(target = self.socket.run_forever)
        self.socket_thread.start()
        self.active = True

    def close(self):
        self.socket.close()
        self.active = False

class Callbacks:
    def __init__(self, client):
        """
        Build the callback handler
        client: Client to be used
        This is meant to be subclassed
        """
        self.client = client
        
        self.methods = {
            1000: self.on_message_received
        }

    def resolve(self, data):
        data = json.loads(data)
        return self.methods.get(data["t"], self.default)(data)

    def on_message_received(self, data):
        "called when a message is received"
        pass

    def default(self, data):
        "called when the parameter `t` is not matched"
        pass
