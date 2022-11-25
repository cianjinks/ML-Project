import time
import logging

class RateLimiter:

    def __init__(self):
        self.request_window_limit_1 = {}
        self.request_window_limit_120 = {}

    def register_api_key(self, api_key):
        self.request_window_limit_1[api_key] = []
        self.request_window_limit_120[api_key] = []

    def update_time_windows(self, api_key):
        current_time = time.time()
        last_1 = current_time - 1
        last_120 = current_time - 120

        new_request_window_limit_1 = []
        new_request_window_limit_120 = []

        for t in self.request_window_limit_1[api_key]:
            if t >= last_1:
                new_request_window_limit_1.append(t)

        for t in self.request_window_limit_120[api_key]:
            if t >= last_120:
                new_request_window_limit_120.append(t)

        self.request_window_limit_1[api_key] = new_request_window_limit_1
        self.request_window_limit_120[api_key] = new_request_window_limit_120


    def block_execution(self, api_key):
        return len(self.request_window_limit_120[api_key]) >= 95 or len(self.request_window_limit_1[api_key]) >= 18


    def append_moment(self, api_key):
        current = time.time()
        self.request_window_limit_1[api_key].append(current)
        self.request_window_limit_120[api_key].append(current)
        logging.info(f"Sent a request: {current}")


    def rate_limit(self, api_key):
        first = True
        while self.block_execution(api_key):
            self.update_time_windows(api_key)
            if first:
                logging.info("Waiting...")
                first = False