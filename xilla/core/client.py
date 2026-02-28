from xilla.core.setup import setup_xilla
import os
import sys
import logging
import asyncio
from herokutl import TelegramClient, events
from xilla.core.loader import ModuleLoader
from xilla.core.config import get_api_credentials, ConfigManager
from xilla.core.i18n import I18n
from xilla.core.db import XillaDB
from xilla.utils.cache import MediaCache

class XillaClient:
    def __init__(self):
        self.logger = logging.getLogger("Xilla")
        self.api_id, self.api_hash = get_api_credentials()
        self.session_path = os.path.join(os.getcwd(), "xilla.session")
        self.client = TelegramClient(self.session_path, self.api_id, self.api_hash, device_model="Xilla Userbot", system_version="Linux", app_version="A1")
        
        # Attach core utilities to client so modules can access them
        self.client.xilla_config = ConfigManager()
        self.client.xilla_i18n = I18n(self.client.xilla_config)
        self.client.xilla_db = XillaDB()
        self.client.xilla_cache = MediaCache()
        
        self.client.xilla_loader = ModuleLoader(self.client)
        self.loader = self.client.xilla_loader

    async def _start_async(self):
        self.logger.info("☀️ Запуск Xilla (Anti 1)...")
        await self.client.connect()
        
        # Safe Login Flow
        if not await self.client.is_user_authorized():
            phone = input("📱 Введите номер телефона (или токен бота): ")
            try:
                await self.client.send_code_request(phone)
                code = input("💬 Введите код из Telegram: ")
                try:
                    await self.client.sign_in(phone, code)
                except Exception as e:
                    if "SessionPasswordNeeded" in str(type(e).__name__) or "password" in str(e).lower():
                        import getpass
                        password = getpass.getpass("🔒 Введите пароль двухфакторной аутентификации: ")
                        await self.client.sign_in(password=password)
                    else:
                        raise e
            except Exception as e:
                self.logger.error(f"❌ Ошибка авторизации: {e}")
                sys.exit(1)
            
        msg = self.client.xilla_i18n.t("startup_success", "☀️ Xilla A1 успешно запущена!")
        self.logger.info(msg)
        
        # Run auto-setup
        await setup_xilla(self.client)

        
        # Load internal modules, plugins and packages
        await self.loader.load_all()
        
        self.logger.info("☀️ Xilla Userbot готов к работе!")
        await self.client.run_until_disconnected()

    def run(self):
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._start_async())
        except KeyboardInterrupt:
            self.logger.info("[!] Остановка Xilla...")
            loop.run_until_complete(self.client.disconnect())
        finally:
            import os, signal
            os.kill(os.getpid(), signal.SIGKILL)
