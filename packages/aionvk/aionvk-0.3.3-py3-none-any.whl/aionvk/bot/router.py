from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union, Optional

from .filters import (
    AndFilter,
    BaseFilter,
    CommandFilter,
    PayloadFilter,
    StateFilter,
    TextFilter,
)
# Импортируем наши новые классы
from ..magic import MagicFilter, MagicFilterAdapter


@dataclass
class Handler:
    callback: Callable[..., Any]
    filters: List[BaseFilter] = field(default_factory=list)


class Router:
    def __init__(self):
        self.handlers: List[Handler] = []

    def _prepare_filters(self, custom_filters: tuple, **kwargs: Any) -> List[BaseFilter]:
        # Эта функция будет преобразовывать все фильтры в нужный нам формат
        filters = []
        for f in custom_filters:
            if isinstance(f, MagicFilter):
                filters.append(MagicFilterAdapter(f))
            elif isinstance(f, BaseFilter):
                filters.append(f)
            # Можно добавить обработку других типов, если нужно

        # ... твой код для text, command, state ...
        if (text := kwargs.pop("text", None)) is not None:
            filters.append(TextFilter(text, ignore_case=kwargs.pop("ignore_case", True)))
        if (command := kwargs.pop("command", None)) is not None:
            filters.append(CommandFilter(command, prefix=kwargs.pop("prefix", "/")))
        if (state := kwargs.pop("state", None)) is not None:
            filters.append(StateFilter(state))
        if (payload := kwargs.pop("payload", None)) is not None:
            filters.append(PayloadFilter(payload))

        return filters

    def message(
            self,
            *custom_filters: Any,  # Принимаем Any, чтобы не ругался на F
            **kwargs: Any,
    ) -> Callable:
        # Убираем типизацию из аргументов и делаем ее внутри
        filters = self._prepare_filters(custom_filters, **kwargs)

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            # Если фильтров несколько, объединяем их через "И"
            final_filter = AndFilter(*filters) if filters else None
            handler = Handler(callback=callback, filters=[final_filter] if final_filter else [])
            self.handlers.append(handler)
            return callback

        return decorator

    def callback(
            self,
            *custom_filters: Any,  # Принимаем Any
            **kwargs: Any,
    ) -> Callable:
        filters = self._prepare_filters(custom_filters, **kwargs)

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            final_filter = AndFilter(*filters) if filters else None
            handler = Handler(callback=callback, filters=[final_filter] if final_filter else [])
            self.handlers.append(handler)
            return callback

        return decorator

    def include_router(self, router: "Router") -> None:
        """
        Включает все обработчики из другого роутера в текущий.

        :param router: Экземпляр Router, который нужно подключить.
        """
        self.handlers.extend(router.handlers)
