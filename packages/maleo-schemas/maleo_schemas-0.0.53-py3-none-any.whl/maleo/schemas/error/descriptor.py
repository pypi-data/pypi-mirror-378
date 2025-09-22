from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Union
from typing_extensions import Annotated
from maleo.mixins.general import Descriptor
from .enums import Code as ErrorCode


class ErrorDescriptor(Descriptor[ErrorCode]):
    code: Annotated[ErrorCode, Field(..., description="Error's code")] = (
        ErrorCode.INTERNAL_SERVER_ERROR
    )
    message: Annotated[str, Field("Error", description="Error's message")] = "Error"
    description: Annotated[
        str, Field("An error occurred.", description="Error's description")
    ] = "An error occurred."


ErrorDescriptorT = TypeVar("ErrorDescriptorT", bound=ErrorDescriptor)


class ErrorDescriptorMixin(BaseModel, Generic[ErrorDescriptorT]):
    descriptor: ErrorDescriptorT = Field(..., description="Error's Descriptor")


class BadRequestErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.BAD_REQUEST
    message: str = "Bad Request"
    description: str = "Bad/Unexpected parameters given."


class UnauthorizedErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.UNAUTHORIZED
    message: str = "Unauthorized"
    description: str = "Authentication is required or invalid."


class ForbiddenErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.FORBIDDEN
    message: str = "Forbidden"
    description: str = "Insufficient permission found."


class NotFoundErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.NOT_FOUND
    message: str = "Not Found"
    description: str = "The requested resource could not be found."


class MethodNotAllowedErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.METHOD_NOT_ALLOWED
    message: str = "Method Not Allowed"
    description: str = "The HTTP method is not supported for this resource."


class ConflictErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.CONFLICT
    message: str = "Conflict"
    description: str = "Failed processing request due to conflicting state."


class UnprocessableEntityErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.UNPROCESSABLE_ENTITY
    message: str = "Unprocessable Entity"
    description: str = "The request was well-formed but could not be processed."


class TooManyRequestsErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.TOO_MANY_REQUESTS
    message: str = "Too Many Requests"
    description: str = "You have sent too many requests in a given time frame."


class InternalServerErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR
    message: str = "Internal Server Error"
    description: str = "An unexpected error occurred on the server."


class NotImplementedErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.NOT_IMPLEMENTED
    message: str = "Not Implemented"
    description: str = "This functionality is not supported by the server."


class BadGatewayErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.BAD_GATEWAY
    message: str = "Bad Gateway"
    description: str = (
        "The server received an invalid response from an upstream server."
    )


class ServiceUnavailableErrorDescriptor(ErrorDescriptor):
    code: ErrorCode = ErrorCode.SERVICE_UNAVAILABLE
    message: str = "Service Unavailable"
    description: str = "The server is temporarily unable to handle the request."


AnyErrorDescriptor = Union[
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
]
