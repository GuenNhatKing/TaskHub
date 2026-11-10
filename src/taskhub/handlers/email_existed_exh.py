from fastapi import Request, status
from fastapi.responses import JSONResponse

from taskhub.exceptions import EmailExistedException


async def email_existed_exception_handler(request: Request, ex: EmailExistedException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "code": "EMAIL_ALREADY_EXISTS",
            "detail": ex.message,
            "meta": {"email": ex.email},
        },
    )
