# FastAPI Rate Limiter

A production-inspired API Rate Limiter built with FastAPI, featuring multiple algorithms, a live dashboard, and real-time traffic visualization.

dashboard link

# Live Demo
https://fastapi-rate-limiter.onrender.com — try spamming requests and watch the rate limiter block them in real time

 # Why Rate Limiting Matters
Rate limiting is a critical component of backend systems. 
1. It Prevents API abuse and DDoS attacks
2. Ensures fair usage across clients
3. Protects server resources under high load

## Algorithms Implemented

| Algorithm       | How it works                                   | Best for                 |
|-----------      |------------------------------------------------|--------------------------|
| Token Bucket    | Fixed capacity bucket, tokens refill over time | Handling burst traffic   |
| Sliding Window  | Tracks requests in a rolling time window       | Smooth, fair limiting    |
| Leaky Bucket    | Requests processed at constant rate            | Preventing sudden spikes |



# Features
 - Switch algorithms in real-time
 - Live dashboard with token/bucket state
 - Real-time request monitoring (200 vs 429)
 - Traffic visualization using charts
 - Namespace-based API key provisioning
 - Concurrency-safe request handling

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
# Key Learnings
- Trade-offs between rate limiting strategies (latency vs fairness vs memory)
- Handling race conditions in concurrent systems
- Designing scalable backend components
- Building real-time dashboards without heavy frameworks

# Future Improvements
- Redis integration for distributed rate limiting
- Horizontal scaling support
- Authentication + per-user rate limits
- Dockerization & deployment
## Author
**Ajala** — https://github.com/ajala-02 
