"""
Proxy Client for secure API communication
Routes all requests through OpenOracle proxy to protect API keys
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ProxyClient:
    """
    Secure proxy client for OpenOracle API
    Routes requests through proxy server to protect OpenRouter API keys
    """

    def __init__(
        self,
        openoracle_api_key: str,
        proxy_url: str = "https://api.openoracle.xyz",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize proxy client

        Args:
            openoracle_api_key: Your OpenOracle API key (NOT OpenRouter!)
            proxy_url: OpenOracle proxy server URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = openoracle_api_key
        self.proxy_url = proxy_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_reset: Optional[datetime] = None
        self._rate_limit_remaining: int = 100

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def connect(self):
        """Create aiohttp session"""
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-SDK-Version": "1.0.0",
                    "X-SDK-Platform": "python"
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self):
        """Close aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None

    def _check_rate_limit(self) -> bool:
        """Check if we're rate limited"""
        if self._rate_limit_reset and datetime.now() < self._rate_limit_reset:
            if self._rate_limit_remaining <= 0:
                return False
        return True

    def _update_rate_limit(self, headers: Dict[str, str]):
        """Update rate limit info from response headers"""
        if 'X-RateLimit-Remaining' in headers:
            self._rate_limit_remaining = int(headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in headers:
            reset_timestamp = int(headers['X-RateLimit-Reset'])
            self._rate_limit_reset = datetime.fromtimestamp(reset_timestamp)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make request through proxy

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Response data

        Raises:
            Exception: On request failure
        """
        if not self._session:
            await self.connect()

        # Check rate limit
        if not self._check_rate_limit():
            wait_time = (self._rate_limit_reset - datetime.now()).total_seconds()
            raise Exception(f"Rate limited. Please wait {wait_time:.0f} seconds")

        url = f"{self.proxy_url}{endpoint}"

        try:
            async with self._session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                # Update rate limit info
                self._update_rate_limit(dict(response.headers))

                # Check response status
                if response.status == 429:
                    retry_after = response.headers.get('Retry-After', '60')
                    raise Exception(f"Rate limited. Retry after {retry_after} seconds")

                if response.status == 401:
                    raise Exception("Invalid API key or unauthorized")

                if response.status == 402:
                    raise Exception("Payment required - please upgrade your plan")

                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"Request failed ({response.status}): {error_text}")

                return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise Exception(f"Network error: {str(e)}")

    async def generate_ai_content(
        self,
        prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI content through proxy

        Args:
            prompt: AI prompt
            model: Model to use
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            response_format: Optional JSON schema for structured output

        Returns:
            AI response
        """
        return await self.request(
            method="POST",
            endpoint="/api/ai/generate",
            data={
                "prompt": prompt,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": response_format
            }
        )

    async def analyze_market(
        self,
        text: str,
        user_address: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze text for market creation through proxy

        Args:
            text: Market text to analyze
            user_address: User's wallet address
            preferences: Optional user preferences

        Returns:
            Market analysis results
        """
        return await self.request(
            method="POST",
            endpoint="/api/markets/analyze",
            data={
                "text": text,
                "user_address": user_address,
                "preferences": preferences
            }
        )

    async def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics

        Returns:
            Usage stats including rate limits and quota
        """
        return await self.request(
            method="GET",
            endpoint="/api/usage/stats"
        )

    async def validate_api_key(self) -> bool:
        """
        Validate API key

        Returns:
            True if API key is valid
        """
        try:
            response = await self.request(
                method="GET",
                endpoint="/api/auth/validate"
            )
            return response.get("valid", False)
        except Exception:
            return False


class RateLimiter:
    """Rate limiting helper for ProxyClient"""

    def __init__(self, requests_per_hour: int = 50):
        """
        Initialize rate limiter

        Args:
            requests_per_hour: Maximum requests per hour
        """
        self.requests_per_hour = requests_per_hour
        self.request_times: List[datetime] = []

    def can_make_request(self) -> bool:
        """Check if request can be made within rate limit"""
        now = datetime.now()
        cutoff = now - timedelta(hours=1)

        # Remove old requests
        self.request_times = [t for t in self.request_times if t > cutoff]

        # Check limit
        return len(self.request_times) < self.requests_per_hour

    def record_request(self):
        """Record a request timestamp"""
        self.request_times.append(datetime.now())

    def wait_time(self) -> float:
        """Calculate wait time until next request allowed"""
        if self.can_make_request():
            return 0.0

        oldest = min(self.request_times)
        wait_until = oldest + timedelta(hours=1)
        wait_seconds = (wait_until - datetime.now()).total_seconds()
        return max(0.0, wait_seconds)