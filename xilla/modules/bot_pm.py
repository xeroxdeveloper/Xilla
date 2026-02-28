import re
import asyncio
import aiohttp
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
            # Listen to our outgoing messages to the bot to answer as the bot
            self.client.add_event_handler(self._bot_pm_outgoing, events.NewMessage(chats=self.bot_username, outgoing=True))

    async def _bot_message_handler(self, event):
        # Setup wizard automation
        text = event.raw_text
        if not text:
            return
        pass

    async def _bot_pm_outgoing(self, event):
        text = event.raw_text
        if text and text.strip().startswith("/start"):
            bot_token = self.client.xilla_config.get("core", "inline_bot_token")
            if not bot_token:
                return
            
            wizard_text = (
                "<b>☀️ Добро пожаловать в Xilla A2 Wizard!</b>\n\n"
                "<i>Выберите язык интерфейса:</i>\n"
                "🇷🇺 <code>.setlang ru</code>\n"
                "🇬🇧 <code>.setlang en</code>\n\n"
                "<i>Выберите частоту бэкапов:</i>\n"
                "🕒 <code>.setbackup 1h</code> (Каждый час)\n"
                "📅 <code>.setbackup 24h</code> (Каждый день)\n"
                "❌ <code>.setbackup 0</code> (Отключить)"
            )
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": event.sender_id,  # send it back to the userbot
                "text": wizard_text,
                "parse_mode": "HTML"
            }
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(url, json=payload)
            except Exception as e:
                pass

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
