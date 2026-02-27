class web:
    class Request:
        pass
    class Response:
        def __init__(self, status=200, body=None, text=None, headers=None):
            self.status = status
            self.body = body or text or b""
            if isinstance(self.body, str):
                self.body = self.body.encode()
            self.headers = headers or {}
