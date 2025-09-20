from typing import Generic, Literal, Optional, Union, overload
from uuid import UUID
from maleo.mixins.general import SuccessT
from maleo.mixins.timestamp import OperationTimestamp
from maleo.security.authentication import AuthenticationT
from maleo.security.authorization import AuthorizationT
from maleo.security.impersonation import Impersonation
from ..contexts.request import RequestContext
from ..contexts.response import ResponseContext
from ..contexts.service import ServiceContext
from ..error import OptionalErrorT, ErrorT
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
from .action.resource import (
    ResourceOperationActionT,
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    AllResourceOperationAction,
    Factory as ResourceOperationActionFactory,
)


class RequestOperation(
    BaseOperation[
        ResourceOperationActionT,
        None,
        SuccessT,
        OptionalErrorT,
        RequestContext,
        AuthenticationT,
        AuthorizationT,
        Optional[Impersonation],
        bytes,
        ResponseContext,
    ],
    Generic[
        ResourceOperationActionT,
        SuccessT,
        OptionalErrorT,
        AuthenticationT,
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
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ResourceOperationActionT,
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
):
    success: Literal[False] = False
    summary: str = "Failed processing request"


class CreateFailedRequestOperation(
    FailedRequestOperation[
        CreateResourceOperationAction,
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
):
    pass


class ReadFailedRequestOperation(
    FailedRequestOperation[
        ReadResourceOperationAction,
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
):
    pass


class UpdateFailedRequestOperation(
    FailedRequestOperation[
        UpdateResourceOperationAction,
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
):
    pass


class DeleteFailedRequestOperation(
    FailedRequestOperation[
        DeleteResourceOperationAction,
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ErrorT,
        AuthenticationT,
        AuthorizationT,
    ],
):
    pass


class SuccessfulRequestOperation(
    RequestOperation[
        ResourceOperationActionT,
        Literal[True],
        None,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        ResourceOperationActionT,
        AuthenticationT,
        AuthorizationT,
    ],
):
    success: Literal[True] = True
    error: None = None
    summary: str = "Successfully processed request"


class CreateSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        CreateResourceOperationAction,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        AuthenticationT,
        AuthorizationT,
    ],
):
    pass


class ReadSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        ReadResourceOperationAction,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        AuthenticationT,
        AuthorizationT,
    ],
):
    pass


class UpdateSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        UpdateResourceOperationAction,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        AuthenticationT,
        AuthorizationT,
    ],
):
    pass


class DeleteSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        DeleteResourceOperationAction,
        AuthenticationT,
        AuthorizationT,
    ],
    Generic[
        AuthenticationT,
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
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> CreateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: ReadResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> ReadFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: UpdateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> UpdateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: DeleteResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> DeleteFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.CREATE],
        create_type: Optional[ResourceOperationCreateType] = ...,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> CreateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.READ],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> ReadFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT]: ...
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
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> UpdateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.DELETE],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> DeleteFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT]: ...
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
        timestamp: OperationTimestamp,
        summary: str,
        error: ErrorT,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> Union[
        CreateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        ReadFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        UpdateFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
        DeleteFailedRequestOperation[ErrorT, AuthenticationT, AuthorizationT],
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
                    ErrorT, AuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, ReadResourceOperationAction):
                return ReadFailedRequestOperation[
                    ErrorT, AuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, UpdateResourceOperationAction):
                return UpdateFailedRequestOperation[
                    ErrorT, AuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, DeleteResourceOperationAction):
                return DeleteFailedRequestOperation[
                    ErrorT, AuthenticationT, AuthorizationT
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
                    ErrorT, AuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.READ:
                action = ResourceOperationActionFactory.generate(type_)
                return ReadFailedRequestOperation[
                    ErrorT, AuthenticationT, AuthorizationT
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
                    ErrorT, AuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.DELETE:
                action = ResourceOperationActionFactory.generate(type_)
                return DeleteFailedRequestOperation[
                    ErrorT, AuthenticationT, AuthorizationT
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
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> CreateSuccessfulRequestOperation[AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_successful(
        action: ReadResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> ReadSuccessfulRequestOperation[AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_successful(
        action: UpdateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> UpdateSuccessfulRequestOperation[AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_successful(
        action: DeleteResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> DeleteSuccessfulRequestOperation[AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_successful(
        *,
        type_: Literal[ResourceOperationType.CREATE],
        create_type: Optional[ResourceOperationCreateType] = ...,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> CreateSuccessfulRequestOperation[AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_successful(
        *,
        type_: Literal[ResourceOperationType.READ],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> ReadSuccessfulRequestOperation[AuthenticationT, AuthorizationT]: ...
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
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> UpdateSuccessfulRequestOperation[AuthenticationT, AuthorizationT]: ...
    @overload
    @staticmethod
    def generate_successful(
        *,
        type_: Literal[ResourceOperationType.DELETE],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> DeleteSuccessfulRequestOperation[AuthenticationT, AuthorizationT]: ...
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
        timestamp: OperationTimestamp,
        summary: str,
        request_context: RequestContext,
        authentication: AuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: bytes,
        response_context: ResponseContext,
    ) -> Union[
        CreateSuccessfulRequestOperation[AuthenticationT, AuthorizationT],
        ReadSuccessfulRequestOperation[AuthenticationT, AuthorizationT],
        UpdateSuccessfulRequestOperation[AuthenticationT, AuthorizationT],
        DeleteSuccessfulRequestOperation[AuthenticationT, AuthorizationT],
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
                    AuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, ReadResourceOperationAction):
                return ReadSuccessfulRequestOperation[AuthenticationT, AuthorizationT](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, UpdateResourceOperationAction):
                return UpdateSuccessfulRequestOperation[
                    AuthenticationT, AuthorizationT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, DeleteResourceOperationAction):
                return DeleteSuccessfulRequestOperation[
                    AuthenticationT, AuthorizationT
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
