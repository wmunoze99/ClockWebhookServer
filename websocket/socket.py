import json
import logging
import random

from websockets.sync.server import serve
from websocket.device import Device
from websocket.response import Response
from store.tunnel import MessageQueue
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class WebSocketManager:
    connected_clients = {}
    server = None
    mq = MessageQueue()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebSocketManager, cls).__new__(cls)

        return cls.instance

    def __find_connected_client_by_chat_id__(self, value):
        for key, obj in self.connected_clients.items():
            if getattr(obj, 'chat_id') == value:
                return obj

        return None

    def __listener_handler__(self, response):
        chat_id = response['chat_id']
        message = response['message']
        client = self.__find_connected_client_by_chat_id__(chat_id)
        response = json.dumps(message)
        client.webhook.send(response)

    def handler(self, webhook):
        for message in webhook:
            try:
                decoded_message = json.loads(message)
                if decoded_message["command"] == "start":
                    mac = decoded_message["message"]["mac"]
                    self.connected_clients[mac] = Device(mac, webhook)
                    logging.info("New device added")

                    response = json.dumps(Response("start", {"response": "Device added"}).__dict__)
                    logging.info(response)
                    webhook.send(response)
                elif decoded_message["command"] == "auth":
                    mac = decoded_message["message"]["mac"]
                    chat_id = decoded_message["message"]["chat_id"]
                    code = decoded_message["message"]["code"]

                    try:
                        client = self.connected_clients[mac]
                        client.assign_chat_id(chat_id, code)
                        response = json.dumps(Response("auth_confirm", {"response": "Confirm"}).__dict__)
                        webhook.send(response)

                        random_codes = [random.randint(1000, 9999) for _ in range(6)]
                        index = random.randint(0, 5)
                        random_codes.insert(index, code)  # Insert real code on randoms

                        markup = InlineKeyboardMarkup()

                        for code in random_codes:
                            markup.row(InlineKeyboardButton(code, callback_data=f"code_{mac}_{chat_id}_{code}"))

                        message = {
                            "chat_id": chat_id,
                            "message": "Please select the correct password",
                            "markup": markup
                        }
                        self.mq.add_message('telegram', message)
                    except:
                        pass
                else:
                    webhook.send(message)  # Echo

                logging.info(message)
            except json.JSONDecodeError:
                webhook.send(message)
                logging.info(message)

    def start_in_thread(self):
        logging.info("Webhook server started at localhost:8765")
        self.mq.listen('websocket', self.__listener_handler__)
        with serve(handler=self.handler, host='0.0.0.0', port=8765, path='/') as sock:
            self.server = sock
            sock.serve_forever()

    def send_message(self, client: str, message: Response):
        client = self.connected_clients[client]
        response = json.dumps(message.__dict__)

        client.webhook.send(response)

    def close(self):
        self.server.shutdown()
