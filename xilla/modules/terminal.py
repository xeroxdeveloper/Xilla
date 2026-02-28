import asyncio
import os
import sys
import traceback
import subprocess
from xilla.core import Module, command
from herokutl.tl.types import Message

class TerminalMod(Module):
    """Выполнение системных команд (Shell & Pip)"""

    @command("t")
    async def terminal_cmd(self, message: Message):
        """<команда> - Выполнить bash/shell команду"""
        cmd = message.args.strip()
        if not cmd:
            return await message.edit("❌ Введите команду для выполнения (например: <code>.t ls -la</code>)", parse_mode="HTML")
            
        await message.edit(f"<b>💻 Выполнение:</b>\n<code>{cmd}</code>", parse_mode="HTML")
        
        try:
            # Run async to not block the main loop
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            out = stdout.decode('utf-8', errors='ignore')[:3500]
            err = stderr.decode('utf-8', errors='ignore')[:500]
            
            result = ""
            if out: result += f"<b>STDOUT:</b>\n<blockquote expandable><code>{out}</code></blockquote>\n"
            if err: result += f"<b>STDERR:</b>\n<blockquote expandable><code>{err}</code></blockquote>\n"
            
            if not result:
                result = "<i>Успешно (без вывода)</i>"
                
            await message.edit(f"<b>💻 Команда:</b> <code>{cmd}</code>\n\n{result}", parse_mode="HTML")
        except Exception as e:
            await message.edit(f"<b>❌ Ошибка выполнения:</b>\n<code>{e}</code>", parse_mode="HTML")

    @command("pip")
    async def pip_cmd(self, message: Message):
        """install <пакет> - Управление python-пакетами"""
        args = message.args.strip()
        if not args:
            return await message.edit("❌ Укажите аргументы для pip (например: <code>.pip install openai</code>)", parse_mode="HTML")
            
        await message.edit(f"<b>📦 Установка...</b>\n<code>pip {args}</code>", parse_mode="HTML")
        
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", *args.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            out = stdout.decode('utf-8', errors='ignore')[:3500]
            err = stderr.decode('utf-8', errors='ignore')[:500]
            
            result = ""
            if out: result += f"<b>STDOUT:</b>\n<blockquote expandable><code>{out}</code></blockquote>\n"
            if err: result += f"<b>STDERR:</b>\n<blockquote expandable><code>{err}</code></blockquote>\n"
            
            await message.edit(f"<b>📦 Pip:</b> <code>{args}</code>\n\n{result}", parse_mode="HTML")
        except Exception as e:
            await message.edit(f"<b>❌ Ошибка Pip:</b>\n<code>{e}</code>", parse_mode="HTML")
