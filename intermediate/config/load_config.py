from dataclasses import  dataclass
from typing import Optional

from environs import  Env

from .pg_config import  PgConfig
from .redis_config import RedisConfig


@dataclass
class Config:
    pg: PgConfig
    redis: RedisConfig


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path)

    return  Config(
        pg=PgConfig.from_env(env=env),
        redis=RedisConfig.from_env(env=env)
    )



