import os
import aiohttp
from xilla.core import Module, command
from herokutl.tl.types import Message

class InstallerMod(Module):
    """Модуль для скачивания плагинов по ссылке"""

    @command("install")
    async def install_cmd(self, message: Message):
        """<ссылка> - Скачать и установить модуль"""
        # Feature 2: Github/Gitlab module direct install
        url = message.args.strip()
        if not url:
            return await message.edit("❌ Укажите ссылку на .py файл (GitHub/GitLab)")
        
        # Auto-convert github UI links to raw format
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            
        await message.edit("⏳ Загрузка модуля...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        code = await resp.text()
                        filename = url.split("/")[-1]
                        if not filename.endswith(".py"): 
                            filename += ".py"
                            
                        filepath = os.path.join("plugins", filename)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(code)
                            
                        # Hot reload
                        await message.client.xilla_loader.load_file(filepath)
                        await message.edit(f"✅ Плагин <b>{filename}</b> успешно установлен и загружен!", parse_mode="HTML")
                    else:
                        await message.edit(f"❌ Ошибка скачивания: HTTP {resp.status}", parse_mode="HTML")
        except Exception as e:
            await message.edit(f"❌ Системная ошибка: {e}", parse_mode="HTML")
