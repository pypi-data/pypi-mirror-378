import logging
import asyncio

#接管 uvicorn 日志
class AsyncLogHandler(logging.Handler):
    def __init__(self, log_writer):
        super().__init__()
        self.log_writer = log_writer
        self.loop = asyncio.get_event_loop()

    def emit(self, record):
        try:
            msg = self.format(record)
            # 在非async环境调用异步写日志，得用loop.create_task或run_coroutine_threadsafe
            asyncio.run_coroutine_threadsafe(self.log_writer.write_log(msg), self.loop)
        except Exception:
            self.handleError(record)