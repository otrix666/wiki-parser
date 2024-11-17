from redis import Redis

from intermediate.app.errors import CustomRedisError


class RedisClient:
    def __init__(self, connection: Redis):
        self.client = connection

    def add_urls(self, urls: set[str]):
        try:
            self.client.sadd("saved_urls", *urls)
        except Exception as e:
            raise CustomRedisError(f"add redis urls error: {e}") from e

    def get_saved_urls(self) -> set[str]:
        try:
            return {url.decode("utf-8") for url in self.client.smembers("saved_urls")}
        except Exception as e:
            raise CustomRedisError(f"get saved urls error: {e}") from e

    def clear_urls(self):
        try:
            return self.client.delete("saved_urls")
        except Exception as e:
            raise CustomRedisError(f"clear saved urls error: {e}") from e
