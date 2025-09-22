from enum import IntEnum
from pydantic import BaseModel, Field, model_validator
from typing import Generic, Optional, Self, TypeVar, Union
from maleo.types.integer import OptionalInteger


class Limit(IntEnum):
    LIM_10 = 10
    LIM_20 = 20
    LIM_50 = 50
    LIM_100 = 100


class Page(BaseModel):
    page: int = Field(1, ge=1, description="Page number, must be >= 1.")


class FlexibleLimit(BaseModel):
    limit: OptionalInteger = Field(None, ge=1, description="Page limit. (Optional)")


class StrictLimit(BaseModel):
    limit: Limit = Field(Limit.LIM_10, description="Page limit.")


class PageInfo(BaseModel):
    data_count: int = Field(..., ge=0, description="Fetched data count")
    total_data: int = Field(..., ge=0, description="Total data count")
    total_pages: int = Field(..., ge=1, description="Total pages count")


class BaseFlexiblePagination(FlexibleLimit, Page):
    @model_validator(mode="after")
    def validate_page_and_limit(self) -> Self:
        if self.limit is None:
            self.page = 1
        return self


class FlexiblePagination(PageInfo, BaseFlexiblePagination):
    pass


class BaseStrictPagination(StrictLimit, Page):
    pass


class StrictPagination(PageInfo, BaseStrictPagination):
    pass


AnyPagination = Union[FlexiblePagination, StrictPagination]
PaginationT = TypeVar("PaginationT", bound=AnyPagination)
OptionalAnyPagination = Optional[AnyPagination]
OptionalPaginationT = TypeVar("OptionalPaginationT", bound=OptionalAnyPagination)


class PaginationMixin(BaseModel, Generic[OptionalPaginationT]):
    pagination: OptionalPaginationT = Field(..., description="Pagination")
