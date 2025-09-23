from pydantic import Field
from typing_extensions import Annotated
from maleo.types.dict import OptionalStringToAnyDict
from ..enums import SystemOperationType
from .base import BaseOperationAction


class SystemOperationAction(BaseOperationAction[SystemOperationType]):
    details: Annotated[
        OptionalStringToAnyDict, Field(None, description="Action's details")
    ] = None
