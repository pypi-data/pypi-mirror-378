from typing import Any
from magic_filter import MagicFilter as _MagicFilter
from .bot.filters import BaseFilter
from .types import VKEvent


class MagicFilter(_MagicFilter):
    pass


class MagicFilterAdapter(BaseFilter):
    def __init__(self, magic_filter: MagicFilter):
        self.magic_filter = magic_filter

    async def check(self, event: VKEvent, **data: Any) -> bool:
        return self.magic_filter.resolve(event)


F = MagicFilter()
