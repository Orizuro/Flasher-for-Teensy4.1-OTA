import queue

class Console:
    def __init__(self):
        self.queue = queue.Queue()

    def log(self, message):
        """Adds log messages to the queue."""
        self.queue.put({'type': 'log', 'message': message})

    def process_queue(self, log_callback):
        """Processes messages from the queue and sends them to the UI."""
        while not self.queue.empty():
            try:
                msg = self.queue.get_nowait()
                if msg['type'] == 'log':
                    log_callback(msg['message'])
            except queue.Empty:
                pass
