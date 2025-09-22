from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from src.idosell._common import Gateway


@dataclass
class RequestConfig:
    """Configuration object for API requests to reduce parameter count."""
    client: Optional[httpx.Client] = None
    headers: Optional[Dict[str, str]] = None
    auth: Optional[httpx.Auth] = None
    bearer_token: Optional[str] = None
    api_key_header: str = "X-API-KEY"
    timeout: Optional[float | httpx.Timeout] = None

class ApiRequest:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,  # Force keyword-only arguments
        config: Optional[RequestConfig] = None,
        client: Optional[httpx.Client] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[httpx.Auth] = None,
        bearer_token: Optional[str] = None,
        api_key_header: str = "X-API-KEY",
        timeout: Optional[float | httpx.Timeout] = None
    ):
        """Initialize ApiRequest with required base_url and api_key.

        Args:
            base_url: API base URL (required)
            api_key: API key (required)
            config: RequestConfig object with additional settings
            client: Pre-configured httpx.Client
            headers: Extra headers
            auth: Authentication object
            bearer_token: Bearer token for authorization
            api_key_header: Header name for API key
            timeout: Request timeout
        """
        self.base_url = base_url
        self.api_key = api_key

        if config is not None:
            self.config = config
        else:
            self.config = RequestConfig(
                client=client,
                headers=headers,
                auth=auth,
                bearer_token=bearer_token,
                api_key_header=api_key_header,
                timeout=timeout
            )

    def _encode_query_value(self, value: Any) -> Any:
        # Enums -> their value, lists/sets/tuples -> comma-separated, bools -> "true"/"false"
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, (list, tuple, set)):
            return ",".join(str(self._encode_query_value(v)) for v in value) # type: ignore
        if isinstance(value, bool):
            return "true" if value else "false"
        return value

    def _build_query_params(self, model: BaseModel) -> Dict[str, Any]:
        # Prefer model's custom builder if present
        build_q = getattr(model, "build_query", None)
        if callable(build_q):
            params = build_q()
            # Ensure final encoding
            return {k: self._encode_query_value(v) for k, v in params.items() if v is not None}  # type: ignore

        # Generic pydantic v2 dump with aliases for camelCase
        data = model.model_dump(by_alias=True, exclude_none=True)
        return {k: self._encode_query_value(v) for k, v in data.items()}

    def _merge_headers(
        self,
        headers: Optional[Dict[str, str]],
        bearer_token: Optional[str],
        api_key: Optional[str],
        api_key_header: str,
    ) -> Dict[str, str]:
        final = {
            "Accept": "application/json",
            "User-Agent": "idosell-python-httpx",
        }
        if headers:
            final.update(headers)
        if bearer_token:
            final["Authorization"] = f"Bearer {bearer_token}"
        if api_key:
            final[api_key_header] = api_key
        return final

    def _build_request_data(self, dto: Gateway, method: str) -> tuple[Optional[Dict[str, Any]], Any]:
        """Build query parameters and JSON body based on HTTP method and DTO."""
        json_body: Any = None
        params: Optional[Dict[str, Any]] = None

        if method in {"GET", "HEAD"}:
            params = self._build_query_params(dto)
        else:
            # Allow DTO to provide custom query params even for non-GET
            build_q = getattr(dto, "build_query", None)
            if callable(build_q):
                q = build_q()
                params = {k: self._encode_query_value(v) for k, v in q.items() if v is not None}  # type: ignore

            # Prefer DTO-provided body if present; otherwise dump the DTO as JSON
            build_b = getattr(dto, "build_body", None)
            if callable(build_b):
                json_body = build_b()
            else:
                json_body = dto.model_dump(by_alias=True, exclude_none=True)

        return params, json_body

    def _merge_request_config(self, override_config: RequestConfig) -> RequestConfig:
        """Merge request-specific config with instance config, preferring request-specific values."""
        return RequestConfig(
            client=override_config.client or self.config.client,
            headers=override_config.headers or self.config.headers,
            auth=override_config.auth or self.config.auth,
            bearer_token=override_config.bearer_token or self.config.bearer_token,
            api_key_header=override_config.api_key_header,
            timeout=override_config.timeout or self.config.timeout,
        )

    def _setup_client(self, config: RequestConfig) -> tuple[httpx.Client, bool]:
        """Set up HTTP client, returning (client, owns_client)."""
        if config.client is not None:
            return config.client, False

        client = httpx.Client(base_url=self.base_url, timeout=config.timeout)
        return client, True

    def _setup_async_client(self, config: RequestConfig) -> tuple[httpx.AsyncClient, bool]:
        """Set up async HTTP client, returning (client, owns_client)."""
        # Note: config.client might be AsyncClient, but we need type checking
        if hasattr(config, 'client') and isinstance(getattr(config, 'client', None), httpx.AsyncClient):
            return config.client, False # type: ignore

        client = httpx.AsyncClient(base_url=self.base_url, timeout=config.timeout)
        return client, True

    def _process_response(self, response: httpx.Response, raise_for_status: bool, parse_json: bool) -> Any:
        """Process HTTP response based on configuration."""
        if raise_for_status:
            response.raise_for_status()
            return response.json() if parse_json else response

        if response.is_error:
            if parse_json:
                return {
                    "_error": {
                        "status_code": response.status_code,
                        "reason": response.reason_phrase,
                        "url": str(response.request.url),
                        "body": response.text,
                    }
                }
            return response

        return response.json() if parse_json else response

    async def _process_async_response(self, response: httpx.Response, raise_for_status: bool, parse_json: bool) -> Any:
        """Process async HTTP response based on configuration."""
        if raise_for_status:
            response.raise_for_status()
            return response.json() if parse_json else response

        if response.is_error:
            if parse_json:
                return {
                    "_error": {
                        "status_code": response.status_code,
                        "reason": response.reason_phrase,
                        "url": str(response.request.url),
                        "body": response.text,
                    }
                }
            return response

        return response.json() if parse_json else response

    def request(
        self,
        dto: Gateway,
        *,  # Force keyword-only arguments
        config: Optional[RequestConfig] = None,
        raise_for_status: bool = False,
        parse_json: bool = True
    ) -> Any:
        """
        Execute HTTP request for Gateway-based DTOs.

        Args:
            dto: Pydantic model with `_endpoint` and optional `_method` (defaults to GET)
            config: RequestConfig object with request-specific settings
            raise_for_status: If True, raises on 4xx/5xx
            parse_json: If True, returns response.json(); otherwise returns httpx.Response
        """
        # Get method and endpoint from DTO
        method = getattr(dto, "_method", "GET").upper()
        endpoint = getattr(dto, "_endpoint", None)
        if not endpoint:
            raise ValueError("DTO must define a private '_endpoint' attribute")

        # Merge configuration
        final_config = self._merge_request_config(config or RequestConfig())

        # Build request data
        params, json_body = self._build_request_data(dto, method)

        # Prepare headers with authentication
        headers = self._merge_headers(
            final_config.headers,
            final_config.bearer_token,
            self.api_key,
            final_config.api_key_header
        )

        # Set up client
        client, owns_client = self._setup_client(final_config)

        try:
            response = client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_body,
                headers=headers,
                auth=final_config.auth,
                timeout=final_config.timeout,
            )
            return self._process_response(response, raise_for_status, parse_json)
        finally:
            if owns_client:
                client.close()

    async def async_request(
        self,
        dto: Gateway,
        *,  # Force keyword-only arguments
        config: Optional[RequestConfig] = None,
        raise_for_status: bool = False,
        parse_json: bool = True
    ) -> Any:
        """
        Execute async HTTP request for Gateway-based DTOs.

        Args:
            dto: Pydantic model with `_endpoint` and optional `_method` (defaults to GET)
            config: RequestConfig object with request-specific settings
            raise_for_status: If True, raises on 4xx/5xx
            parse_json: If True, returns response.json(); otherwise returns httpx.Response
        """
        # Get method and endpoint from DTO
        method = getattr(dto, "_method", "GET").upper()
        endpoint = getattr(dto, "_endpoint", None)
        if not endpoint:
            raise ValueError("DTO must define a private '_endpoint' attribute")

        # Merge configuration
        final_config = self._merge_request_config(config or RequestConfig())

        # Build request data
        params, json_body = self._build_request_data(dto, method)

        # Prepare headers with authentication
        headers = self._merge_headers(
            final_config.headers,
            final_config.bearer_token,
            self.api_key,
            final_config.api_key_header
        )

        # Set up async client
        client, owns_client = self._setup_async_client(final_config)

        try:
            response = await client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_body,
                headers=headers,
                auth=final_config.auth,
                timeout=final_config.timeout,
            )
            return await self._process_async_response(response, raise_for_status, parse_json)
        finally:
            if owns_client:
                await client.aclose()
