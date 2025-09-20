from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar, Union
from .metadata import ErrorMetadata
from .spec import (
    ErrorSpec,
    BadRequestErrorSpec,
    UnauthorizedErrorSpec,
    ForbiddenErrorSpec,
    NotFoundErrorSpec,
    MethodNotAllowedErrorSpec,
    ConflictErrorSpec,
    UnprocessableEntityErrorSpec,
    TooManyRequestsErrorSpec,
    InternalServerErrorSpec,
    DatabaseErrorSpec,
    NotImplementedErrorSpec,
    BadGatewayErrorSpec,
    ServiceUnavailableErrorSpec,
)


class Error(
    ErrorMetadata,
    ErrorSpec,
):
    pass


class BadRequestError(BadRequestErrorSpec, Error):
    pass


class UnauthorizedError(UnauthorizedErrorSpec, Error):
    pass


class ForbiddenError(ForbiddenErrorSpec, Error):
    pass


class NotFoundError(NotFoundErrorSpec, Error):
    pass


class MethodNotAllowedError(MethodNotAllowedErrorSpec, Error):
    pass


class ConflictError(ConflictErrorSpec, Error):
    pass


class UnprocessableEntityError(UnprocessableEntityErrorSpec, Error):
    pass


class TooManyRequestsError(TooManyRequestsErrorSpec, Error):
    pass


class InternalServerError(InternalServerErrorSpec, Error):
    pass


class DatabaseError(DatabaseErrorSpec, InternalServerError):
    pass


class NotImplementedError(NotImplementedErrorSpec, Error):
    pass


class BadGatewayError(BadGatewayErrorSpec, Error):
    pass


class ServiceUnavailableError(ServiceUnavailableErrorSpec, Error):
    pass


AllError = Union[
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    MethodNotAllowedError,
    ConflictError,
    UnprocessableEntityError,
    TooManyRequestsError,
    InternalServerError,
    DatabaseError,
    NotImplementedError,
    BadGatewayError,
    ServiceUnavailableError,
]
ErrorT = TypeVar("ErrorT", bound=AllError)
OptionalErrorT = TypeVar("OptionalErrorT", bound=Optional[AllError])


class ErrorMixin(BaseModel, Generic[OptionalErrorT]):
    error: OptionalErrorT = Field(..., description="Error.")
