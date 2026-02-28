from xilla.core import Module, command
from herokutl.tl.types import Message
import io

class AestheticsMod(Module):
    """Визуальные функции и баннеры"""

    @command("info")
    async def info_cmd(self, message: Message):
        """Информация о юзерботе"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            width, height = 800, 300
            image = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(image)
            
            # Xilla Blue Gradient
            for x in range(width):
                r = int(0 + (58 - 0) * (x / width))
                g = int(210 + (123 - 210) * (x / width))
                b = int(255 + (213 - 255) * (x / width))
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
                
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
                font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            except Exception:
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()

            title = "XILLA ANTI-1"
            title_bbox = draw.textbbox((0, 0), title, font=font_title)
            draw.text(((width - (title_bbox[2]-title_bbox[0])) / 2, 100), title, fill="white", font=font_title)
            
            sub = "Переписано с чистого листа"
            sub_bbox = draw.textbbox((0, 0), sub, font=font_subtitle)
            draw.text(((width - (sub_bbox[2]-sub_bbox[0])) / 2, 190), sub, fill="#f0f0f0", font=font_subtitle)
            
            out = io.BytesIO()
            out.name = "banner.jpg"
            image.save(out, "JPEG", quality=90)
            out.seek(0)
            
            me = await message.client.get_me()
            text = f"<b>☀️ Xilla Userbot (Anti-1)</b>\n\n<b>Владелец:</b> {me.first_name}\n<b>Ядро:</b> herokutl\n<b>Состояние:</b> Идеальное"
            await message.client.send_file(message.peer_id, out, caption=text, reply_to=message.reply_to_msg_id)
            await message.delete()
        except Exception as e:
            await message.edit(f"<b>☀️ Xilla Userbot (Anti-1)</b>\n\nОшибка рендера: {e}", parse_mode="HTML")
