import time
from odoo import _

class BandwidthThrottler:
    def __init__(self, max_kbps=1024):
        self.max_bytes_per_sec = max_kbps * 1024
        self.start_time = time.time()
        self.bytes_transferred = 0

    def throttle(self, chunk_size):
        self.bytes_transferred += chunk_size
        elapsed = time.time() - self.start_time
        expected_time = self.bytes_transferred / self.max_bytes_per_sec
        
        if elapsed < expected_time:
            time.sleep(expected_time - elapsed)