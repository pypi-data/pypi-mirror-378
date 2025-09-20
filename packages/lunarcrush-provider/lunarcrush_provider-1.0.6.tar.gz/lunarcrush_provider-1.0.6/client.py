"""
LunarCrush API Client

Handles API requests with bearer token authentication, rate limiting, and error handling.
"""

import time
import logging
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class RateLimitException(Exception):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, wait_time: int = 60):
        self.wait_time = wait_time
        super().__init__(f"Rate limit exceeded. Wait {wait_time} seconds.")


class LunarCrushClient:
    """
    LunarCrush API Client with rate limiting and authentication
    """
    
    BASE_URL = "https://lunarcrush.com/api4/public"
    
    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize LunarCrush API client
        
        Args:
            api_key: Bearer token for API authentication
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        
        # Rate limit tracking from headers
        self.minute_remaining = 10  # Default assumption
        self.day_remaining = 2000   # Default assumption
        self.minute_reset = 0
        self.day_reset = 0
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=2,
            respect_retry_after_header=True
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'FreqTrade-LunarCrush/1.0.0'
        })
        
        logger.info("LunarCrush API client initialized")
    
    def _update_rate_limits(self, headers: Dict[str, str]) -> None:
        """Update rate limit counters from response headers"""
        try:
            self.minute_remaining = int(headers.get('x-rate-limit-minute-remaining', self.minute_remaining))
            self.day_remaining = int(headers.get('x-rate-limit-day-remaining', self.day_remaining))
            self.minute_reset = int(headers.get('x-rate-limit-minute-reset', 0))
            self.day_reset = int(headers.get('x-rate-limit-day-reset', 0))
            
            logger.debug(f"Rate limits updated: {self.minute_remaining}/min, {self.day_remaining}/day")
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse rate limit headers: {e}")
    
    def _check_rate_limits(self) -> Optional[int]:
        """
        Check if we can make a request based on rate limits
        
        Returns:
            Wait time in seconds if rate limited, None if OK
        """
        current_time = int(time.time())
        
        # Check minute rate limit
        if self.minute_remaining <= 0:
            if self.minute_reset > current_time:
                wait_time = self.minute_reset - current_time
                logger.warning(f"Minute rate limit exceeded. Waiting {wait_time}s")
                return wait_time
            else:
                # Reset period passed, assume we have requests available
                self.minute_remaining = 10
        
        # Check daily rate limit
        if self.day_remaining <= 0:
            if self.day_reset > current_time:
                wait_time = self.day_reset - current_time
                logger.warning(f"Daily rate limit exceeded. Waiting {wait_time}s")
                return wait_time
            else:
                # Reset period passed, assume we have requests available
                self.day_remaining = 2000
        
        return None
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated request to LunarCrush API
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            RateLimitException: If rate limited
            requests.RequestException: For other request errors
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        # Check rate limits before making request
        wait_time = self._check_rate_limits()
        if wait_time:
            raise RateLimitException(wait_time)
        
        logger.debug(f"Making request to: {url}")
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            # Update rate limits from response headers
            self._update_rate_limits(response.headers)
            
            # Handle rate limit response
            if response.status_code == 429:
                # Parse retry-after header if available
                retry_after = response.headers.get('retry-after', '60')
                try:
                    wait_time = int(retry_after)
                except ValueError:
                    wait_time = 60
                raise RateLimitException(wait_time)
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            logger.debug(f"Request successful: {len(data.get('data', []))} items returned")
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout}s")
            raise
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - check internet connectivity")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_coin_list(self) -> Dict[str, Any]:
        """
        Get list of available coins
        
        Returns:
            Coin list response with mappings
        """
        logger.info("Fetching coin list")
        return self._make_request("coins/list/v1")
    
    def get_coin_timeseries(self, coin_id: int, start_time: Optional[int] = None, 
                           end_time: Optional[int] = None) -> Dict[str, Any]:
        """
        Get time series data for a specific coin
        
        Args:
            coin_id: LunarCrush internal coin ID
            start_time: Unix timestamp start (optional)
            end_time: Unix timestamp end (optional)
            
        Returns:
            Time series response data
        """
        endpoint = f"coins/{coin_id}/time-series/v2"
        
        params = {}
        if start_time:
            params['start'] = start_time
        if end_time:
            params['end'] = end_time
        
        logger.info(f"Fetching timeseries for coin {coin_id}")
        return self._make_request(endpoint, params)
    
    def get_rate_limit_status(self) -> Dict[str, int]:
        """
        Get current rate limit status
        
        Returns:
            Dict with rate limit information
        """
        return {
            'minute_remaining': self.minute_remaining,
            'day_remaining': self.day_remaining,
            'minute_reset': self.minute_reset,
            'day_reset': self.day_reset
        }
    
    def wait_for_rate_limit(self, max_wait: int = 3600) -> bool:
        """
        Wait for rate limit to reset if needed
        
        Args:
            max_wait: Maximum time to wait in seconds
            
        Returns:
            True if can proceed, False if max_wait exceeded
        """
        wait_time = self._check_rate_limits()
        if wait_time is None:
            return True
        
        if wait_time > max_wait:
            logger.error(f"Rate limit wait time {wait_time}s exceeds max_wait {max_wait}s")
            return False
        
        logger.info(f"Waiting {wait_time}s for rate limit reset...")
        time.sleep(wait_time)
        return True