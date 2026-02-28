import os
import shutil
import tempfile
import json
import base64
import zlib

from hikkatl.tl.types import Message
from xilla import loader, utils

@loader.tds
class XillaPackMod(loader.Module):
    """
    Системный модуль (пакет) для упаковки и распаковки модулей Xilla
    в любые нестандартные текстовые форматы (.txt, .rb, .pl и др.)
    """
    
    strings = {
        "name": "XillaPack",
        "reply_required": "<b>☀️ Реплай на файл(ы) модуля обязателен!</b>",
        "no_ext": "<b>❌ Укажите расширение, например:</b> <code>.pack .rb</code>",
        "packing": "<b>📦 Упаковка модуля...</b>",
        "unpacking": "<b>📦 Распаковка модуля...</b>",
        "done": "<b>☀️ Готово!</b>",
        "error": "<b>❌ Ошибка:</b> <code>{error}</code>",
        "invalid_pack": "<b>❌ Этот файл не является корректным Xilla Pack!</b>"
    }
    
    # MAGIC SIGNATURE FOR OUR PACK FILES
    MAGIC = b"XILLA_PACK_V1:"

    async def client_ready(self):
        pass

    @loader.command()
    async def pack(self, message: Message):
        """<ext> - Упаковать Python-модуль(и) в специальный текстовый пакет с указанным расширением"""
        args = utils.get_args_raw(message)
        ext = args if args else ".txt"
        if not ext.startswith("."):
            ext = "." + ext

        reply = await message.get_reply_message()
        if not reply or not reply.media or not getattr(reply.file, "name", "").endswith(".py"):
            return await utils.answer(message, self.strings("reply_required"))

        msg = await utils.answer(message, self.strings("packing"))

        try:
            filename = reply.file.name
            pack_name = filename.rsplit(".", 1)[0] + ext
            
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, filename)
                await message.client.download_media(reply, file=filepath)
                
                with open(filepath, "r", encoding="utf-8") as f:
                    code = f.read()

                # Compress and encode to base64 to make it fit into text cleanly and avoid escaping issues
                compressed = zlib.compress(code.encode("utf-8"))
                encoded = base64.b64encode(compressed)
                
                # Format: MAGIC + filename|encoded_data
                payload = self.MAGIC + f"{filename}|".encode("utf-8") + encoded
                
                pack_path = os.path.join(tmpdir, pack_name)
                with open(pack_path, "wb") as f:
                    f.write(payload)

                try:
                    from .banners import create_banner
                    banner = await create_banner("PACKAGER", f"Упаковано в {ext}", "#8E2DE2", "#4A00E0")
                    await utils.answer_file(msg, banner, self.strings("done"))
                except Exception:
                    await utils.answer(msg, self.strings("done"))
                    
                await message.client.send_file(message.peer_id, pack_path, reply_to=message.reply_to_msg_id)
                await msg.delete()

        except Exception as e:
            await utils.answer(msg, self.strings("error").format(error=str(e)))

    @loader.command()
    async def unpack(self, message: Message):
        """- Распаковать Xilla Pack обратно в .py"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            return await utils.answer(message, self.strings("reply_required"))

        msg = await utils.answer(message, self.strings("unpacking"))

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "temp_pack")
                await message.client.download_media(reply, file=filepath)
                
                with open(filepath, "rb") as f:
                    data = f.read()

                if not data.startswith(self.MAGIC):
                    return await utils.answer(msg, self.strings("invalid_pack"))

                # Remove magic
                data = data[len(self.MAGIC):]
                
                # Split filename and content
                try:
                    filename_bytes, content_bytes = data.split(b"|", 1)
                    filename = filename_bytes.decode("utf-8")
                except ValueError:
                    return await utils.answer(msg, self.strings("invalid_pack"))

                decoded = base64.b64decode(content_bytes)
                decompressed = zlib.decompress(decoded).decode("utf-8")

                out_path = os.path.join(tmpdir, filename)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(decompressed)

                try:
                    from .banners import create_banner
                    banner = await create_banner("UNPACKER", f"Распаковано: {filename}", "#11998e", "#38ef7d")
                    await utils.answer_file(msg, banner, self.strings("done"))
                except Exception:
                    await utils.answer(msg, self.strings("done"))
                    
                await message.client.send_file(message.peer_id, out_path, reply_to=message.reply_to_msg_id)
                await msg.delete()

        except Exception as e:
            await utils.answer(msg, self.strings("error").format(error=str(e)))
