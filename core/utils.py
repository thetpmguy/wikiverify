"""Shared utilities for WikiVerify."""
import time
import logging
from typing import Optional
from functools import wraps
from core.config import Config

# Set up logging
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, delay: Optional[float] = None):
        """
        Initialize rate limiter.
        
        Args:
            delay: Delay between requests in seconds (defaults to Config.RATE_LIMIT_DELAY)
        """
        self.delay = delay or Config.RATE_LIMIT_DELAY
        self.last_request_time = 0.0
    
    def wait(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def reset(self):
        """Reset the rate limiter."""
        self.last_request_time = 0.0


class HTTPClient:
    """Shared HTTP client with rate limiting and error handling."""
    
    def __init__(self, base_url: Optional[str] = None, user_agent: Optional[str] = None,
                 rate_limit_delay: Optional[float] = None, timeout: Optional[int] = None):
        """
        Initialize HTTP client.
        
        Args:
            base_url: Base URL for requests
            user_agent: User agent string
            rate_limit_delay: Delay between requests
            timeout: Request timeout in seconds
        """
        import requests
        
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = timeout or Config.CHECK_TIMEOUT
        self.rate_limiter = RateLimiter(rate_limit_delay)
        self._requests = requests  # Store for type hints
        
        headers = {}
        if user_agent:
            headers['User-Agent'] = user_agent
        elif Config.WIKIPEDIA_USER_AGENT:
            headers['User-Agent'] = Config.WIKIPEDIA_USER_AGENT
        
        if headers:
            self.session.headers.update(headers)
    
    def get(self, url: str, params: Optional[dict] = None, **kwargs):
        """
        Make a GET request with rate limiting.
        
        Args:
            url: URL to request
            params: Query parameters
            **kwargs: Additional arguments for requests.get
        
        Returns:
            Response object or None if error
        """
        self.rate_limiter.wait()
        
        full_url = f"{self.base_url}{url}" if self.base_url and not url.startswith('http') else url
        timeout = kwargs.pop('timeout', self.timeout)
        
        try:
            response = self.session.get(full_url, params=params, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except self._requests.Timeout as e:
            # Timeouts are expected for slow/unresponsive URLs - log as warning
            logger.debug(f"HTTP GET timeout for {full_url} (timeout={timeout}s)")
            return None
        except self._requests.ConnectionError as e:
            # Connection errors are also somewhat expected - log as warning
            logger.debug(f"HTTP GET connection error for {full_url}: {e}")
            return None
        except self._requests.RequestException as e:
            # Other HTTP errors (4xx, 5xx) are logged as warnings since they're expected
            if hasattr(e.response, 'status_code'):
                logger.debug(f"HTTP GET error for {full_url}: {e.response.status_code} {e}")
            else:
                logger.warning(f"HTTP GET error for {full_url}: {e}")
            return None
    
    def post(self, url: str, data: Optional[dict] = None, **kwargs):
        """
        Make a POST request with rate limiting.
        
        Args:
            url: URL to request
            data: POST data
            **kwargs: Additional arguments for requests.post
        
        Returns:
            Response object or None if error
        """
        self.rate_limiter.wait()
        
        full_url = f"{self.base_url}{url}" if self.base_url and not url.startswith('http') else url
        timeout = kwargs.pop('timeout', self.timeout)
        
        try:
            response = self.session.post(full_url, data=data, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except self._requests.Timeout as e:
            logger.debug(f"HTTP POST timeout for {full_url} (timeout={timeout}s)")
            return None
        except self._requests.ConnectionError as e:
            logger.debug(f"HTTP POST connection error for {full_url}: {e}")
            return None
        except self._requests.RequestException as e:
            if hasattr(e.response, 'status_code'):
                logger.debug(f"HTTP POST error for {full_url}: {e.response.status_code} {e}")
            else:
                logger.warning(f"HTTP POST error for {full_url}: {e}")
            return None
    
    def head(self, url: str, **kwargs):
        """
        Make a HEAD request with rate limiting.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.head
        
        Returns:
            Response object or None if error
        """
        self.rate_limiter.wait()
        
        full_url = f"{self.base_url}{url}" if self.base_url and not url.startswith('http') else url
        timeout = kwargs.pop('timeout', self.timeout)
        
        try:
            response = self.session.head(full_url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except self._requests.Timeout as e:
            # Timeouts are expected for slow/unresponsive URLs - log as debug
            logger.debug(f"HTTP HEAD timeout for {full_url} (timeout={timeout}s)")
            return None
        except self._requests.ConnectionError as e:
            # Connection errors are also somewhat expected - log as debug
            logger.debug(f"HTTP HEAD connection error for {full_url}: {e}")
            return None
        except self._requests.RequestException as e:
            # HTTP errors (4xx, 5xx) are expected when checking links - log as debug
            if hasattr(e.response, 'status_code'):
                logger.debug(f"HTTP HEAD error for {full_url}: {e.response.status_code} {e}")
            else:
                logger.warning(f"HTTP HEAD error for {full_url}: {e}")
            return None


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None):
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
        log_file: Optional log file path
    """
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Decorator for retrying function calls.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator
