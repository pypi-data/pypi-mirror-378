"""
MeroHub Core GitHub Integration Module
Author: MERO (Telegram: @QP4RM)

Core classes for GitHub API integration, authentication, and configuration management.
Provides the fundamental building blocks for all GitHub operations in MeroHub.
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
import threading
from urllib.parse import urljoin, urlparse, parse_qs
import base64
import hashlib
import hmac
from dataclasses import dataclass, field
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from .exceptions import (
    AuthenticationError, APIError, ValidationError, 
    NetworkError, RateLimitError, ConfigurationError,
    create_error_from_response, validate_github_token
)
from .utils import Logger, ConfigManager, SecurityManager, retry_on_exception, rate_limit


@dataclass
class GitHubConfig:
    """Configuration container for GitHub API settings."""
    
    token: Optional[str] = None
    base_url: str = "https://api.github.com"
    timeout: int = 30
    retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    user_agent: str = "MeroHub/1.0.0"
    accept_header: str = "application/vnd.github+json"
    api_version: str = "2022-11-28"
    per_page: int = 30
    max_pages: int = 100
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes
    enable_rate_limit_handling: bool = True
    auto_retry_on_rate_limit: bool = True
    webhook_secret: Optional[str] = None
    app_id: Optional[int] = None
    private_key: Optional[str] = None
    installation_id: Optional[int] = None
    config_path: Optional[str] = None
    debug_mode: bool = False
    enable_metrics: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.token:
            validate_github_token(self.token)
        
        if self.base_url and not self.base_url.startswith(('http://', 'https://')):
            raise ConfigurationError(f"Invalid base URL: {self.base_url}")
        
        if self.timeout <= 0:
            raise ConfigurationError("Timeout must be positive")
        
        if self.retries < 0:
            raise ConfigurationError("Retries cannot be negative")
    
    def update_token(self, token: str):
        """Update GitHub token with validation."""
        validate_github_token(token)
        self.token = token
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                config_dict[key] = value
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'GitHubConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def merge(self, other: 'GitHubConfig') -> 'GitHubConfig':
        """Merge with another configuration."""
        merged_dict = self.to_dict()
        merged_dict.update(other.to_dict())
        return GitHubConfig.from_dict(merged_dict)
    
    def clone(self) -> 'GitHubConfig':
        """Create a copy of the configuration."""
        return GitHubConfig.from_dict(self.to_dict())


class GitHubAuth:
    """Advanced authentication manager for GitHub API."""
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.logger = Logger("GitHubAuth")
        self.security = SecurityManager()
        
        # Authentication state
        self._authenticated = False
        self._user_info = None
        self._permissions = []
        self._token_info = None
        self._app_installation_token = None
        self._app_installation_expires = None
        
        # JWT for GitHub Apps
        self._jwt_token = None
        self._jwt_expires = None
        
        # Session management
        self._session_start = None
        self._last_activity = None
        
        # Rate limiting info
        self._rate_limit_info = {
            'limit': 5000,
            'remaining': 5000,
            'reset': int(time.time()) + 3600,
            'used': 0
        }
    
    def authenticate(self) -> bool:
        """Authenticate with GitHub using configured method."""
        try:
            if self.config.token:
                return self._authenticate_with_token()
            elif self.config.app_id and self.config.private_key:
                return self._authenticate_as_app()
            else:
                raise AuthenticationError("No authentication method configured")
                
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            self._authenticated = False
            return False
    
    def _authenticate_with_token(self) -> bool:
        """Authenticate using personal access token."""
        self.logger.info("Authenticating with personal access token")
        
        # Validate token format
        token_validation = self.security.validate_token(self.config.token)
        if not token_validation['valid']:
            raise AuthenticationError(
                "Invalid token format",
                token_status="invalid_format",
                details=token_validation
            )
        
        # Test token with GitHub API
        headers = {
            'Authorization': f'token {self.config.token}',
            'Accept': self.config.accept_header,
            'User-Agent': self.config.user_agent,
            'X-GitHub-Api-Version': self.config.api_version
        }
        
        try:
            response = requests.get(
                f"{self.config.base_url}/user",
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self._user_info = response.json()
                self._authenticated = True
                self._session_start = datetime.now()
                self._last_activity = datetime.now()
                
                # Get token permissions
                self._get_token_permissions(headers)
                
                self.logger.info(f"Authenticated as: {self._user_info.get('login')}")
                return True
            else:
                error = create_error_from_response(response, '/user', 'GET')
                raise error
                
        except requests.RequestException as e:
            raise NetworkError(f"Network error during authentication: {e}")
    
    def _authenticate_as_app(self) -> bool:
        """Authenticate as GitHub App."""
        self.logger.info("Authenticating as GitHub App")
        
        # Generate JWT for GitHub App
        jwt_token = self._generate_app_jwt()
        
        # Get installation token
        installation_token = self._get_installation_token(jwt_token)
        
        if installation_token:
            self.config.token = installation_token
            self._app_installation_token = installation_token
            self._app_installation_expires = datetime.now() + timedelta(minutes=55)  # GitHub tokens expire in 1 hour
            
            return self._authenticate_with_token()
        
        return False
    
    def _generate_app_jwt(self) -> str:
        """Generate JWT for GitHub App authentication."""
        if not self.config.app_id or not self.config.private_key:
            raise AuthenticationError("GitHub App ID and private key required")
        
        # Load private key
        try:
            private_key_bytes = self.config.private_key.encode('utf-8')
            private_key = serialization.load_pem_private_key(
                private_key_bytes, 
                password=None
            )
        except Exception as e:
            raise AuthenticationError(f"Invalid private key: {e}")
        
        # Create JWT payload
        now = int(time.time())
        payload = {
            'iat': now,
            'exp': now + 600,  # 10 minutes
            'iss': self.config.app_id
        }
        
        # Sign JWT
        jwt_token = jwt.encode(payload, private_key, algorithm='RS256')
        
        self._jwt_token = jwt_token
        self._jwt_expires = datetime.now() + timedelta(minutes=10)
        
        return jwt_token
    
    def _get_installation_token(self, jwt_token: str) -> Optional[str]:
        """Get installation access token using JWT."""
        if not self.config.installation_id:
            raise AuthenticationError("GitHub App installation ID required")
        
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': self.config.accept_header,
            'User-Agent': self.config.user_agent,
            'X-GitHub-Api-Version': self.config.api_version
        }
        
        url = f"{self.config.base_url}/app/installations/{self.config.installation_id}/access_tokens"
        
        try:
            response = requests.post(url, headers=headers, timeout=self.config.timeout)
            
            if response.status_code == 201:
                token_data = response.json()
                return token_data['token']
            else:
                error = create_error_from_response(response, url, 'POST')
                raise error
                
        except requests.RequestException as e:
            raise NetworkError(f"Network error getting installation token: {e}")
    
    def _get_token_permissions(self, headers: Dict[str, str]):
        """Get token permissions and scopes."""
        try:
            # Check token scopes via the /user endpoint headers
            response = requests.head(
                f"{self.config.base_url}/user",
                headers=headers,
                timeout=self.config.timeout
            )
            
            scopes_header = response.headers.get('X-OAuth-Scopes', '')
            self._permissions = [scope.strip() for scope in scopes_header.split(',') if scope.strip()]
            
            # Get rate limit info
            self._update_rate_limit_from_headers(response.headers)
            
        except Exception as e:
            self.logger.warning(f"Could not get token permissions: {e}")
    
    def _update_rate_limit_from_headers(self, headers: Dict[str, str]):
        """Update rate limit information from response headers."""
        try:
            if 'X-RateLimit-Limit' in headers:
                self._rate_limit_info.update({
                    'limit': int(headers['X-RateLimit-Limit']),
                    'remaining': int(headers['X-RateLimit-Remaining']),
                    'reset': int(headers['X-RateLimit-Reset']),
                    'used': int(headers['X-RateLimit-Used'])
                })
        except (ValueError, KeyError) as e:
            self.logger.debug(f"Could not parse rate limit headers: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        if not self._authenticated:
            return False
        
        # Check if app installation token needs renewal
        if (self._app_installation_token and 
            self._app_installation_expires and 
            datetime.now() >= self._app_installation_expires):
            
            self.logger.info("App installation token expired, renewing")
            return self.authenticate()
        
        return True
    
    def get_authenticated_user(self) -> Optional[str]:
        """Get authenticated user login."""
        if self._user_info:
            return self._user_info.get('login')
        return None
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information."""
        return self._user_info or {}
    
    def get_permissions(self) -> List[str]:
        """Get token permissions/scopes."""
        return self._permissions.copy()
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit information."""
        return self._rate_limit_info.copy()
    
    def has_permission(self, permission: str) -> bool:
        """Check if token has specific permission."""
        return permission in self._permissions
    
    def refresh_token(self) -> bool:
        """Refresh authentication token if possible."""
        if self.config.app_id and self.config.private_key:
            return self._authenticate_as_app()
        else:
            # For personal access tokens, just re-authenticate
            return self.authenticate()
    
    def revoke_token(self) -> bool:
        """Revoke the current token."""
        if not self.is_authenticated():
            return False
        
        try:
            headers = {
                'Authorization': f'token {self.config.token}',
                'Accept': self.config.accept_header,
                'User-Agent': self.config.user_agent
            }
            
            # For personal access tokens
            if self.config.token.startswith(('ghp_', 'github_pat_')):
                response = requests.delete(
                    f"{self.config.base_url}/applications/{self.config.app_id}/token",
                    headers=headers,
                    json={'access_token': self.config.token},
                    timeout=self.config.timeout
                )
                
                success = response.status_code == 204
            else:
                # Cannot revoke app installation tokens directly
                success = True
            
            if success:
                self._reset_auth_state()
                self.logger.info("Token revoked successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to revoke token: {e}")
            return False
    
    def _reset_auth_state(self):
        """Reset authentication state."""
        self._authenticated = False
        self._user_info = None
        self._permissions = []
        self._token_info = None
        self._app_installation_token = None
        self._app_installation_expires = None
        self._jwt_token = None
        self._jwt_expires = None
        self._session_start = None
        self._last_activity = None
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated")
        
        headers = {
            'Authorization': f'token {self.config.token}',
            'Accept': self.config.accept_header,
            'User-Agent': self.config.user_agent,
            'X-GitHub-Api-Version': self.config.api_version
        }
        
        # Add custom headers
        headers.update(self.config.custom_headers)
        
        # Update last activity
        self._last_activity = datetime.now()
        
        return headers
    
    def validate_webhook(self, payload: bytes, signature: str) -> bool:
        """Validate GitHub webhook signature."""
        if not self.config.webhook_secret:
            self.logger.warning("No webhook secret configured")
            return False
        
        expected_signature = hmac.new(
            self.config.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        expected_signature = f"sha256={expected_signature}"
        
        return hmac.compare_digest(expected_signature, signature)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        return {
            'authenticated': self._authenticated,
            'user': self.get_authenticated_user(),
            'permissions': self._permissions,
            'session_start': self._session_start.isoformat() if self._session_start else None,
            'last_activity': self._last_activity.isoformat() if self._last_activity else None,
            'session_duration': str(datetime.now() - self._session_start) if self._session_start else None,
            'rate_limit': self._rate_limit_info,
            'token_type': 'app' if self._app_installation_token else 'personal'
        }


class GitHubCore:
    """Core GitHub API client with advanced features."""
    
    def __init__(self, config: GitHubConfig, auth: GitHubAuth):
        self.config = config
        self.auth = auth
        self.logger = Logger("GitHubCore")
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent,
            'Accept': config.accept_header,
            'X-GitHub-Api-Version': config.api_version
        })
        
        # Request metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'cached_responses': 0,
            'average_response_time': 0.0,
            'last_request_time': None,
            'endpoints_used': {},
            'status_codes': {}
        }
        
        # Response cache
        self.cache = {} if config.enable_caching else None
        self.cache_lock = threading.Lock() if config.enable_caching else None
        
        # Rate limiting
        self._last_request_time = 0
        self._request_count = 0
        self._rate_limit_lock = threading.Lock()
    
    @retry_on_exception(max_retries=3, delay=1.0, backoff_factor=2.0)
    @rate_limit(calls=5000, period=3600)  # Default GitHub rate limit
    def make_request(self, method: str, endpoint: str, 
                    params: Optional[Dict[str, Any]] = None,
                    data: Optional[Union[Dict[str, Any], str]] = None,
                    json_data: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None,
                    timeout: Optional[int] = None,
                    allow_redirects: bool = True,
                    stream: bool = False) -> requests.Response:
        """Make authenticated request to GitHub API."""
        
        if not self.auth.is_authenticated():
            raise AuthenticationError("Authentication required")
        
        # Prepare request
        url = self._build_url(endpoint)
        request_headers = self.auth.get_auth_headers()
        
        if headers:
            request_headers.update(headers)
        
        # Check cache first
        cache_key = None
        if self.config.enable_caching and method.upper() == 'GET':
            cache_key = self._generate_cache_key(method, url, params, json_data)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self.metrics['cached_responses'] += 1
                return cached_response
        
        # Make request
        start_time = time.time()
        
        try:
            self.logger.debug(f"Making {method} request to {endpoint}")
            
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=timeout or self.config.timeout,
                allow_redirects=allow_redirects,
                stream=stream
            )
            
            # Update metrics
            end_time = time.time()
            response_time = end_time - start_time
            self._update_metrics(method, endpoint, response.status_code, response_time)
            
            # Update rate limit info
            self.auth._update_rate_limit_from_headers(response.headers)
            
            # Handle rate limiting
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                self._handle_rate_limit(response)
            
            # Check for errors
            if not response.ok:
                error = create_error_from_response(response, endpoint, method)
                self.metrics['failed_requests'] += 1
                raise error
            
            # Cache successful GET responses
            if (self.config.enable_caching and method.upper() == 'GET' and 
                cache_key and response.status_code == 200):
                self._cache_response(cache_key, response)
            
            self.metrics['successful_requests'] += 1
            return response
            
        except requests.RequestException as e:
            self.metrics['failed_requests'] += 1
            raise NetworkError(f"Network error: {e}")
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self.make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request."""
        return self.make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PUT request."""
        return self.make_request('PUT', endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PATCH request."""
        return self.make_request('PATCH', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        return self.make_request('DELETE', endpoint, **kwargs)
    
    def get_json(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make GET request and return JSON response."""
        response = self.get(endpoint, **kwargs)
        return response.json()
    
    def post_json(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make POST request and return JSON response."""
        response = self.post(endpoint, **kwargs)
        return response.json() if response.content else {}
    
    def paginate(self, endpoint: str, 
                per_page: Optional[int] = None,
                max_pages: Optional[int] = None,
                **kwargs) -> List[Dict[str, Any]]:
        """Paginate through all results."""
        
        all_items = []
        page = 1
        per_page = per_page or self.config.per_page
        max_pages = max_pages or self.config.max_pages
        
        while page <= max_pages:
            params = kwargs.get('params', {})
            params.update({
                'per_page': per_page,
                'page': page
            })
            kwargs['params'] = params
            
            try:
                response = self.get(endpoint, **kwargs)
                items = response.json()
                
                if not items or not isinstance(items, list):
                    break
                
                all_items.extend(items)
                
                # Check if there are more pages
                link_header = response.headers.get('Link', '')
                if 'rel="next"' not in link_header:
                    break
                
                page += 1
                
            except Exception as e:
                self.logger.warning(f"Pagination stopped at page {page}: {e}")
                break
        
        return all_items
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        return urljoin(self.config.base_url, endpoint)
    
    def _generate_cache_key(self, method: str, url: str, 
                          params: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key for request."""
        key_parts = [method, url]
        
        if params:
            key_parts.append(json.dumps(params, sort_keys=True))
        
        if json_data:
            key_parts.append(json.dumps(json_data, sort_keys=True))
        
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[requests.Response]:
        """Get cached response if available and not expired."""
        if not self.cache or not self.cache_lock:
            return None
        
        with self.cache_lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                
                # Check if cache is still valid
                if time.time() - timestamp < self.config.cache_ttl:
                    # Recreate response object
                    response = requests.Response()
                    response._content = cached_data['content'].encode('utf-8')
                    response.status_code = cached_data['status_code']
                    response.headers.update(cached_data['headers'])
                    response.url = cached_data['url']
                    
                    return response
                else:
                    # Remove expired cache entry
                    del self.cache[cache_key]
        
        return None
    
    def _cache_response(self, cache_key: str, response: requests.Response):
        """Cache response data."""
        if not self.cache or not self.cache_lock:
            return
        
        with self.cache_lock:
            cached_data = {
                'content': response.text,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'url': response.url
            }
            
            self.cache[cache_key] = (cached_data, time.time())
            
            # Clean up old cache entries (simple LRU)
            if len(self.cache) > 1000:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
    
    def _handle_rate_limit(self, response: requests.Response):
        """Handle rate limit response."""
        self.metrics['rate_limited_requests'] += 1
        
        if self.config.auto_retry_on_rate_limit:
            reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
            wait_time = max(reset_time - time.time(), 1)
            
            self.logger.warning(f"Rate limited. Waiting {wait_time} seconds")
            time.sleep(wait_time)
        else:
            raise RateLimitError(
                "GitHub API rate limit exceeded",
                reset_time=int(response.headers.get('X-RateLimit-Reset')),
                remaining=int(response.headers.get('X-RateLimit-Remaining', 0)),
                limit=int(response.headers.get('X-RateLimit-Limit', 5000))
            )
    
    def _update_metrics(self, method: str, endpoint: str, 
                       status_code: int, response_time: float):
        """Update request metrics."""
        self.metrics['total_requests'] += 1
        self.metrics['last_request_time'] = datetime.now().isoformat()
        
        # Update average response time
        total_time = (self.metrics['average_response_time'] * 
                     (self.metrics['total_requests'] - 1) + response_time)
        self.metrics['average_response_time'] = total_time / self.metrics['total_requests']
        
        # Track endpoint usage
        if endpoint not in self.metrics['endpoints_used']:
            self.metrics['endpoints_used'][endpoint] = 0
        self.metrics['endpoints_used'][endpoint] += 1
        
        # Track status codes
        if status_code not in self.metrics['status_codes']:
            self.metrics['status_codes'][status_code] = 0
        self.metrics['status_codes'][status_code] += 1
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        try:
            response = self.get('/rate_limit')
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get rate limit: {e}")
            return self.auth.get_rate_limit_info()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics."""
        return self.metrics.copy()
    
    def clear_cache(self):
        """Clear response cache."""
        if self.cache and self.cache_lock:
            with self.cache_lock:
                self.cache.clear()
    
    def reset_metrics(self):
        """Reset client metrics."""
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'cached_responses': 0,
            'average_response_time': 0.0,
            'last_request_time': None,
            'endpoints_used': {},
            'status_codes': {}
        }
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
        self.logger.info("GitHubCore session closed")


__all__ = [
    'GitHubConfig',
    'GitHubAuth', 
    'GitHubCore'
]