# /llm_api/utils/retry.py
# Title: Async Retry Decorator
# Role: Provides a generic asynchronous retry decorator for handling transient errors in API calls.

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Coroutine, Type, Tuple, Optional, Dict, TypeVar, List

logger = logging.getLogger(__name__)

from ..config import settings

T = TypeVar('T')

RETRYABLE_EXCEPTIONS_LIST: List[Type[Exception]] = []
_HTTPX_AVAILABLE = False
_HTTPStatusError: Optional[Type[Exception]] = None

try:
    from httpx import RequestError, HTTPStatusError
    RETRYABLE_EXCEPTIONS_LIST.extend([RequestError, HTTPStatusError])
    _HTTPX_AVAILABLE = True
    _HTTPStatusError = HTTPStatusError
except ImportError:
    logger.debug("httpx is not installed. Retry logic for httpx errors will be skipped.")

try:
    from openai import APIConnectionError
    RETRYABLE_EXCEPTIONS_LIST.append(APIConnectionError)
except ImportError:
    logger.debug("openai is not installed. Retry logic for openai errors will be skipped.")

try:
    from anthropic import APIConnectionError as AnthropicAPIConnectionError
    RETRYABLE_EXCEPTIONS_LIST.append(AnthropicAPIConnectionError)
except ImportError:
    logger.debug("anthropic is not installed. Retry logic for anthropic errors will be skipped.")

try:
    from google.api_core.exceptions import ServiceUnavailable, DeadlineExceeded
    RETRYABLE_EXCEPTIONS_LIST.extend([ServiceUnavailable, DeadlineExceeded])
except ImportError:
    logger.debug("google-api-core is not installed. Retry logic for google errors will be skipped.")


RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = tuple(RETRYABLE_EXCEPTIONS_LIST)


def async_retry(
    max_attempts: int = settings.RETRY_MAX_ATTEMPTS,
    initial_wait: float = settings.RETRY_INITIAL_WAIT,
    backoff_factor: float = settings.RETRY_BACKOFF_FACTOR,
    max_wait: float = settings.RETRY_MAX_WAIT,
    retryable_exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS
) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """
    非同期関数が一時的なエラーで失敗した場合に、指数関数的バックオフでリトライするデコレータ。
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_attempts):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    
                    is_retryable = False

                    # ステップA: HTTPステータスエラーがリトライ可能かチェック
                    # isinstanceで型を限定してから、安全に属性にアクセスします
                    if _HTTPX_AVAILABLE and _HTTPStatusError and isinstance(e, _HTTPStatusError):
                        # e.responseが存在し、かつステータスコードが5xx系か確認
                        if hasattr(e, 'response') and e.response and 500 <= e.response.status_code < 600:
                            is_retryable = True
                    
                    # ステップB: 上記でリトライ対象外だった場合に、他のリトライ可能例外リストと照合
                    if not is_retryable and isinstance(e, retryable_exceptions):
                        is_retryable = True

                    if is_retryable and attempt < max_attempts - 1:
                        wait_time = min(initial_wait * (backoff_factor ** attempt), max_wait)
                        logger.warning(
                            f"Call to '{func.__name__}' failed due to {type(e).__name__}. "
                            f"Retrying in {wait_time:.2f}s... (Attempt {attempt + 1}/{max_attempts})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        break
            
            if last_exception is not None:
                raise last_exception
            else:
                raise RuntimeError(
                    f"Retry wrapper for '{func.__name__}' completed unexpectedly "
                    "without returning a value or recording an exception."
                )
        
        return wrapper
    
    return decorator