import logging

from redis.asyncio import Redis, from_url
from redis.exceptions import RedisError

from taskhub.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Redis = from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> Redis:
    return redis_client


async def delete_keys_by_pattern(redis: Redis, pattern: str) -> None:
    try:
        # Scan là cơ chế duyệt danh sách key theo phân trang bằng con trỏ,
        # giúp tìm kiếm key mà không làm đóng băng Redis.
        keys = [key async for key in redis.scan_iter(match=pattern)]
        if keys:
            await redis.delete(*keys)
    except RedisError as exc:
        logger.warning("Xóa cache Redis thất bại với mẫu %s: %s", pattern, exc)
