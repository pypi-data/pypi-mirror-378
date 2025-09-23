from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar


class SubscriptionConfig(BaseModel):
    id: str = Field(..., description="Subscription's ID")
    max_messages: int = Field(10, description="Subscription's Max messages")
    ack_deadline: int = Field(10, description="Subscription's ACK deadline")


class Config(BaseModel):
    pass


ConfigT = TypeVar("ConfigT", bound=Optional[Config])


class ConfigMixin(BaseModel, Generic[ConfigT]):
    subscription: ConfigT = Field(..., description="Subscription config")
