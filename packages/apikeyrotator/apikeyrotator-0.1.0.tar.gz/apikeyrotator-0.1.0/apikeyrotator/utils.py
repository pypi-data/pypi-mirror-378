import asyncio
import time
from typing import Callable, Any, Type, Union
import requests


def retry_with_backoff(
        func: Callable,
        retries: int = 3,
        backoff_factor: float = 0.5,
        exceptions: Type[Exception] = Exception
) -> Any:
    """
    Универсальная функция для повторных попыток с экспоненциальной задержкой.

    Пример использования:
    response = retry_with_backoff(
        lambda: requests.get('https://api.example.com'),
        exceptions=requests.RequestException
    )
    """
    for attempt in range(retries):
        try:
            return func()
        except exceptions as e:
            if attempt == retries - 1:
                raise e
            delay = backoff_factor * (2 ** attempt)
            time.sleep(delay)
            print(f"Retry {attempt + 1}/{retries} after {delay:.1f}s delay")


async def async_retry_with_backoff(
        func: Callable,
        retries: int = 3,
        backoff_factor: float = 0.5,
        exceptions: Type[Exception] = Exception
) -> Any:
    """
    Асинхронная универсальная функция для повторных попыток с экспоненциальной задержкой.

    Пример использования:
    response = await async_retry_with_backoff(
        lambda: aiohttp.ClientSession().get('https://api.example.com'),
        exceptions=aiohttp.ClientError
    )
    """
    for attempt in range(retries):
        try:
            return await func()
        except exceptions as e:
            if attempt == retries - 1:
                raise e
            delay = backoff_factor * (2 ** attempt)
            await asyncio.sleep(delay)
            print(f"Async Retry {attempt + 1}/{retries} after {delay:.1f}s delay")

