import os
import aiohttp
import tempfile
import json
from xilla.core import Module, command
from herokutl.tl.types import Message

class InstallerMod(Module):
    """Модуль для скачивания плагинов и установки"""

    def __init__(self):
        super().__init__()
        self.pending_installs = {}

    @command("install")
    async def install_cmd(self, message: Message):
        """<ссылка/реплай> - Скачать и установить модуль"""
        reply = await message.get_reply_message()
        url = message.args.strip()
        
        if not url and not (reply and reply.media):
            return await message.edit("❌ Укажите ссылку на .py файл (GitHub/GitLab) или сделайте реплай на файл.")
            
        await message.edit("⏳ Подготовка к установке...")
        
        install_mode = message.client.xilla_config.get("installer", "mode")
        code = ""
        filename = ""
        
        try:
            if reply and reply.media:
                filename = getattr(reply.file, "name", "plugin.py")
                if not filename.endswith(".py"):
                    filename += ".py"
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, filename)
                    await message.client.download_media(reply, file=path)
                    with open(path, "r", encoding="utf-8") as f:
                        code = f.read()
            else:
                if "github.com" in url and "/blob/" in url:
                    url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                    
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            code = await resp.text()
                            filename = url.split("/")[-1]
                            if not filename.endswith(".py"): 
                                filename += ".py"
                        else:
                            return await message.edit(f"❌ Ошибка скачивания: HTTP {resp.status}", parse_mode="HTML")
        except Exception as e:
            return await message.edit(f"❌ Системная ошибка загрузки: {e}", parse_mode="HTML")

        if install_mode == "always_disk":
            await self._save_and_load(message, filename, code, save_to_disk=True)
        elif install_mode == "always_memory":
            await self._save_and_load(message, filename, code, save_to_disk=False)
        else:
            bot_token = message.client.xilla_config.get("core", "inline_bot_token")
            bot_username = message.client.xilla_config.get("core", "inline_bot_username")
            
            if bot_token and bot_username:
                # Cache the code to install later
                install_id = f"{message.chat_id}_{message.id}"
                self.pending_installs[install_id] = {"filename": filename, "code": code, "original_msg": message}
                
                text = f"📦 <b>Установка модуля:</b> {filename}\n\n<i>Как вы хотите установить этот модуль?</i>"
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "💾 Сохранить на диск", "callback_data": f"inst_disk_{install_id}"}],
                        [{"text": "🧠 В оперативную память", "callback_data": f"inst_mem_{install_id}"}],
                        [{"text": "🔒 Всегда на диск (Больше не спрашивать)", "callback_data": f"inst_alw_{install_id}"}],
                        [{"text": "🚫 Отмена", "callback_data": f"inst_can_{install_id}"}]
                    ]
                }
                
                # Send via Bot API to Bot's PM to ensure the bot can send it (bots can't message users first unless they started it)
                # Since the user started the bot during setup, sending to user's ID works!
                me = await message.client.get_me()
                try:
                    async with aiohttp.ClientSession() as session:
                        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        payload = {
                            "chat_id": me.id,
                            "text": text,
                            "parse_mode": "HTML",
                            "reply_markup": json.dumps(keyboard)
                        }
                        await session.post(api_url, json=payload)
                        
                    await message.edit(f"⏳ <b>Подтвердите установку в личных сообщениях с ботом @{bot_username}...</b>", parse_mode="HTML")
                except Exception as e:
                    await message.edit(f"❌ Ошибка отправки кнопок: {e}")
            else:
                # Fallback
                await self._save_and_load(message, filename, code, save_to_disk=True)

    async def _save_and_load(self, message, filename, code, save_to_disk):
        if save_to_disk:
            filepath = os.path.join("plugins", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            try:
                await message.client.xilla_loader.load_file(filepath)
                await message.edit(f"✅ Плагин <b>{filename}</b> успешно установлен на диск и загружен!", parse_mode="HTML")
            except Exception as e:
                await message.edit(f"❌ Ошибка загрузки: {e}", parse_mode="HTML")
        else:
            import tempfile
            fd, path = tempfile.mkstemp(suffix=".py", prefix="xilla_mem_")
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            
            try:
                await message.client.xilla_loader.load_file(path)
                await message.edit(f"✅ Плагин <b>{filename}</b> загружен в оперативную память!", parse_mode="HTML")
            except Exception as e:
                await message.edit(f"❌ Ошибка загрузки в память: {e}", parse_mode="HTML")
            finally:
                try:
                    os.remove(path)
                except: pass

    async def on_load(self):
        from herokutl import events
        
        # Intercept callback queries from the bot
        bot_username = self.client.xilla_config.get("core", "inline_bot_username")
        if bot_username:
            @self.client.on(events.CallbackQuery())
            async def installer_callback_handler(event):
                data = event.data.decode('utf-8')
                if not data.startswith("inst_"):
                    return
                    
                parts = data.split("_", 2)
                if len(parts) < 3: return
                
                action = parts[1]
                install_id = parts[2]
                
                if install_id not in self.pending_installs:
                    return await event.answer("❌ Сессия установки устарела", alert=True)
                    
                pending = self.pending_installs[install_id]
                filename = pending["filename"]
                code = pending["code"]
                orig_msg = pending["original_msg"]
                
                bot_token = self.client.xilla_config.get("core", "inline_bot_token")
                
                async def delete_bot_msg():
                    async with aiohttp.ClientSession() as session:
                        await session.post(f"https://api.telegram.org/bot{bot_token}/deleteMessage", json={"chat_id": event.chat_id, "message_id": event.message_id})

                if action == "disk":
                    await self._save_and_load(orig_msg, filename, code, True)
                    await delete_bot_msg()
                elif action == "mem":
                    await self._save_and_load(orig_msg, filename, code, False)
                    await delete_bot_msg()
                elif action == "alw":
                    self.client.xilla_config.set("installer", "mode", "always_disk")
                    await self._save_and_load(orig_msg, filename, code, True)
                    await delete_bot_msg()
                elif action == "can":
                    await orig_msg.edit("🚫 Установка отменена.")
                    await delete_bot_msg()
                    
                del self.pending_installs[install_id]