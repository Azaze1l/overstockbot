from typing import Optional, List

from pydantic import BaseModel, Field


class InlineKeyboardButton(BaseModel):
    text: str = Field(...)
    url: Optional[str] = Field(None)
    callback_data: Optional[str] = Field(None)


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: List[List[InlineKeyboardButton]] = Field(...)
