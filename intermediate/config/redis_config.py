from dataclasses import  dataclass
from environs import Env


@dataclass
class RedisConfig:
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str

    @staticmethod
    def from_env(env: Env):
        redis_host = env.str("REDIS_HOST")
        redis_port = env.int("REDIS_PORT")
        redis_db = env.str("REDIS_DB")
        redis_password = env.str("REDIS_PASSWORD")

        return RedisConfig(
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db,
            redis_password=redis_password
        )