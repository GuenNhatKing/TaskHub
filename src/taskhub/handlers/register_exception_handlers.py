from fastapi import FastAPI

from taskhub.exceptions import (
    BaseBusinessException,
    EmailExistedException,
    UserNotFoundException,
)

from .base_business_exh import base_business_exception_handler
from .email_existed_exh import email_existed_exception_handler
from .global_exh import global_exception_handler
from .user_not_found_exh import user_not_found_exception_handler


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(EmailExistedException, email_existed_exception_handler)
    app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler)

    app.add_exception_handler(BaseBusinessException, base_business_exception_handler)

    app.add_exception_handler(Exception, global_exception_handler)
