# Создание модулей для Xilla Userbot

Модули в Xilla базируются на классах и позволяют легко расширять функционал бота.

## Базовая структура

Вот пример самого простого модуля, который отвечает на команду:

```python
from hikkatl.tl.types import Message
from xilla import loader, utils

@loader.tds
class MyCustomMod(loader.Module):
    """Описание вашего модуля"""
    
    strings = {
        "name": "MyCustom",
        "response": "<b>☀️ Привет! Я работаю.</b>"
    }

    async def client_ready(self):
        # Вызывается при запуске бота
        pass

    @loader.command()
    async def mycmd(self, message: Message):
        """- Описание команды"""
        # Отправляем ответ
        await utils.answer(message, self.strings("response"))
```

## Работа с аргументами

Для получения текста после команды:

```python
    @loader.command()
    async def say(self, message: Message):
        """<текст> - Сказать что-то"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Нет текста!")
            
        await utils.answer(message, f"Вы сказали: {args}")
```

## Особенности
1. **Эмодзи:** Xilla использует тематику солнца (☀️).
2. **utils.answer:** Всегда используйте `utils.answer(message, text)` вместо обычного редактирования, так как функция сама понимает, нужно ли отредактировать сообщение или отправить новое (если бот вызван кем-то другим).
3. **Импорты:** Используйте `hikkatl` вместо `telethon` для максимальной совместимости.
