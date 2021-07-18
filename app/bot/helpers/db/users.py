import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.celery_app import logger

collection = "users"


class Users:
    @staticmethod
    async def get_user_by_id(db: AsyncIOMotorDatabase, id: str):
        try:
            user = await db[collection].find_one({"_id": ObjectId(id)})
        except PyMongoError as ex:
            logger.error(f"get_user_by_id failed: {ex}")
            return None
        return user

    @staticmethod
    async def register_bot_user(db: AsyncIOMotorDatabase, chat_id: int):
        data = {
            "user_id": chat_id,
            "chat_id": chat_id,
            "registered_at": datetime.datetime.now(datetime.timezone.utc),
        }
        try:
            result = await db[collection].insert_one(data)
            logger.info(f"User {chat_id} was successfully registered")
        except PyMongoError as ex:
            logger.error(f"register_bot_user failed: {ex}")
            return None
        return result.inserted_id

    @staticmethod
    async def get_or_create_new_user(db: AsyncIOMotorDatabase, chat_id: int):
        user = await Users.get_user(db, chat_id=chat_id)
        if not user:
            new_id = await Users.register_bot_user(db, chat_id)
            user = await Users.get_user_by_id(db, id=new_id)
        return user

    @staticmethod
    async def get_user(db: AsyncIOMotorDatabase, chat_id: int):
        try:
            user = await db[collection].find_one(
                {
                    "user_id": chat_id,
                    "chat_id": chat_id,
                }
            )
        except PyMongoError as ex:
            logger.error(f"get_user failed: {ex}")
            return None
        return user
