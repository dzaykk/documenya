class AppException(Exception):
    status_code: int = 400
    detail: str = "Application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)