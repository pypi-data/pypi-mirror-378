import logging
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from maleo.logging.enums import Level, LoggerType
from ..error.constants import ERROR_CODE_STATUS_CODE_MAP
from ..error import AnyErrorT
from ..error.enums import Code as ErrorCode
from ..response import (
    ErrorResponseT,
    UnauthorizedResponse,
    UnprocessableEntityResponse,
    InternalServerErrorResponse,
    ErrorFactory as ErrorResponseFactory,
)
from maleo.security.authentication import OptionalAnyAuthenticationT
from maleo.security.authorization import OptionalAuthorizationT
from .exc import MaleoException


def authentication_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        content=UnauthorizedResponse(
            other={
                "exc_type": type(exc).__name__,
                "exc_data": {
                    "message": str(exc),
                    "args": exc.args,
                },
            }
        ).model_dump(mode="json"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def general_exception_handler(request: Request, exc: Exception):
    other = {
        "exc_type": type(exc).__name__,
        "exc_data": {
            "message": str(exc),
            "args": exc.args,
        },
    }

    # Get the first arg as a potential ErrorCode
    code = exc.args[0] if exc.args else None

    if isinstance(code, ErrorCode):
        error_code = code
    elif isinstance(code, str) and code in ErrorCode:
        error_code = ErrorCode[code]
    else:
        error_code = None

    if error_code is not None:
        status_code = ERROR_CODE_STATUS_CODE_MAP.get(error_code, None)

        if status_code is not None:
            response_cls = ErrorResponseFactory.cls_from_code(status_code)
            return JSONResponse(
                content=response_cls(other=other).model_dump(mode="json"),
                status_code=status_code,
            )

    return JSONResponse(
        content=InternalServerErrorResponse(other=other).model_dump(mode="json"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        content=UnprocessableEntityResponse(
            other=jsonable_encoder(exc.errors())
        ).model_dump(mode="json"),
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        content=UnprocessableEntityResponse(other=exc.errors()).model_dump(mode="json"),
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    other = {
        "exc_type": type(exc).__name__,
        "exc_data": {
            "status_code": exc.status_code,
            "detail": exc.detail,
            "headers": exc.headers,
        },
    }

    response_cls = ErrorResponseFactory.cls_from_code(exc.status_code)
    return JSONResponse(
        content=response_cls(other=other).model_dump(mode="json"),
        status_code=exc.status_code,
    )


async def maleo_exception_handler(
    request: Request,
    exc: MaleoException[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ],
):
    logger = logging.getLogger(
        f"{exc.service_context.environment} - {exc.service_context.key} - {LoggerType.EXCEPTION}"
    )

    exc.operation.log(logger, Level.ERROR)

    return JSONResponse(
        content=exc.response.model_dump(mode="json"),
        status_code=exc.error.spec.status_code,
    )
