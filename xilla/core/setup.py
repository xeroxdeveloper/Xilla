import string
import random
import logging
import asyncio
from herokutl.tl.functions.channels import CreateChannelRequest, EditPhotoRequest
from herokutl.tl.functions.messages import ImportChatInviteRequest
from herokutl.tl.types import InputChatUploadedPhoto

logger = logging.getLogger("XillaSetup")

async def setup_xilla(client):
    """Run initial setup routines (groups, bot creation)"""
    config = client.xilla_config
    
    setup_done = config.get("core", "setup_done", False)
    if setup_done:
        return
        
    logger.info("☀️ Запуск первоначальной настройки Xilla...")
    
    # 1. Create or Find Groups
    try:
        logs_id = config.get("core", "logs_chat")
        backups_id = config.get("core", "backups_chat")
        
        # Check existing dialogs first to not create duplicates
        if not logs_id or not backups_id:
            async for dialog in client.iter_dialogs():
                if dialog.title == "Xilla Logs" and not logs_id:
                    logs_id = dialog.id
                    config.set("core", "logs_chat", logs_id)
                elif dialog.title == "Xilla Backups" and not backups_id:
                    backups_id = dialog.id
                    config.set("core", "backups_chat", backups_id)
                    
        if not logs_id:
            logger.info("Создание группы Xilla Logs...")
            result = await client(CreateChannelRequest(
                title="Xilla Logs",
                about="Системные логи юзербота Xilla.",
                megagroup=True
            ))
            logs_id = result.chats[0].id
            config.set("core", "logs_chat", logs_id)
            
        if not backups_id:
            logger.info("Создание группы Xilla Backups...")
            result = await client(CreateChannelRequest(
                title="Xilla Backups",
                about="Резервные копии конфигурации Xilla.",
                megagroup=True
            ))
            backups_id = result.chats[0].id
            config.set("core", "backups_chat", backups_id)
    except Exception as e:
        logger.error(f"Не удалось создать системные группы: {e}")

    # 2. Create Bot
    bot_token = config.get("core", "inline_bot_token")
    if not bot_token:
        logger.info("Создание инлайн-бота через @BotFather...")
        try:
            rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            bot_username = f"xilla_{rnd}_bot"
            
            async with client.conversation("@BotFather", timeout=15) as conv:
                await conv.send_message("/newbot")
                await conv.get_response() # alright, new bot. name?
                
                await conv.send_message("Xilla")
                await conv.get_response() # good. username?
                
                await conv.send_message(bot_username)
                resp = await conv.get_response()
                
                if "Done! Congratulations" in resp.text:
                    import re
                    # BotFather response format usually:
                    # Use this token to access the HTTP API:
                    # 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ
                    match = re.search(r"([0-9]{8,10}:[a-zA-Z0-9_-]{35})", resp.text)
                    if match:
                        bot_token = match.group(1)
                        config.set("core", "inline_bot_token", bot_token)
                        config.set("core", "inline_bot_username", bot_username)
                        logger.info(f"✅ Бот @{bot_username} успешно создан!")
                        
                        # Enable inline mode
                        await conv.send_message("/setinline")
                        await conv.get_response()
                        await conv.send_message(f"@{bot_username}")
                        await conv.get_response()
                        await conv.send_message("Search Xilla...")
                        await conv.get_response()
                        logger.info("✅ Инлайн режим включен!")
                    else:
                        logger.error("Не удалось спарсить токен.")
                else:
                    logger.error(f"BotFather вернул ошибку: {resp.text}")
        except Exception as e:
            logger.error(f"Сбой диалога с BotFather: {e}")
            
        # Fallback manual input if auto-creation failed
        if not bot_token:
            print("\n\033[38;2;255;100;100m[!] Автоматическое создание бота не удалось (возможно флуд-лимит BotFather).[0m")
            print("Пожалуйста, создайте бота вручную в @BotFather и введите его токен сюда:")
            try:
                bot_token = input("Токен бота: ").strip()
                if bot_token:
                    config.set("core", "inline_bot_token", bot_token)
                    logger.info("Токен сохранен!")
            except Exception:
                pass

    config.set("core", "setup_done", True)
    logger.info("☀️ Первоначальная настройка завершена!")
