from dataclasses import  dataclass
from environs import  Env

@dataclass
class PgConfig:
    pg_db: str
    pg_host: str
    pg_port: int
    pg_user: str
    pg_password: str

    @staticmethod
    def from_env(env: Env):
        pg_db = env.str("POSTGRES_DB")
        pg_host = env.str("POSTGRES_HOST")
        pg_port = env.str("POSTGRES_PORT")
        pg_user = env.str("POSTGRES_USER")
        pg_password = env.str("POSTGRES_PASSWORD")

        return PgConfig(
            pg_db=pg_db,
            pg_host=pg_host,
            pg_port=pg_port,
            pg_user=pg_user,
            pg_password=pg_password
        )



