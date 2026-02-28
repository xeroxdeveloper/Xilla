import urllib.parse
from hikkatl.tl.types import Message
from xilla import loader, utils
import aiohttp

@loader.tds
class XillaAIMod(loader.Module):
    """Мощный ИИ-ассистент на базе Google Gemini и генерации изображений"""
    
    strings = {
        "name": "XillaAI",
        "processing": "<b>🧠 XillaAI Думает...</b>",
        "generating": "<b>🎨 Генерация изображения...</b>",
        "no_text": "<b>❌ Укажите текст запроса!</b>",
        "no_key": "<b>❌ Укажите API ключ Gemini в конфигурации модуля (.cfg)</b>",
        "error": "<b>❌ Ошибка ИИ:</b> <code>{error}</code>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "gemini_api_key",
                None,
                lambda: "API Ключ для Google Gemini (получить на aistudio.google.com)",
                validator=loader.validators.Hidden(loader.validators.String())
            ),
            loader.ConfigValue(
                "custom_ai_prompt",
                "Ты полезный ассистент XillaAI, работающий на модели Gemini-3.1-Pro-Preview. Отвечай кратко, красиво и по делу.",
                lambda: "Системный промпт для ИИ"
            )
        )

    @loader.command()
    async def ai(self, message: Message):
        """<запрос> - Задать вопрос ИИ (Требуется Gemini API Key)"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        prompt = args
        if not prompt and reply and reply.text:
            prompt = reply.text
            
        if not prompt:
            return await utils.answer(message, self.strings("no_text"))
            
        api_key = self.config["gemini_api_key"]
        if not api_key:
            return await utils.answer(message, self.strings("no_key"))
            
        msg = await utils.answer(message, self.strings("processing"))
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"{self.config['custom_ai_prompt']}\\n\\nВопрос пользователя: {prompt}"}]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Нет ответа")
                        
                        # Add beautiful signature
                        final_text = f"<b>🤖 XillaAI (Gemini):</b>\\n\\n{result}"
                        await utils.answer(msg, final_text)
                    else:
                        error_data = await response.text()
                        await utils.answer(msg, self.strings("error").format(error=f"HTTP {response.status}: {error_data}"))
        except Exception as e:
            await utils.answer(msg, self.strings("error").format(error=str(e)))

    @loader.command()
    async def igen(self, message: Message):
        """<описание> - Сгенерировать изображение по описанию (Без ключа)"""
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
            # Image generation still uses Pollinations as Gemini API doesn't support free Image Gen directly yet
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"
            
            await message.client.send_photo(
                message.peer_id, 
                url, 
                caption=f"<b>🎨 Сгенерировано по запросу:</b> <code>{prompt}</code>",
                reply_to=message.reply_to_msg_id
            )
            await msg.delete()
        except Exception as e:
            await utils.answer(msg, self.strings("error").format(error=str(e)))

