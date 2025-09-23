from pydantic import BaseModel, Field
from typing import Generic
from .publisher import TopicsConfigT, ConfigMixin as PublisherConfigMixin
from .subscription import (
    ConfigT as SubscriptionConfigT,
    ConfigMixin as SubscriptionConfigMixin,
)


class Config(
    SubscriptionConfigMixin[SubscriptionConfigT],
    PublisherConfigMixin[TopicsConfigT],
    BaseModel,
    Generic[TopicsConfigT, SubscriptionConfigT],
):
    pass


class ConfigMixin(BaseModel, Generic[TopicsConfigT, SubscriptionConfigT]):
    pubsub: Config[TopicsConfigT, SubscriptionConfigT] = Field(
        ..., description="PubSub config"
    )
