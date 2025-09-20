from typing import Generic, Literal, Optional, Union, overload
from uuid import UUID
from maleo.mixins.general import SuccessT
from maleo.security.authentication import OptionalAllAuthenticationT
from maleo.security.authorization import AuthorizationT
from maleo.security.impersonation import OptionalImpersonation
from ..contexts.request import RequestContext
from ..contexts.response import ResponseContext
from ..contexts.service import ServiceContext
from ..error import OptionalErrorT, ErrorT
from .action.resource import (
    ResourceOperationActionT,
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    AllResourceOperationAction,
    Factory as ResourceOperationActionFactory,
)
from .base import BaseOperation
from .context import Context as OperationContext
from .enums import (
    OperationType,
    ResourceOperationType,
    ResourceOperationCreateType,
    ResourceOperationUpdateType,
    ResourceOperationDataUpdateType,
    ResourceOperationStatusUpdateType,
)
from .mixins import Timestamp


class RequestOperation(
    BaseOperation[
        ResourceOperationActionT,
        None,
        SuccessT,
        OptionalErrorT,
        RequestContext,
        OptionalAllAuthenticationT,
        AuthorizationT,
        OptionalImpersonation,
        bytes,
        ResponseContext,
    ],
    Generic[
        ResourceOperationActionT,
        SuccessT,
        OptionalErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    type: OperationType = OperationType.REQUEST
    resource: None = None


class FailedRequestOperation(
    RequestOperation[
        ResourceOperationActionT,
        Literal[False],
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ResourceOperationActionT,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    success: Literal[False] = False
    summary: str = "Failed processing request"


class CreateFailedRequestOperation(
    FailedRequestOperation[
        CreateResourceOperationAction,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    pass


class ReadFailedRequestOperation(
    FailedRequestOperation[
        ReadResourceOperationAction,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    pass


class UpdateFailedRequestOperation(
    FailedRequestOperation[
        UpdateResourceOperationAction,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    pass


class DeleteFailedRequestOperation(
    FailedRequestOperation[
        DeleteResourceOperationAction,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    pass


class SuccessfulRequestOperation(
    RequestOperation[
        ResourceOperationActionT,
        Literal[True],
        None,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ResourceOperationActionT,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    success: Literal[True] = True
    error: None = None
    summary: str = "Successfully processed request"


class CreateSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        CreateResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    pass


class ReadSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        ReadResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    pass


class UpdateSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        UpdateResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    pass


class DeleteSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        DeleteResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
    ],
):
    pass


class Factory:
    @overload
    @staticmethod
    def generate_failed(
        action: CreateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> CreateFailedRequestOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: ReadResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> ReadFailedRequestOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: UpdateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> UpdateFailedRequestOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: DeleteResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> DeleteFailedRequestOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: AllResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> Union[
        CreateFailedRequestOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT
        ],
        ReadFailedRequestOperation[ErrorT, OptionalAllAuthenticationT, AuthorizationT],
        UpdateFailedRequestOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT
        ],
        DeleteFailedRequestOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT
        ],
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.CREATE],
        create_type: Optional[ResourceOperationCreateType] = ...,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> CreateFailedRequestOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.READ],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> ReadFailedRequestOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.UPDATE],
        update_type: Optional[ResourceOperationUpdateType] = ...,
        data_update_type: Optional[ResourceOperationDataUpdateType] = ...,
        status_update_type: Optional[ResourceOperationStatusUpdateType] = ...,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> UpdateFailedRequestOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.DELETE],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> DeleteFailedRequestOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @staticmethod
    def generate_failed(
        action: Optional[AllResourceOperationAction] = None,
        *,
        type_: Optional[ResourceOperationType] = None,
        create_type: Optional[ResourceOperationCreateType] = None,
        update_type: Optional[ResourceOperationUpdateType] = None,
        data_update_type: Optional[ResourceOperationDataUpdateType] = None,
        status_update_type: Optional[ResourceOperationStatusUpdateType] = None,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> Union[
        CreateFailedRequestOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT
        ],
        ReadFailedRequestOperation[ErrorT, OptionalAllAuthenticationT, AuthorizationT],
        UpdateFailedRequestOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT
        ],
        DeleteFailedRequestOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT
        ],
    ]:
        if (action is None and type_ is None) or (
            action is not None and type_ is not None
        ):
            raise ValueError("Only either 'action' or 'type' must be given")

        common_kwargs = {
            "service_context": service_context,
            "id": id,
            "context": context,
            "action": action,
            "timestamp": timestamp,
            "summary": summary,
            "error": error,
            "request_context": request_context,
            "authentication": authentication,
            "authorization": authorization,
            "impersonation": impersonation,
            "response": response,
            "response_context": response_context,
        }

        if action is not None:
            if not isinstance(
                action,
                (
                    CreateResourceOperationAction,
                    ReadResourceOperationAction,
                    UpdateResourceOperationAction,
                    DeleteResourceOperationAction,
                ),
            ):
                raise ValueError(f"Invalid 'action' type: '{type(action)}'")

            if isinstance(action, CreateResourceOperationAction):
                return CreateFailedRequestOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, ReadResourceOperationAction):
                return ReadFailedRequestOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, UpdateResourceOperationAction):
                return UpdateFailedRequestOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, DeleteResourceOperationAction):
                return DeleteFailedRequestOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )

        if type_ is not None:
            if type_ is ResourceOperationType.CREATE:
                action = ResourceOperationActionFactory.generate(
                    type_, create_type=create_type
                )
                return CreateFailedRequestOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.READ:
                action = ResourceOperationActionFactory.generate(type_)
                return ReadFailedRequestOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.UPDATE:
                action = ResourceOperationActionFactory.generate(
                    type_,
                    update_type=update_type,
                    data_update_type=data_update_type,
                    status_update_type=status_update_type,
                )
                return UpdateFailedRequestOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.DELETE:
                action = ResourceOperationActionFactory.generate(type_)
                return DeleteFailedRequestOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            else:
                raise ValueError(f"Invalid type_: {type_}")

        # This should never happen due to initial validation,
        # but type checker needs to see all paths covered
        raise ValueError("Neither 'action' nor 'type' provided")

    @overload
    @staticmethod
    def generate_successful(
        action: CreateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> CreateSuccessfulRequestOperation[
        OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_successful(
        action: ReadResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> ReadSuccessfulRequestOperation[OptionalAllAuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_successful(
        action: UpdateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> UpdateSuccessfulRequestOperation[
        OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_successful(
        action: DeleteResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> DeleteSuccessfulRequestOperation[
        OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_successful(
        *,
        type_: Literal[ResourceOperationType.CREATE],
        create_type: Optional[ResourceOperationCreateType] = ...,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> CreateSuccessfulRequestOperation[
        OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_successful(
        *,
        type_: Literal[ResourceOperationType.READ],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> ReadSuccessfulRequestOperation[OptionalAllAuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_successful(
        *,
        type_: Literal[ResourceOperationType.UPDATE],
        update_type: Optional[ResourceOperationUpdateType] = ...,
        data_update_type: Optional[ResourceOperationDataUpdateType] = ...,
        status_update_type: Optional[ResourceOperationStatusUpdateType] = ...,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> UpdateSuccessfulRequestOperation[
        OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @overload
    @staticmethod
    def generate_successful(
        *,
        type_: Literal[ResourceOperationType.DELETE],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> DeleteSuccessfulRequestOperation[
        OptionalAllAuthenticationT, AuthorizationT
    ]: ...
    @staticmethod
    def generate_successful(
        action: Optional[AllResourceOperationAction] = None,
        *,
        type_: Optional[ResourceOperationType] = None,
        create_type: Optional[ResourceOperationCreateType] = None,
        update_type: Optional[ResourceOperationUpdateType] = None,
        data_update_type: Optional[ResourceOperationDataUpdateType] = None,
        status_update_type: Optional[ResourceOperationStatusUpdateType] = None,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: Timestamp,
        summary: str,
        request_context: RequestContext,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> Union[
        CreateSuccessfulRequestOperation[OptionalAllAuthenticationT, AuthorizationT],
        ReadSuccessfulRequestOperation[OptionalAllAuthenticationT, AuthorizationT],
        UpdateSuccessfulRequestOperation[OptionalAllAuthenticationT, AuthorizationT],
        DeleteSuccessfulRequestOperation[OptionalAllAuthenticationT, AuthorizationT],
    ]:
        if (action is None and type_ is None) or (
            action is not None and type_ is not None
        ):
            raise ValueError("Only either 'action' or 'type' must be given")

        common_kwargs = {
            "service_context": service_context,
            "id": id,
            "context": context,
            "action": action,
            "timestamp": timestamp,
            "summary": summary,
            "request_context": request_context,
            "authentication": authentication,
            "authorization": authorization,
            "impersonation": impersonation,
            "response": response,
            "response_context": response_context,
        }

        if action is not None:
            if not isinstance(
                action,
                (
                    CreateResourceOperationAction,
                    ReadResourceOperationAction,
                    UpdateResourceOperationAction,
                    DeleteResourceOperationAction,
                ),
            ):
                raise ValueError(f"Invalid 'action' type: '{type(action)}'")

            if isinstance(action, CreateResourceOperationAction):
                return CreateSuccessfulRequestOperation[
                    OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, ReadResourceOperationAction):
                return ReadSuccessfulRequestOperation[
                    OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, UpdateResourceOperationAction):
                return UpdateSuccessfulRequestOperation[
                    OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, DeleteResourceOperationAction):
                return DeleteSuccessfulRequestOperation[
                    OptionalAllAuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )

        if type_ is not None:
            if type_ is ResourceOperationType.CREATE:
                action = ResourceOperationActionFactory.generate(
                    type_, create_type=create_type
                )
                return CreateSuccessfulRequestOperation(
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.READ:
                action = ResourceOperationActionFactory.generate(type_)
                return ReadSuccessfulRequestOperation(
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.UPDATE:
                action = ResourceOperationActionFactory.generate(
                    type_,
                    update_type=update_type,
                    data_update_type=data_update_type,
                    status_update_type=status_update_type,
                )
                return UpdateSuccessfulRequestOperation(
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.DELETE:
                action = ResourceOperationActionFactory.generate(type_)
                return DeleteSuccessfulRequestOperation(
                    **common_kwargs,
                    action=action,
                )
            else:
                raise ValueError(f"Invalid type_: {type_}")

        # This should never happen due to initial validation,
        # but type checker needs to see all paths covered
        raise ValueError("Neither 'action' nor 'type' provided")
