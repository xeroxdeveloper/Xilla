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
    
    # 1. Create Groups
    try:
        logs_id = config.get("core", "logs_chat")
        if not logs_id:
            logger.info("Создание группы Xilla Logs...")
            result = await client(CreateChannelRequest(
                title="Xilla Logs",
                about="Системные логи юзербота Xilla.",
                megagroup=True
            ))
            logs_id = result.chats[0].id
            config.set("core", "logs_chat", logs_id)
            
        backups_id = config.get("core", "backups_chat")
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
            # We communicate with BotFather
            rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            bot_username = f"xilla_{rnd}_bot"
            
            async with client.conversation("@BotFather", timeout=10) as conv:
                await conv.send_message("/newbot")
                await conv.get_response() # alright, new bot. name?
                
                await conv.send_message("Xilla Assistant")
                await conv.get_response() # good. username?
                
                await conv.send_message(bot_username)
                resp = await conv.get_response()
                
                if "Done! Congratulations" in resp.text:
                    # Extract token
                    import re
                    match = re.search(r"Use this token to access the HTTP API:\n([0-9]+:[a-zA-Z0-9_-]+)", resp.text)
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
                        logger.error("Не удалось найти токен в ответе BotFather.")
                else:
                    logger.error(f"Ошибка создания бота: {resp.text}")
        except Exception as e:
            logger.error(f"Сбой диалога с BotFather: {e}")

    config.set("core", "setup_done", True)
    logger.info("☀️ Первоначальная настройка завершена!")
