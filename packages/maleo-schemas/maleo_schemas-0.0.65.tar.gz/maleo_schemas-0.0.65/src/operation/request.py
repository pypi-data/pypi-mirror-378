from copy import deepcopy
from typing import Any, Generic, Literal, Optional, Type, Union, overload
from uuid import UUID
from maleo.mixins.general import SuccessT
from maleo.security.authentication import OptionalAnyAuthenticationT
from maleo.security.authorization import OptionalAuthorizationT
from maleo.security.impersonation import OptionalImpersonation
from ..connection import ConnectionContext
from ..error import OptionalAnyErrorT, AnyErrorT
from ..pagination import OptionalAnyPagination
from ..response import (
    ResponseContext,
    ResponseT,
    ErrorResponseT,
    AnyDataResponse,
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


class RequestOperation(
    BaseOperation[
        AnyResourceOperationActionT,
        None,
        SuccessT,
        OptionalAnyErrorT,
        ConnectionContext,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ResponseT,
        ResponseContext,
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
    type: OperationType = OperationType.REQUEST
    resource: None = None


class FailedRequestOperation(
    RequestOperation[
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
    summary: str = "Failed processing request"


class CreateFailedRequestOperation(
    FailedRequestOperation[
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


class ReadFailedRequestOperation(
    FailedRequestOperation[
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


class UpdateFailedRequestOperation(
    FailedRequestOperation[
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


class DeleteFailedRequestOperation(
    FailedRequestOperation[
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


class SuccessfulRequestOperation(
    RequestOperation[
        AnyResourceOperationActionT,
        Literal[True],
        None,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        AnyDataResponse[Any, OptionalAnyPagination, Any],
    ],
    Generic[
        AnyResourceOperationActionT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
    ],
):
    success: Literal[True] = True
    error: None = None
    summary: str = "Successfully processed request"


class CreateSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        CreateResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
    ],
):
    pass


class ReadSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        ReadResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
    ],
):
    pass


class UpdateSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        UpdateResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
    ],
):
    pass


class DeleteSuccessfulRequestOperation(
    SuccessfulRequestOperation[
        DeleteResourceOperationAction,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
    ],
    Generic[
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
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
        CreateFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: ReadResourceOperationAction) -> Type[
        ReadFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: UpdateResourceOperationAction) -> Type[
        UpdateFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: DeleteResourceOperationAction) -> Type[
        DeleteFailedRequestOperation[
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
            CreateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            ReadFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            UpdateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            DeleteFailedRequestOperation[
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
            CreateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            ReadFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            UpdateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            DeleteFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
    ]:
        if isinstance(action, CreateResourceOperationAction):
            operation_cls = CreateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif isinstance(action, ReadResourceOperationAction):
            operation_cls = ReadFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif isinstance(action, UpdateResourceOperationAction):
            operation_cls = UpdateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif isinstance(action, DeleteResourceOperationAction):
            operation_cls = DeleteFailedRequestOperation[
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
        CreateFailedRequestOperation[
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
        ReadFailedRequestOperation[
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
        UpdateFailedRequestOperation[
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
        DeleteFailedRequestOperation[
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
            CreateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            ReadFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            UpdateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
        Type[
            DeleteFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        ],
    ]:
        if type_ is ResourceOperationType.CREATE:
            operation_cls = CreateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif type_ is ResourceOperationType.READ:
            operation_cls = ReadFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif type_ is ResourceOperationType.UPDATE:
            operation_cls = UpdateFailedRequestOperation[
                AnyErrorT,
                OptionalAnyAuthenticationT,
                OptionalAuthorizationT,
                ErrorResponseT,
            ]
        elif type_ is ResourceOperationType.DELETE:
            operation_cls = DeleteFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> CreateFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> ReadFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> UpdateFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> DeleteFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> Union[
        CreateFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        ReadFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        UpdateFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        DeleteFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> CreateFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> ReadFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> UpdateFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> DeleteFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> Union[
        CreateFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        ReadFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        UpdateFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        DeleteFailedRequestOperation[
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
        timestamp: Timestamp,
        summary: str,
        error: AnyErrorT,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: ErrorResponseT,
        response_context: ResponseContext,
    ) -> Union[
        CreateFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        ReadFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        UpdateFailedRequestOperation[
            AnyErrorT,
            OptionalAnyAuthenticationT,
            OptionalAuthorizationT,
            ErrorResponseT,
        ],
        DeleteFailedRequestOperation[
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
            "timestamp": timestamp,
            "summary": summary,
            "error": error,
            "connection_context": connection_context,
            "authentication": authentication,
            "authorization": authorization,
            "impersonation": impersonation,
            "response": response,
            "response_context": response_context,
        }

        if action is not None:
            if not isinstance(action, ResourceOperationActions):
                raise ValueError(f"Invalid 'action' type: '{type(action)}'")

            kwargs = deepcopy(common_kwargs)
            kwargs["action"] = action

            return cls.operation_cls_from_action(action).model_validate(kwargs)

        elif type_ is not None:
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


class SuccessfulFactory(Generic[OptionalAnyAuthenticationT, OptionalAuthorizationT]):
    @overload
    @classmethod
    def operation_cls_from_action(
        cls, action: CreateResourceOperationAction
    ) -> Type[
        CreateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(
        cls, action: ReadResourceOperationAction
    ) -> Type[
        ReadSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(
        cls, action: UpdateResourceOperationAction
    ) -> Type[
        UpdateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(
        cls, action: DeleteResourceOperationAction
    ) -> Type[
        DeleteSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_action(cls, action: AnyResourceOperationAction) -> Union[
        Type[
            CreateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            ReadSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            UpdateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            DeleteSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
    ]: ...
    @classmethod
    def operation_cls_from_action(cls, action: AnyResourceOperationAction) -> Union[
        Type[
            CreateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            ReadSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            UpdateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            DeleteSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
    ]:
        if isinstance(action, CreateResourceOperationAction):
            operation_cls = CreateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        elif isinstance(action, ReadResourceOperationAction):
            operation_cls = ReadSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        elif isinstance(action, UpdateResourceOperationAction):
            operation_cls = UpdateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        elif isinstance(action, DeleteResourceOperationAction):
            operation_cls = DeleteSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        return operation_cls

    @overload
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: Literal[ResourceOperationType.CREATE],
    ) -> Type[
        CreateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: Literal[ResourceOperationType.READ],
    ) -> Type[
        ReadSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: Literal[ResourceOperationType.UPDATE],
    ) -> Type[
        UpdateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ]
    ]: ...
    @overload
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: Literal[ResourceOperationType.DELETE],
    ) -> Type[
        DeleteSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ]
    ]: ...
    @classmethod
    def operation_cls_from_type(
        cls,
        type_: ResourceOperationType,
    ) -> Union[
        Type[
            CreateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            ReadSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            UpdateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
        Type[
            DeleteSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        ],
    ]:
        if type_ is ResourceOperationType.CREATE:
            operation_cls = CreateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        elif type_ is ResourceOperationType.READ:
            operation_cls = ReadSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        elif type_ is ResourceOperationType.UPDATE:
            operation_cls = UpdateSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
            ]
        elif type_ is ResourceOperationType.DELETE:
            operation_cls = DeleteSuccessfulRequestOperation[
                OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> CreateSuccessfulRequestOperation[
        OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> ReadSuccessfulRequestOperation[
        OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> UpdateSuccessfulRequestOperation[
        OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> DeleteSuccessfulRequestOperation[
        OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> Union[
        CreateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        ReadSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        UpdateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        DeleteSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> CreateSuccessfulRequestOperation[
        OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> ReadSuccessfulRequestOperation[
        OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> UpdateSuccessfulRequestOperation[
        OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> DeleteSuccessfulRequestOperation[
        OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> Union[
        CreateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        ReadSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        UpdateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        DeleteSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
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
        timestamp: Timestamp,
        summary: str,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthenticationT,
        authorization: OptionalAuthorizationT,
        impersonation: OptionalImpersonation = None,
        response: AnyDataResponse[Any, OptionalAnyPagination, Any],
        response_context: ResponseContext,
    ) -> Union[
        CreateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        ReadSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        UpdateSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
        ],
        DeleteSuccessfulRequestOperation[
            OptionalAnyAuthenticationT, OptionalAuthorizationT
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
            "timestamp": timestamp,
            "summary": summary,
            "connection_context": connection_context,
            "authentication": authentication,
            "authorization": authorization,
            "impersonation": impersonation,
            "response": response,
            "response_context": response_context,
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
