from typing import Any, Union, Dict

from magic_filter import MagicFilter as _MagicFilter

from .bot.filters import BaseFilter
from .types import VKEvent


class MagicFilter(_MagicFilter):
    def __and__(self, other: Any) -> "MagicFilter":
        return super().__and__(other)

    def __or__(self, other: Any) -> "MagicFilter":
        return super().__or__(other)


class MagicFilterAdapter(BaseFilter):
    """
    Адаптер, который делает объект MagicFilter совместимым с системой фильтров aionvk.
    """

    def __init__(self, magic_filter: MagicFilter):
        self.magic_filter = magic_filter

    async def check(self, event: VKEvent, **data: Any) -> Union[bool, Dict[str, Any]]:
        # Просто вызываем магию, которую нам передали
        return self.magic_filter.resolve(event)


F = MagicFilter()