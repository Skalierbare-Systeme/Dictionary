import logging

import redis
from redis import Redis, RedisError
from src.models import Ingredient
import os

redis_ip = str(os.getenv('REDIS_IP') or 'redis-db')
redis_port = int(os.getenv('REDIS_PORT') or '6379')

redis_pool = redis.ConnectionPool(host=redis_ip, port=redis_port)


def connect_to_redis() -> Redis:
    try:
        connection = redis.Redis.from_pool(redis_pool)
        connection.ping()  # Force test of connection
        return connection
    except RedisError as e:
        raise RedisError(f"Redis error: {e}") from e

def add_new_pair(connection: Redis, ingredient: Ingredient) -> bool:
    """
    Adds a new ingredient to Redis, but only if it doesn't already exist.
    This is an atomic operation.
    """
    try:
        # Use nx=True to "set if not exists"
        # It returns True if the key was set (because it was new)
        # It returns False if the key already existed and was NOT set
        was_set = connection.set(
            ingredient.ingredient_name,
            ingredient.ingredient_definition,
            nx=True
        )

        if not was_set:
            # This is not a technical error, but a business logic rule.
            # The key already exists, so we raise a ValueError to stop the process.
            raise ValueError("Ingredient already exists")

        return True

    except redis.RedisError as e:
        # This catches actual database connection errors
        raise RedisError(f"Redis error: {e}") from e



def get_pair(connection: Redis, ingredient_name: str) -> Ingredient:
    try:
        result : bytes | None= connection.get(ingredient_name)
        if not result:
            raise RedisError("failed to get the value")
        return Ingredient(ingredient_name, result.decode("utf-8"))
    except redis.RedisError as e:
        raise RedisError(f"Redis error: {e}") from e


def get_multiple_pairs(connection: Redis, keys: list[str]) -> list[Ingredient]:
    try:
        values: list[bytes | None] = connection.mget(keys)
    except RedisError as e:
        raise RedisError(f"Redis error: {e}") from e

    ingredients: list[Ingredient] = []
    for i in range(len(values)):
        if values[i] is not None:
            ingredients.append(Ingredient(keys[i], values[i].decode("utf-8")))
        else:
            # Optional: log or handle missing key
            logging.warning(f"Key '{keys[i]}' not found in Redis.")

    return ingredients


def delete_pair(connection: Redis, ingredient_name: str)-> bool:
    try:
        result = connection.delete(ingredient_name)
        if result:
            return True
        else:
            raise RuntimeError("failed to delete the value")
    except RedisError as e:
        raise RedisError(f"Redis error: {e}") from e
