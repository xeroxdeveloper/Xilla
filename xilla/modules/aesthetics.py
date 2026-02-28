from xilla.core import Module, command
from herokutl.tl.types import Message
import io

class AestheticsMod(Module):
    """Визуальные функции и баннеры"""
    strings = {"name": "Aesthetics"}

    @command("info")
    async def info_cmd(self, message: Message):
        """Информация о юзерботе"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import os
            
            width, height = 800, 300
            image = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(image)
            
            # Xilla Purple-Blue Gradient
            for x in range(width):
                r = int(58 + (0 - 58) * (x / width))
                g = int(123 + (210 - 123) * (x / width))
                b = int(213 + (255 - 213) * (x / width))
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
                
            # Add some stars / aesthetic particles
            import random
            for _ in range(50):
                sx = random.randint(0, width)
                sy = random.randint(0, height)
                sr = random.randint(1, 3)
                draw.ellipse([sx, sy, sx+sr, sy+sr], fill="white")
                
            try:
                # Try to use a system font if available, fallback to default
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
                font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            except Exception:
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()

            title = "XILLA USERBOT"
            # Fallback measurement for default font
            if hasattr(font_title, "getbbox"):
                title_bbox = font_title.getbbox(title)
                title_w = title_bbox[2] - title_bbox[0]
            else:
                title_w = len(title) * 45 # Rough estimate
                
            draw.text(((width - title_w) / 2, 100), title, fill="white", font=font_title)
            
            sub = "Anti-1 Architecture"
            if hasattr(font_subtitle, "getbbox"):
                sub_bbox = font_subtitle.getbbox(sub)
                sub_w = sub_bbox[2] - sub_bbox[0]
            else:
                sub_w = len(sub) * 15
                
            draw.text(((width - sub_w) / 2, 190), sub, fill="#f0f0f0", font=font_subtitle)
            
            out = io.BytesIO()
            out.name = "xilla_info.jpg"
            image.save(out, "JPEG", quality=95)
            out.seek(0)
            
            me = await message.client.get_me()
            text = f"<b>☀️ Xilla Userbot (A2)</b>\n\n<b>👑 Владелец:</b> {me.first_name}\n<b>⚡ Ядро:</b> herokutl\n<b>🛡️ Статус:</b> Стабильно"
            
            await message.client.send_file(message.peer_id, out, caption=text, reply_to=message.reply_to_msg_id, parse_mode="HTML")
            await message.delete()
        except Exception as e:
            await message.edit(f"<b>☀️ Xilla Userbot (A2)</b>\n\nОшибка рендера: {e}", parse_mode="HTML")
