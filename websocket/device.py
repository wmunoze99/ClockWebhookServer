class Device:
    mac = ""
    chat_id = ""
    webhook = None
    code = 0
    auth = False

    def __init__(self, mac, webhook):
        self.mac = mac
        self.webhook = webhook

    def assign_chat_id(self, chat_id: str, code: int):
        self.chat_id = chat_id
        self.code = code

    def set_auth(self):
        self.auth = True
