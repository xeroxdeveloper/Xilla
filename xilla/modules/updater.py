import sys
import os
import git
from hikkatl.tl.types import Message
from xilla import loader, utils

@loader.tds
class UpdaterMod(loader.Module):
    """Обновление Xilla"""
    
    strings = {
        "name": "Updater",
        "updating": "<b>☀️ Установка обновления...</b>",
        "success": "<b>☀️ Xilla успешно обновлена! Перезагрузка...</b>",
        "no_updates": "<b>☀️ Обновлений не найдено. Вы используете последнюю версию Xilla!</b>",
        "error": "<b>❌ Ошибка при обновлении:</b> <code>{error}</code>"
    }

    @loader.command()
    async def update(self, message: Message):
        """- Обновить юзербота"""
        banner = "https://image.pollinations.ai/prompt/shining_sun_minimalist_vector_uploading_updating_aesthetic_blue_orange?width=600&height=200&nologo=true"
        msg = await utils.answer_file(message, banner, self.strings("updating"))
        try:
            repo = git.Repo(search_parent_directories=True)
            origin = repo.remotes.origin
            origin.fetch()
            
            diff = repo.git.log(["HEAD..origin/main", "--oneline"])
            if not diff:
                return await utils.answer_file(msg, banner, self.strings("no_updates"))
                
            repo.git.reset("--hard", "origin/main")
            os.system(f"{sys.executable} -m pip install -r requirements.txt -q")
            
            await utils.answer_file(msg, banner, self.strings("success"))
            os.execl(sys.executable, sys.executable, "-m", "xilla")
            
        except Exception as e:
            await utils.answer_file(msg, banner, self.strings("error").format(error=str(e)))
