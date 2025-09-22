from typing import Any, Dict, Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field

from ..magic import F, MagicFilter
from ..types import Callback, VKEvent
from .filters import BaseFilter

T = TypeVar("T", bound="CallbackData")


class CallbackData(BaseModel):
    """
    Базовый класс для создания структурированных callback-данных.

    Использование:
    class MyCallback(CallbackData, prefix="my_prefix"):
        action: str
        item_id: int
    """

    prefix: str = Field(..., alias="@")

    def pack(self) -> str:
        """Упаковывает данные в JSON-строку для `payload` кнопки."""
        return self.model_dump_json(by_alias=True)

    @classmethod
    def unpack(cls: Type[T], payload: Dict[str, Any]) -> T:
        """Распаковывает словарь payload в объект CallbackData."""
        return cls.model_validate(payload)

    @classmethod
    def filter(cls, rule: Optional[MagicFilter] = None) -> "CallbackDataFilter":
        """
        Создает фильтр для данного типа CallbackData.

        :param rule: Дополнительное магическое правило для фильтрации.
        """
        base_rule = F.payload["@"] == cls.model_fields["prefix"].default
        if rule:
            final_rule = base_rule & rule
        else:
            final_rule = base_rule
        return CallbackDataFilter(callback_data_type=cls, rule=final_rule)


class CallbackDataFilter(BaseFilter):
    """
    Специальный фильтр, который проверяет и распаковывает CallbackData.
    """

    def __init__(self, callback_data_type: Type[CallbackData], rule: MagicFilter):
        self.callback_data_type = callback_data_type
        self.rule = rule

    async def check(self, event: VKEvent, **data: Any) -> Union[bool, Dict[str, Any]]:
        if not isinstance(event, Callback) or not isinstance(event.payload, dict):
            return False

        if not self.rule.resolve(event):
            return False

        try:
            callback_data_obj = self.callback_data_type.unpack(event.payload)
            return {"callback_data": callback_data_obj}
        except Exception:
            return False
