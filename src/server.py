import asyncio
from websocket_server import WebsocketServer
from threading import Thread

# websocket.enableTrace(True)

class Server:
    def __init__(self, log):
        self.log = log
        self.lastMessage = ""

    def start_server(self):
        # print(self.lastMessage)
        self.server = WebsocketServer(host='127.0.0.1', port=1100)
        # server = websocket.WebSocketApp("wss://localhost:1100", on_open=on_open, on_message=on_message, on_close=on_close)
        self.server.set_fn_new_client(self.handle_new_client)
        self.server.run_forever(threaded=True)

    def handle_new_client(self, client, server):
        if self.lastMessage != "":
            self.send_message(self.lastMessage)

    def send_message(self, message):
        self.lastMessage = message
        self.server.send_message_to_all(message)

        
    