from typing import Any

from magic_filter import MagicFilter as _MagicFilter

from .bot.filters import BaseFilter
from .types import VKEvent


class MagicFilter(BaseFilter, _MagicFilter):
    """
    Магический фильтр для гибкой фильтрации событий VK.
    Основан на библиотеке magic-filter, адаптирован для aionvk.
    """

    async def check(self, event: VKEvent, **data: Any) -> bool:
        return self.resolve(event)


F = MagicFilter()
