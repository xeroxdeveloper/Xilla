import time
import os
import subprocess
from xilla.core import Module, command
from herokutl.tl.types import Message
from xilla.version import __version__, branch, codename

START_TIME = time.time()

def get_uptime():
    seconds = int(time.time() - START_TIME)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    return f"{days}д {hours}ч {mins}м {secs}с"

def get_last_commit():
    try:
        commit = subprocess.check_output(["git", "log", "-1", "--format=%h: %s"], stderr=subprocess.STDOUT).decode().strip()
        return commit
    except Exception:
        return "Неизвестно"

class CoreMod(Module):
    """Основные утилиты юзербота Xilla"""
    
    @command("ping")
    async def ping_cmd(self, message: Message):
        """Проверка работоспособности"""
        start = time.perf_counter_ns()
        msg = await message.edit("<b>☀️ Понг...</b>", parse_mode="HTML")
        ping_ms = round((time.perf_counter_ns() - start) / 10**6, 2)
        
        await msg.edit(f"<b>☀️ Pong!</b>\n<b>⚡ Пинг:</b> <code>{ping_ms} ms</code>\n<b>⏳ Аптайм:</b> <code>{get_uptime()}</code>", parse_mode="HTML")

    @command("xilla")
    async def xilla_cmd(self, message: Message):
        """Информация о юзерботе"""
        version_str = ".".join(map(str, __version__))
        commit = get_last_commit()
        
        text = (
            f"<b>☀️ Xilla Userbot ({codename})</b>\n\n"
            f"<b>⚙️ Версия:</b> <code>{version_str}</code>\n"
            f"<b>🌿 Ветка:</b> <code>{branch}</code>\n"
            f"<b>📝 Последний коммит:</b> <code>{commit}</code>\n\n"
            f"<b>🔗 Репозиторий:</b> <a href='https://github.com/xeroxdeveloper/Xilla'>GitHub</a>"
        )
        await message.edit(text, parse_mode="HTML", link_preview=False)

    @command("help")
    async def help_cmd(self, message: Message):
        """Справка по командам"""
        reply = f"<b>☀️ Xilla {codename}</b>\n\n"
        
        modules = message.client.xilla_loader.modules
        reply += f"<b>📚 Всего модулей:</b> <code>{len(modules)}</code>\n\n"
        
        # Split into system and user plugins based on filepath or specific flag
        sys_mods = []
        user_mods = []
        
        for mod in modules:
            name = getattr(mod, "strings", {}).get("name", mod.__class__.__name__.replace("Mod", ""))
            cmds = []
            for m_name in dir(mod):
                method = getattr(mod, m_name)
                if hasattr(method, "_xilla_command"):
                    cmds.append(f"<code>.{method._xilla_command}</code>")
                    
            if not cmds:
                continue
                
            mod_text = f"<b>📦 {name}:</b>\n {' '.join(cmds)}\n"
            
            # Use module's underlying module name to determine if it's from core or plugins
            if mod.__module__.startswith("xilla.dynamic"):
                user_mods.append(mod_text)
            else:
                sys_mods.append(mod_text)
                
        # Feature: Different quoting/formatting for System vs User modules
        if sys_mods:
            reply += "<blockquote expandable><b>🛠 Системные:</b>\n\n" + "\n".join(sys_mods) + "</blockquote>\n"
            
        if user_mods:
            reply += "<blockquote expandable><b>🧩 Установленные:</b>\n\n" + "\n".join(user_mods) + "</blockquote>\n"
            
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            width, height = 800, 300
            image = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(image)
            
            # Xilla Cyan-Blue Gradient
            for x in range(width):
                r = int(0 + (34 - 0) * (x / width))
                g = int(210 + (157 - 210) * (x / width))
                b = int(255 + (229 - 255) * (x / width))
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
                
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            except Exception:
                font_title = ImageFont.load_default()

            title = "XILLA HELP"
            if hasattr(font_title, "getbbox"):
                title_bbox = font_title.getbbox(title)
                title_w = title_bbox[2] - title_bbox[0]
            else:
                title_w = len(title) * 45
                
            draw.text(((width - title_w) / 2, 100), title, fill="white", font=font_title)
            
            out = io.BytesIO()
            out.name = "help.jpg"
            image.save(out, "JPEG", quality=95)
            out.seek(0)
            
            await message.client.send_file(message.peer_id, out, caption=reply, reply_to=message.reply_to_msg_id, parse_mode="HTML")
            await message.delete()
        except Exception:
            await message.edit(reply, parse_mode="HTML")
        except Exception:
            await message.edit(reply, parse_mode="HTML")
