"""
http utilities for fuero
provides http client functionality and web utilities
"""

import requests
import urllib.parse
import urllib.request
import urllib.error
import json
from typing import Dict, Any, Optional, Union, List
import time


class HttpResponse:
    """http response wrapper"""
    
    def __init__(self, response: requests.Response):
        self.response = response
        self.status_code = response.status_code
        self.headers = dict(response.headers)
        self.text = response.text
        self.content = response.content
        self.url = response.url
        self.encoding = response.encoding
    
    def json(self) -> Any:
        """Parse response as JSON"""
        return self.response.json()
    
    def is_success(self) -> bool:
        """Check if request was successful (2xx status)"""
        return 200 <= self.status_code < 300
    
    def is_error(self) -> bool:
        """Check if request resulted in error (4xx or 5xx status)"""
        return self.status_code >= 400


class Http:
    """http client and web utilities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.default_timeout = 30
        self.default_headers = {
            'User-Agent': 'Fuero-HTTP/1.1.1'
        }
    
    # Basic HTTP methods
    def get(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, 
            timeout: Optional[int] = None) -> HttpResponse:
        """Send GET request"""
        return self._request('GET', url, params=params, headers=headers, timeout=timeout)
    
    def post(self, url: str, data: Optional[Union[Dict, str]] = None, json_data: Optional[Dict] = None,
             headers: Optional[Dict] = None, timeout: Optional[int] = None) -> HttpResponse:
        """Send POST request"""
        return self._request('POST', url, data=data, json=json_data, headers=headers, timeout=timeout)
    
    def put(self, url: str, data: Optional[Union[Dict, str]] = None, json_data: Optional[Dict] = None,
            headers: Optional[Dict] = None, timeout: Optional[int] = None) -> HttpResponse:
        """Send PUT request"""
        return self._request('PUT', url, data=data, json=json_data, headers=headers, timeout=timeout)
    
    def patch(self, url: str, data: Optional[Union[Dict, str]] = None, json_data: Optional[Dict] = None,
              headers: Optional[Dict] = None, timeout: Optional[int] = None) -> HttpResponse:
        """Send PATCH request"""
        return self._request('PATCH', url, data=data, json=json_data, headers=headers, timeout=timeout)
    
    def delete(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None) -> HttpResponse:
        """Send DELETE request"""
        return self._request('DELETE', url, headers=headers, timeout=timeout)
    
    def head(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None) -> HttpResponse:
        """Send HEAD request"""
        return self._request('HEAD', url, headers=headers, timeout=timeout)
    
    def options(self, url: str, headers: Optional[Dict] = None, timeout: Optional[int] = None) -> HttpResponse:
        """Send OPTIONS request"""
        return self._request('OPTIONS', url, headers=headers, timeout=timeout)
    
    def _request(self, method: str, url: str, **kwargs) -> HttpResponse:
        """Internal method to make HTTP requests"""
        # Merge default headers with provided headers
        headers = self.default_headers.copy()
        if 'headers' in kwargs and kwargs['headers']:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        # Set default timeout
        if 'timeout' not in kwargs or kwargs['timeout'] is None:
            kwargs['timeout'] = self.default_timeout
        
        try:
            response = self.session.request(method, url, **kwargs)
            return HttpResponse(response)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"HTTP request failed: {e}")
    
    # Session management
    def set_default_headers(self, headers: Dict[str, str]):
        """Set default headers for all requests"""
        self.default_headers.update(headers)
    
    def set_auth(self, username: str, password: str):
        """Set basic authentication"""
        self.session.auth = (username, password)
    
    def set_bearer_token(self, token: str):
        """Set Bearer token authentication"""
        self.default_headers['Authorization'] = f'Bearer {token}'
    
    def set_api_key(self, key: str, header_name: str = 'X-API-Key'):
        """Set API key authentication"""
        self.default_headers[header_name] = key
    
    def clear_auth(self):
        """Clear authentication"""
        self.session.auth = None
        if 'Authorization' in self.default_headers:
            del self.default_headers['Authorization']
    
    def set_timeout(self, timeout: int):
        """Set default timeout for requests"""
        self.default_timeout = timeout
    
    # Cookie management
    def get_cookies(self) -> Dict[str, str]:
        """Get current session cookies"""
        return dict(self.session.cookies)
    
    def set_cookie(self, name: str, value: str, domain: Optional[str] = None):
        """Set a cookie"""
        self.session.cookies.set(name, value, domain=domain)
    
    def clear_cookies(self):
        """Clear all cookies"""
        self.session.cookies.clear()
    
    # File operations
    def download_file(self, url: str, filepath: str, chunk_size: int = 8192) -> bool:
        """Download file from URL"""
        try:
            response = self.get(url, timeout=None)
            if response.is_success():
                with open(filepath, 'wb') as f:
                    for chunk in response.response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                return True
            return False
        except Exception:
            return False
    
    def upload_file(self, url: str, filepath: str, field_name: str = 'file',
                   additional_data: Optional[Dict] = None) -> HttpResponse:
        """Upload file to URL"""
        files = {field_name: open(filepath, 'rb')}
        data = additional_data or {}
        
        try:
            response = self.session.post(url, files=files, data=data, 
                                       headers=self.default_headers, timeout=self.default_timeout)
            return HttpResponse(response)
        finally:
            files[field_name].close()
    
    # URL utilities
    def encode_url(self, url: str) -> str:
        """URL encode string"""
        return urllib.parse.quote(url)
    
    def decode_url(self, url: str) -> str:
        """URL decode string"""
        return urllib.parse.unquote(url)
    
    def parse_url(self, url: str) -> Dict[str, str]:
        """Parse URL into components"""
        parsed = urllib.parse.urlparse(url)
        return {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'hostname': parsed.hostname,
            'port': parsed.port,
            'path': parsed.path,
            'params': parsed.params,
            'query': parsed.query,
            'fragment': parsed.fragment
        }
    
    def build_url(self, base: str, path: str = '', params: Optional[Dict] = None) -> str:
        """Build URL from components"""
        url = urllib.parse.urljoin(base, path)
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
        return url
    
    def parse_query_string(self, query: str) -> Dict[str, List[str]]:
        """Parse query string into dictionary"""
        return urllib.parse.parse_qs(query)
    
    def build_query_string(self, params: Dict[str, Any]) -> str:
        """Build query string from dictionary"""
        return urllib.parse.urlencode(params)
    
    # JSON API helpers
    def get_json(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
        """GET request expecting JSON response"""
        response = self.get(url, params=params, headers=headers)
        if response.is_success():
            return response.json()
        else:
            raise ValueError(f"Request failed with status {response.status_code}")
    
    def post_json(self, url: str, data: Dict, headers: Optional[Dict] = None) -> Any:
        """POST JSON data and expect JSON response"""
        response = self.post(url, json_data=data, headers=headers)
        if response.is_success():
            return response.json()
        else:
            raise ValueError(f"Request failed with status {response.status_code}")
    
    def put_json(self, url: str, data: Dict, headers: Optional[Dict] = None) -> Any:
        """PUT JSON data and expect JSON response"""
        response = self.put(url, json_data=data, headers=headers)
        if response.is_success():
            return response.json()
        else:
            raise ValueError(f"Request failed with status {response.status_code}")
    
    # Rate limiting and retry
    def request_with_retry(self, method: str, url: str, max_retries: int = 3, 
                          backoff_factor: float = 1.0, **kwargs) -> HttpResponse:
        """Make request with automatic retry on failure"""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return self._request(method, url, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    wait_time = backoff_factor * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    raise last_exception
    
    def rate_limited_request(self, method: str, url: str, requests_per_second: float = 1.0, **kwargs) -> HttpResponse:
        """Make rate-limited request"""
        if hasattr(self, '_last_request_time'):
            time_since_last = time.time() - self._last_request_time
            min_interval = 1.0 / requests_per_second
            if time_since_last < min_interval:
                time.sleep(min_interval - time_since_last)
        
        response = self._request(method, url, **kwargs)
        self._last_request_time = time.time()
        return response
    
    # Batch requests
    def batch_get(self, urls: List[str], max_workers: int = 5) -> List[HttpResponse]:
        """Make multiple GET requests concurrently"""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.get, url) for url in urls]
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    # Create a mock response for failed requests
                    class FailedResponse:
                        def __init__(self, error):
                            self.status_code = 0
                            self.text = str(error)
                            self.error = error
                        def is_success(self):
                            return False
                    results.append(FailedResponse(e))
            return results
    
    # WebSocket utilities (basic)
    def is_websocket_url(self, url: str) -> bool:
        """Check if URL is a WebSocket URL"""
        return url.startswith(('ws://', 'wss://'))
    
    def websocket_url_to_http(self, ws_url: str) -> str:
        """Convert WebSocket URL to HTTP URL"""
        if ws_url.startswith('ws://'):
            return ws_url.replace('ws://', 'http://', 1)
        elif ws_url.startswith('wss://'):
            return ws_url.replace('wss://', 'https://', 1)
        return ws_url
    
    # Response utilities
    def is_json_response(self, response: HttpResponse) -> bool:
        """Check if response contains JSON"""
        content_type = response.headers.get('content-type', '').lower()
        return 'application/json' in content_type
    
    def is_html_response(self, response: HttpResponse) -> bool:
        """Check if response contains HTML"""
        content_type = response.headers.get('content-type', '').lower()
        return 'text/html' in content_type
    
    def get_response_size(self, response: HttpResponse) -> int:
        """Get response size in bytes"""
        return len(response.content)
    
    # Status code utilities
    def is_informational(self, status_code: int) -> bool:
        """Check if status code is informational (1xx)"""
        return 100 <= status_code < 200
    
    def is_success(self, status_code: int) -> bool:
        """Check if status code indicates success (2xx)"""
        return 200 <= status_code < 300
    
    def is_redirection(self, status_code: int) -> bool:
        """Check if status code indicates redirection (3xx)"""
        return 300 <= status_code < 400
    
    def is_client_error(self, status_code: int) -> bool:
        """Check if status code indicates client error (4xx)"""
        return 400 <= status_code < 500
    
    def is_server_error(self, status_code: int) -> bool:
        """Check if status code indicates server error (5xx)"""
        return 500 <= status_code < 600
