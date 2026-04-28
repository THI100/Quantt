import queue


class SyncLogStreamer:
    def __init__(self):
        # Thread-safe queue
        self.queue = queue.Queue(maxsize=100)

    def broadcast(self, message):
        """Put log into the queue."""
        try:
            self.queue.put_nowait(message)
        except queue.Full:
            # If the queue is full, delete oldest or current log
            pass

    def generator(self):
        """The generator that yields logs as they arrive."""
        while True:
            message = self.queue.get()
            yield f"data: {message}\n\n"


log_stream = SyncLogStreamer()
