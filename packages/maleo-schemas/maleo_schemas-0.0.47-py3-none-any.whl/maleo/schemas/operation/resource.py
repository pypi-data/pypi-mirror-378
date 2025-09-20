from typing import Generic, Literal, Optional, Union, overload
from uuid import UUID
from maleo.mixins.general import SuccessT
from maleo.security.authentication import OptionalAllAuthenticationT
from maleo.security.authorization import AuthorizationT
from maleo.security.impersonation import Impersonation
from ..contexts.request import RequestContext
from ..contexts.service import ServiceContext
from ..data import ModelDataT
from ..error import OptionalErrorT, ErrorT
from ..metadata import MetadataT
from ..pagination import PaginationT
from ..resource import Resource
from ..response import (
    ResponseT,
    ErrorResponseT,
    SuccessResponseT,
    NoDataResponse,
    CreateSingleDataResponse,
    ReadSingleDataResponse,
    UpdateSingleDataResponse,
    DeleteSingleDataResponse,
    CreateMultipleDataResponse,
    ReadMultipleDataResponse,
    UpdateMultipleDataResponse,
    DeleteMultipleDataResponse,
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


class ResourceOperation(
    BaseOperation[
        ResourceOperationActionT,
        Resource,
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
        ResourceOperationActionT,
        SuccessT,
        OptionalErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.RESOURCE
    response_context: None = None


class FailedResourceOperation(
    ResourceOperation[
        ResourceOperationActionT,
        Literal[False],
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        ResourceOperationActionT,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
):
    success: Literal[False] = False


class CreateFailedResourceOperation(
    FailedResourceOperation[
        CreateResourceOperationAction,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
):
    pass


class ReadFailedResourceOperation(
    FailedResourceOperation[
        ReadResourceOperationAction,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
):
    pass


class UpdateFailedResourceOperation(
    FailedResourceOperation[
        UpdateResourceOperationAction,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
):
    pass


class DeleteFailedResourceOperation(
    FailedResourceOperation[
        DeleteResourceOperationAction,
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        ErrorT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ErrorResponseT,
    ],
):
    pass


class SuccessfulResourceOperation(
    ResourceOperation[
        ResourceOperationActionT,
        Literal[True],
        None,
        OptionalAllAuthenticationT,
        AuthorizationT,
        SuccessResponseT,
    ],
    Generic[
        ResourceOperationActionT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        SuccessResponseT,
    ],
):
    success: Literal[True] = True
    error: None = None


class NoDataResourceOperation(
    SuccessfulResourceOperation[
        ResourceOperationActionT,
        OptionalAllAuthenticationT,
        AuthorizationT,
        NoDataResponse[MetadataT],
    ],
    Generic[
        ResourceOperationActionT, OptionalAllAuthenticationT, AuthorizationT, MetadataT
    ],
):
    pass


class CreateSingleResourceOperation(
    SuccessfulResourceOperation[
        CreateResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
        CreateSingleDataResponse[ModelDataT, MetadataT],
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
        ModelDataT,
        MetadataT,
    ],
):
    pass


class ReadSingleResourceOperation(
    SuccessfulResourceOperation[
        ReadResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ReadSingleDataResponse[ModelDataT, MetadataT],
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
        ModelDataT,
        MetadataT,
    ],
):
    pass


class UpdateSingleResourceOperation(
    SuccessfulResourceOperation[
        UpdateResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
        UpdateSingleDataResponse[ModelDataT, MetadataT],
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
        ModelDataT,
        MetadataT,
    ],
):
    pass


class DeleteSingleResourceOperation(
    SuccessfulResourceOperation[
        DeleteResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
        DeleteSingleDataResponse[ModelDataT, MetadataT],
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
        ModelDataT,
        MetadataT,
    ],
):
    pass


class CreateMultipleResourceOperation(
    SuccessfulResourceOperation[
        CreateResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
        CreateMultipleDataResponse[ModelDataT, PaginationT, MetadataT],
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
        ModelDataT,
        PaginationT,
        MetadataT,
    ],
):
    pass


class ReadMultipleResourceOperation(
    SuccessfulResourceOperation[
        ReadResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
        ReadMultipleDataResponse[ModelDataT, PaginationT, MetadataT],
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
        ModelDataT,
        PaginationT,
        MetadataT,
    ],
):
    pass


class UpdateMultipleResourceOperation(
    SuccessfulResourceOperation[
        UpdateResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
        UpdateMultipleDataResponse[ModelDataT, PaginationT, MetadataT],
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
        ModelDataT,
        PaginationT,
        MetadataT,
    ],
):
    pass


class DeleteMultipleResourceOperation(
    SuccessfulResourceOperation[
        DeleteResourceOperationAction,
        OptionalAllAuthenticationT,
        AuthorizationT,
        DeleteMultipleDataResponse[ModelDataT, PaginationT, MetadataT],
    ],
    Generic[
        OptionalAllAuthenticationT,
        AuthorizationT,
        ModelDataT,
        PaginationT,
        MetadataT,
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
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> CreateFailedResourceOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: ReadResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> ReadFailedResourceOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: UpdateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> UpdateFailedResourceOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: DeleteResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> DeleteFailedResourceOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        action: AllResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> Union[
        CreateFailedResourceOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
        ],
        ReadFailedResourceOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
        ],
        UpdateFailedResourceOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
        ],
        DeleteFailedResourceOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
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
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> CreateFailedResourceOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.READ],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> ReadFailedResourceOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
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
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> UpdateFailedResourceOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @staticmethod
    def generate_failed(
        *,
        type_: Literal[ResourceOperationType.DELETE],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> DeleteFailedResourceOperation[
        ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
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
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: ErrorT,
        request_context: Optional[RequestContext] = None,
        authentication: OptionalAllAuthenticationT,
        authorization: AuthorizationT,
        impersonation: Optional[Impersonation] = None,
        response: ErrorResponseT,
    ) -> Union[
        CreateFailedResourceOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
        ],
        ReadFailedResourceOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
        ],
        UpdateFailedResourceOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
        ],
        DeleteFailedResourceOperation[
            ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
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
            "resource": resource,
            "timestamp": timestamp,
            "summary": summary,
            "error": error,
            "request_context": request_context,
            "authentication": authentication,
            "authorization": authorization,
            "impersonation": impersonation,
            "response": response,
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
                return CreateFailedResourceOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, ReadResourceOperationAction):
                return ReadFailedResourceOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, UpdateResourceOperationAction):
                return UpdateFailedResourceOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif isinstance(action, DeleteResourceOperationAction):
                return DeleteFailedResourceOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
                ](
                    **common_kwargs,
                    action=action,
                )

        if type_ is not None:
            if type_ is ResourceOperationType.CREATE:
                action = ResourceOperationActionFactory.generate(
                    type_, create_type=create_type
                )
                return CreateFailedResourceOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.READ:
                action = ResourceOperationActionFactory.generate(type_)
                return ReadFailedResourceOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
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
                return UpdateFailedResourceOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
                ](
                    **common_kwargs,
                    action=action,
                )
            elif type_ is ResourceOperationType.DELETE:
                action = ResourceOperationActionFactory.generate(type_)
                return DeleteFailedResourceOperation[
                    ErrorT, OptionalAllAuthenticationT, AuthorizationT, ErrorResponseT
                ](
                    **common_kwargs,
                    action=action,
                )
            else:
                raise ValueError(f"Invalid type_: {type_}")

        # This should never happen due to initial validation,
        # but type checker needs to see all paths covered
        raise ValueError("Neither 'action' nor 'type' provided")
