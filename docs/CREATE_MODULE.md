# Создание модулей для Xilla Userbot

Модули в Xilla базируются на классах и позволяют легко и интуитивно расширять функционал бота. Эта документация описывает процесс их создания для версии **Alpaca B3**.

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
        # Отличное место для инициализации переменных.
        pass

    @loader.command()
    async def mycmd(self, message: Message):
        """- Описание команды"""
        await utils.answer(message, self.strings("response"))
```

## Работа с аргументами

Xilla имеет встроенные утилиты для парсинга аргументов из текста сообщения.

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

## Использование инлайн-меню (Inline Form)

В Xilla встроен мощный `inline_manager` для создания интерактивных форм.

```python
    @loader.command()
    async def mymenu(self, message: Message):
        """- Открыть меню"""
        
        await self.inline.form(
            message=message,
            text="<b>☀️ Добро пожаловать в меню!</b>",
            reply_markup=[
                [{"text": "🚀 Кнопка", "callback": self._btn_handler}],
                [{"text": "❌ Закрыть", "action": "close"}]
            ]
        )

    async def _btn_handler(self, call):
        await call.answer("Вы нажали кнопку!", show_alert=True)
        await call.edit("<b>Текст изменился!</b>")
```

## Генерация Pillow-баннеров (Новинка Alpaca B3)

Начиная с версии Alpaca B3, в ядре Xilla встроен мощный генератор градиентных баннеров для эстетичного ответа. Вы можете использовать его в своих модулях!

```python
    @loader.command()
    async def draw(self, message: Message):
        """- Нарисовать баннер"""
        
        try:
            # Импортируем системный генератор
            from .banners import create_banner
            
            # (Заголовок, Подзаголовок, Цвет1, Цвет2)
            banner = await create_banner("МОЙ МОДУЛЬ", "Это сгенерировано через Pillow", "#FF0099", "#493240")
            
            # Отправляем картинку с подписью
            await utils.answer_file(message, banner, "<b>☀️ Смотрите, какая красота!</b>")
        except Exception as e:
            await utils.answer(message, f"Ошибка: {e}")
```

## Конфигурация модуля

Позвольте пользователям настраивать ваш модуль через `.cfg`.

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
```

## Особенности Xilla
1. **Эмодзи:** Xilla использует тематику солнца (☀️) и светлые тона. 
2. **utils.answer:** Всегда используйте `utils.answer(message, text)` вместо обычного `message.edit()`. Функция `utils.answer` сама понимает, можно ли отредактировать сообщение (если вы автор) или нужно отправить новое (если команду вызвал другой пользователь).
3. **Импорты:** Используйте `hikkatl` вместо `telethon`.
4. **Упаковка:** Вы можете отправить свой `.py` файл другу прямо в чат и попросить его запаковать код через команду `.pack txt` с помощью модуля **XillaPack**.
