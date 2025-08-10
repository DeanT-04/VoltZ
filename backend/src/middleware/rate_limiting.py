"""
Rate Limiting Middleware

Implements rate limiting to prevent API abuse and ensure fair usage.
"""

import time
from typing import Dict, Tuple, Callable
from collections import defaultdict, deque

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    Implements sliding window rate limiting per IP address.
    For production, this should be replaced with Redis-based rate limiting.
    
    Requirements: 6.4 (rate limiting to prevent abuse)
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # In-memory storage for request timestamps
        # Format: {ip_address: {"minute": deque, "hour": deque}}
        self._request_history: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: {"minute": deque(), "hour": deque()}
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, timestamps: deque, window_seconds: int) -> None:
        """Remove timestamps older than the specified window."""
        current_time = time.time()
        while timestamps and timestamps[0] < current_time - window_seconds:
            timestamps.popleft()
    
    def _check_rate_limit(self, ip_address: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request should be rate limited.
        
        Returns:
            Tuple of (is_allowed, remaining_counts)
        """
        current_time = time.time()
        history = self._request_history[ip_address]
        
        # Clean old requests
        self._clean_old_requests(history["minute"], 60)  # 1 minute window
        self._clean_old_requests(history["hour"], 3600)  # 1 hour window
        
        # Check limits
        minute_count = len(history["minute"])
        hour_count = len(history["hour"])
        
        minute_remaining = max(0, self.requests_per_minute - minute_count)
        hour_remaining = max(0, self.requests_per_hour - hour_count)
        
        # Allow request if both limits are satisfied
        is_allowed = (
            minute_count < self.requests_per_minute and 
            hour_count < self.requests_per_hour
        )
        
        if is_allowed:
            # Record this request
            history["minute"].append(current_time)
            history["hour"].append(current_time)
        
        return is_allowed, {
            "minute_remaining": minute_remaining,
            "hour_remaining": hour_remaining
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting to incoming requests."""
        
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        is_allowed, remaining = self._check_rate_limit(client_ip)
        
        if not is_allowed:
            # Rate limit exceeded
            raise HTTPException(
                status_code=429,
                detail={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "details": {
                        "limit_per_minute": self.requests_per_minute,
                        "limit_per_hour": self.requests_per_hour,
                        "retry_after": 60  # Suggest retry after 1 minute
                    }
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Minute"] = str(remaining["minute_remaining"])
        response.headers["X-RateLimit-Remaining-Hour"] = str(remaining["hour_remaining"])
        
        return response