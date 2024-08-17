from queue import Queue, Empty
from threading import Thread, Event


class MessageQueue:
    queues = {
        "websocket": Queue(),
        "telegram": Queue()
    }

    listeners = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MessageQueue, cls).__new__(cls)

        return cls.instance

    def add_message(self, queue_name, message):
        if queue_name not in self.queues.keys():
            raise ValueError("Queue no available")

        self.queues.get(queue_name).put(message)

    def get_last(self, queue_name):
        if queue_name not in self.queues.keys():
            raise ValueError("Queue no available")

        self.queues.get(queue_name).get()

    def __listener__(self, queue_name, callback, stop_event):
        while not stop_event.is_set():
            try:
                message = self.queues.get(queue_name).get(timeout=1)
                callback(message)
            except Empty:
                continue

    def listen(self, queue_name, callback):
        if queue_name not in self.queues.keys():
            raise ValueError("Queue not available")
        if queue_name in self.listeners:
            raise RuntimeError(f"Listener for {queue_name} already running")

        stop_event = Event()
        listener_thread = Thread(target=self.__listener__, args=(queue_name, callback, stop_event))
        listener_thread.start()
        self.listeners[queue_name] = (listener_thread, stop_event)

    def stop_listener(self, queue_name):
        if queue_name not in self.listeners:
            raise ValueError("Listener not found for queue")

        listener_thread, stop_event = self.listeners.pop(queue_name)
        stop_event.set()
        listener_thread.join()
