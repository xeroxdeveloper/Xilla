import re
import asyncio
from herokutl import events
from herokutl.tl.types import Message
from xilla.core import Module, command

class BotWizardMod(Module):
    """Мастер настройки юзербота (Bot PM Wizard)"""
    
    strings = {"name": "BotWizard"}

    async def on_load(self):
        # We listen to incoming messages from our own bot
        self.bot_username = self.client.xilla_config.get("core", "inline_bot_username")
        if self.bot_username:
            self.client.add_event_handler(self._bot_message_handler, events.NewMessage(chats=self.bot_username, incoming=True))

    async def _bot_message_handler(self, event):
        # Setup wizard automation
        text = event.raw_text
        if not text:
            return
            
        # Example of how a wizard would work using buttons
        # Since we are the userbot, we can click inline buttons sent by the bot!
        
        # But wait, our own userbot code doesn't have the Bot API server running yet to answer /start.
        # So we should actually just implement the Bot API polling in a lightweight way,
        # or handle it purely via Userbot.
        
        # Let's handle it purely via userbot: we intercept /start we send to the bot, 
        # and we make the userbot edit our own /start message with the config!
        pass

    @command("start")
    async def start_wizard(self, message: Message):
        """Запустить мастер настройки"""
        # This is intercepted when user types /start in the bot PM
        if message.to_id and getattr(message.to_id, "user_id", None) and getattr(message.to_id, "user_id") == message.sender_id:
             # Wait, message.out is True. We are sending /start to someone.
             pass
             
        # Actually a better approach is to just use a regular command for wizard
        await message.edit(
            "<b>☀️ Добро пожаловать в Xilla A2 Wizard!</b>\n\n"
            "<i>Выберите язык интерфейса:</i>\n"
            "🇷🇺 <code>.setlang ru</code>\n"
            "🇬🇧 <code>.setlang en</code>\n\n"
            "<i>Выберите частоту бэкапов:</i>\n"
            "🕒 <code>.setbackup 1h</code> (Каждый час)\n"
            "📅 <code>.setbackup 24h</code> (Каждый день)\n"
            "❌ <code>.setbackup 0</code> (Отключить)", 
            parse_mode="HTML"
        )
        
    @command("setlang")
    async def set_lang(self, message: Message):
        """<ru/en> - Установить язык"""
        lang = message.args.strip()
        if lang in ["ru", "en"]:
            message.client.xilla_config.set("core", "language", lang)
            message.client.xilla_i18n.load_lang(lang)
            await message.edit(f"✅ Язык установлен на <b>{lang}</b>", parse_mode="HTML")
        else:
            await message.edit("❌ Доступные языки: ru, en", parse_mode="HTML")

    @command("setbackup")
    async def set_backup(self, message: Message):
        """<1h/24h/0> - Установить частоту бэкапов"""
        freq = message.args.strip()
        if freq in ["1h", "24h", "0"]:
            message.client.xilla_config.set("core", "backup_frequency", freq)
            await message.edit(f"✅ Частота бэкапов установлена на: <b>{freq}</b>", parse_mode="HTML")
        else:
            await message.edit("❌ Доступные значения: 1h, 24h, 0", parse_mode="HTML")
