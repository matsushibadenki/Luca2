# /llm_api/utils/retry.py
# Title: Async Retry Decorator
# Role: Provides a generic asynchronous retry decorator for handling transient errors in API calls.

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Coroutine, Type, Tuple, Optional, Dict, TypeVar, List

logger = logging.getLogger(__name__)

# settingsをインポート
from ..config import settings

# TypeVarを定義してより正確な型付けを行う
T = TypeVar('T')

# --- ▼▼▼ ここから修正 ▼▼▼ ---
# リトライ対象とする例外のリストを安全に構築する

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

# --- ▲▲▲ ここまで修正 ▲▲▲ ---


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
                    return result  # 成功したらここで抜ける
                except Exception as e:
                    last_exception = e  # 最後に発生した例外を記録
                    
                    is_retryable = False
                    # HTTPStatusErrorで5xx系の場合はリトライ対象とする
                    if _HTTPX_AVAILABLE and _HTTPStatusError and isinstance(e, _HTTPStatusError) and 500 <= e.response.status_code < 600:
                        is_retryable = True
                    # その他の定義済みリトライ可能例外に該当する場合
                    elif isinstance(e, retryable_exceptions):
                        is_retryable = True

                    # リトライ可能で、かつまだ試行回数が残っている場合
                    if is_retryable and attempt < max_attempts - 1:
                        wait_time = min(initial_wait * (backoff_factor ** attempt), max_wait)
                        logger.warning(
                            f"Call to '{func.__name__}' failed due to {type(e).__name__}. "
                            f"Retrying in {wait_time:.2f}s... (Attempt {attempt + 1}/{max_attempts})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        # リトライ不可、または最終試行の場合
                        break
            
            # すべての試行が失敗した場合、最後の例外を再発生させる
            if last_exception is not None:
                raise last_exception
            else:
                # 理論的には到達しないはずだが、安全のため例外を発生
                raise RuntimeError(
                    f"Retry wrapper for '{func.__name__}' completed unexpectedly "
                    "without returning a value or recording an exception."
                )
        
        return wrapper
    
    return decorator