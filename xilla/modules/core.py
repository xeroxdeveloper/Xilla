from xilla.core import Module, command
from herokutl.tl.types import Message

class CoreMod(Module):
    """Основные утилиты юзербота Xilla"""
    
    @command("ping")
    async def ping_cmd(self, message: Message):
        """Проверка работоспособности"""
        await message.edit("<b>☀️ Xilla (Anti 1) работает отлично!</b>", parse_mode="HTML")

    @command("help")
    async def help_cmd(self, message: Message):
        """Справка по командам"""
        await message.edit("<b>☀️ Справка Xilla</b>\n\nВ разработке...", parse_mode="HTML")
