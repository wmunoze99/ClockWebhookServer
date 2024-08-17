from websocket.socket import WebSocketManager
from threading import Thread

import telegram.TelgramHandler as Tl
import logging

logging.basicConfig(level=logging.DEBUG)
socket = WebSocketManager()

if __name__ == '__main__':
    Tl.init()
    telegram_thread = Thread(name="telegram", target=Tl.run)

    try:
        telegram_thread.start()
        socket.start_in_thread()
    except KeyboardInterrupt:
        logging.info("Closing server.")
        logging.info("Telegram is been close")
        Tl.stop()
        telegram_thread.join()
        logging.info("Telegram closed")
        logging.info("Closing websocket")
        socket.close()
        logging.info("Websocket closed")
        logging.info("Bye")
