import os
import secrets
from datetime import datetime
from pydantic import BaseSettings


class Settings(BaseSettings):

    OVERSTOCK_LIST_URL: str = "https://cs.money/list_overstock?appId=730"
    ITEMS_ON_PAGE_WITH_FOLLOWING_ITEMS: int = 5

    MONGODB_CONNECTION_URL: str
    MONGO_DB: str = os.environ.get("MONGO_DB", "csmoney")

    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")

    TG_TOKEN: str

    PERCENTAGE_RATIO: float = 0.66  # бот отображает имена при поиске коллекций при совпадении как минимум на эту часть

    CELERY_BROKER_URL: str = "amqp://guest@localhost//"

    class Config:
        case_sensitive = True


settings = Settings()
