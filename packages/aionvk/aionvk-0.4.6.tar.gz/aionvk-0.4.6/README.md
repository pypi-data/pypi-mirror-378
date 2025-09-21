# aionvk

<p align="center">
  <strong>Асинхронный, быстрый и удобный фреймворк для создания ботов ВКонтакте на Python.</strong>
</p>

<p align="center">
  <em>Создан с вдохновением от <a href="https://github.com/aiogram/aiogram">aiogram</a>.</em>
</p>

[![PyPI - Version](https://img.shields.io/pypi/v/aionvk)](https://pypi.org/project/aionvk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/aionvk.svg)](https://pypi.org/project/aionvk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

**aionvk** — это современный фреймворк, который делает разработку ботов для VK простой и приятной. Он использует лучшие практики асинхронного программирования и строгую типизацию на основе `pydantic`, чтобы ваш код был надежным, читаемым и легко масштабируемым.

## 🚀 Ключевые особенности

*   **Полностью асинхронный**: Построен на `asyncio` и `httpx` для максимальной производительности.
*   **Модульная архитектура**: Используйте `Router` для разделения логики вашего бота на множество файлов и модулей.
*   **Мощная фильтрация**: Интуитивно понятные фильтры, включая "магические" F-объекты для лаконичных и выразительных проверок.
*   **Машина состояний (FSM)**: Встроенная поддержка FSM для создания сложных диалоговых сценариев с поддержкой различных хранилищ (in-memory, Redis).
*   **Типобезопасность**: Pydantic-модели для всех объектов VK API, что обеспечивает валидацию данных и отличный автокомплит в IDE.
*   **Удобные конструкторы**: `KeyboardBuilder` и `Paginator` для легкого создания inline и reply-клавиатур любой сложности.
*   **Фабрика Callback-данных**: Создавайте структурированные и безопасные данные для кнопок без головной боли с парсингом строк.

## 📦 Установка

```bash
pip install aionvk
```

Для использования FSM с хранилищем Redis:
```bash
pip install aionvk[redis]
```

##  quickstart.py: Быстрый старт

Этот пример демонстрирует базовые возможности: запуск бота, обработку команды `/start` и нажатие на inline-кнопку.

```python
import asyncio
import os

from aionvk import Bot, Button, Dispatcher, F, KeyboardBuilder, Router
from aionvk.bot import CommandFilter
from aionvk.types import Callback, Message

# Используйте переменные окружения для токена
API_TOKEN = os.getenv("VK_BOT_TOKEN", "your_vk_token_here")

# --- Основные объекты ---
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)


# --- Хендлеры ---
@router.message(CommandFilter("start"))
async def command_start_handler(event: Message):
    """
    Этот хендлер будет вызван на команду /start
    """
    kb = KeyboardBuilder(inline=True)
    kb.add(Button.callback("Нажми меня!", payload={"command": "button_press"}))
    
    await event.answer(
        "Привет! Я простой бот на фреймворке aionvk.",
        keyboard=kb.build()
    )


@router.callback(F.payload["command"] == "button_press")
async def button_press_handler(event: Callback):
    """
    Этот хендлер ловит нажатие на inline-кнопку
    """
    # Отвечаем на колбэк, чтобы убрать "часики" у кнопки
    await event.answer()
    # Отправляем новое сообщение
    await bot.send_message(
        peer_id=event.peer_id,
        text="Ты нажал на кнопку!"
    )


async def main():
    """Функция для запуска long polling."""
    # Здесь должен быть ваш код для получения событий, например, через aiohttp webhook
    # или через цикл long polling. Для примера, мы просто выведем сообщение.
    print("Бот запущен... (этот пример не включает long polling)")
    # В реальном приложении здесь будет запуск веб-сервера или long polling цикл.


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
```

## 🧠 Продвинутые примеры

### Управление состояниями (FSM)

`aionvk` имеет встроенную машину состояний для ведения диалогов.

```python
from aionvk.bot import FSMContext, State, StatesGroup
from aionvk.bot.fsm import RedisStorage  # Рекомендуется для продакшена
import redis.asyncio as redis

# 1. Определяем состояния
class Form(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()

# 2. Настраиваем хранилище (в main-файле)
# storage = RedisStorage(redis.Redis(host='localhost', port=6379))
# dp.setup_fsm(storage)

# 3. Пишем хендлеры для каждого шага
@router.message(CommandFilter("form"))
async def start_form(event: Message, state: FSMContext):
    await state.set_state(Form.waiting_for_name)
    await event.answer("Как тебя зовут?")

@router.message(F.text, state=Form.waiting_for_name)
async def process_name(event: Message, state: FSMContext):
    await state.update_data(name=event.text)
    await state.set_state(Form.waiting_for_age)
    await event.answer("Сколько тебе лет?")

@router.message(F.text.isdigit(), state=Form.waiting_for_age)
async def process_age(event: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get("name")
    age = event.text
    
    await event.answer(f"Приятно познакомиться, {name}! Тебе {age} лет.")
    
    # Завершаем диалог
    await state.clear()
```

### Inline-клавиатуры с `CallbackData`

Забудьте о ручном парсинге JSON в `payload`. Используйте `CallbackData` для создания типизированных и безопасных данных.

```python
from aionvk.bot.callback_data import CallbackData

# 1. Определяем "схему" данных
class ItemCallback(CallbackData, prefix="item"):
    action: str  # 'view' или 'delete'
    item_id: int

# 2. Создаем клавиатуру
def get_item_keyboard(item_id: int) -> str:
    builder = KeyboardBuilder(inline=True)
    builder.add(
        Button.callback("Посмотреть", payload=ItemCallback(action="view", item_id=item_id).pack()),
        Button.callback("Удалить", payload=ItemCallback(action="delete", item_id=item_id).pack())
    )
    return builder.build()

# 3. Создаем хендлеры с фильтрами
@router.callback(ItemCallback.filter(F.payload.action == "view"))
async def view_item_handler(event: Callback, callback_data: ItemCallback):
    # callback_data - это уже объект ItemCallback, а не словарь!
    await event.answer(show_snackbar=f"Просмотр товара #{callback_data.item_id}")

@router.callback(ItemCallback.filter(F.payload.action == "delete"))
async def delete_item_handler(event: Callback, callback_data: ItemCallback):
    await event.answer(show_snackbar=f"Удаление товара #{callback_data.item_id}")
    await event.edit_text("Товар удален.")
```

### Магические фильтры

Пишите сложные фильтры лаконично и читаемо с помощью `F`-объектов.

```python
from aionvk import F

# Сработает на сообщение, где есть вложение типа "фото"
@router.message(F.attachments[0].type == "photo")
async def photo_handler(event: Message):
    await event.answer("Я вижу фото!")

# Сработает, если текст "привет" и пользователь из России
@router.message(
    (F.text.lower() == "привет") &
    (F.client_info.lang_id.is_in([0, 100]))  # 0 - RU, 100 - RU (новые клиенты)
)
async def russian_hello_handler(event: Message):
    await event.answer("Привет, соотечественник!")
```

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.