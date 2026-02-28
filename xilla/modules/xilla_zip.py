import os
import tarfile
import zipfile
import shutil
import tempfile
import asyncio

from hikkatl.tl.types import Message
from xilla import loader, utils

@loader.tds
class XillaZipMod(loader.Module):
    """Module for creating archives (.zip, .tar, .tar.gz) from files or local paths."""
    
    strings = {
        "name": "XillaZip",
        "reply_required": "<b>❌ Реплай на файл(ы) или укажите путь!</b>",
        "downloading": "<b>⬇️ Скачивание файлов...</b>",
        "archiving": "<b>📦 Создание архива {archive_name}...</b>",
        "uploading": "<b>⬆️ Загрузка архива...</b>",
        "error": "<b>❌ Ошибка:</b> <code>{error}</code>",
        "invalid_path": "<b>❌ Путь не найден!</b>"
    }
    
    async def client_ready(self):
        pass

    async def _pack(self, message: Message, fmt: str):
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        path_to_pack = None
        archive_name = "archive" + fmt
        
        if not reply and not args:
            return await utils.answer(message, self.strings("reply_required"))
            
        if args and os.path.exists(args):
            path_to_pack = args
            archive_name = os.path.basename(path_to_pack) + fmt
        elif args and not reply:
            return await utils.answer(message, self.strings("invalid_path"))
        elif reply and args:
            archive_name = args if args.endswith(fmt) else args + fmt
            
        msg = await utils.answer(message, self.strings("downloading") if reply else self.strings("archiving").format(archive_name=archive_name))
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                if not path_to_pack:
                    # Download replied file
                    filename = getattr(reply.file, "name", "file") or "file"
                    path_to_pack = os.path.join(tmpdir, filename)
                    await message.client.download_media(reply, file=path_to_pack)
                
                await utils.answer(msg, self.strings("archiving").format(archive_name=archive_name))
                archive_path = os.path.join(tmpdir, archive_name)
                
                if fmt == ".zip":
                    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                        if os.path.isdir(path_to_pack):
                            for root, dirs, files in os.walk(path_to_pack):
                                for file in files:
                                    zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path_to_pack, '..')))
                        else:
                            zf.write(path_to_pack, os.path.basename(path_to_pack))
                elif fmt in [".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz"]:
                    mode = "w"
                    if fmt in [".tar.gz", ".tgz"]: mode = "w:gz"
                    elif fmt == ".tar.bz2": mode = "w:bz2"
                    elif fmt == ".tar.xz": mode = "w:xz"
                    
                    with tarfile.open(archive_path, mode) as tf:
                        tf.add(path_to_pack, arcname=os.path.basename(path_to_pack))
                        
                await utils.answer(msg, self.strings("uploading"))
                await message.client.send_file(message.peer_id, archive_path, reply_to=message.reply_to_msg_id)
                await msg.delete()
                
        except Exception as e:
            await utils.answer(msg, self.strings("error").format(error=str(e)))

    @loader.command()
    async def zip(self, message: Message):
        """<path/reply> - Pack into .zip"""
        await self._pack(message, ".zip")

    @loader.command()
    async def tar(self, message: Message):
        """<path/reply> - Pack into .tar"""
        await self._pack(message, ".tar")
        
    @loader.command()
    async def gz(self, message: Message):
        """<path/reply> - Pack into .tar.gz"""
        await self._pack(message, ".tar.gz")

    @loader.command()
    async def tgz(self, message: Message):
        """<path/reply> - Pack into .tgz"""
        await self._pack(message, ".tgz")
