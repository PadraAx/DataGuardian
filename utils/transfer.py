import threading
from queue import Queue
from odoo import _

class ParallelTransfer:
    def __init__(self, max_threads=4):
        self.queue = Queue()
        self.max_threads = max_threads

    def add_task(self, file_path, remote_path):
        self.queue.put((file_path, remote_path))

    def _worker(self, cloud_connector):
        while not self.queue.empty():
            file_path, remote_path = self.queue.get()
            try:
                cloud_connector.upload_backup(file_path, remote_path)
            finally:
                self.queue.task_done()

    def execute(self, cloud_connector):
        for _ in range(self.max_threads):
            t = threading.Thread(
                target=self._worker,
                args=(cloud_connector,)
            )
            t.daemon = True
            t.start()
        self.queue.join()