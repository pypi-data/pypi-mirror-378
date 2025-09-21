import logging
from functools import partial
from typing import Any, Callable, Dict, Optional, List

from pydantic import ValidationError

from . import FSMContext
from .. import Bot
from ..types import Callback, Message, VKEvent
from .fsm import BaseStorage, FSMMiddleware
from .middleware import BaseMiddleware
from .router import Router

logger = logging.getLogger(__name__)


class Dispatcher:
    """
    Основной класс, управляющий роутингом, middlewares и обработкой событий.
    """

    def __init__(self, bot: Bot, storage: Optional[BaseStorage] = None):
        self.bot = bot
        self.storage = storage
        self.router = Router()
        self.middlewares: List[BaseMiddleware] = []

        if self.storage:
            self.setup_fsm(self.storage)

    def setup_fsm(self, storage: BaseStorage) -> None:
        """Настраивает FSM, регистрируя middleware."""
        self.storage = storage
        self.register_middleware(FSMMiddleware(storage))

    def register_middleware(self, middleware: BaseMiddleware) -> None:
        """Регистрирует middleware."""
        self.middlewares.append(middleware)

    def include_router(self, router: Router) -> None:
        """Включает роутер в диспетчер."""
        self.router.include_router(router)

    def get_fsm_context(self, user_id: int, peer_id: int) -> FSMContext:
        """
        Создает и возвращает экземпляр FSMContext для конкретного пользователя.

        Это позволяет управлять состоянием пользователя вне потока обработки событий
        (например, в фоновых задачах или админ-панели).

        :param user_id: ID пользователя.
        :param peer_id: ID диалога (часто совпадает с user_id для ЛС).
        :return: Экземпляр FSMContext.
        """
        if not self.storage:
            raise RuntimeError(
                "Невозможно получить FSM context, так как хранилище не настроено. "
                "Передайте storage в конструктор Dispatcher или используйте dispatcher.setup_fsm(storage)."
            )

        # Ключ должен генерироваться по той же стратегии, что и в FSMMiddleware
        key = f"fsm:{user_id}:{peer_id}"

        return FSMContext(storage=self.storage, key=key, bot=self.bot)

    async def _call_handler(
        self, callback: Callable[..., Any], event: VKEvent, **data: Any
    ) -> None:
        # Добавляем бота и диспетчер в данные, доступные для хендлера
        data["bot"] = self.bot
        data["dispatcher"] = self
        await callback(event, **data)

    async def _trigger_event(self, event: VKEvent, data: Dict[str, Any]) -> None:
        """Ищет и вызывает подходящий обработчик для события."""
        # Устанавливаем ссылку на бота в событие для shortcut-методов (event.answer и т.д.)
        event.bot = self.bot

        for handler in self.router.handlers:
            if not handler.filters:
                await self._call_handler(handler.callback, event, **data)
                return

            filter_result = await handler.filters[0].check(event, **data)
            if filter_result:
                handler_data = data.copy()
                if isinstance(filter_result, dict):
                    handler_data.update(filter_result)

                await self._call_handler(handler.callback, event, **handler_data)
                return

    async def feed_raw_event(self, event_data: Dict[str, Any], **kwargs: Any) -> None:
        """
        Точка входа. Принимает сырое событие от VK, парсит его
        и запускает цепочку обработки.
        """
        event_type = event_data.get("type")
        event_obj: VKEvent

        try:
            if event_type == "message_new":
                event_obj = Message.model_validate(event_data["object"])
            elif event_type == "message_event":
                event_obj = Callback.model_validate(event_data["object"])
            else:
                logger.debug("Ignored unknown event type: %s", event_type)
                return
        except ValidationError as e:
            logger.warning(
                "Failed to validate VK event. Type: %s, Error: %s, Data: %s",
                event_type,
                e,
                event_data,
            )
            return
        except Exception as e:
            logger.error(
                "An unexpected error occurred during event parsing. Type: %s, Error: %s",
                event_type,
                e,
                exc_info=True,
            )
            return

        event_obj.bot = kwargs.get("bot")

        handler_to_call = self._trigger_event

        for middleware in reversed(self.middlewares):
            handler_to_call = partial(middleware, handler_to_call)

        context_data = kwargs.copy()

        try:
            await handler_to_call(event=event_obj, data=context_data)
        except Exception as e:
            logger.exception("Exception raised during event processing: %s", e)
