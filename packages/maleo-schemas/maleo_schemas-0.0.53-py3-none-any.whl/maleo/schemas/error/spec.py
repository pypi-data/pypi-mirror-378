from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Union
from typing_extensions import Annotated
from maleo.mixins.general import StatusCode
from .enums import ErrorType as ErrorTypeEnum


class ErrorType(BaseModel):
    type: Annotated[ErrorTypeEnum, Field(..., description="Error type")] = (
        ErrorTypeEnum.INTERNAL_SERVER_ERROR
    )


class ErrorSpec(StatusCode, ErrorType):
    status_code: Annotated[
        int, Field(..., description="Status code", ge=100, le=600)
    ] = 500


ErrorSpecT = TypeVar("ErrorSpecT", bound=ErrorSpec)


class ErrorSpecMixin(BaseModel, Generic[ErrorSpecT]):
    spec: ErrorSpecT = Field(..., description="Error's Spec")


class BadRequestErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.BAD_REQUEST
    status_code: int = 400


class UnauthorizedErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.UNAUTHORIZED
    status_code: int = 401


class ForbiddenErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.FORBIDDEN
    status_code: int = 403


class NotFoundErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.NOT_FOUND
    status_code: int = 404


class MethodNotAllowedErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.METHOD_NOT_ALLOWED
    status_code: int = 405


class ConflictErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.CONFLICT
    status_code: int = 409


class UnprocessableEntityErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.UNPROCESSABLE_ENTITY
    status_code: int = 422


class TooManyRequestsErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.TOO_MANY_REQUESTS
    status_code: int = 429


class InternalServerErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.INTERNAL_SERVER_ERROR
    status_code: int = 500


class NotImplementedErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.NOT_IMPLEMENTED
    status_code: int = 501


class BadGatewayErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.BAD_GATEWAY
    status_code: int = 502


class ServiceUnavailableErrorSpec(ErrorSpec):
    type: ErrorTypeEnum = ErrorTypeEnum.SERVICE_UNAVAILABLE
    status_code: int = 503


AnyErrorSpec = Union[
    BadRequestErrorSpec,
    UnauthorizedErrorSpec,
    ForbiddenErrorSpec,
    NotFoundErrorSpec,
    MethodNotAllowedErrorSpec,
    ConflictErrorSpec,
    UnprocessableEntityErrorSpec,
    TooManyRequestsErrorSpec,
    InternalServerErrorSpec,
    NotImplementedErrorSpec,
    BadGatewayErrorSpec,
    ServiceUnavailableErrorSpec,
]
