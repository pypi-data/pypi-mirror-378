from copy import deepcopy
from typing import Generic, Literal, Optional, Type, Union, overload
from uuid import UUID
from maleo.mixins.general import SuccessT
from maleo.security.authentication import OptionalAnyAuthenticationT
from maleo.security.authorization import OptionalAuthorizationT
from maleo.security.impersonation import OptionalImpersonation
from ..connection import OptionalConnectionContext
from ..data import ModelDataT
from ..error import OptionalAnyErrorT, AnyErrorT
from ..metadata import ModelMetadataT
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
from ..service import ServiceContext
from .action.resource import (
    AnyResourceOperationActionT,
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    ResourceOperationActions,
    AnyResourceOperationAction,
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
        AnyResourceOperationActionT,
        Resource,
        SuccessT,
        OptionalAnyErrorT,
        OptionalConnectionContext,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ResponseT,
        None,
    ],
    Generic[
        AnyResourceOperationActionT,
        SuccessT,
        OptionalAnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ResponseT,
    ],
):
    type: OperationType = OperationType.RESOURCE
    response_context: None = None


class FailedResourceOperation(
    ResourceOperation[
        AnyResourceOperationActionT,
        Literal[False],
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        AnyResourceOperationActionT,
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
):
    success: Literal[False] = False


class CreateFailedResourceOperation(
    FailedResourceOperation[
        CreateResourceOperationAction,
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
):
    pass


class ReadFailedResourceOperation(
    FailedResourceOperation[
        ReadResourceOperationAction,
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
):
    pass


class UpdateFailedResourceOperation(
    FailedResourceOperation[
        UpdateResourceOperationAction,
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
):
    pass


class DeleteFailedResourceOperation(
    FailedResourceOperation[
        DeleteResourceOperationAction,
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
    Generic[
        AnyErrorT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ErrorResponseT,
    ],
):
    pass


class SuccessfulResourceOperation(
    ResourceOperation[
        AnyResourceOperationActionT,
        Literal[True],
        None,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        SuccessResponseT,
    ],
    Generic[
        AnyResourceOperationActionT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        SuccessResponseT,
    ],
):
    success: Literal[True] = True
    error: None = None


class NoDataResourceOperation(
    SuccessfulResourceOperation[
        AnyResourceOperationActionT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        NoDataResponse[ModelMetadataT],
    ],
    Generic[
        AnyResourceOperationActionT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelMetadataT,
    ],
):
    pass


class CreateSingleResourceOperation(
    SuccessfulResourceOperation[
        CreateResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        CreateSingleDataResponse[ModelDataT, ModelMetadataT],
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelDataT,
        ModelMetadataT,
    ],
):
    pass


class ReadSingleResourceOperation(
    SuccessfulResourceOperation[
        ReadResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ReadSingleDataResponse[ModelDataT, ModelMetadataT],
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelDataT,
        ModelMetadataT,
    ],
):
    pass


class UpdateSingleResourceOperation(
    SuccessfulResourceOperation[
        UpdateResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        UpdateSingleDataResponse[ModelDataT, ModelMetadataT],
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelDataT,
        ModelMetadataT,
    ],
):
    pass


class DeleteSingleResourceOperation(
    SuccessfulResourceOperation[
        DeleteResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        DeleteSingleDataResponse[ModelDataT, ModelMetadataT],
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelDataT,
        ModelMetadataT,
    ],
):
    pass


class CreateMultipleResourceOperation(
    SuccessfulResourceOperation[
        CreateResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        CreateMultipleDataResponse[ModelDataT, PaginationT, ModelMetadataT],
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelDataT,
        PaginationT,
        ModelMetadataT,
    ],
):
    pass


class ReadMultipleResourceOperation(
    SuccessfulResourceOperation[
        ReadResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ReadMultipleDataResponse[ModelDataT, PaginationT, ModelMetadataT],
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelDataT,
        PaginationT,
        ModelMetadataT,
    ],
):
    pass


class UpdateMultipleResourceOperation(
    SuccessfulResourceOperation[
        UpdateResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        UpdateMultipleDataResponse[ModelDataT, PaginationT, ModelMetadataT],
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelDataT,
        PaginationT,
        ModelMetadataT,
    ],
):
    pass


class DeleteMultipleResourceOperation(
    SuccessfulResourceOperation[
        DeleteResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        DeleteMultipleDataResponse[ModelDataT, PaginationT, ModelMetadataT],
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ModelDataT,
        PaginationT,
        ModelMetadataT,
    ],
):
    pass


class FailedFactory(
    Generic[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]
):
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: CreateResourceOperationAction) -> Type[
        CreateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: ReadResourceOperationAction) -> Type[
        ReadFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: UpdateResourceOperationAction) -> Type[
        UpdateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: DeleteResourceOperationAction) -> Type[
        DeleteFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: AnyResourceOperationAction) -> Union[
        Type[
            CreateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            ReadFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            UpdateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            DeleteFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
    ]: ...
    @classmethod
    def operation_cls_from_action(cls, action: AnyResourceOperationAction) -> Union[
        Type[
            CreateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            ReadFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            UpdateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            DeleteFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
    ]:
        if isinstance(action, CreateResourceOperationAction):
            operation_cls = CreateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif isinstance(action, ReadResourceOperationAction):
            operation_cls = ReadFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif isinstance(action, UpdateResourceOperationAction):
            operation_cls = UpdateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif isinstance(action, DeleteResourceOperationAction):
            operation_cls = DeleteFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        return operation_cls

    @overload
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: Literal[ResourceOperationType.CREATE],
    ) -> Type[
        CreateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: Literal[ResourceOperationType.READ],
    ) -> Type[
        ReadFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: Literal[ResourceOperationType.UPDATE],
    ) -> Type[
        UpdateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: Literal[ResourceOperationType.DELETE],
    ) -> Type[
        DeleteFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: ResourceOperationType,
    ) -> Union[
        Type[
            CreateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            ReadFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            UpdateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            DeleteFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
    ]:
        if type_ is ResourceOperationType.CREATE:
            operation_cls = CreateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif type_ is ResourceOperationType.READ:
            operation_cls = ReadFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif type_ is ResourceOperationType.UPDATE:
            operation_cls = UpdateFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif type_ is ResourceOperationType.DELETE:
            operation_cls = DeleteFailedResourceOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        return operation_cls

    @overload
    @classmethod
    def generate(
        cls,
        action: CreateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> CreateFailedResourceOperation[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
        action: ReadResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> ReadFailedResourceOperation[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
        action: UpdateResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> UpdateFailedResourceOperation[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
        action: DeleteResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> DeleteFailedResourceOperation[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
        action: AnyResourceOperationAction,
        *,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> Union[
        CreateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        ReadFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        UpdateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        DeleteFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
        *,
        type_: Literal[ResourceOperationType.CREATE],
        create_type: Optional[ResourceOperationCreateType] = ...,
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> CreateFailedResourceOperation[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
        *,
        type_: Literal[ResourceOperationType.READ],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> ReadFailedResourceOperation[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
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
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> UpdateFailedResourceOperation[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
        *,
        type_: Literal[ResourceOperationType.DELETE],
        service_context: ServiceContext,
        id: UUID,
        context: OperationContext,
        resource: Resource,
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> DeleteFailedResourceOperation[
        AnyErrorT, OptionalAnyAuthenticationT, OptionalAuthorizationT, ErrorResponseT
    ]: ...
    @overload
    @classmethod
    def generate(
        cls,
        *,
        type_: ResourceOperationType,
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
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> Union[
        CreateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        ReadFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        UpdateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        DeleteFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
    ]: ...
    @classmethod
    def generate(
        cls,
        action: Optional[AnyResourceOperationAction] = None,
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
        error: AnyErrorT,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
    ) -> Union[
        CreateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        ReadFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        UpdateFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        DeleteFailedResourceOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
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
            "connection_context": connection_context,
            "authentication": authentication,
            "authorization": authorization,
            "impersonation": impersonation,
            "response": response,
        }

        if action is not None:
            if not isinstance(action, ResourceOperationActions):
                raise ValueError(f"Invalid 'action' type: '{type(action)}'")

            kwargs = deepcopy(common_kwargs)
            kwargs["action"] = action

            return cls.operation_cls_from_action(action).model_validate(kwargs)

        if type_ is not None:
            action = ResourceOperationActionFactory.generate(
                type_,
                create_type=create_type,
                update_type=update_type,
                data_update_type=data_update_type,
                status_update_type=status_update_type,
            )
            kwargs = deepcopy(common_kwargs)
            kwargs["action"] = action
            return cls.operation_cls_from_type(type_).model_validate(kwargs)

        # This should never happen due to initial validation,
        # but type checker needs to see all paths covered
        raise ValueError("Neither 'action' nor 'type' provided")
