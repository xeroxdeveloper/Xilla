import string
import random
import logging
import asyncio
from herokutl.tl.functions.channels import CreateChannelRequest, EditPhotoRequest
from herokutl.tl.functions.messages import ImportChatInviteRequest
from herokutl.tl.types import InputChatUploadedPhoto

logger = logging.getLogger("XillaSetup")

async def setup_xilla(client):
    """Run initial setup routines (groups, bot creation, bot adding)"""
    config = client.xilla_config
    
    logs_id = config.get("core", "logs_chat")
    backups_id = config.get("core", "backups_chat")
    bot_token = config.get("core", "inline_bot_token")
    
    if logs_id and backups_id and bot_token:
        # Check if setup_done is true just to prevent infinite /start messages
        if config.get("core", "setup_done", False):
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
        if not config.get("core", "inline_bot_token"):
            print("\n\033[38;2;255;100;100m[!] Автоматическое создание бота не удалось (возможно флуд-лимит BotFather).[0m")
            print("Пожалуйста, создайте бота вручную в @BotFather и введите его токен сюда:")
            try:
                manual_token = input("Токен бота: ").strip()
                if manual_token:
                    config.set("core", "inline_bot_token", manual_token)
                    logger.info("Токен сохранен!")
                    # Extract bot username from token
                    bot_username = await client.get_entity(manual_token.split(":")[0])
                    bot_username = bot_username.username
                    config.set("core", "inline_bot_username", bot_username)
            except Exception:
                pass

    # 3. Add Bot to Groups and Start Initial Config
    bot_username = config.get("core", "inline_bot_username")
    if bot_username:
        try:
            from herokutl.tl.functions.channels import InviteToChannelRequest
            
            # 1. Сначала отправим /start, чтобы клиент "увидел" бота (кэшировал сущность)
            if not config.get("core", "setup_done", False):
                try:
                    await asyncio.sleep(2)  # Дать Telegram время на регистрацию юзернейма
                    await client.send_message(bot_username, "/start")
                    logger.info("🤖 Отправлена команда /start для запуска мастера настройки.")
                except Exception as e:
                    logger.error(f"Не удалось отправить /start: {e}")
                    
            # 2. Теперь бот в кэше, добавляем его в группы
            # Resolve entities for adding to channels
            try:
                bot_user = await client.get_input_entity(bot_username)
            except Exception:
                bot_user = bot_username

            # Add to Logs
            if logs_id:
                try:
                    logs_channel = await client.get_input_entity(logs_id)
                    await client(InviteToChannelRequest(logs_channel, [bot_user]))
                    logger.info("🤖 Бот добавлен в Xilla Logs")
                except Exception as e:
                    logger.error(f"Не удалось добавить бота в Logs: {e}")
                    
            # Add to Backups
            if backups_id:
                try:
                    backups_channel = await client.get_input_entity(backups_id)
                    await client(InviteToChannelRequest(backups_channel, [bot_user]))
                    logger.info("🤖 Бот добавлен в Xilla Backups")
                except Exception as e:
                    logger.error(f"Не удалось добавить бота в Backups: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка при настройке бота: {e}")

    # 4. Telegram Folders setup
    try:
        from herokutl.tl.functions.messages import GetDialogFiltersRequest, UpdateDialogFilterRequest
        from herokutl.tl.types import DialogFilter, InputPeerChat, InputPeerUser, InputPeerChannel
        
        # Get existing folders to not overwrite or duplicate
        filters_obj = await client(GetDialogFiltersRequest())
        
        xilla_folder_exists = False
        archive_folder_exists = False
        max_id = 1
        
        for f in filters_obj.filters:
            if hasattr(f, 'id') and f.id > max_id:
                max_id = f.id
            if getattr(f, 'title', '') == "Xilla":
                xilla_folder_exists = True
                
        # We need peer objects to add to folders
        include_peers = []
        bot_peer = await client.get_input_entity(bot_username) if bot_username else None
        if bot_peer: include_peers.append(bot_peer)
        
        logs_peer = await client.get_input_entity(logs_id) if logs_id else None
        if logs_peer: include_peers.append(logs_peer)
        
        if not xilla_folder_exists and include_peers:
            logger.info("Создание папки Xilla в Telegram...")
            await client(UpdateDialogFilterRequest(
                id=max_id + 1,
                filter=DialogFilter(
                    id=max_id + 1,
                    title="Xilla",
                    pinned_peers=include_peers,
                    include_peers=include_peers,
                    exclude_peers=[],
                    contacts=False,
                    non_contacts=False,
                    groups=False,
                    broadcasts=False,
                    bots=False,
                    exclude_muted=False,
                    exclude_read=False,
                    exclude_archived=False
                )
            ))
            
        # Put Backups into Telegram Archive
        if backups_id:
            try:
                from herokutl.tl.functions.folders import EditPeerFoldersRequest
                from herokutl.tl.types import InputFolderPeer
                logger.info("Отправка Xilla Backups в Архив...")
                await client(EditPeerFoldersRequest(
                    folder_peers=[InputFolderPeer(
                        peer=await client.get_input_entity(backups_id),
                        folder_id=1 # 1 is Telegram's builtin Archive folder
                    )]
                ))
            except Exception as e:
                logger.error(f"Не удалось архивировать Backups: {e}")

    except Exception as e:
        logger.error(f"Ошибка настройки папок: {e}")

    config.set("core", "setup_done", True)
    logger.info("☀️ Первоначальная настройка завершена!")
