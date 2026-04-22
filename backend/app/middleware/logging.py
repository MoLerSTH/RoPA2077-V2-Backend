# app/middleware/logging.py
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        # คุณสามารถเพิ่ม Logic การบันทึก Log ลง DB ที่นี่ได้ในอนาคต
        response.headers["X-Process-Time"] = str(process_time)
        return response