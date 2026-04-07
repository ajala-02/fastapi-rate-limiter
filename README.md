# FastAPI Rate Limiter

A production-inspired API rate limiter built with FastAPI. Implements three core algorithms, exposes a live dashboard, and visualizes traffic in real time.


# Live Demo
https://fastapi-rate-limiter.onrender.com — try spamming requests and watch the rate limiter block them in real time

 # Why Rate Limiting Matters

Rate limiting is load-bearing infrastructure in any serious backend:

- Prevents API abuse and DDoS amplification
- Ensures fair usage across clients sharing the same resource
- Protects server capacity during sudden traffic spikes
- Gives operators visibility into how their API is actually being used

Most tutorials treat it as a one-liner middleware. This project goes deeper in implementing the algorithms from scratch, exposing their internal state, and
making the trade-offs tangible.

## Request lifecycle
<img width="1440" height="324" alt="image" src="https://github.com/user-attachments/assets/99a11256-d0ae-4a82-840d-f353645da368" />




## Algorithms Implemented

| Algorithm       | How it works                                   | Best for                 |
|-----------      |------------------------------------------------|--------------------------|
| Token Bucket    | Fixed capacity bucket, tokens refill over time | Handling burst traffic   |
| Sliding Window  | Tracks requests in a rolling time window       | Smooth, fair limiting    |
| Leaky Bucket    | Requests processed at constant rate            | Preventing sudden spikes |



The key trade-off: token bucket tolerates bursts but is harder to reason about at boundaries. Sliding window is fairer but memory-heavier under many clients.
Leaky bucket is the most predictable, but the least forgiving.


# Features
- Switch algorithms in real time without restarting the server
- Live dashboard showing token levels, bucket state, and request history
- Real-time traffic charts (200 vs 429 breakdown via Chart.js)
- Namespace-based API key provisioning — simulate isolated clients
- Concurrency-safe request handling (no race conditions on shared state)
- SQLite-backed persistence across restarts

## Dashboard preview


  <img width="1900" height="881" alt="image" src="https://github.com/user-attachments/assets/16bef283-e567-4859-8ae1-c29da2dd3959" />

> Spam 50 requests and watch the token bucket empty in real time.

# Tech Stack
- **Backend:**   Python, FastAPI
- **Frontend:**  Vanilla JS, Chart.js
- **Database:**  SQLite

# Run Locally
```bash
# Clone the repo
git clone https://github.com/ajala-02/fastapi-rate-limiter.git
cd fastapi-rate-limiter

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

Then open `http://localhost:8000` in your browser.

## How to Test It
1. Enter a namespace (e.g. prod_backend_01)
2. Click Provision Key
3. Send a few normal requests
4. Spam multiple requests (e.g. 50x)
5. Observe:
- Token depletion
- Rate limiting (429 responses)
- Real-time dashboard updates
6. Switch algorithms mid-session and repeat — the difference in behavior is
   visible within seconds

# Project Structure
```fastapi-rate-limiter/
├── main.py
├── api/
│   └── routes.py
├── core/              # Rate limiting logic
├── db/                # Database models
├── static/
│   └── index.html     # Dashboard UI
└── requirements.txt
```

## Technical deep dive

**Race conditions under concurrency.** Concurrent requests reading and
decrementing the same token counter can produce incorrect allow/deny decisions
without careful locking. Solving this without introducing a bottleneck required
thinking carefully about where shared state lives and how writes are serialized.

**Algorithm switching without request loss.** Swapping algorithms at runtime
meant deciding what to do with in-flight requests and partially depleted state.
The current approach resets algorithm-specific counters on switch while
preserving the namespace and key — a deliberate trade-off between consistency
and continuity.

**SQLite under high concurrency.** SQLite's write-lock model surfaces quickly
when you're hammering an endpoint. Handling contention gracefully — rather than
surfacing lock errors to the client — required retry logic and intentional
transaction scoping.

# Key Learnings

- The right algorithm depends on your traffic pattern, not on which one sounds best
- Distributed rate limiting is a fundamentally different problem from single
- -instance rate limiting — local state doesn't survive horizontal scale
- Building the dashboard alongside the limiter forced clearer thinking about what state is actually meaningful to expose

# Future Improvements
- **Redis integration** for distributed rate limiting across multiple instances
- **Horizontal scaling support** — consistent limiting when multiple workers
  share no local state
- **Per-user authentication** with individual rate limit tiers
- **Dockerization** for one-command local setup and easier deployment
## Author
**Ajala** — https://github.com/ajala-02 
