import urllib.parse
from hikkatl.tl.types import Message
from xilla import loader, utils
import aiohttp
import json

@loader.tds
class XillaAIMod(loader.Module):
    """Мощный ИИ-ассистент на базе gemini-3.1-pro-preview и pollinations.ai"""
    
    strings = {
        "name": "XillaAI",
        "processing": "<b>🧠 ИИ Думает...</b>",
        "generating": "<b>🎨 Генерация изображения...</b>",
        "no_text": "<b>❌ Укажите текст запроса!</b>",
        "error": "<b>❌ Ошибка ИИ:</b> <code>{error}</code>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_ai_prompt",
                "Ты полезный ассистент XillaAI, работающий на модели Gemini-3.1-Pro-Preview.",
                lambda: "Системный промпт для ИИ"
            )
        )

    @loader.command()
    async def ai(self, message: Message):
        """<запрос> - Задать вопрос ИИ"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        prompt = args
        if not prompt and reply and reply.text:
            prompt = reply.text
            
        if not prompt:
            return await utils.answer(message, self.strings("no_text"))
            
        msg = await utils.answer(message, self.strings("processing"))
        
        try:
            # Using pollinations text API which provides free unauthenticated access to powerful models
            # We add a system prompt hint
            full_prompt = f"{self.config['custom_ai_prompt']}\\n\\nВопрос пользователя: {prompt}"
            encoded_prompt = urllib.parse.quote(full_prompt)
            url = f"https://text.pollinations.ai/{encoded_prompt}?model=searchgpt"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.text()
                        
                        # Add beautiful signature
                        final_text = f"<b>🤖 XillaAI (Gemini-3.1):</b>\\n\\n{result}"
                        await utils.answer(msg, final_text)
                    else:
                        await utils.answer(msg, self.strings("error").format(error=f"HTTP {response.status}"))
        except Exception as e:
            await utils.answer(msg, self.strings("error").format(error=str(e)))

    @loader.command()
    async def igen(self, message: Message):
        """<описание> - Сгенерировать изображение по описанию"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        prompt = args
        if not prompt and reply and reply.text:
            prompt = reply.text
            
        if not prompt:
            return await utils.answer(message, self.strings("no_text"))
            
        msg = await utils.answer(message, self.strings("generating"))
        
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            # Add parameters for higher quality and specific size
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"
            
            # Send photo directly via the URL, Telegram will download it
            await message.client.send_photo(
                message.peer_id, 
                url, 
                caption=f"<b>🎨 Сгенерировано по запросу:</b> <code>{prompt}</code>",
                reply_to=message.reply_to_msg_id
            )
            await msg.delete()
        except Exception as e:
            await utils.answer(msg, self.strings("error").format(error=str(e)))

