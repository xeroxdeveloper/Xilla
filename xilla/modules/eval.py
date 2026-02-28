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
            exec(f"async def _eval_func(message, client):
" + "".join(f"    {l}
" for l in code.split("
")), globals(), locals())
            await locals()["_eval_func"](message, message.client)
            res = redirected_output.getvalue()
            
            if not res:
                res = "Успешно (без вывода)"
                
            await message.edit(f"<b>💻 Код:</b>
<blockquote><code>{code}</code></blockquote>

<b>ВЫВОД:</b>
<blockquote expandable><code>{res}</code></blockquote>", parse_mode="HTML")
        except Exception as e:
            err = traceback.format_exc()
            await message.edit(f"<b>❌ Ошибка Eval:</b>
<blockquote expandable><code>{err}</code></blockquote>", parse_mode="HTML")
        finally:
            sys.stdout = old_stdout
