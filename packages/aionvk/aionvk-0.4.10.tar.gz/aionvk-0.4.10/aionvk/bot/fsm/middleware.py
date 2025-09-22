from typing import Any, Awaitable, Callable, Dict

from ...types import VKEvent
from ..middleware import BaseMiddleware
from .context import FSMContext
from .storage import BaseStorage


class FSMMiddleware(BaseMiddleware):
    """
    Встроенный middleware для поддержки FSM.
    Автоматически создает и внедряет FSMContext в каждый обработчик.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[VKEvent, Dict[str, Any]], Awaitable[Any]],
        event: VKEvent,
        data: Dict[str, Any],
    ) -> Any:
        bot = event.bot
        if not bot:
            raise RuntimeError(
                "Экземпляр Bot не был прикреплен к событию. "
                "Убедитесь, что Dispatcher.feed_raw_event получает аргумент 'bot'."
            )

        key = f"{event.user_id}:{event.peer_id}"

        context = FSMContext(storage=self.storage, _key=key, bot=bot)

        data["state"] = context
        return await handler(event, data)
