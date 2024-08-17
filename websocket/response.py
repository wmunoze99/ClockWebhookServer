import json
from time import time


class Response:
    command = ""
    message = {}
    time = time()

    def __init__(self, command, message):
        self.command = command
        self.message = message
