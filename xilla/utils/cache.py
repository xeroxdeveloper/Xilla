import os
import hashlib
import aiohttp
import aiofiles

class MediaCache:
    """Интеллектуальное кэширование стикеров и медиа для экономии трафика"""
    def __init__(self):
        self.cache_dir = os.path.join(os.getcwd(), "cache")

    def get_path(self, identifier):
        hash_id = hashlib.md5(str(identifier).encode()).hexdigest()
        path = os.path.join(self.cache_dir, hash_id)
        if os.path.exists(path):
            return path
        return None
        
    def generate_path(self, identifier, ext=""):
        hash_id = hashlib.md5(str(identifier).encode()).hexdigest()
        return os.path.join(self.cache_dir, hash_id + ext)

    async def fetch_cached(self, url, ext=""):
        cached = self.get_path(url)
        if cached:
            return cached
            
        path = self.generate_path(url, ext)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    async with aiofiles.open(path, 'wb') as f:
                        await f.write(data)
                    return path
        return None
