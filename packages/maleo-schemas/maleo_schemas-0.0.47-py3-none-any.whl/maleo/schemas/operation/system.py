from typing import Generic, Literal, Optional
from maleo.mixins.general import SuccessT
from maleo.security.authentication import OptionalAllAuthenticationT
from maleo.security.authorization import AuthorizationT
from maleo.security.impersonation import Impersonation
from ..contexts.request import RequestContext
from ..error import (
    OptionalErrorT,
    ErrorT,
)
from ..response import ResponseT, ErrorResponseT, SuccessResponseT
from .action.system import SystemOperationAction
from .base import BaseOperation
from .enums import OperationType


class SystemOperation(
    BaseOperation[
        SystemOperationAction,
        None,
        SuccessT,
        OptionalErrorT,
        Optional[RequestContext],
        OptionalAllAuthenticationT,
        AuthorizationT,
        Optional[Impersonation],
        ResponseT,
        None,
    ],
    Generic[
        SuccessT,
        OptionalErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.SYSTEM
    resource: None = None
    response_context: None = None


class FailedSystemOperation(
    SystemOperation[
        Literal[False],
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
    Generic[ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT],
):
    success: Literal[False] = False


class SuccessfulSystemOperation(
    SystemOperation[
        Literal[True],
        None,
        OptionalAllAuthenticationT,
        AuthorizationT,
        SuccessResponseT,
    ],
    Generic[OptionalAllAuthenticationT, AuthorizationT, SuccessResponseT],
):
    success: Literal[True] = True
    error: None = None
