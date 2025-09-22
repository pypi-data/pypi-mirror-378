from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar, Union
from typing_extensions import Annotated
from .descriptor import (
    BadRequestErrorDescriptor,
    UnauthorizedErrorDescriptor,
    ForbiddenErrorDescriptor,
    NotFoundErrorDescriptor,
    MethodNotAllowedErrorDescriptor,
    ConflictErrorDescriptor,
    UnprocessableEntityErrorDescriptor,
    TooManyRequestsErrorDescriptor,
    InternalServerErrorDescriptor,
    NotImplementedErrorDescriptor,
    BadGatewayErrorDescriptor,
    ServiceUnavailableErrorDescriptor,
    ErrorDescriptorT,
    ErrorDescriptorMixin,
)
from .metadata import ErrorMetadataMixin
from .spec import (
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
    ErrorSpecT,
    ErrorSpecMixin,
)


class Error(
    ErrorMetadataMixin,
    ErrorDescriptorMixin[ErrorDescriptorT],
    ErrorSpecMixin[ErrorSpecT],
    Generic[ErrorSpecT, ErrorDescriptorT],
):
    pass


class BadRequestError(Error[BadRequestErrorSpec, BadRequestErrorDescriptor]):
    spec: Annotated[
        BadRequestErrorSpec, Field(..., description="Bad request error spec")
    ] = BadRequestErrorSpec()
    descriptor: Annotated[
        BadRequestErrorDescriptor,
        Field(..., description="Bad request error descriptor"),
    ] = BadRequestErrorDescriptor()


class UnauthorizedError(Error[UnauthorizedErrorSpec, UnauthorizedErrorDescriptor]):
    spec: Annotated[
        UnauthorizedErrorSpec, Field(..., description="Unauthorized error spec")
    ] = UnauthorizedErrorSpec()
    descriptor: Annotated[
        UnauthorizedErrorDescriptor,
        Field(..., description="Unauthorized error descriptor"),
    ] = UnauthorizedErrorDescriptor()


class ForbiddenError(Error[ForbiddenErrorSpec, ForbiddenErrorDescriptor]):
    spec: Annotated[
        ForbiddenErrorSpec, Field(..., description="Forbidden error spec")
    ] = ForbiddenErrorSpec()
    descriptor: Annotated[
        ForbiddenErrorDescriptor, Field(..., description="Forbidden error descriptor")
    ] = ForbiddenErrorDescriptor()


class NotFoundError(Error[NotFoundErrorSpec, NotFoundErrorDescriptor]):
    spec: Annotated[
        NotFoundErrorSpec, Field(..., description="Not found error spec")
    ] = NotFoundErrorSpec()
    descriptor: Annotated[
        NotFoundErrorDescriptor, Field(..., description="Not found error descriptor")
    ] = NotFoundErrorDescriptor()


class MethodNotAllowedError(
    Error[MethodNotAllowedErrorSpec, MethodNotAllowedErrorDescriptor]
):
    spec: Annotated[
        MethodNotAllowedErrorSpec,
        Field(..., description="Method not allowed error spec"),
    ] = MethodNotAllowedErrorSpec()
    descriptor: Annotated[
        MethodNotAllowedErrorDescriptor,
        Field(..., description="Method not allowed error descriptor"),
    ] = MethodNotAllowedErrorDescriptor()


class ConflictError(Error[ConflictErrorSpec, ConflictErrorDescriptor]):
    spec: Annotated[
        ConflictErrorSpec, Field(..., description="Conflict error spec")
    ] = ConflictErrorSpec()
    descriptor: Annotated[
        ConflictErrorDescriptor, Field(..., description="Conflict error descriptor")
    ] = ConflictErrorDescriptor()


class UnprocessableEntityError(
    Error[UnprocessableEntityErrorSpec, UnprocessableEntityErrorDescriptor]
):
    spec: Annotated[
        UnprocessableEntityErrorSpec,
        Field(..., description="Unprocessable entity error spec"),
    ] = UnprocessableEntityErrorSpec()
    descriptor: Annotated[
        UnprocessableEntityErrorDescriptor,
        Field(..., description="Unprocessable entity error descriptor"),
    ] = UnprocessableEntityErrorDescriptor()


class TooManyRequestsError(
    Error[TooManyRequestsErrorSpec, TooManyRequestsErrorDescriptor]
):
    spec: Annotated[
        TooManyRequestsErrorSpec, Field(..., description="Too many requests error spec")
    ] = TooManyRequestsErrorSpec()
    descriptor: Annotated[
        TooManyRequestsErrorDescriptor,
        Field(..., description="Too many requests error descriptor"),
    ] = TooManyRequestsErrorDescriptor()


class InternalServerError(
    Error[InternalServerErrorSpec, InternalServerErrorDescriptor]
):
    spec: Annotated[
        InternalServerErrorSpec, Field(..., description="Internal server error spec")
    ] = InternalServerErrorSpec()
    descriptor: Annotated[
        InternalServerErrorDescriptor,
        Field(..., description="Internal server error descriptor"),
    ] = InternalServerErrorDescriptor()


class NotImplementedError(
    Error[NotImplementedErrorSpec, NotImplementedErrorDescriptor]
):
    spec: Annotated[
        NotImplementedErrorSpec, Field(..., description="Not implemented error spec")
    ] = NotImplementedErrorSpec()
    descriptor: Annotated[
        NotImplementedErrorDescriptor,
        Field(..., description="Not implemented error descriptor"),
    ] = NotImplementedErrorDescriptor()


class BadGatewayError(Error[BadGatewayErrorSpec, BadGatewayErrorDescriptor]):
    spec: Annotated[
        BadGatewayErrorSpec, Field(..., description="Bad gateway error spec")
    ] = BadGatewayErrorSpec()
    descriptor: Annotated[
        BadGatewayErrorDescriptor,
        Field(..., description="Bad gateway error descriptor"),
    ] = BadGatewayErrorDescriptor()


class ServiceUnavailableError(
    Error[ServiceUnavailableErrorSpec, ServiceUnavailableErrorDescriptor]
):
    spec: Annotated[
        ServiceUnavailableErrorSpec,
        Field(..., description="Service unavailable error spec"),
    ] = ServiceUnavailableErrorSpec()
    descriptor: Annotated[
        ServiceUnavailableErrorDescriptor,
        Field(..., description="Service unavailable error descriptor"),
    ] = ServiceUnavailableErrorDescriptor()


AnyError = Union[
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    MethodNotAllowedError,
    ConflictError,
    UnprocessableEntityError,
    TooManyRequestsError,
    InternalServerError,
    NotImplementedError,
    BadGatewayError,
    ServiceUnavailableError,
]
AnyErrorT = TypeVar("AnyErrorT", bound=AnyError)
OptionalAnyError = Optional[AnyError]
OptionalAnyErrorT = TypeVar("OptionalAnyErrorT", bound=OptionalAnyError)


class ErrorMixin(BaseModel, Generic[OptionalAnyErrorT]):
    error: OptionalAnyErrorT = Field(..., description="Error.")
