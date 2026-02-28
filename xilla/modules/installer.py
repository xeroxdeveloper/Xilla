import os
import aiohttp
import tempfile
from xilla.core import Module, command
from herokutl.tl.types import Message
from herokutl.tl.custom.button import Button

class InstallerMod(Module):
    """Модуль для скачивания плагинов и установки"""

    def __init__(self):
        super().__init__()
        # Temporary storage for files waiting for installation choice
        self.pending_installs = {}

    @command("install")
    async def install_cmd(self, message: Message):
        """<ссылка/реплай> - Скачать и установить модуль"""
        reply = await message.get_reply_message()
        url = message.args.strip()
        
        if not url and not (reply and reply.media):
            return await message.edit("❌ Укажите ссылку на .py файл (GitHub/GitLab) или сделайте реплай на файл.")
            
        await message.edit("⏳ Подготовка к установке...")
        
        # Determine installation mode preference
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

        # If user has a saved preference, execute immediately
        if install_mode == "always_disk":
            await self._save_and_load(message, filename, code, save_to_disk=True)
        elif install_mode == "always_memory":
            await self._save_and_load(message, filename, code, save_to_disk=False)
        else:
            # First time install or no preference set: ask via Bot API inline buttons!
            # Since we can only send real inline keyboards via bot or userbot clicking bot, 
            # let's just use the bot to ask the question in the log channel or chat.
            
            # Actually, userbots can't SEND inline buttons. We must send a message using the inline bot 
            # or just ask for a command response.
            
            # Since we have an inline bot configured, we can ask the bot to send the keyboard to the Logs channel,
            # but that's complex. Let's do a simple interactive terminal-like approach or command-based approach.
            
            bot_username = message.client.xilla_config.get("core", "inline_bot_username")
            if bot_username:
                # We can use inline bot via inline query to generate a button, but it's easier to just ask the user
                # to reply with a choice, OR we can generate an inline keyboard if we send it via our bot token.
                pass
                
            # Alternative: Text-based interactive menu
            self.pending_installs[message.chat_id] = {"filename": filename, "code": code, "msg_id": message.id}
            
            text = (
                f"📦 <b>Установка модуля:</b> <code>{filename}</code>\n\n"
                f"<i>Как вы хотите установить этот модуль? Выберите вариант и отправьте соответствующую цифру в ответ:</i>\n\n"
                f"<b>1.</b> 💾 Сохранить на диск (Останется после перезагрузки)\n"
                f"<b>2.</b> 🧠 Установить в память (Удалится при перезагрузке)\n"
                f"<b>3.</b> 🔒 Всегда сохранять на диск (Больше не спрашивать)\n"
                f"<b>4.</b> 🚫 Отмена"
            )
            await message.edit(text, parse_mode="HTML")
            
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
            # Load in memory
            # We can write to a temp file and load it, then delete it.
            # But loader needs a file path.
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

    # We need to catch the reply
    async def on_load(self):
        from herokutl import events
        
        async def reply_handler(event):
            if not event.message.out:
                return
                
            reply = await event.get_reply_message()
            if not reply or event.chat_id not in self.pending_installs:
                return
                
            pending = self.pending_installs[event.chat_id]
            if reply.id == pending["msg_id"]:
                choice = event.raw_text.strip()
                filename = pending["filename"]
                code = pending["code"]
                
                if choice == "1":
                    await self._save_and_load(reply, filename, code, True)
                    del self.pending_installs[event.chat_id]
                elif choice == "2":
                    await self._save_and_load(reply, filename, code, False)
                    del self.pending_installs[event.chat_id]
                elif choice == "3":
                    event.client.xilla_config.set("installer", "mode", "always_disk")
                    await self._save_and_load(reply, filename, code, True)
                    del self.pending_installs[event.chat_id]
                elif choice == "4":
                    await reply.edit("🚫 Установка отменена.")
                    del self.pending_installs[event.chat_id]
                    
                await event.delete()
                
        self.client.add_event_handler(reply_handler, events.NewMessage())