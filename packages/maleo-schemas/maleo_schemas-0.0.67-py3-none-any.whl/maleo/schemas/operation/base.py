import traceback
from logging import Logger
from typing import Generic
from maleo.logging.enums import Level
from maleo.mixins.general import Success, SuccessT
from maleo.security.authentication import (
    OptionalAnyAuthenticationT,
    AuthenticationMixin,
)
from maleo.security.authorization import OptionalAuthorizationT, AuthorizationMixin
from maleo.security.impersonation import OptionalImpersonation, ImpersonationMixin
from maleo.types.boolean import OptionalBoolean
from maleo.types.dict import (
    OptionalStringToStringDict,
    StringToAnyDict,
    StringToStringDict,
)
from maleo.utils.merger import merge_dicts
from ..connection import OptionalConnectionContextT, ConnectionContextMixin
from ..error import OptionalAnyErrorT, ErrorMixin
from ..resource import OptionalResourceT, ResourceMixin
from ..response import (
    OptionalResponseContextT,
    ResponseContextMixin,
    ResponseT,
    ResponseMixin,
)
from ..service import ServiceContextMixin
from .action import (
    ActionMixin,
    ActionT,
)
from .context import ContextMixin
from .mixins import Id, OperationType, Summary, TimestampMixin


class BaseOperation(
    ResponseContextMixin[OptionalResponseContextT],
    ResponseMixin[ResponseT],
    ImpersonationMixin[OptionalImpersonation],
    AuthorizationMixin[OptionalAuthorizationT],
    AuthenticationMixin[OptionalAnyAuthenticationT],
    ConnectionContextMixin[OptionalConnectionContextT],
    ErrorMixin[OptionalAnyErrorT],
    Success[SuccessT],
    Summary,
    TimestampMixin,
    ResourceMixin[OptionalResourceT],
    ActionMixin[ActionT],
    ContextMixin,
    OperationType,
    Id,
    ServiceContextMixin,
    Generic[
        ActionT,
        OptionalResourceT,
        SuccessT,
        OptionalAnyErrorT,
        OptionalConnectionContextT,
        OptionalAnyAuthenticationT,
        OptionalAuthorizationT,
        ResponseT,
        OptionalResponseContextT,
    ],
):
    @property
    def log_message(self) -> str:
        message = f"Operation {self.id} - {self.type} - "

        success_information = f"{'success' if self.success else 'failed'}"

        if self.response_context is not None:
            success_information += f" {self.response_context.status_code}"

        message += f"{success_information} - "

        if self.connection_context is not None:
            message += (
                f"{self.connection_context.method} {self.connection_context.url} - "
                f"IP: {self.connection_context.ip_address} - "
            )

        if self.authentication is None:
            authentication = "No Authentication"
        else:
            # * In this line, 'is_authenticated' is not detected
            # * due to the use of generic, but this property exists
            if not self.authentication.user.is_authenticated:
                authentication = "Unauthenticated"
            else:
                # * In this line, 'display_name' and 'identity' is not detected
                # * due to the use of generic, but this property exists
                authentication = (
                    "Authenticated | "
                    f"Username: {self.authentication.user.display_name} | "
                    f"Email: {self.authentication.user.identity}"
                )

        message += f"{authentication} - "
        message += self.summary

        return message

    @property
    def labels(self) -> StringToStringDict:
        labels = {
            "service": self.service_context.key,
            "environment": self.service_context.environment,
            "operation_id": str(self.id),
            "operation_type": self.type,
            "success": "true" if self.success else "false",
        }

        if self.connection_context is not None:
            labels["method"] = self.connection_context.method
            labels["url"] = self.connection_context.url
        if self.response_context is not None:
            labels["status_code"] = str(self.response_context.status_code)

        return labels

    def log_labels(
        self,
        *,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ) -> StringToStringDict:
        if override_labels is not None:
            return override_labels

        labels = self.labels
        if additional_labels is not None:
            for k, v in additional_labels.items():
                if k in labels.keys():
                    raise ValueError(
                        f"Key '{k}' already exist in labels, override the labels if necessary"
                    )
                labels[k] = v
            labels = merge_dicts(labels, additional_labels)
        return labels

    def log_extra(
        self,
        *,
        additional_extra: OptionalStringToStringDict = None,
        override_extra: OptionalStringToStringDict = None,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ) -> StringToAnyDict:
        labels = self.log_labels(
            additional_labels=additional_labels, override_labels=override_labels
        )

        if override_extra is not None:
            extra = override_extra
        else:
            extra = {"json_fields": self.model_dump(mode="json"), "labels": labels}
            if additional_extra is not None:
                extra = merge_dicts(extra, additional_extra)

        return extra

    def log(
        self,
        logger: Logger,
        level: Level,
        *,
        exc_info: OptionalBoolean = None,
        additional_extra: OptionalStringToStringDict = None,
        override_extra: OptionalStringToStringDict = None,
        additional_labels: OptionalStringToStringDict = None,
        override_labels: OptionalStringToStringDict = None,
    ):
        try:
            message = self.log_message
            extra = self.log_extra(
                additional_extra=additional_extra,
                override_extra=override_extra,
                additional_labels=additional_labels,
                override_labels=override_labels,
            )
            logger.log(
                level,
                message,
                exc_info=exc_info,
                extra=extra,
            )
        except Exception:
            print("Failed logging operation:\n", traceback.format_exc())
