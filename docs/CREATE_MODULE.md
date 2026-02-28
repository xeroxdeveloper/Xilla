# Создание модулей для Xilla Userbot

Модули в Xilla базируются на классах и позволяют легко и интуитивно расширять функционал бота. Эта документация подробно описывает процесс их создания.

## Базовая структура модуля

Модуль — это класс, унаследованный от `loader.Module`, обязательно задекорированный `@loader.tds`.

```python
from hikkatl.tl.types import Message
from xilla import loader, utils

@loader.tds
class MyCustomMod(loader.Module):
    """Описание вашего модуля (отображается в .help)"""
    
    strings = {
        "name": "MyCustom",
        "response": "<b>☀️ Привет! Я работаю.</b>",
        "error": "<b>❌ Произошла ошибка.</b>"
    }

    async def client_ready(self):
        # Метод вызывается, когда клиент запущен и модуль полностью загружен.
        # Отличное место для инициализации переменных или подписки на события.
        self.my_var = True

    @loader.command()
    async def mycmd(self, message: Message):
        """- Описание команды"""
        # Отправляем ответ
        await utils.answer(message, self.strings("response"))
```

## Работа с аргументами и текстом

Xilla имеет встроенные утилиты для парсинга аргументов.

```python
    @loader.command()
    async def echo(self, message: Message):
        """<текст> - Повторить текст"""
        
        # Получает весь текст после команды (.echo привет мир -> "привет мир")
        args = utils.get_args_raw(message)
        
        if not args:
            return await utils.answer(message, "❌ Вы ничего не ввели!")
            
        await utils.answer(message, f"Вы сказали: {args}")
```

## Использование инлайн-кнопок (Inline)

В Xilla встроен мощный `inline_manager` для создания интерактивных форм без необходимости вникать в API Aiogram.

```python
    @loader.command()
    async def mymenu(self, message: Message):
        """- Открыть инлайн-меню"""
        
        # Форма - это интерактивное меню. Она заменяет сообщение, на которое вызвали команду, или отправляет новое.
        await self.inline.form(
            message=message,
            text="<b>☀️ Добро пожаловать в меню!</b>",
            reply_markup=[
                [{"text": "🚀 Кнопка 1", "callback": self._btn1_handler}],
                [{"text": "❌ Закрыть", "action": "close"}] # action="close" - это встроенное действие Xilla
            ]
        )

    async def _btn1_handler(self, call):
        # call - это InlineCall объект
        await call.answer("Вы нажали кнопку!", show_alert=True)
        await call.edit("<b>Текст изменился!</b>")
```

## Конфигурация модуля

Вы можете позволить пользователям настраивать ваш модуль через `.cfg`.

```python
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "my_setting",
                "Дефолтное значение",
                lambda: "Описание настройки",
                validator=loader.validators.String()
            )
        )
        
    @loader.command()
    async def checkcfg(self, message: Message):
        """- Проверить настройку"""
        val = self.config["my_setting"]
        await utils.answer(message, f"Значение настройки: {val}")
```

## Особенности Xilla
1. **Эмодзи:** Xilla использует тематику солнца (☀️) и светлые/синие тона. Старайтесь придерживаться этого стиля.
2. **utils.answer:** Всегда используйте `utils.answer(message, text)` вместо обычного `message.edit()`. Функция `utils.answer` сама понимает, можно ли отредактировать сообщение (если вы автор) или нужно отправить новое (если команду вызвал другой пользователь).
3. **Импорты:** Используйте `hikkatl` вместо `telethon`. Xilla работает на форке Telethon для большей стабильности.
