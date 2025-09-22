import abc
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from ..types import Message, VKEvent


@dataclass(frozen=True)
class CommandObject:
    """
    Объект, содержащий распарсенную команду и ее аргументы.
    """

    prefix: str
    command: str
    args: Optional[str]


class BaseFilter(abc.ABC):
    @abc.abstractmethod
    async def check(self, event: VKEvent, **data: Any) -> Union[bool, Dict[str, Any]]:
        raise NotImplementedError

    def __and__(self, other: Any) -> "AndFilter":
        return AndFilter(self, other)

    def __or__(self, other: Any) -> "OrFilter":
        return OrFilter(self, other)


class AndFilter(BaseFilter):
    def __init__(self, *filters: Any):
        from ..magic import MagicFilter, MagicFilterAdapter

        self.filters = []
        for f in filters:
            if isinstance(f, BaseFilter):
                self.filters.append(f)
            elif isinstance(f, MagicFilter):
                self.filters.append(MagicFilterAdapter(f))

    async def check(self, event: VKEvent, **data: Any) -> Union[bool, Dict[str, Any]]:
        handler_data = {}
        for f in self.filters:
            result = await f.check(event, **data)
            if not result:
                return False
            if isinstance(result, dict):
                handler_data.update(result)
        return handler_data or True


class OrFilter(BaseFilter):
    def __init__(self, *filters: Any):
        from ..magic import MagicFilter, MagicFilterAdapter

        self.filters = []
        for f in filters:
            if isinstance(f, BaseFilter):
                self.filters.append(f)
            elif isinstance(f, MagicFilter):
                self.filters.append(MagicFilterAdapter(f))

    async def check(self, event: VKEvent, **data: Any) -> Union[bool, Dict[str, Any]]:
        for f in self.filters:
            result = await f.check(event, **data)
            if result:
                return result
        return False


class TextFilter(BaseFilter):
    def __init__(self, text: Union[str, List[str]], ignore_case: bool = True):
        self.texts = [text] if isinstance(text, str) else text
        self.ignore_case = ignore_case

    async def check(self, event: VKEvent, **data: Any) -> bool:
        if not isinstance(event, Message) or not event.text:
            return False
        text_to_check = event.text.lower() if self.ignore_case else event.text
        texts_to_find = (
            [t.lower() for t in self.texts] if self.ignore_case else self.texts
        )
        return text_to_check in texts_to_find


class CommandFilter(BaseFilter):
    def __init__(self, commands: Union[str, List[str]], prefix: str = "/"):
        cmds = [commands] if isinstance(commands, str) else commands
        self.commands = [cmd.lower() for cmd in cmds]
        self.prefix = prefix

    async def check(self, event: VKEvent, **data: Any) -> Union[bool, Dict[str, Any]]:
        if not isinstance(event, Message) or not event.text:
            return False
        text = event.text.strip()
        if not text.startswith(self.prefix):
            return False
        command_part, *args_part = text.split(maxsplit=1)
        command = command_part[len(self.prefix) :].lower()
        args = args_part[0] if args_part else None
        if command in self.commands:
            return {
                "command": CommandObject(prefix=self.prefix, command=command, args=args)
            }
        return False


class StateFilter(BaseFilter):
    def __init__(self, state: Any):
        self.target_state = state.state if hasattr(state, "state") else state

    async def check(self, event: VKEvent, **data: Any) -> bool:
        from .fsm.context import FSMContext

        fsm_context: FSMContext = data.get("state")
        if not fsm_context:
            return self.target_state is None
        current_state = await fsm_context.get_state()
        if self.target_state == "*":
            return current_state is not None
        return current_state == self.target_state


class PayloadFilter(BaseFilter):
    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    async def check(self, event: VKEvent, **data: Any) -> bool:
        if not event.payload:
            return False
        return self.payload.items() <= event.payload.items()


class LambdaFilter(BaseFilter):
    def __init__(self, func: Callable[[VKEvent, Dict[str, Any]], Awaitable[bool]]):
        self.func = func

    async def check(self, event: VKEvent, **data: Any) -> bool:
        return await self.func(event, **data)
