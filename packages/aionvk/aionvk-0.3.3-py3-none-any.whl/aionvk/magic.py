from typing import Any

from magic_filter import MagicFilter as _MagicFilter

from .bot.filters import BaseFilter
from .types import VKEvent


# 1. Это "чистая" магия. PyCharm будет счастлив, потому что тут нет
#    конфликтов наследования. Он видит, что F.payload == "..." возвращает MagicFilter.
class MagicFilter(_MagicFilter):
    pass


# 2. А это - наш "переводчик" с языка магии на язык нашего фреймворка.
class MagicFilterAdapter(BaseFilter):
    """
    Адаптер, который делает объект MagicFilter совместимым с системой фильтров aionvk.
    """
    def __init__(self, magic_filter: MagicFilter):
        self.magic_filter = magic_filter

    async def check(self, event: VKEvent, **data: Any) -> bool:
        # Просто вызываем магию, которую нам передали
        return self.magic_filter.resolve(event)


# F теперь - экземпляр "чистого" магического класса.
F = MagicFilter()