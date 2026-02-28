import io
import sys
import traceback
from xilla.core import Module, command
from herokutl.tl.types import Message

class EvalMod(Module):
    """Виртуальная песочница Python"""

    @command("eval")
    async def eval_cmd(self, message: Message):
        """<код> - Выполнить python код"""
        code = message.args
        if not code:
            return await message.edit("❌ Введите код")
        
        await message.edit("⏳ Выполнение...")
        
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        try:
            # Feature 7: Virtual Sandbox
            exec(f"async def _eval_func(message, client):\n" + "".join(f"    {l}\n" for l in code.split("\n")), globals(), locals())
            await locals()["_eval_func"](message, message.client)
            res = redirected_output.getvalue()
            
            if not res:
                res = "Успешно (без вывода)"
                
            await message.edit(f"<b>💻 Код:</b>\n<code>{code}</code>\n\n<b>ВЫВОД:</b>\n<code>{res}</code>", parse_mode="HTML")
        except Exception as e:
            err = traceback.format_exc()
            await message.edit(f"<b>❌ Ошибка Eval:</b>\n<code>{err}</code>", parse_mode="HTML")
        finally:
            sys.stdout = old_stdout
