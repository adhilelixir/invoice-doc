import redis
from app.core.config import settings

# Create Redis client
# In production, you might want to handle connection errors gracefully
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_inventory_cache(sku: str):
    return redis_client.get(f"inventory:{sku}")

def set_inventory_cache(sku: str, quantity: int):
    redis_client.set(f"inventory:{sku}", quantity)

def delete_inventory_cache(sku: str):
    redis_client.delete(f"inventory:{sku}")
