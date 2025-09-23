from typing import Generic, Literal
from maleo.mixins.general import SuccessT
from maleo.security.authentication import OptionalAnyAuthenticationT
from maleo.security.authorization import OptionalAuthorizationT
from ..connection import OptionalConnectionContext
from ..error import (
    OptionalAnyErrorT,
    AnyErrorT,
)
from ..response import ResponseT, ErrorResponseT, SuccessResponseT
from .action.websocket import WebSocketOperationAction
from .base import BaseOperation
from .enums import OperationType


class WebSocketOperation(
    BaseOperation[
        WebSocketOperationAction,
        None,
        SuccessT,
        OptionalAnyErrorT,
        OptionalConnectionContext,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ResponseT,
        None,
    ],
    Generic[
        SuccessT,
        OptionalAnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.WEBSOCKET
    resource: None = None
    response_context: None = None


class FailedWebSocketOperation(
    WebSocketOperation[
        Literal[False],
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ],
):
    success: Literal[False] = False


class SuccessfulWebSocketOperation(
    WebSocketOperation[
        Literal[True],
        None,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        SuccessResponseT,
    ],
    Generic[OptionalAnyAuthenticationT, OptionalAuthorizationT, SuccessResponseT],
):
    success: Literal[True] = True
    error: None = None
