from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from noxus_sdk.client import Client

T = TypeVar("T")


class BaseResource(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    client: Client = Field(..., exclude=True)


class BaseService(Generic[T]):
    def __init__(self, client: "Client") -> None:
        self.client = client
