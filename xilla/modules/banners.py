import io
from PIL import Image, ImageDraw, ImageFont

_BANNER_CACHE = {}

async def create_banner(title: str, subtitle: str, color1: str = "#00d2ff", color2: str = "#3a7bd5") -> io.BytesIO:
    """Creates a beautiful gradient banner using Pillow (Optimized)"""
    cache_key = f"{title}_{subtitle}_{color1}_{color2}"
    if cache_key in _BANNER_CACHE:
        out = io.BytesIO(_BANNER_CACHE[cache_key])
        out.name = "banner.jpg"
        return out
        
    width, height = 800, 300
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    
    # Create horizontal gradient
    c1 = tuple(int(color1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    c2 = tuple(int(color2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    for x in range(width):
        r = int(c1[0] + (c2[0] - c1[0]) * (x / width))
        g = int(c1[1] + (c2[1] - c1[1]) * (x / width))
        b = int(c1[2] + (c2[2] - c1[2]) * (x / width))
        draw.line([(x, 0), (x, height)], fill=(r, g, b))
        
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()

    # Draw title
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_w) / 2, 100), title, fill="white", font=font_title)
    
    # Draw subtitle
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text(((width - sub_w) / 2, 190), subtitle, fill="#f0f0f0", font=font_subtitle)
    
    # Save to BytesIO
    out = io.BytesIO()
    out.name = "banner.jpg"
    image.save(out, "JPEG", quality=90)
    
    _BANNER_CACHE[cache_key] = out.getvalue()
    
    out.seek(0)
    return out

from .. import loader
@loader.tds
class PillowBannersMod(loader.Module):
    """Генерирует красивые градиентные баннеры для системных команд с помощью Pillow"""
    strings = {"name": "PillowBanners"}