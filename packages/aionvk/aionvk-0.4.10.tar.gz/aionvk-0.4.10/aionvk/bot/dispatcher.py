import inspect
import logging
from functools import partial
from typing import Any, Callable, Dict

from pydantic import ValidationError


from ..types import Callback, Message, VKEvent
from .fsm import BaseStorage, FSMMiddleware
from .middleware import BaseMiddleware
from .router import Router

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self):
        self.router = Router()
        self.middlewares: list[BaseMiddleware] = []
        self.fsm: FSMMiddleware | None = None
        self.bot: Any = None

    def include_router(self, router: Router):
        self.router.handlers.extend(router.handlers)
        router.bot = self.bot

    def register_middleware(self, middleware: BaseMiddleware):
        self.middlewares.append(middleware)

    def setup_fsm(self, storage: BaseStorage):
        self.fsm = FSMMiddleware(storage)
        self.middlewares.insert(0, self.fsm)

    def get_fsm_context(self, user_id: int, peer_id: int):
        from . import FSMContext
        if not self.fsm:
            raise RuntimeError(
                "FSM не настроен. Вызовите dispatcher.setup_fsm(storage)."
            )
        key = f"{user_id}:{peer_id}"
        return FSMContext(storage=self.fsm.storage, _key=key, bot=self.bot)

    async def _trigger_event(self, event: VKEvent, data: Dict[str, Any]) -> None:
        for handler in self.router.handlers:
            check_result = True
            if handler.filters:
                check_result = await handler.filters[0].check(event, **data)

            if not check_result:
                continue

            handler_data = data.copy()
            if isinstance(check_result, dict):
                handler_data.update(check_result)

            await self._call_handler(handler.callback, event, **handler_data)
            return

    @staticmethod
    async def _call_handler(callback: Callable[..., Any], event: VKEvent, **data: Any):
        signature = inspect.signature(callback).parameters
        args_to_pass: Dict[str, Any] = {}

        first_param_name = next(iter(signature.keys()))

        available_deps = data.copy()
        available_deps[first_param_name] = event

        for param_name, param in signature.items():
            if param_name in available_deps:
                args_to_pass[param_name] = available_deps[param_name]
                continue

            if param.annotation is not inspect.Parameter.empty:
                for dep_value in available_deps.values():
                    if isinstance(dep_value, param.annotation):
                        args_to_pass[param_name] = dep_value
                        break

        await callback(**args_to_pass)

    async def feed_raw_event(self, event_data: Dict[str, Any], **kwargs: Any) -> None:
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
            logger.warning("Failed to validate VK event: %s, Data: %s", e, event_data)
            return
        except Exception as e:
            logger.error("Unexpected error during event parsing: %s", e, exc_info=True)
            return

        self.bot = kwargs.get("bot")
        event_obj.bot = self.bot
        event_obj.dispatcher = self

        handler_to_call = self._trigger_event
        for middleware in reversed(self.middlewares):
            handler_to_call = partial(middleware, handler_to_call)

        context_data = kwargs.copy()

        try:
            await handler_to_call(event=event_obj, data=context_data)
        except Exception as e:
            logger.exception("Exception raised during event processing: %s", e)
