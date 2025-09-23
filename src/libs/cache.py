import json
import logging
from functools import wraps

from fastapi import Request
from pydantic import BaseModel

from src.libs.redis_app import redis

logger = logging.getLogger(__name__)



def is_primitive(obj):
    """Check if an object is a primitive type (int, float, str, bool)."""
    return isinstance(obj, (int, float, str, bool))


def serialize_arg(arg):
    """
    Serialize an argument for inclusion in the cache key.

    Args:
        arg: The argument to serialize (Pydantic model, primitive, or other).

    Returns:
        str or None: Serialized string if arg is a Pydantic model or primitive, None otherwise.
    """
    if isinstance(arg, BaseModel):
        return arg.model_dump_json()
    elif is_primitive(arg):
        return str(arg)
    return None


def cache(seconds: int = 0, minutes: int = 0, hours: int = 0):
    """
    A decorator to cache FastAPI GET endpoint responses in Redis.

    The cache key is generated from the request URL and serialized user-provided arguments
    (Pydantic DTOs and primitive fields), excluding injected dependencies.
    Caching is only applied to GET requests and can be disabled via the CACHE_ENABLED env var.

    Args:
        seconds (int): Cache expiration time in seconds.
        minutes (int): Cache expiration time in minutes.
        hours (int): Cache expiration time in hours.

    Returns:
        Callable: Decorated endpoint function with caching.

    Raises:
        ValueError: If the request object is not provided in the endpoint signature.
    """

    expiration = seconds + minutes * 60 + hours * 60 * 60

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if request is None:
                raise ValueError(
                    "Request object is required for caching. Add 'request: Request' to endpoint signature.")

            serializable_args = []
            for key, value in kwargs.items():
                if key == "request":
                    continue
                serialized = serialize_arg(value)
                if serialized is not None:
                    serializable_args.append((key, serialized))

            serializable_args.sort()
            args_str = "-".join(f"{key}:{value}" for key, value in serializable_args)

            key = f"cache:{request.method}:{request.url.path}:{args_str}"

            try:
                cached = await redis.get(key)
                if cached:
                    logger.info(f"Cache hit for key: {key}")
                    return json.loads(cached)
                logger.info(f"Cache miss for key: {key}")
            except Exception as e:
                logger.error(f"Cache retrieval error for {key}: {e}")

            response = await func(*args, **kwargs)
            try:
                serialized_response = json.dumps(response)
                await redis.set(key, serialized_response, ex=expiration)
                logger.debug(f"Cached response for {key} with expiration {expiration}s")
            except Exception as e:
                logger.error(f"Failed to cache response for {key}: {e}")

            return response

        return wrapper

    return decorator
