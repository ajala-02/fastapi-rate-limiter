import time
from threading import Lock

class BaseLimiter:
    def consume(self) -> bool:
        pass
    def get_tokens(self) -> int:
        pass

class TokenBucket(BaseLimiter):
    def __init__(self, capacity: int = 100, refill_rate: float = 2.0): 
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_tokens(self) -> int:
        with self.lock:
            self._refill()
            return int(self.tokens)

class SlidingWindow(BaseLimiter):
    def __init__(self, limit: int = 10, window: int = 15):
        self.limit = limit
        self.window = window
        self.timestamps = []
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            self.timestamps = [t for t in self.timestamps if now - t < self.window]
            if len(self.timestamps) < self.limit:
                self.timestamps.append(now)
                return True
            return False

    def get_tokens(self) -> int:
        with self.lock:
            now = time.time()
            self.timestamps = [t for t in self.timestamps if now - t < self.window]
            return max(0, self.limit - len(self.timestamps))

class LeakyBucket(TokenBucket):
    # Same as Token Bucket but with a strictly slower refill rate (5 tokens per 5s = 1.0/s)
    def __init__(self, capacity: int = 100, refill_rate: float = 1.0):
        super().__init__(capacity, refill_rate)


# In-memory stores partitioned by algorithm
stores = {
    "token": {},
    "sliding": {},
    "leaky": {}
}

def get_limiter(algo: str, api_key: str) -> BaseLimiter:
    if algo not in stores:
        algo = "token"
        
    store = stores[algo]
    if api_key not in store:
        if algo == "sliding":
            store[api_key] = SlidingWindow(limit=10, window=15)
        elif algo == "leaky":
            store[api_key] = LeakyBucket(capacity=100, refill_rate=1.0)
        else:
            store[api_key] = TokenBucket(capacity=100, refill_rate=2.0)
            
    return store[api_key]
