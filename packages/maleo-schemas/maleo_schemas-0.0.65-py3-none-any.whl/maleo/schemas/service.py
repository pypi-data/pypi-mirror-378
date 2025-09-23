import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import Annotated
from maleo.enums.environment import Environment
from maleo.enums.service import Key


class ServiceContext(BaseModel):
    environment: Environment = Field(..., description="Service's environment")
    key: Key = Field(..., description="Service's key")

    @classmethod
    def from_env(cls) -> "ServiceContext":
        load_dotenv()
        environment = os.getenv("ENVIRONMENT", None)
        if environment is None:
            raise ValueError("Variable 'ENVIRONMENT' not found in ENV")

        key = os.getenv("SERVICE_KEY", None)
        if key is None:
            raise ValueError("Variable 'SERVICE_KEY' not found in ENV")

        return cls(environment=Environment(environment), key=Key(key))


OptionalServiceContext = Optional[ServiceContext]


class ServiceContextMixin(BaseModel):
    service_context: Annotated[
        ServiceContext,
        Field(ServiceContext.from_env(), description="Service's context"),
    ] = ServiceContext.from_env()
