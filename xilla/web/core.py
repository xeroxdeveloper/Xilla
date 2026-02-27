"""Responsible for web init and mandatory ops"""
import asyncio
import contextlib
import inspect
import logging
import os
import subprocess
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..database import Database
from ..loader import Modules
from ..tl_cache import CustomTelegramClient
from . import proxypass, root

logger = logging.getLogger(__name__)

class Web(root.Web):
    def __init__(self, **kwargs):
        self.runner = None
        self.port = None
        self.running = asyncio.Event()
        self.ready = asyncio.Event()
        self.client_data = {}
        
        self.app = FastAPI(title="Xilla Web Config")
        self.proxypasser = proxypass.ProxyPasser()
        
        self.templates = Jinja2Templates(directory="web-resources")
        # Expose app for root.py compatibility or just adapt methods
        self.app.mount("/static", StaticFiles(directory="web-resources/static"), name="static")
        
        super().__init__(**kwargs)
        
        # Add root.py routes natively (adapter pattern for FastAPI)
        self.app.get("/")(self._wrap_get(self.root))
        self.app.put("/set_api")(self._wrap_post(self.set_tg_api))
        self.app.post("/send_tg_code")(self._wrap_post(self.send_tg_code))
        self.app.post("/check_session")(self._wrap_post(self.check_session))
        self.app.post("/web_auth")(self._wrap_post(self.web_auth))
        self.app.post("/tg_code")(self._wrap_post(self.tg_code))
        self.app.post("/finish_login")(self._wrap_post(self.finish_login))
        self.app.post("/custom_bot")(self._wrap_post(self.custom_bot))
        self.app.post("/init_qr_login")(self._wrap_post(self.init_qr_login))
        self.app.post("/get_qr_url")(self._wrap_post(self.get_qr_url))
        self.app.post("/qr_2fa")(self._wrap_post(self.qr_2fa))
        self.app.post("/can_add")(self._wrap_post(self.can_add))
        self.app.get("/favicon.ico")(self.favicon)
        
    def _wrap_get(self, func):
        async def wrapper(request: Request):
            res = await func(request)
            if isinstance(res, dict):
                return self.templates.TemplateResponse("root.jinja2", {"request": request, **res})
            if hasattr(res, 'text') and res.text:
                from fastapi.responses import HTMLResponse
                return HTMLResponse(content=res.text, status_code=getattr(res, 'status', 200))
            if hasattr(res, 'body') and res.body:
                from fastapi.responses import PlainTextResponse
                return PlainTextResponse(content=res.body, status_code=getattr(res, 'status', 200))
            if hasattr(res, 'status'):
                from fastapi import Response as FAResponse
                return FAResponse(status_code=res.status)
            return res
        return wrapper

    def _wrap_post(self, func):
        async def wrapper(request: Request):
            class MockRequest:
                def __init__(self, req):
                    self.req = req
                async def post(self):
                    return await self.req.form()
                async def json(self):
                    return await self.req.json()
                @property
                def remote(self):
                    return self.req.client.host if self.req.client else '127.0.0.1'
                @property
                def cookies(self):
                    return self.req.cookies
            res = await func(MockRequest(request))
            from fastapi.responses import PlainTextResponse, Response as FAResponse
            status = getattr(res, 'status', 200)
            if hasattr(res, 'text') and res.text:
                return PlainTextResponse(content=res.text, status_code=status)
            if hasattr(res, 'body') and res.body:
                body = res.body.decode() if isinstance(res.body, bytes) else res.body
                return PlainTextResponse(content=body, status_code=status)
            return FAResponse(status_code=status)
        return wrapper

    async def start_if_ready(self, total_count: int, port: int, proxy_pass: bool = False):
        if total_count <= len(self.client_data):
            if not self.running.is_set():
                await self.start(port, proxy_pass=proxy_pass)
            self.ready.set()

    async def get_url(self, proxy_pass: bool) -> str:
        url = None
        if all(option in os.environ for option in {"LAVHOST", "USER", "SERVER"}):
            return f"https://{os.environ['USER']}.{os.environ['SERVER']}.lavhost.ml"
        if proxy_pass:
            with contextlib.suppress(Exception):
                url = await asyncio.wait_for(
                    self.proxypasser.get_url(self.port), timeout=10
                )
        if not url:
            ip = "127.0.0.1" if "DOCKER" not in os.environ else subprocess.run(
                    ["hostname", "-i"], stdout=subprocess.PIPE, check=True
                ).stdout.decode("utf-8").strip()
            url = f"http://{ip}:{self.port}"
        self.url = url
        return url

    async def start(self, port: int, proxy_pass: bool = False):
        self.port = int(os.environ.get("PORT", port))
        
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port, log_level="warning")
        self.runner = uvicorn.Server(config)
        
        # Uvicorn blocks by default, we need to run it as an asyncio task
        asyncio.create_task(self.runner.serve())
        
        await asyncio.sleep(1) # wait for boot
        await self.get_url(proxy_pass)
        self.running.set()

    async def stop(self):
        if self.runner:
            self.runner.should_exit = True
        self.running.clear()
        self.ready.clear()

    async def add_loader(self, client: CustomTelegramClient, loader: Modules, db: Database):
        self.client_data[client.tg_id] = (loader, client, db)

    @staticmethod
    async def favicon():
        return RedirectResponse(url="https://i.imgur.com/IRAiWBo.jpeg")
