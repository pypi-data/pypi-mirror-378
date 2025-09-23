from fastapi import Request, Header
from typing import Callable
from uuid import UUID
from maleo.enums.connection import Header as HeaderEnum
from maleo.types.uuid import OptionalUUID
from .enums import IdSource
from .extractor import extract_operation_id


def get_operation_id(
    source: IdSource = IdSource.STATE, *, generate: bool = False
) -> Callable[..., UUID]:

    def dependency(
        request: Request,
        # the following operation_id is for documentation purpose only
        operation_id: OptionalUUID = Header(
            None,
            alias=HeaderEnum.X_OPERATION_ID.value,
            description="Operation ID Header",
        ),
    ) -> UUID:
        return extract_operation_id(source, request=request, generate=generate)

    return dependency
