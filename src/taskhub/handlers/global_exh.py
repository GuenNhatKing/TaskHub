import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("taskhub.handlers")


async def global_exception_handler(request: Request, ex: Exception):
    logger.error(f"Lỗi hệ thống không xác định: {request.url.path}: {ex}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "detail": "Đã có lỗi xảy ra từ hệ thống. Vui lòng thử lại sau hoặc liên hệ Admin.",
            "meta": None,
        },
    )
