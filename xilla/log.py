class _AiogramExceptionMock(Exception):
    pass
TerminatedByOtherGetUpdates = _AiogramExceptionMock
Unauthorized = _AiogramExceptionMock
BadRequest = _AiogramExceptionMock
MessageIdInvalid = _AiogramExceptionMock
MessageNotModified = _AiogramExceptionMock
RetryAfter = _AiogramExceptionMock
NetworkError = _AiogramExceptionMock
import asyncio
import inspect
import io
import linecache
import logging
import re
import sys
import traceback
import typing
from logging.handlers import RotatingFileHandler
import hikkatl
from . import utils
from .tl_cache import CustomTelegramClient
from .types import BotInlineCall, Module
old = linecache.getlines

def getlines(filename: str, module_globals=None) -> str:
    try:
        if filename.startswith('<') and filename.endswith('>'):
            module = filename[1:-1].split(maxsplit=1)[-1]
            if (module.startswith('xilla.modules') or module.startswith('dragon.modules')) and module in sys.modules:
                return list(map(lambda x: f'{x}\n', sys.modules[module].__loader__.get_source().splitlines()))
    except Exception:
        logging.debug("Can't get lines for %s", filename, exc_info=True)
    return old(filename, module_globals)
linecache.getlines = getlines

def override_text(exception: Exception) -> typing.Optional[str]:
    if isinstance(exception, NetworkError):
        return '✈️ <b>You have problems with internet connection on your server.</b>'
    return None

class XillaException:

    def __init__(self, message: str, full_stack: str, sysinfo: typing.Optional[typing.Tuple[object, Exception, traceback.TracebackException]]=None):
        self.message = message
        self.full_stack = full_stack
        self.sysinfo = sysinfo
        self.debug_url = None

    @classmethod
    def from_exc_info(cls, exc_type: object, exc_value: Exception, tb: traceback.TracebackException, stack: typing.Optional[typing.List[inspect.FrameInfo]]=None, comment: typing.Optional[typing.Any]=None) -> 'XillaException':

        def to_hashable(dictionary: dict) -> dict:
            dictionary = dictionary.copy()
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    dictionary[key] = to_hashable(value)
                else:
                    try:
                        if getattr(getattr(value, '__class__', None), '__name__', None) == 'Database':
                            dictionary[key] = '<Database>'
                        elif isinstance(value, (hikkatl.TelegramClient, CustomTelegramClient)):
                            dictionary[key] = f'<{value.__class__.__name__}>'
                        elif len(str(value)) > 512:
                            dictionary[key] = f'{str(value)[:512]}...'
                        else:
                            dictionary[key] = str(value)
                    except Exception:
                        dictionary[key] = f'<{value.__class__.__name__}>'
            return dictionary
        full_traceback = traceback.format_exc().replace('Traceback (most recent call last):\n', '')
        line_regex = re.compile('  File "(.*?)", line ([0-9]+), in (.+)')

        def format_line(line: str) -> str:
            filename_, lineno_, name_ = line_regex.search(line).groups()
            return f'👉 <code>{utils.escape_html(filename_)}:{lineno_}</code> <b>in</b> <code>{utils.escape_html(name_)}</code>'
        filename, lineno, name = next((line_regex.search(line).groups() for line in reversed(full_traceback.splitlines()) if line_regex.search(line)), (None, None, None))
        full_traceback = '\n'.join([format_line(line) if line_regex.search(line) else f'<code>{utils.escape_html(line)}</code>' for line in full_traceback.splitlines()])
        caller = utils.find_caller(stack or inspect.stack())
        return cls(message=override_text(exc_value) or '{}<b>🎯 Source:</b> <code>{}:{}</code><b> in </b><code>{}</code>\n<b>❓ Error:</b> <code>{}</code>{}'.format('🔮 <b>Cause: method </b><code>{}</code><b> of </b><code>{}</code>\n\n'.format(utils.escape_html(caller.__name__), utils.escape_html(caller.__self__.__class__.__name__)) if caller and hasattr(caller, '__self__') and hasattr(caller, '__name__') else '', utils.escape_html(filename), lineno, utils.escape_html(name), utils.escape_html(''.join(traceback.format_exception_only(exc_type, exc_value)).strip()), f'\n💭 <b>Message:</b> <code>{utils.escape_html(str(comment))}</code>' if comment else ''), full_stack=full_traceback, sysinfo=(exc_type, exc_value, tb))

