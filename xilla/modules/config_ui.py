import json
import os
import io
from xilla.core import Module, command
from herokutl.tl.types import Message

class ConfigUIMod(Module):
    """Красивая настройка юзербота"""

    @command("config")
    async def config_cmd(self, message: Message):
        """[mod] [key] [val] - Настройки модулей"""
        args = message.args.split()
        
        # New prettier Config UI
        if not args:
            cfg_text = "<b>⚙️ XILLA CONFIG HUB</b>\n\n"
            if os.path.exists("xilla.json"):
                with open("xilla.json", "r") as f:
                    data = json.load(f)
                    mods = data.get("modules", {})
                    if not mods:
                        cfg_text += "<i>Пока нет настроек модулей.</i>\n"
                    else:
                        for mod, keys in mods.items():
                            cfg_text += f"<b>📦 {mod}</b>\n"
                            for k, v in keys.items():
                                # Feature: Mask API keys automatically in UI
                                val = "*" * len(str(v)) if "key" in k.lower() or "token" in k.lower() else str(v)
                                cfg_text += f"  • <code>{k}</code> = {val}\n"
                                
            cfg_text += "\n<i>Использование: .config set [модуль] [ключ] [значение]</i>"
            
            # Generate Pillow Banner for Config Hub just like in previous versions
            try:
                from PIL import Image, ImageDraw, ImageFont
                width, height = 800, 300
                image = Image.new("RGB", (width, height))
                draw = ImageDraw.Draw(image)
                
                # Neon Purple Gradient
                for x in range(width):
                    r = int(142 + (74 - 142) * (x / width))
                    g = int(45 + (0 - 45) * (x / width))
                    b = int(226 + (224 - 226) * (x / width))
                    draw.line([(x, 0), (x, height)], fill=(r, g, b))
                    
                font_title = ImageFont.load_default()
                draw.text((320, 100), "CONFIG HUB", fill="white", font=font_title)
                
                out = io.BytesIO()
                out.name = "banner.jpg"
                image.save(out, "JPEG", quality=90)
                out.seek(0)
                
                await message.client.send_file(message.peer_id, out, caption=cfg_text, reply_to=message.reply_to_msg_id, parse_mode="HTML")
                await message.delete()
            except Exception:
                await message.edit(cfg_text, parse_mode="HTML")
                
        elif len(args) >= 4 and args[0] == "set":
            # Usage: .config set XillaAI gemini_api_key 12345
            mod = args[1]
            key = args[2]
            val = " ".join(args[3:])
            
            message.client.xilla_config.set(mod, key, val)
            await message.edit(f"✅ Настройка обновлена!\n<b>{mod}</b> -> <code>{key}</code> = <code>{val}</code>", parse_mode="HTML")
        else:
            await message.edit("❌ Неверный формат! Используйте <code>.config set [модуль] [ключ] [значение]</code>", parse_mode="HTML")
