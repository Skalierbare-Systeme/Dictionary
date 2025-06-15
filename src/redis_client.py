import logging

import redis
from redis import Redis, RedisError
from src.models import Ingredient
import os

redis_ip = str(os.getenv('REDIS_IP') or 'localhost')
redis_port = int(os.getenv('REDIS_PORT') or '6379')

redis_pool = redis.ConnectionPool(host=redis_ip, port=redis_port)


def connect_to_redis() -> Redis:
    try:
        return redis.Redis.from_pool(redis_pool)
    except RedisError as e:
        raise RedisError(f"Redis error: {e}") from e


def add_new_pair(connection: Redis, ingredient: Ingredient) -> bool:
    try:
        result = get_pair(connection, ingredient.ingredient_name)
        if result:
            raise ValueError("Ingredient already exists")
        result = connection.set(ingredient.ingredient_name, ingredient.ingredient_definition)
        if not result:
            raise ValueError("failed to set the value")
        return True
    except redis.RedisError as e:
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
        values: list[bytes] | None = connection.mget(keys)
    except RedisError as e:
        raise RedisError(f"Redis error: {e}") from e
    ingredients: list[Ingredient] = []
    for i in range(len(values)):
        ingredients.append(Ingredient(keys[i], values[i].decode("utf-8")))

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
