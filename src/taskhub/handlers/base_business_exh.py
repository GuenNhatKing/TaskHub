from fastapi import Request
from fastapi.responses import JSONResponse

from taskhub.exceptions import BaseBusinessException


async def base_business_exception_handler(request: Request, ex: BaseBusinessException):
    return JSONResponse(
        status_code=ex.status_code,
        content={
            "code": ex.code,
            "detail": ex.message,
            "meta": getattr(ex, "meta", None),
        },
    )
