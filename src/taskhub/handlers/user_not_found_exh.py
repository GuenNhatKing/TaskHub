from fastapi import Request, status
from fastapi.responses import JSONResponse

from taskhub.exceptions import UserNotFoundException


async def user_not_found_exception_handler(request: Request, ex: UserNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"code": "USER_NOT_FOUND", "detail": ex.message, "meta": None},
    )
