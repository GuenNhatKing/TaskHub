from fastapi import Request, status
from fastapi.responses import JSONResponse

from taskhub.exceptions import BaseBusinessException


async def base_business_exception_handler(request: Request, ex: BaseBusinessException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": "LOGIC_ERROR",
            "detail": ex.message,
            "meta": getattr(ex, "meta", None),
        },
    )
