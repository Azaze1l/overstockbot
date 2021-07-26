import logging
import time
from typing import List
import json

import redis
from pymongo.errors import ServerSelectionTimeoutError

from app.celery_app.custom_tools.joke import get_random_joke
from app.celery_app.custom_tools.keyboards import get_confirm_notification_keyboard
from app.celery_app.services import (
    send_message,
    get_following_items,
    get_mongo_connection,
    update_data_in_collection,
)

from celery import Celery
from celery.schedules import crontab
from pymongo import MongoClient, WriteConcern, ReadPreference
from pymongo.read_concern import ReadConcern

from app.config import settings
import requests


logger = logging.getLogger("tasks")

celery_app = Celery("worker", broker=settings.CELERY_BROKER_URL)


@celery_app.task(bind=True)
def check_if_item_out_of_overstock_task(self, overstock_items_list):
    try:
        client, db = get_mongo_connection()
        logger.info("check_if_item_out_of_overstock_task: STARTED")
        redis_storage = redis.Redis(host=settings.REDIS_HOST, db=10)
        cursor = db.users.find({})
        users = list(cursor)
    except ServerSelectionTimeoutError as exc:
        raise self.retry(exc=exc)
    for user in users:
        user["_id"] = str(user["_id"])
        following_items = get_following_items(redis_storage, user["chat_id"])
        for item in following_items:
            if item["name"] not in [
                elem["market_hash_name"] for elem in overstock_items_list
            ]:
                logger.info(f"item {item} out of overstock for user {user['user_id']}")
                logger.info("check_if_item_out_of_overstock_task: FINISHED")
                send_notification_task.delay(user, item)
                return
    logger.info("check_if_item_out_of_overstock_task: all items in overstock")
    logger.info("check_if_item_out_of_overstock_task: FINISHED")


@celery_app.task
def send_notification_task(user, item):
    logger.info("send_notification_task: STARTED")
    redis_storage = redis.Redis(host=settings.REDIS_HOST, db=10)
    following_items = get_following_items(redis_storage, user["chat_id"])
    while item in following_items:
        msg_text = f"Вещь {item['name']} вышла из оверстока!!!! А это значит я расскажу тебе заебатый анекдотик\n\n"
        try:
            msg_text += get_random_joke()
        except FileNotFoundError:
            msg_text += "ФУНКЦИОНАЛ АНЕКДОТИКОВ ОТПАЛ))))"
        send_message(
            user["chat_id"],
            msg_text,
            reply_markup=get_confirm_notification_keyboard(item["id"]),
        )
        following_items = get_following_items(redis_storage, user["chat_id"])
        time.sleep(30)


@celery_app.task(bind=True)
def sync_overstock_data_task(self):
    try:
        client, db = get_mongo_connection()

        wc_majority = WriteConcern("majority", wtimeout=1000)
        logger.info("sync_overstock_data_task task: STARTED")
        url = f"{settings.OVERSTOCK_LIST_URL}"
        result = requests.get(url)
        if result.status_code == 200:
            items_list = result.json()
            logger.info(f"sync_overstock_data_task: {len(items_list)} items found")
            if len(items_list) > 0:
                check_if_item_out_of_overstock_task.delay(items_list)
                with client.start_session() as session:
                    session.with_transaction(
                        lambda s: update_data_in_collection(
                            s, data=items_list, collection_name="overstock_items"
                        ),
                        read_concern=ReadConcern("local"),
                        write_concern=wc_majority,
                        read_preference=ReadPreference.PRIMARY,
                    )
        else:
            logger.warning("sync_overstock_data_task: wrong request result")
        logger.info("sync_overstock_data_task: FINISHED")
    except ServerSelectionTimeoutError as exc:
        self.retry(exc=exc)


celery_app.conf.beat_schedule = {
    "sync_overstock_data_task": {
        "task": "app.celery_app.sync_overstock_data_task",
        "schedule": crontab(
            minute="*/1",
        ),
    },
}