class TelegramLogsHandler(logging.Handler):

    def __init__(self, targets: list, capacity: int):
        super().__init__(0)
        self.buffer = []
        self.handledbuffer = []
        self._queue = []
        self._mods = {}
        self.tg_buff = []
        self.force_send_all = False
        self.tg_level = 20
        self.ignore_common = False
        self.web_debugger = None
        self.targets = targets
        self.capacity = capacity
        self.lvl = logging.NOTSET
        self._send_lock = asyncio.Lock()

    def install_tg_log(self, mod: Module):
        if getattr(self, '_task', False):
            self._task.cancel()
        self._mods[mod.tg_id] = mod
        if mod.db.get(__name__, 'debugger', False):
            self.web_debugger = WebDebugger()
        self._task = asyncio.ensure_future(self.queue_poller())

    async def queue_poller(self):
        while True:
            await self.sender()
            await asyncio.sleep(3)

    def setLevel(self, level: int):
        self.lvl = level

    def dump(self):
        return self.handledbuffer + self.buffer

    def dumps(self, lvl: int=0, client_id: typing.Optional[int]=None) -> typing.List[str]:
        return [self.targets[0].format(record) for record in self.buffer + self.handledbuffer if record.levelno >= lvl and (not record.xilla_caller or client_id == record.xilla_caller)]

    async def _show_full_trace(self, call, bot, item):
        pass

    def emit(self, record: logging.LogRecord):
        try:
            caller = next((frame_info.frame.f_locals['_xilla_client_id_logging_tag'] for frame_info in inspect.stack() if isinstance(getattr(getattr(frame_info, 'frame', None), 'f_locals', {}).get('_xilla_client_id_logging_tag'), int)), False)
            if not isinstance(caller, int):
                caller = None
        except Exception:
            caller = None
        record.xilla_caller = caller
        if record.levelno >= self.tg_level:
            if record.exc_info:
                exc = XillaException.from_exc_info(*record.exc_info, stack=record.__dict__.get('stack', None), comment=record.msg % record.args)
                if not self.ignore_common or all((field not in exc.message for field in ['InputPeerEmpty() does not have any entity type', 'https://docs.telethon.dev/en/stable/concepts/entities.html'])):
                    self.tg_buff += [(exc, caller)]
            else:
                self.tg_buff += [(_tg_formatter.format(record), caller)]
        if len(self.buffer) + len(self.handledbuffer) >= self.capacity:
            if self.handledbuffer:
                del self.handledbuffer[0]
            else:
                del self.buffer[0]
        self.buffer.append(record)
        if record.levelno >= self.lvl >= 0:
            self.acquire()
            try:
                for precord in self.buffer:
                    for target in self.targets:
                        if record.levelno >= target.level:
                            target.handle(precord)
                self.handledbuffer = self.handledbuffer[-(self.capacity - len(self.buffer)):] + self.buffer
                self.buffer = []
            finally:
                self.release()
_main_formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', style='%')
_tg_formatter = logging.Formatter(fmt='[%(levelname)s] %(name)s: %(message)s\n', datefmt=None, style='%')
rotating_handler = RotatingFileHandler(filename='xilla.log', mode='a', maxBytes=10 * 1024 * 1024, backupCount=1, encoding='utf-8', delay=0)
rotating_handler.setFormatter(_main_formatter)

def init():
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(_main_formatter)
    logging.getLogger().handlers = []
    logging.getLogger().addHandler(TelegramLogsHandler((handler, rotating_handler), 7000))
    logging.getLogger().setLevel(logging.NOTSET)
    logging.getLogger('hikkatl').setLevel(logging.WARNING)
    logging.getLogger('hikkapyro').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.captureWarnings(True)