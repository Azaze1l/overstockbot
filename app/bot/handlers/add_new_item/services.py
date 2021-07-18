import logging
import re
from typing import Optional
from fuzzywuzzy import fuzz
from app.config import settings
from motor import motor_asyncio


async def _get_similar_words(actual_words: list, word: str):
    sorted_actual_words = []
    words = []
    for actual_word in actual_words:
        sorted_actual_words.append(fuzz.token_sort_ratio(actual_word, word.lower()))
    for i in range(len(sorted_actual_words)):
        if sorted_actual_words[i] > 70:
            words.append(actual_words[i])
    return words


async def _get_combinations_of_similar_words(words: list):
    try:
        combinations = words[0]
        for i in range(1, len(words)):
            for j in range(len(combinations)):
                combination = combinations.pop(j)
                for word in words[i]:
                    combinations = [combination + " " + word] + combinations
        return combinations
    except IndexError:
        return []


async def get_similar_overstock_item_names(
    item_name_from_msg: str, overstock_items_list: Optional[dict]
):
    """
    Функция возвращает список из имен коллекций, похожих на введенное.
    Если таковых нет, или введенное имя полностью совпадает с полным именем коллекции - возвращает пустой список
    """
    sorted_overstock_item_names = []
    actual_words = []
    words = []
    similar_overstock_items = []
    subscriptions_names = [
        elem.get("market_hash_name") for elem in overstock_items_list
    ]
    lower_subscription_name_from_msg = item_name_from_msg.lower()
    for subscription_name in [elem.lower() for elem in subscriptions_names]:
        sorted_overstock_item_names.append(
            fuzz.token_sort_ratio(lower_subscription_name_from_msg, subscription_name)
        )
        actual_words += re.split(" |-", subscription_name.replace(".", ""))
    actual_words = [word for word in set(actual_words)]

    if not subscriptions_names.count(
        item_name_from_msg
    ):  # если введенное пользователем имя совпадает с
        # названием коллекции, то бот не будет рекомендовать имена
        for word in item_name_from_msg.split(" "):
            similar_words = await _get_similar_words(actual_words, word)
            if len(similar_words) != 0:
                words.append(similar_words)  # список words заполняется похожими на
            # введенные словами из актуального списка подписок
        combinations_list = await _get_combinations_of_similar_words(
            words
        )  # составляются возможные комбинации из
        # актуальных слов; по самой удачной из них дальше отбирается рекомендованное имя
        for overstock_item in overstock_items_list:
            for combination in combinations_list:
                success = 0
                combination = combination.split(" ")
                for word in combination:
                    if (
                        overstock_item.get("market_hash_name").lower().find(word) != -1
                    ):  # если слово из комбинации
                        # встречается в актуальном имени подписки, то счетчик успеха повышается на единицу
                        success += 1
                    if (
                        float(success) >= len(combination) * settings.PERCENTAGE_RATIO
                    ):  # если успешных слов в
                        # комбинации больше ее определенной в PERCENT_RATIO части, определяется рекомедованное имя
                        if overstock_item.get("market_hash_name") not in [
                            item.get("name") for item in similar_overstock_items
                        ]:
                            similar_overstock_items.append(
                                {
                                    "name": overstock_item.get("market_hash_name"),
                                    "id": str(overstock_item.get("_id")),
                                }
                            )
    return similar_overstock_items


async def get_overstock_items_list_from_mongodb():
    mongo_client = motor_asyncio.AsyncIOMotorClient(settings.MONGODB_CONNECTION_URL)
    db = mongo_client[f"{settings.MONGO_DB}"]

    cursor = db.overstock_items.find({})
    overstock_items = await cursor.to_list(None)
    logging.info(overstock_items)
    return overstock_items
