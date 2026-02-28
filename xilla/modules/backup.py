import os
import asyncio
from xilla.core import Module, command
from herokutl.tl.types import Message

class BackupMod(Module):
    """Автоматическое резервное копирование конфигурации"""

    async def on_load(self):
        # Feature 4: Auto-backup configuration to Saved Messages
        asyncio.create_task(self.periodic_backup())
        
    async def periodic_backup(self):
        while True:
            await asyncio.sleep(86400) # Every 24 hours
            await self.do_backup()
            
    async def do_backup(self):
        try:
            if os.path.exists("xilla.json"):
                await self.client.send_file(
                    "me", 
                    "xilla.json", 
                    caption="<b>☁️ Автоматический бэкап конфигурации Xilla (Anti-1)</b>", 
                    parse_mode="HTML"
                )
        except Exception as e:
            self.logger.error(f"Auto-backup failed: {e}")
            
    @command("backup")
    async def force_backup(self, message: Message):
        """- Сделать бэкап настроек вручную"""
        await message.edit("⏳ Создание бэкапа...")
        await self.do_backup()
        await message.edit("✅ Бэкап успешно отправлен в Избранное!", parse_mode="HTML")
