# aionvk/bot/router.py

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from .filters import (
    AndFilter,
    BaseFilter,
    CommandFilter,
    PayloadFilter,
    StateFilter,
    TextFilter,
)

# Импортируем наши магические классы
from ..magic import MagicFilter, MagicFilterAdapter


@dataclass
class Handler:
    callback: Callable[..., Any]
    filters: List[BaseFilter] = field(default_factory=list)


class Router:
    def __init__(self):
        self.handlers: List[Handler] = []

    def _prepare_and_wrap_filters(
        self, custom_filters: tuple, kwargs: Dict[str, Any]
    ) -> BaseFilter:
        """
        Собирает все фильтры в один финальный AndFilter.
        Автоматически оборачивает MagicFilter в адаптер, чтобы наша система его понимала.
        """
        filters = []
        # Сначала обрабатываем позиционные фильтры (*args)
        for f in custom_filters:
            if isinstance(f, MagicFilter):
                filters.append(MagicFilterAdapter(f))
            elif isinstance(f, BaseFilter):
                filters.append(f)
            else:
                # Если передали что-то непонятное - кидаем ошибку, чтобы сразу было ясно, в чем дело
                raise TypeError(
                    f"Недопустимый тип фильтра: {type(f)}. Ожидался BaseFilter или MagicFilter."
                )

        # Теперь обрабатываем именованные фильтры (**kwargs)
        if (text := kwargs.pop("text", None)) is not None:
            filters.append(
                TextFilter(text, ignore_case=kwargs.pop("ignore_case", True))
            )
        if (command := kwargs.pop("command", None)) is not None:
            filters.append(CommandFilter(command, prefix=kwargs.pop("prefix", "/")))
        if (state := kwargs.pop("state", None)) is not None:
            filters.append(StateFilter(state))
        if (payload := kwargs.pop("payload", None)) is not None:
            filters.append(PayloadFilter(payload))

        if kwargs:
            raise TypeError(
                f"Неизвестные аргументы-фильтры: {', '.join(kwargs.keys())}"
            )

        # Если фильтров вообще нет, возвращаем "пустышку", которая всегда проходит
        if not filters:

            class _PassFilter(BaseFilter):
                async def check(self, event: Any, **data: Any) -> bool:
                    return True

            return _PassFilter()

        # Если фильтр один, возвращаем его. Если несколько - оборачиваем в AndFilter.
        if len(filters) == 1:
            return filters[0]
        return AndFilter(*filters)

    def message(self, *custom_filters: Any, **kwargs: Any) -> Callable:
        """
        Декоратор для регистрации обработчика сообщений.
        Принимает любые фильтры.
        """
        final_filter = self._prepare_and_wrap_filters(custom_filters, kwargs)

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            handler = Handler(callback=callback, filters=[final_filter])
            self.handlers.append(handler)
            return callback

        return decorator

    def callback(self, *custom_filters: Any, **kwargs: Any) -> Callable:
        """
        Декоратор для регистрации обработчика callback-событий.
        Принимает любые фильтры.
        """
        final_filter = self._prepare_and_wrap_filters(custom_filters, kwargs)

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            handler = Handler(callback=callback, filters=[final_filter])
            self.handlers.append(handler)
            return callback

        return decorator

    def include_router(self, router: "Router") -> None:
        self.handlers.extend(router.handlers)
