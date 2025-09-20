from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .filters import (
    AndFilter,
    BaseFilter,
    CommandFilter,
    PayloadFilter,
    StateFilter,
    TextFilter,
)
from ..magic import MagicFilter, MagicFilterAdapter


@dataclass
class Handler:
    callback: Callable[..., Any]
    filters: List[BaseFilter] = field(default_factory=list)


class Router:
    def __init__(self):
        self.handlers: List[Handler] = []

    def _prepare_filters(
            self, custom_filters: tuple, kwargs: Dict[str, Any]
    ) -> List[BaseFilter]:
        filters = []
        for f in custom_filters:
            if isinstance(f, MagicFilter):
                filters.append(MagicFilterAdapter(f))
            elif isinstance(f, BaseFilter):
                filters.append(f)
            else:
                raise TypeError(f"Фильтр имеет неверный тип: {type(f)}")

        if (text := kwargs.pop("text", None)) is not None:
            filters.append(TextFilter(text, ignore_case=kwargs.pop("ignore_case", True)))
        if (command := kwargs.pop("command", None)) is not None:
            filters.append(CommandFilter(command, prefix=kwargs.pop("prefix", "/")))
        if (state := kwargs.pop("state", None)) is not None:
            filters.append(StateFilter(state))
        if (payload := kwargs.pop("payload", None)) is not None:
            filters.append(PayloadFilter(payload))

        if kwargs:
            raise TypeError(f"Неизвестные аргументы-фильтры: {', '.join(kwargs.keys())}")

        return filters

    def message(self, *custom_filters: Any, **kwargs: Any) -> Callable:
        filters = self._prepare_filters(custom_filters, kwargs)

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            final_filter = AndFilter(*filters) if len(filters) > 1 else (filters[0] if filters else None)
            handler = Handler(callback=callback, filters=[final_filter] if final_filter else [])
            self.handlers.append(handler)
            return callback

        return decorator

    def callback(self, *custom_filters: Any, **kwargs: Any) -> Callable:
        filters = self._prepare_filters(custom_filters, kwargs)

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            final_filter = AndFilter(*filters) if len(filters) > 1 else (filters[0] if filters else None)
            handler = Handler(callback=callback, filters=[final_filter] if final_filter else [])
            self.handlers.append(handler)
            return callback

        return decorator

    def include_router(self, router: "Router") -> None:
        self.handlers.extend(router.handlers)
