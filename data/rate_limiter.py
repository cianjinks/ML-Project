import time

class RateLimiter:

    def __init__(self):
        self.request_window_limit_1 = []
        self.request_window_limit_120 = []

    def update_time_windows(self):
        current_time = time.time()
        last_1 = current_time - 1
        last_120 = current_time - 120

        new_request_window_limit_1 = []
        new_request_window_limit_120 = []

        for t in self.request_window_limit_1:
            if t >= last_1:
                new_request_window_limit_1.append(t)

        for t in self.request_window_limit_120:
            if t >= last_120:
                new_request_window_limit_120.append(t)

        self.request_window_limit_1 = new_request_window_limit_1
        self.request_window_limit_120 = new_request_window_limit_120


    def block_execution(self):
        return len(self.request_window_limit_120) >= 95 or len(self.request_window_limit_1) >= 18


    def append_moment(self):
        current = time.time()
        self.request_window_limit_1.append(current)
        self.request_window_limit_120.append(current)
        print(f"Sent a request: {current}")


    def rate_limit(self):
        first = True
        while self.block_execution():
            self.update_time_windows()
            if first:
                print("Waiting...")
                first = False
