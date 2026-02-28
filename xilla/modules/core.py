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
        
        for mod in modules:
            name = getattr(mod, "strings", {}).get("name", mod.__class__.__name__.replace("Mod", ""))
            
            cmds = []
            for m_name in dir(mod):
                method = getattr(mod, m_name)
                if hasattr(method, "_xilla_command"):
                    cmds.append(f"<code>.{method._xilla_command}</code>")
                    
            if cmds:
                reply += f"<b>📦 {name}:</b>\n {' '.join(cmds)}\n\n"
                
        await message.edit(reply, parse_mode="HTML")
