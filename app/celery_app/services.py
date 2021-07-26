import json
from typing import List
from pymongo.client_session import ClientSession
import requests

import redis
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from app.config import settings
from app.main import storage

TG_BASE_URL = f"https://api.telegram.org/bot{settings.TG_TOKEN}/"


def get_following_items(db: redis.Redis, chat_id: int):
    key = storage.generate_key(chat_id, chat_id, "data")
    data = db.get(key)
    if data is not None:
        data = json.loads(data)
        following_items = data.get("following_items")
        if following_items:
            return following_items
        else:
            return []


def send_message(chat_id, text, reply_markup=None):
    url = TG_BASE_URL + "sendMessage"
    if reply_markup is not None:
        data = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup.dict(exclude_none=True),
        }
    else:
        data = {
            "chat_id": chat_id,
            "text": text,
        }
    result = requests.post(url, json=data)


def get_mongo_connection():

    client = MongoClient(
        settings.MONGODB_CONNECTION_URL,
        serverSelectionTimeoutMS=10,
    )
    return client, client[settings.MONGO_DB]


def update_data_in_collection(
    session: ClientSession, data: List[dict], collection_name: str
):
    data_collection = session.client[settings.MONGO_DB][collection_name]
    data_collection.delete_many({}, session=session)
    data_collection.insert_many(data, session=session)
