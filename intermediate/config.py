from dataclasses import dataclass, field
from os import environ as env


@dataclass
class PgConfig:
    pg_db: str = field(default_factory=lambda: env.get("POSTGRES_DB").strip())
    pg_host: str = field(default_factory=lambda: env.get("POSTGRES_HOST").strip())
    pg_port: int = field(default_factory=lambda: env.get("POSTGRES_PORT").strip())
    pg_user: str = field(default_factory=lambda: env.get("POSTGRES_USER").strip())
    pg_password: str = field(default_factory=lambda: env.get("POSTGRES_PASSWORD").strip())


@dataclass
class RedisConfig:
    redis_host: str = field(default_factory=lambda: env.get("REDIS_HOST").strip())
    redis_port: int = field(default_factory=lambda: env.get("REDIS_PORT").strip())
    redis_db: int = field(default_factory=lambda: env.get("REDIS_DB").strip())


@dataclass
class Config:
    pg: PgConfig = field(default_factory=PgConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
