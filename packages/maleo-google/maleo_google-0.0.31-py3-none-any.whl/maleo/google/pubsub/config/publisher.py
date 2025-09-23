from pydantic import BaseModel, Field
from typing import Generic, TypeVar


class TopicConfig(BaseModel):
    id: str = Field(..., description="Topic's Id")


DEFAULT_OPERATION_TOPIC_CONFIG = TopicConfig(id="operation")
DEFAULT_DATABASE_OPERATION_TOPIC_CONFIG = TopicConfig(id="database-operation")
DEFAULT_REQUEST_OPERATION_TOPIC_CONFIG = TopicConfig(id="request-operation")
DEFAULT_RESOURCE_OPERATION_TOPIC_CONFIG = TopicConfig(id="resource-operation")
DEFAULT_SYSTEM_OPERATION_TOPIC_CONFIG = TopicConfig(id="system-operation")
DEFAULT_RESOURCE_MEASUREMENT_TOPIC_CONFIG = TopicConfig(id="resource-measurement")


class OperationTopicsConfig(BaseModel):
    default: TopicConfig = Field(
        DEFAULT_OPERATION_TOPIC_CONFIG,
        description="Operation topic config",
    )
    database: TopicConfig = Field(
        DEFAULT_DATABASE_OPERATION_TOPIC_CONFIG,
        description="Database operation topic config",
    )
    request: TopicConfig = Field(
        DEFAULT_REQUEST_OPERATION_TOPIC_CONFIG,
        description="Request operation topic config",
    )
    resource: TopicConfig = Field(
        DEFAULT_RESOURCE_OPERATION_TOPIC_CONFIG,
        description="Resource operation topic config",
    )
    system: TopicConfig = Field(
        DEFAULT_SYSTEM_OPERATION_TOPIC_CONFIG,
        description="System operation topic config",
    )


class ResourceTopicsConfig(BaseModel):
    measurement: TopicConfig = Field(
        DEFAULT_RESOURCE_MEASUREMENT_TOPIC_CONFIG,
        description="Resource measurement topics config",
    )


class InfraTopicsConfig(BaseModel):
    resource: ResourceTopicsConfig = Field(..., description="Resource's topics config")


class TopicsConfig(BaseModel):
    infra: InfraTopicsConfig = Field(..., description="Infra's topics config")
    operation: OperationTopicsConfig = Field(
        ..., description="Operation's topics config"
    )


TopicsConfigT = TypeVar("TopicsConfigT", bound=TopicsConfig)


class Config(BaseModel, Generic[TopicsConfigT]):
    topics: TopicsConfigT = Field(..., description="Topics config")


class ConfigMixin(BaseModel, Generic[TopicsConfigT]):
    publisher: Config[TopicsConfigT] = Field(..., description="Publisher config")
