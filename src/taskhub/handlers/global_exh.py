import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from taskhub.core.messages import ErrorMessage

logger = logging.getLogger("taskhub.handlers")


async def global_exception_handler(request: Request, ex: Exception):
    logger.error(f"Lỗi hệ thống không xác định: {request.url.path}: {ex}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "detail": ErrorMessage.INTERNAL_SERVER_ERROR,
            "meta": None,
        },
    )
