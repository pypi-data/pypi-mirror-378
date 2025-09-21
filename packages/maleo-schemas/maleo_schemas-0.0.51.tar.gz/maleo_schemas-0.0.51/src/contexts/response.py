from pydantic import (
    BaseModel,
    Field,
)
from typing import Generic, List, Optional, Tuple, TypeVar
from maleo.types.string import OptionalString


class ResponseContext(BaseModel):
    status_code: int = Field(..., description="Status code")
    media_type: OptionalString = Field(None, description="Media type (Optional)")
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Response's headers"
    )


OptionalResponseContext = Optional[ResponseContext]
OptionalResponseContextT = TypeVar(
    "OptionalResponseContextT", bound=Optional[OptionalResponseContext]
)


class ResponseContextMixin(BaseModel, Generic[OptionalResponseContextT]):
    response_context: OptionalResponseContextT = Field(
        ..., description="Response's context"
    )
