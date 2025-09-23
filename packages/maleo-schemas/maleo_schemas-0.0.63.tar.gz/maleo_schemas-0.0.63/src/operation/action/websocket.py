from pydantic import Field
from typing_extensions import Annotated
from maleo.types.dict import OptionalStringToAnyDict
from ..enums import WebSocketOperationType
from .base import BaseOperationAction


class WebSocketOperationAction(BaseOperationAction[WebSocketOperationType]):
    details: Annotated[
        OptionalStringToAnyDict, Field(None, description="Action's details")
    ] = None
