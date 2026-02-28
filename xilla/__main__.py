import sys
import os
import asyncio

if __package__ != 'xilla':
    print("🚫 Ошибка: Запускайте как пакет `python3 -m xilla`")
    sys.exit(1)

from xilla.core.client import XillaClient
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

if __name__ == "__main__":
    try:
        XillaClient().run()
    except KeyboardInterrupt:
        pass
